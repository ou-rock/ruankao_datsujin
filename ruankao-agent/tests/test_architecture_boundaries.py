from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "ruankao_agent"
DOCS_ROOT = REPO_ROOT / "docs"
ENTRY_ADAPTERS = {
    "cli",
    "web",
    "web_actions",
    "web_app",
    "web_bootstrap",
    "web_files",
    "web_forms",
    "web_handlers",
    "web_page",
    "web_page_forms",
    "web_page_sections",
    "web_page_style",
    "web_page_view",
}


EXPECTED_INTERNAL_DEPS = {
    "cheko": {"domain", "learning", "storage"},
    "cli": {
        "cheko",
        "dashboard",
        "domain",
        "evolution",
        "export_state",
        "learning",
        "loop",
        "notebooklm",
        "principles",
        "rag",
        "receipts",
        "route_map",
        "study",
        "vault",
        "web",
    },
    "dashboard": set(),
    "domain": set(),
    "evolution": {"receipts"},
    "export_state": {"storage"},
    "learning": {"domain", "learning_style"},
    "learning_style": set(),
    "loop": {"dashboard", "notebooklm"},
    "memory": {"storage"},
    "notebooklm": set(),
    "principles": {"domain", "storage"},
    "rag": {
        "domain",
        "memory",
        "rag_index",
        "rag_rank",
        "rag_report",
        "rag_types",
        "storage",
    },
    "rag_index": {"rag_types"},
    "rag_rank": {"domain", "rag_index", "rag_types"},
    "rag_report": {"rag_types"},
    "rag_types": {"domain"},
    "receipts": {"loop", "memory", "rag", "storage"},
    "route_map": {"domain", "memory", "storage"},
    "storage": {"domain"},
    "study": {"domain", "storage"},
    "vault": set(),
    "web": {"web_app", "web_handlers"},
    "web_actions": {
        "cheko",
        "domain",
        "evolution",
        "export_state",
        "rag",
        "receipts",
        "route_map",
        "storage",
        "study",
        "vault",
        "web_forms",
    },
    "web_app": {
        "dashboard",
        "loop",
        "storage",
        "web_actions",
        "web_bootstrap",
        "web_files",
        "web_forms",
        "web_page",
    },
    "web_bootstrap": {"learning", "storage", "vault"},
    "web_files": set(),
    "web_forms": {"domain"},
    "web_handlers": {"web_forms"},
    "web_page": {
        "domain",
        "evolution",
        "export_state",
        "memory",
        "rag",
        "receipts",
        "route_map",
        "web_page_sections",
        "web_page_view",
        "web_render",
    },
    "web_page_forms": {"web_page_view", "web_render"},
    "web_page_sections": {
        "web_page_forms",
        "web_page_style",
        "web_page_view",
        "web_render",
    },
    "web_page_style": set(),
    "web_page_view": set(),
    "web_render": {"domain", "memory", "storage"},
}


def test_internal_dependency_graph_matches_architecture_contract() -> None:
    assert _internal_dependency_graph() == EXPECTED_INTERNAL_DEPS


def test_inner_modules_do_not_depend_on_entry_adapters() -> None:
    graph = _internal_dependency_graph()
    for module, deps in graph.items():
        if module in {
            "cli",
            "web",
            "web_actions",
            "web_app",
            "web_bootstrap",
            "web_handlers",
            "web_page",
            "web_page_forms",
            "web_page_sections",
            "web_page_view",
        }:
            continue
        assert not (deps & ENTRY_ADAPTERS)


def test_architecture_boundary_doc_lists_modules_boundaries_and_coupling() -> None:
    text = (DOCS_ROOT / "ARCHITECTURE_BOUNDARIES.md").read_text(encoding="utf-8")

    assert "# 架构边界与耦合地图" in text
    assert "模块清单" in text
    assert "当前内部导入图" in text
    assert "耦合分类" in text
    assert "耦合热点" in text
    assert "允许依赖规则" in text
    for module in EXPECTED_INTERNAL_DEPS:
        assert f"`{module}.py`" in text or f"{module} " in text


def _internal_dependency_graph() -> dict[str, set[str]]:
    modules = {
        path.stem
        for path in PACKAGE_ROOT.glob("*.py")
        if path.name != "__init__.py"
    }
    graph: dict[str, set[str]] = {}
    for module in modules:
        path = PACKAGE_ROOT / f"{module}.py"
        graph[module] = _module_internal_deps(path, modules)
    return graph


def _module_internal_deps(path: Path, modules: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    deps: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            top = node.module.split(".", 1)[0]
            if top in modules:
                deps.add(top)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ruankao_agent."):
                    top = alias.name.split(".", 2)[1]
                    if top in modules:
                        deps.add(top)
    return deps
