import inspect

from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.adaptation.adaptation_pipeline import AdaptationPipeline
from src.adaptation import operations

from src.adaptation.operations.transpose_sequence_operation import TransposeSequenceOperation

# this is more of a draft

# prepare a pipeline
pipeline = AdaptationPipeline()
pipeline.register(TransposeSequenceOperation)


# # adapt a melody with the pipeline
# input_analysis = analyse(input_sequence, pipeline.required_analysis)
# pipeline.execute(gen_base_sequence, input_sequence, input_analysis)


class Adaptation():

    def __init__(self):
        self.pipeline = AdaptationPipeline()
        self.available_operations = self.__load_operations()

    def __load_operations(self):
        available_operations = []

        for name, obj in inspect.getmembers(operations):
            if inspect.isclass(obj) and issubclass(obj, AbstractAdaptationOperation) and obj is not AbstractAdaptationOperation:
                available_operations.append(obj)

        return available_operations



