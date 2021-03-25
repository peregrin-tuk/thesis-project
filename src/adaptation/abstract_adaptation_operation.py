from abc import ABC, abstractmethod
import music21
from src.datatypes.melody_data import AdaptationMelodyData

class AbstractAdaptationOperation(ABC):
    """Description

    Adapts x based on y

    Attributes:
        required_analysis (set of functions): set of analysis functions the adaptation operations requires to run.

    """
    
    def __init__(self):
        self.required_analysis = set()

    @abstractmethod
    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        raise NotImplementedError

    def create_meta_and_update_base(self, base: AdaptationMelodyData, name: str, duration: float, adapted_sequence: music21.stream.Stream):
        base.sequence = adapted_sequence
        base.meta.setdefault('adaptation_steps',[]).append({
            'name': name,
            'duration': duration,
            'intermediate_result': adapted_sequence
        })
        return base