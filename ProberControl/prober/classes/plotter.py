from __future__ import print_function
import time
try:
    from multiprocessing import Process, Pipe
except ImportError:
    from processing import Process, Pipe

import numpy as np

class close_handler(object):
    def __init__(self, shelled_handle):
        self.sh = shelled_handle

    def __call__(self, evt):
        self.sh[0].after_cancel(self.sh[1])

class ProcessPlotter(object):

    def __init__(self):
        self.title = ''
        self.xlabel = ''
        self.ylabel = ''
        self.DataList = []
        self.clear = False
        self.sh = [None, None]

    def terminate(self):
        import matplotlib.pyplot as plt
        self.fig.canvas.manager.window.after_cancel()
        plt.close('all')


    def update_fig(self):
            import matplotlib.pyplot as plt
            while 1:
                if not self.pipe.poll():
                    break

                command = self.pipe.recv()

                if command is None:
                    self.terminate()
                    return False

                else:

                    self.DataList=command[0][:]

                    self.title  = command[1]
                    self.xlabel = command[2]
                    self.ylabel = command[3]
                    self.clear  = command[4]

                    if self.clear:
                        self.fig.clear()
                        self.ax = self.fig.add_subplot(111)

                    plt.title(self.title)
                    plt.xlabel(self.xlabel)
                    plt.ylabel(self.ylabel)

                    self.ax.plot(zip(*self.DataList)[0], zip(*self.DataList)[1], 'b')

            self.fig.canvas.draw()
            try:
                self.sh[1] = self.fig.canvas.manager.window.after(1000,self.update_fig)
            except Exception as e:
                print(e)
            return True



    def __call__(self, pipe):
        self.pipe = pipe

        while not self.pipe.poll():
            time.sleep(0.15)

        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt

        while 1:

            print('starting plotter...')
            handle_close = close_handler(self.sh)
            self.fig = plt.figure()
            self.sh[0] = self.fig.canvas.manager.window
            self.fig.canvas.mpl_connect('close_event', handle_close)
            self.ax = self.fig.add_subplot(111)
            self.update_fig()

            plt.show()
            while not self.pipe.poll():
                time.sleep(0.15)

class Singleton(object):
    ''' Singleton paradigm implementation '''
    def __init__(self, u_class):
        self.u_class = u_class
        self.instance = None
    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.u_class(*args, **kwargs)
        return self.instance


@Singleton        # apply the Singleton decorator
class NBPlot(object):
    def __init__(self):
        self.plot_pipe, plotter_pipe = Pipe()
        self.plotter = ProcessPlotter()
        self.plot_process = Process(target = self.plotter,
                                    args = (plotter_pipe,))
        self.plot_process.daemon = True
        self.plot_process.start()
        self.clear = True

    def set_clear(self,clear=True):
        if clear:
            self.clear = True
        else:
            self.clear = False

    def plot(self,data,title='',xaxis='',yaxis=''):
        send = self.plot_pipe.send

        datas = [data,title,xaxis,yaxis,self.clear]
        send(datas)

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
