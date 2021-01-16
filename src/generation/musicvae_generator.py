import itertools
from enum import Enum
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from . import AbstractGenerator

_CHECKPOINTS = {
    1: ['cat-mel_2bar_big',  'MEL_2BAR'],
    2: ['hierdec-mel_16bar', 'MEL_16BAR'],
}
Checkpoint = Enum(
    value='Checkpoint',
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _CHECKPOINTS.items()
    )
)


class MusicVAEGenerator(AbstractGenerator):
    """
    docstring
    """

    def __init__(self, checkpoint=Checkpoint.MEL_2BAR, batch_size=4):
        super().__init__()
        print("[GEN] Initializing Music VAE with checkpoint '" +
              Checkpoint[checkpoint].name + "'...")
        self.checkpoint = checkpoint
        self.model = TrainedModel(
            configs.CONFIG_MAP[Checkpoint[checkpoint].name],
            batch_size=batch_size,
            checkpoint_dir_or_path=AbstractGenerator.base_path + '/vae/' + Checkpoint[checkpoint].name + '.ckpt')
        print('[GEN] 🎉 Initialization finished!')


    def generate(self, length=8, temperature=1.0, amount=1):
        generated_sequence = self.model.sample(
            n=amount, length=length, temperature=temperature)

        return {
            'note_seq': generated_sequence,
            'meta': {
                'gen_dur': 0,
		        'model': 'MusicVAE',
		        'checkpoint': self.checkpoint.name,
		        'temperature':temperature	
            }
        }
