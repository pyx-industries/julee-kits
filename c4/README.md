# julee-c4

C4 architecture models for [julee](https://github.com/pyx-industries/julee)
solutions: software systems, containers, components, the relationships
between them, deployment nodes and dynamic steps.

```toml
[tool.julee]
kits = ["c4"]
```

A C4 model describes any system, so this kit holds no domain of its own.
It gives a solution somewhere to say what it is built from, and
[julee-viewpoints](../viewpoints/) renders that into documentation.

The kit provides:

- **Models:** `SoftwareSystem`, `Container`, `Component`, `Relationship`,
  `DeploymentNode`, `DynamicStep`, and the six diagram types.
- **Use cases:** CRUD for each model, generated from the entities (ADR 008),
  and the diagram queries that assemble a landscape, context, container,
  component, deployment or dynamic view.
- **Repositories:** in-memory for tests, file-backed for RST sources.
- **Parsers and serializers:** RST in, RST and PlantUML out.

Regenerate the CRUD with `sh generate-crud.sh`.
