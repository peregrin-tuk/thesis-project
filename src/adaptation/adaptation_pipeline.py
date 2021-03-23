import time
from src.datatypes.melody_data import AdaptationMelodyData
from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation


class AdaptationPipeline(AbstractAdaptationOperation):

    def __init__(self):
        self.operations = []
        self._required_analysis = set()


    def register(self, operation: AbstractAdaptationOperation):
        self.operations.append(operation)
        self._required_analysis.update(operation.required_analysis)

    @property
    def required_analysis(self):
        return self._required_analysis


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
        for operation in self.operations:
            base = operation.execute(base, control, control_analysis)
        t2 = time.time()

        base.meta['adaptation_duration'] = t2-t1

        return base