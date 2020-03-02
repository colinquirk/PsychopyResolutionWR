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

import errno
import os

import numpy as np

import psychopy

import template as template


class ResolutionWR(template.BaseExperiment):
    """
    ...
    """
    def __init__():
        """
        ...
        """
        pass

    def chdir(self):
        """Changes the directory to where the data will be saved.
        """

        try:
            os.makedirs(self.data_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        os.chdir(self.data_directory)

    def make_block(self):
        pass

    def _too_close(self, attempt, locs):
        """Checks that an attempted location is valid.

        This method is used by generate_locations to ensure the min_distance condition is followed.

        Parameters:
        attempt -- A list of two values (x,y) in visual angle.
        locs -- A list of previous successful attempts to be checked.
        """
        if np.linalg.norm(np.array(attempt)) < self.min_distance:
            return True  # Too close to center

        for loc in locs:
            if np.linalg.norm(np.array(attempt) - np.array(loc)) < self.min_distance:
                return True  # Too close to another square

        return False

    def generate_locations(self):
        pass

    def make_trial(self):
        pass

    def display_break(self):
        """Displays a break screen in between blocks.
        """

        break_text = 'Please take a short break. Press space to continue.'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def display_fixation(self, wait_time):
        """Displays a fixation cross. A helper function for self.run_trial.

        Parameters:
        wait_time -- The amount of time the fixation should be displayed for.
        """

        psychopy.visual.TextStim(
            self.experiment_window, text='+', color=[-1, -1, -1]).draw()
        self.experiment_window.flip()

        psychopy.core.wait(wait_time)

    def display_stimuli(self):
        pass

    def display_test(self):
        pass

    def get_response(self):
        pass

    def run_trial(self):
        pass

    def run(self):
        pass
