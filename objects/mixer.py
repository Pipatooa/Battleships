import json

import pygame


class Mixer:
    """
    Object containing information about sounds
    """

    def __init__(self):
        pygame.mixer.init()

        self.CHANNEL_NUMBER = 16
        self.SOUNDS_ENABLED = True

        pygame.mixer.set_num_channels(self.CHANNEL_NUMBER)

        with open("sounds.json") as file:
            self.sounds = json.load(file)

        for name, file in self.sounds.items():
            self.sounds[name] = pygame.mixer.Sound(file)

        self.next_channel = 0

    def play_sound(self, name):
        if not self.SOUNDS_ENABLED:
            return

        self.next_channel += 1
        if self.next_channel >= self.CHANNEL_NUMBER:
            self.next_channel = 0

        pygame.mixer.Channel(self.next_channel).play(self.sounds[name])