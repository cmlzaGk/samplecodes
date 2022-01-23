'''
    Module Stack contains generic Stack
'''
from typing import Generic, Iterator, TypeVar

T = TypeVar('T') # pylint: disable=invalid-name

class Stack(Generic[T]):
    '''
        Class stack
    '''
    def __init__(self):
        self._data = []

    def push(self, element: T):
        '''
            push
        '''
        self._data.append(element)

    def pop(self) -> T:
        '''
            pop
        '''
        return self._data.pop()

    def peek(self) -> T:
        '''
            peek
        '''
        return self._data[-1]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(reversed(self._data))
