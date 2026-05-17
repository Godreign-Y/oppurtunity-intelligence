"""
app/pipelines/__init__.py

Standalone per-source pipeline modules.

Each pipeline is independently callable via its `run_*_pipeline()` async function.
All pipelines return signals already tagged with an opportunity_category from the 6 canonical categories.
"""
