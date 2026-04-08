from __future__ import annotations

from typing import Any

from ue_bridge.remote_exec_client import UERemoteExecClient


def get_selected_material_name(client: UERemoteExecClient | None = None) -> str:
    ue = client or UERemoteExecClient()
    payload = ue.run_python("get_selected_material_name()")

    name = payload.get("material_name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Failed to get selected material name from UE")
    return name


def export_selected_material_graph(client: UERemoteExecClient | None = None) -> dict[str, Any]:
    ue = client or UERemoteExecClient()
    payload = ue.run_python("export_selected_material_graph()")

    if not isinstance(payload, dict):
        raise ValueError("UE export payload is invalid")
    return payload


def export_material_graph_by_name(
    name: str,
    client: UERemoteExecClient | None = None,
) -> dict[str, Any]:
    if not name.strip():
        raise ValueError("Material name cannot be empty")

    ue = client or UERemoteExecClient()
    payload = ue.run_python(f"export_material_graph_by_name('{name}')")

    if not isinstance(payload, dict):
        raise ValueError("UE export payload is invalid")
    return payload
