"""Repositories backed by the files a solution already has.

An app and an integration are declared in a YAML manifest beside the code
they describe; a story is written as a Gherkin feature file. These read
those where they are, rather than asking anyone to restate them.

Epics and journeys are not here: they are authored in RST, and the rst
package reads and writes those losslessly.
"""

from .app import FileAppRepository
from .integration import FileIntegrationRepository
from .story import FileStoryRepository

__all__ = [
    "FileAppRepository",
    "FileIntegrationRepository",
    "FileStoryRepository",
]
