class Stack:
    def __init__(self):
        self._data = []

    def push(self, element):
        self._data.append(element)

    def pop(self):
        return self._data.pop()

    def peek(self):
        return self._data[-1]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    def __iter__(self):
        return iter(reversed(self._data))