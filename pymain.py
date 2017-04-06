from typing import Callable, Union
from functools import wraps

import argparse
import inspect

# To reduce probability of collision, the name of the module is included.
# Additionally, a syntactically invalid attribute string is used ("!!")
ALIAS_ATTR = '_!!_' + __name__ + '_aliases'

_Param = inspect.Parameter
_Sig = inspect.Parameter

MainFunc = Callable[..., None]


def _is_empty(src: Union[_Param, _Sig], val: Union[type, None]) -> bool:
    return val == type(src).empty


def alias(original: str, new: str) -> Callable[[MainFunc], MainFunc]:
    """Allows aliasing options, useful for short names.

    Used as a decorator, this function returns a function decorator which
    returns a wrapper, intended to be used for the main function. It adds
    an alias map to main, to be used in argument parsing.
    """

    def decorator(main: MainFunc) -> MainFunc:
        # Retrieve the alias map, or create a new one
        try:
            attrs = getattr(main, ALIAS_ATTR)
        except AttributeError:
            attrs = dict()
            setattr(main, ALIAS_ATTR, attrs)

        # Retrieve the list of aliases, or create a new one
        try:
            aliases = attrs[original]
        except KeyError:
            aliases = []
            attrs[original] = aliases

        aliases.append(new)
        return main

    return decorator


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
    aliases = getattr(main, ALIAS_ATTR, None)  # type: dict

    for p in required:
        parser.add_argument(p.name, type=p.annotation)
    for p in extended + optional:
        prefixer = lambda n: '--' + n if len(n) > 1 else '-' + n

        if aliases is not None:
            alias_list  = aliases.get(p.name, [])
            alias_list.append(p.name)

            flags = list(map(prefixer, alias_list))
        else:
            flags = [prefixer(p.name)]

        parser.add_argument(*flags, default=p.default, type=p.annotation)

    @wraps(main)
    def wrapper(*args, **kwargs):
        if args or kwargs:
            main(*args, **kwargs)
        else:
            main(**vars(parser.parse_args()))

    return wrapper
