"""Tests for workflow service template (Gap 2)."""
import pathlib
import tempfile

from precompute import build_workflow, build_entity_context
from codegen import render_entity_files


def _approval_request():
    return {
        "name": "approval_request",
        "table": "approval_request",
        "columns": [
            {"name": "id", "type": "bigserial", "pk": True},
            {"name": "title", "type": "varchar(200)"},
            {"name": "status", "type": "varchar(30)"},
        ],
        "workflow": {
            "status_column": "status",
            "states": ["DRAFT", "SUBMITTED", "IN_PROGRESS", "APPROVED", "REJECTED", "CANCELLED"],
            "transitions": [
                {"action": "submit",  "from": ["DRAFT"], "to": "SUBMITTED"},
                {"action": "start",   "from": ["SUBMITTED"], "to": "IN_PROGRESS"},
                {"action": "approve", "from": ["IN_PROGRESS"], "to": "APPROVED"},
                {"action": "reject",  "from": ["IN_PROGRESS"], "to": "REJECTED"},
                {"action": "cancel",  "from": ["DRAFT", "SUBMITTED", "IN_PROGRESS"], "to": "CANCELLED"},
            ],
        },
    }


def test_build_workflow_none_when_absent():
    assert build_workflow({"name": "customer"}) is None


def test_build_workflow_extracts_states_and_transitions():
    wf = build_workflow(_approval_request())
    assert wf["status_column"] == "status"
    assert wf["status_column_upper"] == "STATUS"
    assert wf["states"] == ["DRAFT", "SUBMITTED", "IN_PROGRESS", "APPROVED", "REJECTED", "CANCELLED"]
    actions = [t["action"] for t in wf["transitions"]]
    assert actions == ["submit", "start", "approve", "reject", "cancel"]
    cancel = wf["transitions"][-1]
    assert cancel["from_states"] == ["DRAFT", "SUBMITTED", "IN_PROGRESS"]
    assert cancel["to_state"] == "CANCELLED"


def test_build_entity_context_carries_workflow():
    ctx = build_entity_context(_approval_request(), base_package="kr.demo")
    assert ctx["workflow"] is not None
    assert len(ctx["workflow"]["transitions"]) == 5


def test_build_entity_context_workflow_none_for_plain_entity():
    plain = {"name": "customer", "table": "customer", "columns": [{"name": "id", "pk": True}]}
    ctx = build_entity_context(plain, base_package="kr.demo")
    assert ctx["workflow"] is None


def test_render_workflow_files_emitted_when_workflow_present():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        written = render_entity_files(out, _approval_request(), base_package="kr.demo", lane="jakarta")
        paths = [p.as_posix() for p in written]
        assert any("ApprovalRequestWorkflowService.java" in p for p in paths)
        assert any("ApprovalRequestWorkflowServiceImpl.java" in p for p in paths)
        impl = next(p for p in written if "WorkflowServiceImpl.java" in p.name)
        body = impl.read_text(encoding="utf-8")
        assert "STATE_DRAFT" in body
        assert "STATE_APPROVED" in body
        assert "submit_approval_request" in body
        assert "ALLOWED_FROM_SUBMIT" in body
        assert "cannot `cancel` from" in body
        assert "update_approval_request_status" in body
        iface = next(p for p in written if p.name == "ApprovalRequestWorkflowService.java")
        ibody = iface.read_text(encoding="utf-8")
        assert "list_approval_request_by_status" in ibody
        for action in ("submit", "start", "approve", "reject", "cancel"):
            assert f"{action}_approval_request" in ibody


def test_render_workflow_files_skipped_for_plain_entity():
    plain = {
        "name": "customer",
        "table": "customer",
        "columns": [
            {"name": "id", "type": "bigserial", "pk": True},
            {"name": "name", "type": "varchar(100)"},
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        written = render_entity_files(out, plain, base_package="kr.demo", lane="jakarta")
        names = [p.name for p in written]
        assert not any("Workflow" in n for n in names)


def test_mapper_interface_includes_workflow_methods_when_workflow_present():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        written = render_entity_files(out, _approval_request(), base_package="kr.demo", lane="jakarta")
        mapper = next(p for p in written if p.name == "ApprovalRequestMapper.java")
        body = mapper.read_text(encoding="utf-8")
        assert "select_approval_request_by_id" in body
        assert "update_approval_request_status" in body


def test_mapper_xml_includes_workflow_statements_when_workflow_present():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        written = render_entity_files(out, _approval_request(), base_package="kr.demo", lane="jakarta")
        xml = next(p for p in written if p.name == "ApprovalRequestMapper.xml")
        body = xml.read_text(encoding="utf-8")
        assert 'id="select_approval_request_by_id"' in body
        assert 'id="update_approval_request_status"' in body
        assert "STATUS = #{NEW_STATUS}" in body
