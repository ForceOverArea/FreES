# FreES internal function library. Version 2.
# Grant Christiansen Jan. 2022

# This version is specifically intended for 
# development purposes with (ideally) more
# declarative programming even at the cost of 
# performance drops.


from re import findall, IGNORECASE
from time import time
from json import load
from math import sin, cos, tan, sinh, cosh, tanh, asin, acos, atan, log10, log, exp


class soln:
    """Wrapper for solution info returned by solver function."""
    def __init__(self, soln, duration, percent_err=None):
        self.soln = soln
        self.percent_err = percent_err
        self.duration = duration  


def f_range(start, stop, steps=8):
    step_size = (stop - start) / (steps - 1)
    return [start + step_size * i for i in range(steps)]


def convert(from_unit:str, to_unit:str):
    """Return a conversion factor between two units."""

    with open("units.json","r") as f:
        factors = load(f)

    for cat in factors:
        print(factors[cat])
        if from_unit in factors[cat] and to_unit in factors[cat]:
            print(cat)
            unit_set = factors[cat]

    return unit_set[from_unit]/unit_set[to_unit]


def default_function_toolkit():
    """Returns the default functions to be recognized by FreES."""

    return {
        "sin":sin,
        "cos":cos,
        "tan":tan,
        "sinh":sinh,
        "cosh":cosh,
        "tanh":tanh,
        "asin":asin,
        "acos":acos,
        "atan":atan,
        "log":log10,
        "ln":log,
        "exp":exp,
        "convert":convert
    }


def iter_solve(func:str, condition:float, var="x", vals={}, left_search_bound=-1E20, right_search_bound=1E20, target_dx=1E-20, steps=8):
    """A more declarative approach to iterative solving. Approximately 4-5x slower than 'iter_solve', but much easier to understand."""

    start = time()

    def uar(myDict:dict, newDict:dict):
        """Stands for 'update and return'"""
        myDict.update(newDict)
        return myDict

    def f(x): return eval(func, uar(vals, {var: x}))
    def e(x): return abs(f(x) - condition)

    x = left_search_bound
    dx = (left_search_bound - right_search_bound) / steps
    
    while abs(dx) > target_dx:

        while e(x + dx) < e(x):
            x += dx

        x += dx # go to the next point
        dx *= -2 / steps

    x += dx * steps / -2
    return soln({var: x}, time()-start, percent_err=100*abs(f(x)-condition)/condition)


def solve_line(line:str, vals={}, target_dx=1E-20):
    """Parse an equation as a string and solve for a single unknown variable after subbing in known values."""
    start = time()

    def vf(expr:str):
        """'Variable finder'. Returns a list of variables in an expression"""
        found_vars = []
        for var in findall("[a-z]+", expr, IGNORECASE):
            
            if var not in vals and var not in found_vars:
                found_vars.append(var)
                
        return found_vars
    
    if line.lstrip().startswith("#"):
        print(f"Skipping commented line... {line}")
        return None # line is a comment, don't solve.
        

    exprs = line.split("=")
    
    if len(exprs) < 2:
        print(f"Skipping non-equation line... {line}")
        return None # line is not an equation, stop solving.
        
        
    lhs = vf(exprs[0])
    rhs = vf(exprs[1])
    
    if len(lhs) > 1 or len(rhs) > 1:
        print(f"Skipping unsolvable line... (Too many unknowns) {line}")
        return None # line is unsolvable due to too many unknowns.
    
    elif len(lhs) == 1 and len(rhs) == 0:
        return iter_solve(
            func = exprs[0],
            condition = eval(exprs[1], vals),
            var = lhs[0],
            vals = vals,
            target_dx = target_dx
        )

    elif len(rhs) == 1 and len(lhs) == 0:
        return iter_solve(
            func = exprs[1],
            condition = eval(exprs[0], vals),
            var = rhs[0],
            vals = vals,
            target_dx = target_dx
        )

    else:
        return None


class frees:
    "FreES engine for solving systems of equations."

    def __init__(self, exprs:str, precision=1E-20):
        self.exprs = exprs
        self.lines = exprs.strip().split("\n")
        self.unsolved = []
        self.precision = precision
        self.soln = soln(default_function_toolkit(), 0, percent_err=0.0)
        self.iter_solve = iter_solve


    def solve(self):
        solution_in_progress = True
        
        while solution_in_progress:
            number_of_known_values = len(self.soln.soln)
            
            for line in self.lines:
                line_number = self.lines.index(line) + 1
                line_soln = solve_line(line, self.soln.soln, target_dx=self.precision)

                if line_soln != None:
                    self.soln.soln.update(line_soln.soln)
                    self.soln.duration += line_soln.duration

                    if line_soln.percent_err > self.soln.percent_err: 
                        self.soln.percent_err = line_soln.percent_err 

                    if line_number in self.unsolved:
                        self.unsolved.remove(line_number)
                
                else:
                    self.unsolved.append(line_number)
                    continue
            
            if len(self.soln.soln) == number_of_known_values: # no new solutions have been found this loop, so break and report results.
                if '__builtins__' in self.soln.soln: 
                    del self.soln.soln['__builtins__']
                
                solution_in_progress = False
