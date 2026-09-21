# julee-kits

Domain kits for [julee](https://github.com/pyx-industries/julee): reusable
bounded contexts, with their infrastructure and app contributions, that a
solution plugs in.

The framework itself lives in the julee repository. Everything here knows
about a particular business domain, which is why it is not in the framework.
See [ADR 012](https://github.com/pyx-industries/julee/blob/master/docs/ADRs/012-framework-and-kits.md).

## Kits

Each kit is a distribution of its own, with its own dependencies, its own
doctrine run and its own release. None are here yet; they arrive one at a
time out of `julee.contrib`:

| Kit | Distribution | Import package |
|---|---|---|
| CEAP (capture, extract, assemble, publish) | `julee-ceap` | `julee_ceap` |
| Polling | `julee-polling` | `julee_polling` |
| UNTP | `julee-untp` | `julee_untp` |
| Supply chain | `julee-supply-chain` | `julee_supply_chain` |
| Ontology mapper | `julee-onto-mapper` | `julee_onto_mapper` |

## Using a kit

Install it, then adopt it. Installing alone does nothing: a kit that arrives
as a transitive dependency must not change a solution's behaviour.

```toml
[tool.julee]
kits = ["ceap"]
```

## Layout

One uv workspace, one directory per kit, each a julee solution in its own
right as [ADR 001](https://github.com/pyx-industries/julee/blob/master/docs/ADRs/001-contrib-layout.md)
describes.
