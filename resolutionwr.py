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


import copy
import json
import math
import random

import numpy as np

import psychopy

import template as template


psychopy.logging.console.setLevel(psychopy.logging.CRITICAL)  # Avoid error output


class ResolutionWR(template.BaseExperiment):
    """
    ...
    """
    def __init__(self, set_sizes, trials_per_set_size, distance_from_fixation, min_color_dist,
                 colorwheel_path, stim_size, sample_time, **kwargs):
        """
        ...
        """
        self.set_sizes = set_sizes
        self.trials_per_set_size = trials_per_set_size

        self.distance_from_fixation = distance_from_fixation
        self.stim_size = stim_size

        self.mouse = None

        self.min_color_dist = min_color_dist

        self.sample_time = sample_time

        self.color_wheel = self._load_color_wheel(colorwheel_path)

        super().__init__(**kwargs)

    def _load_color_wheel(self, path):
        with open(path) as f:
            color_wheel = json.load(f)

        color_wheel = [template.convert_color_value(i) for i in color_wheel]

        return np.array(color_wheel)

    def calculate_locations(self, set_size):
        angle_dist = 360 / set_size
        rotation = random.randint(0, angle_dist - 1)
        angles = [int(i * angle_dist + rotation + random.randint(-5, 5)) for i in range(set_size)]

        locations = [(self.distance_from_fixation * math.cos(math.radians(i)),
                      self.distance_from_fixation * math.sin(math.radians(i)))
                     for i in angles]

        return locations

    def _check_dist(self, attempt, colors):
        for c in colors:
            raw_dist = abs(c - attempt)
            dist = min(raw_dist, 360 - raw_dist)

            if dist < self.min_color_dist:
                return False

        return True

    def generate_color_indexes(self, set_size):
        colors = []

        while len(colors) < set_size:
            attempt = random.randint(0, 359)
            if self._check_dist(attempt, colors):
                colors.append(attempt)

        return colors

    def make_trial(self, set_size):
        color_indexes = self.generate_color_indexes(set_size)
        color_values = [self.color_wheel[i] for i in color_indexes]
        wheel_rotations = [random.randint(0, 359) for _ in range(set_size)]
        locations = self.calculate_locations(set_size)

        trial = {
            'set_size': set_size,
            'color_indexes': color_indexes,
            'color_values': color_values,
            'wheel_rotations': wheel_rotations,
            'locations': locations
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

    def display_blank(self, wait_time):
        """
        ...
        """
        self.experiment_window.flip()

        psychopy.core.wait(wait_time)

    def display_stimuli(self, coordinates, colors):
        """
        ...
        """

        for pos, color in zip(coordinates, colors):
            psychopy.visual.Circle(
                self.experiment_window, radius=self.stim_size, pos=pos, fillColor=color,
                units='deg', lineColor=None).draw()

        self.experiment_window.flip()

        psychopy.core.wait(self.sample_time)

    def draw_color_wheels(self, coordinates, wheel_rotations):
        mask = np.zeros([100, 1])
        mask[-30:] = 1

        for pos, rot in zip(coordinates, wheel_rotations):
            rotated_wheel = np.roll(self.color_wheel, rot, axis=0)
            tex = np.repeat(rotated_wheel[np.newaxis, :, :], 360, 0)

            psychopy.visual.RadialStim(
                self.experiment_window, tex=tex, mask=mask, pos=pos, angularRes=256,
                angularCycles=1, interpolate=False, size=self.stim_size * 2).draw()

    def _calc_mouse_color(self, mouse_pos):
        frame = np.array(self.experiment_window._getFrame())  # Uses psychopy internal function

        x_correction = self.experiment_window.size[0] / 2
        y_correction = self.experiment_window.size[1] / 2

        x = int(psychopy.tools.monitorunittools.deg2pix(mouse_pos[0], self.experiment_monitor) + x_correction)
        y = self.experiment_window.size[1] - int(psychopy.tools.monitorunittools.deg2pix(mouse_pos[1], self.experiment_monitor) + y_correction)

        try:
            color = frame[y, x, :]
        except IndexError:
            color = None

        return color

    def _calc_mouse_position(self, coordinates, mouse_pos):
        dists = [np.linalg.norm(np.array(i) - np.array(mouse_pos) / 2) for i in coordinates]
        closest_dist = min(dists)

        if closest_dist < 4:
            return coordinates[np.argmin(dists)]
        else:
            return None

    def _response_loop(self, coordinates, wheel_rotations):
        temp_coordinates = copy.copy(coordinates)
        temp_rotations = copy.copy(wheel_rotations)

        resp_colors = [0] * len(coordinates)

        while True:
            self.draw_color_wheels(temp_coordinates, temp_rotations)

            lclick, _, _ = self.mouse.getPressed()

            mouse_pos = self.mouse.getPos()
            px_color = self._calc_mouse_color(mouse_pos)

            if px_color is not None and not np.array_equal(px_color, np.array([128, 128, 128])):
                preview_pos = self._calc_mouse_position(temp_coordinates, mouse_pos)

                if preview_pos:
                    if lclick:
                        color_index = coordinates.index(preview_pos)
                        resp_colors[color_index] = px_color
                        del temp_rotations[temp_coordinates.index(preview_pos)]
                        temp_coordinates.remove(preview_pos)

                        if not temp_coordinates:
                            return resp_colors
                    else:
                        psychopy.visual.Circle(
                            self.experiment_window, radius=self.stim_size / 2, pos=preview_pos,
                            fillColor=template.convert_color_value(px_color), units='deg',
                            lineColor=None).draw()

            self.experiment_window.flip()

    def get_response(self, coordinates, wheel_rotations):
        self.draw_color_wheels(coordinates, wheel_rotations)

        self.experiment_window.flip()

        if not self.mouse:
            self.mouse = psychopy.event.Mouse(visible=False, win=self.experiment_window)

        self.mouse.setVisible(1)
        self.mouse.clickReset()

        resp_colors = self._response_loop(coordinates, wheel_rotations)

        self.mouse.setVisible(0)

        return resp_colors

    def run_trial(self, trial):
        self.display_blank(1)
        self.display_stimuli(trial['locations'], trial['color_values'])
        self.display_blank(1)

    def run(self):
        self.open_window(screen=0)

        block = self.make_block()

        self.run_trial(block[0])

        self.quit_experiment()


o = ResolutionWR(
    set_sizes=[5], trials_per_set_size=5, distance_from_fixation=8,
    colorwheel_path='colors.json', stim_size=1.5, sample_time=2, min_color_dist=25,
    experiment_name='ResolutionWR', data_fields=[], monitor_distance=90)
o.run()
