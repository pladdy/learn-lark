import lark


def parser():
    return lark.Lark(
        open("learn_lark/lucene.lark"),
        start="query",
        parser="lalr",
    )
