import lark


class TreeToJson(lark.Transformer):
    def string(self, s):
        # print(f"string is {s}")
        return s[0][1:-1]
        # (s,) = s
        # return s[1:-1]

    def number(self, n):
        #  print(n)
        return float(n[0])

    dict = dict
    list = list
    pair = tuple

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False


def parser():
    return lark.Lark(
        open("learn_lark/json.lark").read(),
        start="value",
        lexer="basic",
        parser="lalr",
    )
