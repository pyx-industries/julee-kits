#!/bin/sh
# Regenerate the CRUD use cases (ADR 008). Run from the kit directory:
#   sh generate-crud.sh
#
# The output is committed, unlike a solution's, because a kit ships as a
# wheel: what is not in the repository is not in the distribution.
#
# Create fields mirror each entity's own fields, defaults included, so a
# caller may name only what it knows. The slug is among them because an
# HCD entity is identified by a slug read off its name, not by a key the
# repository mints. Update fields are the same list without the slug; the
# generator makes them optional itself.
#
# Derived fields are left out: name_normalized, persona_normalized and
# app_normalized are computed from the fields beside them, so accepting
# them on the way in would let a caller contradict the entity.
# --delete emits the fifth use case. It is opt-in in julee because two
# of the five kits must never delete; these entities are documentation,
# and documentation that cannot forget goes stale.
set -e
out=src/julee_hcd/usecases

# Every authored entity carries these; see domain/models/base.py.
authored='solution_slug:str="" docname:str="" page_title:str="" preamble_rst:str="" epilogue_rst:str=""'

# $6 is the plural: inflect makes "personae" of a persona, and the
# generated names are this kit's public API.
gen() {
  uv run python -m julee.core.usecases.generate_crud \
    --entity "$1" --entity-module "julee_hcd.domain.models.$2" \
    --repo "$3" --repo-module "julee_hcd.domain.repositories.$2" \
    --id-field slug --plural "$6" --out "$out" --delete \
    --create-fields "$4 $authored" --update-fields "$5 $authored"
}

gen App app AppRepository \
  'slug:str name:str app_type:AppType=AppType.UNKNOWN status:str|None=None description:str="" interface:AppInterface=AppInterface.UNKNOWN technology:str="" accelerators:tuple[str,...]=() manifest_path:str=""' \
  'name:str app_type:AppType status:str|None description:str interface:AppInterface technology:str accelerators:tuple[str,...] manifest_path:str' \
  'Apps'

gen ContribModule contrib ContribRepository \
  'slug:str name:str="" description:str="" technology:str="Python" code_path:str=""' \
  'name:str description:str technology:str code_path:str' \
  'ContribModules'

gen Epic epic EpicRepository \
  'slug:str description:str="" story_refs:tuple[str,...]=()' \
  'description:str story_refs:tuple[str,...]' \
  'Epics'

gen Integration integration IntegrationRepository \
  'slug:str module:str name:str description:str="" direction:Direction=Direction.BIDIRECTIONAL depends_on:tuple[ExternalDependency,...]=() manifest_path:str=""' \
  'module:str name:str description:str direction:Direction depends_on:tuple[ExternalDependency,...] manifest_path:str' \
  'Integrations'

gen Journey journey JourneyRepository \
  'slug:str persona:str="" intent:str="" outcome:str="" goal:str="" depends_on:tuple[str,...]=() steps:tuple[JourneyStep,...]=() preconditions:tuple[str,...]=() postconditions:tuple[str,...]=()' \
  'persona:str intent:str outcome:str goal:str depends_on:tuple[str,...] steps:tuple[JourneyStep,...] preconditions:tuple[str,...] postconditions:tuple[str,...]' \
  'Journeys'

# A persona's slug comes off its name, so creating one need not give it.
gen Persona persona PersonaRepository \
  'slug:str="" name:str goals:tuple[str,...]=() frustrations:tuple[str,...]=() jobs_to_be_done:tuple[str,...]=() context:str="" app_slugs:tuple[str,...]=() epic_slugs:tuple[str,...]=() accelerator_slugs:tuple[str,...]=() contrib_slugs:tuple[str,...]=()' \
  'name:str goals:tuple[str,...] frustrations:tuple[str,...] jobs_to_be_done:tuple[str,...] context:str app_slugs:tuple[str,...] epic_slugs:tuple[str,...] accelerator_slugs:tuple[str,...] contrib_slugs:tuple[str,...]' \
  'Personas'

# i_want and so_that are required here although the entity defaults them:
# the defaults are placeholders for a story read out of a feature file
# that said nothing, not something a caller should be able to leave out.
gen Story story StoryRepository \
  'slug:str feature_title:str persona:str i_want:str so_that:str app_slug:str file_path:str abs_path:str="" gherkin_snippet:str=""' \
  'feature_title:str persona:str i_want:str so_that:str app_slug:str file_path:str abs_path:str gherkin_snippet:str' \
  'Stories'
