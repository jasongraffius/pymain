from typing import Callable, Union
from functools import wraps

import inspect
import sys

_Param = inspect.Parameter
_Sig = inspect.Parameter


def _is_empty(src: Union[_Param, _Sig], val: Union[type, None]) -> bool:
    return val == type(src).empty


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
