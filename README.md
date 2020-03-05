A customizable and extendable whole report estimation experiment written in Psychopy (adapted from Adam, Vogel, & Awh, 2017). Designed for the desktop.

![](exp_example.gif)

Author - Colin Quirk (cquirk@uchicago.edu)

Repo: https://github.com/colinquirk/PsychopyResolutionWR

This is a common working memory paradigm used to provide a measure of working memory resolution across all items of a display.

This code can either be used directly or it can be inherited and extended.
If this file is run directly the defaults at the top of the page will be
used. To make simple changes, you can adjust any of these parameters or use the provided hooks.
For more in depth changes you will need to overwrite the methods yourself.

**Note**: this code relies on my templateexperiments module. You can get it from
https://github.com/colinquirk/templateexperiments and either put it in the same folder as this
code or give the path to psychopy in the preferences.



### Classes
* ResolutionWR -- The class that runs the experiment.
    

### Parameters
* colorwheel_path -- A string or Path describing the location of a json file containing
        a 360 length array of length 3 rgb arrays.
* data_directory -- Where the data should be saved.
* delay_time -- The number of seconds between the stimuli display and test.
* distance_from_fixation -- A number describing how far from fixation stimuli will
        appear in visual degrees.
* instruct_text -- The text to be displayed to the participant at the beginning of the experiment.
* iti_time -- The number of seconds in between a response and the next trial.
* min_color_dist -- The minimum number of degrees in color space between display items.
* number_of_blocks -- The number of blocks in the experiment.
* questionaire_dict -- Questions to be included in the dialog.
* sample_time -- The number of seconds the stimuli are on the screen for.
* set_sizes -- A list of all the set sizes.
        An equal number of trials will be shown for each set size.
* stim_size -- The size of the stimuli in visual degrees.
* trials_per_set_size -- The number of trials per set size per block.

Additional keyword arguments are sent to template.BaseExperiment().

### Methods
* calculate_locations -- Calculates locations for the upcoming trial with random jitter.
* calculate_error -- Calculates error in a response compared to the true color value.
* chdir -- Changes the directory to where the data will be saved.
* display_blank -- Displays a blank screen.
* display_break -- Displays a screen during the break between blocks.
* display_stimuli -- Displays the stimuli.
* draw_color_wheels -- Draws color wheels at stimuli locations with random rotation.
* generate_color_indexes -- Generates colors for a trial given the minimum distance.
* get_response -- Manages getting responses for all color wheels.
* make_block -- Creates a list of trials to be run.
* make_trial -- Creates a single trial dictionary.
* run -- Runs the entire experiment including optional hooks.
* run_trial -- Runs a single trial.
* send_data -- Updates the experiment data with the information from the last trial.

## Hooks

Hooks can be sent to the `run` method in order to allow for small changes to be made without having to completely rewrite the run method in a subclass.

#### Available Hooks

- setup_hook -- takes self, executed once the window is open.
- before_first_trial_hook -- takes self, executed after instructions are displayed.
- pre_block_hook -- takes self, block list, and block num
    Executed immediately before block start.
    Can optionally return an altered block list.
- pre_trial_hook -- takes self, trial dict, block num, and trial num
    Executed immediately before trial start.
    Can optionally return an altered trial dict.
    Can optionally return an altered trial dict.
- post_trial_hook -- takes self and the trial data, executed immediately after trial end.
    Can optionally return altered trial data to be stored.
- post_block_hook -- takes self, executed at end of block before break screen (including
    last block).
- end_experiment_hook -- takes self, executed immediately before end experiment screen.

#### Hook Example

For example, if you wanted a block of practice trials, you could simply define a function:

```
# Arbitrary function name
def my_before_first_trial_hook(self):
    # Self refers to the experiment object
    self.display_text_screen('We will now do a practice block.')
    practice_block = self.make_block()
    for trial_num, trial in enumerate(practice_block):
        self.run_trial(trial, 'practice', trial_num)
    self.display_break()
    self.display_text_screen('Good job! We will now start the real trials.')
```

Then simply pass the hook into run.

```
exp.run(before_first_trial_hook=my_before_first_trial_hook)
```

Just like that, you have modified the experiment without having to change anything about the underlying implementation!
