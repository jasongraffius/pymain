from pymain import pymain, alias


@pymain
@alias({"opt1": "x", "opt2": "y"})
def foo(value: float, *, opt1: float = 1.0, opt2: float = 2.0):
    print(value + opt1)
    print(value - opt2)
