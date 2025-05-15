from typing import Callable
# from typing import Any, AsyncGenerator, Awaitable, Dict, Generator, List, Optional, Set, Tuple, Union

def a(x: int) -> None:
    print("a")

def b(a: Callable[[int], None]) -> None:
    a(1)

b(a)
