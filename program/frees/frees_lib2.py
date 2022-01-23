# FreES internal function library.

from time import time
from re import findall, IGNORECASE
from sys import setrecursionlimit

default_precision = 1E-6
setrecursionlimit(1500)


def f_range(start, stop, num_steps=8):
    """Produces a list of floats with length 'num_steps' from 'start' to 'stop' (both inclusive)."""
    step = abs(stop - start)/(num_steps-1)
    rng = [start]
    while rng[-1] < stop:
        rng.append(rng[-1] + step)
    return rng


class soln:
    """Wrapper for solution info returned by solver functions."""
    def __init__(self, soln, duration, guess_l=None, guess_r=None, percent_err=None):
        self.soln = soln
        self.guess_l = guess_l
        self.guess_r = guess_r
        self.percent_err = percent_err
        self.duration = duration  


def iter_solve(expr:str, y_actual:float, var="x", vals={},  guess_l=-1E20, guess_r=1E20,  percent_err=default_precision, steps=8):
    """Iteratively solves a given function 'func' on the domain 'guess_l' < x < 'guess_r'.
    The function must have only one unknown variable to solve
    Iteration continues until value returned results in a lower percent error than the 
    value specified. Defaults to 0.1%"""
    
    def uc(myDict:dict, newDict:dict):
        """Stands for 'update closure'. Updates a dict and returns the result."""
        myDict.update(newDict)
        return myDict

    start = time()
    dmn = f_range(guess_l, guess_r, steps)
    rng = [eval(expr, uc(vals, {var: x})) for x in dmn]
    err = [abs(j - y_actual) for j in rng]
    ime = err.index(min(err)) # indices of minimum error

    if y_actual == 0:
        cpe = 100*min(err)/1E-20 # approximation to prevent division by zero.
    else: 
        cpe = 100*min(err)/abs(y_actual) # current percent error

    if cpe > percent_err:
        # Get a smaller domain to inspect. NOTE Only one exception should occur at maximum.
        try: lbnd = dmn[ime-1]
        except: lbnd = dmn[ime]
        try: rbnd = dmn[ime+1]
        except: rbnd = dmn[ime]

        # recurse on a smaller domain
        return iter_solve(expr, y_actual, var, vals, lbnd, rbnd, percent_err, steps)

    else:
        return soln({var:dmn[ime]}, time()-start, dmn[0], dmn[-1], cpe)


def solve_line(line:str, vals={}, percent_err=default_precision):
    """Parse an equation as a string and solve for a single unknown variable after subbing in known values."""
    start = time()

    def vfc(expr:str):
        """Variable finding closure function. Returns a list of variables in an expression"""
        found_vars = []
        for var in findall("[a-z]+", expr, IGNORECASE):
            if var not in vals and var not in found_vars:
                found_vars.append(var)
        return found_vars

    # get unknown variables in expression

    exprs = line.split("=")
    exprs[1] = exprs[1].split("#")[0] # remove comments from rhs.

    # Conditions to immediately stop attempting a solution.
    if len(exprs) < 2: return None 
    if line.lstrip().startswith("#"): return None
    
    lhs = vfc(exprs[0])
    rhs = vfc(exprs[1])
    
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

    def __init__(self, exprs:str, precision=default_precision):
        self.exprs = exprs
        self.lines = exprs.strip().split("\n")
        self.unsolved = []
        self.precision = precision
        self.soln = soln({}, 0, percent_err=0.0)


    def solve(self):
        
        solution_in_progress = True
        
        while solution_in_progress:
            
            known_values = len(self.soln.soln)
            
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
            
            if len(self.soln.soln) == known_values:
                del self.soln.soln['__builtins__']
                solution_in_progress = False # no new solutions have been found this loop, so break and report results.
            
        

system = frees("""
y = 90 
x + y = 87
x = c
c = r**3 + r + 5
""")

system.solve()

print(f"\nSystem solved in {system.soln.duration} seconds with a maximum solution error of {system.soln.percent_err}%. \n\nValues Found:\n{system.soln.soln}\n")