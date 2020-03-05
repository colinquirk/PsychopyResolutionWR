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
import errno
import json
import math
import os
import random
import sys

import numpy as np

import psychopy

import template as template

# Things you probably want to change
set_sizes = [1, 2, 4, 6]
trials_per_set_size = 5
number_of_blocks = 2

sample_time = 2
monitor_distance = 90

experiment_name = 'ResolutionWR'

data_directory = os.path.join(
    os.path.expanduser('~'), 'Desktop', experiment_name, 'Data')

instruct_text = [
    ('Welcome to the experiment. Press space to begin.'),
    ('In this experiment you will be remembering colors.\n\n'
     'Each trial will start with a blank screen.\n'
     'Then, a number of circles with different colors will appear.\n'
     'Remember as many colors as you can.\n\n'
     'After a short delay, color wheels will appear.\n\n'
     'Match the color wheel to the color that appeared in that position.\n'
     'Click the mouse button until the wheel disappears.\n'
     'If you are not sure, just take your best guess.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to start.'),
]

# Things you probably don't need to change, but can if you want to
colorwheel_path = 'colors.json'

distance_from_fixation = 6
stim_size = 1.5
min_color_dist = 25

data_fields = [
    'Subject',
    'Block',
    'Trial',
    'LocationNumber',
    'ClickNumber',
    'Timestamp',
    'SetSize',
    'LocationX',
    'LocationY',
    'ColorIndex',
    'TrueColor',
    'RespColor',
    'Error',
    'RT',
]

gender_options = [
    'Male',
    'Female',
    'Other/Choose Not To Respond',
]

hispanic_options = [
    'Yes, Hispanic or Latino/a',
    'No, not Hispanic or Latino/a',
    'Choose Not To Respond',
]

race_options = [
    'American Indian or Alaskan Native',
    'Asian',
    'Pacific Islander',
    'Black or African American',
    'White / Caucasian',
    'More Than One Race',
    'Choose Not To Respond',
]

# Add additional questions here
questionaire_dict = {
    'Session': 1,
    'Age': 0,
    'Gender': gender_options,
    'Hispanic:': hispanic_options,
    'Race': race_options,
}

# This is the logic that runs the experiment
# Change anything below this comment at your own risk
psychopy.logging.console.setLevel(psychopy.logging.CRITICAL)  # Avoid error output


class ResolutionWR(template.BaseExperiment):
    """
    ...
    """
    def __init__(self, set_sizes, trials_per_set_size, number_of_blocks, distance_from_fixation,
                 min_color_dist, colorwheel_path, stim_size, sample_time, data_directory,
                 questionaire_dict, instruct_text, **kwargs):
        """
        ...
        """
        self.set_sizes = set_sizes
        self.trials_per_set_size = trials_per_set_size
        self.number_of_blocks = number_of_blocks

        self.distance_from_fixation = distance_from_fixation
        self.stim_size = stim_size

        self.questionaire_dict = questionaire_dict
        self.data_directory = data_directory

        self.instruct_text = instruct_text

        self.min_color_dist = min_color_dist

        self.sample_time = sample_time

        self.color_wheel = self._load_color_wheel(colorwheel_path)

        self.mouse = None

        super().__init__(**kwargs)

    def chdir(self):
        """Changes the directory to where the data will be saved."""
        try:
            os.makedirs(self.data_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        os.chdir(self.data_directory)

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
        y = (self.experiment_window.size[1] -
             int(psychopy.tools.monitorunittools.deg2pix(mouse_pos[1], self.experiment_monitor) + y_correction))

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
        rts = [0] * len(coordinates)
        click_order = [0] * len(coordinates)

        click = 1

        self.mouse.clickReset()

        self.draw_color_wheels(temp_coordinates, temp_rotations)
        self.experiment_window.flip()

        while True:
            if psychopy.event.getKeys(keyList=['q']):
                self.quit_experiment()

            (lclick, _, _), (rt, _, _) = self.mouse.getPressed(getTime=True)

            mouse_pos = self.mouse.getPos()
            px_color = self._calc_mouse_color(mouse_pos)

            if px_color is not None and not np.array_equal(px_color, np.array([128, 128, 128])):
                preview_pos = self._calc_mouse_position(temp_coordinates, mouse_pos)

                if preview_pos:
                    if lclick:
                        resp_colors[coordinates.index(preview_pos)] = px_color
                        rts[coordinates.index(preview_pos)] = rt
                        click_order[coordinates.index(preview_pos)] = click
                        click += 1

                        del temp_rotations[temp_coordinates.index(preview_pos)]
                        temp_coordinates.remove(preview_pos)

                        if not temp_coordinates:
                            return resp_colors, rts, click_order
                    else:
                        psychopy.visual.Circle(
                            self.experiment_window, radius=self.stim_size / 2, pos=preview_pos,
                            fillColor=template.convert_color_value(px_color), units='deg',
                            lineColor=None).draw()

            self.draw_color_wheels(temp_coordinates, temp_rotations)
            self.experiment_window.flip()

    def get_response(self, coordinates, wheel_rotations):
        if not self.mouse:
            self.mouse = psychopy.event.Mouse(visible=False, win=self.experiment_window)

        self.mouse.setVisible(1)
        psychopy.event.clearEvents()

        resp_colors, rts, click_order = self._response_loop(coordinates, wheel_rotations)

        self.mouse.setVisible(0)

        return resp_colors, rts, click_order

    def calculate_error(self, color_index, resp_color):
        row_index = np.where((self.color_wheel == resp_color).all(axis=1))[0]

        if row_index.shape[0] < 1:
            return None  # if empty, return None

        raw_error = row_index[0] - color_index
        if raw_error >= -180 and raw_error <= 180:
            error = raw_error
        elif raw_error < -180:
            error = 360 + raw_error
        else:
            error = raw_error - 360

        return error

    def send_data(self, data):
        """Updates the experiment data with the information from the last trial.

        This function is seperated from run_trial to allow additional information to be added
        afterwards.

        Parameters:
        data -- A dict where keys exist in data_fields and values are to be saved.
        """
        self.update_experiment_data(data)

    def run_trial(self, trial, block_num, trial_num):
        self.display_blank(1)
        self.display_stimuli(trial['locations'], trial['color_values'])
        self.display_blank(1)
        resp_colors, rts, click_order = self.get_response(trial['locations'], trial['wheel_rotations'])

        data = []
        timestamp = psychopy.core.getAbsTime()

        for i, (color, rt, click) in enumerate(zip(resp_colors, rts, click_order)):
            data.append({
                'Subject': self.experiment_info['Subject Number'],
                'Block': block_num,
                'Trial': trial_num,
                'LocationNumber': i + 1,
                'ClickNumber': click,
                'Timestamp': timestamp,
                'SetSize': trial['set_size'],
                'LocationX': trial['locations'][i][0],
                'LocationY': trial['locations'][i][1],
                'ColorIndex': trial['color_indexes'][i],
                'TrueColor': trial['color_values'][i],
                'RespColor': template.convert_color_value(color),
                'Error': self.calculate_error(trial['color_indexes'][i], template.convert_color_value(color)),
                'RT': rt,
            })

        return data

    def display_break(self):
        """Displays a break screen in between blocks.
        """

        break_text = 'Please take a short break. Press space to continue.'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def run(self):
        self.chdir()

        ok = self.get_experiment_info_from_dialog(self.questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        for block_num in range(self.number_of_blocks):
            block = self.make_block()
            for trial_num, trial in enumerate(block):
                data = self.run_trial(trial, block_num, trial_num)
                self.send_data(data)
            self.save_data_to_csv()
            if block_num + 1 != self.number_of_blocks:
                self.display_break()

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255])

        self.quit_experiment()


o = ResolutionWR(
    set_sizes=set_sizes, trials_per_set_size=trials_per_set_size,
    number_of_blocks=number_of_blocks, distance_from_fixation=distance_from_fixation,
    colorwheel_path=colorwheel_path, stim_size=stim_size, sample_time=sample_time,
    min_color_dist=min_color_dist, questionaire_dict=questionaire_dict,
    data_directory=data_directory, experiment_name=experiment_name,
    instruct_text=instruct_text, data_fields=data_fields,
    monitor_distance=monitor_distance)
o.run()
