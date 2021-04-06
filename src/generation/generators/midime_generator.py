import time
from pathlib import Path
import tensorflow as tf
from enum import Enum
from magenta.models.music_vae import data
from magenta.models.music_vae.configs import CONFIG_MAP as VAE_CONFIG_MAP
from note_seq import midi_to_note_sequence
from .midime.midime_train import train
from .midime.trained_model import TrainedModel
from .midime.configs import CONFIG_MAP, update_config
from . import AbstractGenerator
from definitions import ROOT_DIR

_CHECKPOINTS = {
    1: ['cat-mel_2bar_big',  'MEL_2BAR'],
}
Checkpoint = Enum(
    value='Checkpoint',
    names=itertools.chain.from_iterable(
        itertools.product(v, [k]) for k, v in _CHECKPOINTS.items()
    )
)

class MidiMeGenerator(AbstractGenerator):

    checkpoint = 'cat-mel_2bar_big'
    config = CONFIG_MAP['ae-' + checkpoint]
    vae_config = VAE_CONFIG_MAP[checkpoint]
    pretrained_path =  ROOT_DIR / Path('/models/vae/cat-mel_2bar_big.ckpt')
    train_dir = ROOT_DIR / Path('/models/tmp/train/')

    def __init__(self):
        super().__init__()

    
    def trainFromMIDI(self, midis, num_steps=100):
        """
        Trains the MidiMe model based on a list of midi objects.

        Args:
            tfrecord_path (List[PrettyMIDI]): list of midi objects
            num_steps (int): Number of training steps (default = 50)

        """
        print('[GEN] Writing MIDIs to tfrecord...')
        t1 = time.time()
        tfrecord = ROOT_DIR / Path('/models/midime/tmp/training-data-cache.tfrecord')

        for midi in midis:
            note_seq = midi_to_note_sequence(midi)

            with tf.io.TFRecordWriter(tfrecord) as writer:
                writer.write(note_seq.SerializeToString())
        t2 = time.time()
        print('[GEN] 🎉 Done writing in ' + str(t2-t1) + ' sec.')

        self.trainFromTfRecord(tfrecord, num_steps)



    def trainFromTfRecord(self, tfrecord_path, num_steps=100):
        """
        Trains the MidiMe model based on a set of note_sequences serialized to a .tfrecord file.

        Args:
            tfrecord_path (str): Location of the .tfrecord file
            num_steps (int): Number of training steps (default = 50)

        """
        print('[GEN] Training MidiMe model...')
        t1 = time.time()
        config_update_map = {}
        config_update_map['train_examples_path'] = tfrecord_path
        config_update_map['pretrained_path'] = self.pretrained_path
        
        self.config = update_config(self.config, config_update_map)
        self.num_steps = num_steps

        train(
            train_dir=self.train_dir,
            config=self.config,
            dataset_fn=self.__dataset_fn,
            num_steps=num_steps,
        )
        t2 = time.time()
        self.train_dur = t2-t1
        print('[GEN] 🎉 Finished training in ' + str(t2-t1) + ' sec.')

        print('[GEN] Initializing constrainted VAE model...')
        t1 = time.time()
        self.model = TrainedModel(
            vae_config=self.vae_config,
            model_config=self.config,
            batch_size=1,
            vae_checkpoint_dir_or_path=self.pretrained_path,
            model_checkpoint_dir_or_path=self.train_dir,
            model_var_pattern=['latent'],
            session_target=''
        )
        t2 = time.time()
        self.train_dur += t2-t1
        print('[GEN] 🎉 Initialization finished in ' + str(t2-t1) + ' sec.')


    def initializeFromCheckpoint(self, path=train_dir):
        '''
        NOTE not sure if this works considering the configs might be incorrect if not trained within hte same object instance
        '''
        print('[GEN] Initializing constrainted VAE model...')
        t1 = time.time()
        self.model = TrainedModel(
            vae_config=self.vae_config,
            model_config=self.config,
            batch_size=1,
            vae_checkpoint_dir_or_path=self.pretrained_path,
            model_checkpoint_dir_or_path=path,
            model_var_pattern=['latent'],
            session_target=''
        )
        t2 = time.time()
        self.train_dur += t2-t1
        print('[GEN] 🎉 Initialization finished in ' + str(t2-t1) + ' sec.')



    def generate(self, length_in_quarters=16, temperature=0.4):
        
        t1 = time.time()
        generated_sequence = self.model.sample(n=1, length=length_in_quarters*4, temperature=temperature)
        t2 = time.time()

        return {
            'sequence': generated_sequence[0],
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MidiMe',
		        'checkpoint': self.checkpoint,
		        'temperature':temperature,
                'training_meta': {
                    'trained_on': [], # TODO add midi file refs (pass optional array to train() ?)
                    'train_dur': self.train_dur,
                    'steps': self.num_steps
                }	
            }
        }



    def generateMultiple(self, number=10, length_in_quarters=8, temperature=0.4):
        
        t1 = time.time()
        generated_sequences = self.model.sample(n=number, length=length_in_quarters*4, temperature=temperature)
        t2 = time.time()

        return {
            'sequences': generated_sequences,
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MidiMe',
		        'checkpoint': self.checkpoint,
		        'temperature':temperature,
                'training_meta': {
                    'trained_on': [], # TODO add midi file refs (pass optional array to train() ?)
                    'train_dur': self.train_dur,
                    'steps': self.num_steps
                }	
            }
        }


    def __dataset_fn(self):
        return data.get_dataset(
            self.config,
            tf_file_reader=tf.data.TFRecordDataset,
            is_training=True,
            cache_dataset=True
        )
