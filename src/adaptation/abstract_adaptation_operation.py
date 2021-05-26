from abc import ABC, abstractmethod
import music21
from src.datatypes.melody_data import AdaptationMelodyData
from src.io.conversion import music21_to_pretty_midi

class AbstractAdaptationOperation(ABC):
    """Description

    Adapts x based on y

    Attributes:
        required_analysis (set of functions): set of analysis functions the adaptation operations requires to run.

    """
    
    def __init__(self):
        self.required_analysis = set()

    @abstractmethod
    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData):
        raise NotImplementedError

    def create_meta_and_update_base(self, base: AdaptationMelodyData, name: str, duration: float, adapted_sequence: music21.stream.Stream, base_analysis: dict):
        base.sequence = adapted_sequence
        base.meta.setdefault('steps',[]).append({
            'name': name,
            'duration': duration,
            'intermediate_result': music21_to_pretty_midi(adapted_sequence)
        })
        base.analysis.update(base_analysis)
        return base