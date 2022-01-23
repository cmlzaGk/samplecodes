'''
    Internal module to hold the first-follow sets
    TODO : Put better type hints for dictionary contents
'''

from dataclasses import dataclass, field
from .elements import GrammarToken

# Type Variables
FirstFollowKeyType = tuple[GrammarToken, ...]
FirstFollowValueType = set[GrammarToken]

compatiblekeys = FirstFollowKeyType | list[GrammarToken] | GrammarToken
compatiblevalues = FirstFollowValueType | list[GrammarToken] | GrammarToken

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
    data : dict[FirstFollowKeyType, FirstFollowValueType] = field(default_factory=dict,
                                                            init=False)
    dirty: bool = field(default=False, init=False)

    @staticmethod
    def _compatible_key_type(k: compatiblekeys) -> FirstFollowKeyType:

        if isinstance(k, tuple):
            return k
        if isinstance(k, list):
            return tuple(k)
        if isinstance(k, GrammarToken):
            return tuple([k])
        raise Exception (f'Unknown type {type(k)} for {k}')

    @staticmethod
    def _compatible_value_type(token_s: compatiblevalues) -> FirstFollowValueType:

        if isinstance(token_s, set):
            return token_s
        if isinstance(token_s, list):
            return set(token_s)
        if isinstance(token_s, GrammarToken):
            return set([token_s])
        raise Exception (f'Unknown type {type(token_s)} for {token_s}')

    def add(self, key: compatiblekeys, token_s: compatiblevalues):
        '''
            add set of tokens in token_s to the set in dict[key]
            update dirty if the dict[key] was modified
        '''

        key, token_s = (FirstFollowSet._compatible_key_type(key)
                        , FirstFollowSet._compatible_value_type(token_s))

        old = self.data.get(key, None)

        self.data[key] = self.data.get(key, set()).union(token_s)

        self.dirty = self.dirty or (old != self.data[key])

    def add_empty(self, k: compatiblekeys):
        '''
            create an empty set in dict[key] if not present
            update dirty if the dict[k] was modified
        '''

        dictkey = FirstFollowSet._compatible_key_type(k)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set())

        self.dirty = self.dirty or (old != self.data[dictkey])

    def remove(self, k: compatiblekeys, removeset: compatiblevalues):
        '''
            remove set of tokens in token_s from the set in dict[key]
            update dirty if the dict[key] was modified
        '''

        dictkey = FirstFollowSet._compatible_key_type(k)

        removeset = FirstFollowSet._compatible_value_type(removeset)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set()) - removeset

        self.dirty = self.dirty or (old != self.data[dictkey])

    def get(self, k: compatiblekeys):
        '''
            return self.data[k]
        '''
        dictkey = FirstFollowSet._compatible_key_type(k)

        return self.data.get(dictkey, set())

    def __str__(self):
        combined_str = []
        for k,val in self.data.items():
            k_str = ','.join([str(x) for x in k])
            v_str = ','.join([str(x) for x in val])
            combined_str.append(f'[{k_str}] => [{v_str}]')
        return ', '.join(combined_str)
