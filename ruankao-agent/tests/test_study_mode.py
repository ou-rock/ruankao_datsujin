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
        learner_position="可用性概念粗糙，缺少度量",
        codex_position="案例教练",
        destination="写出可评分的质量属性场景",
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
    assert result.learner_position == "可用性概念粗糙，缺少度量"
    assert result.codex_position == "案例教练"
    assert result.destination == "写出可评分的质量属性场景"
    assert "我在哪: 可用性概念粗糙，缺少度量" in records[0].text
    assert "你在哪: 案例教练" in records[1].text
    assert "我们要去哪: 写出可评分的质量属性场景" in records[1].text


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
            "--learner-position",
            "知道 ATAM 名称，但分类不稳",
            "--codex-position",
            "ruankao-teach 追问者",
            "--destination",
            "能区分四类评估点",
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
    assert "fronts=选择题、案例题" in result.stdout
    assert "fronts=choice,case" not in result.stdout


def test_study_mode_command_documents_dialogue_protocol() -> None:
    command = Path(__file__).resolve().parents[2] / ".codex" / "commands" / "ruankao-study-mode.md"
    text = command.read_text(encoding="utf-8")

    assert "Mein" in text
    assert "Du" in text
    assert "追问" in text
    assert "ruankao-teach" in text
    assert "Uns" in text
    assert "我在哪" in text
    assert "你在哪" in text
    assert "我们要去哪" in text
    assert "study-turn" in text
    assert "不一次问多个问题" in text
    assert "原则链接只作为夜间挖掘候选" in text
