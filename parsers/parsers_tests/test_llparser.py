from lib2to3.pgen2 import token
import unittest
from parsers import tokenizer, GrammarTerminal, Start, NonTerminal, Rule, Alternate, Eof
from parsers.elements import Epsilon, Grammar
from parsers.llparser import LLParser

class TestLLParser(unittest.TestCase):
    def parser_table_as_symbols(self, p):
        '''
            returns parser table as string symbols for languages without conflicts
            results[NT,t] = P[0]
        '''
        result = {}
        for (nt,t) in p:
            self.assertEqual(len(p[(nt, t)]), 1)
            result[(str(nt), str(t))] = str(p[(nt,t)][0])

        return result

    @staticmethod
    def create_grammar(language_buf, epsilon=None):
        '''
            Test utility to create a grammar
            $ is reserved
            Parses NT: singrule[\n|eof]*
            singlerule = NT or t where t is everything not recognized as NT
        '''

        parser_lines = language_buf.strip().splitlines()

        nonterminals = {}
        start = None
        for p in parser_lines:
            match p.split(':'):
                case nonterminal_str, _:
                    nonterminal_str = nonterminal_str.strip()
                    if start is None:
                        start = Start(symbol=nonterminal_str)
                        nonterminals[nonterminal_str] = start
                    else:
                        nonterminals[nonterminal_str] = \
                            nonterminals.get(nonterminal_str,
                                NonTerminal(symbol=nonterminal_str))
                case _:
                    raise Exception('parse: Unable to parse :{}'.format(p))

        # TODO: do one pass for collecting terminals as well as
        # generating rules
        terminals = {epsilon: Epsilon(epsilon)} if epsilon else {}

        for p in parser_lines:
            _, rulestr = p.split(':')
            for token in rulestr.split():
                if token not in nonterminals and token != start.symbol:
                    terminals[token] = terminals.get(token,
                                        GrammarTerminal(symbol=token,
                                                        val=token))

        symbol_db = { start.symbol:start }
        symbol_db.update(nonterminals)
        symbol_db.update(terminals)

        rules = {}

        for p in parser_lines:
            nonterminal_str, rulestr = p.split(':')
            nonterminal_sym = nonterminals[nonterminal_str.strip()]
            altdata = []
            for token in rulestr.split():
                altdata.append(symbol_db[token])
            # this is guarenteed to be nonterminal or start
            if nonterminal_sym not in rules:
                rules[nonterminal_sym] = Rule(alts=[], ident = nonterminal_sym)
            rules[nonterminal_sym].alts.append(Alternate(altdata))

        data = {}
        for k in nonterminals:
            data[nonterminals[k]] = rules[nonterminals[k]]

        return Grammar(
                set(terminals.values()),
                data,
                start,
                Eof('$'),
                terminals.get(epsilon)
        )

    def test_basic_without_parsing(self):
        '''
            This test is same as test_basic except the test
            does not parse the bnf
            Test for the following language
            S : F
            S : ( S + F )
            F : a
        '''
        a = GrammarTerminal('a', 'a')
        leftparan = GrammarTerminal('(', '(')
        rightparan = GrammarTerminal(')', ')')
        plus = GrammarTerminal('+', '+')
        S = Start('S')
        F = NonTerminal('F')
        data = {
                S: Rule(alts=
                    [
                        Alternate([F]),
                        Alternate([leftparan,S,plus,F,rightparan])
                    ],
                    ident = S),
                F: Rule(alts=[Alternate([a])], ident=F)
                }
        terminals = set([a,leftparan,rightparan,plus])

        grammar = Grammar(
                terminals,
                data,
                S,
                Eof(None),
                None
        )
        llparser = LLParser(grammar)
        pr = self.parser_table_as_symbols(llparser._parser_table)
        self.assertDictEqual(pr, {('S', 'a'): 'F',
                                  ('S', '('): '(S+F)',
                                  ('F', 'a'): 'a'} )

    def test_basic1(self):
        '''
            Test for the following language
            S : F
            S : ( S + F )
            F : a
        '''
        language = '''
        S : F
        S : ( S + F )
        F : a
        '''
        grammar = TestLLParser.create_grammar(language_buf=language)
        llparser = LLParser(grammar)
        pr = self.parser_table_as_symbols(llparser._parser_table)
        self.assertDictEqual(pr, {('S', 'a'): 'F',
                                  ('S', '('): '(S+F)',
                                  ('F', 'a'): 'a'} )

    def test_conflict_first_first(self):
        '''
        Test of the language:
        S -> E | E 'a'
        E -> 'b' | ε

        When the parser sees 'b' and S is on stack,
        it does not know whether to apply E or E 'a'.
        '''
        language = '''
        S : E
        S : E a
        E : b
        E : e
        '''

        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        p = llparser._parser_table
        self.assertEqual(len(p[(Start('S'), GrammarTerminal('b','b'))]), 2)

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
        E : e
        '''

        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        pr = self.parser_table_as_symbols(llparser._parser_table)
        self.assertDictEqual(pr, {('S', 'b'): 'bE',
                                  ('S', 'e'): 'E',
                                  ('S', '$'): 'E',
                                  ('S', 'a'): 'E',
                                  ('E', 'a'): 'a',
                                  ('E', 'e') : 'e',
                                  ('E', '$'): 'e'})

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
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        p = llparser._parser_table
        self.assertEqual(len(p[(NonTerminal('E'),
                             GrammarTerminal('b','b'))]), 2)
        self.assertEqual(len(p[(NonTerminal('E'),
                                GrammarTerminal('c','c'))]), 2)

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
        Z : e
        '''
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        pr = self.parser_table_as_symbols(llparser._parser_table)
        self.assertDictEqual(pr, {('S', 'b'): 'E',
                                  ('S', 'c'): 'E',
                                  ('E', 'b'): 'TZ',
                                  ('E', 'c'): 'TZ',
                                  ('Z', '+'): '+a',
                                  ('Z', 'e'): 'e',
                                  ('Z', '$'): 'e',
                                  ('T', 'b'): 'b',
                                  ('T', 'c'): 'c'})

    def test_first_follow_conflict(self):
        '''
        Test of the language:
        S -> A 'a' 'b'
        A -> 'a' | ε

        '''

        language = '''
        S : A a b
        A : a
        A : e
        '''
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        p = llparser._parser_table
        self.assertEqual(len(p[(NonTerminal('A'), GrammarTerminal('a','a'))]), 2)

    def test_basic_derivation(self):
        '''
            Test derivation for
            S => F | ( S + F )
            F => a
        '''
        language = '''
            S : F
            S : ( S + F )
            F : a
        '''
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        llparser.parse(list(tokenizer(iter('( a + a )'))))
        llparser.parse(list(tokenizer(iter('( ( a +  a ) + a )'))))
        #TODO : Test using ASTs
        self.assertEqual(1, 1)

    def test_basic_derivation_with_epslion(self):
        '''
            Test derivation for
            S -> b E | E
            E -> a | ε
        '''
        language = '''
        S : b E
        S : E
        E : a
        E : e
        '''
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        llparser.parse(list(tokenizer(iter('b'))))
        self.assertEqual(1, 1)

    def test_dangingling_else(self):
        '''
            S -> iEtSS'| a
            S' -> eS | epsilon
            E -> b
        '''
        language = '''
        Statement : if E then Statement EStatement
        Statement : a
        EStatement : else Statement
        EStatement : e
        E : b
        '''
        grammar = TestLLParser.create_grammar(language_buf=language,
                                            epsilon='e')
        llparser = LLParser(grammar)
        p = llparser._parser_table
        self.assertEqual(len(p[(NonTerminal('EStatement'), GrammarTerminal('else','else'))]), 2)