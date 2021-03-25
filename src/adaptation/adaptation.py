import inspect
from src.analysis import analyze

from src.datatypes.melody_data import MelodyData
from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.adaptation.adaptation_pipeline import AdaptationPipeline
import src.adaptation.operations as operations_module

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
        self.available_operations = self.__load_operations_from_module()


    def construct_pipeline(self, operations: list):
        self.pipeline.empty()
        for op in operations:
            if isinstance(op, str):
                self.pipeline.register(self.__find_operation_by_name(op))
            elif inspect.isclass(op) and issubclass(op, AbstractAdaptationOperation):
                self.pipeline.register(op)
            else:
                print("[ADAPT] Warning: Illegal argument for adaptaiton operations: " + str(op))


    def adapt(self, base: MelodyData, control: MelodyData):
        adapt_base = base.to_adaptation_data()
        adapt_control = control.to_adaptation_data()
        control_analysis = analyze(adapt_control, self.pipeline.required_analysis)
        adapted_sequence = self.pipeline.execute(adapt_base, adapt_control, control_analysis)
        base.update_sequence_from_adaptation_data(adapted_sequence)
        return base


    def __load_operations_from_module(self):
        available_operations = []
        for _, obj in inspect.getmembers(operations_module):
            if inspect.isclass(obj) and issubclass(obj, AbstractAdaptationOperation) and obj is not AbstractAdaptationOperation:
                available_operations.append(obj)
        return available_operations


    def __find_operation_by_name(self, name: str):
        for op in self.available_operations:
            if name == op.__name__:
                return op
        print("[ADAPT] Warning: Operation with name '" + name + "' is not available.")


