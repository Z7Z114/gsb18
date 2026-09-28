"""端到端：注入假的 OpenAI 客户端后，转写分段必须落进对话实录与纪要。"""
from backend.services.ai_service import ai_service


class FakeSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class FakeTranscript:
    text = "住持：屋面漏雨严重。工匠：需更换瓦面重做防水。"
    segments = [
        FakeSegment(0.0, 2.5, "住持：屋面漏雨严重。"),
        FakeSegment(2.5, 6.0, "工匠：需更换瓦面重做防水。"),
    ]


class _AsyncCreate:
    async def create(self, **kwargs):
        return FakeTranscript()


class _Audio:
    transcriptions = _AsyncCreate()


class _Message:
    content = "（模拟生成内容）"


class _Choice:
    message = _Message()

class _ChatResponse:
    choices = [_Choice()]


class _ChatCreate:
    async def create(self, **kwargs):
        return _ChatResponse()


class _Chat:
    def __init__(self):
        self.completions = _ChatCreate()


class FakeOpenAIClient:
    # 只有转写接口可用；聊天/角色识别等调用会失败并走各自兜底
    audio = _Audio()

    def __init__(self):
        self.chat = _Chat()


def _prepare_meeting(client):
    r = client.post("/api/temples/", json={"name": "寒山寺", "location": "苏州"})
    temple = r.json()
    r = client.post(f"/api/temples/{temple['id']}/halls", json={"name": "大雄宝殿"})
    hall = r.json()
    r = client.post("/api/meetings/", json={
        "hall_id": hall["id"],
        "title": "大雄宝殿修缮会议",
        "date": "2026-09-01T09:00:00",
    })
    meeting = r.json()
    r = client.post(
        f"/api/meetings/{meeting['id']}/upload-audio",
        files={"file": ("meeting.mp3", b"fake-audio", "audio/mpeg")},
    )
    assert r.status_code == 200
    return meeting


def test_processing_persists_transcript_segments_to_dialogue(client):
    meeting = _prepare_meeting(client)

    original_client = ai_service.client
    ai_service.client = FakeOpenAIClient()
    try:
        r = client.post(f"/api/meetings/{meeting['id']}/process")
        assert r.status_code == 200, r.text
    finally:
        ai_service.client = original_client

    detail = client.get(f"/api/meetings/{meeting['id']}").json()
    assert detail["status"] == "completed"
    assert detail["transcript"] == FakeTranscript.text

    dialogue = client.get(f"/api/meetings/{meeting['id']}/dialogue").json()
    assert [turn["content"] for turn in dialogue] == [
        "住持：屋面漏雨严重。",
        "工匠：需更换瓦面重做防水。",
    ]
    assert dialogue[0]["timestamp"] == "0.0s - 2.5s"
    assert dialogue[1]["timestamp"] == "2.5s - 6.0s"

    markdown = client.get(
        f"/api/meetings/{meeting['id']}/download-markdown"
    ).text
    assert "会议对话实录" in markdown
    assert "屋面漏雨严重" in markdown
