# Contains the code for the solving process (i.e. 'steps'). All other code should go in a separate module file.

import colorama
from frz_lib import *
from time import time
from colorama import Fore
colorama.init()

def solver(exprs:str, verbose=True):
    """Takes a system of equations in a string as its only argument. 
    Solves the given system and returns all variables and their 
    solved values in a dict.
    """

    if verbose: print("Initializing solver...")
    soln = {} # Dict to hold vaiable name-value pairs
    exprs = exprs.split("\nSolution:")[0].replace("^","**") # Ignore the solution block of the .frz file
    checker = soln_checker(soln)
    update_unit_info() # If units.json was edited, before the solve button was hit, reflect the changes
    start_time = time()

    # Sub in constant values first
    exprs = sub_consts(exprs)
    if verbose: print("Substituted constant values successfully.")
    
    iteration = 0
    if verbose: print("Starting solving process...")
    while not checker.completed(soln) or iteration == 0:
        
        iteration += 1
        if verbose: print(Fore.WHITE, f"\nStarting iteration {iteration}...")

        lines = exprs.split("\n")
        for line in lines:         
            line_number = lines.index(line)+1

            if \
                "!guess" in line and \
                not line.strip().startswith("#") and \
                not line_number in checker.solved: 
                
                try:
                   if verbose: print(Fore.WHITE, f"\nAttempting iterative solution at line {line_number}...")
                   checker.mark_as_attempted(line_number)
                   soln.update(iter_sol(line, soln))
                   checker.mark_as_solved(line_number)
                   if verbose: print(Fore.GREEN, "[  OK  ]")
            
                except:
                    if verbose: print(Fore.RED, "[ ABORT ]")
                    continue

            elif \
                len(line.strip()) != 0 and \
                not line[0].isdigit() and \
                not line.strip().startswith("#") and \
                not line_number in checker.solved: 
                
                try:
                    if verbose: print(Fore.WHITE, f"\nAttempting algebraic solution at line {line_number}...")
                    checker.mark_as_attempted(line_number)
                    soln.update(alg_sol(line, soln))
                    checker.mark_as_solved(line_number)
                    if verbose: print(Fore.GREEN, "[  OK  ]")
                except:
                    if verbose: print(Fore.RED, "[ ABORT ]")
    
    end_time = time()
    if verbose: print(Fore.WHITE, f"\nSystem solved. ({round(end_time-start_time,5)} sec)")

    return soln, checker.unsolved_lines()