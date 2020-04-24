#
# Laying out a tkinter grid
#
# Please also find two images:
#    GridLayout.png and screenshot.png
# Credit: Modified by Larz60+ From the original:
#    'http://www.tkdocs.com/tutorial/grid.html'
#
from tkinter import *
from tkinter import ttk


class ResizableWindow:
    def __init__(self, parent):
        self.parent = parent
        self.f1_style = ttk.Style()
        self.f1_style.configure('My.TFrame', background='#334353')
        self.f1 = ttk.Frame(self.parent, style='My.TFrame', padding=(3, 3, 12, 12))  # added padding

        self.f1.grid(column=0, row=0, sticky=(N, S, E, W))  # added sticky
        self.f2 = ttk.Frame(self.f1, borderwidth=5, relief="sunken", width=200, height=100)
        self.namelbl = ttk.Label(self.f1, text="Name")
        self.name = ttk.Entry(self.f1)

        self.onevar = BooleanVar()
        self.twovar = BooleanVar()
        self.threevar = BooleanVar()

        self.onevar.set(True)
        self.twovar.set(False)
        self.threevar.set(True)

        self.one = ttk.Checkbutton(self.f1, text="One", variable=self.onevar, onvalue=True)
        self.two = ttk.Checkbutton(self.f1, text="Two", variable=self.twovar, onvalue=True)
        self.three = ttk.Checkbutton(self.f1, text="Three", variable=self.threevar, onvalue=True)
        self.ok = ttk.Button(self.f1, text="Okay")
        #self.test = ttk.Entry(self.f1)
        self.cancel = ttk.Button(self.f1, text="Cancel")

        self.f1.grid(column=0, row=0, sticky=(N, S, E, W))  # added sticky
        self.f2.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=(N, S, E, W))  # added sticky
        self.namelbl.grid(column=3, row=0, columnspan=2, sticky=(N, W), padx=5)  # added sticky, padx
        self.name.grid(column=3, row=1, columnspan=2, sticky=(N, E, W), pady=5, padx=5)  # added sticky, pady, padx
        self.one.grid(column=0, row=3)
        self.two.grid(column=1, row=3)
        self.three.grid(column=2, row=3)
        self.ok.grid(column=3, row=3)
        self.cancel.grid(column=4, row=3)
        #self.test.grid(column= 5, row = 3)

        # added resizing configs
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.f1.columnconfigure(0, weight=3)
        self.f1.columnconfigure(1, weight=3)
        self.f1.columnconfigure(2, weight=3)
        self.f1.columnconfigure(3, weight=3)
        self.f1.columnconfigure(4, weight=3)
        self.f1.rowconfigure(1, weight=1)
        #self.f1.columnconfigure(5, weight = 1)

    def get_widget_attributes(self):
        all_widgets = self.f1.winfo_children()
        for widg in all_widgets:
            print('\nWidget Name: {}'.format(widg.winfo_class()))
            keys = widg.keys()
            for key in keys:
                print("Attribute: {:<20}".format(key), end=' ')
                value = widg[key]
                vtype = type(value)
                print('Type: {:<30} Value: {}'.format(str(vtype), value))


def main():
    root = Tk()
    rw = ResizableWindow(root)
    #rw.get_widget_attributes()
    root.mainloop()


if __name__ == '__main__':
    main()
