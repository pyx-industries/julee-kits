#!/bin/sh
# Regenerate the CRUD use cases (ADR 008). Run from the kit directory:
#   sh generate-crud.sh
#
# The output is committed, unlike a solution's, because a kit ships as a
# wheel: what is not in the repository is not in the distribution.
#
# The create fields mirror each entity's own fields, defaults included, so a
# caller may name only what it knows. The slug is among them because a C4
# element is identified by a slug read off its name, not by a key the
# repository mints. The update fields are the same list without the slug;
# the generator makes them optional itself.
# --delete emits the fifth use case. It is opt-in in julee because two
# of the five kits must never delete; these entities are documentation,
# and documentation that cannot forget goes stale.
set -e
out=src/julee_c4/usecases
gen() {
  uv run python -m julee.core.usecases.generate_crud \
    --entity "$1" --entity-module "julee_c4.domain.models.$2" \
    --repo "$1Repository" --repo-module "julee_c4.domain.repositories.$2" \
    --id-field slug --out "$out" --delete \
    --create-fields "$3" --update-fields "$4"
}

gen SoftwareSystem software_system \
  'slug:str name:str description:str="" system_type:SystemType=SystemType.INTERNAL owner:str="" technology:str="" url:str="" tags:tuple[str,...]=() docname:str=""' \
  'name:str description:str system_type:SystemType owner:str technology:str url:str tags:tuple[str,...] docname:str'

gen Container container \
  'slug:str name:str system_slug:str description:str="" container_type:ContainerType=ContainerType.OTHER technology:str="" url:str="" tags:tuple[str,...]=() docname:str=""' \
  'name:str system_slug:str description:str container_type:ContainerType technology:str url:str tags:tuple[str,...] docname:str'

gen Component component \
  'slug:str name:str container_slug:str system_slug:str description:str="" technology:str="" interface:str="" code_path:str="" tags:tuple[str,...]=() docname:str=""' \
  'name:str container_slug:str system_slug:str description:str technology:str interface:str code_path:str tags:tuple[str,...] docname:str'

gen Relationship relationship \
  'slug:str="" source_type:ElementType source_slug:str destination_type:ElementType destination_slug:str description:str="Uses" technology:str="" tags:tuple[str,...]=() bidirectional:bool=False docname:str=""' \
  'source_type:ElementType source_slug:str destination_type:ElementType destination_slug:str description:str technology:str tags:tuple[str,...] bidirectional:bool docname:str'

gen DeploymentNode deployment_node \
  'slug:str name:str environment:str="production" node_type:NodeType=NodeType.OTHER description:str="" technology:str="" instances:int=1 parent_slug:str|None=None tags:tuple[str,...]=() docname:str=""' \
  'name:str environment:str node_type:NodeType description:str technology:str instances:int parent_slug:str|None tags:tuple[str,...] docname:str'

gen DynamicStep dynamic_step \
  'slug:str="" sequence_name:str step_number:int source_type:ElementType source_slug:str destination_type:ElementType destination_slug:str description:str="" technology:str="" return_value:str="" is_async:bool=False tags:tuple[str,...]=() docname:str=""' \
  'sequence_name:str step_number:int source_type:ElementType source_slug:str destination_type:ElementType destination_slug:str description:str technology:str return_value:str is_async:bool tags:tuple[str,...] docname:str'
