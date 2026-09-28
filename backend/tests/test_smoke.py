"""顺利路径冒烟测试。

这些用例只覆盖「正常一条龙」，在修复前后都必须全绿：
它们既不能暴露缺陷，也不能因为修复而变红。
"""
import os
from pathlib import Path

from backend.config import settings


def _temples(client):
    r = client.get("/api/temples/")
    assert r.status_code == 200, r.text
    return r.json()


def _make_temple(client, name="寒山寺", location="苏州"):
    r = client.post("/api/temples/", json={
        "name": name,
        "location": location,
        "description": "千年古刹",
    })
    assert r.status_code == 200, r.text
    return r.json()


def _make_hall(client, temple_id, name="大雄宝殿"):
    # 前端登记殿堂时会把整个表单体发过来（历史上带 temple_id），这里沿用
    r = client.post(f"/api/temples/{temple_id}/halls", json={
        "temple_id": temple_id,
        "name": name,
        "description": "主殿",
        "estimated_cost": "120万",
        "damage_details": {"木构腐朽": "严重，三根檐柱糟朽"},
        "repair_plan": {"木构替换": "更换檐柱"},
    })
    assert r.status_code == 200, r.text
    return r.json()


def _make_meeting(client, hall_id, title="大雄宝殿修缮募捐会议", date="2026-09-01T09:30:00"):
    r = client.post("/api/meetings/", json={
        "hall_id": hall_id,
        "title": title,
        "date": date,
        "participants": ["住持", "监院", "工匠"],
    })
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------- 基础

def test_root_and_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_openapi_docs_available(client):
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


# ---------------------------------------------------------------- 寺庙 / 殿堂

def test_temple_and_hall_roundtrip(client):
    temple = _make_temple(client)
    assert temple["name"] == "寒山寺"
    assert [t["id"] for t in _temples(client)] == [temple["id"]]

    r = client.get(f"/api/temples/{temple['id']}")
    assert r.status_code == 200
    assert r.json()["location"] == "苏州"

    hall = _make_hall(client, temple["id"])
    assert hall["name"] == "大雄宝殿"

    r = client.get(f"/api/temples/{temple['id']}/halls")
    assert r.status_code == 200
    assert [h["id"] for h in r.json()] == [hall["id"]]

    r = client.get(f"/api/temples/halls/{hall['id']}")
    assert r.status_code == 200
    assert r.json()["damage_details"]["木构腐朽"].startswith("严重")

    # 前端「保存病害信息」会把整个殿堂对象回传
    payload = dict(r.json())
    payload["damage_details"] = {"木构腐朽": "严重，三根檐柱糟朽", "彩绘剥落": "中等"}
    r = client.put(f"/api/temples/halls/{hall['id']}", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["damage_details"]["彩绘剥落"] == "中等"
    assert r.json()["temple_id"] == temple["id"]

    r = client.get("/api/temples/424242")
    assert r.status_code == 404


# ---------------------------------------------------------------- 会议一条龙

def test_meeting_upload_process_download(client):
    temple = _make_temple(client)
    hall = _make_hall(client, temple["id"])
    meeting = _make_meeting(client, hall["id"])

    r = client.get("/api/meetings/", params={"hall_id": hall["id"]})
    assert r.status_code == 200
    assert [m["id"] for m in r.json()] == [meeting["id"]]

    # 上传一段录音
    files = {"file": ("住持与工匠.mp3", b"ID3\x03\x00\x00\x00fake-audio", "audio/mpeg")}
    r = client.post(f"/api/meetings/{meeting['id']}/upload-audio", files=files)
    assert r.status_code == 200, r.text
    stored = Path(r.json()["file_path"])
    assert stored.exists()
    assert Path(settings.TEMP_AUDIO_DIR).resolve() in stored.resolve().parents

    r = client.get(f"/api/meetings/{meeting['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "audio_uploaded"

    # 离线处理：未配置 Key 时也必须能跑完，不联网
    r = client.post(f"/api/meetings/{meeting['id']}/process")
    assert r.status_code == 200, r.text

    r = client.get(f"/api/meetings/{meeting['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    r = client.get(f"/api/meetings/{meeting['id']}/dialogue")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get(f"/api/meetings/{meeting['id']}/download-markdown")
    assert r.status_code == 200
    assert "修缮募捐功德纪要" in r.text
    assert "大雄宝殿" in r.text

    r = client.get("/api/meetings/424242")
    assert r.status_code == 404


def test_send_emails_offline_is_reported_not_raised(client):
    temple = _make_temple(client)
    hall = _make_hall(client, temple["id"])
    meeting = _make_meeting(client, hall["id"])

    r = client.post(f"/api/meetings/{meeting['id']}/send-emails", json={
        "to_emails": ["jushi@example.com"],
        "subject": "功德纪要",
        "markdown_content": "# 功德纪要",
    })
    assert r.status_code == 200
    assert r.json()["success"] is False


# ---------------------------------------------------------------- 功德主

def test_donor_roundtrip(client):
    r = client.post("/api/donors/", json={
        "name": "张居士",
        "email": "zhang@example.com",
        "phone": "13800000000",
        "amount": "人民币壹仟元整",
        "blessing_content": "愿以此功德，回向法界众生",
    })
    assert r.status_code == 200, r.text
    donor = r.json()

    r = client.get("/api/donors/")
    assert r.status_code == 200
    assert [d["id"] for d in r.json()] == [donor["id"]]

    r = client.get(f"/api/donors/{donor['id']}")
    assert r.status_code == 200
    assert r.json()["amount"] == "人民币壹仟元整"

    assert client.get("/api/donors/424242").status_code == 404
