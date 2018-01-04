from datetime import date

import fest.bases


class SampleAPI(fest.bases.BaseAPI):
    pass


class SampleObject(fest.bases.BaseObject):
    pass


def test_api_init():
    ret = SampleAPI('service')
    assert ret.service is 'service'


def test_api_log():
    ret = SampleAPI('service')
    assert ret.__log__ == 'tests.test_bases.SampleAPI'


def test_obj_init():
    ret = SampleObject('service', fizz='buzz')
    assert ret.struct == {'fizz': 'buzz'}


def test_obj_getitem():
    ret = SampleObject('service', fizz='buzz')
    assert ret['fizz'] == 'buzz'


def test_obj_len():
    ret = SampleObject('service', fizz='buzz')
    assert len(ret) == 1


def test_obj_iter():
    ret = SampleObject('service', fizz='buzz')
    assert list(ret) == list({'fizz': 'buzz'})


def test_obj_repr():
    ret = SampleObject('service', fizz='buzz')
    assert repr(ret) == '{\n  "fizz": "buzz"\n}'


def test_obj_str():
    ret = SampleObject('service', fizz='buzz')
    assert str(ret) == '{\n  "fizz": "buzz"\n}'


def test_obj_str_err():
    ret = SampleObject('service', fizz=date(2018, 1, 1))
    assert str(ret) == "{'fizz': datetime.date(2018, 1, 1)}"


def test_digest():
    ret = SampleObject('service', fizz='buzz')
    assert ret.digest() == '4f4a4ec053fc9c86aa8863127fd8f303dfd94aac'


def test_source_digest():
    ret = SampleObject('service', fizz='buzz')
    assert ret.source_digest is None


def test_source_id():
    ret = SampleObject('service', fizz='buzz')
    assert ret.source_id is None
