"""Use case for resolving app references.

Finds stories, personas, journeys, and epics related to an app.

The finding itself is in the domain, with the entities it is about:
three in models/app.py, and get_personas_for_app in models/persona.py,
because persona.py already imports app.py and the reverse would be a
cycle. They were here, which is how an adapter came to import a use
case package to reach them.
"""

from julee_hcd.domain.models.app import (
    get_epics_for_app,
    get_journeys_for_app,
    get_stories_for_app,
)
from julee_hcd.domain.models.persona import get_personas_for_app

from ..dtos.resolve_app_references import (
    ResolveAppReferencesRequest,
    ResolveAppReferencesResponse,
)


class ResolveAppReferencesUseCase:
    """Resolve everything an app is connected to at once.

    An app's page shows its stories, the personas who use it, and the
    journeys and epics those stories belong to. All four are derived from
    the same set of stories, so they are resolved together.
    """

    async def execute(
        self, request: ResolveAppReferencesRequest
    ) -> ResolveAppReferencesResponse:
        """Resolve an app's references.

        Args:
            request: The app, and the entities to search

        Returns:
            The stories, personas, journeys and epics connected to the app
        """
        stories = list(request.stories)
        epics = list(request.epics)
        return ResolveAppReferencesResponse(
            stories=tuple(get_stories_for_app(request.app, stories)),
            personas=tuple(get_personas_for_app(request.app, stories, epics)),
            journeys=tuple(
                get_journeys_for_app(request.app, stories, list(request.journeys))
            ),
            epics=tuple(get_epics_for_app(request.app, stories, epics)),
        )
