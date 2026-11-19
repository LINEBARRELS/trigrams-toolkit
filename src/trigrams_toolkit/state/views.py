"""Public projections of Registry entities and located documents."""
from pathlib import Path
from typing import Literal, NotRequired, TypedDict, cast

from .location import artifact_location
from .model import Artifact, Entity, Feature, Module, RegistryState


class ModuleView(TypedDict):
    id: str
    kind: Literal["core:module"]
    name: str


class FeatureView(TypedDict):
    id: str
    kind: Literal["core:feature"]
    name: str
    moduleId: str


class ArtifactView(TypedDict):
    id: str
    kind: str
    title: str
    moduleId: NotRequired[str]
    featureIds: list[str]


class LocatedArtifactView(ArtifactView):
    path: str


EntityView = ModuleView | FeatureView | ArtifactView
LocateResult = ModuleView | FeatureView | LocatedArtifactView


def _artifact_view(artifact: Artifact) -> ArtifactView:
    view: ArtifactView = {"id": artifact["id"], "kind": artifact["kind"], "title": artifact["title"],
                          "featureIds": list(artifact["featureIds"])}
    if "moduleId" in artifact:
        view["moduleId"] = artifact["moduleId"]
    return view


def _named_view(entity: Module | Feature) -> ModuleView | FeatureView:
    if "moduleId" in entity:
        feature = cast(Feature, entity)
        return {"id": feature["id"], "kind": "core:feature", "name": feature["name"], "moduleId": feature["moduleId"]}
    return {"id": entity["id"], "kind": "core:module", "name": entity["name"]}


def entity_view(entity: Entity) -> EntityView:
    if "kind" in entity:
        return _artifact_view(cast(Artifact, entity))
    return _named_view(entity)


def located_entity_view(project_root: Path, state: RegistryState, entity: Entity) -> LocateResult:
    if "kind" in entity:
        artifact = cast(Artifact, entity)
        location = artifact_location(project_root, state, artifact)
        return {**_artifact_view(artifact), "path": str(location)}
    return _named_view(entity)
