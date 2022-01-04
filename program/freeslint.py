# -*- coding: utf-8 -*-

class frees_linter():
    
    def __init__(self, expr:str, scope:dict):
        
        self.expr = expr
        self.scope = scope
        
    def iter_solvable(self):
        """
        Checks if an expression is ready to be solved iteratively.
        (i.e. there is only one unknown value in rhs.)
        """
        
        lhs = self.expr.split("=")[0]
        rhs_and_var = self.expr.split("=")[1].split("!guess")[0]
        rhs = rhs_and_var.split("!guess")[0]
        var = rhs_and_var.split("!guess")[1].split()[0]
        
        # left-hand-side solvability?
        try:
            eval(lhs) 
        except:
            return False
        
        # right-hand-side already solved?
        try:
            for var in self.scope:
                rhs = rhs.replace(var, self.scope[var])
            eval(rhs)
            return False
        except:
            pass
        
        # any other variables in rhs?
        for char in rhs.replace(var, 00):
            if not char.isdigit() and char not in ["+-/*()%"]:
                return False
            
        return True
            
        
            
        