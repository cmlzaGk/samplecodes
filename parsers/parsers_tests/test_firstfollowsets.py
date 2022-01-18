import unittest

from parsers import FirstFollowSet
from parsers.elements import GrammarTerminal, NonTerminal, Eof, Epsilon

class TestFirstFollow(unittest.TestCase):

    def test_firstfollow_init(self):

        f = FirstFollowSet()
        self.assertEqual(f.dirty, False)
        self.assertEqual(len(f.data), 0)

    def test_firstfollow_emptyset(self):

        f = FirstFollowSet()
        t = GrammarTerminal(symbol='a', val=5)
        f.add_empty(t)
        self.assertEqual(f.dirty, True)
        self.assertEqual(f.get(t), set())

    def test_firstfollow_empty_and_add(self):
        f = FirstFollowSet()
        t = GrammarTerminal(symbol='a', val=5)
        f.add_empty(t)

        v = [GrammarTerminal('x', 5), NonTerminal('y')]
        f.add(t, v)

        self.assertEqual(f.get(t), set(v))

    def test_firstfollow_key_compat(self):
        f = FirstFollowSet()
        t = NonTerminal(symbol='a')
        v = [GrammarTerminal('x', 7), NonTerminal('y')]
        f.add(t, v)

        self.assertEqual(f.get(t), set(v))
        self.assertEqual(f.get([t]), set(v))
        self.assertEqual(f.get(tuple([t])), set(v))

    def test_firstfollow_multi_add(self):
        f = FirstFollowSet()
        t = GrammarTerminal('a', '4')
        v1 = [GrammarTerminal('x', 'a'), NonTerminal('y')]
        v2 = [GrammarTerminal('u', 10), NonTerminal('v')]
        v3 = [GrammarTerminal('p', 'x'), NonTerminal('v')]

        f.dirty = False
        f.add(t, v1)
        self.assertEqual(f.get(t), set(v1))
        self.assertEqual(f.dirty, True)

        f.dirty = False
        f.add(t, v2)
        self.assertEqual(f.get(t), set(v1).union(v2))
        self.assertEqual(f.dirty, True)

        f.dirty = False
        f.add(t, v3)
        self.assertEqual(f.dirty, True)
        self.assertEqual(f.get(t), set(v1).union(v2).union(v3))

        # adding v3 again should not change anything, so dirty should not be reset
        f.dirty = False
        f.add(t, v3)
        self.assertEqual(f.get(t), set(v1).union(v2).union(v3))
        self.assertEqual(f.dirty, False)

    def test_remove(self):
        f = FirstFollowSet()
        t = GrammarTerminal('a', 10)
        # GrammarTerminal second argument is not used for equality comparisons
        v_add = [GrammarTerminal('x', 10), NonTerminal('y'), Eof('4')]
        v_remove = [GrammarTerminal('x', 15), NonTerminal('p')]
        f.add(t, v_add)
        self.assertEqual(f.get(t), set(v_add))

        f.dirty = False
        f.remove(t, v_remove)
        self.assertEqual(f.get(t), set(v_add) - set(v_remove))
        self.assertEqual(f.dirty, True)

        # Second removal should be no-op, so dirty should remain False
        f.dirty = False
        f.remove(t, v_remove)
        self.assertEqual(f.dirty, False)

    def test_multiple_items(self):
        f = FirstFollowSet()
        t1 = GrammarTerminal('a', 10)
        t2 = GrammarTerminal('b', 15)
        v1 = [GrammarTerminal('x', 10), NonTerminal('y')]
        v2 = [GrammarTerminal('u', 7)]

        f.add(t1, v1)
        f.add(t2, v2)

        self.assertEqual(f.get(t1), set(v1))
        self.assertEqual(f.get(t2), set(v2))

    def test_higher_order_keylen(self):
        f = FirstFollowSet()

        t1 = [NonTerminal('a'), GrammarTerminal('b', 7)]
        v1 = [NonTerminal('k'), Epsilon('e'), Eof(None)]
        f.add(t1, v1)
        self.assertEqual(f.get(t1), set(v1))
        self.assertEqual(f.get(tuple(t1)), set(v1))

        # Make sure t1 is ordered, by reversing the elements we should end up with an empty set returned.
        # also a test for empty return
        t2 = list(reversed(t1))
        self.assertEqual(f.get(t2), set())
        self.assertEqual(f.get(tuple(t2)), set())