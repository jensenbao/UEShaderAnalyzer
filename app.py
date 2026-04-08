import json
from pathlib import Path

import streamlit as st

from data_models.material_graph import MaterialGraph
from parser.ue_api_parser import parse_ue_api_payload
from ue_bridge.export_material_graph import export_selected_material_graph


st.set_page_config(page_title="UE AI Material Analyzer", layout="wide")
st.title("UE AI Material Analyzer (MVP)")

sample_path = Path("samples/sample_graph_01.json")


def show_graph(graph: MaterialGraph) -> None:
    data = graph.to_dict()
    stats = data["stats"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Material", data["material_name"])
    c2.metric("Nodes", stats["node_count"])
    c3.metric("Edges", stats["edge_count"])
    c4.metric("Outputs", stats["output_count"])

    st.subheader("Nodes")
    st.dataframe(data["nodes"], use_container_width=True)

    st.subheader("Edges")
    st.dataframe(data["edges"], use_container_width=True)

    st.subheader("Outputs")
    st.dataframe(data["outputs"], use_container_width=True)

if st.button("Load sample graph"):
    if not sample_path.exists():
        st.error("Sample file not found: samples/sample_graph_01.json")
    else:
        with sample_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            graph = MaterialGraph.from_dict(data)
            st.success("Sample graph loaded and validated")
            show_graph(graph)
        except Exception as exc:
            st.error(f"Validation failed: {exc}")

if st.button("Load from UE Live"):
    try:
        raw_payload = export_selected_material_graph()
        graph = parse_ue_api_payload(raw_payload)
        st.success("UE Live graph loaded and validated")
        show_graph(graph)
    except Exception as exc:
        st.error(f"UE Live load failed: {exc}")

st.caption("Next: connect UE Live export and normalize parser output")
