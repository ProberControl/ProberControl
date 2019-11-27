#!/usr/bin/env python

'''
        AutoProber launch program
'''
try:

    import sys
    import traceback
    import os
    # add to PYTHONPATH for dynamic importing
    # pwd = os.path.abspath(path='.')
    # folders = ['instruments','procedures','classes']
    # for i in folders:
    #     sys.path.append(os.path.join(pwd, i))

    def cleanUp(stages):
        '''Release instrument resources'''
        for stage in list(stages.values()):
            if getattr(stage, 'close', None) is not None:
                # NOTE only call close on instruments that have it
                # implemented
                stage.close()
        print('Instrument clean-up complete.')

    if __name__ == '__main__':
        from prober.classes import plotter

        pl = plotter.NBPlot()

        from prober.classes import Initializer, ScriptController, GUI, maitre, ScriptBuilderGUI
        import ScriptBuilder
        '''
        import imp
        import time
        
        GUI = imp.load_source("GUI", "./prober/classes/GUI.py")
        '''
        # SYSTEM INITIALIZATION
        init = Initializer.Initializer()
        init.read_config()
        # STAGE GENERATION
        stages = init.generate_stages()
        try:
           # ASK ABOUT GUI INITIALIZATION __> where is maitre passerd in? why work for scriptbuilder gui but not normal gui?
            while True:
                #ScriptBuilderGUI = imp.load_source("ScriptBuilderGUI", "./prober/classes/ScriptBuilderGUI.py")
                #GUI = imp.load_source("GUI", "./prober/classes/GUI.py")
                app = GUI.Application(stages = stages)
                app.focus_set()
            
                import time
            ### Start Looping and wating for events
                app.mainloop()
                #app.restartGUI(stages = stages)
                time.sleep(3)
            
        # stages clean-up
        finally:
            cleanUp(stages)
        
        
        
        
except:
    traceback.print_exc()
    input("Press Enter to close") # Python 2

'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
