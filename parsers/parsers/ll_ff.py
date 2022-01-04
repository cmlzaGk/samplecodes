'''
    Internal module to hold the first-follow sets
    TODO : Put better type hints for dictionary contents
'''

from dataclasses import dataclass, field
from .elements import GrammarToken

@dataclass
class FirstFollowSet:
    '''
        Data class to hold first and follow sets
            data = dict
                key = tuple made up of GrammarElements. Hence is a word of the grammar
                value = set of GrammarTokens.

            dirty = bool
                is set to True if there is any update of data using companion functions.
                It is caller's responsibility to reset it.
        Companion Methods - add_empty, add, remove, get

        FirstFollowSet is basically a data-structure to mantain a word -> set(Tokens) data
        The only additional functionality is provided by a dirty check for any set operation
    '''
    data : dict = field(default_factory=dict)
    dirty: bool = False

    @staticmethod
    def _compatible_key_type(k):

        match k:
            case tuple():
                return k
            case [*_]:
                return tuple(k)
            case GrammarToken():
                return tuple([k])
            case _:
                raise Exception (f'Unknown type {type(k)} for {k}')

    @staticmethod
    def _compatible_value_type(token_s):

        match token_s:
            case set():
                return token_s
            case [*_]:
                return set(token_s)
            case GrammarToken():
                return set([token_s])
            case _:
                raise Exception (f'Unknown type {type(token_s)} for {token_s}')

    def add(self, key, token_s):
        '''
            add set of tokens in token_s to the set in dict[key]
            update dirty if the dict[key] was modified
        '''

        key, token_s = (FirstFollowSet._compatible_key_type(key)
                        , FirstFollowSet._compatible_value_type(token_s))

        old = self.data.get(key, None)

        self.data[key] = self.data.get(key, set()).union(token_s)

        self.dirty = self.dirty or (old != self.data[key])

    def add_empty(self, k):
        '''
            create an empty set in dict[key] if not present
            update dirty if the dict[k] was modified
        '''

        dictkey = FirstFollowSet._compatible_key_type(k)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set())

        self.dirty = self.dirty or (old != self.data[dictkey])

    def remove(self, k, removeset):
        '''
            remove set of tokens in token_s from the set in dict[key]
            update dirty if the dict[key] was modified
        '''

        dictkey = FirstFollowSet._compatible_key_type(k)

        removeset = FirstFollowSet._compatible_value_type(removeset)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set()) - removeset

        self.dirty = self.dirty or (old != self.data[dictkey])

    def get(self, k):
        '''
            return self.data[k]
        '''
        dictkey = FirstFollowSet._compatible_key_type(k)

        return self.data.get(dictkey, set())
