# Python: Testing

How to structure and run Python unit and validation tests.

---

## Unit Tests (utests)

- Live under `utests/`, mirroring the source structure.
- Run via pytest; test files are named `test_<module_name>.py`.
- Organised into focused `unittest.TestCase` classes named after what they test.

```python
class Test<Concept>_<Aspect>(unittest.TestCase):

    def test_<behaviour>(
        self,
    ): ...
```

---

## Validation Tests (vtests)

- Live under `vtests/`, mirroring the source structure.
- Use when a unit test is not practical: numerical convergence, decomposition accuracy, or integrated behaviour across modules.
- Run via `uv run vtests/run_all.py`, which runs each `test_*.py` as a subprocess and passes or fails on its exit code.
- Each is one `Test`-prefixed class, so a project can also collect them with pytest.
- Every vtest saves one figure, inspected by eye alongside its pass/fail signal.

`__init__` stores only tunable test parameters; `run` creates the figure and drives the checks, passing data explicitly to single-task helpers. A helper lives on the class only if it reads one of those parameters; otherwise it is a module-level function:

```python
class Test<Concept>:

    def __init__(
        self,
    ):
        ## tunable, explicitly-typed test parameters
        ...

    def run(
        self,
    ) -> None:
        ## generate the input dataset and initialise the figure
        failed: list[str] = []
        for <scenario-index>, <scenario-name> in enumerate(<scenarios>):
            ## plot a diagnostic of the scenario
            ## check if the scenario passes, and append its name if not
            ...
        ## save the figure before asserting, so a fail stays inspectable
        assert not failed, f"failed: {failed}"
        ## log the overall result


if __name__ == "__main__":
    Test<Concept>().run()
```

> **Note:** a single-check vtest drops the loop and asserts directly.
