# FreES GUI toolkit library. Version 2

from time import sleep
from frees_lib2 import frees, f_range
from json import load, dump
from matplotlib import pyplot as plt
from os import system as sh
from tkinter import * 
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
# from tkinter.ttk import Button, Label, Entry


class frees_app:
    """FreES window and all of its controls and internal data."""

    def __init__(self, fp):
        self.window = Tk() 
        self.window.title("FreES - The Free, Open Source, Engineering Equation Solver")
        self.window.minsize(600, 400)
        self.current_file = fp
        Grid.rowconfigure(self.window, 1, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)

        numcols = 7 # Hard-coded here to parametrize later code.

        self.exprs_box = ScrolledText(self.window)
        self.exprs_box.grid(columnspan=numcols, column=0, row=1, padx=10, pady=10, sticky="nsew")
        self.exprs_box.configure(state='normal')
        
        self.solve_button =     Button(self.window, text = "Save/Solve",     command = self.open_solution_window)   # Solve Button 
        self.fs_button =        Button(self.window, text = "Open",           command = self.open_file_select)       # File Selection
        self.save_button =      Button(self.window, text = "Save",           command = self.save_file)              # Save Button
        self.saveas_button =    Button(self.window, text = "Save As...",     command = self.open_saveas_window)     # Save file as
        self.plot_button =      Button(self.window, text = "New Plot",       command = self.open_plot_window)       # Plot Button
        self.settings_button =  Button(self.window, text = "Settings",       command = self.open_settings_window)   # Change settings
        self.label =            Label( self.window, text = "No File Selected")                                      # Label showing current file

        self.solve_button   .grid(column = 0, row = 0, sticky="ew", padx = 2, pady = 2)
        self.fs_button      .grid(column = 1, row = 0, padx = 2, pady = 2)
        self.save_button    .grid(column = 2, row = 0, padx = 2, pady = 2)
        self.saveas_button  .grid(column = 3, row = 0, padx = 2, pady = 2)
        self.plot_button    .grid(column = 4, row = 0, padx = 2, pady = 2)
        self.settings_button.grid(column = 6, row = 0, padx = 2, pady = 2)
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
        self.save_file()
        sw = solution_window(self)
        sw.window.mainloop()


    def open_plot_window(self):
        """Create a plot of an independent and dependent variable."""
        pw = plot_window(self)
        pw.window.mainloop()


    def open_file_select(self):
        """Open a file to edit in the FreES editor."""
        fp_to_open = askopenfilename(initialdir = "..", filetypes=(("FreES files", "*.fr*"), ("All files", "*.*"))) # "~/Documents")
        
        if fp_to_open != "":
            self.current_file = fp_to_open

        self.label.configure(text = "Editing: " + self.current_file)
        self.exprs_box.delete("0.0",END)
        self.exprs_box.insert(END, self.open_file())


    def edit_unit_config(self):
        """Edit the units.json file."""
        with open("settings.json", "r") as f:
            text_editor = load(f)["TEXT_EDITOR"]
        sh(f"{text_editor} ./units.json")



    def save_file(self):
        """Write the current editor window's contents to file."""
        with open(self.current_file, "w") as f:
            f.write(self.fetch_eqns())


    def open_saveas_window(self):
        """Write the current editor window's contents to a given filepath."""
        saw = save_as_window(self)
        saw.window.mainloop()


    def open_settings_window(self):
        """Open the settings window to cleanly edit settings.json"""
        sew = settings_window(self)
        sew.window.mainloop()


    def start(self):
        self.exprs_box.focus()
        self.window.mainloop()


class save_as_window:
    """Window for creating files from withing FreES."""

    def __init__(self, parent):
        self.window = Toplevel()
        self.parent = parent
        self.window.title("FreES - Save File As...")
        self.window.minsize(200,50)

        self.new_filename = StringVar()

        self.filename_label =   Label(self.window, text = "File Name: ")
        self.name_box =         Entry(self.window, textvariable = self.new_filename)
        self.saveas_button =    Button(self.window, text = "Save", command = self.save_as)

        self.filename_label .grid(row = 0, column = 0)
        self.name_box       .grid(row = 0, column = 1, pady = 10, sticky = "ew")
        self.saveas_button  .grid(row = 1, columnspan = 2, padx = 10, pady = 10, sticky = "ew")


    def save_as(self):
        """Save a file to a given destination."""
        new_filename = "../" + self.name_box.get() + ".fr"
        with open(new_filename, "w") as f:
            f.write(self.parent.fetch_eqns())

        self.parent.current_file = new_filename
        self.parent.label.configure(text = "Editing: " + self.parent.current_file)
        
        self.window.destroy()


class settings_window:
    """Window for editing settings.json with a cleaner UI."""

    def __init__(self, parent):

        self.scale = 10 # parametrizes the scaling of the accuracy setting

        with open("./settings.json", "r") as f:            
            self.settings = load(f)
        
        self.window = Toplevel()
        self.parent = parent
        self.window.title("FreES - Settings")
        self.window.minsize(250,200)


        self.truncate_label =       Label(self.window, text = "Decimal Places:")
        self.truncate_slider =      Scale(self.window, from_ = 0, to = 10, tickinterval = 2, orient = "horizontal")
        self.slncols_label =        Label(self.window, text = "Sln. Window Columns:")
        self.slncols_slider =       Scale(self.window, from_ = 1, to = 5, tickinterval = 1, orient = "horizontal")
        self.accuracy_label =       Label(self.window, text = f"Solver Accuracy (Res. = 1E-{self.scale}X):")
        self.accuracy_slider =      Scale(self.window, from_ = 1, to = 32, tickinterval = 31, orient = "horizontal")
        self.text_editor_label =    Label(self.window, text = "Change text editor:")
        self.text_editor_box =      Button(self.window, text = "Browse", command = self.change_text_editor)
        self.unit_label =           Label(self.window, text = "Edit Units file:")
        self.unit_button =          Button(self.window, text = "Edit", command = self.edit_unit_config)
        self.apply_button =         Button(self.window, text = "Apply Changes", command = self.apply_changes)


        self.truncate_label         .grid(column = 0, row = 0, pady = 10, padx = 20)
        self.truncate_slider        .grid(column = 1, row = 0, pady = 10, padx = 20, sticky = "w")
        self.slncols_label          .grid(column = 0, row = 1, pady = 10, padx = 20)
        self.slncols_slider         .grid(column = 1, row = 1, pady = 10, padx = 20, sticky = "w")
        self.accuracy_label         .grid(column = 0, row = 2, pady = 10, padx = 20)
        self.accuracy_slider        .grid(column = 1, row = 2, pady = 10, padx = 20, sticky = "w")
        self.text_editor_label      .grid(column = 0, row = 3, pady = 10, padx = 20)
        self.text_editor_box        .grid(column = 1, row = 3, pady = 10, padx = 20, sticky = "w")
        self.unit_label             .grid(column = 0, row = 4, pady = 10, padx = 20)
        self.unit_button            .grid(column = 1, row = 4, pady = 10, padx = 20, sticky = "w")
        self.apply_button           .grid(columnspan = 2, row = 5, pady = 10, padx = 10, sticky = "ew")


        self.truncate_slider        .set(self.settings["DEC_PLACES"])
        self.slncols_slider         .set(self.settings["SOLN_COLS"])
        self.accuracy_slider        .set(int(self.settings["ACCURACY"][3:])/self.scale)


    def change_text_editor(self):
        """Choose a default text editor for editing units.txt"""
        fp = askopenfilename(initialdir = "/", filetypes=(("Executables", "*.exe*"), ("All files", "*.*")))
        print(fp)
        if fp != "":
            self.settings["TEXT_EDITOR"] = fp


    def edit_unit_config(self):
        """Edit the units.json file."""
        with open("settings.json", "r") as f:
            text_editor = load(f)["TEXT_EDITOR"]
        sh(f"{text_editor} ./units.json")

        
    def apply_changes(self):
        self.settings["DEC_PLACES"] = int(self.truncate_slider.get())
        self.settings["SOLN_COLS"] = int(self.slncols_slider.get())
        self.settings["ACCURACY"] = f"1E-{self.accuracy_slider.get()*self.scale}"

        print(self.settings)

        with open("./settings.json","w") as f:
            dump(self.settings, f, indent = 4)

        self.apply_button.configure(text = "Changes Applied!")
        self.apply_button.update_idletasks()
        sleep(0.5)
        self.apply_button.configure(text = "Apply Changes")


class solution_window:
    """Window for displaying solution."""

    def __init__(self, parent:frees_app):
        self.window = Toplevel()
        self.parent = parent
        self.window.title("FreES - Solution Window")
        self.window.minsize(200,200)
        self.window.resizable(0, 0)

        with open("settings.json","r") as f:
            settings = load(f)
            dec_places = settings["DEC_PLACES"]
            soln_cols = settings["SOLN_COLS"]
            accuracy = float(settings["ACCURACY"])

        soln = frees(self.parent.fetch_eqns(), accuracy)
        try:
            soln.solve()

            duration = f"Solved in {round(soln.soln.duration, 5)} seconds."
            values = [f"{item} = {round(soln.soln.soln[item], dec_places)}" for item in soln.soln.soln]
            if len(soln.warnings) > 0:
                warnings = "=========\n" + '\n'.join(soln.warnings)
            else:
                warnings = ""

                
            def sublists(items:list, n:int):
                # looping till length l
                for i in range(0, len(items), n): 
                    yield items[i:i + n]

            gridified = "\n\n".join(["\t\t".join(i) for i in list(sublists(values, soln_cols))])
            
            soln_text = f"{duration}\n=========\n\n{gridified}\n\n{warnings}"
        
        except Exception as e:
            soln_text = f"Could not solve due to the following Python error: \n\n{str(e)}" 

        self.titlebar = Label(self.window, text = "Solution:\n=========")
        self.swtext = Label(self.window, text = soln_text)
        self.close_button = Button(self.window, text = "Close", command = self.close)

        self.titlebar       .grid(column = 0, row = 0)
        self.swtext         .grid(column = 0, row = 1, padx = 10, pady = 10)
        self.close_button   .grid(column = 0, row = 2, pady = 10)


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
        
        dmn_size = self.dmn_size.get()

        if dmn_size == "":
            dmn_size = 25
        else: 
            dmn_size = int(dmn_size)

        domain = f_range(
            float(self.dmn_start.get()), 
            float(self.dmn_end.get()), 
            dmn_size
            )
        y = []
        pb = prog_bar(dmn_size, style="basic")

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

        present = f'( {wheel} )'
        past = '|' * p
        future = '.' * f

        state = f"[{past}{present}{future}] {int(self.progress)}/{self.max_prog} [{c}%]"

        return state
        

frees_app("../tmp").start()
