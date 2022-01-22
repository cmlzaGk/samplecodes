
'''
    Class Peeker wraps an iterable and provides an additional
    peek functionality
'''
from typing import Iterator, Optional

# TODO : Make this class generic and add tests
class Peeker:
    '''
        Class Peeker wraps an iterable and provides an additional
        peek functionality

        arguments:
        iterable -> iterable of str

        peek() and next() returns None if StopIteration is encountered
        This is ok because iterable is supposed to be iterator of str
    '''
    def __init__(self, iterable: Iterator[str]):
        self._iter: Iterator[str] = iterable
        self._p: Optional[str] = None

    def _peek(self) -> str:
        self._p = self._p if self._p else next(self._iter)
        return self._p

    def peek(self) -> Optional[str]:
        '''
            returns the next element without consuming it from next()
            None if StopIteration is called
        '''
        try:
            return self._peek()
        except StopIteration:
            return None

    def _next(self) -> Optional[str]:
        lastpeek, self._p = self._p, None
        if lastpeek:
            return lastpeek
        return next(self._iter)

    def next(self) -> Optional[str]:
        '''
            consumes an element from iterator and returns it.
            None if StopIteration is called
        '''
        try:
            return self._next()
        except StopIteration:
            return None
