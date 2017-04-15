from functools import wraps
from typing import Callable, Union, List, Mapping

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


def alias(original: Union[str, Mapping[str, Union[str, List[str]]]],
          new: str = None) -> Callable[[MainFunc], MainFunc]:
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

        if new is None:
            # Parameter 'new' wasn't provided, so assume the dict form is given
            try:
                # Update attrs for each entry in aliases
                for k, v in original.items():
                    try:
                        aliases = attrs[k]
                    except KeyError:
                        aliases = []
                        attrs[k] = aliases

                    if isinstance(v, List):
                        aliases.extend(v)
                    else:
                        aliases.append(v)
            except TypeError:
                import sys
                print( "The one-parameter version of alias needs a dictionary",
                       "of alias mappings (original -> alias or [aliases]",
                       file=sys.stderr)
                raise
        else:
            # Retrieve the list of aliases, or create a new one
            try:
                aliases = attrs[original]
            except KeyError:
                aliases = []
                attrs[original] = aliases

            # Update with new alias
            aliases.append(new)

        return main

    return decorator


def pymain(main: MainFunc = None, *,
           auto = None) -> Union[MainFunc, Callable[[MainFunc], MainFunc]]:

    def wrap(main: MainFunc) -> MainFunc:
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
        aliases = getattr(main, ALIAS_ATTR, None)

        for p in required:
            parser.add_argument(p.name, type=p.annotation)
        for p in extended:
            parser.add_argument(p.name, default=p.default, nargs='?',
                                type=p.annotation)
        for p in optional:
            prefixer = lambda n: '--' + n if len(n) > 1 else '-' + n

            if aliases is not None:
                alias_list = [p.name]
                alias_list.extend(aliases.get(p.name, []))

                flags = list(map(prefixer, alias_list))
            else:
                flags = [prefixer(p.name)]

            parser.add_argument(*flags, default=p.default, type=p.annotation)

        if auto is None or auto:
            if inspect.getmodule(main).__name__ == '__main__':
                main(**vars(parser.parse_args()))

            return main
        else:
            @wraps(main)
            def wrapper(*args, **kwargs):
                if args or kwargs:
                    main(*args, **kwargs)
                else:
                    main(**vars(parser.parse_args()))

            return wrapper

    if main is None:
        return wrap
    else:
        return wrap(main)
