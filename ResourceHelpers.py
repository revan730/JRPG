# -*- coding: utf-8 -*-
import os
import pickle as pic


class StringsHelper:
    def __init__(self, locale):
        self.res_dir = "resources{}strings".format(os.sep)
        self.locale = locale

    def get_strings(self, file_name):
        """
        Gets all strings from file in form of dictionary
        :param file_name: Name of strings file (without locale code)
        :return: Dict with pairs string name - value
        """
        path = os.path.join(self.res_dir, file_name + "_" + self.locale)
        file = open(path, "rb")
        strings = pic.load(file)

        return strings


class SettingsHelper:
    def __init__(self):
        self.settings_file = 'settings'
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file,'rb') as f:
                try:
                    self.settings = pic.load(f)
                except pic.UnpicklingError:
                    raise RuntimeError('Unable to read settings file')

    def get(self, key, default):
        if key in self.settings.keys():
            return self.settings[key]
        else:
            return default

    def set(self, key, value):
        self.settings.update({key: value})
        self.close()
        self.load()

    def close(self):
        with open(self.settings_file, 'wb') as f:
                pic._dump(self.settings, f)

    def __del__(self):
        self.close()

class AnimationsHelper:
    def __init__(self):
        self.res_dir = "resources{}sprites".format(os.sep)

    def get_animation(self, creature, group):
        """
        Get list of tuples with paths to animation sprites
        :param creature: name of animated creature
        :param group: group of animation eg. 'down', 'up'
        :return: list of tuple of string
        """
        anim = []

        for x in range(1, 3):
            anim.append(('{res}{sep}{creat}{sep}{group}_{x}.gif').format(res=self.res_dir, sep=os.sep, creat=creature, group=group, x=x))

        return anim

class MapsHelper:
    @staticmethod
    def get_map(map_name):
        res_dir = 'resources{}maps'.format(os.sep)
        return '{res}{sep}{name}.tmx'.format(res=res_dir, sep= os.sep, name=map_name)