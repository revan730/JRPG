# -*- coding: utf-8 -*-
import os
import pickle as pic


class StringsHelper:
    def __init__(self, locale):
        self.res_dir = "resources/strings"
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
                    pass

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

