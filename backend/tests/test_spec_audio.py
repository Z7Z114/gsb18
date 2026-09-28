"""行为规格 C：上传录音文件名净化与落盘位置约束（C1-C3）。"""
import os
from pathlib import Path

from backend.config import settings
from backend.database import SessionLocal
from backend import models


def _meeting(client):
    r = client.post("/api/temples/", json={"name": "寒山寺", "location": "苏州"})
    temple = r.json()
    r = client.post(f"/api/temples/{temple['id']}/halls", json={"name": "大雄宝殿"})
    hall = r.json()
    r = client.post("/api/meetings/", json={
        "hall_id": hall["id"],
        "title": "修缮会议",
        "date": "2026-09-01T09:00:00",
    })
    return r.json()


def test_upload_strips_directory_traversal(client, tmp_root):
    meeting = _meeting(client)
    malicious = "../../../tmp_evil_audio.mp3"

    r = client.post(
        f"/api/meetings/{meeting['id']}/upload-audio",
        files={"file": (malicious, b"fake-audio", "audio/mpeg")},
    )
    assert r.status_code == 200, r.text

    stored = Path(r.json()["file_path"])
    audio_dir = Path(settings.TEMP_AUDIO_DIR).resolve()

    # C2/C3: 真实落在 TEMP_AUDIO_DIR 内，且文件真实存在
    assert stored.exists()
    assert stored.resolve().parent == audio_dir
    assert ".." not in stored.parts
    assert "tmp_evil_audio.mp3" in stored.name

    # 逃逸目标文件不得被创建
    assert not (Path(settings.TEMP_AUDIO_DIR).parent.parent.parent / "tmp_evil_audio.mp3").exists()

    # C3: 入库路径与返回路径一致（Meeting 响应结构不含该字段，直接查库）
    detail = client.get(f"/api/meetings/{meeting['id']}").json()
    db = SessionLocal()
    try:
        stored_path = db.query(models.Meeting).filter(
            models.Meeting.id == detail["id"]
        ).first().audio_file_path
    finally:
        db.close()
    assert Path(stored_path) == stored


def test_upload_strips_absolute_and_backslash_path(client):
    meeting = _meeting(client)
    r = client.post(
        f"/api/meetings/{meeting['id']}/upload-audio",
        files={"file": (r"..\\..\\windows_evil.wav", b"x", "audio/wav")},
    )
    assert r.status_code == 200, r.text
    stored = Path(r.json()["file_path"]).resolve()
    audio_dir = Path(settings.TEMP_AUDIO_DIR).resolve()
    assert stored.parent == audio_dir
    assert ".." not in stored.parts
    assert stored.exists()


def test_upload_basename_only(client):
    # C1: 目录部分一律剥离
    meeting = _meeting(client)
    r = client.post(
        f"/api/meetings/{meeting['id']}/upload-audio",
        files={"file": ("nested/dir/recording.mp3", b"y", "audio/mpeg")},
    )
    assert r.status_code == 200, r.text
    stored = Path(r.json()["file_path"]).resolve()
    assert stored.parent == Path(settings.TEMP_AUDIO_DIR).resolve()
    assert stored.name.endswith("recording.mp3")
