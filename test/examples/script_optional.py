from pymain import pymain


@pymain
def main(a: float, b: float, c: str = None):
    print(a / b)
    if c is not None:
        print(c)
