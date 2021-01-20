import itertools
import time
from enum import Enum
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from note_seq.protobuf import generator_pb2
from note_seq import NoteSequence
from . import AbstractGenerator

_CHECKPOINTS = {
    1: ['attention_rnn',  'ATTENTION'],
    2: ['lookback_rnn', 'LOOKBACK'],
    2: ['mono_rnn', 'MONO'],
}
Checkpoint = Enum(
    value='Checkpoint',
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _CHECKPOINTS.items()
    )
)


class MusicRNNGenerator(AbstractGenerator):

    def __init__(self, checkpoint=Checkpoint.ATTENTION):
        super().__init__()

        print("[GEN] Initializing Music RNN with checkpoint '" +
              checkpoint.name + "'...")

        t1 = time.time()
        self.checkpoint = checkpoint
        bundle = sequence_generator_bundle.read_bundle_file(AbstractGenerator.models_base_path + '/rnn/' + checkpoint.name + '.mag')
        generator_map = melody_rnn_sequence_generator.get_generator_map()
        self.model = generator_map[checkpoint.name](checkpoint=None, bundle=bundle)
        self.model.initialize()
        t2 = time.time()

        print('[GEN] 🎉 Initialization finished in ' + str(t2-t1) + ' sec.')


    def generate(self, primer_sequence=NoteSequence(), length_in_quarters=16, temperature=0.4):
        t1 = time.time()
        generator_options = self.__setupGeneratorOptions(primer_sequence, length_in_quarters, temperature)
        generated_sequence = self.model.generate(primer_sequence, generator_options)
        t2 = time.time()

        return {
            'sequence': generated_sequence,
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MusicVAE',
		        'checkpoint': self.checkpoint.name,
		        'temperature':temperature	
            }
        }


    def generateMultiple(self, primer_sequence=NoteSequence(), number=10, length_in_quarters=16, temperature=0.4):
        t1 = time.time()
        generator_options = self.__setupGeneratorOptions(primer_sequence, length_in_quarters, temperature)
        generated_sequences = []
        for i in range(0, number):
            generated_sequences.append(self.model.generate(primer_sequence, generator_options))
        t2 = time.time()

        return {
            'sequences': generated_sequences,
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MusicVAE',
		        'checkpoint': self.checkpoint.name,
		        'temperature':temperature	
            }
        }


    def __setupGeneratorOptions(self, primer_sequence, length_in_quarters, temperature):
        num_steps = length_in_quarters * self.model.steps_per_quarter
        qpm = primer_sequence.tempos[0].qpm 
        seconds_per_step = 60.0 / qpm / self.model.steps_per_quarter

        primer_end_time = (max(n.end_time for n in primer_sequence.notes) if primer_sequence.notes else 0)
        total_time = primer_end_time * seconds_per_step + num_steps * seconds_per_step

        print("num_steps: " + str(num_steps))
        print("qpm: " + str(num_steps))
        print("seconds_per_step: " + str(seconds_per_step))
        print("primer_end_time: " + str(primer_end_time))
        print("total_time: " + str(total_time))
        print("primer: " + str(primer_sequence))

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature
        generator_options.generate_sections.add(start_time=primer_end_time + seconds_per_step, end_time=total_time)
        return generator_options