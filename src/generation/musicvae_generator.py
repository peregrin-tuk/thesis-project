from . import AbstractGenerator
from enum import Enum
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel

class Checkpoint(Enum):
    MEL_2BAR = 0  # cat-mel_2bar_big
    MEL_16BAR = 1 # hierdec-mel_16bar

class MusicVAEGenerator(AbstractGenerator):

    def __init__(self, checkpoint = Checkpoint.MEL_2BAR):
        super().__init__()
    