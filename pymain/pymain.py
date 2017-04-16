from functools import wraps
from itertools import chain
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

    Used as a decorator, this function returns a function decorator intended to
    be used for the main function. It adds an alias map to main, to be used in
    argument parsing.

    :param original: Either a parameter to alias, or a mapping of aliases.
    :param new: If original is supplied, the aliased form.

    :returns: Decorator that decorates a main function.
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
    """Wrap a main function

    Intended to be used as a decorator, this function will attempt to read
    the signature of the provided main function, and build a parser that can
    supply arguments to that function from command line arguments (sys.argv).

    This decorator can be used as ``@pymain`` (bare) or ``@pymain(param=value)``
    (with arguments). In the first form, pymain will detect if the defining
    module is ``'__main__'``, and if it is, call it before returning. To prevent
    that behavior, use the second form, setting ``auto`` to ``False``.

    :param main: The main function to wrap.
    :param auto: Whether to automatically call main or not (when not imported).

    :returns: Wrapper around main. Call with no arguments for sys.argv parsing.
    """

    def wrap(main: MainFunc) -> MainFunc:
        signature = inspect.signature(main)

        required = list()
        extended = list()
        optional = list()
        varargs = None

        params = signature.parameters.values()
        for p in params:
            if p.kind == _Param.POSITIONAL_OR_KEYWORD:
                if _is_empty(p, p.default):
                    required.append(p)
                else:
                    extended.append(p)
            elif p.kind == _Param.KEYWORD_ONLY:
                optional.append(p)
            elif p.kind == _Param.VAR_POSITIONAL:
                varargs = p

        parser = argparse.ArgumentParser()
        aliases = getattr(main, ALIAS_ATTR, None)

        for p in required:
            parser.add_argument(p.name, type=p.annotation)
        for p in extended:
            parser.add_argument(p.name, default=p.default, nargs='?',
                                type=p.annotation)
        if varargs is not None:
            p = varargs
            parser.add_argument(p.name, nargs="*", default=[],
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

        @wraps(main)
        def wrapper(*args, **kwargs):
            if args or kwargs:
                main(*args, **kwargs)
            else:
                results = vars(parser.parse_args())
                positional = chain(required, extended)

                args = [results[p.name] for p in positional]
                if varargs is not None:
                    args.extend(results[varargs.name])

                kwargs = {p.name: results[p.name] for p in optional}

                main(*args, **kwargs)

        if auto is None or auto:
            if inspect.getmodule(main).__name__ == '__main__':
                wrapper()

        return wrapper

    if main is None:
        return wrap
    else:
        return wrap(main)
