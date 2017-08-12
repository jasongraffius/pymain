from pymain import pymain


@pymain
def main(first: int, second: int, *, message: str = None):
    print(first + second)
    if message is not None:
        print(message)
