"""An estimation whole report experiment.

Author - Colin Quirk (cquirk@uchicago.edu)

Repo: https://github.com/colinquirk/PsychopyResolutionWR

...

Note: this code relies on my templateexperiments module. You can get
them from https://github.com/colinquirk/templateexperiments and either put it in the same folder
as this code or give the path to psychopy in the preferences.

Classes:
...
"""


import json
import random

import psychopy

import template as template


class ResolutionWR(template.BaseExperiment):
    """
    ...
    """
    def __init__(self, set_sizes, trials_per_set_size, distance_from_fixation, colorwheel_path):
        """
        ...
        """
        self.set_sizes = set_sizes
        self.trials_per_set_size = trials_per_set_size

        self.distance_from_fixation = distance_from_fixation

        self.color_wheel = self._load_color_wheel(colorwheel_path)

    def _load_color_wheel(self, path):
        with open(path) as f:
            color_wheel = json.load(f)

        return color_wheel

    def _calculate_locations(self):
        pass

    def make_trial(self, set_size):
        color_indexes = [random.randint(0, 359) for _ in range(set_size)]
        color_values = [self.color_wheel[i] for i in color_indexes]
        wheel_rotations = [random.randint(0, 359) for _ in range(set_size)]

        trial = {
            'set_size': set_size,
            'color_indexes': color_indexes,
            'color_values': color_values,
            'wheel_rotations': wheel_rotations
        }

        return trial

    def make_block(self):
        """Makes a block of trials.

        Returns a shuffled list of trials created by self.make_trial.
        """

        trial_list = []

        for set_size in self.set_sizes:
            for _ in range(self.trials_per_set_size):
                trial = self.make_trial(set_size)
                trial_list.append(trial)

        random.shuffle(trial_list)

        return trial_list


o = ResolutionWR(
    set_sizes=[4, 6, 8], trials_per_set_size=5, distance_from_fixation=2,
    colorwheel_path='colors.json')

