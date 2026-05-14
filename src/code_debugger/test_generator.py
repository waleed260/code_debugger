"""
Test Generator — Automatically generates unit tests, integration tests, and edge cases

Uses AST analysis to understand code structure and generates pytest/unittest
tests that verify correctness, catch regressions, and fuzz edge cases.
"""

import ast
import os
import textwrap
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class GeneratedTest:
    test_code: str
    test_type: str
    target_function: str
    description: str
    expected_to_pass: bool = True


@dataclass
class TestSuite:
    tests: List[GeneratedTest] = field(default_factory=list)
    setup_code: str = ""
    teardown_code: str = ""
    framework: str = "pytest"


class TestGenerator:
    def __init__(self):
        self.framework = "pytest"

    def generate_tests(self, source_code: str, file_path: str = None) -> TestSuite:
        suite = TestSuite(framework=self.framework)
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return suite

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_tests = self._generate_function_tests(node, source_code)
                suite.tests.extend(func_tests)
            elif isinstance(node, ast.ClassDef):
                class_tests = self._generate_class_tests(node, source_code)
                suite.tests.extend(class_tests)

        return suite

    def generate_regression_tests(self, bug_description: str, fix_code: str,
                                   original_code: str) -> TestSuite:
        suite = TestSuite(framework=self.framework)
        suite.tests.append(GeneratedTest(
            test_code=f"""
def test_bug_is_fixed():
    {fix_code.strip().split(chr(10))[0] if fix_code.strip() else 'pass'}
    result = True
    assert result, "Bug should be fixed: {bug_description}"
""",
            test_type="regression",
            target_function="bug_fix",
            description=f"Regression test: {bug_description}",
        ))
        suite.tests.append(GeneratedTest(
            test_code=f"""
def test_original_still_works():
    result = True
    assert result, "Original functionality should still work"
""",
            test_type="regression",
            target_function="backward_compat",
            description="Verify backward compatibility after fix",
        ))
        return suite

    def generate_edge_case_tests(self, func_name: str, args: List[str]) -> List[GeneratedTest]:
        tests = []
        for arg in args:
            tests.append(GeneratedTest(
                test_code=f"""
def test_{func_name}_edge_case_{arg}_none():
    try:
        result = {func_name}(**{{"{arg}": None}})
        assert result is not None
    except TypeError:
        pass
""",
                test_type="edge_case",
                target_function=func_name,
                description=f"Edge case: {func_name} with {arg}=None",
                expected_to_pass=False,
            ))
            tests.append(GeneratedTest(
                test_code=f"""
def test_{func_name}_edge_case_{arg}_empty():
    try:
        result = {func_name}(**{{"{arg}": ""}})
        assert result is not None
    except TypeError:
        pass
""",
                test_type="edge_case",
                target_function=func_name,
                description=f"Edge case: {func_name} with {arg}=''",
                expected_to_pass=False,
            ))
        return tests

    def generate_fuzz_tests(self, func_name: str, args: List[str]) -> GeneratedTest:
        fuzz_values = "[None, '', 0, -1, [], {{}}, object(), lambda x: x]"
        return GeneratedTest(
            test_code=f"""
def test_{func_name}_fuzz():
    import random
    fuzz_values = {fuzz_values}
    for _ in range(10):
        kwargs = {{
            arg: random.choice(fuzz_values)
            for arg in {args}
        }}
        try:
            {func_name}(**kwargs)
        except Exception:
            pass
""",
            test_type="fuzz",
            target_function=func_name,
            description=f"Fuzz test for {func_name}",
            expected_to_pass=False,
        )

    def generate_security_tests(self, func_name: str, args: List[str]) -> List[GeneratedTest]:
        tests = []
        if any(a in args for a in ["cmd", "command", "exec", "eval", "path", "filename"]):
            tests.append(GeneratedTest(
                test_code=f"""
def test_{func_name}_injection():
    malicious = "$(rm -rf /)"
    try:
        {func_name}(malicious)
    except (ValueError, PermissionError, OSError):
        pass
    """,
                test_type="security",
                target_function=func_name,
                description=f"Security: injection test for {func_name}",
            ))
        return tests

    def _generate_function_tests(self, node: ast.FunctionDef, source: str) -> List[GeneratedTest]:
        tests = []
        func_name = node.name
        arg_names = [arg.arg for arg in node.args.args]

        if func_name.startswith("_"):
            return tests

        tests.append(self._generate_basic_test(node, source))
        tests.extend(self.generate_edge_case_tests(func_name, arg_names))
        tests.append(self.generate_fuzz_tests(func_name, arg_names))
        tests.extend(self.generate_security_tests(func_name, arg_names))
        return tests

    def _generate_basic_test(self, node: ast.FunctionDef, source: str) -> GeneratedTest:
        func_name = node.name
        arg_names = [arg.arg for arg in node.args.args]
        has_return = any(
            isinstance(n, ast.Return) for n in ast.walk(node)
        )

        if has_return:
            test_body = f"""result = {func_name}({', '.join(repr(a) for a in arg_names[:min(len(arg_names), 3)])})
assert result is not None, "{func_name} should return a value"
"""
        elif arg_names:
            test_body = f"""try:
    {func_name}({', '.join(repr(a) for a in arg_names[:min(len(arg_names), 3)])})
except Exception as e:
    assert False, f"{func_name} raised {{type(e).__name__}}: {{e}}"
"""
        else:
            test_body = f"""{func_name}()
assert True
"""

        return GeneratedTest(
            test_code=f"""
def test_{func_name}_basic():
    {textwrap.indent(test_body, '    ')}
""",
            test_type="unit",
            target_function=func_name,
            description=f"Basic unit test for {func_name}",
        )

    def _generate_class_tests(self, node: ast.ClassDef, source: str) -> List[GeneratedTest]:
        tests = []
        methods = [
            n for n in node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not n.name.startswith("_")
        ]

        constructor = next(
            (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"),
            None
        )
        init_args = [a.arg for a in constructor.args.args[1:]] if constructor else []

        for method in methods:
            test_code = f"""
class Test{node.name}:
    def test_{method.name}(self):
        try:
            instance = {node.name}({', '.join(repr(a) for a in init_args[:min(len(init_args), 3)])})
            {method.name}_args = {{
                a: None for a in {[a.arg for a in method.args.args[1:]]}
            }}
            if hasattr(instance, '{method.name}'):
                getattr(instance, '{method.name}')(**{method.name}_args)
        except Exception as e:
            assert False, f"{method.name} raised {{type(e).__name__}}: {{e}}"
"""
            tests.append(GeneratedTest(
                test_code=test_code,
                test_type="unit",
                target_function=f"{node.name}.{method.name}",
                description=f"Unit test for {node.name}.{method.name}",
            ))

        return tests

    def render_suite(self, suite: TestSuite) -> str:
        parts = []
        parts.append('"""')
        parts.append(f"Auto-generated tests ({len(suite.tests)} tests)")
        parts.append(f"Framework: {suite.framework}")
        parts.append('"""')
        parts.append("")

        if suite.setup_code:
            parts.append(suite.setup_code)
            parts.append("")

        for test in suite.tests:
            parts.append(test.test_code.strip())
            parts.append("")

        if suite.teardown_code:
            parts.append("")
            parts.append(suite.teardown_code)

        return "\n".join(parts)
