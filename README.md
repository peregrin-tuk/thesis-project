# thesis-project

Project Name: Rule-Based Adaptation System for Generated Musical Sequences and its Data-Driven Evaluation

Author: Eric Thalhammer

Supervisors: Ulrich Bodenhofer, Jeremiah Diephuis


Abstract:

Research and implementation of a modular hybrid system that leverages third-party pre-trained machine learning models next to rule-based adaptation steps based on music theory and music cognition to generate call-and-response pairs. The calls are user-selected input melodies; the responses are generated melodies adapted to the calls by the implemented rule-based adaptation system.
A data-driven evaluation framework was included in the system to facilitate the instant evaluation of generated melodies using musically informed parameters.


Note:

The pre-trained MusicVAE Checkpoints are not included but can be downloaded from https://github.com/magenta/magenta/tree/master/magenta/models/music_vae (cat-mel_2bar_big and hierdec-mel_16bar). The two tar-files have to be placed in the models/vae folder for the application to run correctly.