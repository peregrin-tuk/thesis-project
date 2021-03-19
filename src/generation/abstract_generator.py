from abc import ABC, abstractmethod
from pathlib import Path
from definitions import ROOT_DIR

class AbstractGenerator(ABC):

    models_base_path = ROOT_DIR / Path('/models')

    @abstractmethod
    def __init__(self):
        pass
    