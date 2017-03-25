
from typing import Callable
from functools import wraps

import inspect
import sys


def pymain(main: Callable[..., None]) -> Callable[..., None]:
    signature = inspect.signature(main)

    @wraps(main)
    def wrapper(*args, **kwargs):
        if args or kwargs:
            main(*args, **kwargs)
        else:
            args = list()
            for p, a in zip(signature.parameters.values(), sys.argv[1:]):
                args.append(p.annotation(a))

            main(*args)

    return wrapper
