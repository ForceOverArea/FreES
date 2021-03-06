# FreES internal function library. Version 2.
# Grant Christiansen Jan. 2022

# This version is specifically intended for 
# development purposes with (ideally) more
# declarative programming even at the cost of 
# performance drops.


from re import findall, IGNORECASE
from time import time
from json import load
from math import sin, cos, tan, sinh, cosh, tanh, asin, acos, atan, log10, log, exp, pi


class soln:
    """Wrapper for solution info returned by solver function."""
    def __init__(self, soln, duration, percent_err=None, key_var=False):
        self.soln = soln
        self.percent_err = percent_err
        self.duration = duration  
        self.key_var = key_var


def f_range(start, stop, steps=8):
    step_size = (stop - start) / (steps - 1)
    return [start + step_size * i for i in range(steps)]


def convert(from_unit:str, to_unit:str):
    """Return a conversion factor between two units."""

    with open("units.json","r") as f:
        factors = load(f)

    for cat in factors:
        if from_unit in factors[cat] and to_unit in factors[cat]:
            unit_set = factors[cat]

    return unit_set[from_unit]/unit_set[to_unit]


def I_tube(OD, ID):
    """Area moment of inertia for a round tube."""
    return pi*(OD**4 - ID**4)/64
    

def I_rect(b, h):
    """Area moment of inertia for rectangular stock"""
    return (b*h**3)/3


def I_u_channel(b, h, thk):
    """Area moment of inertia for u-channel."""
    return ((b-2*thk)*thk**3)/3 + 2*(thk*h**3)/3


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
        "convert":convert,
        "iTube":I_tube,
        "iRect":I_rect,
        "iUChan":I_u_channel
    }


def default_constant_toolkit():
    """Returns a dict of the constants recognized by FreES."""
    with open("units.json", "r") as f:
        return load(f)["CONSTANTS"]


def uar(myDict:dict, newDict:dict):
        """Stands for 'update and return'"""
        myDict.update(newDict)
        return myDict


def iter_solve(func:str, condition:float, var="x", vals={}, left_search_bound=1E20, right_search_bound=-1E20, target_dx=1E-50, steps=8):
    """A more declarative approach to iterative solving. Approximately 4-5x slower than 'iter_solve', but much easier to understand."""

    start = time()

    def f(x): return eval(func, uar(vals, {var: x}))
    def e(x): return abs(f(x) - condition)

    x = left_search_bound
    dx = abs((left_search_bound - right_search_bound) / steps)
    
    while abs(dx) > target_dx:

        while e(x + dx) < e(x) and left_search_bound < x + dx < right_search_bound: # Do not ignore search bounds
            x += dx

        x += dx # go to the next point
        dx *= -2 / steps

    x += dx * steps / -2
    return soln({var: x}, time()-start, percent_err=100*abs(f(x)-condition)/condition)


def iter_solve2(func:str, condition:float, var="x", vals={}, left_search_bound=1E20, right_search_bound=-1E20, target_dx=1E-20, steps=8):
    """A more declarative approach to iterative solving. Approximately 4-5x slower than 'iter_solve', but much easier to understand."""

    start = time()

    def f(x): return eval(func, uar(vals, {var: x}))
    def e(x): return abs(f(x) - condition)
    def ime(some_list): return some_list.index(min(some_list))

    dmn = f_range(left_search_bound, right_search_bound, steps)
    crit_index = ime([e(x) for x in dmn[1:-2]])
    dx = abs(dmn[0]-dmn[1])
    
    if dx > target_dx:
        return iter_solve2(
            func = func, 
            condition = condition,
            var = var,
            vals = vals,
            left_search_bound = dmn[crit_index-1],
            right_search_bound = dmn[crit_index+1],
            target_dx = target_dx,
            steps = steps
            )
    else:
        x = dmn[crit_index]
        return soln({var: x}, time()-start, percent_err=100*abs(f(x)-condition)/condition)


class eqn_parser:

    def __init__(self, equation:str, knowns:dict):
        self.knowns = knowns
        self.equation = equation
        self.vars = self.vf(self.equation)
        self.exprs = self.equation.split("!")[0].split("=")
        self.not_an_equation = len(self.exprs) != 2
        self.is_comment = self.equation.startswith("#")

        if len(self.exprs) == 2:

            self.lhs_vars = self.vf(self.exprs[0])
            self.rhs_vars = self.vf(self.exprs[1].split("!")[0].split("#")[0])
                
            self.too_many_unknowns = len(self.lhs_vars) > 1 or len(self.rhs_vars) > 1 or (len(self.lhs_vars) == 1 and len(self.rhs_vars) == 1)

            self.flags = self.equation.split("!")[1:]
            if len(self.flags) > 0:
                for flag in self.flags:
                    
                    if "bound" in flag:
                        args = flag.split()[1:] # all arguments before next flag

                        self.bound_var = args[0]
                        self.l_bound = min(args[1:])
                        self.r_bound = max(args[1:])

                    else:
                        self.bound_var = None
                        self.l_bound = None
                        self.r_bound = None


                    if "key" in flag:
                        self.key_var = True

                    else:
                        self.key_var = False

                    if "if" in flag:
                        self.conditional = True
                        args = flag.split()[1:]

                        # replace variables with values if possible
                        for i in 0, 2:
                            if args[i] in knowns:
                                args[i] = knowns[args[i]]
                            else:
                                args[i] = args[i]

                        conditions = {
                            "<":  float(args[0]) <  float(args[2]),
                            ">":  float(args[0]) >  float(args[2]),
                            "=":  float(args[0]) == float(args[2]),
                            "==": float(args[0]) == float(args[2]),
                            "<=": float(args[0]) <= float(args[2]),
                            ">=": float(args[0]) >= float(args[2]),
                            "/=": float(args[0]) != float(args[2])
                        }
                    
                        self.satisfied = conditions[args[1]]

                    else:
                        self.conditional = False
                        self.satisfied = False

            else:
                self.bound_var = None
                self.l_bound = None
                self.r_bound = None
                self.key_var = False
                self.conditional = False
                self.satisfied = False
                
        else: 
        
            self.flags = []
    
            self.lhs_vars = []
            self.rhs_vars = []

            self.too_many_unknowns = None

        self.unsolvable = self.is_comment or self.too_many_unknowns or self.not_an_equation


    def vf(self, expr:str):
        """'Variable finder'. Returns a list of variables in an expression"""
        found_vars = []

        strings = findall(r"'([^']*)'", expr)
        candidates = findall("[a-z]+", expr, IGNORECASE)

        for i in strings:
            if i in candidates: # This excludes all string occurences from the list of variables
                candidates.remove(i)

        for i in candidates:
            if i not in self.knowns and i not in found_vars:
                found_vars.append(i)

        return found_vars
        

def solve_line(line:str, vals={}, target_dx=1E-20):
    """Parse an equation as a string and solve for a single unknown variable after subbing in known values."""

    line_info = eqn_parser(line, vals)

    if line_info.too_many_unknowns:
        return f"Skipped unsolvable line due to too many unknowns: \n   {line}" # line is unsolvable due to too many unknowns.

    if line_info.unsolvable:
        return None

    elif len(line_info.lhs_vars) == 1 and len(line_info.rhs_vars) == 0:
    
        if line_info.bound_var == line_info.lhs_vars[0]:
            bounds = line_info.l_bound, line_info.r_bound
            print(f"\n\n------------------------------------\n\nBOUND FLAG: {bounds}")
        else:
            bounds = [-1E20, 1E20]

        if line_info.conditional:
            print(f"\n\n------------------------------------\n\nIF FLAG: condition is {line_info.satisfied}")
            if not line_info.satisfied:
                return f"Skipped line due to unsatisfied condition: {line}"
            else:
                pass

        return iter_solve(
            func = line_info.exprs[0],
            condition = eval(line_info.exprs[1].split("!")[0], vals),
            var = line_info.lhs_vars[0],
            vals = vals,
            left_search_bound = float(bounds[0]),
            right_search_bound = float(bounds[1]),
            target_dx = target_dx
        )

    elif len(line_info.rhs_vars) == 1 and len(line_info.lhs_vars) == 0:

        if line_info.bound_var == line_info.rhs_vars[0]:
            bounds = line_info.l_bound, line_info.r_bound
            print(f"\n\n------------------------------------\n\nBOUND FLAG: {bounds}")
        else:
            bounds = [-1E20, 1E20]

        return iter_solve(
            func = line_info.exprs[1].split("!")[0],
            condition = eval(line_info.exprs[0], vals),
            var = line_info.rhs_vars[0],
            vals = vals,
            left_search_bound = float(bounds[0]),
            right_search_bound = float(bounds[1]),
            target_dx = target_dx
        )

    else:
        return None


class frees:
    """FreES engine for solving systems of equations."""

    def __init__(self, exprs:str, accuracy=1E-1000, toolkit={}):
        self.exprs = exprs

        for const in default_constant_toolkit():
            self.exprs = self.exprs.replace(const, default_constant_toolkit()[const][1])

        print(f"\n\n------------------------------------\n\nSYSTEM:\n{self.exprs}")
        self.lines = self.exprs.strip().split("\n")
        self.accuracy = accuracy
        self.iter_solve = iter_solve
        self.toolkit = uar(default_function_toolkit(), toolkit)
        self.soln = soln({}, 0, percent_err=0.0)
        self.warnings = []

        print(f"\n\n------------------------------------\n\nACCURACY:\n%.2E" % self.accuracy)

    def solve(self):
        solution_in_progress = True
        
        while solution_in_progress:
            number_of_known_values = len(self.soln.soln)
            self.warnings = []
            
            for line in self.lines:
                # line_number = self.lines.index(line) + 1
                line_soln = solve_line(line, uar(self.soln.soln, self.toolkit), target_dx=self.accuracy)

                if type(line_soln) == str:
                    print(f"\n\n------------------------------------\n\nWARNING: {line_soln}")
                    self.warnings.append(line_soln)

                elif line_soln != None:
                    self.soln.soln.update(line_soln.soln)
                    self.soln.duration += line_soln.duration

                    if line_soln.percent_err > self.soln.percent_err: 
                        self.soln.percent_err = line_soln.percent_err 
            
            if len(self.soln.soln) == number_of_known_values: # no new solutions have been found this loop, so break and report results.
                self.soln.soln = {item : self.soln.soln[item] for item in self.soln.soln if item not in self.toolkit.keys() and item != '__builtins__'}
                
                solution_in_progress = False
