from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class MaterialNode:
    id: str
    name: str
    type: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MaterialEdge:
    from_node: str
    from_pin: str
    to_node: str
    to_pin: str


@dataclass(slots=True)
class MaterialOutput:
    output: str
    source_node: str


@dataclass(slots=True)
class MaterialStats:
    node_count: int = 0
    edge_count: int = 0
    output_count: int = 0


@dataclass(slots=True)
class MaterialGraph:
    material_name: str
    source_type: str
    nodes: list[MaterialNode] = field(default_factory=list)
    edges: list[MaterialEdge] = field(default_factory=list)
    outputs: list[MaterialOutput] = field(default_factory=list)
    stats: MaterialStats = field(default_factory=MaterialStats)

    def refresh_stats(self) -> None:
        self.stats.node_count = len(self.nodes)
        self.stats.edge_count = len(self.edges)
        self.stats.output_count = len(self.outputs)

    def validate(self) -> None:
        if not self.material_name:
            raise ValueError("material_name cannot be empty")
        if self.source_type not in {"ue_api", "paste_text", "sample"}:
            raise ValueError("source_type must be one of: ue_api, paste_text, sample")

        node_ids = {node.id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("node IDs must be unique")

        for edge in self.edges:
            if edge.from_node not in node_ids:
                raise ValueError(f"edge.from_node not found: {edge.from_node}")
            if edge.to_node not in node_ids:
                raise ValueError(f"edge.to_node not found: {edge.to_node}")

        for output in self.outputs:
            if output.source_node not in node_ids:
                raise ValueError(f"output.source_node not found: {output.source_node}")

        self.refresh_stats()

    def to_dict(self) -> dict[str, Any]:
        self.refresh_stats()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MaterialGraph":
        stats_data = data.get("stats", {})

        graph = cls(
            material_name=data.get("material_name", ""),
            source_type=data.get("source_type", "sample"),
            nodes=[
                MaterialNode(
                    id=node.get("id", ""),
                    name=node.get("name", ""),
                    type=node.get("type", ""),
                    params=node.get("params", {}),
                )
                for node in data.get("nodes", [])
            ],
            edges=[
                MaterialEdge(
                    from_node=edge.get("from_node", ""),
                    from_pin=edge.get("from_pin", ""),
                    to_node=edge.get("to_node", ""),
                    to_pin=edge.get("to_pin", ""),
                )
                for edge in data.get("edges", [])
            ],
            outputs=[
                MaterialOutput(
                    output=item.get("output", ""),
                    source_node=item.get("source_node", ""),
                )
                for item in data.get("outputs", [])
            ],
            stats=MaterialStats(
                node_count=stats_data.get("node_count", 0),
                edge_count=stats_data.get("edge_count", 0),
                output_count=stats_data.get("output_count", 0),
            ),
        )

        graph.validate()
        return graph
