"""Readers that turn a solution's source files into HCD entities.

A solution is written down in several formats, and each one is read here:

- gherkin.py: feature files, which are where stories are written
- yaml.py: the manifests that declare apps and integrations
- directive_specs.py: what options each HCD RST directive accepts
- docutils_parser.py: RST documents, read through docutils so that a
  document can be turned back into the document it came from
"""
