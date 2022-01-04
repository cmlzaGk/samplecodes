import unittest

from parsers import GrammarTerminal

class TestElements(unittest.TestCase):
    def test_grammarterminal(self):
        '''
            A terminal should be hashable and have equality based on its symbol and not val
        '''

        first = GrammarTerminal(symbol='symA', val='valA')
        second = GrammarTerminal(symbol='symA', val='valB')
        third =  GrammarTerminal(symbol='symC', val='valC')

        self.assertEqual(first, second)
        self.assertNotEqual(first, third)

        myset = set()

        myset.add(first)
        self.assertEqual(len(myset), 1)
        myset.add(second)
        self.assertEqual(len(myset), 1)
        myset.add(third)
        self.assertEqual(len(myset), 2)