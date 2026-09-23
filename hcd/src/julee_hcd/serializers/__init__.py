"""Writers that turn HCD entities back into the files they came from.

The counterpart of parsers: a story becomes a Gherkin feature file, an
app or integration becomes a YAML manifest, and an epic, journey or
accelerator becomes RST directives.

These write the directive by hand. julee_hcd.templates does the same job
through Jinja2, keeping the surrounding prose a document carried, which
is what the RST-backed repositories use.
"""
