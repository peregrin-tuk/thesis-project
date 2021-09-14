from src.datatypes.melody_data import MelodyData
from src.generation import AbstractGenerator


class CallResponseSet():

    def __init__(self,
                 generator: AbstractGenerator,
                 checkpoint: str,
                 input_sequence: MelodyData = None,
                 generated_base_sequence: MelodyData = None,
                 output_sequence: MelodyData = None,
                 input_analysis: dict = None,
                 adaptation_operations: list = None,
                 generation_similarity: dict = None,
                 output_similarity: dict = None
                 ) -> None:
        self.generator = generator
        self.checkpoint = checkpoint
        self.input_sequence = input_sequence
        self.generated_base_sequence = generated_base_sequence
        self.output_sequence = output_sequence
        self.input_analysis = input_analysis
        self.adaptation_operations = adaptation_operations
        self.generation_similarity = generation_similarity
        self.output_similarity = output_similarity
