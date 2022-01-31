'''
    Module llparser contains the llparser class
'''

from typing import Optional

from .elements import Alternate, Eof, Grammar, GrammarTerminal, GrammarToken, NonTerminal, Epsilon
from .ll_ff import FirstFollowSet
from .stack import Stack
from .tokenizer import TokenType, Token

ParserStackElement = NonTerminal|Epsilon|Eof
ParserTableType =  dict[tuple[ParserStackElement, GrammarToken], list[Alternate]]

class TokenReader: # pylint: disable=too-few-public-methods
    '''
        TokenReader class wraps an iterator
    '''
    def __init__(self, tokenlist: list[Token]):
        self._itr = iter(tokenlist)

    def nexttoken(self) -> Optional[Token]:
        '''
            retrieve next value from _itr or None for end
            gobbles up spaces
        '''
        try:
            nextelem = next(self._itr)
            if nextelem.tokentype == TokenType.SPACE:
                return self.nexttoken()
            return nextelem
        except StopIteration:
            return None

class LLParser:
    '''
        LLParser class.
        g -> Grammar
    '''
    def __init__(self, grammar: Grammar):
        self._grammar = grammar
        self._setup_llparser()

    def parse(self, tokenlist: list[Token]):
        '''
            parses a stream of tokens using LL(1)
        '''

        stack: Stack[GrammarToken] = Stack()
        tokens = TokenReader(tokenlist)

        stack.push(self._grammar.endmarker)
        stack.push(self._grammar.start)
        e = tokens.nexttoken() # pylint: disable=invalid-name

        # the static typechecker is unable to catch e != none here
        # so we have to ignore some type errors below
        while e is not None and len(stack) != 0:
            eterminal: GrammarToken
            if e.tokentype == TokenType.EOF: # type: ignore
                eterminal = self._grammar.endmarker
            else:
                eterminal = GrammarTerminal(e.value, e.value) # type: ignore

            if isinstance(stack.peek(), GrammarTerminal) and \
                    stack.peek().symbol == e.value: # type: ignore
                stack.pop()
                e = tokens.nexttoken() # pylint: disable=invalid-name
            elif isinstance(stack.peek(), Epsilon):
                stack.pop()
            elif isinstance(stack.peek(), NonTerminal) and \
                    (stack.peek(), eterminal) in self._parser_table:
                nonterminal: NonTerminal = stack.pop() # type: ignore
                production_rule = self._parser_table[(nonterminal, eterminal)][0].data
                for x in reversed(production_rule): # pylint: disable=invalid-name
                    stack.push(x)
            elif isinstance(stack.peek(), Eof) and \
                    e.tokentype == TokenType.EOF: # type: ignore
                stack.pop()
                e = tokens.nexttoken() # pylint: disable=invalid-name
            else:
                raise Exception(f'Unable to parse e={e}, stack={stack}')

        if e is None and len(stack) == 0:
            return

        # this is likely unreachable. Test the conditions
        raise Exception(f'Potentially Unreachable to parse e={e}, stack={stack}')

    def _generate_parser_table(self) -> ParserTableType:
        '''
            LL(1) parser table is created as follows:
            T[A,a] contains the rule A → w if and only if
                    a is in Fi(w) or
                    ε is in Fi(w) and a is in Fo(A).
            (From: https://en.wikipedia.org/wiki/LL_parser)
        '''
        firsts , follows = self._firsts, self._follows

        parser_table : ParserTableType = {}
        for nonterminal in self._grammar.data:
            for alt in self._grammar.data[nonterminal].alts:
                for terminal in self._grammar.terminals.union([self._grammar.endmarker]):
                    if terminal in firsts.get(alt.data) or \
                        (self._grammar.epsilon in firsts.get(alt.data) \
                         and terminal in follows.get(nonterminal)):


                        if (nonterminal, terminal) in parser_table:
                            parser_table[(nonterminal,terminal)].append(alt)
                        else:
                            parser_table[(nonterminal,terminal)] = [alt]
        return parser_table

    def _setup_llparser(self):

        r'''
            Function that creates the firsts,  follows and parsing table
            Is called by constructor.


            _create_firsts_follows initializes firsts and follows set,
                and keeps applying update rules via _firsts_loop till there is
                more first and follow

            This is an implementation of algorithm :
                https://en.wikipedia.org/wiki/LL_parser

            Fi, Fo = First, Follow sets

            Fi(w), as the set of terminals that can be found at the start of
            some string in w, plus ε if the empty string also belongs to w.

            Fo(A) is a set of terminals {a} such that a string w'Aaw'' can be
            derived from S as the start symbol.

            1 For every Ai -> Wi
                1. initialize every Fi(Ai) and Fi(Wi) with the empty set
                2. initialize Fo(S) with EOF ($)

            while Fi and Fo dont change
                2. For each element in Fi
                    1. Fi(aw') = { a } for every terminal a
                    2. Fi(Aw') = Fi(A) for every nonterminal A
                        with ε not in Fi(A)
                    3. Fi(Aw') = (Fi(A) \ { ε }) ∪ Fi(w' )
                        for every nonterminal A with ε in Fi(A)
                    4. Fi(ε) = { ε }
                3. For every Ai -> Wi:
                    1. add Fi(wi) to Fi(Ai)
                4. For every Aj → wAiw'
                    1. if the terminal a is in Fi(w' ), then add a to Fo(Ai)
                    2. if ε is in Fi(w' ), then add Fo(Aj) to Fo(Ai)
                    3. if w' has length 0, then add Fo(Aj) to Fo(Ai)

            A Context Free Grammar (CFG) is made up of Start Element S,
            Production Rules Ai->Wi, a set of terminal characters,
            a set of non-terminal characters.
            The character epslion is an empty rule.


            For a language Ai->Wi
            Fi(w) = set(a,b,c) => the elements of Fi(w) are terminals that

        '''

        firsts, follows = FirstFollowSet(), FirstFollowSet()

        for nonterminal in self._grammar.data:
            firsts.add_empty([nonterminal])
            for rule in self._grammar.data[nonterminal].alts:
                firsts.add_empty(rule.data)

        follows.add(self._grammar.start, self._grammar.endmarker)

        firsts.dirty, follows.dirty = True, True
        while firsts.dirty or follows.dirty:
            firsts.dirty, follows.dirty = False, False
            LLParser._firsts_loop(self._grammar, firsts, follows)

        self._firsts, self._follows = firsts, follows
        self._parser_table = self._generate_parser_table()

    @staticmethod
    def _firsts_loop(grammar: Grammar, # pylint: disable=too-many-branches
                    firsts: FirstFollowSet,
                    follows: FirstFollowSet):
        '''
            See caller documentation
        '''

        iteration_keys = list(firsts.data.keys())
        for word in iteration_keys:
            if len(word) == 0:
                continue
            A = word[0] # pylint: disable=invalid-name

            if isinstance(A, GrammarTerminal):
                firsts.add(word, [A])
            elif isinstance(A, NonTerminal):
                if grammar.epsilon not in firsts.get([A]):
                    firsts.add(word, firsts.get([A]))
                else:
                    rest = word[1:]
                    AminusE = firsts.get(A) - set([grammar.epsilon]) # pylint: disable=invalid-name
                    firsts.add(word, AminusE)
                    firsts.add(word, firsts.get(rest))
            elif isinstance(A, Epsilon) and len(word) == 1:
                firsts.add(word, set([A]))
            else:
                raise Exception('Unexpected')

        for nonterminal in grammar.data:
            for rule in grammar.data[nonterminal].alts:
                firsts.add(nonterminal, firsts.get(rule.data))


        for nonterminal in grammar.data:
            for rule in grammar.data[nonterminal].alts:
                for idx, grammartoken in enumerate(rule.data):
                    if isinstance(grammartoken, NonTerminal):
                        firsts.add_empty(rule.data[idx+1:])
                        follows.add(grammartoken, firsts.get(rule.data[idx+1:]))

                        if grammar.epsilon in firsts.get(rule.data[idx+1:]):
                            follows.add(grammartoken, follows.get(nonterminal))
                        if len(rule.data[idx+1:]) == 0:
                            follows.add(grammartoken, follows.get(nonterminal))
