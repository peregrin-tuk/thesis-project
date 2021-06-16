import inspect
import copy

from definitions import SequenceType
from src.analysis import analyze
from src.datatypes.melody_data import MelodyData
from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.adaptation.adaptation_pipeline import AdaptationPipeline
import src.adaptation.operations as operations_module


class Adaptation():

    def __init__(self):
        self.pipeline = AdaptationPipeline()
        self.available_operations = self.__load_operations_from_module()


    def construct_pipeline(self, operations: list):
        self.pipeline.empty()
        for op in operations:
            if isinstance(op, str):
                op_class = self.__find_operation_by_name(op)
                if op_class is not None:
                    self.pipeline.register(op_class)
            elif inspect.isclass(op) and issubclass(op, AbstractAdaptationOperation):
                self.pipeline.register(op)
            else:
                print("[ADAPT] Warning: Illegal argument for adaptation operation: " + str(op))


    def adapt(self, base: MelodyData, control: MelodyData):
        adapt_base = base.to_adaptation_data()
        adapt_control = control.to_adaptation_data()

        control_analysis = analyze(adapt_control, self.pipeline.required_analysis)
        adapt_control.analysis.update(control_analysis)

        adapted_sequence = self.pipeline.execute(adapt_base, adapt_control)
        result = copy.deepcopy(base)
        result.sequence_type = SequenceType.OUTPUT
        result.update_sequence_from_adaptation_data(adapted_sequence)
        control.update_sequence_from_adaptation_data(adapt_control)
        return result, control


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
        print("[ADAPT] Warning: Operation with name '" + name + "' does not exist.")


