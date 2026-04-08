from __future__ import annotations

from typing import Any


def normalize_graph_payload(raw: dict[str, Any], source_type: str = "ue_api") -> dict[str, Any]:
    """Normalize varied payload keys into one material_graph dictionary shape."""
    material_name = raw.get("material_name") or raw.get("name") or "UnknownMaterial"
    nodes = raw.get("nodes", [])
    edges = raw.get("edges", [])
    outputs = raw.get("outputs", [])

    if not isinstance(nodes, list):
        nodes = []
    if not isinstance(edges, list):
        edges = []
    if not isinstance(outputs, list):
        outputs = []

    return {
        "material_name": material_name,
        "source_type": source_type,
        "nodes": nodes,
        "edges": edges,
        "outputs": outputs,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "output_count": len(outputs),
        },
    }
