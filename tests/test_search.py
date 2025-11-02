import os
import tempfile
from search_tool import search_in_file


def test_search_simple():
    content = "first line\nsecond keyword here\nthird line\nkeyword at end\n"
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as t:
        t.write(content)
        tmpname = t.name

    try:
        results = search_in_file(tmpname, 'keyword')
        assert isinstance(results, list)
        # should find two matches
        assert len(results) == 2
        # check line numbers
        assert results[0]['line'] == 2
        assert 'second keyword here' in results[0]['text']
        assert results[1]['line'] == 4
    finally:
        os.remove(tmpname)


def test_search_case_insensitive():
    content = "Alpha\nbeta KEYWORD here\nGamma\nkeyword lower\n"
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as t:
        t.write(content)
        tmpname = t.name

    try:
        # default is case-sensitive: should find 1 match when searching 'keyword'
        res_case_sensitive = search_in_file(tmpname, 'keyword')
        assert len(res_case_sensitive) == 1

        # with case_insensitive True, should find 2 matches
        res_ci = search_in_file(tmpname, 'keyword', case_insensitive=True)
        assert len(res_ci) == 2
        assert res_ci[0]['line'] == 2
        assert res_ci[1]['line'] == 4
    finally:
        os.remove(tmpname)


def test_search_regex():
    content = "one 123\ntwo abc\nthree 4567\nno digits here\n"
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as t:
        t.write(content)
        tmpname = t.name

    try:
        # search for any digits using regex
        res = search_in_file(tmpname, r"\d+", use_regex=True)
        assert len(res) == 2
        assert res[0]['line'] == 1
        assert res[1]['line'] == 3

        # invalid regex should raise ValueError
        try:
            search_in_file(tmpname, r"(unclosed[", use_regex=True)
            raised = False
        except ValueError:
            raised = True
        assert raised
    finally:
        os.remove(tmpname)
