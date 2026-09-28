"""行为规格 B：殿堂创建归属由路径决定 / PUT 部分更新且不得改寺庙（B1-B4）。"""


def _temple(client, name="寒山寺"):
    r = client.post("/api/temples/", json={"name": name, "location": "苏州"})
    assert r.status_code == 200, r.text
    return r.json()


def test_create_hall_without_temple_id_in_body(client):
    # B1: 请求体不要求 temple_id
    temple = _temple(client)
    r = client.post(f"/api/temples/{temple['id']}/halls", json={
        "name": "观音殿",
        "description": "供奉观音大士",
    })
    assert r.status_code == 200, r.text
    hall = r.json()
    assert hall["temple_id"] == temple["id"]
    assert hall["name"] == "观音殿"


def test_body_temple_id_never_overrides_path(client):
    # B1: 请求体即便带了别的 temple_id，也以路径参数为准
    temple_a = _temple(client, "寒山寺")
    temple_b = _temple(client, "西园寺")
    r = client.post(f"/api/temples/{temple_a['id']}/halls", json={
        "temple_id": temple_b["id"],
        "name": "地藏殿",
    })
    assert r.status_code == 200, r.text
    assert r.json()["temple_id"] == temple_a["id"]


def test_create_hall_under_missing_temple_returns_404(client):
    # B2
    r = client.post("/api/temples/999999/halls", json={"name": "不存在"})
    assert r.status_code == 404, r.text


def test_put_is_partial_update(client):
    # B3: 只覆盖请求体里出现的字段，未出现的保持原值
    temple = _temple(client)
    r = client.post(f"/api/temples/{temple['id']}/halls", json={
        "name": "大雄宝殿",
        "description": "主殿",
        "estimated_cost": "120万",
        "damage_details": {"木构腐朽": "严重"},
        "repair_plan": {"木构替换": "更换檐柱"},
    })
    hall = r.json()

    r = client.put(f"/api/temples/halls/{hall['id']}", json={
        "damage_details": {"木构腐朽": "中等"},
    })
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["damage_details"] == {"木构腐朽": "中等"}
    # 未出现的字段保持原值
    assert updated["name"] == "大雄宝殿"
    assert updated["description"] == "主殿"
    assert updated["estimated_cost"] == "120万"
    assert updated["repair_plan"] == {"木构替换": "更换檐柱"}


def test_put_cannot_change_temple_id(client):
    # B4: 即使请求体带 temple_id 也必须忽略
    temple_a = _temple(client, "寒山寺")
    temple_b = _temple(client, "西园寺")
    r = client.post(f"/api/temples/{temple_a['id']}/halls", json={"name": "天王殿"})
    hall = r.json()

    r = client.put(f"/api/temples/halls/{hall['id']}", json={
        "name": "天王殿（修缮后）",
        "temple_id": temple_b["id"],
    })
    assert r.status_code == 200, r.text
    assert r.json()["temple_id"] == temple_a["id"]
    assert r.json()["name"] == "天王殿（修缮后）"


def test_put_missing_hall_returns_404(client):
    r = client.put("/api/temples/halls/999999", json={"name": "x"})
    assert r.status_code == 404, r.text
