# Python: Testing

---

## Unit Tests (utests)

Unit tests live under `utests/`, mirroring the source structure. Run via pytest.

Test files are named `test_<module_name>.py`. Tests are organised into focused `unittest.TestCase` classes named after what they test:

```python
class Test<Concept>_<Aspect>(unittest.TestCase):

    def test_<behaviour>(
        self,
    ): ...
```

Private helper functions for building test fixtures use a leading underscore: `_make_<fixture>()`.

### Assertions

All assertion calls follow the same multi-line call site rule as regular function calls: one argument per line, trailing comma, even when the call would fit on one line. The value under test goes on its own first line so each assertion is easy to scan:

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
```

Use `assertAlmostEqual()` for floating-point comparisons and `assertRaises()` for error cases:

```python
def test_<behaviour>_raises(
    self,
):
    with self.assertRaises(
        <ErrorType>,
    ):
        <module>.<function>(
            <param>=<invalid_value>,
        )
```

---

## Validation Tests (vtests)

Validation tests live under `vtests/`, mirroring the source structure. Use them when a unit test is not practical: for example, testing numerical convergence, decomposition accuracy, or integrated behaviour across modules.

Vtests are not pytest-based. Run them via `uv run vtests/run_all.py`. Do not use pytest to run vtests; pytest cannot collect them because vtest classes take `__init__` arguments.

Each vtest is a standalone script with a `main()` function, discovered and run via `vtests/run_all.py`. Where possible, save visual output (plots, diagrams) alongside the test to allow human inspection of results:

```python
def main() -> None:
    ## run validation
    ...
    ## save visual output
    ...
```
