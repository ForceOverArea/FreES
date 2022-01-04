# FrEES
A stab at making a free, open source equation solving program.

# Objectives
Quickly solve a set of equations based on a collection of input values. 
- Solve systems of algebraically solved equations
- Solve equations iteratively when algebraic solutions are difficult/impractical
- Allow use of common constant values in science and engineering from a library of values
- Allow use of conversion factors between different sets of units
- Be presentable and easy to pick up for less code/cli-savvy users
- Be easy to modify/build onto by engineers and scientists (Uses TKinter, Python, JSON)

# Get Started
FrEES uses the python eval() function to read equations, so make sure to use '**' to denote exponents and '#' to denote comments. 
FrEES can solve systems of equations easily so long as the variable being sought after is on the left hand side of the equation.
For example... 

y = 5
x = y + 2

Would return the solution y = 5, x = 7. For cases where this is not practical, instruct FrEES to solve by iteration/estimation:
For example...

y = 60
y = x**5 + 7 * x + 6 !guess x 0 10

Will estimate the x required to (almost) satisfy the system on the domain 0 < x < 10. (From the syntax: !guess x 0 10)
The resulting solution is y = 60, x = 2.08. By comparison, the solution on Desmos.com's graphing calculator is x = 2.085, y = 60.

This is still very much a WIP.
