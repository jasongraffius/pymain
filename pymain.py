
from typing import Callable


# Decorator
def pymain(main: Callable[..., None]) -> Callable[..., None]:
    return main
