from pathlib import Path
from ipywidgets import Output
from definitions import SequenceType
from src.io.input import loadMidiFile
from src.datatypes.melody_data import MelodyData
from src.datatypes.call_response_set import CallResponseSet
from src.adaptation import Adaptation
from src.generation import get_available_generators
from src.db import generations as db
from src.db.reference_sets import fetch_ref_set_by_id, get_normalization_values_of_ref_set
from src.evaluation.evaluation import Evaluation
from src.io.conversion import note_seq_to_pretty_midi
from definitions import ROOT_DIR


class App:

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

        self.get_generators()
        self.set_similarity_reference(1) # set default normalization values


    def get_adaptation_operations(self):
        return [op.__name__ for op in self.adaptation.available_operations]


    def get_generators(self):
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


    def apply_settings(self, generator_id: int, temperature: float, steps: list):
        self.__clear_log()
        self.__log("Saving settings ...")

        # set adaptation steps
        self.adaptation.construct_pipeline(steps)

        # set temperature
        self.temperature = temperature

        # initialize checkpoint if changed
        generator = self.generator_list[generator_id][1]
        checkpoint = self.generator_list[generator_id][2]

        if generator != self.generator or checkpoint != self.checkpoint:
            self.__log("Initializing generation model. This may take 1 (RNN) to 4 (VAE) minutes...")
            self.generator = generator(checkpoint, log=self.log)
            self.checkpoint = checkpoint

        self.__log("Done.")


    def set_similarity_reference(self, ref_set_id: int):
        normalization_values = get_normalization_values_of_ref_set(ref_set_id)
        self.evaluation = Evaluation(normalization_values)

        ref_set = fetch_ref_set_by_id(ref_set_id)
        self.ref_set = ref_set['name'] + ' (' + ref_set['source'] + ')'


    def run(self, input_file_path: str, store_results: bool = True):
        self.__clear_log()

        # CHECK how can we handle uploaded midi files ?
        # construct melodydata from input
        midi = loadMidiFile(input_file_path)
        input_data = MelodyData(midi, SequenceType.EXAMPLE)

        # run generation
        self.__log("Generating base melody for adaptation...")
        gen_base = self.generator.generate(length_in_quarters = 16, temperature=self.temperature)
        gen_data = MelodyData(note_seq_to_pretty_midi(gen_base['sequence']), SequenceType.GEN_BASE, { 'generation': gen_base['meta'] })

        # run adaptation
        self.__log("Adapting generated melody to input...")
        result, input_data = self.adaptation.adapt(gen_data, input_data)

        # evaluate
        generation_similarity = self.evaluation.evaluate_similarity(gen_data.sequence, input_data.sequence)
        output_similarity = self.evaluation.evaluate_similarity(result.sequence, input_data.sequence)
        gen_data.evaluation = generation_similarity
        result.evaluation = output_similarity

        # store data in db
        self.__log("Saving results to database...")
        if store_results:
            db.store_generation_result(
                input_data,
                gen_data,
                result) 
        self.__log("Done.")

        # return data for interface as call-response-set
        return CallResponseSet(self.generator,
                               self.checkpoint,
                               input_data,
                               gen_data,
                               result,
                               input_data.analysis,
                               self.adaptation.pipeline.get_operations,
                               generation_similarity,
                               output_similarity)


    def __log(self, msg: str):
        with self.log:
            print(msg)

    def __clear_log(self):
        self.log.clear_output()
        
