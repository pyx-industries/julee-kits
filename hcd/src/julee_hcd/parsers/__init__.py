"""Readers that turn a solution's source files into HCD entities.

A solution is written down in several formats, and each one is read here:

- gherkin.py: feature files, which are where stories are written
- yaml.py: the manifests that declare apps and integrations
- directive_specs.py: what options each HCD RST directive accepts
- docutils_parser.py: RST documents, read through docutils so that a
  document can be turned back into the document it came from
"""

from julee.core.parsers.ast import scan_bounded_contexts

from .gherkin import scan_feature_directory
from .yaml import scan_app_manifests, scan_integration_manifests

__all__ = [
    # Re-exported from the kernel, because scanning code for bounded
    # contexts is the same job whoever asks for it, and a caller reading
    # a solution should not have to know which package it lives in.
    "scan_bounded_contexts",
    "scan_app_manifests",
    "scan_feature_directory",
    "scan_integration_manifests",
]
