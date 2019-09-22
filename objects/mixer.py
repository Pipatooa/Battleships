import json
import os

import pygame

import vars


class Mixer:
    """
    Object containing information about sounds
    """

    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error:
            self.SOUNDS_ENABLED = False
            return

        self.CHANNEL_NUMBER = 16
        self.SOUNDS_ENABLED = vars.options["sounds_enabled"]

        pygame.mixer.set_num_channels(self.CHANNEL_NUMBER)

        with open(os.path.join(".", "sound_packs", vars.options["sound_pack"])) as file:
            self.sounds = {}

            for name, file in json.load(file).items():
                self.sounds[name] = pygame.mixer.Sound(os.path.join(".", file))

        self.next_channel = 0

    def play_sound(self, name):
        if not self.SOUNDS_ENABLED:
            return

        self.next_channel += 1
        if self.next_channel >= self.CHANNEL_NUMBER:
            self.next_channel = 0

        pygame.mixer.Channel(self.next_channel).play(self.sounds[name])
