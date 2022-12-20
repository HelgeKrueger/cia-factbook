from converters import to_number


def test_with_million():
    assert to_number("248.265 million ") == 248265000


def test_with_billion():
    assert to_number("66.931 billion ") == 66931000000


def test_handling_commas():
    assert to_number("500,350,034,000 ") == 500350034000
