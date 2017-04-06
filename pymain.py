from typing import Callable, Union
from functools import wraps

import argparse
import inspect
import sys

_Param = inspect.Parameter
_Sig = inspect.Parameter

MainFunc = Callable[..., None]


def _is_empty(src: Union[_Param, _Sig], val: Union[type, None]) -> bool:
    return val == type(src).empty


def pymain(main: MainFunc) -> MainFunc:
    signature = inspect.signature(main)

    required = list()
    extended = list()
    optional = list()

    params = signature.parameters.values()
    for p in params:
        if p.kind == _Param.POSITIONAL_OR_KEYWORD:
            if _is_empty(p, p.default):
                required.append(p)
            else:
                extended.append(p)
        elif p.kind == _Param.KEYWORD_ONLY:
            optional.append(p)

    parser = argparse.ArgumentParser()

    for p in required:
        parser.add_argument(p.name, type=p.annotation)
    for p in extended + optional:
        prefix = '--' if len(p.name) > 1 else '-'
        parser.add_argument(prefix + p.name, default=p.default, type=p.annotation)

    @wraps(main)
    def wrapper(*args, **kwargs):
        if args or kwargs:
            main(*args, **kwargs)
        else:
            main(**vars(parser.parse_args()))

    return wrapper
