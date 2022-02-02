# FreES GUI toolkit library. Version 2

from time import sleep
from frees_lib2 import frees, f_range
from matplotlib import pyplot as plt
from os import system as sh
from sys import stdout
from tkinter import * 
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Button, Label, Entry


class frees_app:
    """FreES window and all of its controls and internal data."""

    def __init__(self, fp):
        self.window = Tk() 
        self.window.title("FreES - The Free, Open Source, Engineering Equation Solver")
        self.window.minsize(600, 400)
        self.current_file = fp
        Grid.rowconfigure(self.window, 1, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)

        numcols = 5 # Hard-coded here to parametrize later code.

        self.exprs_box = ScrolledText(self.window)
        self.exprs_box.grid(columnspan=numcols, column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.exprs_box.configure(state='normal')
        
        self.solve_button = Button(self.window, text = "Save/Solve",     command = self.open_solution_window)     # Solve Button 
        self.fs_button =    Button(self.window, text = "Open",           command = self.open_file_select)        # File Selection
        self.save_button =  Button(self.window, text = "Save",           command = self.save_file)               # Save Button
        self.plot_button =  Button(self.window, text = "New Plot",       command = self.open_plot_window)   # Plot Button
        self.unit_button =  Button(self.window, text = "Edit Unit Info", command = self.edit_unit_config)         # Edit Units Button
        self.label =        Label( self.window, text = "No File Selected")                                  # Label showing current file

        self.solve_button   .grid(column = 0, row = 0, sticky="ew")
        self.fs_button      .grid(column = 1, row = 0)
        self.save_button    .grid(column = 2, row = 0)
        self.plot_button    .grid(column = 3, row = 0)
        self.unit_button    .grid(column = 4, row = 0)
        self.label          .grid(columnspan = numcols, row = 2)


    def fetch_eqns(self):
        """Returns only the equations from the expressions box."""
        return self.exprs_box.get("0.0",END).strip()


    def open_file(self):
        """Returns the contents of a plain text file as a string."""
        with open(self.current_file, "r") as f:
            return f.read()

    # methods below this line are called by the GUI itself. 

    def open_solution_window(self):
        """Show the solution to the current system."""
        sw = solution_window(self)
        sw.window.mainloop()


    def open_plot_window(self):
        """Create a plot of an independent and dependent variable."""
        pw = plot_window(self)
        pw.window.mainloop()


    def open_file_select(self):
        """Open a file to edit in the FreES editor."""
        self.current_file = askopenfilename(initialdir = "~/Documents")
        self.label.configure(text = "Editing: " + self.current_file)
        self.exprs_box.delete("0.0",END)
        self.exprs_box.insert(END, self.open_file())


    def edit_unit_config(self):
        """Edit the units.json file."""
        sh("nano ./units.json")


    def save_file(self):
        """Write the current editor window's contents to file."""
        with open(self.current_file, "w") as f:
            f.write(self.fetch_eqns())


    def start(self):
        self.exprs_box.focus()
        self.window.mainloop()

        
class solution_window:
    """Window for displaying solution"""

    def __init__(self, parent:frees_app):
        self.window = Toplevel()
        self.parent = parent
        self.window.title("FreES - Solution Window")
        self.window.minsize(200,200)

        soln = frees(self.parent.fetch_eqns())
        soln.solve()
        
        duration = f"Solved in {round(soln.soln.duration, 5)} seconds."
        values = '\n'.join([f"{item} = {soln.soln.soln[item]}" for item in soln.soln.soln])
        unsolved = ', '.join([f"Line {i}" for i in soln.unsolved])
        
        # TODO: add the unsolved lines warning once it is fixed in frees_lib2.py
        soln_text = f"{duration}\n\n{values}" #\n\nUnsolved: {unsolved}"

        self.titlebar = Label(self.window, text = "Solution:\n=========")
        self.swtext = Label(self.window, text = soln_text)
        self.close_button = Button(self.window, text = "Close", command = self.close)

        self.titlebar       .grid(column = 0, row = 0)
        self.swtext         .grid(column = 0, row = 1, padx = 10, pady = 10)
        self.close_button   .grid(column = 0, row = 2)


    def close(self):
        self.window.destroy()


class plot_window:
    """Separate Tkinter window for plot generation."""

    def __init__(self, parent:frees_app):
        self.window = Tk()
        self.parent = parent
        self.window.title("FreES - Create New Plot")
        self.window.resizable(0, 0)

        plot_menu = Frame(self.window)
        plot_menu.grid(padx=10, pady=10)

        dmn_start = StringVar()
        dmn_end =   StringVar()
        dmn_size =  StringVar()
        dmn_size    .set("100") # TODO: get this to work. does not default to 100.
        ind_var =   StringVar()
        dep_var =   StringVar()
        ptitle =    StringVar()

        # Object initialization
        self.dstart_label = Label(plot_menu, text = "Start of Domain")
        self.dend_label =   Label(plot_menu, text = "End of Domain")
        self.dstep_label =  Label(plot_menu, text = "No. of points")
        self.iv_label =     Label(plot_menu, text = "Independent Var.")
        self.dv_label =     Label(plot_menu, text = "Dependent Var.")
        self.t_label =      Label(plot_menu, text = "Plot Title")

        self.dmn_start =    Entry(plot_menu, width = 30, textvariable = dmn_start)
        self.dmn_end =      Entry(plot_menu, width = 30, textvariable = dmn_end)
        self.dmn_size =     Entry(plot_menu, width = 30, textvariable = dmn_size)
        self.ind_var =      Entry(plot_menu, width = 30, textvariable = ind_var)
        self.dep_var =      Entry(plot_menu, width = 30, textvariable = dep_var)
        self.title =        Entry(plot_menu, width = 30, textvariable = ptitle)

        self.plot_button = Button(plot_menu, text = "Create Plot", command = self.plot)

        # Grid spacing
        self.dstart_label   .grid(column = 0, row = 0, sticky="nsew")
        self.dend_label     .grid(column = 0, row = 1, sticky="nsew")
        self.dstep_label    .grid(column = 0, row = 2, sticky="nsew")
        self.iv_label       .grid(column = 2, row = 0, sticky="nsew")
        self.dv_label       .grid(column = 2, row = 1, sticky="nsew")
        self.t_label        .grid(column = 2, row = 2, sticky="nsew")

        self.dmn_start      .grid(column = 1, row = 0, sticky="nsew")
        self.dmn_end        .grid(column = 1, row = 1, sticky="nsew")
        self.dmn_size       .grid(column = 1, row = 2, sticky="nsew")
        self.ind_var        .grid(column = 3, row = 0, sticky="nsew")
        self.dep_var        .grid(column = 3, row = 1, sticky="nsew")
        self.title          .grid(column = 3, row = 2, sticky="nsew")

        self.plot_button.grid(columnspan = 4, row = 3, sticky="nsew")


    def plot(self):
        """Plots a given dependent variable as a function of a given dependent variable"""
        domain = f_range(
            float(self.dmn_start.get()), 
            float(self.dmn_end.get()), 
            int(self.dmn_size.get())
            )
        y = []
        pb = prog_bar(int(self.dmn_size.get()), style="basic")

        self.plot_button.configure(text=pb.show())
        for x in domain:
            eqns = self.parent.fetch_eqns()
            system = frees(eqns.replace(self.ind_var.get(), str(x)))
            system.solve()
            y.append(system.soln.soln[self.dep_var.get()])
            
            pb.increment()
            self.plot_button.configure(text = pb.show())
            self.plot_button.update_idletasks()

        self.plot_button.configure(text="Create Plot")
        plt.plot(domain, y)
        plt.title(self.title.get())
        plt.show()


class prog_bar:
    """Generates a progress bar similar to the zypper package manager's."""
    def __init__(self, max_prog:int, style="basic"):
        self.style = style
        self.progress = 0.0
        self.max_prog = max_prog
        self.wheel = 0

    def increment(self, amount=1):
        self.progress += amount
        if self.wheel == 15:
            self.wheel = 0
        else: 
            self.wheel += 1


    def show(self, length=40, show_wheel=True):
        proportion = int(length*self.progress/self.max_prog)

        c = int(100*self.progress/self.max_prog)
        p = proportion + 1-len(str(c))
        f = length - proportion

        if show_wheel:
            wheel = ['/','/','/','/','-','-','-','-','\\','\\','\\','\\','|','|','|','|'][self.wheel]

        present = f'({wheel})'
        past = '|' * p
        future = '.' * f

        state = f"[{past}{present}{future}] {int(self.progress)}/{self.max_prog} [{c}%]"

        return state
        

frees_app("~\\Documents").start()
