"""Dynamic step directive for sphinx_c4.

Provides the ``define-dynamic-step`` directive, which records a numbered
step of a dynamic (sequence) diagram and renders it inline as a one-line
summary where it is defined.

Note: unlike Relationship, the ``DynamicStep`` model has no ``tags`` field,
so this directive has no ``:tags:`` option either.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.models.dynamic_step import DynamicStep

from .base import C4Directive, parse_element_ref


class DefineDynamicStepDirective(C4Directive):
    """Define a step in a dynamic sequence diagram.

    Usage::

        .. define-dynamic-step::
           :sequence: user-login
           :step: 1
           :from: person:customer
           :to: container:web-app
           :description: Submits login credentials
           :technology: HTTPS

        .. define-dynamic-step::
           :sequence: user-login
           :step: 2
           :from: container:web-app
           :to: container:api-app
           :description: Validates credentials
           :technology: REST/JSON
    """

    has_content = False
    option_spec = {
        "sequence": directives.unchanged_required,
        "step": directives.positive_int,
        "from": directives.unchanged_required,
        "to": directives.unchanged_required,
        "description": directives.unchanged,
        "technology": directives.unchanged,
        "return": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        sequence_name = self.options.get("sequence", "")
        step_number = self.options.get("step", 1)
        from_ref = self.options.get("from", "")
        to_ref = self.options.get("to", "")
        description = self.options.get("description", "")
        technology = self.options.get("technology", "")
        return_value = self.options.get("return", "")

        source_type, source_slug = parse_element_ref(from_ref)
        dest_type, dest_slug = parse_element_ref(to_ref)

        # Slug is left blank - DynamicStep derives it from sequence + step.
        step = DynamicStep(
            sequence_name=sequence_name,
            step_number=step_number,
            source_type=source_type,
            source_slug=source_slug,
            destination_type=dest_type,
            destination_slug=dest_slug,
            description=description,
            technology=technology,
            return_value=return_value,
            docname=self.docname,
        )
        self.c4_context.dynamic_step_repo.save(step)

        result_nodes: list[nodes.Node] = []

        para = nodes.paragraph()
        para += nodes.strong(text=f"Step {step_number}: ")
        para += nodes.Text(f"{source_slug} -> {dest_slug}")
        if description:
            para += nodes.Text(f": {description}")
        if technology:
            para += nodes.Text(f" [{technology}]")

        result_nodes.append(para)
        return result_nodes
