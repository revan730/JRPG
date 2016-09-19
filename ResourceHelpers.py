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
