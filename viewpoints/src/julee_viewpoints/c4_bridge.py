"""Bridge between the HCD and C4 viewpoints.

``sphinx_hcd`` and ``sphinx_c4`` each hold their own context
(:class:`~julee_viewpoints.sphinx_hcd.sphinx.context.HCDContext` and
:class:`~julee_viewpoints.sphinx_c4.sphinx.context.C4Context`), populated by
their own directives, and neither extension depends on the other. This
module is the one place that reads *both* - joining what a solution says
about its personas and apps (HCD) to what it says about its software
systems and containers (C4).

It is deliberately kept as a single, self-contained module rather than
scattered across ``sphinx_hcd``'s and ``sphinx_c4``'s own directive
modules, because a bridge between two viewpoints is not really part of
either one - it is likely to move out of this kit later, and a single
file is what makes that move easy.

Usage in conf.py, alongside both viewpoints::

    extensions = [
        "julee_viewpoints.sphinx_hcd",
        "julee_viewpoints.sphinx_c4",
        "julee_viewpoints.c4_bridge",
    ]

Note on scope
-------------
Upstream (``apps/sphinx/hcd/directives/c4_bridge.py``) also had a
``c4-container-diagram`` directive that built a container diagram from HCD
apps and accelerators via ``julee.hcd.use_cases.c4_bridge`` and
``julee.hcd.infrastructure.renderers.C4PlantUMLRenderer``. Neither module
exists in this version of ``julee`` - that use case and renderer were never
built for this codebase. ``sphinx_c4`` now provides its own, better
``container-diagram`` directive that reads real C4 containers and
relationships, so ``c4-container-diagram`` is not ported: its job is
superseded, not merely missing.
"""

from typing import TYPE_CHECKING, Any

from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from sphinx.application import Sphinx

    from julee_c4.domain.models.diagrams import PersonInfo
    from julee_viewpoints.sphinx_hcd.sphinx.context import HCDContext

logger = logging.getLogger(__name__)


class AppListByInterfacePlaceholder(nodes.General, nodes.Element):
    """Placeholder for app-list-by-interface, replaced at doctree-resolved."""

    pass


class AcceleratorListPlaceholder(nodes.General, nodes.Element):
    """Placeholder for accelerator-list, replaced at doctree-resolved."""

    pass


def _get_hcd_context(app: Any) -> "HCDContext | None":
    """The HCD context, if ``sphinx_hcd`` is loaded and has initialized one.

    Unlike ``sphinx_hcd.sphinx.context.get_hcd_context``, this never raises:
    the bridge extension can be loaded alongside a solution that only uses
    ``sphinx_c4``, and every directive here must degrade gracefully rather
    than fail the build when there is no HCD side to join.
    """
    context: HCDContext | None = getattr(app, "_hcd_context", None)
    return context


def enrich_persons_from_hcd(
    person_slugs: tuple[str, ...], app: Any
) -> tuple["PersonInfo", ...]:
    """Look up C4 person slugs against HCD's defined personas, for naming.

    A C4 relationship can name a person by slug alone (see
    ``julee_c4.domain.models.relationship``), which is enough to draw a box
    but not enough to write anything on it beyond the slug. When the HCD
    viewpoint is also loaded and has a ``define-persona`` for that slug,
    this returns the richer ``PersonInfo`` the C4 PlantUML serializer uses
    to render a proper name and description instead.

    Args:
        person_slugs: Person slugs referenced by a C4 diagram
        app: Sphinx application, for finding the HCD context

    Returns:
        A ``PersonInfo`` for each slug that matches a defined persona.
        Slugs with no matching persona are simply omitted - the C4
        serializer already falls back to rendering the bare slug for those.
    """
    from julee_c4.domain.models.diagrams import PersonInfo

    hcd_context = _get_hcd_context(app)
    if hcd_context is None or not person_slugs:
        return ()

    persons = []
    for slug in person_slugs:
        persona = hcd_context.persona_repo.get(slug)
        if persona is not None:
            persons.append(
                PersonInfo(
                    slug=persona.slug,
                    name=persona.name,
                    description=persona.context,
                )
            )
    return tuple(persons)


class AppListByInterfaceDirective(SphinxDirective):
    """List HCD apps grouped by interface type.

    Usage::

        .. app-list-by-interface::

    Generates a list of apps grouped by how they are reached - Sphinx
    extension, REST API, MCP server, and so on (see
    ``julee_hcd.domain.models.app.AppInterface``).
    """

    has_content = False

    def run(self) -> list[nodes.Node]:
        return [AppListByInterfacePlaceholder()]


class AcceleratorListDirective(SphinxDirective):
    """List HCD accelerators with their objectives.

    Usage::

        .. accelerator-list::
    """

    has_content = False

    def run(self) -> list[nodes.Node]:
        return [AcceleratorListPlaceholder()]


def build_app_list_by_interface(
    docname: str, hcd_context: "HCDContext"
) -> list[nodes.Node]:
    """Build a bullet list of apps, grouped by interface type."""
    from julee_hcd.domain.models.app import AppInterface
    from julee_viewpoints.shared import path_to_root

    all_apps = hcd_context.app_repo.list_all()
    prefix = path_to_root(docname)

    if not all_apps:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No apps defined")
        return [para]

    by_interface: dict[AppInterface, list[Any]] = {}
    for app in all_apps:
        by_interface.setdefault(app.interface, []).append(app)

    result_nodes: list[nodes.Node] = []

    for interface in sorted(by_interface, key=lambda i: i.value):
        apps = by_interface[interface]

        heading = nodes.paragraph()
        heading += nodes.strong(text=interface.value.upper())
        result_nodes.append(heading)

        bullet_list = nodes.bullet_list()
        for app in sorted(apps, key=lambda a: a.slug):
            item = nodes.list_item()
            item_para = nodes.paragraph()

            if app.docname:
                ref = nodes.reference("", "", refuri=f"{prefix}{app.docname}.html")
                ref += nodes.Text(app.name)
                item_para += ref
            else:
                item_para += nodes.Text(app.name)

            if app.description:
                first_sentence = app.description.split(".")[0]
                item_para += nodes.Text(f" - {first_sentence}")

            item += item_para
            bullet_list += item

        result_nodes.append(bullet_list)

    return result_nodes


def build_accelerator_list(docname: str, hcd_context: "HCDContext") -> list[nodes.Node]:
    """Build a simple bullet list of accelerators."""
    from julee_viewpoints.shared import path_to_root

    all_accelerators = hcd_context.accelerator_repo.list_all()
    prefix = path_to_root(docname)

    if not all_accelerators:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No accelerators defined")
        return [para]

    bullet_list = nodes.bullet_list()
    for accel in sorted(all_accelerators, key=lambda a: a.slug):
        item = nodes.list_item()
        item_para = nodes.paragraph()

        if accel.docname:
            ref = nodes.reference("", "", refuri=f"{prefix}{accel.docname}.html")
            ref += nodes.Text(accel.slug.replace("-", " ").title())
            item_para += ref
        else:
            item_para += nodes.Text(accel.slug.replace("-", " ").title())

        if accel.objective:
            first_sentence = accel.objective.split(".")[0]
            item_para += nodes.Text(f" - {first_sentence}")

        item += item_para
        bullet_list += item

    return [bullet_list]


def process_c4_bridge_placeholders(
    app: "Sphinx", doctree: nodes.document, docname: str
) -> None:
    """Replace this module's placeholders with rendered content.

    Runs at doctree-resolved, once every document has been read, since
    both placeholders list entities that may be defined anywhere in the
    build.
    """
    hcd_context = _get_hcd_context(app)
    if hcd_context is None:
        return

    for app_list_node in doctree.traverse(AppListByInterfacePlaceholder):
        app_list_content = build_app_list_by_interface(docname, hcd_context)
        app_list_node.replace_self(app_list_content)

    for accel_list_node in doctree.traverse(AcceleratorListPlaceholder):
        accel_list_content = build_accelerator_list(docname, hcd_context)
        accel_list_node.replace_self(accel_list_content)


def setup(app: "Sphinx") -> dict[str, Any]:
    """Register the HCD/C4 bridge directives.

    Load this alongside both ``julee_viewpoints.sphinx_hcd`` and
    ``julee_viewpoints.sphinx_c4``. It reads whichever contexts those
    extensions have created (via ``getattr``, not by creating its own),
    so load order with them does not matter.
    """
    app.add_directive("app-list-by-interface", AppListByInterfaceDirective)
    app.add_directive("accelerator-list", AcceleratorListDirective)
    app.add_node(AppListByInterfacePlaceholder)
    app.add_node(AcceleratorListPlaceholder)

    app.connect("doctree-resolved", process_c4_bridge_placeholders)

    logger.info("Loaded julee_viewpoints.c4_bridge extension")

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
