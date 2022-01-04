# -*- coding: utf-8 -*-
"""
FrEES - The Free, open source, Engineering Equation Solver
V0.0.0
Created on Sun Jan 2 17:42:23 2022

@author: Grant Christiansen
"""

def load(path:str, include_soln=False):
    """Returns the contents of a text file (or .frees file) as a string."""
    with open(path, "r") as f:
        if include_soln:
            return f.read()
        else:
            return f.read().split("\n\nFrEES SOLN:")[0] 



def system_solver(exprs:str):
    """
    Takes in a series of expressions as a string and solves for all unknown variables.
    exprs:str -> fn() -> res:dict
    """
    vars = {}
    print("Solving system. This may take a moment...")
    # Initial run through of expressions to get known values 
    for line in exprs.split("\n"):
        
        if len(line) != 0 and not line[0].isdigit() and not line.startswith("#"):
            
            thisline = line.split("=")  
            try: vars[thisline[0].strip()] = eval(thisline[1].strip())
            except: continue
    
    # Replace known values in expressions and solve for more variables
    solved = False
    while not solved:
        
        for var in vars:
        
            exprs = exprs.replace(var, str(vars[var]))
        
        solved = True # Assume expressions are solved until proven otherwise
        for line in exprs.split("\n"):
            
            # if there is a guess instruction TODO: and the line is iteratively solvable
            if "!guess" in line and not line.startswith("#"):# and frees_linter(line, scope=vars).iter_solvable():
                try:
                    args = line.split("!guess")[1].split()
                    
                    var_name = args[0] # variable to be estimated
                    print(f"\nAttempting iterative soln for {var_name}...")
                    print(f"Equation: {line}")
                    start = int(args[1]) # start guess value
                    end = int(args[2]) # end guess value
    
                    vars[var_name] = iter_solve(line, var_name, start, end)
                    print(f"Solved: {var_name} = {vars[var_name]}")
                    
                    # Remove line from expressions once solved
                    exprs.replace(line, "")
                
                except: 
                    print("Aborted iterative soln.")
                    continue
            
            # if the line is algebraically solved
            if len(line) != 0 and not line[0].isdigit() and not line.startswith("#"):
                                
                solved = False
                thisline = line.split("=")
                var_name = thisline[0].strip()
                print(f"\nAttempting algebraic soln for {var_name}...")
                var_expr = thisline[1].strip()
                try: 
            
                    vars[var_name] = eval(var_expr)
                    print(f"Solved: {var_name} = {vars[var_name]}")
                    
                except: 
                    print("Aborted algebraic soln.")
                    continue
                
    print("Done.")           
    return vars

        
def iter_solve(expr:str, target:str, low_bnd=-100000, up_bnd=100000, precision=0.001):
    """Iteratively solves a single equation if it is not algebraically solved"""

    lhs = expr.split("=")[0]
    rhs = expr.split("=")[1].split("!guess")[0]
    lhs = eval(lhs)
    
    # Necessary to create a range of floats. Annoying...
    up_bnd *= 100
    low_bnd *= 100
    
    # Get the initial lists ready to sweep
    sweep_range = [i/100 for i in range(low_bnd, up_bnd)]
    rhs_range = [rhs.replace(target, str(i)) for i in sweep_range]
    
    # Find error sequence
    err = [abs(lhs - eval(rhs)) for rhs in rhs_range]
    
    # Find the index of the minimum error and proceed to iterative sweeps
    mei = err.index(min(err)) # index of minimum error
    
    estimate = sweep_range[mei]
    
    # while err[mei]/lhs > precision: 
    #     prev_range = up_bnd - low_bnd
        
    #     if mei == 0: # look further in -x direction next sweep
    #         print("Looking left..")
    #         up_bnd = copy(low_bnd)
    #         low_bnd = low_bnd - prev_range
    #         sweep_range = [i/100 for i in range(low_bnd, up_bnd)]

    #     elif mei == len(err)-1: # look further in +x direction next sweep
    #         print("Looking right..")    
    #         low_bnd = copy(up_bnd)    
    #         up_bnd = up_bnd + prev_range
    #         sweep_range = [i/100 for i in range(low_bnd, up_bnd)]
        
    #     else: # center search around mei and increase resolution next sweep
    #         print("Enhancing")
    #         up_bnd = int(sweep_range[mei+1]*100)
    #         low_bnd = int(sweep_range[mei-1]*100)
    #         sweep_range = [i/10000 for i in range(low_bnd, up_bnd)]
    
    #     rhs_range = [rhs.replace(target, str(i)) for i in sweep_range]
    #     err = [abs(lhs - eval(rhs)) for rhs in rhs_range]
    #     mei = err.index(min(err))
        
    #     estimate = sweep_range[mei]
    
    print(f"Iterative solution found with {round(100*err[mei]/lhs, 3)}% error")
    return estimate 




        
# Uncomment to test
# solve(".\\demo.frees")
#print(iter_solve("72 = x**2 + x + 6", "x", 0, 10))
#solve(x**2 + x + 6 - 72, x)