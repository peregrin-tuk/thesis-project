import os
from enum import Enum

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class SequenceType(Enum):
    REC_INPUT = 0
    FILE_INPUT = 1
    GEN_BASE = 2
    OUTPUT = 3
