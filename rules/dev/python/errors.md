# Python: Error Handling

Which exceptions to raise and how to phrase error messages.

---

## Exception Types

| Type | When to use |
|---|---|
| `ValueError` | wrong value; constraint violation |
| `TypeError` | wrong type |
| `KeyError` | missing key in a mapping |
| `FileNotFoundError` | a required file or directory does not exist |
| `RuntimeError` | execution failure; always chain with `from` |

---

## Messages

| Rule | |
|---|---|
| Capitalisation | lowercase throughout; capitalise only where the word itself requires it (proper nouns, class names, acronyms) |
| Punctuation | always end with a period |
| Names and identifiers | backticks: parameter names, flag names, config keys, field names, file extensions, literal values (`` `.sh` ``, `` `True` ``, `` `None` ``) |
| Runtime data | bare: paths, shapes, numbers |
| Single quotes | never for quoting names or values in prose; only where structurally required (e.g. inside an f-string already delimited by double quotes) |
| `:` | narrows scope; each colon introduces a more specific detail: `"config error: output_dir: path does not exist."` |
| `;` | joins a contrasting clause (`got`, `searched in`, `found N`): `"must be positive; got -1."` |
| Chaining | wrap caught exceptions with `raise ... from error`; the chain carries the why, don't repeat it in the message |
| Soft errors | accept `raise_error: bool = True`; raise when `True`, log/warn when `False` |

| Message type | Pattern |
|---|---|
| Constraint | `` `<param>` must be <X>; got `<value>`. `` |
| Not found | `` <X> not found: `<name>`; searched in {<path>}. `` |
| Invalid choice | `` `<param>` must be one of {<options>}; got `<value>`. `` |
| Runtime failure | `` `{<thing>}` failed. `` + chain with `from` |

```python
raise ValueError("`<param>` must be <constraint>.")
raise ValueError(f"`<param>` must be <constraint>; got `{<param>}`.")
raise ValueError(f"`{<param_name>}` must be one of {<valid_options>}; got `{<value>}`.")
raise ValueError(f"<item> not found: `{<key>}`; searched in {<location>}.")
raise FileNotFoundError(f"config error: `<field>`: <reason>; got {<path>}.")
raise RuntimeError(f"`{<command>}` failed.") from <error>
```
