from pathlib import Path
from ipywidgets import Output

from definitions import ROOT_DIR, SequenceType
from src.io.input import loadMidiFile
from src.datatypes.melody_data import MelodyData
from src.datatypes.call_response_set import CallResponseSet
from src.adaptation import Adaptation
from src.generation import get_available_generators
from src.generation.generators.musicrnn_generator import MusicRNNGenerator
from src.generation.generators.musicvae_generator import MusicVAEGenerator
from src.db import generations as db
from src.db.reference_sets import fetch_ref_set_by_id, get_normalization_values_of_ref_set
from src.evaluation.evaluation import Evaluation
from src.io.conversion import note_seq_to_pretty_midi


class AppBatch:

    demo_melodies = [
        ('Twinkle, Twinkle', str(ROOT_DIR / Path('midi/examples/monophonic/twinkle1_4b.mid')) ),
        ('Toto: Africa', str(ROOT_DIR / Path('midi/examples/monophonic/africa_intro_2b.mid')) ),
        ('Mancini: Pink Panther', str(ROOT_DIR / Path('midi/examples/monophonic/pinkpanther_4b.mid')) ),
        ('Mozart: Eine kleine Nachtmusik', str(ROOT_DIR / Path('midi/examples/monophonic/mozart1_4b.mid')) ),
        ('Queen: Bohemian Rhapsody', str(ROOT_DIR / Path('midi/examples/monophonic/bohemian_mama_4b.mid')) ),
    ]

    def __init__(self, log: Output):
        self.log = log

        self.adaptation = Adaptation()
        self.generator = None
        self.checkpoint = None
        self.temperature = None
        self.result = None

        db.create_tables()

        self.get_generators()
        self.set_similarity_reference(5) # set default normalization values


    def get_adaptation_operations(self):
        return [op.__name__ for op in self.adaptation.available_operations]


    def get_generators(self):
        """ 
        Fetches all generators available in the system.
        Stores a list of available generators in self.generator_list and returns the list.

        Returns:
            list: list of generators as tuple in the form of (label, generator class, checkpoint enum)

        """
        generators = get_available_generators()
        generator_list = []
        for generator in generators:
            for checkpoint in generator.Checkpoint:
                label = generator.__name__ + ' - ' + checkpoint.name
                generator_list.append((label, generator, checkpoint))

        self.generator_list = generator_list
        return generator_list


    def get_demo_input(self):
        return self.demo_melodies


    def apply_generator_settings(self, generator_id: int, temperature: float):
        self.__clear_log()
        self.__log("Saving generator settings ...")

        # set temperature
        self.temperature = temperature

        # initialize checkpoint if changed
        generator = self.generator_list[generator_id][1]
        checkpoint = self.generator_list[generator_id][2]

        if generator != self.generator or checkpoint != self.checkpoint:
            self.__log("Initializing generation model. This may take 10 seconds (RNN) to 5 minutes (VAE)...")
            self.generator = generator(checkpoint, log=self.log)
            self.checkpoint = checkpoint

        self.__log("Done.")
        return self.generator_list[generator_id][0]


    def apply_adaptation_settings(self, steps: list):
        self.__clear_log()
        self.__log("Saving adaptation settings ...")

        # set adaptation steps
        self.adaptation.construct_pipeline(steps)

        self.__log("Done.")



    def set_similarity_reference(self, ref_set_id: int):
        normalization_values = get_normalization_values_of_ref_set(ref_set_id)
        self.evaluation = Evaluation(normalization_values)

        ref_set = fetch_ref_set_by_id(ref_set_id)
        self.ref_set = ref_set['name'] + ' (' + ref_set['source'] + ')'


    def run(self, input_file_path: str, generation_amount: int, store_results: bool = True):
        self.__clear_log() 

        # construct melodydata from input
        midi = loadMidiFile(input_file_path)
        input_data = MelodyData(midi, SequenceType.FILE_INPUT)

        # generations
        generations = []

        for i in range(0, generation_amount):
            # generate
            self.__clear_log()
            self.__log("Generating base melody " + str(i+1) + "/" + str(generation_amount) + "...")
            gen_data = self.__run_single_generation(input_data)

            # evaluate generation similarity (distance to input)
            generation_similarity = self.evaluation.evaluate_similarity(gen_data.sequence, input_data.sequence)
            gen_data.evaluation = generation_similarity

            self.__log("Creating adaptation of melody " + str(i+1) + "/" + str(generation_amount) + "...")
            adaptation = self.__run_single_adaptation(input_data, gen_data)

            generations.append(adaptation)

        # evaluate generation variance (intra set distance)
        generation_variance = None
        adaptation_variance = None
        if len(generations) > 1:
            generation_variance = self.evaluation.evaluate_variance([g.generated_base_sequence.sequence for g in generations])
            adaptation_variance = self.evaluation.evaluate_variance([g.output_sequence.sequence for g in generations])


        # TEST calculate average similarity values for generations set and all adaptation sets
        generation_avg_similarity = self.evaluation.calc_avg_from_similarity_dicts([g.generation_similarity for g in generations])
        adaptation_avg_similarity = self.evaluation.calc_avg_from_similarity_dicts([g.output_similarity for g in generations])
        

        # store set to database
        if store_results:
            self.__log("Saving results to database...")
            db_set_id = db.store_set(generations, generation_avg_similarity, adaptation_avg_similarity)
        else:
            db_set_id = "not available"
        self.__log("Done.")

        # return list cr sets + avg sim + variance
        self.result = {
            'generations': generations,
            'generation_avg_similarity': generation_avg_similarity,
            'adaptation_avg_similarity': adaptation_avg_similarity,
            'generation_variance': generation_variance,
            'adaptation_variance': adaptation_variance,
            'db_set_id': db_set_id,
        }

        return self.result


    def __run_single_adaptation(self, input_data: MelodyData, gen_data: MelodyData):
               
        # run adaptation
        result, input_data = self.adaptation.adapt(gen_data, input_data)

        # evaluate adaptation similarity (distance to input)
        output_similarity = self.evaluation.evaluate_similarity(result.sequence, input_data.sequence)
        result.evaluation = output_similarity

        # return data for interface as call-response-set
        return CallResponseSet(self.generator,
                               self.checkpoint,
                               input_data,
                               gen_data,
                               result,
                               input_data.analysis,
                               self.adaptation.pipeline.get_operations,
                               gen_data.evaluation,
                               result.evaluation)


    def __run_single_generation(self, input_data):
        if isinstance(self.generator, MusicVAEGenerator):
            length = input_data.sequence.get_end_time()
            note_count = 0
            bar_count = 1
            while (note_count < 3 * bar_count):
                gen_base = self.generator.generate(length_in_quarters = 16, temperature=self.temperature)
                note_count = len(gen_base['sequence'].notes)
                bar_count = length / 4 # CHECK expecting 4/4 time signature, for 3/4 this number has to be 3
        elif isinstance(self.generator, MusicRNNGenerator):
            gen_base = self.generator.generate(primer_sequence=input_data.sequence, length_in_quarters = 16, temperature=self.temperature)
        else:
            self.__log("The selected generator is currently not supported.")
            return
        self.gen_data = MelodyData(note_seq_to_pretty_midi(gen_base['sequence']), SequenceType.GEN_BASE, { 'generation': gen_base['meta'] })
        return self.gen_data


    def __log(self, msg: str):
        with self.log:
            print(msg)

    def __clear_log(self):
        self.log.clear_output()
        
