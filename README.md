# Pymain

Pymain - Simplified main

Pymain is a decorator and related tools to simplify your `main` function(s).
It is intended to be more simple to use and understand than `argparse` and
`docopt`, while still providing most of the functionality of those libraries.

### Description

The basic idea of `pymain` is that your main function (though it doesn't need
to be called "main"), and therefore your script or application itself, probably
takes parameters and keyword arguments in the form of command line arguments.
Since that interface works very similar to calling a python function, `pymain`
translates between those interfaces for you.

### Usage

Import and use the `@pymain` decorator before your main function that has type
annotations for the parameters. Then when you call your main function (such as
in an `if __name__ == '__main__'` block), call it with no arguments. Pymain
will then parse `sys.argv` and pass the appropriate parameters into main.

Pymain uses the type annotations to determine what types to expect. For short
options or aliases, you can add an `@alias` decorator after the `@pymain`
decorator describing the alias (either a single alias or a dictionary of
multiple)

### Examples

optional.py:
``` python
from pymain import pymain

@pymain
def main(a: float, b: float, c: str = None):
    print(a / b)
    if c is not None:
        print(c)

if __name__ == '__main__':
    main()
```

Command line:

``` bash
~ $ python optional.py 4 2
2.0
```

``` bash
~ $ python optional.py 9 2 message
4.5
message
```

keyword\.py:
``` python
from pymain import pymain

@pymain
def main(first: int, second: int, *, message: str = None):
    print(first + second)
    if message is not None:
        print(message)

if __name__ == '__main__':
    main()
```

Command line:
``` bash
~ $ python main.py 4 6
10
```

``` bash
~ $ python main.py 1 2 --message "Hello, World!"
3
Hello, World!
```
---

alias\.py:
``` python
from pymain import pymain, alias

@pymain
@alias({"opt1": "x", "opt2": "y"})
def foo(value: float, *, opt1: float = 1.0, opt2: float = 2.0):
    print(value + opt1)
    print(value - opt2)

if __name__ == '__main__':
    foo()
```

Command line:
``` bash
~ $ python alias.py 2
3.0
0.0
```

``` bash
~ $ python alias.py 5 -x 1 -y 1
6.0
4.0
```

```bash
~ $ python alias.py 10 --opt1 5 --opt2 2
15.0
8.0
```
