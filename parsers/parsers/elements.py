'''
class definitions for elements of a context free grammar
'''

from dataclasses import dataclass, field
from abc import ABC

@dataclass(frozen=True)
class GrammarToken(ABC): # pylint: disable=too-few-public-methods
    '''
        Base class for Grammar tokens.
    '''
    symbol: str

class NonTerminal(GrammarToken):
    '''
        The nonterminal
    '''
    def __str__(self) -> str:
        return self.symbol

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
    val: object = field(compare=False)

    def __str__(self) -> str:
        return self.symbol

@dataclass(frozen=True)
class Start(NonTerminal): # pylint: disable=too-few-public-methods
    '''
        The Start class
    '''

@dataclass(frozen=True)
class Epsilon(GrammarToken): # pylint: disable=too-few-public-methods
    '''
        The Epsilon
    '''
    def __str__(self) -> str:
        return self.symbol

@dataclass(frozen=True)
class Eof(GrammarToken): # pylint: disable=too-few-public-methods
    '''
        The Eof.
        Eof's symbol is only for logging
        so Eof(None) == Eof('anything') is True
    '''

    symbol: str = field(compare=False)

    def __str__(self) -> str:
        return '$'

@dataclass
class Alternate:
    '''
        data class to hold the right side of a production A->B

        data = list of tokens
    '''
    data : list[GrammarToken]

    def __str__(self) -> str:
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

@dataclass
class Grammar:
    '''
        Grammer DataClass
    '''
    terminals: set[GrammarTerminal]
    data: dict[NonTerminal, Rule]
    start: NonTerminal
    endmarker: Eof
    epsilon: NonTerminal
