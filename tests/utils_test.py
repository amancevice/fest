from fest import utils


class SomeClass:
    pass


def test_future():
    fut = utils.Future(iter("abcdefg"))
    ret = fut.filter(lambda x: x < "e").execute()
    exp = list("abcd")
    assert ret == exp


def test_digest():
    ret = {"fizz": "buzz"}
    assert utils.digest(ret) == "f45195aef08daea1be5dbb1c7feb5763c5bc7b37"


def test_logger():
    obj = SomeClass()
    ret = utils.logger(obj)
    exp = "tests.utils_test.SomeClass"
    assert ret.name == exp
