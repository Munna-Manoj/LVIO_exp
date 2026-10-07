# Writing guide

Every page in this repository should leave a visitor with something they can use: a number, a picture
or a way of thinking. This guide is adapted from the DS-MSP writing guide. Read it once, then use the
[checklist](#checklist) every time.

## 1. Know which kind of page you are writing

Following [Diátaxis](https://diataxis.fr/), each page is exactly **one** of these:

| Type | Answers | Lives in |
|---|---|---|
| **Learn** (tutorial) | "Teach me, step by step." | `docs/learn/` |
| **How-to** | "How do I do X here?" | `docs/how-to/` |
| **Explanation** | "Why does X work this way?" | `docs/explain/` |
| **Reference** | "What exactly is X?" | `docs/reference/` |
| **Experiment report** | "What did we test and what happened?" | `docs/experiments/` |

Don't blend types. If a section is doing two jobs, split it and link between the pages.

## 2. House rules

1. **Prove it with a number**, and the number comes from a results file (CLAUDE.md law 1).
   "Works well" is not allowed.
2. **Lead with the point.** The first sentence says what the section is for.
3. **No paragraph over ~40 words.** Split it, turn it into bullets, or move the aside into a callout.
4. **One idea per section**, under a descriptive heading.
5. **Commands run.** Every shell block can be copied as is, with its expected output shown.
6. **Use the same words everywhere:** SE(3)-LVIO, lightning-lm, ATE (cm), ms/scan, prism frame,
   mission names in lower case (`arc-6`).

## 3. Render on GitHub and on the site

Pages are read on GitHub (portfolio visitors) and on the MkDocs site. Use only syntax that works on both:

| Need | Use | Not |
|---|---|---|
| Callout | `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]` | `!!! note`, `/// note` |
| Diagram | ```` ```mermaid ```` | ASCII art, screenshots of diagrams |
| Maths | `$x$` inline, `$$…$$` display | images of equations |
| Image | `![alt](relative/path.png)` + a caption line in italics | HTML `<img>` without alt |
| Collapsible | `<details><summary>…</summary>…</details>` | `??? note` |

What each callout is for:
- **NOTE** for context;
- **TIP** for intuition;
- **IMPORTANT** for the one takeaway;
- **WARNING** for a specific, real mistake.

Use one or two per page at most.

## 4. Make it visual

- **Spatial ideas get a figure by default.** Frames, planes, residuals, manifolds, trajectories:
  assume yes and justify skipping it.
- **Tables** for comparisons, **Mermaid** for pipelines and lifecycles.
- **Generated, not hand-made.** Every figure comes from a checked-in script (`lvx figures`,
  `scripts/make_*.py`), so it can be regenerated and always shows real output.
- **3D content** (maps, trajectories) goes to the web viewer. The page shows a static render and
  links "Open in 3D →".
- **Caption every figure** with what to look at, not only what it is.

## 5. Formulas

- **One relationship per display block.**
- **Name each new symbol** in prose right after the block, with its unit.
- **Before the formal statement**, give the intuition in one or two sentences, e.g. in a `> [!TIP]`.

```
$$\mathrm{Exp}\big([\rho;\phi]\big) = \begin{bmatrix} \mathrm{Exp}(\phi) & J_l(\phi)\,\rho \\ 0 & 1 \end{bmatrix}$$
```

> $\phi$ is the rotation part of the correction (rad), $\rho$ the translation part (m), and $J_l$ the left
> Jacobian of SO(3), which couples them.

## 6. Experiment reports

- **Generated blocks are never edited.** Write only outside `<!-- lvx:… -->`.
- **TL;DR:** one sentence with the verdict and the number.
- **Observations:** at most 5 bullets, each pointing at a figure or a table cell.
- **Discussion:** explain *why*, and link the relevant `docs/explain/` page.
- **Threats to validity are mandatory.** Few missions, one host, a correlated noise floor…

## 7. Tutorials (Learn)

- **The title says what and for whom.** Prerequisites go once, at the top.
- **Fixed sections, in order:** What you will build, Intuition, The math, Build it, See it, Break it,
  In the real systems, Experiment hooks, Try it, Next. [B01](../../course/chapters/B01-imu-propagation/README.md) is the
  reference chapter; match its depth and tone.
- **Small steps,** each ending in something the reader can check (a printed number, a plot).
- **Intuition first.** One plain-language paragraph or a `> [!TIP]` before the first symbol.
- **"Break it"** shows a failure with a number. Readers learn more from a broken filter than a working one.
- **"Try it":** at least two predict-then-run exercises, answers in `<details>`.
- **The chapter folder is the whole lesson** (law 0). Nothing the reader needs lives anywhere else.
- **Code mirrors the maths:** tag equations `\tag{n}`, cite them in code as `(Eq. n)`, and use the symbols as names.
- **Show it.** Choose synthetic data a person recognises at a glance (the chapter's `scene`), put the
  money plot at the top, and prefer 3D for 3D ideas. Don't force a figure where a number says it all.
- **Output is pasted verbatim** from `results/output.txt`, and result numbers in prose are taken from it (CLAUDE.md §11).

## Checklist

- [ ] One Diátaxis type per page; the first sentence states the purpose.
- [ ] Every number comes from a results file and gives its experiment ID.
- [ ] No paragraph over ~40 words; equations one per block, symbols named.
- [ ] Spatial concept → figure; figures generated by script, captioned.
- [ ] Renders on GitHub (no MkDocs-only syntax) and `mkdocs build --strict` passes.
- [ ] Links resolve; images exist (`tools/check_reports.py` for reports).
