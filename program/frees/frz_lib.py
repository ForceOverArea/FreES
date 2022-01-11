# Internal library for FrEES functions that do not have anything to do with the system-solving procedure or controlling GUI elements.

from colorama import Fore
from copy import deepcopy
from json import load
from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, log as ln, log10 as log

class soln_checker():
    """An object for monitoring solution status of a system."""
    def __init__(self, vars:dict):
        self.var_list = deepcopy(vars)
        self.attempted = []
        self.solved = []


    def mark_as_attempted(self, line_no:int):
        """Indicates that a line had a solution attempted, even if it was not necessarily solved.""" 
        # Lines attempted but not solved should be marked as such in the solution to warn the user of 
        # an unsolvable part of the system.
        if line_no not in self.attempted: self.attempted.append(line_no)


    def mark_as_solved(self, line_no:int):
        """Marks a line as solved. """ 
        # (Solved lines should be skipped by the solver functions)
        if line_no not in self.solved: self.solved.append(line_no)


    def completed(self, vars):
        """Returns a bool representing if the solver is making any headway. If not, the solving process should end."""
        done = len(vars) == len(self.var_list)
        if not done:
            self.var_list = deepcopy(vars)
        return done


    def unsolved_lines(self):
        """Returns a list of lines that had unsolved equations even though they were attempted."""
        return [str(line_no) for line_no in self.attempted if line_no not in self.solved]


def sp_eval(expr: str, fns="sin, cos, tan, ln, log10"):
    """Same as Python's eval() function, but imports 'fns' from the standard math library before executing the code in 'expr'."""
    return eval(expr, {
        "sin":sin, 
        "cos":cos,
        "tan":tan,
        "asin":asin,
        "acos":acos,
        "atan":atan,
        "sinh":sinh,
        "cosh":cosh,
        "tanh":tanh,
        "log":log,
        "ln":ln
        })


def alg_sol(line:str, vars:dict):
    """Find the value of a LHS variable in an equation (str). Updates the solution property with the variable and value when successfully called."""
    
    eqn = sub_vals(line, vars).split("=")
    var = eqn[0].strip()
    expr = eqn[1].strip()
    return { var: str(sp_eval(expr)) }


def iter_sol(line:str, vars:dict):
    """Find the value of a specified RHS variable by iteration. Updates the solution with the variable and value when successfully called."""

    increments = 1000 

    eqn = line.split("=")
    lhs = sp_eval(sub_vals(eqn[0].strip(), vars))
    rhs = eqn[1].strip().split("!guess")
    
    # get guess values and target variable
    expr = rhs[0]
    guess_args = rhs[1].split()
    var = guess_args[0]
    lo_guess = int(guess_args[1])*increments
    hi_guess = int(guess_args[2])*increments

    # domain, range, error
    dmn = [i/increments for i in range(int(lo_guess), int(hi_guess))]
    rng = [expr.replace(var, f"({i})") for i in dmn]
    err = [abs(lhs - sp_eval(y)) for y in rng]

    # index of the minimum error
    ime = err.index(min(err)) 
    per_err = 100*min(err)/lhs
    if per_err > 0.1: print(Fore.YELLOW, f"WARNING: Solution for {var} has high error. ({round(per_err, 5)}%)")
    
    return { var: str(dmn[ime]) } # dict of variable/value pair
    

def update_unit_info():
    """Refreshes the constants and unit conversion factors in RAM to the most recent values."""
    global unit_info # sub_consts() depends on this variable.
    with open(".\\config\\units.json", "r") as f:
        unit_info = load(f)


def sub_consts(exprs:str):
    """Substitutes values into given system (exprs: str) for all constants found in 'soln'. The result is returned as a string."""
    constants = unit_info["CONSTANTS"] # generated/updated by update_unit_info()
    for const in constants:
        exprs = exprs.replace(const, constants[const][1]) # constants[const] -> list. index 1 -> constant's value 
    return exprs


def sub_vals(exprs:str, vars:dict):
    """Substitutes values into given system (exprs: str) for all variables currently in the 'solver.soln' property. The result is returned as a string."""
    for var in vars:
        exprs = exprs.replace(var, f"({vars[var]})")
    return exprs