# encoding=utf8
# The endpoint test

"""The endpoing test
"""

import sys
import os.path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

def test_endpoint():
    """The endpoint
    """
    from unifiedrpc import endpoint

    @endpoint()
    def endpoint1():
        """Endpoint1 document"""
        return 1

    assert endpoint1.document == 'Endpoint1 document'
    assert endpoint1.signature.name == 'endpoint1'
    assert not endpoint1.signature.parameter.args
    assert not endpoint1.signature.parameter.keywordArg
    assert not endpoint1.signature.parameter.defaults
    assert endpoint1() == 1

    @endpoint()
    def endpoint2(a):
        return 2

    assert len(endpoint2.signature.parameter.args) == 1 and endpoint2.signature.parameter.args[0] == 'a'
    assert not endpoint2.signature.parameter.keywordArg
    assert not endpoint2.signature.parameter.defaults
    assert endpoint2(1) == 2

    @endpoint()
    def endpoint3(a, b = 1):
        return 3

    assert len(endpoint3.signature.parameter.args) == 2 and endpoint3.signature.parameter.args[0] == 'a' and endpoint3.signature.parameter.args[1] == 'b'
    assert not endpoint3.signature.parameter.keywordArg
    assert len(endpoint3.signature.parameter.defaults) == 1 and endpoint3.signature.parameter.defaults['b'] == 1
    assert endpoint3(1) == 3

    @endpoint()
    def endpoint4(a, b = 1, **c):
        return 4

    assert len(endpoint4.signature.parameter.args) == 2 and endpoint4.signature.parameter.args[0] == 'a' and endpoint4.signature.parameter.args[1] == 'b'
    assert endpoint4.signature.parameter.keywordArg == 'c'
    assert len(endpoint4.signature.parameter.defaults) == 1 and endpoint4.signature.parameter.defaults['b'] == 1
    assert endpoint4(1) == 4

    try:
        # Here, we donot support var argument list
        @endpoint()
        def endpoint5(a, b, *c):
            return 5
        raise AssertionError
    except ValueError:
        pass

    @endpoint()
    class Endpoint6(object):
        """Endpoint6 document"""
        value = 1

        def __init__(self, a, b = 1, **c):
            """Create a new Endpoint6
            """

        def __call__(self, a, b = 1, **c):
            """Endpoint6 call method document"""
            return 6

        @endpoint()
        def endpoint7(self, a, b = 1, **c):
            """Endpoint7 document"""
            return 7

        @endpoint()
        @classmethod
        def endpoint8(cls, a, b = 1, **c):
            assert cls.value == 1
            return 8

        # NOTE: here the endpoint 7 is a function, so the 'self' is treated as a normal parameter
        assert len(endpoint7.signature.parameter.args) == 3 and endpoint7.signature.parameter.args[0] == 'self' and endpoint7.signature.parameter.args[1] == 'a' and endpoint7.signature.parameter.args[2] == 'b'
        assert endpoint7.signature.parameter.keywordArg == 'c'
        assert len(endpoint7.signature.parameter.defaults) == 1 and endpoint7.signature.parameter.defaults['b'] == 1
        assert endpoint7.document == 'Endpoint7 document'

        assert len(endpoint8.signature.parameter.args) == 2 and endpoint8.signature.parameter.args[0] == 'a' and endpoint8.signature.parameter.args[1] == 'b'
        assert endpoint8.signature.parameter.keywordArg == 'c'
        assert len(endpoint8.signature.parameter.defaults) == 1 and endpoint8.signature.parameter.defaults['b'] == 1

    assert Endpoint6.endpoint8(1) == 8

    assert len(Endpoint6.signature.parameter.args) == 2 and Endpoint6.signature.parameter.args[0] == 'a' and Endpoint6.signature.parameter.args[1] == 'b'
    assert Endpoint6.signature.parameter.keywordArg == 'c'
    assert len(Endpoint6.signature.parameter.defaults) == 1 and Endpoint6.signature.parameter.defaults['b'] == 1
    assert Endpoint6.document == 'Endpoint6 document'
    assert Endpoint6(1)(1) == 6

    ep6 = Endpoint6(1)
    assert len(ep6.endpoint7.signature.parameter.args) == 2 and ep6.endpoint7.signature.parameter.args[0] == 'a' and ep6.endpoint7.signature.parameter.args[1] == 'b'
    assert ep6.endpoint7.signature.parameter.keywordArg == 'c'
    assert len(ep6.endpoint7.signature.parameter.defaults) == 1 and ep6.endpoint7.signature.parameter.defaults['b'] == 1
    assert ep6.endpoint7.document == 'Endpoint7 document'
    assert ep6.endpoint7(1) == 7

    endpoint9 = endpoint()(ep6)
    assert len(endpoint9.signature.parameter.args) == 2 and endpoint9.signature.parameter.args[0] == 'a' and endpoint9.signature.parameter.args[1] == 'b'
    assert endpoint9.signature.parameter.keywordArg == 'c'
    assert len(endpoint9.signature.parameter.defaults) == 1 and endpoint9.signature.parameter.defaults['b'] == 1
    assert endpoint9.document == 'Endpoint6 document'
    assert endpoint9(1) == 6

    try:
        # Here, we donnot support argument with tuple
        endpoint(document = 'Endpoint10 document')(lambda (a, b): 10)
        raise AssertionError
    except ValueError:
        pass

    endpoint10 = endpoint(document = 'Endpoint10 document')(lambda a, b: 10)
    assert len(endpoint10.signature.parameter.args) == 2 and endpoint9.signature.parameter.args[0] == 'a' and endpoint9.signature.parameter.args[1] == 'b'
    assert not endpoint10.signature.parameter.keywordArg
    assert not endpoint10.signature.parameter.defaults
    assert endpoint10.document == 'Endpoint10 document'
    assert endpoint10(1, 2) == 10

