#!/usr/bin/env python

'''
    AutoProber launch program
'''

import sys
import os
# add to PYTHONPATH for dynamic importing
pwd = os.path.abspath(path='.')
folders = ['instruments','procedures','classes']
for i in folders:
    sys.path.append(os.path.join(pwd, i))

from classes import Initializer, GUI, plotter, ScriptController, maitre

if __name__ == '__main__':

    pl = plotter.NBPlot()

    # SYSTEM INITIALIZATION
    init = Initializer.Initializer()
    init.read_config()
    # STAGE GENERATION
    stages = init.generate_stages()

    if len(sys.argv) > 1 and (sys.argv[1] == '-s' or sys.argv[1] == '--script'):
        try:
            maitre = maitre.Maitre()
            print("Running script {}".format(sys.argv[2]))
            controller = ScriptController.ScriptController(maitre, stages, scriptName=sys.argv[2])
            controller.execute_script()
        except IndexError as e:
            print("Command line error: {}".format(e))
        except IOError as e:
            print("IO Error: {}".format(e))
        except KeyError as e:
            print("Error within the configuration file: {}".format(e))
        except Exception as e:
            print("Error: {}".format(e))
    else:
        # # DEBUG
        # import inspect
        # print inspect.getmodule(inspect.getmodule(inspect.getmodule(E_Stage).XYZ_Stage).StepMotor).Constructor_Counter
        # print inspect.getmodule(inspect.getmodule(inspect.getmodule(E_Stage).XYZ_Stage).StepMotor).Home_Counter
        # ##

        ### Create Instance of Window
        app = GUI.Application(stages = stages)
        ### Set Focus on windows to catch key strokes
        app.focus_set()
        ### Start Looping and wating for events
        app.mainloop()