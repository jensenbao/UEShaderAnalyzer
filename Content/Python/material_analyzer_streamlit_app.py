import json
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="UE 材质分析器", layout="wide")
st.title("UE 材质分析器")

query_params = st.query_params
query_material = str(query_params.get("material_name", "")).strip()


with st.sidebar:
    st.header("连接设置")
    bridge_url = st.text_input("UE 桥接地址", value="http://127.0.0.1:30010")
    material_path = st.text_input("材质路径（可选）", value=query_material)
    auto_follow_selected = st.toggle("自动读取 UE 当前选择", value=True)
    refresh_seconds = st.slider("自动刷新间隔（秒）", min_value=1, max_value=10, value=2)
    fetch_by_path = st.button("按路径读取")

    st.divider()
    show_debug_tools = st.toggle("显示调试工具", value=False)
    debug_selected = st.button("调试当前选择") if show_debug_tools else False


def fetch_json(url: str) -> dict:
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "request_failed",
            "message": str(exc),
        }


def build_endpoint(base: str, path: str) -> str:
    base = base.rstrip("/")
    if path:
        return f"{base}/material_export_with_fallback?path={quote(path, safe='')}"
    return f"{base}/selected_material_summary"


def normalize(result: dict) -> dict:
    material = result.get("material") or {}
    nodes = result.get("nodes") or []
    edges = result.get("edges") or []
    bindings = result.get("property_bindings") or result.get("outputs") or []
    comments = result.get("comments") or []
    stats = result.get("stats") or {}

    if not stats:
        stats = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "binding_count": len(bindings),
            "comment_count": len(comments),
        }

    return {
        "ok": bool(result.get("ok", False)),
        "source_type": result.get("source_type") or result.get("source") or "unknown",
        "resolved_material_path": result.get("resolved_material_path") or "",
        "selected_material_path": result.get("selected_material_path") or "",
        "cpp_attempted": bool(result.get("cpp_attempted", False)),
        "cpp_ok": bool(result.get("cpp_ok", False)),
        "fallback_from": result.get("fallback_from") or "",
        "fallback_reason": result.get("fallback_reason") or "",
        "fallback_message": result.get("fallback_message") or "",
        "material": material,
        "nodes": nodes,
        "edges": edges,
        "property_bindings": bindings,
        "comments": comments,
        "stats": stats,
        "raw": result,
    }


if fetch_by_path:
    query_path = material_path.strip()
    endpoint = build_endpoint(bridge_url, query_path)
    payload = normalize(fetch_json(endpoint))
    st.session_state["analysis_payload"] = payload

if auto_follow_selected and not material_path.strip():
    @st.fragment(run_every=f"{int(refresh_seconds)}s")
    def _poll_selected_material() -> None:
        endpoint = build_endpoint(bridge_url, "")
        polled_payload = normalize(fetch_json(endpoint))

        if polled_payload.get("ok"):
            current_selected = polled_payload.get("resolved_material_path") or polled_payload.get("selected_material_path")
            previous_selected = st.session_state.get("_last_selected_material", "")
            if current_selected and (
                current_selected != previous_selected or "analysis_payload" not in st.session_state
            ):
                st.session_state["analysis_payload"] = polled_payload
                st.session_state["_last_selected_material"] = current_selected
                st.rerun()
        elif "analysis_payload" not in st.session_state:
            st.session_state["analysis_payload"] = polled_payload
            st.rerun()

        st.caption(f"自动跟随已开启：每 {int(refresh_seconds)} 秒检查一次，仅在选中材质变化时更新页面")

    _poll_selected_material()

if debug_selected:
    debug_endpoint = f"{bridge_url.rstrip('/')}/debug_selected?include_cpp=1"
    st.session_state["debug_payload"] = fetch_json(debug_endpoint)

if query_material and "analysis_payload" not in st.session_state:
    endpoint = build_endpoint(bridge_url, query_material)
    payload = normalize(fetch_json(endpoint))
    st.session_state["analysis_payload"] = payload

payload = st.session_state.get("analysis_payload")
debug_payload = st.session_state.get("debug_payload")

if show_debug_tools and debug_payload:
    with st.expander("调试信息（Bridge）", expanded=False):
        st.code(json.dumps(debug_payload, ensure_ascii=False, indent=2), language="json")

if not payload:
    st.info("请先在 UE 中选中材质（自动读取），或输入材质路径后点击“按路径读取”。")
else:
    if not payload["ok"]:
        st.error(f"读取失败：{payload['raw'].get('error_type', 'unknown')} - {payload['raw'].get('message', '')}")
    else:
        st.success(f"读取成功。来源：{payload['source_type']}")
        if payload.get("resolved_material_path") or payload.get("selected_material_path"):
            st.caption(
                f"selected={payload.get('selected_material_path','')} | resolved={payload.get('resolved_material_path','')}"
            )
        if payload.get("cpp_attempted"):
            if payload.get("cpp_ok"):
                st.caption("C++ 图读取：成功")
            else:
                fallback_note = payload.get("fallback_reason") or payload.get("fallback_message") or "unknown"
                st.warning(f"C++ 图读取失败，已回退到 ue_api：{fallback_note}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("节点", payload["stats"].get("node_count", 0))
        c2.metric("连线", payload["stats"].get("edge_count", 0))
        c3.metric("绑定", payload["stats"].get("binding_count", 0))
        c4.metric("注释", payload["stats"].get("comment_count", 0))

        material = payload["material"]
        st.subheader("材质")
        st.json(
            {
                "name": material.get("name", ""),
                "path": material.get("path", ""),
                "domain": material.get("domain", ""),
                "blend_mode": material.get("blend_mode", ""),
                "two_sided": material.get("two_sided", False),
            }
        )

        n_col, e_col = st.columns(2)

        with n_col:
            st.subheader("节点")
            if payload["nodes"]:
                node_df = pd.DataFrame(payload["nodes"])
                st.dataframe(node_df, use_container_width=True)
            else:
                st.warning("暂无节点")

        with e_col:
            st.subheader("连线")
            if payload["edges"]:
                edge_df = pd.DataFrame(payload["edges"])
                st.dataframe(edge_df, use_container_width=True)
            else:
                st.warning("暂无连线")

        b_col, c_col = st.columns(2)

        with b_col:
            st.subheader("属性绑定")
            if payload["property_bindings"]:
                bind_df = pd.DataFrame(payload["property_bindings"])
                st.dataframe(bind_df, use_container_width=True)
            else:
                st.warning("暂无属性绑定")

        with c_col:
            st.subheader("注释")
            if payload["comments"]:
                comment_df = pd.DataFrame(payload["comments"])
                st.dataframe(comment_df, use_container_width=True)
            else:
                st.warning("暂无注释")

        with st.expander("原始 JSON"):
            st.code(json.dumps(payload["raw"], ensure_ascii=False, indent=2), language="json")
