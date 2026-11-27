"""Deterministic Axiomatic Design matrix solver (reordering, SCC cycles, Theorem 1)."""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
import sys
from typing import Final, Literal, TypedDict

__all__ = [
    "AuditClassification",
    "EdgeKind",
    "SolverMode",
    "analyze_design_matrix",
    "format_markdown_report",
    "main",
]

VALID_SCOPES: Final[frozenset[str]] = frozenset({"layer", "module", "feature", "ad-hoc"})
VALID_FR_STATUS: Final[frozenset[str]] = frozenset({"present", "phantom"})
VALID_DP_STATUS: Final[frozenset[str]] = frozenset({"present", "wild"})
VALID_DP_ROLES: Final[frozenset[str]] = frozenset({"business", "arch"})


class SolverMode(StrEnum):
    PAIRED = "paired"
    BIPARTITE = "bipartite"


class EdgeKind(StrEnum):
    EXPLICIT = "D"
    CHANGE_COUPLING = "C"


class AuditClassification(StrEnum):
    UNCOUPLED = "uncoupled"
    DECOUPLED = "decoupled"
    COUPLED = "coupled"


class FRInput(TypedDict, total=False):
    id: str
    name: str
    ard_ref: str
    status: str


class DPInput(TypedDict, total=False):
    id: str
    name: str
    paths: list[str]
    role: str
    status: str


class PairInput(TypedDict):
    fr: str
    dp: str


class EdgeInput(TypedDict, total=False):
    fr: str
    dp: str
    kind: str
    evidence: str
    note: str


@dataclass(frozen=True)
class FRNode:
    id: str
    name: str
    ard_ref: str
    status: Literal["present", "phantom"]


@dataclass(frozen=True)
class DPNode:
    id: str
    name: str
    paths: tuple[str, ...]
    role: Literal["business", "arch"]
    status: Literal["present", "wild"]


@dataclass(frozen=True)
class MatrixEdge:
    fr: str
    dp: str
    kind: EdgeKind
    evidence: str
    note: str


@dataclass(frozen=True)
class ParsedMatrix:
    scope: str
    title: str
    mode: SolverMode
    frs: tuple[FRNode, ...]
    dps: tuple[DPNode, ...]
    pairs: tuple[tuple[str, str], ...]
    edges: tuple[MatrixEdge, ...]


def _require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _parse_frs(raw_frs: object) -> tuple[FRNode, ...]:
    if not isinstance(raw_frs, list) or not raw_frs:
        raise ValueError("frs must be a non-empty list.")
    seen: set[str] = set()
    nodes: list[FRNode] = []
    for idx, item in enumerate(raw_frs):
        if not isinstance(item, dict):
            raise ValueError(f"frs[{idx}] must be an object.")
        fr_id = _require_non_empty_str(item.get("id"), f"frs[{idx}].id")
        if fr_id in seen:
            raise ValueError(f"Duplicate FR id: {fr_id}")
        seen.add(fr_id)
        name = _require_non_empty_str(item.get("name", fr_id), f"frs[{idx}].name")
        ard_ref = str(item.get("ard_ref", "")).strip()
        status_raw = str(item.get("status", "present")).strip()
        if status_raw not in VALID_FR_STATUS:
            raise ValueError(f"frs[{idx}].status must be one of {sorted(VALID_FR_STATUS)}, got {status_raw!r}.")
        status: Literal["present", "phantom"] = "phantom" if status_raw == "phantom" else "present"
        nodes.append(FRNode(id=fr_id, name=name, ard_ref=ard_ref, status=status))
    return tuple(nodes)


def _parse_dps(raw_dps: object) -> tuple[DPNode, ...]:
    if not isinstance(raw_dps, list) or not raw_dps:
        raise ValueError("dps must be a non-empty list.")
    seen: set[str] = set()
    nodes: list[DPNode] = []
    for idx, item in enumerate(raw_dps):
        if not isinstance(item, dict):
            raise ValueError(f"dps[{idx}] must be an object.")
        dp_id = _require_non_empty_str(item.get("id"), f"dps[{idx}].id")
        if dp_id in seen:
            raise ValueError(f"Duplicate DP id: {dp_id}")
        seen.add(dp_id)
        name = _require_non_empty_str(item.get("name", dp_id), f"dps[{idx}].name")
        raw_paths = item.get("paths", [])
        if not isinstance(raw_paths, list) or not all(isinstance(p, str) for p in raw_paths):
            raise ValueError(f"dps[{idx}].paths must be a list of strings.")
        role_raw = str(item.get("role", "business")).strip()
        if role_raw not in VALID_DP_ROLES:
            raise ValueError(f"dps[{idx}].role must be one of {sorted(VALID_DP_ROLES)}, got {role_raw!r}.")
        role: Literal["business", "arch"] = "arch" if role_raw == "arch" else "business"
        status_raw = str(item.get("status", "present")).strip()
        if status_raw not in VALID_DP_STATUS:
            raise ValueError(f"dps[{idx}].status must be one of {sorted(VALID_DP_STATUS)}, got {status_raw!r}.")
        status: Literal["present", "wild"] = "wild" if status_raw == "wild" else "present"
        nodes.append(DPNode(id=dp_id, name=name, paths=tuple(raw_paths), role=role, status=status))
    return tuple(nodes)


def _parse_edges(raw_edges: object, fr_ids: set[str], dp_ids: set[str]) -> tuple[MatrixEdge, ...]:
    if not isinstance(raw_edges, list):
        raise ValueError("edges must be a list.")
    edges: list[MatrixEdge] = []
    for idx, item in enumerate(raw_edges):
        if not isinstance(item, dict):
            raise ValueError(f"edges[{idx}] must be an object.")
        fr_id = _require_non_empty_str(item.get("fr"), f"edges[{idx}].fr")
        dp_id = _require_non_empty_str(item.get("dp"), f"edges[{idx}].dp")
        if fr_id not in fr_ids:
            raise ValueError(f"edges[{idx}].fr references unknown FR id {fr_id!r}.")
        if dp_id not in dp_ids:
            raise ValueError(f"edges[{idx}].dp references unknown DP id {dp_id!r}.")
        kind_raw = _require_non_empty_str(item.get("kind"), f"edges[{idx}].kind")
        try:
            kind = EdgeKind(kind_raw)
        except ValueError as err:
            raise ValueError(f"edges[{idx}].kind must be 'D' or 'C', got {kind_raw!r}.") from err
        evidence = _require_non_empty_str(item.get("evidence"), f"edges[{idx}].evidence")
        note = str(item.get("note", "")).strip()
        edges.append(MatrixEdge(fr=fr_id, dp=dp_id, kind=kind, evidence=evidence, note=note))
    return tuple(edges)


def _resolve_mode_and_pairs(
    raw_mode: object,
    raw_pairs: object,
    frs: tuple[FRNode, ...],
    dps: tuple[DPNode, ...],
) -> tuple[SolverMode, tuple[tuple[str, str], ...]]:
    active_frs = [node for node in frs if node.status == "present"]
    present_dps = [node for node in dps if node.status == "present"]
    active_fr_ids = {node.id for node in active_frs}
    all_dp_ids = {node.id for node in dps}

    explicit_pairs: list[tuple[str, str]] = []
    if raw_pairs is not None:
        if not isinstance(raw_pairs, list):
            raise ValueError("pairs must be a list when provided.")
        seen_fr: set[str] = set()
        seen_dp: set[str] = set()
        for idx, item in enumerate(raw_pairs):
            if not isinstance(item, dict):
                raise ValueError(f"pairs[{idx}] must be an object.")
            fr_id = _require_non_empty_str(item.get("fr"), f"pairs[{idx}].fr")
            dp_id = _require_non_empty_str(item.get("dp"), f"pairs[{idx}].dp")
            if fr_id not in active_fr_ids:
                raise ValueError(f"pairs[{idx}].fr must reference an active (present) FR, got {fr_id!r}.")
            if dp_id not in all_dp_ids:
                raise ValueError(f"pairs[{idx}].dp references unknown DP {dp_id!r}.")
            if fr_id in seen_fr or dp_id in seen_dp:
                raise ValueError(f"pairs[{idx}] duplicates an already paired FR or DP.")
            seen_fr.add(fr_id)
            seen_dp.add(dp_id)
            explicit_pairs.append((fr_id, dp_id))

    if raw_mode is None:
        if explicit_pairs and len(explicit_pairs) == len(active_frs):
            mode = SolverMode.PAIRED
        elif not explicit_pairs and len(active_frs) == len(present_dps) and active_frs:
            mode = SolverMode.PAIRED
        else:
            mode = SolverMode.BIPARTITE
    else:
        mode_str = _require_non_empty_str(raw_mode, "mode")
        try:
            mode = SolverMode(mode_str)
        except ValueError as err:
            raise ValueError(f"mode must be 'paired' or 'bipartite', got {mode_str!r}.") from err

    if mode is SolverMode.PAIRED:
        if explicit_pairs:
            if len(explicit_pairs) != len(active_frs):
                raise ValueError("paired mode requires one pair for every active (present) FR.")
            return mode, tuple(explicit_pairs)
        if len(active_frs) != len(present_dps):
            raise ValueError(
                f"paired mode without explicit pairs requires equal counts of active FRs ({len(active_frs)}) "
                f"and present DPs ({len(present_dps)})."
            )
        inferred = tuple((fr.id, dp.id) for fr, dp in zip(active_frs, present_dps, strict=True))
        return mode, inferred

    return mode, tuple(explicit_pairs)


def _parse_input(payload: dict[str, object]) -> ParsedMatrix:
    if not isinstance(payload, dict):
        raise ValueError("Input JSON root must be an object.")
    scope = _require_non_empty_str(payload.get("scope", "module"), "scope")
    if scope not in VALID_SCOPES:
        raise ValueError(f"scope must be one of {sorted(VALID_SCOPES)}, got {scope!r}.")
    title = str(payload.get("title", "")).strip() or f"Axiomatic Design Audit ({scope})"
    frs = _parse_frs(payload.get("frs"))
    dps = _parse_dps(payload.get("dps"))
    fr_ids = {node.id for node in frs}
    dp_ids = {node.id for node in dps}
    edges = _parse_edges(payload.get("edges", []), fr_ids, dp_ids)
    mode, pairs = _resolve_mode_and_pairs(payload.get("mode"), payload.get("pairs"), frs, dps)
    return ParsedMatrix(scope=scope, title=title, mode=mode, frs=frs, dps=dps, pairs=pairs, edges=edges)


def _tarjan_scc(nodes: list[str], adjacency: dict[str, set[str]]) -> list[list[str]]:
    """Return strongly connected components in reverse topological order of finish."""
    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []
    order_pos = {node: pos for pos, node in enumerate(nodes)}

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in sorted(adjacency.get(node, ()), key=lambda item: order_pos[item]):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlink[node] = min(lowlink[node], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node] = min(lowlink[node], indices[neighbor])

        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                popped = stack.pop()
                on_stack.remove(popped)
                component.append(popped)
                if popped == node:
                    break
            component.sort(key=lambda item: order_pos[item])
            components.append(component)

    for node in nodes:
        if node not in indices:
            strongconnect(node)
    return components


def _condensation_order(
    nodes: list[str],
    precedence_edges: dict[str, set[str]],
) -> tuple[list[str], list[list[str]]]:
    """Order nodes so foundation predecessors come earlier; return (ordered_nodes, cyclic_sccs).

    precedence_edges[v] contains u meaning v must precede u (u depends on v),
    which places dependency (u, v) in the lower triangle (row(u) > col(v)).
    """
    order_pos = {node: pos for pos, node in enumerate(nodes)}
    sccs = _tarjan_scc(nodes, precedence_edges)
    comp_id: dict[str, int] = {}
    for cid, comp in enumerate(sccs):
        for node in comp:
            comp_id[node] = cid

    comp_adj: dict[int, set[int]] = {cid: set() for cid in range(len(sccs))}
    indegree: dict[int, int] = {cid: 0 for cid in range(len(sccs))}
    for src, targets in precedence_edges.items():
        c_src = comp_id[src]
        for dst in targets:
            c_dst = comp_id[dst]
            if c_src != c_dst and c_dst not in comp_adj[c_src]:
                comp_adj[c_src].add(c_dst)
                indegree[c_dst] += 1

    # Kahn topological sort with deterministic tie-breaking by original input order.
    ready: list[int] = [cid for cid, deg in indegree.items() if deg == 0]
    ready.sort(key=lambda cid: min(order_pos[n] for n in sccs[cid]))
    ordered_cids: list[int] = []
    while ready:
        current = ready.pop(0)
        ordered_cids.append(current)
        for nxt in comp_adj[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
        ready.sort(key=lambda cid: min(order_pos[n] for n in sccs[cid]))

    ordered_nodes = [node for cid in ordered_cids for node in sccs[cid]]
    cyclic_sccs = [sccs[cid] for cid in ordered_cids if len(sccs[cid]) > 1]
    return ordered_nodes, cyclic_sccs


def _maximum_bipartite_matching(
    left_nodes: list[str],
    right_nodes: list[str],
    adj: dict[str, set[str]],
) -> dict[str, str]:
    """Compute a deterministic maximum matching from left_nodes (FR) to right_nodes (DP)."""
    right_order = {node: pos for pos, node in enumerate(right_nodes)}
    match_right: dict[str, str] = {}

    def dfs(u: str, visited: set[str]) -> bool:
        for v in sorted(adj.get(u, ()), key=lambda item: right_order[item]):
            if v in visited:
                continue
            visited.add(v)
            if v not in match_right or dfs(match_right[v], visited):
                match_right[v] = u
                return True
        return False

    for u in left_nodes:
        dfs(u, set())

    return {u: v for v, u in match_right.items()}


def _find_hall_bottleneck(
    left_nodes: list[str],
    adj: dict[str, set[str]],
    matching: dict[str, str],
) -> tuple[list[str], list[str]]:
    """When matching < |left_nodes|, find a minimal witness subset S with |N(S)| < |S|."""
    match_right = {v: u for u, v in matching.items()}
    unmatched = [u for u in left_nodes if u not in matching]
    if not unmatched:
        return [], []

    visited_left: set[str] = set()
    visited_right: set[str] = set()
    queue: deque[str] = deque([unmatched[0]])
    visited_left.add(unmatched[0])
    while queue:
        u = queue.popleft()
        for v in sorted(adj.get(u, ())):
            if v in visited_right:
                continue
            visited_right.add(v)
            paired_u = match_right.get(v)
            if paired_u is not None and paired_u not in visited_left:
                visited_left.add(paired_u)
                queue.append(paired_u)

    left_pos = {u: idx for idx, u in enumerate(left_nodes)}
    return sorted(visited_left, key=lambda u: left_pos[u]), sorted(visited_right)


def _cell_symbol(kinds: set[EdgeKind], *, is_primary_diagonal: bool) -> str:
    if EdgeKind.EXPLICIT in kinds and EdgeKind.CHANGE_COUPLING in kinds:
        return "D+C"
    if EdgeKind.EXPLICIT in kinds:
        return "D"
    if EdgeKind.CHANGE_COUPLING in kinds:
        return "C"
    return "●" if is_primary_diagonal else "·"


def _build_cell_map(edges: list[MatrixEdge]) -> dict[tuple[str, str], list[MatrixEdge]]:
    cells: dict[tuple[str, str], list[MatrixEdge]] = defaultdict(list)
    for edge in edges:
        cells[(edge.fr, edge.dp)].append(edge)
    return cells


def _solve_paired_view(
    parsed: ParsedMatrix,
    edges: list[MatrixEdge],
) -> dict[str, object]:
    dp_by_id = {dp.id: dp for dp in parsed.dps}
    fr_by_id = {fr.id: fr for fr in parsed.frs}
    pair_dp_of_fr = dict(parsed.pairs)
    pair_fr_of_dp = {dp_id: fr_id for fr_id, dp_id in parsed.pairs}
    unit_frs = [fr_id for fr_id, _ in parsed.pairs]

    # Active wild DPs that are touched by edges still appear as trailing columns so coupling is visible.
    paired_dp_set = set(pair_fr_of_dp)
    active_wild_dps = sorted(
        {edge.dp for edge in edges if edge.dp not in paired_dp_set},
        key=lambda dp_id: [d.id for d in parsed.dps].index(dp_id),
    )

    precedence: dict[str, set[str]] = {fr_id: set() for fr_id in unit_frs}
    off_diagonal_edges: list[MatrixEdge] = []
    for edge in edges:
        if edge.fr not in pair_dp_of_fr:
            continue
        owner_dp = pair_dp_of_fr[edge.fr]
        if edge.dp == owner_dp:
            continue
        off_diagonal_edges.append(edge)
        provider_fr = pair_fr_of_dp.get(edge.dp)
        if provider_fr is not None and provider_fr != edge.fr:
            # edge.fr depends on provider_fr's DP -> provider_fr must precede edge.fr.
            precedence[provider_fr].add(edge.fr)

    ordered_frs, cyclic_sccs = _condensation_order(unit_frs, precedence)
    ordered_dps = [pair_dp_of_fr[fr_id] for fr_id in ordered_frs] + active_wild_dps
    fr_pos = {fr_id: idx for idx, fr_id in enumerate(ordered_frs)}
    dp_pos = {dp_id: idx for idx, dp_id in enumerate(ordered_dps)}

    cells = _build_cell_map(edges)
    upper_violations: list[dict[str, str]] = []
    wild_couplings: list[dict[str, str]] = []
    for edge in off_diagonal_edges:
        r = fr_pos[edge.fr]
        c = dp_pos[edge.dp]
        record = {
            "fr": edge.fr,
            "dp": edge.dp,
            "kind": edge.kind.value,
            "evidence": edge.evidence,
            "note": edge.note,
        }
        if edge.dp not in paired_dp_set:
            wild_couplings.append(record)
        elif r < c:
            upper_violations.append(record)

    if cyclic_sccs or upper_violations:
        classification = AuditClassification.COUPLED
    elif off_diagonal_edges:
        classification = AuditClassification.DECOUPLED
    else:
        classification = AuditClassification.UNCOUPLED

    matrix_rows: list[list[str]] = []
    for r, fr_id in enumerate(ordered_frs):
        row: list[str] = []
        for c, dp_id in enumerate(ordered_dps):
            cell_edges = cells.get((fr_id, dp_id), [])
            kinds = {edge.kind for edge in cell_edges}
            is_diag = r == c and dp_id == pair_dp_of_fr[fr_id]
            symbol = _cell_symbol(kinds, is_primary_diagonal=is_diag)
            if r < c and cell_edges and dp_id in paired_dp_set:
                symbol = f"!{symbol}"
            row.append(symbol)
        matrix_rows.append(row)

    scc_details = []
    for comp in cyclic_sccs:
        comp_set = set(comp)
        comp_dps = {pair_dp_of_fr[fr_id] for fr_id in comp}
        internal = [
            {
                "fr": edge.fr,
                "dp": edge.dp,
                "kind": edge.kind.value,
                "evidence": edge.evidence,
                "note": edge.note,
            }
            for edge in off_diagonal_edges
            if edge.fr in comp_set and edge.dp in comp_dps
        ]
        scc_details.append({
            "members": [{"fr": fr_id, "fr_name": fr_by_id[fr_id].name, "dp": pair_dp_of_fr[fr_id],
                         "dp_name": dp_by_id[pair_dp_of_fr[fr_id]].name} for fr_id in comp],
            "size": len(comp),
            "edges": internal,
        })

    return {
        "mode": SolverMode.PAIRED.value,
        "classification": classification.value,
        "ordered_frs": [{"id": fr_id, "name": fr_by_id[fr_id].name} for fr_id in ordered_frs],
        "ordered_dps": [{"id": dp_id, "name": dp_by_id[dp_id].name, "role": dp_by_id[dp_id].role,
                         "status": dp_by_id[dp_id].status} for dp_id in ordered_dps],
        "matrix": matrix_rows,
        "cyclic_sccs": scc_details,
        "upper_triangular_violations": upper_violations,
        "wild_dp_couplings": wild_couplings,
        "off_diagonal_edge_count": len(off_diagonal_edges),
        "deficient_design": False,
        "redundant_dp_count": max(0, len(ordered_dps) - len(ordered_frs)),
        "hall_bottleneck": None,
        "unsatisfied_frs": [],
    }


def _solve_bipartite_view(
    parsed: ParsedMatrix,
    edges: list[MatrixEdge],
) -> dict[str, object]:
    fr_by_id = {fr.id: fr for fr in parsed.frs}
    dp_by_id = {dp.id: dp for dp in parsed.dps}
    active_frs = [fr.id for fr in parsed.frs if fr.status == "present"]
    active_fr_set = set(active_frs)
    active_edges = [edge for edge in edges if edge.fr in active_fr_set]

    # Include all present DPs plus any wild DP actually touched by an active FR edge.
    touched_dps = {edge.dp for edge in active_edges}
    active_dps = [dp.id for dp in parsed.dps if dp.status == "present" or dp.id in touched_dps]

    adj: dict[str, set[str]] = {fr_id: set() for fr_id in active_frs}
    rev_adj: dict[str, set[str]] = {dp_id: set() for dp_id in active_dps}
    for edge in active_edges:
        adj[edge.fr].add(edge.dp)
        rev_adj[edge.dp].add(edge.fr)

    unsatisfied_frs = [fr_id for fr_id in active_frs if not adj[fr_id]]
    solvable_frs = [fr_id for fr_id in active_frs if adj[fr_id]]
    deficient_design = len(active_dps) < len(active_frs)

    # Exact bottom-to-top peeling: a remaining column touching only one remaining FR
    # can always satisfy that FR last without disturbing any earlier FR.
    rem_frs = list(solvable_frs)
    rem_fr_set = set(rem_frs)
    rem_dps = [dp_id for dp_id in active_dps]
    peeled_tail_rev: list[tuple[str, str]] = []

    while rem_frs:
        candidates: list[tuple[int, int, str, str]] = []
        for idx, dp_id in enumerate(rem_dps):
            touching = [fr_id for fr_id in rem_frs if fr_id in rev_adj[dp_id]]
            if len(touching) == 1:
                # Prefer peeling private/low-total-degree columns first so shared upstream DPs stay at top-left.
                candidates.append((len(rev_adj[dp_id]), idx, touching[0], dp_id))
        if not candidates:
            break
        candidates.sort(key=lambda item: (item[0], item[1]))
        _, _, fr_id, dp_id = candidates[0]
        peeled_tail_rev.append((fr_id, dp_id))
        rem_frs.remove(fr_id)
        rem_fr_set.remove(fr_id)
        rem_dps.remove(dp_id)

    peeled_tail = list(reversed(peeled_tail_rev))
    peeled_frs = [fr_id for fr_id, _ in peeled_tail]
    peeled_dps = [dp_id for _, dp_id in peeled_tail]
    peeled_primary_dp = dict(peeled_tail)

    # Any remaining DP that touches no remaining FR is an upstream/redundant parameter
    # (fixed before the coupled core or peeled tail).
    upstream_redundant_dps = [dp_id for dp_id in rem_dps if not (rev_adj[dp_id] & rem_fr_set)]
    core_rem_dps = [dp_id for dp_id in rem_dps if dp_id not in set(upstream_redundant_dps)]

    cyclic_sccs: list[dict[str, object]] = []
    hall_bottleneck: dict[str, object] | None = None
    core_primary_dp: dict[str, str] = {}

    if rem_frs:
        rem_adj = {fr_id: (adj[fr_id] & set(core_rem_dps)) for fr_id in rem_frs}
        matching = _maximum_bipartite_matching(rem_frs, core_rem_dps, rem_adj)
        if len(matching) < len(rem_frs):
            hall_frs, hall_dps = _find_hall_bottleneck(rem_frs, rem_adj, matching)
            hall_bottleneck = {
                "frs": [{"id": fr_id, "name": fr_by_id[fr_id].name} for fr_id in hall_frs],
                "dps": [{"id": dp_id, "name": dp_by_id[dp_id].name} for dp_id in hall_dps],
                "reason": f"{len(hall_frs)} FRs compete for only {len(hall_dps)} DP(s).",
            }
            core_frs_ordered = hall_frs + [f for f in rem_frs if f not in set(hall_frs)]
            core_dps_ordered = hall_dps + [d for d in core_rem_dps if d not in set(hall_dps)]
        else:
            inv_match = {dp_id: fr_id for fr_id, dp_id in matching.items()}
            precedence: dict[str, set[str]] = {fr_id: set() for fr_id in rem_frs}
            for fr_id in rem_frs:
                for dp_id in rem_adj[fr_id]:
                    owner_fr = inv_match.get(dp_id)
                    if owner_fr is not None and owner_fr != fr_id:
                        precedence[owner_fr].add(fr_id)
            core_frs_ordered, raw_sccs = _condensation_order(rem_frs, precedence)
            matched_dps_ordered = [matching[fr_id] for fr_id in core_frs_ordered]
            extra_core_dps = [d for d in core_rem_dps if d not in set(matched_dps_ordered)]
            core_dps_ordered = extra_core_dps + matched_dps_ordered
            core_primary_dp = dict(matching)
            for comp in raw_sccs:
                comp_set = set(comp)
                comp_dps = {matching[f] for f in comp}
                internal = [
                    {
                        "fr": edge.fr,
                        "dp": edge.dp,
                        "kind": edge.kind.value,
                        "evidence": edge.evidence,
                        "note": edge.note,
                    }
                    for edge in active_edges
                    if edge.fr in comp_set and edge.dp in comp_dps and matching[edge.fr] != edge.dp
                ]
                cyclic_sccs.append({
                    "members": [{"fr": f, "fr_name": fr_by_id[f].name, "dp": matching[f],
                                 "dp_name": dp_by_id[matching[f]].name} for f in comp],
                    "size": len(comp),
                    "edges": internal,
                })
        ordered_frs = core_frs_ordered + peeled_frs + unsatisfied_frs
        ordered_dps = upstream_redundant_dps + core_dps_ordered + peeled_dps
    else:
        ordered_frs = peeled_frs + unsatisfied_frs
        ordered_dps = upstream_redundant_dps + peeled_dps

    # Determine classification.
    if deficient_design or rem_frs or unsatisfied_frs:
        classification = AuditClassification.COUPLED
    else:
        shared_dp_exists = any(len(rev_adj[dp_id]) > 1 for dp_id in active_dps)
        classification = AuditClassification.DECOUPLED if shared_dp_exists else AuditClassification.UNCOUPLED

    cells = _build_cell_map(active_edges)
    dp_pos = {dp_id: idx for idx, dp_id in enumerate(ordered_dps)}

    # Each row's primary column sets the lower-triangular boundary; entries to its right are violations.
    row_col_limit: dict[str, int] = {}
    for fr_id, dp_id in peeled_primary_dp.items():
        row_col_limit[fr_id] = dp_pos[dp_id]
    for fr_id, dp_id in core_primary_dp.items():
        row_col_limit[fr_id] = dp_pos[dp_id]
    core_offset = len(upstream_redundant_dps)
    for idx, fr_id in enumerate(ordered_frs):
        if fr_id not in row_col_limit:
            row_col_limit[fr_id] = min(core_offset + idx, max(0, len(ordered_dps) - 1))

    upper_violations: list[dict[str, str]] = []
    matrix_rows: list[list[str]] = []
    for fr_id in ordered_frs:
        row: list[str] = []
        limit = row_col_limit[fr_id]
        for c, dp_id in enumerate(ordered_dps):
            cell_edges = cells.get((fr_id, dp_id), [])
            kinds = {edge.kind for edge in cell_edges}
            symbol = _cell_symbol(kinds, is_primary_diagonal=False)
            if cell_edges and c > limit:
                symbol = f"!{symbol}"
                for edge in cell_edges:
                    upper_violations.append({
                        "fr": edge.fr,
                        "dp": edge.dp,
                        "kind": edge.kind.value,
                        "evidence": edge.evidence,
                        "note": edge.note,
                    })
            row.append(symbol)
        matrix_rows.append(row)

    return {
        "mode": SolverMode.BIPARTITE.value,
        "classification": classification.value,
        "ordered_frs": [{"id": fr_id, "name": fr_by_id[fr_id].name} for fr_id in ordered_frs],
        "ordered_dps": [{"id": dp_id, "name": dp_by_id[dp_id].name, "role": dp_by_id[dp_id].role,
                         "status": dp_by_id[dp_id].status} for dp_id in ordered_dps],
        "matrix": matrix_rows,
        "cyclic_sccs": cyclic_sccs,
        "upper_triangular_violations": upper_violations,
        "wild_dp_couplings": [],
        "off_diagonal_edge_count": len(active_edges),
        "deficient_design": deficient_design,
        "redundant_dp_count": max(0, len(active_dps) - len(active_frs)),
        "hall_bottleneck": hall_bottleneck,
        "unsatisfied_frs": [{"id": fr_id, "name": fr_by_id[fr_id].name} for fr_id in unsatisfied_frs],
    }


def _solve_view(parsed: ParsedMatrix, edges: list[MatrixEdge]) -> dict[str, object]:
    if parsed.mode is SolverMode.PAIRED:
        return _solve_paired_view(parsed, edges)
    return _solve_bipartite_view(parsed, edges)


def analyze_design_matrix(payload: dict[str, object]) -> dict[str, object]:
    """Validate and solve an Axiomatic Design matrix across full (D+C) and explicit-only (D) views."""
    parsed = _parse_input(payload)
    full_edges = list(parsed.edges)
    explicit_edges = [edge for edge in parsed.edges if edge.kind is EdgeKind.EXPLICIT]
    change_edges = [edge for edge in parsed.edges if edge.kind is EdgeKind.CHANGE_COUPLING]

    full_view = _solve_view(parsed, full_edges)
    explicit_view = _solve_view(parsed, explicit_edges)

    touched_dps = {edge.dp for edge in full_edges}
    phantom_frs = [
        {"id": fr.id, "name": fr.name, "ard_ref": fr.ard_ref}
        for fr in parsed.frs
        if fr.status == "phantom"
    ]
    wild_dps = [
        {"id": dp.id, "name": dp.name, "paths": list(dp.paths), "coupled_to_active_fr": dp.id in touched_dps}
        for dp in parsed.dps
        if dp.status == "wild"
    ]
    unreferenced_dps = [
        {"id": dp.id, "name": dp.name}
        for dp in parsed.dps
        if dp.status == "present" and dp.id not in touched_dps and dp.id not in {p[1] for p in parsed.pairs}
    ]

    hidden_escalation = (
        explicit_view["classification"] != AuditClassification.COUPLED.value
        and full_view["classification"] == AuditClassification.COUPLED.value
    )

    return {
        "ok": True,
        "scope": parsed.scope,
        "title": parsed.title,
        "mode": parsed.mode.value,
        "summary": {
            "full_classification": full_view["classification"],
            "explicit_only_classification": explicit_view["classification"],
            "hidden_coupling_escalation": hidden_escalation,
            "active_fr_count": sum(1 for fr in parsed.frs if fr.status == "present"),
            "active_dp_count": sum(1 for dp in parsed.dps if dp.status == "present"),
            "explicit_edge_count": len(explicit_edges),
            "change_coupling_edge_count": len(change_edges),
            "scc_count": len(full_view["cyclic_sccs"]),  # type: ignore[arg-type]
            "phantom_fr_count": len(phantom_frs),
            "wild_dp_count": len(wild_dps),
        },
        "full_view": full_view,
        "explicit_only_view": explicit_view,
        "drift": {
            "phantom_frs": phantom_frs,
            "wild_dps": wild_dps,
            "unreferenced_dps": unreferenced_dps,
        },
    }


def format_markdown_report(result: dict[str, object]) -> str:
    """Format the solved matrix and diagnostics as compact Markdown tables."""
    summary = result["summary"]
    full_view = result["full_view"]
    drift = result["drift"]
    assert isinstance(summary, dict)
    assert isinstance(full_view, dict)
    assert isinstance(drift, dict)

    lines: list[str] = [
        f"# {result['title']}",
        "",
        f"- **Scope**: `{result['scope']}` (`{result['mode']}`)",
        f"- **Full View (D+C)**: `{summary['full_classification']}`",
        f"- **Explicit Only (D)**: `{summary['explicit_only_classification']}`",
        f"- **Hidden Coupling Escalation**: `{summary['hidden_coupling_escalation']}`",
        f"- **Counts**: FR={summary['active_fr_count']}, DP={summary['active_dp_count']}, "
        f"D={summary['explicit_edge_count']}, C={summary['change_coupling_edge_count']}, "
        f"SCC={summary['scc_count']}",
        "",
        "## Reordered Design Matrix (D+C)",
        "",
    ]

    ordered_frs = full_view["ordered_frs"]
    ordered_dps = full_view["ordered_dps"]
    matrix = full_view["matrix"]
    assert isinstance(ordered_frs, list)
    assert isinstance(ordered_dps, list)
    assert isinstance(matrix, list)

    header = ["FR \\ DP", *[dp["id"] for dp in ordered_dps]]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for fr_meta, row in zip(ordered_frs, matrix, strict=True):
        label = f"`{fr_meta['id']}` {fr_meta['name']}"
        lines.append("| " + " | ".join([label, *row]) + " |")

    lines.append("")
    lines.append("Legend: `●` paired self-fulfillment, `D` explicit code dependency, `C` hidden change coupling, "
                 "`!X` upper-triangular coupling violation, `·` independent.")

    sccs = full_view["cyclic_sccs"]
    assert isinstance(sccs, list)
    if sccs:
        lines.extend(["", "## Coupled Clusters (SCC)", ""])
        for idx, scc in enumerate(sccs, start=1):
            members = ", ".join(f"`{m['fr']}`/`{m['dp']}` ({m['fr_name']})" for m in scc["members"])
            lines.append(f"{idx}. **SCC-{idx}** ({scc['size']} nodes): {members}")

    bottleneck = full_view.get("hall_bottleneck")
    if isinstance(bottleneck, dict):
        lines.extend(["", "## Deficient / Bottleneck Core", "", f"- {bottleneck['reason']}"])

    if drift["phantom_frs"] or drift["wild_dps"]:
        lines.extend(["", "## ARD vs Source Drift", ""])
        for fr in drift["phantom_frs"]:
            lines.append(f"- **Phantom FR**: `{fr['id']}` {fr['name']} ({fr['ard_ref'] or 'ARD'})")
        for dp in drift["wild_dps"]:
            lines.append(f"- **Wild DP**: `{dp['id']}` {dp['name']} ({', '.join(dp['paths']) or 'source'})")

    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="matrix_solver.py",
        description="Reorder an Axiomatic Design FR-DP matrix into lower-triangular form and detect coupling cycles.",
    )
    parser.add_argument("input", type=Path, help="Path to the input evidence JSON file.")
    parser.add_argument("--json-out", type=Path, help="Optional path to write full JSON analysis output.")
    parser.add_argument("--md-out", type=Path, help="Optional path to write Markdown matrix summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        result = analyze_design_matrix(payload)
    except (OSError, json.JSONDecodeError, ValueError) as err:
        print(json.dumps({"ok": False, "error": str(err)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    rendered_json = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with args.json_out.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered_json)

    if args.md_out is not None:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        with args.md_out.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(format_markdown_report(result))

    print(rendered_json, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
