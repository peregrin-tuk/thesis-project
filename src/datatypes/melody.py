from typing import Dict
from pretty_midi import PrettyMIDI
from definitions import SequenceType

class Melody():

    def __init__(self, sequence: PrettyMIDI, sequence_type: SequenceType, meta: dict, evaluation_params: dict = None) -> None:
        self.sequence = sequence
        self.sequence_type = sequence_type
        self.meta = meta
        self.evaluation_params = evaluation_params
        