from src.io.conversion import note_seq_to_pretty_midi
from ipywidgets import Output
from definitions import SequenceType
from src.io.input import loadMidiFile
from src.datatypes.melody_data import MelodyData
from src.datatypes.call_response_set import CallResponseSet
from src.generation.abstract_generator import AbstractGenerator
from src.adaptation import Adaptation
from src.generation import get_available_generators


class App:

    def __init__(self, log: Output):
        self.log = log

        self.adaptation = Adaptation()
        self.generator = None
        self.checkpoint = None
        self.temperature = None


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


    def apply_settings(self, generator: AbstractGenerator, checkpoint: str, temperature: float, steps: list):
        self.__clear_log()
    	self.__log("Saving settings ...")

        # set adaptation steps
        self.adaptation.construct_pipeline(steps)

        # set temperature
        self.temperature = temperature

        # initialize checkpoint if changed
        if generator != self.generator or checkpoint != self.checkpoint:
            self.__log("Initializing generation model...")
            self.generator = generator(checkpoint)
            self.checkpoint = checkpoint

        self.__log("Done.")


    def run(self, input_file_path: str, store_results: bool = True):
        self.__clear_log()

        # CHECK how can we handle uploaded midi files ?
        # construct melodydata from input
        midi = loadMidiFile(input_file_path)
        input_data = MelodyData(midi, SequenceType.EXAMPLE)

        # run generation
        self.__log("Generating base melody for adaptation...")
        gen_base = self.generator.generate(length_in_beats = 16, temperature=self.temperature)
        gen_data = MelodyData(note_seq_to_pretty_midi(gen_base['sequence']), SequenceType.GEN_BASE, { 'generation': gen_base['meta'] })

        # run adaptation
        self.__log("Adapting generated melody to input...")
        result = self.adaption.adapt(gen_data, input_data)

        # store data in db
        self.__log("Saving results to database...")
        if store_results:
            # TODO
            pass

        self.__log("Done.")
        # return data for interface as call-response-set
        # (input, gen_base, output, sim base + output, gen meta, adapt meta)
        # TODO

    def __log(self, msg: str):
        with self.log:
            print(msg)

    def __clear_log(self):
        self.log.clear_output()
        