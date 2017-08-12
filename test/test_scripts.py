from unittest import TestCase, TestSuite
from collections import namedtuple
import subprocess as proc
import os.path as path


def call_script(*args):
    args = ('python',) + args
    p = proc.Popen(args, stdout=proc.PIPE, stderr=proc.PIPE, shell=True)
    stdout, stderr = map(lambda x: x.decode('utf-8').strip(),
                         p.communicate())

    return p.returncode, stdout, stderr


def script_name(*args):
    return path.join(path.dirname(__file__), 'examples', *args)


# Naming to clarify usage at call sites
expect = namedtuple('expect', ('ret', 'out', 'err'))
expect_fail = (lambda r: r != 0, '', lambda e: 'usage' in e.lower())


class ScriptTestCase(TestCase):
    script = None

    def run_test_case(self, expected, args):
        e_ret, e_out, e_err = expected
        ret, out, err = call_script(self.script, *args)

        try:
            if not callable(e_ret):
                self.assertEqual(e_ret, ret)
            else:
                self.assertTrue(e_ret(ret), ret)

            if not callable(e_out):
                self.assertSequenceEqual(e_out.splitlines(), out.splitlines())
            else:
                self.assertTrue(e_out(out), out)

            if not callable(e_err):
                self.assertSequenceEqual(e_err.splitlines(), err.splitlines())
            else:
                self.assertTrue(e_err(err), err)
        except AssertionError:
            for e in ['ret', 'out', 'err']:
                print(e + ' = ' + repr(locals()[e]))
            raise


class TestOptional(ScriptTestCase):
    script = script_name('script_optional.py')

    def test_only_required(self):
        self.run_test_case(
            expect(0, '2.0', ''),
            ['4', '2'],
        )

    def test_with_optional(self):
        self.run_test_case(
            expect(0, '4.5\nmessage', ''),
            ['9', '2', 'message']
        )

    def test_less_than_required(self):
        self.run_test_case(
            expect_fail,
            ['7'],
        )


class TestKeyword(ScriptTestCase):
    script = script_name('script_keyword.py')

    def test_positional_only(self):
        self.run_test_case(
            expect(0, '10', ''),
            ['4', '6'],
        )

    def test_with_keyword_style(self):
        self.run_test_case(
            expect(0, '3\nHello, World!', ''),
            ['1', '2', '--message', 'Hello, World!'],
        )

    def test_no_keyword(self):
        self.run_test_case(
            expect_fail,
            ['1', '2', 'Hello, World!'],
        )


class TestAlias(ScriptTestCase):
    script = script_name('script_alias.py')

    def test_without_optional(self):
        self.run_test_case(
            expect(0, '3.0\n0.0', ''),
            ['2'],
        )

    def test_with_optional(self):
        self.run_test_case(
            expect(0, '15.0\n8.0', ''),
            ['10', '--opt1', '5', '--opt2', '2'],
        )

    def test_with_alias(self):
        self.run_test_case(
            expect(0, '6.0\n4.0', ''),
            ['5', '-x', '1', '-y', '1'],
        )

    def test_wrong_keyword(self):
        self.run_test_case(
            expect_fail,
            ['5', '-y', '1', '-z', '1']
        )


suite = TestSuite()
suite.addTests((TestOptional(), TestKeyword(), TestAlias()))
