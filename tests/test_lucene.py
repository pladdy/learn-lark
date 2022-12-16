import pytest

from learn_lark import lucene

test_parser = lucene.parser()


def rebuild_phrase(single_terms):
    return '"' + " ".join(single_terms) + '"'


def rebuild_single_term(children):
    return "".join([child.value for child in children])


@pytest.mark.parametrize(
    "query",
    [
        ['NOT"a phrase" AND singleTerm OR elephants'],
        ['"a phrase" AND AND singleTerm OR elephants'],
        ['"a phrase" ++ singleTerm OR elephants'],
        ['*ext "a phrase" AND singleTerm OR elephants'],
        ['?ext "a phrase" AND singleTerm OR elephants'],
    ],
)
def test_parser_exceptions(query):
    with pytest.raises(Exception):
        test_parser.parse(query)


@pytest.mark.parametrize(
    "query, expected_fields",
    [
        ['text:"a phrase"', ["text:"]],
        ['text:"a phrase" AND singleTerm', ["text:"]],
        ['text:"a phrase" AND body:singleTerm', ["text:", "body:"]],
        ["text:(!big +small)", ["text:"]],
        ["text:(!big +small) OR body:(+strong -weak)", ["text:", "body:"]],
        [
            "text:(!big +small AND NOT 'a phrase') OR body:(+strong -weak)",
            ["text:", "body:"],
        ],
    ],
)
def test_parser_fields(query, expected_fields):
    parsed = test_parser.parse(query)
    found_fields = parsed.find_data("field")

    fields = []
    for field in found_fields:
        fields.append(field.children[0].strip())

    assert expected_fields == fields, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_fuzz",
    [
        ["lucene query~ syntax", [""]],
        ["pink~1 elephants~0.23 rock", ["1", "0.23"]],
    ],
)
def test_parser_fuzzy_term(query, expected_fuzz):
    parsed = test_parser.parse(query)
    parsed_fuzzy_terms = parsed.find_data("fuzzy_term")

    fuzzes = []
    for parsed_fuzzy_term in parsed_fuzzy_terms:
        fuzz = "".join(parsed_fuzzy_term.children[1:])
        if fuzz:
            fuzz = fuzz.replace("~", "")
        fuzzes.append(fuzz)

    assert expected_fuzz == fuzzes, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_operators",
    [
        ['"a phrase" AND singleTerm', ["AND"]],
        ['"a phrase" AND singleTerm OR elephants', ["AND", "OR"]],
        ['NOT "a phrase" AND singleTerm OR elephants', ["NOT", "AND", "OR"]],
        [
            'NOT   "a phrase"  AND  singleTerm   OR    elephants ',
            ["NOT", "AND", "OR"],
        ],
        [
            '-"a phrase" AND singleTerm && elephants || tigers',
            ["-", "AND", "&&", "||"],
        ],
        [
            '! "a phrase" && singleTerm OR elephants || tigers',
            ["!", "&&", "OR", "||"],
        ],
        [
            '-"a phrase" +singleTerm OR elephants || tigers',
            ["-", "+", "OR", "||"],
        ],
    ],
)
def test_parser_operator(query, expected_operators):
    parsed = test_parser.parse(query)
    found_operators = list(parsed.find_data("leading_operator")) + list(
        parsed.find_data("operator")
    )

    operators = []
    for operator in found_operators:
        operators.append(operator.children[0].strip())

    assert expected_operators == operators, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_phrases",
    [
        ['"a phrase" for search', ['"a phrase"']],
        [
            '"a phrase" for search "with another phrase"',
            ['"a phrase"', '"with another phrase"'],
        ],
    ],
)
def test_parser_phrase(query, expected_phrases):
    parsed = test_parser.parse(query)
    parsed_phrases = parsed.find_data("phrase")

    phrases = []
    for parsed_phrase in parsed_phrases:
        parsed_single_terms = parsed_phrase.find_data("single_term")

        single_terms = []
        for parsed_single_term in parsed_single_terms:
            single_terms.append(
                rebuild_single_term(parsed_single_term.children)
            )
        phrases.append(rebuild_phrase(single_terms))

    assert expected_phrases == phrases, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_boosts",
    [
        ['"a phrase"^2 for search', ["2"]],
        [
            '"a phrase"^2 for search "with another phrase"^1.5',
            ["2", "1.5"],
        ],
    ],
)
def test_parser_phrase_boost(query, expected_boosts):
    parsed = test_parser.parse(query)
    parsed_terms = parsed.find_data("term")

    boosts = []
    for parsed_term in parsed_terms:
        for parsed_boost in parsed_term.find_data("boost"):
            boost = "".join(parsed_boost.children)
            if boost:
                boost = boost.replace("^", "")
            boosts.append(boost)

    assert expected_boosts == boosts, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_proximity",
    [
        ['"lucene query"~2', ["2"]],
        ['"lucene query"~2 AND "elphants rock"~5', ["2", "5"]],
    ],
)
def test_parser_proximity(query, expected_proximity):
    parsed = test_parser.parse(query)
    parsed_fuzzy_terms = parsed.find_data("proximity")

    proximities = []
    for parsed_fuzzy_term in parsed_fuzzy_terms:
        proximity = "".join(parsed_fuzzy_term.children[1:])
        proximity = proximity.replace("~", "")
        if proximity:
            proximities.append(proximity)

    assert expected_proximity == proximities, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_terms",
    [
        ["lucene query syntax", ["lucene", "query", "syntax"]],
        ["pink elephants rock", ["pink", "elephants", "rock"]],
    ],
)
def test_parser_single_term(query, expected_terms):
    parsed = test_parser.parse(query)
    parsed_single_terms = parsed.find_data("single_term")

    single_terms = []
    for parsed_single_term in parsed_single_terms:
        single_terms.append(rebuild_single_term(parsed_single_term.children))

    assert expected_terms == single_terms, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_boosts",
    [
        ["elephants^2 for search", ["2"]],
        [
            "purple^2 for search tomcat^1.5",
            ["2", "1.5"],
        ],
    ],
)
def test_parser_single_term_boost(query, expected_boosts):
    parsed = test_parser.parse(query)
    parsed_terms = parsed.find_data("term")

    boosts = []
    for parsed_term in parsed_terms:
        for parsed_boost in parsed_term.find_data("boost"):
            boost = "".join(parsed_boost.children)
            boost = boost.replace("^", "")
            if boost:
                boosts.append(boost)

    assert expected_boosts == boosts, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_ranges",
    [
        ["some_field:[100 TO 1000]", ["[100 TO 1000]"]],
        [
            "some_field:[100 TO 1000] AND other_field:{Aida TO Ravioli}",
            ["[100 TO 1000]", "{Aida TO Ravioli}"],
        ],
    ],
)
def test_parser_range(query, expected_ranges):
    parsed = test_parser.parse(query)
    parsed_terms = parsed.find_data("field")

    ranges = []
    for parsed_term in parsed_terms:
        for parsed_range in parsed_term.find_data("range"):
            _range = "".join(parsed_range.children)
            if _range:
                ranges.append(_range)

    assert expected_ranges == ranges, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_subqueries",
    [
        ["lucene (query syntax)", ["query syntax"]],
        ["(lucene query) syntax", ["lucene query"]],
    ],
)
def test_parser_subquery(query, expected_subqueries):
    parsed = test_parser.parse(query)
    parsed_subqueries = parsed.find_data("subquery")

    subqueries = []
    for parsed_subquery in parsed_subqueries:
        terms = []
        for parsed_single_term in parsed_subquery.find_data("single_term"):
            terms.append(rebuild_single_term(parsed_single_term.children))
        subqueries.append(" ".join(terms))

    assert expected_subqueries == subqueries, parsed.pretty()


@pytest.mark.parametrize(
    "query, expected_wildcards",
    [
        ["lucen? query syntax*", ["?", "*"]],
        ["(lucen?) (query syntax*)", ["?", "*"]],
    ],
)
def test_parser_wildcard(query, expected_wildcards):
    parsed = test_parser.parse(query)
    parsed_single_terms = parsed.find_data("single_term")

    wild_cards = []
    for parsed_single_term in parsed_single_terms:
        term = rebuild_single_term(parsed_single_term.children)
        if "*" in term:
            wild_cards.append("*")
        if "?" in term:
            wild_cards.append("?")

    assert expected_wildcards == wild_cards, parsed.pretty()


@pytest.mark.parametrize(
    "query",
    [
        "this \\? is a special char",
        "\\* \\&& \\? are special chars",
    ],
)
def test_parser_special_chars(query):
    _ = test_parser.parse(query)
    # TODO: should special chars be labeled so they can be found/tested?
