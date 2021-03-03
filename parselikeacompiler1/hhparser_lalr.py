from lark import Lark, Transformer
hh_parser = Lark(r'''
    handhistories : handhistory*
    handhistory: handdesc datetimewhen table seats posts preflop [flop] [turn] [river] [boards] summary winner [shows]
    datetimewhen: when _NL
    handdesc: "#" NUMBER ":" words "-" words "/" words _NL
    table: "Table '" words "' Seat " seatnum " is the button" _NL
    seats: [seat*]
    seat: "Seat " seatnum ": " player " (" stack ")" _NL
    posts: [(post|straddle)*]
    post: player ": posts " words _NL
    straddle: player ": straddles " words _NL
    preflop: "*** HOLE CARDS ***" _NL deals actions
    deals: [deal*]
    deal: "Dealt to " words ": [" words "]" _NL
    actions: [(fold|raise|call|check|bets|showdown)*]
    fold: player " folds" _NL
    raise: player " raises to " stack [andisallin] _NL
    bets: player " bets " stack [andisallin] _NL
    call: player " calls " stack [andisallin] _NL
    check: player " checks" _NL
    andisallin: " and is all in"
    showdown: player " shows [" words "]" _NL
    flop: "*** FLOP *** [" words "]" _NL actions
    turn: "*** TURN *** [" words "] [" words "]" _NL actions
    river: "*** RIVER *** [" words "] [" words "]" _NL actions
    summary: "*** SUMMARY ***" _NL playersummary+
    playersummary: "Seat " seatnum ": " words "(" stack ")" [(" +"|" -") stack] _NL
    winner: normalwinner | splitpotwinner*
    normalwinner: player " wins pot (" stack ")" _NL
    splitpotwinner: player " wins (" stack ")" [fromwhere] _NL
    boards: board*
    board: "*** BOARD " boardnum " - RIVER *** [" boardlayout "] [" words "]" _NL
    fromwhere: " from " words
    shows: showdown+

    player: foo|bar|foobar|mrfoo
    foo : /foo/
    bar : /bar/
    foobar : /foobar/
    mrfoo : /Mr Foo/
    words: /[\w ]+/
    stakes: /[\w]+/
    when: /[\d\-: ]+/
    seatnum: /\d/
    boardnum: /\d/
    boardlayout : /[\w  \-]+/
    stack :/\d[\d,\.]*/
    %import common.WS
    %import common.NUMBER
    %import common.NEWLINE -> _NL
    %import common.WORD

''', start='handhistories', parser='lalr')

with open('sample.txt', 'r') as file:
    data = file.read()
tree = hh_parser.parse(data)
print(tree.pretty())
