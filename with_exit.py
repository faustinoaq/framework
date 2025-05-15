# from new_balboa import Balboa

# app = Balboa(__name__)

# @app.get("/")
# def handler():
#     return "<p>Hello, World!</p>"

# @app.get("/name")
# def handler():
#     return ('Hello, Name!')

# app.run()

class A:
    def __init__(self):
        self.a = None
    def __enter__(self):
        print('enter')
        return self
    def __exit__(self, *args):
        print('exit')
        self.__del__()

with A() as a:
    a.a = 1
    print(a.a)

print(a.a)
