import learn_lark.json as ll_json

text = '{"key": ["item0", "item1", 3.14]}'
tree = ll_json.parser().parse(text)


class TestTreeToJson:
    def test_parser(self):
        result = ll_json.TreeToJson().transform(tree)
        assert result == {"key": ["item0", "item1", 3.14]}


def test_parser():
    assert (
        tree.pretty() == 'dict\n  pair\n    string\t"key"\n    list\n'
        '      string\t"item0"\n      string\t"item1"\n      number\t3.14\n'
    )
