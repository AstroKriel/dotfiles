# Python: Classes and Data Structures

How to structure Python classes, enums, and dataclasses.

---

## Classes

- Private classes have a leading underscore; they are implementation details supporting public classes and are not re-exported.

```python
class _<Name>:
    ...
```

---

## Enums

| Enum type | Base classes |
|---|---|
| Used as strings | `str, Enum` |
| Pure value holder | `Enum` |

```python
class <Name>(str, Enum): ...   # used as strings
class <Name>(Enum): ...        # pure value holder
```

Enum members may hold dataclass instances as values to carry rich metadata per member:

```python
class <EnumName>(Enum):
    <MEMBER> = <DataclassType>(
        <arg>,
        <arg>,
        <arg>,
    )
```

---

## Dataclasses

- Prefer `@dataclass(frozen=True)`; immutable by default.
- Use `@cached_property` for derived attributes.
- Alternative constructors are `@classmethod` methods named for the operation and source: `from_<type>` for pure type conversion, `load_from_<source>` for I/O reads.
- Use context managers (`__enter__` / `__exit__`) for resource lifecycle.
- Use `@property` for attributes derived from existing state: no parameters, no side effects, cheap to compute; use `get_*` for operations that take parameters, involve I/O, or significant cost.
- Method ordering: `__post_init__`, private helpers (`_`), `@property`, `@cached_property`, instance methods, `@classmethod`.
- Store a collection of similar records as a `list` of `@dataclass(frozen=True)` instances.
