from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TempleBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None


class TempleCreate(TempleBase):
    pass


class Temple(TempleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class HallBase(BaseModel):
    name: str
    description: Optional[str] = None
    damage_details: Optional[Dict[str, Any]] = None
    repair_plan: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[str] = None


class HallCreate(HallBase):
    # 殿堂归属由路径参数决定；请求体里若带了 temple_id 也会被忽略
    temple_id: Optional[int] = None


class HallUpdate(BaseModel):
    # PUT 为部分更新：只覆盖请求体里出现的字段；temple_id 不可经此修改
    name: Optional[str] = None
    description: Optional[str] = None
    damage_details: Optional[Dict[str, Any]] = None
    repair_plan: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[str] = None


class Hall(HallBase):
    temple_id: int
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class DialogueTurnBase(BaseModel):
    speaker: str
    speaker_role: str
    content: str
    timestamp: Optional[str] = None


class DialogueTurnCreate(DialogueTurnBase):
    meeting_id: int


class DialogueTurn(DialogueTurnBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MeetingBase(BaseModel):
    hall_id: int
    title: str
    date: datetime
    participants: Optional[List[str]] = None


class MeetingCreate(MeetingBase):
    pass


class Meeting(MeetingBase):
    id: int
    status: str
    transcript: Optional[str] = None
    summary: Optional[str] = None
    fundraising_copy: Optional[str] = None
    merit_list: Optional[str] = None
    markdown_file: Optional[str] = None
    created_at: datetime
    dialogue_turns: List[DialogueTurn] = []

    class Config:
        orm_mode = True


class MeetingUpdate(BaseModel):
    status: Optional[str] = None
    transcript: Optional[str] = None
    speaker_diarization: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    fundraising_copy: Optional[str] = None
    merit_list: Optional[str] = None
    markdown_file: Optional[str] = None


class TranscriptionResult(BaseModel):
    transcript: str
    segments: List[Dict[str, Any]]


class SpeakerDiarizationResult(BaseModel):
    segments: List[Dict[str, Any]]


class DonorBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    amount: str
    blessing_content: Optional[str] = None


class DonorCreate(DonorBase):
    pass


class Donor(DonorBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class EmailRequest(BaseModel):
    to_emails: List[str]
    subject: str
    markdown_content: str


class ProcessAudioRequest(BaseModel):
    meeting_id: int
    audio_file_path: str
