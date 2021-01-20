import os
import tensorflow as tf
from magenta.models.music_vae import data
from .midime.midime_train import train
from .midime.configs import CONFIG_MAP, update_config
from . import AbstractGenerator

class MidiMeGenerator(AbstractGenerator):

    model = 'ae-cat-mel_2bar_big'
    config = CONFIG_MAP[model]
    pretrained_path =  os.path.abspath('../models/vae/cat-mel_2bar_big.ckpt')
    train_dir = os.path.abspath('../models/tmp/train/')

    def __init__(self):
        super().__init__()

    
    def trainFromMIDI(self, midis, num_steps=50):
        """
        docstring
        """


    def trainFromTfRecord(self, tfrecord_path, num_steps=50):
        """
        docstring
        """
        config_update_map = {}
        config_update_map['train_examples_path'] = tfrecord_path
        config_update_map['pretrained_path'] = self.pretrained_path
        
        self.config = update_config(self.config, config_update_map)

        train(
            train_dir=self.train_dir,
            config=self.config,
            dataset_fn=self.__dataset_fn,
            num_steps=num_steps,
        )


    def generate(self):
        pass


    def __dataset_fn(self):
        return data.get_dataset(
            self.config,
            tf_file_reader=tf.data.TFRecordDataset,
            is_training=True,
            cache_dataset=True
        )
