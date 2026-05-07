"""
Tests for the EPL Error Explainer module (epl.error_explainer).

Tests pattern matching, "did you mean?" suggestions, Python/JS keyword
detection, and the terminal formatting output.

Run with:  pytest tests/test_error_explainer.py -v
"""

import sys
import os

# Ensure the project root is on the path so `epl` is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from epl.errors import (
    EPLError,
    NameError as EPLNameError,
    ParserError,
    TypeError as EPLTypeError,
    RuntimeError as EPLRuntimeError,
    IndexError as EPLIndexError,
    ImportError as EPLImportError,
    set_source_context,
)
from epl.error_explainer import explain, format_explanation, ErrorExplanation


# ═══════════════════════════════════════════════════════════
#  Pattern Matching Tests
# ═══════════════════════════════════════════════════════════

class TestUndefinedVariable:
    """Test explanations for undefined variable errors."""

    def test_basic_undefined(self):
        err = EPLNameError("Undefined variable 'score'", line=3)
        source = 'Say "Hello"\nCreate name equal to "Alice"\nSay score'
        exp = explain(err, source=source)
        assert exp.category == "name"
        assert "score" in exp.what_went_wrong
        assert exp.confidence >= 0.8

    def test_typo_suggestion(self):
        err = EPLNameError("Undefined variable 'naem'", line=2)
        source = 'Create name equal to "Alice"\nSay naem'
        exp = explain(err, source=source)
        assert "name" in exp.what_went_wrong or "name" in exp.how_to_fix
        assert exp.category == "name"

    def test_no_similar_match(self):
        err = EPLNameError("Undefined variable 'xyzzy'", line=1)
        source = "Say xyzzy"
        exp = explain(err, source=source)
        assert "xyzzy" in exp.what_went_wrong
        assert "Create" in exp.how_to_fix


class TestUndefinedFunction:
    """Test explanations for undefined function errors."""

    def test_stdlib_typo(self):
        err = EPLNameError("Undefined function 'leng'", line=1)
        source = 'Say leng("hello")'
        exp = explain(err, source=source)
        assert exp.category == "name"
        # Should suggest "length"
        assert "length" in exp.how_to_fix.lower() or "length" in exp.corrected_code.lower()

    def test_unknown_function(self):
        err = EPLNameError("Undefined function 'frobnicate'", line=1)
        exp = explain(err, source='Call frobnicate()')
        assert exp.category == "name"
        assert "Function" in exp.how_to_fix

    def test_close_match_sorted(self):
        err = EPLNameError("Undefined function 'srot'", line=1)
        exp = explain(err, source='Create result equal to srot(mylist)')
        # Should suggest 'sorted' or 'sqrt'
        assert exp.category == "name"


class TestParserErrors:
    """Test explanations for parser/syntax errors."""

    def test_missing_end(self):
        err = ParserError('Expected "End"', line=5)
        source = 'Function greet Takes name\n    Say "Hello " + name\n'
        exp = explain(err, source=source)
        assert exp.category == "syntax"
        assert "End" in exp.how_to_fix

    def test_missing_end_identifies_block(self):
        err = ParserError('Expected "End"', line=5)
        source = (
            'Say "Start"\n'
            'If score > 10 Then\n'
            '    Say "High"\n'
            'Say "Done"\n'
        )
        exp = explain(err, source=source)
        assert exp.category == "syntax"
        assert "If" in exp.what_went_wrong

    def test_unexpected_python_print(self):
        err = ParserError("Unexpected token 'print'", line=1)
        source = 'print("Hello World")'
        exp = explain(err, source=source)
        assert "Say" in exp.how_to_fix
        assert exp.category == "syntax"

    def test_unexpected_python_def(self):
        err = ParserError("Unexpected token 'def'", line=1)
        source = 'def greet(name):'
        exp = explain(err, source=source)
        assert "Function" in exp.how_to_fix

    def test_unexpected_js_let(self):
        err = ParserError("Unexpected token 'let'", line=1)
        source = 'let x = 5'
        exp = explain(err, source=source)
        assert "Create" in exp.how_to_fix

    def test_unexpected_js_const(self):
        err = ParserError("Unexpected token 'const'", line=1)
        source = 'const PI = 3.14'
        exp = explain(err, source=source)
        assert "Constant" in exp.how_to_fix

    def test_unexpected_unknown_token(self):
        err = ParserError("Unexpected token 'blarg'", line=1)
        exp = explain(err, source='blarg 123')
        assert exp.category == "syntax"
        assert exp.what_went_wrong != ""


class TestTypeErrors:
    """Test explanations for type mismatch errors."""

    def test_string_plus_integer(self):
        err = EPLTypeError("Cannot add string and integer", line=3)
        exp = explain(err, source='Create result equal to "score: " + 42')
        assert exp.category == "type"
        assert "to_text" in exp.how_to_fix

    def test_type_mismatch_generic(self):
        err = EPLTypeError("Type mismatch in comparison", line=2)
        exp = explain(err)
        assert exp.category == "type"

    def test_cannot_compare(self):
        err = EPLTypeError("Cannot compare these values", line=1)
        exp = explain(err)
        assert exp.category == "type"


class TestRuntimeErrors:
    """Test explanations for runtime errors."""

    def test_divide_by_zero(self):
        err = EPLRuntimeError("Division by zero", line=2)
        exp = explain(err, source='Create x equal to 10\nCreate y equal to x / 0')
        assert exp.category == "runtime"
        assert "zero" in exp.what_went_wrong.lower()

    def test_index_out_of_range(self):
        err = EPLIndexError("Index out of range: 5", line=2)
        exp = explain(err)
        assert exp.category == "index"
        assert "length" in exp.how_to_fix.lower()

    def test_key_not_found(self):
        err = EPLRuntimeError("Key not found: 'age'", line=3)
        exp = explain(err)
        assert exp.category == "runtime"
        assert "has_key" in exp.how_to_fix

    def test_max_recursion(self):
        err = EPLRuntimeError("Maximum recursion depth exceeded", line=5)
        exp = explain(err)
        assert exp.category == "runtime"
        assert "base case" in exp.how_to_fix.lower()

    def test_not_callable(self):
        err = EPLNameError("'x' is not callable", line=2)
        exp = explain(err)
        assert exp.category == "name"


class TestImportErrors:
    """Test explanations for import errors."""

    def test_module_not_found(self):
        err = EPLImportError("Cannot find module 'mylib'", line=1)
        exp = explain(err, source='Import "mylib"')
        assert exp.category == "import"


# ═══════════════════════════════════════════════════════════
#  Phase 3: Expanded Pattern Tests (EPL-native error messages)
# ═══════════════════════════════════════════════════════════

class TestNativeNameErrors:
    """Test patterns matching EPL's native error message phrasing."""

    def test_variable_not_created(self):
        """EPL says 'has not been created yet', not 'undefined variable'."""
        err = EPLNameError('Variable "score" has not been created yet.', line=3)
        source = 'Say score'
        exp = explain(err, source=source)
        assert exp.category == "name"

    def test_function_not_defined(self):
        """EPL says 'Function "X" has not been defined.'"""
        err = EPLNameError('Function "greet" has not been defined.', line=5)
        exp = explain(err)
        assert exp.category == "name"
        assert "greet" in exp.what_went_wrong

    def test_function_not_defined_with_typo(self):
        """Should suggest stdlib functions for close matches."""
        err = EPLNameError('Function "langth" has not been defined.', line=2)
        exp = explain(err)
        assert exp.category == "name"
        assert "length" in exp.how_to_fix.lower()

    def test_class_not_found(self):
        err = EPLNameError('Class "Animal" not found.', line=10)
        exp = explain(err)
        assert exp.category == "name"
        assert "animal" in exp.what_went_wrong.lower()

    def test_parent_class_not_found(self):
        err = EPLNameError('Parent class "BaseEntity" not found.', line=5)
        exp = explain(err)
        assert exp.category == "name"
        assert "baseentity" in exp.what_went_wrong.lower()


class TestNativeTypeErrors:
    """Test patterns matching EPL's native TypeError messages."""

    def test_not_a_class(self):
        err = EPLTypeError('"myVar" is not a class.', line=3)
        exp = explain(err)
        assert exp.category == "type"
        assert "myvar" in exp.what_went_wrong.lower()

    def test_list_index_must_be_integer(self):
        err = EPLTypeError("List index must be integer.", line=4)
        exp = explain(err)
        assert exp.category == "type"
        assert "integer" in exp.what_went_wrong.lower()

    def test_cannot_call(self):
        err = EPLTypeError("Cannot call integer.", line=2)
        exp = explain(err)
        assert exp.category == "type"
        assert "integer" in exp.what_went_wrong.lower()

    def test_for_each_requires_list(self):
        err = EPLTypeError("For each requires list, text, map, or generator.", line=6)
        exp = explain(err)
        assert exp.category == "type"
        assert "for each" in exp.what_went_wrong.lower()

    def test_repeat_count(self):
        err = EPLTypeError("Repeat count must be integer.", line=3)
        exp = explain(err)
        assert exp.category == "type"

    def test_property_not_found(self):
        err = EPLTypeError('integer has no property "length".', line=5)
        exp = explain(err)
        assert exp.category == "type"
        assert "length" in exp.what_went_wrong


class TestNativeRuntimeErrors:
    """Test patterns matching EPL's native RuntimeError messages."""

    def test_constant_reassignment(self):
        err = EPLRuntimeError('Cannot change constant "PI".', line=4)
        exp = explain(err)
        assert exp.category == "runtime"
        assert "pi" in exp.what_went_wrong.lower()

    def test_wrong_arg_count(self):
        err = EPLRuntimeError("length() takes 1 argument.", line=3)
        exp = explain(err)
        assert exp.category == "runtime"
        assert "length" in exp.what_went_wrong

    def test_cannot_convert(self):
        err = EPLRuntimeError("Cannot convert to integer.", line=2)
        exp = explain(err)
        assert exp.category == "runtime"
        assert "convert" in exp.what_went_wrong.lower()

    def test_cannot_add_types(self):
        err = EPLTypeError("Cannot add text and integer.", line=5)
        exp = explain(err)
        assert exp.category == "type"


# ═══════════════════════════════════════════════════════════
#  Formatting Tests
# ═══════════════════════════════════════════════════════════

class TestFormatExplanation:
    """Test the terminal output formatting."""

    def test_basic_format_no_color(self):
        exp = ErrorExplanation(
            error_type="NameError", error_code="E0500",
            message="Undefined variable 'x'", line=5,
            source_line="Say x",
            what_went_wrong="Variable 'x' was never created.",
            how_to_fix="Add: Create x equal to <value>",
            corrected_code="",
        )
        output = format_explanation(exp, color=False)
        assert "What went wrong" in output
        assert "How to fix" in output
        assert "Variable 'x'" in output

    def test_format_with_corrected_code(self):
        exp = ErrorExplanation(
            error_type="ParserError", error_code="E0200",
            message="Unexpected token", line=1,
            source_line='print("hi")',
            what_went_wrong="Wrong keyword",
            how_to_fix="Use Say",
            corrected_code='Say "hi"',
        )
        output = format_explanation(exp, color=False)
        assert "Suggested code" in output
        assert 'Say "hi"' in output

    def test_format_without_ai(self):
        exp = ErrorExplanation(
            error_type="RuntimeError", error_code="E0300",
            message="Some error", line=1,
            source_line="",
            what_went_wrong="Something broke",
            how_to_fix="Fix it",
            corrected_code="",
            ai_explanation="",
        )
        output = format_explanation(exp, color=False)
        assert "AI Analysis" not in output

    def test_format_with_ai(self):
        exp = ErrorExplanation(
            error_type="RuntimeError", error_code="E0300",
            message="Some error", line=1,
            source_line="",
            what_went_wrong="Something broke",
            how_to_fix="Fix it",
            corrected_code="",
            ai_explanation="The AI thinks you should do X.",
        )
        output = format_explanation(exp, color=False)
        assert "AI Analysis" in output
        assert "The AI thinks" in output


# ═══════════════════════════════════════════════════════════
#  Fallback / Edge Case Tests
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test that the explainer handles edge cases gracefully."""

    def test_no_source_provided(self):
        err = EPLNameError("Undefined variable 'x'", line=1)
        exp = explain(err, source=None, ai=False)
        assert exp.what_went_wrong != ""
        assert exp.ai_explanation == ""

    def test_empty_source(self):
        err = EPLRuntimeError("Something failed", line=1)
        exp = explain(err, source="", ai=False)
        assert exp.source_line == ""

    def test_line_out_of_range(self):
        err = EPLRuntimeError("Error", line=999)
        exp = explain(err, source="Say hello", ai=False)
        assert exp.source_line == ""

    def test_no_pattern_match(self):
        err = EPLRuntimeError("Something completely unexpected happened", line=1)
        exp = explain(err, source="Say hello", ai=False)
        assert exp.confidence < 0.5  # Low confidence = no pattern matched
        assert exp.what_went_wrong != ""  # Still has a default message

    def test_no_ai_when_disabled(self):
        err = EPLNameError("Undefined variable 'x'", line=1)
        exp = explain(err, source="Say x", ai=False)
        assert exp.ai_explanation == ""


# ═══════════════════════════════════════════════════════════
#  to_context_dict Tests (errors.py modification)
# ═══════════════════════════════════════════════════════════

class TestContextDict:
    """Test the to_context_dict() method added to EPLError."""

    def test_context_dict_with_source(self):
        source = "Say hello\nCreate x equal to 5\nSay x + y"
        set_source_context(source, "test.epl")
        err = EPLNameError("Undefined variable 'y'", line=3)
        ctx = err.to_context_dict()
        assert "source_line" in ctx
        assert "Say x + y" in ctx["source_line"]
        assert "context" in ctx

    def test_context_dict_without_source(self):
        set_source_context("", "<empty>")
        err = EPLNameError("Undefined variable 'x'", line=1)
        ctx = err.to_context_dict()
        # Should still have basic fields from to_dict()
        assert ctx["type"] == "NameError"
        assert ctx["message"] == "Undefined variable 'x'"
        # But no source_line since source is empty
        assert "source_line" not in ctx


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
