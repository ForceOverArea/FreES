# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 18:23:45 2022

@author: grant
"""
import tkinter as tk
from tkinter import filedialog, Grid, scrolledtext, ttk
from frees import load, system_solver
from os import system as sh
from platform import platform

current_file = "temp.frz"


def solve_from_gui():
    """Feed Editor window to system solver fn and update window with solution."""
    global exprs_box
    
    exprs = exprs_box.get("0.0",tk.END).split("\nSolution:")[0].rstrip()
    res = system_solver(exprs)
    
    header = "\n\n\n\nSolution:\n===========\n"
    body = "\n".join([f"{var} = {res[var]}" for var in res])
        
    with open(current_file, "w") as f:
        f.write(exprs + header + body)
    
    #Update scrolledtext
    exprs_box.delete("0.0",tk.END)
    exprs_box.insert(tk.END,
        load(current_file, include_soln=True)
        )


def open_plot_window():
    """Create a plot of an independent and dependent variable."""
    plotwin = tk.Tk()
    plotwin.title("FrEES Plot Window")
    plotwin.minsize(200,400)
    

def file_select():
    """Open a file to edit in FrEES editor."""
    global current_file, label, exprs_box
    
    # get current file and print to console
    current_file = filedialog.askopenfilename(initialdir="..")
    print(current_file)
    
    label.configure(text="Editing: " + current_file)
    
    exprs_box.delete("0.0",tk.END)
    exprs_box.insert(tk.END,
        load(current_file, include_soln=True)
        )
    

def edit_units():
    try:
        sh("notepad .\\config\\units.json")
    except:
        sh("nano ./config/units.json")
    
    
def save():
    """Write the current editor window's contents to the open .frz file"""
    global exprs_box
    contents = exprs_box.get("0.0",tk.END)
    
    with open(current_file, "w") as f:
        f.write(contents)
        

def clear():
    if "windows" in platform().lower():
        sh("cls")
    elif "linux" in platform().lower():
        sh("clear")
        
    
# Initialize window object
window = tk.Tk() 
window.title("FrEES - The Free, Open Source, Engineering Equation Solver")
window.minsize(600,400)
#window.resizable(False, False) 
window.iconbitmap(".\\assets\\frees.ico")
Grid.rowconfigure(window, 1, weight=1)
Grid.columnconfigure(window, 0, weight=1)

numcols = 6

# expressions variable
exprs = tk.StringVar()
# expressions textbox - put your equations here
exprs_box = scrolledtext.ScrolledText(window)
exprs_box.grid(
    columnspan=numcols, 
    column=0, 
    row=1, 
    padx=10,
    pady=10,
    sticky="nsew"
    )
exprs_box.configure(state='normal')


# Solve Button 
solve_button = ttk.Button(window, text = "Save/Solve", command = solve_from_gui)
solve_button.grid(column = 0, row = 0, sticky="ew")
# File Selection
fs_button = ttk.Button(window, text="Open", command = file_select)
fs_button.grid(column = 1, row = 0)
# Save Button
save_button = ttk.Button(window, text = "Save", command = save)
save_button.grid(column = 2, row = 0)
# Clear Terminal Button
cls_button = ttk.Button(window, text = "Clear Terminal", command = clear)
cls_button.grid(column = 3, row = 0)
# Plot Button
plot_button = ttk.Button(window, text = "New Plot", command = open_plot_window)
plot_button.grid(column = 4, row = 0)
# Edit Units Button
unit_button = ttk.Button(window, text = "Edit Unit Info", command = edit_units)
unit_button.grid(column = 5, row = 0)


# Label showing current file
label = ttk.Label(window, text = "No File Selected")
label.grid(columnspan = numcols, row = 2)


exprs_box.focus()
window.mainloop()