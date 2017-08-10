import sys
import os

# add to PYTHONPATH for dynamic importing
pwd = os.path.abspath(path='./..')
folders = ['instruments','procedures','classes']
sys.path.append(pwd)
for i in folders:
    sys.path.append(os.path.join(pwd, i))

from classes import Initializer, GUI, plotter, ScriptController, maitre

def main(args):

    pl = plotter.NBPlot()

    # SYSTEM INITIALIZATION
    init = Initializer.Initializer()
    init.read_config()
    # STAGE GENERATION
    stages = init.generate_stages()

    try:
        maitre_actual = maitre.Maitre()
        print("Running script {}".format(args))
        controller = ScriptController.ScriptController(maitre_actual, stages, args)
        controller.execute_script()
    except IndexError as e:
        print("Command line error: {}".format(e))
    except IOError as e:
        print("IO Error: {}".format(e))
    except KeyError as e:
        print("Error within the configuration file: {}".format(e))
    except Exception as e:
       print("Error: {}".format(e))