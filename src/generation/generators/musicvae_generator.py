
import itertools
import time
from enum import Enum
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from src.generation import AbstractGenerator

_CHECKPOINTS = {
    1: ['cat-mel_2bar_big',  'MEL_2BAR'],
    2: ['hierdec-mel_16bar', 'MEL_16BAR'],
}


class MusicVAEGenerator(AbstractGenerator):
    """
    docstring
    """
    Checkpoint = Enum(
        value='Checkpoint',
        names=itertools.chain.from_iterable(
            itertools.product(v, [k]) for k, v in _CHECKPOINTS.items()
        )
    )

    def __init__(self, checkpoint=Checkpoint.MEL_2BAR, batch_size=4, log=None):
        super().__init__()
        self.log = log

        self.__log("[GEN] Initializing Music VAE with checkpoint '" +
              checkpoint.name + "'...")

        t1 = time.time()
        self.checkpoint = checkpoint
        self.model = TrainedModel(
            configs.CONFIG_MAP[str(checkpoint.name)],
            batch_size=batch_size,
            checkpoint_dir_or_path=str(AbstractGenerator.models_base_path) + '/vae/' + checkpoint.name + '.tar')
        t2 = time.time()
        
        self.__log('[GEN] 🎉 Initialization finished in ' + str(t2-t1) + ' sec.')


    def __log(self, msg: str):
        if self.log is None:
            print(msg)
        else:
            with self.log:
                print(msg)


    def generate(self, length_in_quarters=16, temperature=0.4):
        t1 = time.time()
        generated_sequence = self.model.sample(
            n=1, length=length_in_quarters*4, temperature=temperature)
        t2 = time.time()

        return {
            'sequence': generated_sequence[0],
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MusicVAE',
		        'checkpoint': self.checkpoint.name,
		        'temperature':temperature	
            }
        }

    def generateMultiple(self, number=10, length_in_quarters=8, temperature=0.4):
        t1 = time.time()
        generated_sequence = self.model.sample(
            n=number, length=length_in_quarters*4, temperature=temperature)
        t2 = time.time()

        return {
            'sequences': generated_sequence,
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MusicVAE',
		        'checkpoint': self.checkpoint.name,
		        'temperature':temperature	
            }
        }
