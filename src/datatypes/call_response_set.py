
# // analysis for gen_base/output is done at each adaptation step for whatever data is needed
# ?? should we build a similar class for multiple outputs (same structure, just that gen_base and output are lists of sequences, as comparative evaluation is a list of evaluations)
# ==> first do it for one, can easily be expanded in a next step if necessary

# => class Sequence
# ?? ==> subclass GeneratedSequence (meta: gen_dur, model, checkpoint, temperature)
# ?? ==> subclass InputSequence
# ?? meta data as dict (it will never be needed in code, just to be stored in the DB and shown in the dashboard,
# therefore there is not really need for a dedicated variable per meta data item. Also, this makes it flexible to store whatever meta data)

# Analysis object (can be dict)
# key weights for whole sequence
# key weights per bar
# thomassen melodic accent per note
# expectancy value per note

# // beat depth doesn't need to be annotated -> it's only based on time signature

# // Möglichkeit, die es zu überlegen und prüfen gilt: 
# // refactor this class to call_response_pair (just the melodies) and call_response_configuration (with generator, adaptation steps, length, temperatures)


from src.datatypes.melody import Melody
from src.generation import AbstractGenerator


class CallResponseSet():

    def __init__(self,
                generator: AbstractGenerator,
                 input_sequence: Melody = None,
                 generated_base_sequence: Melody = None,
                 output_sequence: Melody = None,
                 input_analysis: dict = None,
                 adaptation_operations: list = None, # TODO rename?
                 similarity_evaluation: dict = None  # rename?
                 ) -> None:
        self.generator = generator
        self.input_sequence = input_sequence
        self.generated_base_sequence = generated_base_sequence
        self.output_sequence = output_sequence
        self.input_analysis = input_analysis
        self.adaptation_operations = adaptation_operations
        self.similarity_evaluation = similarity_evaluation
        


# next:
# TODO melodic accent and key analysis in analysis class (wrapper or direct access via music21?)
# => analysis wrapper for all used analysis operations (expectancy algo, music21 calls, evtl. own beat weight calculation based on velocity and note duration)
# TODO pipeline and adaptation operations
# TODO write docstrings
