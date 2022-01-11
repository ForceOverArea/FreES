from colorama import Fore
from datetime import datetime
from os import system as sh
from colorama.ansi import Fore
from matplotlib import pyplot as plt
from platform import platform
from frz_solver import solver
from sys import stdout
from time import time
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Button, Label, Entry


class frees_app():
    """FrEES app and all its windows and internal data. Call frees_app().start() to run the program."""

    def __init__(self, fp):
        self.window = Tk() 
        self.window.title("FrEES - The Free, Open Source, Engineering Equation Solver")
        self.window.minsize(600,400)
        self.window.iconbitmap(".\\assets\\frees.ico")
        self.current_file = fp
        Grid.rowconfigure(self.window, 1, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)

        numcols = 6 # Hard-coded here to parametrize later code.

        self.exprs_box = ScrolledText(self.window)
        self.exprs_box.grid(
            columnspan=numcols, 
            column=0, 
            row=1, 
            padx=10,
            pady=10,
            sticky="nsew"
            )
        self.exprs_box.configure(state='normal')
        
        self.solve_button = Button(self.window, text = "Save/Solve",     command = self.solve_from_gui)     # Solve Button 
        self.fs_button = Button(   self.window, text="Open",             command = self.file_select)        # File Selection
        self.save_button = Button( self.window, text = "Save",           command = self.save)               # Save Button
        self.cls_button = Button(  self.window, text = "Clear Terminal", command = self.clear)              # Clear Terminal Button
        self.plot_button = Button( self.window, text = "New Plot",       command = self.open_plot_window)   # Plot Button
        self.unit_button = Button( self.window, text = "Edit Unit Info", command = self.edit_units)         # Edit Units Button
        self.label = Label(self.window, text = "No File Selected")                                          # Label showing current file

        self.solve_button.grid(column = 0, row = 0, sticky="ew")
        self.fs_button.grid(   column = 1, row = 0)
        self.save_button.grid( column = 2, row = 0)
        self.cls_button.grid(  column = 3, row = 0)
        self.plot_button.grid( column = 4, row = 0)
        self.unit_button.grid( column = 5, row = 0)
        self.label.grid(columnspan = numcols, row = 2)


    def solve_from_gui(self):
        """Feed Editor window to system solver fn and update window with solution."""
        global exprs_box
        
        exprs = self.exprs_box.get("0.0",END).split("\nSolution:")[0].rstrip()
        findings = solver(exprs)
        res = findings[0]
        unsolved_lines = [f"Line {item}" for item in findings[1]]
        
        header = "\n\n\n\nSolution:\n===========\n"
        body = "\n".join([f"{var} = {res[var]}" for var in res])
        
        if len(unsolved_lines) > 0:
            body += f"\n\nUnsolvable: {', '.join(unsolved_lines)}"
        
        with open(self.current_file, "w") as f:
            f.write(exprs + header + body)
        
        #Update scrolledtext
        self.exprs_box.delete("0.0", END)
        self.exprs_box.insert(END,
            self.load(include_soln=True)
            )


    def open_plot_window(self):
        """Create a plot of an independent and dependent variable."""
        pw = plot_window(self)
        pw.window.mainloop()

    def load(self, include_soln=False):
        """Returns the contents of a text file (or .frz file) as a string."""
        with open(self.current_file, "r") as f:
            if include_soln:
                return f.read()
            else:
                return f.read().split("\n\nFrEES SOLN:")[0]     


    def file_select(self):
        """Open a file to edit in FrEES editor."""
        
        self.current_file = askopenfilename(initialdir="..")
        print("Opened: ",self.current_file)
        
        self.label.configure(text="Editing: " + self.current_file)
        
        self.exprs_box.delete("0.0",END)
        self.exprs_box.insert(END, self.load(include_soln=True))
        

    def edit_units(self):
        try:
            sh("notepad .\\config\\units.json")
        except:
            sh("nano ./config/units.json")
        
        
    def save(self):
        """Write the current editor window's contents to the open .frz file"""
        contents = self.exprs_box.get("0.0",END)
        
        with open(self.current_file, "w") as f:
            f.write(contents)
            print(f"Saved: {self.current_file} on {datetime.now()}")
            

    def clear(self):
        if "windows" in platform().lower():
            sh("cls")
        elif "linux" in platform().lower():
            sh("clear")


    def start(self):
        self.exprs_box.focus()
        self.window.mainloop()


class plot_window():
    """Separate Tkinter window for plot generation."""

    def __init__(self, parent:Tk):
        self.window = Tk()
        self.parent = parent
        self.window.title("FrEES - Create New Plot")
        self.window.iconbitmap(".\\assets\\frees.ico")
        self.window.resizable(0, 0)

        plot_menu = Frame(self.window)
        plot_menu.grid(padx=10, pady=10)

        dmn_start = StringVar()
        dmn_end = StringVar()
        dmn_step = StringVar()
        ind_var = StringVar()
        dep_var = StringVar()
        ptitle = StringVar()

        self.dstart_label = Label(  plot_menu, text = "Start of Domain")
        self.dend_label = Label(    plot_menu, text = "End of Domain")
        self.dstep_label = Label(   plot_menu, text = "Domain Step Size")
        self.iv_label = Label(      plot_menu, text = "Independent Var.")
        self.dv_label = Label(      plot_menu, text = "Dependent Var.")
        self.t_label = Label(       plot_menu, text = "Plot Title")

        self.dmn_start = Entry(     plot_menu, width = 30, textvariable = dmn_start)
        self.dmn_end = Entry(       plot_menu, width = 30, textvariable = dmn_end)
        self.dmn_step = Entry(      plot_menu, width = 30, textvariable = dmn_step)
        self.ind_var = Entry(       plot_menu, width = 30, textvariable = ind_var)
        self.dep_var = Entry(       plot_menu, width = 30, textvariable = dep_var)
        self.title = Entry(         plot_menu, width = 30, textvariable = ptitle)

        self.plot_button = Button(  plot_menu, text = "Create Plot", command = self.plot)

        self.dstart_label.grid( column = 0, row = 0, sticky="nsew")
        self.dend_label.grid(   column = 0, row = 1, sticky="nsew")
        self.dstep_label.grid(  column = 0, row = 2, sticky="nsew")
        self.iv_label.grid(     column = 2, row = 0, sticky="nsew")
        self.dv_label.grid(     column = 2, row = 1, sticky="nsew")
        self.t_label.grid(      column = 2, row = 2, sticky="nsew")

        self.dmn_start.grid(    column = 1, row = 0, sticky="nsew")
        self.dmn_end.grid(      column = 1, row = 1, sticky="nsew")
        self.dmn_step.grid(     column = 1, row = 2, sticky="nsew")
        self.ind_var.grid(      column = 3, row = 0, sticky="nsew")
        self.dep_var.grid(      column = 3, row = 1, sticky="nsew")
        self.title.grid(        column = 3, row = 2, sticky="nsew")

        self.plot_button.grid(columnspan = 4, row = 3, sticky="nsew")


    def plot(self):
        """Plots a given dependent variable as a function of a given dependent variable"""
        print(Fore.WHITE, "\nGenerating plot. This may take some time...")
        start = time()

        dstep = 1/float(self.dmn_step.get())
        dstart = int(self.dmn_start.get())
        dend = int(self.dmn_end.get())
        print(f"Domain: {dstart} < x < {dend}, Interval: {1/dstep}")
        
        dmn = [i/dstep for i in range(int(dstart*dstep), int(dend*dstep))]
        exprs = self.parent.exprs_box.get("0.0",END).split("\nSolution:")[0].rstrip()

        # setup toolbar
        stdout.write(f"\nCalculating points: (0/{len(dmn)})")
        stdout.flush()
        stdout.write("\b" * (len(str(len(dmn)))+4)) # return to '('

        # Long story short, runs the solver for every point in the domain and generates the range as a list. Plot lightly! :')
        rng = []
        for x in dmn:
            y = solver( exprs.replace( self.ind_var.get(), f"({x})" ), verbose=False )[0][self.dep_var.get()]
            rng.append(float(y))

            # update progress meter in terminal
            prog = f"({dmn.index(x)+1}/{len(dmn)})"
            stdout.write(prog)
            stdout.flush()
            stdout.write("\b" * len(prog)) # return to '('

        print("\nPlotting...")
        plt.plot(dmn, rng)
        plt.title(self.title.get())
        end = time()
        print(f"\nPlot creation successful. ({round(end-start, 5)} sec)")
        plt.show()
        