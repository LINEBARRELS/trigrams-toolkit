"""One dependency model for validation, eligibility and state transitions."""

from __future__ import annotations

from dataclasses import dataclass
import heapq

from trigrams_toolkit.shared.errors import require
from .model import JsonObject, PlanDefinition, PlanError, Status, TaskDefinition


@dataclass(frozen=True)
class Schedule:
    predecessors: dict[str, set[str]]
    producers: dict[str, tuple[str, str]]
    order: tuple[str, ...]


def _cycle(graph: dict[str, set[str]], unresolved: set[str]) -> list[str]:
    # Follow predecessor links; reverse the result to report execution direction.
    path: list[str] = []
    positions: dict[str, int] = {}
    current = min(unresolved)
    while current not in positions:
        positions[current] = len(path)
        path.append(current)
        current = min(graph[current] & unresolved)
    return list(reversed([*path[positions[current]:], current]))


def _order(graph: dict[str, set[str]]) -> tuple[str, ...]:
    successors: dict[str, list[str]] = {identity: [] for identity in graph}
    indegrees = {identity: len(dependencies) for identity, dependencies in graph.items()}
    for identity, dependencies in graph.items():
        for predecessor in dependencies:
            successors[predecessor].append(identity)
    ready = [identity for identity, degree in indegrees.items() if degree == 0]
    heapq.heapify(ready)
    ordered = []
    while ready:
        identity = heapq.heappop(ready)
        ordered.append(identity)
        for successor in successors[identity]:
            indegrees[successor] -= 1
            if indegrees[successor] == 0:
                heapq.heappush(ready, successor)
    unresolved = set(graph) - set(ordered)
    if unresolved:
        chain = _cycle(graph, unresolved)
        raise PlanError("dependency_cycle", "Dependency cycle: " + " -> ".join(chain), [{"chain": chain}])
    return tuple(ordered)


def build_schedule(definition: PlanDefinition) -> Schedule:
    graph = {task.identity: set(task.dependencies) for task in definition.tasks}
    stub_ids = {stub.identity for stub in definition.stubs}
    for task in definition.tasks:
        missing = set(task.dependencies) - graph.keys()
        require(not missing, "invalid_dependency", f"{task.identity} references missing Tasks: {sorted(missing)}")
        unknown = set((*task.installs, *task.fills, *task.uses)) - stub_ids
        require(not unknown, "invalid_stub", f"{task.identity} references missing Stubs: {sorted(unknown)}")
    producers = {}
    for stub in definition.stubs:
        installers = [task.identity for task in definition.tasks if stub.identity in task.installs]
        fillers = [task.identity for task in definition.tasks if stub.identity in task.fills]
        require(len(installers) == len(fillers) == 1, "invalid_stub",
                f"{stub.identity} requires exactly one installer and one filler; installs={installers}, fills={fillers}.")
        require(installers[0] != fillers[0], "invalid_stub", f"{stub.identity} must be installed and filled by different Tasks.")
        producers[stub.identity] = installers[0], fillers[0]
    for task in definition.tasks:
        graph[task.identity].update(producers[identity][0] for identity in (*task.fills, *task.uses))
    return Schedule(graph, producers, _order(graph))


def stub_states(schedule: Schedule, tasks: JsonObject) -> dict[str, str]:
    result = {}
    for identity, (installer, filler) in schedule.producers.items():
        status = "uninstalled"
        if tasks[installer]["status"] == Status.DONE:
            status = "filled" if tasks[filler]["status"] == Status.DONE else "installed"
        result[identity] = status
    return result


def blockers(task: TaskDefinition, state: JsonObject) -> list[JsonObject]:
    result = [{"type": "task", "id": identity, "required": "done"}
              for identity in task.dependencies if state["tasks"][identity]["status"] != Status.DONE]
    for identity in sorted(set((*task.fills, *task.uses))):
        if state["stubs"][identity]["status"] == "uninstalled":
            result.append({"type": "stub", "id": identity, "required": "installed"})
    return result


def validate_current(definition: PlanDefinition, state: JsonObject) -> None:
    issues = []
    for task in definition.tasks:
        if state["tasks"][task.identity]["status"] not in (Status.DOING, Status.DONE):
            continue
        unmet = blockers(task, state)
        if unmet:
            issues.append({"task": task.identity, "blockers": unmet})
    if issues:
        raise PlanError("invalid_progress", "Active or completed Tasks have unmet prerequisites.", issues)
    if state["status"] == Status.DONE:
        unfinished = [identity for identity, record in state["tasks"].items()
                      if record["status"] not in (Status.DONE, Status.CANCELLED)]
        unfilled = [identity for identity, record in state["stubs"].items() if record["status"] != "filled"]
        require(not unfinished and not unfilled, "not_ready", f"Plan has unfinished Tasks {unfinished} or Stubs {unfilled}.")


def validate_completion(schedule: Schedule, state: JsonObject) -> None:
    reachable: set[str] = set()
    issues = []
    for identity in schedule.order:
        if state["tasks"][identity]["status"] == Status.CANCELLED:
            continue
        unmet = schedule.predecessors[identity] - reachable
        if unmet:
            issues.append({"task": identity, "unreachablePredecessors": sorted(unmet)})
        else:
            reachable.add(identity)
    for identity, producers in schedule.producers.items():
        if not set(producers) <= reachable:
            issues.append({"stub": identity, "unreachableProducers": sorted(set(producers) - reachable)})
    if issues:
        raise PlanError("unreachable_plan", "Cancelled prerequisites prevent this Plan from completing.", issues)
