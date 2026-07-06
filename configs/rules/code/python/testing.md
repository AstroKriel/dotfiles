# Python: Testing

How to structure and run Python unit and validation tests.

---

## Unit Tests (utests)

- Live under `utests/`, mirroring the source structure.
- Run via pytest; test files are named `test_<module_name>.py`.
- Organised into focused classes named after what they test.

### TestCase (default)

Use `unittest.TestCase` by default:

```python
class Test<Concept>_<Aspect>(unittest.TestCase):

    def test_<behaviour>(
        self,
    ): ...
```

Assertion calls follow the same multi-line call site rule as regular function calls: one argument per line, trailing comma, even when the call would fit on one line. The value under test goes on its own first line so each assertion is easy to scan:

```python
self.assertEqual(
    <result>,
    <expected>,
)

self.assertTrue(
    <condition>,
)

numpy.testing.assert_array_almost_equal(
    <result>,
    <expected>,
)

with self.assertRaises(
    <ErrorType>,
):
    <module>.<function>(
        <param>=<invalid_value>,
    )
```

### Plain pytest

Use plain pytest classes or functions when a pytest fixture is genuinely the better tool. The canonical case is `capsys` for stdout/stderr testing: it captures what the terminal receives regardless of how the code produces it, while mocking the output object is more fragile and implementation-specific.

```python
class Test<Concept>_<Aspect>:

    def test_<behaviour>(
        self,
        <fixture>: pytest.<FixtureType>[str],
    ) -> None:
        ...
        assert <condition>

    def test_<behaviour>_raises(
        self,
    ) -> None:
        with pytest.raises(
            <ErrorType>,
        ):
            ...
```

### Helpers

Private helper functions get a leading underscore, with a verb that names what they do: `_make_<fixture>()`, `_generate_<data>()`, `_evaluate_<formula>()` are common examples, though not an exhaustive list.

---

## Validation Tests (vtests)

Validation tests live under `vtests/`, mirroring the source structure. Use them when a unit test is not practical: for example, testing numerical convergence, decomposition accuracy, or integrated behaviour across modules.

- Not pytest-based; run via `uv run vtests/run_all.py`.
- Do not use pytest to run vtests; it cannot collect them because vtest classes take `__init__` arguments.

Each vtest is a standalone script with a `main()` function, discovered and run via `vtests/run_all.py`. Where possible, save visual output (plots, diagrams) alongside the test:

```python
def main() -> None:
    ## run validation
    ...
    ## save visual output
    ...
```
