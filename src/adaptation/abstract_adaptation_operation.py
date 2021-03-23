from abc import ABC, abstractmethod
from src.datatypes.melody_data import AdaptationMelodyData

class AbstractAdaptationOperation(ABC):
    """Description

    Adapts x based on y

    Attributes:
        required_analysis (set of functions): set of analysis functions the adaptation operations requires to run.

    """
    
    @abstractmethod
    @property
    def required_analysis(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        raise NotImplementedError