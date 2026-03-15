import pygame

from constants import (
    AUDIO_ENABLED,
    MUSIC_ENABLED,
    SOUND_VOLUME,
    MUSIC_VOLUME,
)


class AudioManager:
    def __init__(self):
        self.audio_available = False
        self.sounds = {}
        self.current_music_path = None

        if not AUDIO_ENABLED:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.audio_available = True
        except pygame.error:
            self.audio_available = False

    def load_sound(self, name, path):
        if not self.audio_available:
            self.sounds[name] = None
            return

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(SOUND_VOLUME)
            self.sounds[name] = sound
        except (pygame.error, FileNotFoundError):
            self.sounds[name] = None

    def play_sound(self, name):
        if not self.audio_available:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self, music_path, loop=True, force_restart=False):
        if not self.audio_available or not MUSIC_ENABLED:
            return

        if not force_restart and self.current_music_path == music_path:
            return

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music_path = music_path
        except (pygame.error, FileNotFoundError):
            pass

    def stop_music(self):
        if self.audio_available and MUSIC_ENABLED:
            pygame.mixer.music.stop()
            self.current_music_path = None

    def pause_music(self):
        if self.audio_available and MUSIC_ENABLED:
            pygame.mixer.music.pause()

    def unpause_music(self):
        if self.audio_available and MUSIC_ENABLED:
            pygame.mixer.music.unpause()