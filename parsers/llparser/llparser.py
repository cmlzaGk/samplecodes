from dataclasses import dataclass, field

from os import pardir
from typing import ParamSpecArgs
import unittest


@dataclass(frozen=True)
class Token:
    symbol: str
    def __str__(self):
        return self.symbol

class NonTerminal(Token):
    pass

class Terminal(Token):
    pass

class Start(NonTerminal):
    pass

class Epsilon(Token):
    pass

class Eof(Token):
    pass

@dataclass
class ProductionRule:
    '''
        Simple data class to hold the right side of a production A->B

        data = list of tokens
    '''
    data : list[Token] = field(default_factory=list)

    def add(self, element: Token):
        self.data.append(element)

    def __str__(self):
        return ''.join([t.symbol for t in self.data])


@dataclass
class ProductionRules:
    '''
        Simple data class to hold the right side of a production A->B|C
        data = dictionary of rules
            key = NonTerminal A
            value = List of Rules [B, C]
    '''
    data : dict = field(default_factory=dict)

    def add(self, k: NonTerminal, element: ProductionRule):
        self.data[k] = self.data.get(k, [])
        self.data[k].append(element)



@dataclass
class FirstFollowSet:
    '''
        Data class to hold first and follow sets
            data = dict
                key = tuple or ordered production rules. eg. A -> wABCq, key is some subset of right hand side eg.tuple([ABCq])
                value = set of tokens(terminals, nonterminals, eof, start, epsilon)
            dirty = bool
                is set to True if there is any update of data using companion functions.
                It is caller's responsibility to reset it. 
        Companion Methods - add_empty, add, remove, get
    '''
    data : dict = field(default_factory=dict)
    dirty: bool = False

    @staticmethod
    def compatible_key_type(k):

        if type(k) is tuple:
            return k

        if type(k) is list:
            return tuple(k)

        if isinstance(k, Token):
            return tuple([k])

        raise Exception ('Unknown type {} for {}'.format(type(k), k))

    @staticmethod
    def compatible_value_type(k):

        if type(k) is set:
            return k

        if type(k) is list:
            return set(k)

        if isinstance(k, Token):
            return set([k])

        raise Exception ('Unknown type {} for {}'.format(type(k), k))

    def add(self, k, v):

        k, v = FirstFollowSet.compatible_key_type(k), FirstFollowSet.compatible_value_type(v)

        old = self.data.get(k, None)

        self.data[k] = self.data.get(k, set()).union(set(v))

        self.dirty = self.dirty or (old != self.data[k])

    def add_empty(self, k):

        dictkey = FirstFollowSet.compatible_key_type(k)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set())

        self.dirty = self.dirty or (old != self.data[dictkey])

    def remove(self, k, removeset):

        dictkey = FirstFollowSet.compatible_key_type(k)

        removeset = FirstFollowSet.compatible_value_type(removeset)

        old = self.data.get(dictkey, None)

        self.data[dictkey] = self.data.get(dictkey, set()) - removeset

        self.dirty = self.dirty or (old != self.data[dictkey])

    def get(self, k):
        dictkey = FirstFollowSet.compatible_key_type(k)

        return self.data.get(dictkey, set())

def create_ll_firsts_follows(g):

    '''
        Function that creates the firsts and follows.
        Is called by constructor. 

        _create_firsts_follows initializes firsts and follows set, 
            and keeps applying update rules via _firsts_loop till there is more first and follow

        This is an implementation of algorithm : https://en.wikipedia.org/wiki/LL_parser

        Fi, Fo = First, Follow sets

        Fi(W) is a set of terminals that are the first terminals of all derivations of W where W is made up of NonTerminal and Terminals. 
        Fo(A) is a set of terminals {a} such that a string w'Aaw'' can be derived from S as the start symbol.

        1 For every Ai -> Wi
            1. initialize every Fi(Ai) and Fi(Wi) with the empty set
            2. initialize Fo(S) with EOF ($)

        while Fi and Fo dont change
            2. For each element in Fi
                1. Fi(aw') = { a } for every terminal a
                2. Fi(Aw') = Fi(A) for every nonterminal A with ε not in Fi(A)
                3. Fi(Aw') = (Fi(A) \ { ε }) ∪ Fi(w' ) for every nonterminal A with ε in Fi(A)
                4. Fi(ε) = { ε }
            3. For every Ai -> Wi:
                1. add Fi(wi) to Fi(Ai) 
            4. For every Aj → wAiw'
                1. if the terminal a is in Fi(w' ), then add a to Fo(Ai)
                2. if ε is in Fi(w' ), then add Fo(Aj) to Fo(Ai)
                3. if w' has length 0, then add Fo(Aj) to Fo(Ai)

        A Context Free Grammar (CFG) is made up of Start Element S, Production Rules Ai->Wi, a set of terminal characters, 
        a set of non-terminal characters. 
        The character epslion is an empty rule. 


        For a language Ai->Wi 
        Fi(w) = set(a,b,c) => the elements of Fi(w) are terminals that 

    '''

    firsts, follows = FirstFollowSet(), FirstFollowSet()

    for nonterminal in g.productions.data:
        firsts.add_empty([nonterminal])
        for rule in g.productions.data[nonterminal]:
            firsts.add_empty(rule.data)

    follows.add(g.start, g.eof)

    firsts.dirty, follows.dirty = True, True
    while firsts.dirty or follows.dirty:
        firsts.dirty, follows.dirty = False, False
        _firsts_loop(g, firsts, follows)

    return firsts, follows

def _firsts_loop(g, firsts, follows):
    '''
        See caller documentation
    '''

    iteration_keys = list(firsts.data.keys())
    for word in iteration_keys:
        match word:
            case [Terminal() as a, *_]:
                firsts.add(word, [a])

            case [NonTerminal() as A, *_] if g.epsilon not in firsts.get([A]):
                firsts.add(word, firsts.get([A]))

            case [NonTerminal() as A, *rest]:
                AminusE = firsts.get(A) - set([g.epsilon])
                firsts.add(word, AminusE)
                firsts.add(word, firsts.get(rest))

            case [Epsilon() as e]:
                firsts.add(word, set([e]))

            case []:
                pass

            case _:
                raise Exception('Unexpected')

    for nonterminal in g.productions.data:
        for rule in g.productions.data[nonterminal]:
            firsts.add(nonterminal, firsts.get(rule.data))


    for nonterminal in g.productions.data:
        for rule in g.productions.data[nonterminal]:
            for idx, t in enumerate(rule.data):
                if isinstance(t, NonTerminal):
                    firsts.add_empty(rule.data[idx+1:])
                    follows.add(t, firsts.get(rule.data[idx+1:]))

                    if g.epsilon in firsts.get(rule.data[idx+1:]):
                        follows.add(t, follows.get(nonterminal))
                    if len(rule.data[idx+1:]) == 0:
                        follows.add(t, follows.get(nonterminal))

def create_parser_table(g):
    '''
        LL(1) parser table is created as follows:
        T[A,a] contains the rule A → w if and only if
                a is in Fi(w) or
                ε is in Fi(w) and a is in Fo(A).
        (From: https://en.wikipedia.org/wiki/LL_parser)
    '''
    firsts , follows = create_ll_firsts_follows(g)

    parser_table = {}
    for nt in g.nonterminals:
        nonterminal = g.nonterminals[nt]

        for rule in g.productions.data[nonterminal]:

            for t in g.terminals:

                terminal = g.terminals[t]
                if terminal in firsts.get(rule.data) or \
                    (g.epsilon in firsts.get(rule.data) and terminal in follows.get(nonterminal)):

                    if (nonterminal, terminal) in parser_table:
                        parser_table[(nonterminal,terminal)].append(rule)
                    else:
                        parser_table[(nonterminal,terminal)] = [rule]
    return parser_table

class LLParser: 
    def __init__(self, language_buf, start_symbol, epsilon_symbol, eof_symbol):

        self.start = Start(symbol=start_symbol)
        self.epsilon = Epsilon(symbol=epsilon_symbol)
        self.eof = Eof(symbol=eof_symbol)

        self.nonterminals = {start_symbol: self.start}
        self.terminals = {epsilon_symbol: self.epsilon, eof_symbol: self.eof}
        self.productions = ProductionRules()


        self._create_grammar(language_buf)


    def _create_grammar(self, language_buf):

        parser_lines = language_buf.strip().splitlines()
        for p in parser_lines:
            match p.split(':'):
                case nonterminal_str, _:
                    nonterminal_str = nonterminal_str.strip()
                    self.nonterminals[nonterminal_str] = self.nonterminals.get(nonterminal_str, NonTerminal(symbol=nonterminal_str))
                case _:
                    raise Exception('parse: Unable to parse :{}'.format(p))

        for p in parser_lines:
            nonterminal_str, rulestr = p.split(':')
            nonterminal = self.nonterminals[nonterminal_str.strip()]
            rule = ProductionRule()

            for token in rulestr.split():
                if token in self.nonterminals:
                    rule.add(self.nonterminals[token])
                else:
                    self.terminals[token] = self.terminals.get(token, Terminal(symbol=token))
                    rule.add(self.terminals[token])
            self.productions.add(nonterminal, rule)

class TestHelperObjects(unittest.TestCase):

    def test_firstfollow_init(self):

        f = FirstFollowSet()
        self.assertEqual(f.dirty, False)
        self.assertEqual(len(f.data), 0)

    def test_firstfollow_emptyset(self):

        f = FirstFollowSet()
        t = Token(symbol='a')
        f.add_empty(t)
        self.assertEqual(f.dirty, True)
        self.assertEqual(f.get(t), set())

    def test_firstfollow_empty_and_add(self):
        f = FirstFollowSet()
        t = Token(symbol='a')
        f.add_empty(t)

        v = [Terminal('x'), NonTerminal('y')]
        f.add(t, v)

        self.assertEqual(f.get(t), set(v))

    def test_firstfollow_key_compat(self):
        f = FirstFollowSet()
        t = Token(symbol='a')
        v = [Terminal('x'), NonTerminal('y')]
        f.add(t, v)

        self.assertEqual(f.get(t), set(v))
        self.assertEqual(f.get([t]), set(v))
        self.assertEqual(f.get(tuple([t])), set(v))

    def test_firstfollow_multi_add(self):
        f = FirstFollowSet()
        t = Token(symbol='a')
        v1 = [Terminal('x'), NonTerminal('y')]
        v2 = [Terminal('u'), NonTerminal('v')]
        v3 = [Terminal('p'), NonTerminal('v')]

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
        t = Token(symbol='a')
        v_add = [Terminal('x'), NonTerminal('y'), Eof('z')]
        v_remove = [Terminal('x'), NonTerminal('p')]
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
        t1 = Token(symbol='a')
        t2 = Token(symbol='b')
        v1 = [Terminal('x'), NonTerminal('y')]
        v2 = [Terminal('u')]

        f.add(t1, v1)
        f.add(t2, v2)

        self.assertEqual(f.get(t1), set(v1))
        self.assertEqual(f.get(t2), set(v2))

    def test_higher_order_keylen(self):
        f = FirstFollowSet()

        t1 = [NonTerminal('a'), Terminal('b')]
        v1 = [NonTerminal('k'), Epsilon('l'), Eof('z')]
        f.add(t1, v1)
        self.assertEqual(f.get(t1), set(v1))
        self.assertEqual(f.get(tuple(t1)), set(v1))

        # Make sure t1 is ordered, by reversing the elements we should end up with an empty set returned.
        # also a test for empty return
        t2 = list(reversed(t1))
        self.assertEqual(f.get(t2), set())
        self.assertEqual(f.get(tuple(t2)), set())


    def test_dataclasses(self):
        self.assertEqual(Terminal('x'), Terminal('x'))
        self.assertNotEqual(Terminal('x'), NonTerminal('x'))
        self.assertNotEqual(Terminal('x'), Terminal('y'))
        self.assertEqual(set[Terminal('x'), Terminal('y'), NonTerminal('x')], 
                        set[Terminal('x'), Terminal('y'), NonTerminal('x')])
        
class TestParser(unittest.TestCase):

    def parser_table_as_symbols(self, p):
        '''
            returns parser table as string symbols for languages without conflicts
            results[NT,t] = P[0]
        '''
        result = {}
        for (nt,t) in p:
            self.assertEqual(len(p[(nt, t)]), 1)
            result[(str(nt.symbol), str(t.symbol))] = str(p[(nt,t)][0])

        return result

    def test_basic(self):
        language = '''
        S : F
        S : ( S + F )
        F : a 
        '''
    
        g = LLParser(language, 'S', 'ε', '$')
        self.assertEqual(set(g.terminals.keys()), set(['ε', '$', '(', '+', ')', 'a']))
        self.assertEqual(set(g.nonterminals.keys()), set(['F', 'S']))
        self.assertEqual(len(g.productions.data), 2)

        p = create_parser_table(g)
        pr = self.parser_table_as_symbols(p)
        self.assertDictEqual(pr, {('S', 'a'): 'F', ('S', '('): '(S+F)', ('F', 'a'): 'a'} )

    def test_conflict_first_first(self):
        '''
        Test of the language:
        S -> E | E 'a'
        E -> 'b' | ε
        
        When the parser sees 'b' and S is on stack, it does not know whether to apply E or E 'a'.
        '''
        language = '''
        S : E
        S : E a
        E : b
        E : ε
        '''

        g = LLParser(language, 'S', 'ε', '$')
        p = create_parser_table(g)
        self.assertEqual(len(p[(Start('S'), Terminal('b'))]), 2)

    def test_resolve_first_first(self):
        '''
        Resolution of the language:
        S -> E | E 'a'
        E -> 'b' | ε

        is done by 'left factoring'

        S -> b E | E
        E -> a | ε
        
        When the parser sees 'b' and S is on stack, it does not know whether to apply E or E 'a'.
        '''
        language = '''
        S : b E
        S : E
        E : a
        E : ε
        '''

        g = LLParser(language, 'S', 'ε', '$')
        p = create_parser_table(g)
        self.assertIsNotNone(p)
        pr = self.parser_table_as_symbols(p)
        self.assertDictEqual(pr, {('S', 'b'): 'bE', ('S', 'ε'): 'E', ('S', '$'): 'E', ('S', 'a'): 'E', ('E', 'a'): 'a', ('E', 'ε') : 'ε', ('E', '$'): 'ε'})

    def test_left_left_recursion(self):
        '''
        Test of the language:
        E -> E '+' term | alt1 | alt2

        When the parser sees alt1, it does not know whether to apply E->alt1 or E + term 

        '''
        language = '''
        S : E
        E : E + a
        E : b
        E : c
        '''
        g = LLParser(language, 'S', 'ε', '$')
        p = create_parser_table(g)
        self.assertEqual(len(p[(NonTerminal('E'), Terminal('b'))]), 2)
        self.assertEqual(len(p[(NonTerminal('E'), Terminal('c'))]), 2)

    def test_resolve_left_left_recursion(self):
        '''
        https://en.wikipedia.org/wiki/Left_recursion#Removing_left_recursion

        Below 
            E -> E '+' T
            E -> T

        is resolved by 
        E -> T Z
        Z -> '+' T Z
        Z -> ε

        '''
        language = '''
        S : E
        E : T Z
        Z : + a
        T : b
        T : c
        Z : ε
        '''
        g = LLParser(language, 'S', 'ε', '$')
        p = create_parser_table(g)
        pr = self.parser_table_as_symbols(p)
        print(pr)
        self.assertDictEqual(pr, 
                {('S', 'b'): 'E', ('S', 'c'): 'E', ('E', 'b'): 'TZ', ('E', 'c'): 'TZ', ('Z', '+'): '+a', ('Z', 'ε'): 'ε', ('Z', '$'): 'ε', ('T', 'b'): 'b', ('T', 'c'): 'c'})

    def test_first_follow_conflict(self):
        '''
        Test of the language:
        S -> A 'a' 'b'
        A -> 'a' | ε
        
        '''

        language = '''
        S : A a b 
        A : a
        A : ε
        '''
        g = LLParser(language, 'S', 'ε', '$')
        (firsts, follows) = create_ll_firsts_follows(g)
        p = create_parser_table(g)
        self.assertEqual(len(p[(NonTerminal('A'), Terminal('a'))]), 2)

if __name__ == '__main__':
    unittest.main()
