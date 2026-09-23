"""Contrib module directives for sphinx_hcd.

Provides directives for contrib modules (reusable utilities):
- define-contrib: Define a contrib module with metadata
- contrib-index: Generate index of contrib modules
- contrib-list: Generate bullet list of contrib modules
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.domain.repositories import ContribRepository

from ...utils import path_to_root
from .base import HCDDirective


class ContribIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder for contrib-index, replaced at doctree-resolved."""

    pass


class ContribListPlaceholder(nodes.General, nodes.Element):
    """Placeholder for contrib-list, replaced at doctree-resolved."""

    pass


class DefineContribDirective(HCDDirective):
    """Define a contrib module with metadata.

    Usage::

        .. define-contrib:: polling
           :name: Polling Workflow
           :technology: Python, Temporal
           :path: src/julee/contrib/polling/

           A reusable workflow for long-running polling operations.
    """

    required_arguments = 1
    has_content = True
    option_spec = {
        "name": directives.unchanged,
        "technology": directives.unchanged,
        "path": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        slug = self.arguments[0]
        docname = self.env.docname

        name = self.options.get("name", "").strip()
        technology = self.options.get("technology", "").strip() or "Python"
        code_path = self.options.get("path", "").strip()
        description = "\n".join(self.content).strip()

        contrib = ContribModule(
            slug=slug,
            name=name,
            description=description,
            technology=technology,
            code_path=code_path,
            docname=docname,
        )
        self.hcd_context.contrib_repo.save(contrib)

        return build_contrib_content(contrib)


class ContribIndexDirective(HCDDirective):
    """Generate index of contrib modules.

    Usage::

        .. contrib-index::
    """

    def run(self) -> list[nodes.Node]:
        return [ContribIndexPlaceholder()]


class ContribListDirective(HCDDirective):
    """Generate bullet list of contrib modules.

    Usage::

        .. contrib-list::
    """

    def run(self) -> list[nodes.Node]:
        return [ContribListPlaceholder()]


def build_contrib_content(contrib: ContribModule) -> list[nodes.Node]:
    """Build content nodes for a contrib module page.

    Only uses the contrib module's own data, so a directive can call this
    directly at parse time - no cross-document lookups are involved.
    """
    from sphinx.addnodes import seealso

    result_nodes: list[nodes.Node] = []

    if contrib.description:
        desc_para = nodes.paragraph()
        desc_para += nodes.Text(contrib.description)
        result_nodes.append(desc_para)

    seealso_node = seealso()

    if contrib.technology:
        tech_para = nodes.paragraph()
        tech_para += nodes.strong(text="Technology: ")
        tech_para += nodes.Text(contrib.technology)
        seealso_node += tech_para

    if contrib.code_path:
        path_para = nodes.paragraph()
        path_para += nodes.strong(text="Code: ")
        path_para += nodes.literal(text=contrib.code_path)
        seealso_node += path_para

    result_nodes.append(seealso_node)
    return result_nodes


def build_contrib_index(docname: str, hcd_context) -> list[nodes.Node]:
    """Build contrib module index."""
    all_contribs = hcd_context.contrib_repo.list_all()

    if not all_contribs:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No contrib modules defined")
        return [para]

    contrib_list = nodes.bullet_list()

    for contrib in sorted(all_contribs, key=lambda c: c.slug):
        item = nodes.list_item()
        para = nodes.paragraph()

        contrib_path = f"{contrib.slug}.html"
        ref = nodes.reference("", "", refuri=contrib_path)
        ref += nodes.Text(contrib.display_title)
        para += ref

        if contrib.description:
            first_sentence = contrib.description.split(".")[0]
            para += nodes.Text(f" - {first_sentence}")

        item += para
        contrib_list += item

    return [contrib_list]


def build_contrib_list(docname: str, hcd_context) -> list[nodes.Node]:
    """Build simple bullet list of contrib modules."""
    prefix = path_to_root(docname)
    all_contribs = hcd_context.contrib_repo.list_all()

    if not all_contribs:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No contrib modules defined")
        return [para]

    bullet_list = nodes.bullet_list()

    for contrib in sorted(all_contribs, key=lambda c: c.slug):
        item = nodes.list_item()
        item_para = nodes.paragraph()

        if contrib.docname:
            ref = nodes.reference("", "", refuri=f"{prefix}{contrib.docname}.html")
            ref += nodes.Text(contrib.display_title)
            item_para += ref
        else:
            item_para += nodes.Text(contrib.display_title)

        if contrib.description:
            first_sentence = contrib.description.split(".")[0]
            item_para += nodes.Text(f" - {first_sentence}")

        item += item_para
        bullet_list += item

    return [bullet_list]


def clear_contrib_state(app, env, docname):
    """Clear contrib state when a document is re-read."""
    from ..context import get_hcd_context

    hcd_context = get_hcd_context(app)
    async_repo = hcd_context.contrib_repo.async_repo
    assert isinstance(async_repo, ContribRepository)
    hcd_context.contrib_repo.run_async(async_repo.clear_by_docname(docname))


def process_contrib_placeholders(app, doctree, docname):
    """Replace contrib placeholders with rendered content."""
    from ..context import get_hcd_context

    hcd_context = get_hcd_context(app)

    for node in doctree.traverse(ContribIndexPlaceholder):
        content = build_contrib_index(docname, hcd_context)
        node.replace_self(content)

    for node in doctree.traverse(ContribListPlaceholder):
        content = build_contrib_list(docname, hcd_context)
        node.replace_self(content)
