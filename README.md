# Pymain

Pymain - simplified main

Pymain is a decorator and related tools to simplify your `main` function(s).
It is intended to be more simple to use and understand than `argparse` and
`docopt`, while still providing most of the functionality of those libraries.

### Description

The basic idea of `pymain` is that your main function (though it doesn't need
to be called "main"), and therefore your script or application itself, probably
takes parameters and keyword arguments in the form of command line arguments.
Since that interface sounds almost exactly like calling a python function,
`pymain` translates between those interfaces for you.
