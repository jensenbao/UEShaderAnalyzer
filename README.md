# UE AI Material Analyzer

A Streamlit-based tool for Unreal Engine material graph performance analysis.

## Scope (Current Phase)

- Target: Assignment 2 only (material node performance analysis)
- Material only, no blueprint support
- Analysis first, generation later
- Web UI uses Streamlit
- Input priority:
  1. UE Live (UE Python / Remote Execution)
  2. Paste Text fallback
- AI is used for explanation, reporting, and suggestions
- Deterministic rules remain the primary detection logic

## Architecture (MVP)

1. UE material graph export (UE Live first)
2. Normalize to a unified `material_graph` structure
3. Run deterministic rules
4. Use AI to summarize and explain findings
5. Render report in Streamlit and export JSON/Markdown

## Folder Layout

- `app.py`: Streamlit entry
- `data_models/`: unified graph data model
- `parser/`: UE API and text parser
- `analyzer/`: graph utilities and rules
- `services/`: AI and report services
- `skills/`: reusable skill modules
- `samples/`: local sample inputs
- `outputs/`: parsed graphs and reports
- `ue_bridge/`: UE remote bridge functions

## Quick Start

1. Create and activate a Python environment.
2. Install dependencies from `requirements.txt`.
3. Run:

```bash
streamlit run app.py
```

## Next Milestone

- Complete `material_graph` model and validation
- Implement UE Live export minimal functions
- Parse and normalize UE Live output into `material_graph`
