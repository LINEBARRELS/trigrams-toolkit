"""Identity, ownership and extra-relation graph invariants."""
from __future__ import annotations

from typing import Any
from trigrams_toolkit.shared.errors import require
from .model import Artifact, Edge, Entity, RegistryState, all_entities, entity_kind
from .providers import Types


def validate_ownership(state: RegistryState, artifact: Artifact) -> None:
    module = artifact.get("moduleId")
    require(module is None or any(m["id"] == module for m in state["modules"]), "invalid_reference", f"Unknown moduleId in {artifact['id']}: {module}")
    features = artifact["featureIds"]
    require(not features or module is not None, "invalid_reference", f"featureIds in {artifact['id']} require moduleId.")
    require(len(set(features)) == len(features), "invalid_reference", f"Duplicate featureIds in {artifact['id']}.")
    for identity in features:
        require(any(f["id"] == identity and f["moduleId"] == module for f in state["features"]),
                "invalid_reference", f"Feature {identity} does not belong to {module}.")


def validate_identity_graph(state: RegistryState) -> None:
    entities = all_entities(state)
    ids = {e["id"] for e in entities}
    require(len(ids) == len(entities), "identity_conflict", "Duplicate Registry identity.")
    for feature in state["features"]:
        require(any(m["id"] == feature["moduleId"] for m in state["modules"]), "invalid_reference", f"Unknown Module: {feature['moduleId']}")
    for artifact in state["artifacts"]:
        validate_ownership(state, artifact)
    edges = state["relations"]
    require(len({(e["kind"], e["from"], e["to"]) for e in edges}) == len(edges), "invalid_reference", "Duplicate relation.")
    for edge in edges:
        require(edge["from"] in ids and edge["to"] in ids and edge["from"] != edge["to"], "invalid_reference", "Invalid relation endpoints.")


def _rule(edge: Edge, entities: dict[str, Entity], types: Types) -> dict[str, Any]:
    source, target = entities.get(edge["from"]), entities.get(edge["to"])
    require(source is not None and target is not None and source["id"] != target["id"], "invalid_reference", "Relation endpoints must be distinct registered entities.")
    assert source is not None and target is not None
    if edge["kind"] in types.same_artifact_kind:
        require("kind" in source and "kind" in target and entity_kind(source) == entity_kind(target),
                "invalid_reference", "supersedes requires Artifacts of the same kind.")
        return {"maxOutgoing": None, "maxIncoming": None, "acyclic": True}
    rule = types.relations.get(edge["kind"])
    require(rule is not None, "missing_capability", f"No package declares relation {edge['kind']}.")
    assert rule is not None
    require(entity_kind(source) in rule["fromKinds"] and entity_kind(target) in rule["toKinds"], "invalid_reference", f"Endpoint kinds differ for {edge['kind']}.")
    return rule


def _no_cycles(edges: list[Edge]) -> None:
    # Kahn's algorithm also handles graphs deeper than Python's recursion limit.
    neighbors: dict[str, list[str]] = {}
    degrees: dict[str, int] = {}
    for edge in edges:
        neighbors.setdefault(edge["from"], []).append(edge["to"])
        degrees.setdefault(edge["from"], 0)
        degrees[edge["to"]] = degrees.get(edge["to"], 0) + 1
    ready = [key for key, count in degrees.items() if count == 0]
    visited = 0
    while ready:
        current = ready.pop()
        visited += 1
        for target in neighbors.get(current, []):
            degrees[target] -= 1
            if degrees[target] == 0:
                ready.append(target)
    require(visited == len(degrees), "invalid_reference", "Relation graph contains a cycle.")


def validate_relations(state: RegistryState, types: Types) -> None:
    entities = {e["id"]: e for e in all_entities(state)}
    for kind in dict.fromkeys(e["kind"] for e in state["relations"]):
        edges = [e for e in state["relations"] if e["kind"] == kind]
        for edge in edges:
            rule = _rule(edge, entities, types)
            for direction, limit in (("from", "maxOutgoing"), ("to", "maxIncoming")):
                require(rule[limit] is None or sum(dict(e)[direction] == dict(edge)[direction] for e in edges) <= rule[limit],
                        "invalid_reference", f"Cardinality exceeded: {kind}")
        if rule["acyclic"]:
            _no_cycles(edges)


def change_relation(state: RegistryState, edge: Edge, remove: bool, types: Types) -> bool:
    require(edge["kind"] not in ("core:feature-module", "core:module-spec", "core:feature-spec"), "invalid_arguments",
            "Use register feature --module or register artifact --module/--feature to maintain ownership.")
    _rule(edge, {e["id"]: e for e in all_entities(state)}, types)
    exists = edge in state["relations"]
    if exists == (not remove):
        return False
    if remove:
        state["relations"].remove(edge)
    else:
        state["relations"].append(edge)
    validate_relations(state, types)
    return True


def effective_relations(state: RegistryState) -> list[dict[str, str]]:
    result: list[dict[str, str]] = [{"kind": e["kind"], "from": e["from"], "to": e["to"], "source": "relation"} for e in state["relations"]]
    result.extend({"kind": "core:feature-module", "from": f["id"], "to": f["moduleId"], "source": "feature"} for f in state["features"])
    for artifact in state["artifacts"]:
        if "moduleId" in artifact:
            result.append({"kind": "core:module-spec", "from": artifact["moduleId"], "to": artifact["id"], "source": "document"})
        result.extend({"kind": "core:feature-spec", "from": f, "to": artifact["id"], "source": "document"} for f in artifact["featureIds"])
    return result
