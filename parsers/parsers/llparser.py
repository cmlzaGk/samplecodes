'''
    Module llparser contains the llparser class
'''

from .elements import Eof, Grammar, GrammarTerminal, NonTerminal, Epsilon
from .ll_ff import FirstFollowSet
from .stack import Stack
from .tokenizer import TokenType, Token

class TokenReader:
    def __init__(self, tokenlist:list[Token]):
        self._itr = iter(tokenlist)

    def next(self):
        try:
            n = next(self._itr)
            if n.tokentype == TokenType.SPACE:
                return self.next()
            return n
        except StopIteration:
            return None

class LLParser:
    '''
        LLParser class.
        g -> Grammar
    '''
    def __init__(self, grammar: Grammar):
        self._grammar = grammar
        self._parser_table = LLParser.create_parser_table(grammar)

    def parse(self, tokenlist: list[Token]):

        stack = Stack()
        tokens = TokenReader(tokenlist)

        stack.push(self._grammar.endmarker)
        stack.push(self._grammar.start)
        e = tokens.next()
        while e != None and len(stack) != 0:
            if isinstance(stack.peek(), GrammarTerminal):
                if stack.peek().symbol == e.value:
                    stack.pop()
                    e = tokens.next()
                else:
                    raise Exception(f'Unable to parse e={e}, stack={stack}')

            elif isinstance(stack.peek(), Epsilon):
                stack.pop()
            elif isinstance(stack.peek(), NonTerminal):
                if e.tokentype == TokenType.EOF:
                    eterminal = self._grammar.endmarker
                else:
                    eterminal = GrammarTerminal(e.value, e.value)
                if (stack.peek(), eterminal) in self._parser_table:
                    nt = stack.pop()
                    production_rule = self._parser_table[(nt, eterminal)][0].data
                    for x in reversed(production_rule):
                        stack.push(x)
                else:
                    raise Exception(f'Unable to parse e={e}, stack={stack}')

            elif isinstance(stack.peek(), Eof):
                if e.tokentype == TokenType.EOF:
                    stack.pop()
                    e = tokens.next()
            else:
                    raise Exception(f'Unable to parse e={e}, stack={stack}')
        if e == None and len(stack) == 0:
            return

        # this is likely unreachable. Test the conditions
        raise Exception(f'Potentially Unreachable to parse e={e}, stack={stack}')

    @staticmethod
    def create_parser_table(grammar: Grammar):
        '''
            LL(1) parser table is created as follows:
            T[A,a] contains the rule A → w if and only if
                    a is in Fi(w) or
                    ε is in Fi(w) and a is in Fo(A).
            (From: https://en.wikipedia.org/wiki/LL_parser)
        '''
        firsts , follows = LLParser.create_ll_firsts_follows(grammar)

        parser_table = {}
        for nonterminal in grammar.data:
            for alt in grammar.data[nonterminal].alts:
                for terminal in grammar.terminals.union([grammar.endmarker]):
                    if terminal in firsts.get(alt.data) or \
                        (grammar.epsilon in firsts.get(alt.data) \
                         and terminal in follows.get(nonterminal)):


                        if (nonterminal, terminal) in parser_table:
                            parser_table[(nonterminal,terminal)].append(alt)
                        else:
                            parser_table[(nonterminal,terminal)] = [alt]
        return parser_table

    @staticmethod
    def create_ll_firsts_follows(grammar:Grammar):

        r'''
            Function that creates the firsts and follows.
            Is called by constructor.

            _create_firsts_follows initializes firsts and follows set,
                and keeps applying update rules via _firsts_loop till there is
                more first and follow

            This is an implementation of algorithm :
                https://en.wikipedia.org/wiki/LL_parser

            Fi, Fo = First, Follow sets

            Fi(W) is a set of terminals that are the first terminals of all
            derivations of W where W is made up of NonTerminal and Terminals.
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

        for nonterminal in grammar.data:
            firsts.add_empty([nonterminal])
            for rule in grammar.data[nonterminal].alts:
                firsts.add_empty(rule.data)

        follows.add(grammar.start, grammar.endmarker)

        firsts.dirty, follows.dirty = True, True
        while firsts.dirty or follows.dirty:
            firsts.dirty, follows.dirty = False, False
            LLParser._firsts_loop(grammar, firsts, follows)

        return firsts, follows

    @staticmethod
    def _firsts_loop(grammar: Grammar,
                    firsts: FirstFollowSet,
                    follows: FirstFollowSet):
        '''
            See caller documentation
        '''

        iteration_keys = list(firsts.data.keys())
        for word in iteration_keys:
            match word:
                case [GrammarTerminal() as a, *_]:
                    firsts.add(word, [a])

                case [NonTerminal() as A, *_] if \
                        grammar.epsilon not in firsts.get([A]):
                    firsts.add(word, firsts.get([A]))

                case [NonTerminal() as A, *rest]:
                    AminusE = firsts.get(A) - set([grammar.epsilon])
                    firsts.add(word, AminusE)
                    firsts.add(word, firsts.get(rest))

                case [Epsilon() as e]:
                    firsts.add(word, set([e]))

                case []:
                    pass

                case _:
                    raise Exception('Unexpected')

        for nonterminal in grammar.data:
            for rule in grammar.data[nonterminal].alts:
                firsts.add(nonterminal, firsts.get(rule.data))


        for nonterminal in grammar.data:
            for rule in grammar.data[nonterminal].alts:
                for idx, t in enumerate(rule.data):
                    if isinstance(t, NonTerminal):
                        firsts.add_empty(rule.data[idx+1:])
                        follows.add(t, firsts.get(rule.data[idx+1:]))

                        if grammar.epsilon in firsts.get(rule.data[idx+1:]):
                            follows.add(t, follows.get(nonterminal))
                        if len(rule.data[idx+1:]) == 0:
                            follows.add(t, follows.get(nonterminal))
