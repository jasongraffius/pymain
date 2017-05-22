from functools import wraps
from itertools import chain
from typing import Callable, List, Mapping, TypeVar, Union

import argparse
import inspect

# To reduce probability of collision, the name of the module is included.
# Additionally, a syntactically invalid attribute string is used ("!!")
ALIAS_ATTR = '_!!_' + __name__ + '_aliases'

Param = inspect.Parameter
Sig = inspect.Signature

MainFunc = Callable[..., None]
Main = TypeVar('Main', bound=MainFunc)


def is_empty(src: Union[Param, Sig], val: Union[type, None]) -> bool:
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
                print("The one-parameter version of alias needs a dictionary",
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


def pymain(main: Main = None, *,
           aliases: Mapping[str, str] = None,
           auto: bool = None,
           use_help: bool = True) -> Union[Main, Callable[[Main], Main]]:
    """Wrap a main function

    Intended to be used as a decorator, this function will attempt to read
    the signature of the provided main function, and build a parser that can
    supply arguments to that function from command line arguments (sys.argv).

    This decorator can be used as ``@pymain`` (bare) or ``@pymain(param=value)``
    (with arguments). In the first form, pymain will detect if the defining
    module is ``'__main__'``, and if it is, call it before returning. To prevent
    that behavior, use the second form, setting ``auto`` to ``False``.

    :param main: The main function to wrap.
    :param aliases: Aliases to apply (see ``alias`` function).
    :param auto: Whether to automatically call main or not (when not imported).
    :param use_help: When ``True``, automatically adds a help parameter ``-h``.

    :returns: Wrapper around main. Call with no arguments for sys.argv parsing.
    """

    def wrap(m: MainFunc) -> MainFunc:
        signature = inspect.signature(m)

        # Track the various forms of parameters
        required = list()
        extended = list()
        optional = list()
        varargs = None

        # Split parameters into each list
        params = signature.parameters.values()
        for p in params:
            if p.kind == Param.POSITIONAL_OR_KEYWORD:
                if is_empty(p, p.default):
                    required.append(p)
                else:
                    extended.append(p)
            elif p.kind == Param.KEYWORD_ONLY:
                optional.append(p)
            elif p.kind == Param.VAR_POSITIONAL:
                varargs = p

        # Start builing an argument parser
        parser = argparse.ArgumentParser(add_help=use_help)

        # Update with passed-in aliases, if provided
        if aliases is not None:
            alias_decorate = alias(aliases)
            alias_decorate(m)

        # Check for aliases
        defined_aliases = getattr(m, ALIAS_ATTR, None)

        # Add each form of parameter to the argument parser
        for p in required:
            t = p.annotation if not is_empty(p, p.annotation) else str
            parser.add_argument(p.name, type=t)
        for p in extended:
            t = p.annotation if not is_empty(p, p.annotation) else str
            parser.add_argument(p.name, default=p.default, nargs='?',
                                type=t)
        if varargs is not None:
            p = varargs
            t = p.annotation if not is_empty(p, p.annotation) else str
            parser.add_argument(p.name, nargs="*", default=[],
                                type=t)
        for p in optional:
            def prefixer(n: str) -> str:
                return '--' + n if len(n) > 1 else '-' + n

            if defined_aliases is not None:
                alias_list = [p.name]
                alias_list.extend(defined_aliases.get(p.name, []))

                flags = list(map(prefixer, alias_list))
            else:
                flags = [prefixer(p.name)]

            t = p.annotation if not is_empty(p, p.annotation) else str
            parser.add_argument(*flags, default=p.default, type=t)

        # Produce the returned wrapper
        @wraps(m)
        def wrapper(*args, **kwargs):
            if args or kwargs:
                # Currently does not support calling a main function with no
                # arguments or only default arguments.
                m(*args, **kwargs)
            else:
                # Main was called with no arguments, parse sys.arv
                results = vars(parser.parse_args())
                positional = chain(required, extended)

                # Build the list of positional arguments, in order
                args = [results[param.name] for param in positional]
                if varargs is not None:
                    args.extend(results[varargs.name])

                # Build the dictionary of keyword arguments, in order
                kwargs = {param.name: results[param.name] for param in optional}

                # Call original main with the supplied arguments
                m(*args, **kwargs)

        # Automatically call main if it is defined in __main__
        if auto is None or auto:
            if inspect.getmodule(m).__name__ == '__main__':
                wrapper()

        return wrapper

    # Determine if called as a bare decorator or with arguments
    if main is None:
        return wrap
    else:
        return wrap(main)
