# LaTeX: Writing Style

LaTeX writing style, particularly for scientific notes and papers.

---

## Document Structure

| Rule | Detail |
|---|---|
| No paragraph indentation | add `\setlength{\parindent}{0pt}` and `\setlength{\parskip}{6pt}` to the preamble |
| No `\paragraph*{}` headings | fold the label into running prose instead |
| Source indentation | 4 spaces per nesting level (never tabs); applies to environments, sections, and macro bodies |

---

## Cross-references

| Rule | Detail |
|---|---|
| Equation, figure, and table references | use `\cref{...}` standalone (from `cleveref`); never `equation~\ref{...}`, `figure~\ref{...}`, etc.; do not precede `\cref` with a descriptive name |
| Section references | use `§\ref{sec:...}` |

---

## Labels

Three-part hierarchy: `type:group:name`. The group is the context; the name is the specific item. Sub-groups use `-` within the group field.

| Type prefix | Use |
|---|---|
| `eqn:` | equations |
| `sec:` | sections, subsections, subsubsections |
| `fig:` | figures |
| `tab:` | tables |
| Sub-groups | `-` within the group field: `eqn:mhd-linear:momentum`, `sec:mhd-waves:linearise` |

---

## Mathematics

| Rule | Detail |
|---|---|
| Inline math | use `$ ... $` |
| All display math | use `align`, numbering every equation even if unreferenced; never `$$` or `equation` |
| Roman (upright) text in math | use `\mathrm{}`; `{\rm ...}` is a deprecated plain TeX mode switch |
| Exponentials | use `\exp(...)` rather than `e^{...}` |
| Coordinate planes | write planes as `(x,y)` or `$(\mVectorUnit{e}_1,\mVectorUnit{e}_2)$`, not `x--y` or `x\text{-}y` |
| Symbol case | lower-case for scalar and vector fields (including placeholder/dummy variables); upper-case for rank-2+ tensor fields, e.g. the vector field $\mVector{F}$ should be written $\mVector{f}$ |
| Equation layout (single equation) | LHS on its own line; `&= RHS` indented below; long RHS terms broken across lines, indented to show structure; `, \label{}` on its own final line |
| Equation layout (multi-equation, with `\\`) | `, \label{}` must appear on the same source line as `\\`, not on a separate line; for short RHS append inline (`&= 0 , \label{...} \\`); for long RHS put on the last continuation line before `\\` |
| Tensor dot-product conventions | when defining a rank-2+ tensor via component notation, state at first use which index is contracted from which side of a dot product, e.g. `dotting from the left contracts <j>, leaves <i> free`; pick one convention per document and apply it consistently everywhere the tensor is dotted with a vector |
| Bracket hierarchy | square brackets mark a differential operator (`nabla`, `D_t`, `partial_<i>`, a directional-derivative operator like `(<a> . nabla)`) acting on the whole enclosed multi-term group; round brackets are plain algebraic/coefficient grouping |

Single-equation example:
```latex
\begin{align}
    \text{LHS term one}
        + \text{LHS term two}
        &= \text{RHS term one}
            + \text{RHS term two}
    , \label{eqn:group:name}
\end{align}
```

Multi-equation example:
```latex
\begin{align}
    \text{short LHS}
        &= \text{short RHS} , \label{eqn:group:name-a} \\
    \text{short LHS}
        &= \text{long RHS term one}
            + \text{long RHS term two}
        , \label{eqn:group:name-b}
\end{align}
```

---

## Explanatory Prose

Lean toward direct, declarative derivation steps (`<X> gives...`, `substituting <Y>...`) over commentary. A conversational aside can be worth it at a document's hardest step, but only when it teaches the reader something not already visible in the equation.

---

## Footnotes

- Content goes on its own indented line; the closing brace goes on its own line.
- Never attach directly to a math expression (`$...$\footnote{}`); the marker reads as an exponent. Rephrase so the marker attaches to a word.

```latex
\footnote{
    note text
}
```
