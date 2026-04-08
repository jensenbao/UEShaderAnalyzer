from __future__ import annotations

from data_models.material_graph import MaterialGraph
from parser.normalize_graph import normalize_graph_payload


def parse_ue_api_payload(raw_payload: dict) -> MaterialGraph:
    normalized = normalize_graph_payload(raw_payload, source_type="ue_api")
    return MaterialGraph.from_dict(normalized)
