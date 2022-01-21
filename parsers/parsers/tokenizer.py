'''
Tokenizer module performs lexical analysis for parsers in this library
'''
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable, Iterator

from .peeker import Peeker


SHOULD_NOT_BE_IN_WORD = ["'", '"']

class TokenizerException(Exception):
    '''
        Exception during Tokenization
    '''

class TokenType(Enum):
    '''
        A word is a series of characters seperated by white-space
        STRING is any word within single quotes or double quotes
        INT is any word that can be an integer.
        NAME is everything else

    '''
    SPACE = auto()
    NAME = auto()
    STRING = auto()
    INT = auto()
    EOF = auto()

@dataclass
class Token:
    '''
        dataclass to hold the token and value.
        This object can have the file location for error reporting later.
    '''
    tokentype: TokenType
    value: object

# return an iterator of words
def words(iterable: Iterable[str]) -> Iterator[str]:
    '''
        Generator class to provide a list of words
        The difference between split() and words() is that words() generates a different
        item for each space character in the iterator
    '''
    peeker = Peeker(iterable)
    word = []
    # peeker.peek() is idempotent and peeker.next() resets peeker.peek()
    while peeker.peek():
        # generate spaces one by one
        while peeker.peek().isspace():
            yield peeker.next()
        #generate a word
        word = ''
        while peeker.peek() and not peeker.peek().isspace():
            word += peeker.next()
        if word:
            yield word

def _valid_word(word:str) -> bool:
    return not any(x in word for x in SHOULD_NOT_BE_IN_WORD)

def tokenizer(iterable: Iterable[str]) -> Iterator[Token]:
    '''
        Geneator function returns tokens from an iterator of strs
    '''
    for word in words(iterable):
        if word.isnumeric():
            yield Token(tokentype=TokenType.INT, value=int(word))
        elif word[0] == "'" \
            and word[-1] == "'" \
            and len(word[1:-1]) \
            and _valid_word(word[1:-1]):
            yield Token(tokentype=TokenType.STRING, value=word)
        elif word[0] == '"' \
            and word[-1] == '"' \
            and len(word[1:-1]) \
            and _valid_word(word[1:-1]):
            yield Token(tokentype=TokenType.STRING, value=word)
        elif word.isspace():
            yield Token(tokentype=TokenType.SPACE, value=word)
        elif _valid_word(word):
            yield Token(tokentype=TokenType.NAME, value=word)
        else:
            raise TokenizerException(f'We messed up {word}')
    yield Token(tokentype=TokenType.EOF, value=None)

