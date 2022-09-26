from kegg2svg import D3Scale


def test_simple():
    d = D3Scale(domain=(0, 10), range=(0, 10))
    assert d.map(4) == 4


def test_simple_reverse_domain():
    d = D3Scale(domain=(10, 0), range=(0, 10))
    assert d.map(2) == 8


def test_simple_reverse_range():
    d = D3Scale(domain=(0, 10), range=(10, 0))
    assert d.map(4) == 6


def test_simple_shifted():
    d = D3Scale(domain=(10, 20), range=(0, 10))
    assert d.map(14) == 4


def test_simple_shifted_reverse_domain():
    d = D3Scale(domain=(20, 10), range=(0, 10))
    assert d.map(14) == 6


def test_simple_shifted_reverse_range():
    d = D3Scale(domain=(10, 20), range=(10, 0))
    assert d.map(14) == 6


def test_simple_shifted_reverse_both():
    d = D3Scale(domain=(20, 10), range=(10, 0))
    assert d.map(14) == 4


def test_outside_domain_1():
    d = D3Scale(domain=(0, 10), range=(0, 10))
    assert d.map(11) == 10


def test_outside_domain_1():
    d = D3Scale(domain=(0, 10), range=(0, 10))
    assert d.map(-1) == 0
