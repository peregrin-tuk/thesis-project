import os
import time
import tensorflow as tf
from magenta.models.music_vae import data
from magenta.models.music_vae.configs import CONFIG_MAP as VAE_CONFIG_MAP
from note_seq import midi_to_note_sequence
from .midime.midime_train import train
from .midime.trained_model import TrainedModel
from .midime.configs import CONFIG_MAP, update_config
from . import AbstractGenerator

class MidiMeGenerator(AbstractGenerator):

    model = 'cat-mel_2bar_big'
    config = CONFIG_MAP['ae-' + model]
    vae_config = VAE_CONFIG_MAP[model]
    pretrained_path =  os.path.abspath('../models/vae/cat-mel_2bar_big.ckpt')
    train_dir = os.path.abspath('../models/tmp/train/')

    def __init__(self):
        super().__init__()

    
    def trainFromMIDI(self, midis, num_steps=50):
        """
        Trains the MidiMe model based on a list of midi objects.

        Args:
            tfrecord_path (List[PrettyMIDI]): list of midi objects
            num_steps (int): Number of training steps (default = 50)

        """
        print('[GEN] Writing MIDIs to tfrecord...')
        t1 = time.time()
        tfrecord = os.path.expanduser('../models/midimi/tmp/training-data-cache.tfrecord')

        for midi in midis:
            note_seq = midi_to_note_sequence(midi)

            with tf.io.TFRecordWriter(tfrecord) as writer:
                writer.write(note_seq.SerializeToString())
        t2 = time.time()
        print('[GEN] 🎉 Done writing in ' + t2-t1 + ' sec.')

        self.trainFromTfRecord(tfrecord, num_steps)



    def trainFromTfRecord(self, tfrecord_path, num_steps=50):
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
        print('[GEN] 🎉 Finished training in ' + t2-t1 + ' sec.')



    def generate(self, length_in_quarters=8, temperature=0.4):
        
        t1 = time.time()
        print('[GEN] Loading model...')
        model = TrainedModel(
            vae_config=self.vae_config,
            model_config=self.config,
            batch_size=1,
            vae_checkpoint_dir_or_path=self.pretrained_path,
            model_checkpoint_dir_or_path=self.train_dir,
            model_var_pattern=['latent'],
            session_target=''
        )

        print('[GEN] Sampling from model...')
        generated_sequence = model.sample(n=1, length=length_in_quarters*4, temperature=temperature)
        t2 = time.time()

        return {
            'sequence': generated_sequence[0],
            'meta': {
                'gen_dur': t2-t1,
		        'model': 'MidiMe',
		        'checkpoint': self.model,
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
