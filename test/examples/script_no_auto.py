from pymain import pymain


@pymain(auto=False)
def fail(aval: int) -> None:
    print('Main was called.')
    exit(3)
