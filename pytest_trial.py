def test_addition():
    assert 2 + 2 == 4  # Passes
    assert 2 + 2 == 5  # Fails

def test_boolean():
    assert True  # Passes
    assert False  # Fails

def test_membership():
    assert 'a' in 'apple'  # Passes
    assert 'z' in 'apple'  # Fails

def test_comparison():
    assert 5 > 3  # Passes
    assert 3 > 5  # Fails

def test_custom_message():
    assert 2 + 2 == 5, "Math is broken!"  # Fails with custom message


def test_example1():
    assert 2 + 2 == 4
    
    
def test_example2():
    assert 2 + 2 == 5