from pathlib import Path


def test_daily_cycle_script_includes_closure_exports() -> None:
    script = Path(__file__).resolve().parents[2] / "run-daily-cycle.command"
    text = script.read_text(encoding="utf-8")

    assert "cheko-seed-cards" in text
    assert "seed-principles" in text
    assert "daily-receipt" in text
    assert "route-map" in text
    assert "night-evolve" in text
    assert "vault-sync" in text
    assert "raw-vault-sync" in text
    assert "export-state" in text
    assert text.index("raw-vault-sync") < text.index("export-state")
