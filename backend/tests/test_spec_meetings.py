"""行为规格 A：会议列表过滤 / 排序 / 殿堂存在性校验（验收点 A1-A4）。"""
from datetime import datetime


def _temple(client, name="寒山寺"):
    r = client.post("/api/temples/", json={"name": name, "location": "苏州"})
    assert r.status_code == 200, r.text
    return r.json()


def _hall(client, temple_id, name):
    r = client.post(f"/api/temples/{temple_id}/halls", json={"name": name})
    assert r.status_code == 200, r.text
    return r.json()


def _meeting(client, hall_id, title, date):
    r = client.post("/api/meetings/", json={
        "hall_id": hall_id,
        "title": title,
        "date": date,
    })
    assert r.status_code == 200, r.text
    return r.json()


def test_hall_id_zero_filter_is_strict(client):
    # A1: hall_id=0 必须严格过滤，而不是退化成返回全部
    temple = _temple(client)
    hall = _hall(client, temple["id"], "大雄宝殿")
    meeting = _meeting(client, hall["id"], "会议甲", "2026-09-01T09:00:00")

    r = client.get("/api/meetings/", params={"hall_id": 0})
    assert r.status_code == 200
    assert r.json() == []

    r = client.get("/api/meetings/", params={"hall_id": hall["id"]})
    assert [m["id"] for m in r.json()] == [meeting["id"]]


def test_list_ordered_by_date_desc_then_id_desc(client):
    # A3: 一律按 date 倒序，date 相同时按 id 倒序
    temple = _temple(client)
    hall = _hall(client, temple["id"], "大雄宝殿")
    m1 = _meeting(client, hall["id"], "早会", "2026-09-01T09:00:00")
    m2 = _meeting(client, hall["id"], "晚会", "2026-09-03T18:00:00")
    m3 = _meeting(client, hall["id"], "同点会一", "2026-09-03T18:00:00")

    r = client.get("/api/meetings/")
    assert r.status_code == 200
    assert [m["id"] for m in r.json()] == [m3["id"], m2["id"], m1["id"]]

    r = client.get("/api/meetings/", params={"hall_id": hall["id"]})
    assert [m["id"] for m in r.json()] == [m3["id"], m2["id"], m1["id"]]


def test_skip_limit_still_apply(client):
    # A4: skip / limit 生效
    temple = _temple(client)
    hall = _hall(client, temple["id"], "大雄宝殿")
    _meeting(client, hall["id"], "一", "2026-09-01T09:00:00")
    _meeting(client, hall["id"], "二", "2026-09-02T09:00:00")
    _meeting(client, hall["id"], "三", "2026-09-03T09:00:00")

    r = client.get("/api/meetings/", params={"skip": 1, "limit": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "二"


def test_create_meeting_with_missing_hall_returns_404(client):
    # A2: hall_id 指向不存在殿堂时 404，且不写入任何会议
    r = client.post("/api/meetings/", json={
        "hall_id": 999999,
        "title": "悬空会议",
        "date": "2026-09-01T09:00:00",
    })
    assert r.status_code == 404, r.text

    r = client.get("/api/meetings/")
    assert r.json() == []
