from frz_gui import frees_app
my_app = frees_app("tmp.frz") # NOTE: You can change the filepath to be a defult file location on startup
my_app.start()

# from frz_solver import solver
# print(
# solver("""
# y = 90

# y = x**5 + x**4 + x + 6 !guess x 0 10
# x = u**3 + u**2 + u + 5 !guess u -10 0

# r = x**2
# """)
# )