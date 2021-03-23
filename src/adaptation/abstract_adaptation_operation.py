from abc import ABC, abstractmethod
from src.datatypes.melody import Melody

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
    def execute(self, base: Melody, control: Melody, control_analysis: dict):
        raise NotImplementedError