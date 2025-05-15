from typing import Any


class Balboa:
    def __init__(self, name):
        self.router = {}

    def run(self):
        for path, handler in self.router.items():
            print(f'{path}: {handler()}')

    def get(self, path):
        self.path = path
        return self
    
    def __call__(self, handler):
        self.router[self.path] = handler

    def __invert__(self, handler):
        self.__call__(handler)
