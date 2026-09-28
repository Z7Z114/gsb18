"""行为规格 D：AI 转写取真实分段 / 离线分支 / client 可注入（D1-D3）。"""
import asyncio

from backend.services.ai_service import AIService


class FakeSegment:
    """模拟 OpenAI SDK 返回的分段：带属性的对象，而不是 dict。"""

    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class FakeTranscript:
    def __init__(self):
        self.text = "住持：屋面漏雨。工匠：需更换瓦面。"
        self.segments = [
            FakeSegment(0.0, 2.5, "住持：屋面漏雨。"),
            FakeSegment(2.5, 5.0, "工匠：需更换瓦面。"),
        ]


class _AsyncCall:
    def __init__(self, result):
        self._result = result

    async def create(self, **kwargs):
        return self._result


class _Audio:
    def __init__(self, result):
        self.transcriptions = _AsyncCall(result)


class FakeOpenAIClient:
    def __init__(self, result):
        self.audio = _Audio(result)


class RaisingClient:
    """模拟真实调用失败：任何调用都抛异常。"""

    class _Transcriptions:
        async def create(self, **kwargs):
            raise RuntimeError("网络异常，不应到达这里")

    class _Audio:
        def __init__(self):
            self.transcriptions = RaisingClient._Transcriptions()

    def __init__(self):
        self.audio = RaisingClient._Audio()


def test_transcribe_reads_object_segments(tmp_path):
    # D1: 分段是对象而不是 dict 时也要正确取到 start/end/text
    service = AIService.__new__(AIService)
    service.client = FakeOpenAIClient(FakeTranscript())

    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake-audio")

    result = asyncio.run(service.transcribe_audio(str(audio)))

    assert result["transcript"] == "住持：屋面漏雨。工匠：需更换瓦面。"
    assert result["segments"] == [
        {"start": 0.0, "end": 2.5, "text": "住持：屋面漏雨。"},
        {"start": 2.5, "end": 5.0, "text": "工匠：需更换瓦面。"},
    ]


def test_offline_branch_returns_empty_transcript_without_network(tmp_path):
    # D2: client 缺失（未配置 Key）时返回确定空结果，绝不碰客户端
    service = AIService.__new__(AIService)
    service.client = None

    audio = tmp_path / "missing.mp3"  # 文件不存在也没关系，不应尝试打开
    result = asyncio.run(service.transcribe_audio(str(audio)))

    assert result == {"transcript": "", "segments": []}


def test_transcribe_failure_path_returns_empty(tmp_path):
    # 失败路径：注入会抛异常的客户端，验证兜底而非真的发请求
    service = AIService.__new__(AIService)
    service.client = RaisingClient()

    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake-audio")

    result = asyncio.run(service.transcribe_audio(str(audio)))
    assert result["transcript"] == ""
    assert result["segments"] == []
    assert "error" in result


def test_client_attribute_is_replaceable_injection_point():
    # D3: 保留可整体替换的 client 属性
    service = AIService()
    service.client = FakeOpenAIClient(FakeTranscript())
    assert isinstance(service.client, FakeOpenAIClient)


def test_offline_chat_methods_dont_raise():
    # 离线分支下其余 AI 方法也必须不联网、不抛异常
    service = AIService.__new__(AIService)
    service.client = None

    summary = asyncio.run(service.generate_meeting_summary("", {"name": "大雄宝殿"}))
    assert "大雄宝殿" in summary
    assert asyncio.run(service.generate_fundraising_copy("", {}))
    assert asyncio.run(service.generate_merit_list(""))
    roles = asyncio.run(service.identify_speaker_roles([
        {"speaker": "SPEAKER_00", "text": "甲"},
        {"speaker": "SPEAKER_01", "text": "乙"},
    ]))
    assert roles == {"SPEAKER_00": "住持", "SPEAKER_01": "工匠"}
