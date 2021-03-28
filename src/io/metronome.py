from pathlib import Path
import asyncio
import pygame

from definitions import ROOT_DIR

sound_file_path = ROOT_DIR / Path('midi/click.wav')

class Metronome():

    def __init__(self, bpm: int):
        self.ms = self.__bpm_to_ms(bpm)
        self.on = False
        pygame.init()
        self.sound = pygame.mixer.Sound(sound_file_path)

    def __del__(self):
        self.off = True
        pygame.quit()


    ### PUBLIC METHODS

    def start(self):
        self.on = True
        self.__run()

    def stop(self):
        self.on = False

    def change_bpm(self, bpm: int):
        self.ms = self.__bpm_to_ms(bpm)

    @property
    def bpm(self):
        return self.__ms_to_bpm(self.ms)


    ### PRIVATE METHODS

    def __run(self):  
        clock = pygame.time.Clock()
        TICK = pygame.USEREVENT + 1
        pygame.time.set_timer(TICK, self.ms)

        # debug output
        timer = pygame.time.get_ticks
        start = now = timer()
        # end

        while self.on:
            for event in pygame.event.get():
                if event.type == TICK:

                    # debug output
                    now = timer()
                    print(now - start)
                    start = now
                    # end

                    self.sound.play()

            clock.tick()

    def __bpm_to_ms(self, bpm: int) -> int:
        return int(60000 / bpm)

    def __ms_to_bpm(self, ms: int) -> int:
        return int(60000 / ms)