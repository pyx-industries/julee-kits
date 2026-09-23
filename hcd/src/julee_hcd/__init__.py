"""Human-centred design models.

A julee kit. It holds the people a solution is for and what they are
trying to do — personas, journeys, epics and stories — together with the
applications and integrations that serve them, and the contributions and
accelerators a solution draws on.

It describes who a system is for rather than how it is built, so it
carries no technical domain of its own. julee-viewpoints renders what a
solution declares here into its documentation, and julee-c4 describes the
same solution's structure.

Install it, then adopt it::

    [tool.julee]
    kits = ["hcd"]
"""

from julee.core.entities.kit import Kit

kit = Kit(
    slug="hcd",
    name="Human-centred design models",
    package="julee_hcd",
    viewpoint=True,
)

__all__ = ["kit"]
