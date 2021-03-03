from lark import Lark
cfg = r'''
    list: "[" listelem ("," listelem)* "]"
    listelem: list|WORD

    %import common.WS
    %ignore WS
    %import common.WORD
'''

list_parser = Lark(cfg, start='list')
print(list_parser.parse('[test, me, [I, am, nested, [no, kidding]]]').pretty())
