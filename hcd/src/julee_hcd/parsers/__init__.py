"""Readers that turn a solution's source files into HCD entities.

A solution is written down in several formats, and each one is read here:

- gherkin.py: feature files, which are where stories are written
- yaml.py: the manifests that declare apps and integrations
- directive_specs.py: what options each HCD RST directive accepts
- docutils_parser.py: RST documents, read through docutils so that a
  document can be turned back into the document it came from
"""

from .gherkin import scan_feature_directory
from .yaml import scan_app_manifests, scan_integration_manifests

# scan_bounded_contexts is deliberately not re-exported here. It lives in
# julee.core.parsers.ast, which imports griffe, which only julee[doctrine]
# installs — so re-exporting it made importing this package fail for
# anyone who had not installed that extra. Whoever scans code should ask
# the kernel for the scanner and declare the extra themselves.
__all__ = [
    "scan_app_manifests",
    "scan_feature_directory",
    "scan_integration_manifests",
]
