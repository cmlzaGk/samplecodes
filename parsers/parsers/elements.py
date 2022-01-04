'''
class definitions for elements of a context free grammar
'''

from dataclasses import dataclass, field
from abc import ABC

class GrammarToken(ABC): # pylint: disable=too-few-public-methods
    '''
        Empty Class
    '''

@dataclass(frozen=True)
class NonTerminal(GrammarToken):
    '''
        The nonterminal
    '''
    symbol: str

@dataclass(frozen=True)
class GrammarTerminal(GrammarToken):
    '''
        GrammarTerminal has a symbol and a val
        GrammarTerminal(sym='int', val=5)
        The special aspect of GrammarTerminal is that the object equality only on sym.

        This means that the following set creation will have only one element
        set([GrammarTerminal(sym='int', val=5),
             GrammarTerminal(sym='int', val=6)])
    '''
    symbol: str
    val: object = field(compare=False)

class Start(NonTerminal): # pylint: disable=too-few-public-methods
    '''
        The Start class
    '''

class Epsilon(GrammarToken): # pylint: disable=too-few-public-methods
    '''
        The Epsilon
    '''

class Eof(GrammarToken): # pylint: disable=too-few-public-methods
    '''
        The Eof
    '''

@dataclass
class Alternate:
    '''
        data class to hold the right side of a production A->B

        data = list of tokens
    '''
    data : list[GrammarToken]

    def __str__(self):
        return ''.join([t.symbol for t in self.data])


@dataclass
class Rule:
    '''
        Simple data class to hold the right side of a production A->B|C
        data = dictionary of rules
            key = NonTerminal A
            value = List of Rules [B, C]
    '''
    alts : list[Alternate]
    ident: NonTerminal
