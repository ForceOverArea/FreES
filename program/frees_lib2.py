# FreES internal function library. Version 2.
# Grant Christiansen Jan. 2022

# This version is specifically intended for 
# development purposes with (ideally) more
# declarative programming even at the cost of 
# a slight performance drop.


from re import findall, IGNORECASE
from time import time


class soln:
    """Wrapper for solution info returned by solver function."""
    def __init__(self, soln, duration, percent_err=None):
        self.soln = soln
        self.percent_err = percent_err
        self.duration = duration  


def iter_solve(expr:str, y_actual:float, var="x", vals={},  guess_l=-1E20, guess_r=1E20,  percent_err=1E-6, steps=8):
    """A more declarative approach to iterative solving. Approximately 4-5x slower than 'iter_solve', but much easier to understand."""

    start = time()

    def uar(myDict:dict, newDict:dict):
        myDict.update(newDict)
        return myDict

    def f(x): return eval(expr, uar(vals, {var: x}))
    def err(x): return abs(f(x) - y_actual)

    x = guess_l # start at left end of domain
    dx = (guess_l - guess_r) / steps

    cpe = 1
    while cpe > percent_err:

        while err(x) > err(x + dx):
            x += dx
            cpe = 100 * err(x) / abs(y_actual) # current percent error

        x += dx # go to the next point

        dx *= -2 / steps

    return soln({var: x}, time()-start, percent_err=cpe)


def solve_line(line:str, vals={}, percent_err=1E-6):
    """Parse an equation as a string and solve for a single unknown variable after subbing in known values."""
    start = time()

    def vf(expr:str):
        """'Variable finder'. Returns a list of variables in an expression"""
        found_vars = []
        for var in findall("[a-z]+", expr, IGNORECASE):
            if var not in vals and var not in found_vars:
                found_vars.append(var)
        return found_vars
    
    if line.lstrip().startswith("#"): return None # line is a comment, don't solve.

    exprs = line.split("=")
    
    if len(exprs) < 2: return None # line is not an equation, stop solving.
    
    lhs = vf(exprs[0])
    rhs = vf(exprs[1])
    
    if len(lhs) > 1 or len(rhs) > 1:
        return None # line is unsolvable due to too many unknowns.
    
    elif len(lhs) == 1 and len(rhs) == 0:
        return iter_solve(
            expr = exprs[0],
            y_actual = eval(exprs[1], vals),
            var = lhs[0],
            vals = vals,
            percent_err = percent_err
        )

    elif len(rhs) == 1 and len(lhs) == 0:
        return iter_solve(
            expr = exprs[1],
            y_actual = eval(exprs[0], vals),
            var = rhs[0],
            vals = vals,
            percent_err = percent_err
        )

    else:
        return None


class frees:
    "FreES engine for solving systems of equations."

    def __init__(self, exprs:str, precision=1E-6):
        self.exprs = exprs
        self.lines = exprs.strip().split("\n")
        self.unsolved = []
        self.precision = precision
        self.soln = soln({}, 0, percent_err=0.0)
        self.iter_solve = iter_solve


    def solve(self):
        solution_in_progress = True
        
        while solution_in_progress:
            number_of_known_values = len(self.soln.soln)
            
            for line in self.lines:
                line_number = self.lines.index(line) + 1
                line_soln = solve_line(line, self.soln.soln, percent_err=self.precision)

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