import time
from src.datatypes.melody_data import AdaptationMelodyData
from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation


class AdaptationPipeline(AbstractAdaptationOperation):

    def __init__(self):
        super().__init__()
        self.__operations = []


    def register(self, operation: AbstractAdaptationOperation):
        op = operation()
        self.__operations.append(op)
        self.required_analysis.update(op.required_analysis)


    def empty(self):
        self.__operations = []


    def get_operations(self, as_str: bool = True):
        """
        Returns the operation steps of the pipline as a list.

        Args:
            as_str (bool)

        Returns:
            list with the name of each operation if as_str = true
            list with the class of each operation if as_str 0 false
        """
        if as_str:
            return [op.__class__.__name__ for op in self.__operations]
        else:
            return [op.__class__ for op in self.__operations]


    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        """
        Executes all operations in the pipeline on the provided source input.

        Args:
            base (AdaptationMelodyData): midi sequence to be adapted
            control (AdaptationMelodyData): midi sequence to which the base sequence should be adapted to
            control_analysis (dict): analysis data of the control sequence

        Returns:
            AdaptationMelodyData: Adapted source sequence. Its meta data contains a list of applied adaptations as well as the durations of their execution.
        """
        t1 = time.time()
        for operation in self.__operations:
            base = operation.execute(base, control, control_analysis)
        t2 = time.time()

        base.meta['adaptation_duration'] = t2-t1

        return base