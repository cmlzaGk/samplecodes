import unittest

from parsers import tokenizer, TokenType, TokenizerException

class TokenizerTests(unittest.TestCase):
    def test_tokenizer(self):
        buffer = 'Today   is the 5th day of the week for 1 person'
        expected = [(TokenType.NAME, 'Today'),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'is'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'the'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, '5th'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'day'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'of'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'the'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'week'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'for'),
            (TokenType.SPACE, ' '),
            (TokenType.INT, 1),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'person'),
            (TokenType.EOF, None)]
        result = [(t.tokentype, t.value) for t in list(tokenizer(iter(buffer)))]
        self.assertEqual(result, expected)

    def test_tokenizer_nl(self):
        buffer = '''Today   is the 5th day of the 
        
        week for 1 person'''
        expected = [(TokenType.NAME, 'Today'),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'is'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'the'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, '5th'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'day'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'of'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'the'),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, '\n'),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, '\n'),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'week'),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'for'),
            (TokenType.SPACE, ' '),
            (TokenType.INT, 1),
            (TokenType.SPACE, ' '),
            (TokenType.NAME, 'person'),
            (TokenType.EOF, None)]
        result = [(t.tokentype, t.value) for t in list(tokenizer(iter(buffer)))]
        self.assertEqual(result, expected)

    def test_bad_input(self):
        buffer = '''Today "  is the 5th day of the '''
        with self.assertRaises(TokenizerException):
            list(tokenizer(iter(buffer)))