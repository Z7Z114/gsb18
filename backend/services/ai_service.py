import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from ..config import settings


class AIService:
    def __init__(self):
        # client 是 OpenAI 客户端的注入点：默认可直接替换；未配置 Key 时为
        # None，所有调用走离线分支，绝不创建客户端、绝不发网络请求。
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

    @staticmethod
    def _field(segment, key):
        # OpenAI SDK 返回的分段是带属性的对象而不是 dict
        if isinstance(segment, dict):
            return segment[key]
        return getattr(segment, key)

    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        if self.client is None:
            # 离线分支：确定结果，不发起任何网络请求
            return {"transcript": "", "segments": []}

        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment", "word"],
                    language="zh",
                )
            return {
                "transcript": transcript.text,
                "segments": [
                    {
                        "start": self._field(seg, "start"),
                        "end": self._field(seg, "end"),
                        "text": self._field(seg, "text"),
                    }
                    for seg in transcript.segments
                ],
            }
        except Exception as e:
            return {
                "transcript": "",
                "segments": [],
                "error": str(e),
            }

    async def diarize_speakers(
        self, audio_file_path: str, num_speakers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        try:
            from pyannote.audio import Pipeline

            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=settings.PYANNOTE_AUTH_TOKEN,
            )

            diarization = pipeline(audio_file_path, num_speakers=num_speakers)

            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append(
                    {
                        "start": turn.start,
                        "end": turn.end,
                        "speaker": speaker,
                    }
                )

            return segments
        except Exception as e:
            return [{"error": str(e)}]

    def align_transcript_with_speakers(
        self, transcript_segments: List[Dict[str, Any]], 
        speaker_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        aligned_segments = []

        for trans_seg in transcript_segments:
            trans_start = trans_seg["start"]
            trans_end = trans_seg["end"]
            trans_text = trans_seg["text"]

            best_speaker = None
            max_overlap = 0

            for speaker_seg in speaker_segments:
                if "error" in speaker_seg:
                    continue

                spk_start = speaker_seg["start"]
                spk_end = speaker_seg["end"]

                overlap_start = max(trans_start, spk_start)
                overlap_end = min(trans_end, spk_end)
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = speaker_seg["speaker"]

            aligned_segments.append(
                {
                    "start": trans_start,
                    "end": trans_end,
                    "speaker": best_speaker or "UNKNOWN",
                    "text": trans_text,
                }
            )

        return aligned_segments

    async def generate_meeting_summary(self, transcript: str, 
                                       hall_info: Optional[Dict] = None) -> str:
        hall_context = ""
        if hall_info:
            hall_context = f"""
            殿堂信息：
            名称：{hall_info.get('name', '')}
            描述：{hall_info.get('description', '')}
            病害情况：{json.dumps(hall_info.get('damage_details', {}), ensure_ascii=False)}
            """

        prompt = f"""你是一位负责寺庙修缮募捐会议纪要的书记僧人，请根据以下对话内容生成专业的会议纪要。

{hall_context}

会议对话内容：
{transcript}

请生成包含以下内容的会议纪要：
1. 会议概述
2. 殿堂病害详细分析（木构腐朽、彩绘剥落、基础沉降等）
3. 修缮方案讨论（木构替换、彩绘重绘、防水处理等）
4. 工程预算与工期
5. 待确认事项

请使用古风文雅的语言，符合佛门语境。"""

        if self.client is None:
            hall_name = (hall_info or {}).get("name", "本寺殿堂")
            offline_summary = (
                f"【离线纪要】本次为{hall_name}修缮事宜会商，"
                "因未配置 AI 服务，纪要由离线分支生成。"
            )
            if transcript:
                offline_summary += "\n\n会议对话实录如下：\n" + transcript
            return offline_summary

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成摘要时出错: {str(e)}"

    async def generate_fundraising_copy(self, summary: str, 
                                       hall_info: Dict) -> str:
        if self.client is None:
            hall_name = (hall_info or {}).get("name", "本寺殿堂")
            return (
                f"【离线募捐文案】伏以三宝慈光，普荫群萌。{hall_name}年深岁久，"
                "亟待修缮。愿诸善信随喜布施，共襄盛举，功德无量。"
            )

        prompt = f"""你是一位寺庙的文疏法师，请根据以下会议纪要和殿堂信息，撰写一篇感人至深的募捐文案。

殿堂信息：
名称：{hall_info.get('name', '')}
描述：{hall_info.get('description', '')}
病害情况：{json.dumps(hall_info.get('damage_details', {}), ensure_ascii=False)}
修缮方案：{json.dumps(hall_info.get('repair_plan', {}), ensure_ascii=False)}
预估费用：{hall_info.get('estimated_cost', '')}

会议纪要摘要：
{summary}

请撰写一篇募捐文案，要求：
1. 以佛门慈悲济世的视角出发
2. 详述殿堂的历史价值和当前困境
3. 说明修缮的紧迫性和重要性
4. 呼吁信众发心布施，积累功德
5. 语言典雅，富有感染力
6. 字数约800-1200字

请使用古风文言与白话结合的方式，符合佛教语境。"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成募捐文案时出错: {str(e)}"

    async def generate_merit_list(self, fundraising_copy: str) -> str:
        if self.client is None:
            return (
                "【离线功德回向清单】\n"
                "- 随喜布施者，回向合家平安、福慧增长\n"
                "- 发心供养者，回向事业顺遂、善愿皆成\n"
                "- 乐助修缮者，镌刻芳名、世代流芳"
            )

        prompt = f"""你是一位寺庙的知客师，请根据以下募捐文案，撰写一份功德回向清单模板。

募捐文案：
{fundraising_copy}

请生成功德回向清单，包含以下内容：
1. 修缮项目明细及所需功德金
2. 不同布施金额对应的功德回向
3. 随喜赞叹的回向文
4. 供僧、供灯、供花等附加功德项目

请使用佛教传统的表述方式，如：
- 布施壹佰元者，回向某某
- 布施壹仟元者，回向某某
- 布施万元以上者，镌刻功德碑，世代流芳

语言要庄重典雅，符合佛教仪轨。"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成功德回向清单时出错: {str(e)}"

    async def identify_speaker_roles(
        self, aligned_segments: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        speaker_texts = {}
        for seg in aligned_segments:
            speaker = seg["speaker"]
            if speaker not in speaker_texts:
                speaker_texts[speaker] = []
            speaker_texts[speaker].append(seg["text"])

        speaker_roles = {}
        if self.client is None:
            # 离线分支：不联网，给出确定的默认角色
            for index, speaker in enumerate(speaker_texts):
                speaker_roles[speaker] = "住持" if index == 0 else "工匠"
            return speaker_roles

        for speaker, texts in speaker_texts.items():
            combined_text = " ".join(texts)
            prompt = f"""根据以下对话内容，判断说话人{SPEAKER_NAMES.get(speaker, speaker)}的身份角色。

对话内容摘要：
{combined_text[:2000]}

请从以下角色中选择最匹配的一个：
- 住持（寺院负责人，讲佛法、讲发心）
- 监院（寺院管家，讲具体事务安排）
- 工匠（负责修缮技术，讲木构、彩绘、工艺）
- 设计师（负责方案设计，讲规划、预算）
- 居士（护法居士，讲护持、发心）
- 其他

请只返回角色名称。"""

            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                role = response.choices[0].message.content.strip()
                speaker_roles[speaker] = role
            except Exception:
                speaker_roles[speaker] = "未知"

        return speaker_roles


SPEAKER_NAMES = {
    "SPEAKER_00": "甲",
    "SPEAKER_01": "乙",
    "SPEAKER_02": "丙",
    "SPEAKER_03": "丁",
    "SPEAKER_04": "戊",
}


ai_service = AIService()
