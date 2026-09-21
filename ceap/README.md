# julee-ceap

Capture, Extract, Assemble, Publish — document processing for
[julee](https://github.com/pyx-industries/julee) solutions.

```toml
[tool.julee]
kits = ["ceap"]
```

A document arrives; a knowledge service extracts what it can find in it;
the results are assembled against a specification; the assembly is
validated against a policy; the result is published. Each step is a use
case, and each runs durably as a Temporal pipeline.

The kit provides:

- **Domain models:** `Document`, `Assembly`, `AssemblySpecification`,
  `Policy`, `DocumentPolicyValidation`, `KnowledgeServiceConfig`,
  `KnowledgeServiceQuery`.
- **Use cases:** `ExtractAssembleDataUseCase`, `ValidateDocumentUseCase`,
  `InitializeSystemDataUseCase`.
- **Infrastructure:** in-memory and MinIO repositories, Temporal proxies,
  and a knowledge service backed by Anthropic (with an in-memory one for
  tests).
- **Apps:** a FastAPI application and a Temporal worker.

Fixtures for a demonstration run ship in `src/julee_ceap/fixtures/`.
