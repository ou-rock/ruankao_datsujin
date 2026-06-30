import subprocess
import sys
from pathlib import Path

from ruankao_agent.domain import ExamFront, SourceIdentity
from ruankao_agent.storage import RuankaoStore
from ruankao_agent.study import capture_study_turn


def test_capture_study_turn_records_mein_and_du_raw_material(tmp_path) -> None:
    root = tmp_path / "demo"

    result = capture_study_turn(
        root,
        topic="质量属性场景",
        user_text="我觉得可用性就是系统别挂。",
        assistant_text="把可用性改成可度量场景：故障后 5 分钟内恢复核心下单能力。",
        fronts=(ExamFront.CASE, ExamFront.ESSAY),
    )

    store = RuankaoStore(root / "data" / "ruankao.db")
    store.initialize()
    records = store.list_raw_records()

    assert result.mein_record_id == records[0].id
    assert result.du_record_id == records[1].id
    assert [record.source for record in records] == [SourceIdentity.MEIN, SourceIdentity.DU]
    assert records[0].summary == "学习模式 Mein：质量属性场景"
    assert records[1].summary == "学习模式 Du：质量属性场景"
    assert records[0].promotion_status == "raw"
    assert records[1].promotion_status == "extracted"
    assert records[0].topics == ("学习模式", "质量属性场景")
    assert records[1].fronts == (ExamFront.CASE, ExamFront.ESSAY)


def test_cli_study_turn_prints_record_ids(tmp_path) -> None:
    root = tmp_path / "demo"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruankao_agent.cli",
            "study-turn",
            "--root",
            str(root),
            "--topic",
            "ATAM",
            "--user",
            "ATAM 是评估架构风险。",
            "--assistant",
            "补充：要区分风险点、非风险点、敏感点和权衡点。",
            "--front",
            "choice",
            "--front",
            "case",
        ],
        cwd=".",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "mein=1" in result.stdout
    assert "du=2" in result.stdout
    assert "topic=ATAM" in result.stdout
    assert "fronts=choice,case" in result.stdout


def test_study_mode_command_documents_dialogue_protocol() -> None:
    command = Path(__file__).resolve().parents[2] / ".codex" / "commands" / "ruankao-study-mode.md"
    text = command.read_text(encoding="utf-8")

    assert "Mein" in text
    assert "Du" in text
    assert "追问" in text
    assert "study-turn" in text
    assert "不一次问多个问题" in text
