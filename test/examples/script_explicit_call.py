from pymain import pymain


@pymain(auto=False)
def fail(aval: int) -> None:
    print('Fail was called.')
    exit(3)


@pymain(auto=False)
def success(aval: int) -> None:
    print('Success was called.')
    exit(aval)


if __name__ == '__main__':
    success.as_main()
