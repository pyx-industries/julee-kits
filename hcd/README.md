# julee-hcd

Human-centred design models for [julee](https://github.com/pyx-industries/julee)
solutions: the people a solution is for, what they are trying to do, and the
applications and integrations that serve them.

```toml
[tool.julee]
kits = ["hcd"]
```

Every solution has users with goals, so this kit holds no domain of its own.
It gives a solution somewhere to say who it is for, and
[julee-viewpoints](../viewpoints/) renders that into documentation.
[julee-c4](../c4/) describes the same solution's structure.

The kit provides:

- **Models:** `Persona`, `Journey`, `Epic`, `Story`, `App`, `Integration`,
  `Contrib` and `CodeInfo`.
- **Repositories:** protocols per model, with in-memory, file and RST
  implementations. The RST ones round-trip losslessly, so documentation stays
  the source of truth rather than a rendering of something else.
- **Use cases:** CRUD for each model, generated from the entities (ADR 008),
  plus the orchestrations that assemble an epic, a journey or a story from its
  parts.

Accelerators live in `julee.core` rather than here, because both this kit and
private supply-chain work describe the same thing.

Licensed GPL-3.0-or-later.
