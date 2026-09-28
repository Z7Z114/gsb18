import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..services.ai_service import ai_service
from ..services.document_service import document_service, email_service
from ..config import settings

router = APIRouter(prefix="/meetings", tags=["会议管理"])


@router.post("/", response_model=schemas.Meeting)
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db)):
    hall = db.query(models.Hall).filter(models.Hall.id == meeting.hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="殿堂不存在")

    db_meeting = models.Meeting(
        hall_id=meeting.hall_id,
        title=meeting.title,
        date=meeting.date,
        participants=meeting.participants,
        status="created",
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


@router.get("/", response_model=List[schemas.Meeting])
def get_meetings(hall_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Meeting)
    # 只要带了 hall_id（包括 0）就必须严格过滤，不用真值判断
    if hall_id is not None:
        query = query.filter(models.Meeting.hall_id == hall_id)
    meetings = (
        query.order_by(models.Meeting.date.desc(), models.Meeting.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return meetings


@router.get("/{meeting_id}", response_model=schemas.Meeting)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


@router.post("/{meeting_id}/upload-audio")
async def upload_audio(meeting_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    # 只取客户端文件名的最后一段，剥离目录分隔符与 ..
    # （Windows 风格的反斜杠分隔符也要防住）
    raw_name = file.filename or ""
    raw_name = raw_name.replace("\\", "/").replace("/", os.sep)
    safe_name = os.path.basename(raw_name).replace("..", "").lstrip(os.sep).strip()
    if not safe_name or safe_name in (os.curdir, os.pardir):
        safe_name = "audio"

    audio_dir = os.path.abspath(settings.TEMP_AUDIO_DIR)
    os.makedirs(audio_dir, exist_ok=True)
    file_location = os.path.abspath(
        os.path.join(audio_dir, f"meeting_{meeting_id}_{safe_name}")
    )

    # 双保险：最终落盘路径必须真实位于 TEMP_AUDIO_DIR 之内
    if os.path.commonpath([audio_dir, file_location]) != audio_dir:
        raise HTTPException(status_code=400, detail="非法的音频文件名")

    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    meeting.audio_file_path = file_location
    meeting.status = "audio_uploaded"
    db.commit()

    return {
        "message": "音频上传成功",
        "file_path": file_location,
    }


@router.post("/{meeting_id}/process")
async def process_meeting(meeting_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    if not meeting.audio_file_path:
        raise HTTPException(status_code=400, detail="请先上传会议音频")

    if not os.path.exists(meeting.audio_file_path):
        raise HTTPException(status_code=400, detail="音频文件不存在")

    meeting.status = "processing"
    db.commit()

    background_tasks.add_task(process_meeting_audio, meeting_id, db)

    return {
        "message": "会议处理已开始，请稍后查看结果",
        "meeting_id": meeting_id,
        "status": "processing",
    }


async def process_meeting_audio(meeting_id: int, db: Session):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        return

    try:
        transcript_result = await ai_service.transcribe_audio(meeting.audio_file_path)
        meeting.transcript = transcript_result["transcript"]

        speaker_segments = await ai_service.diarize_speakers(meeting.audio_file_path)
        meeting.speaker_diarization = {"segments": speaker_segments}

        aligned_segments = ai_service.align_transcript_with_speakers(
            transcript_result["segments"],
            speaker_segments,
        )

        speaker_roles = await ai_service.identify_speaker_roles(aligned_segments)

        db.query(models.DialogueTurn).filter(models.DialogueTurn.meeting_id == meeting_id).delete()

        dialogue_rows = []
        for seg in aligned_segments:
            speaker = seg["speaker"]
            dialogue = models.DialogueTurn(
                meeting_id=meeting_id,
                speaker=speaker,
                speaker_role=speaker_roles.get(speaker, "未知"),
                content=seg["text"],
                timestamp=f"{seg['start']:.1f}s - {seg['end']:.1f}s",
            )
            db.add(dialogue)
            dialogue_rows.append(dialogue)

        hall = meeting.hall
        hall_info = {
            "name": hall.name,
            "description": hall.description,
            "damage_details": hall.damage_details,
            "repair_plan": hall.repair_plan,
            "estimated_cost": hall.estimated_cost,
        } if hall else {}

        meeting.summary = await ai_service.generate_meeting_summary(
            meeting.transcript, hall_info
        )

        meeting.fundraising_copy = await ai_service.generate_fundraising_copy(
            meeting.summary, hall_info
        )

        meeting.merit_list = await ai_service.generate_merit_list(
            meeting.fundraising_copy
        )

        dialogue_list = [
            {
                "speaker": d.speaker,
                "speaker_role": d.speaker_role,
                "content": d.content,
                "timestamp": d.timestamp,
            }
            for d in dialogue_rows
        ]

        markdown_content = document_service.generate_merit_markdown(
            meeting_info={
                "title": meeting.title,
                "date": meeting.date,
            },
            hall_info=hall_info,
            summary=meeting.summary,
            fundraising_copy=meeting.fundraising_copy,
            merit_list=meeting.merit_list,
            dialogue_turns=dialogue_list,
        )

        meeting.markdown_file = document_service.save_markdown(
            markdown_content, f"功德纪要_会议{meeting_id}_{datetime.now().strftime('%Y%m%d')}.md"
        )

        meeting.status = "completed"
        db.commit()

    except Exception as e:
        meeting.status = "failed"
        db.commit()
        print(f"处理会议 {meeting_id} 时出错: {str(e)}")


@router.get("/{meeting_id}/download-markdown")
def download_markdown(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    if not meeting.markdown_file or not os.path.exists(meeting.markdown_file):
        raise HTTPException(status_code=404, detail="Markdown文件不存在")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=meeting.markdown_file,
        filename=os.path.basename(meeting.markdown_file),
        media_type="text/markdown",
    )


@router.post("/{meeting_id}/send-emails")
def send_emails(meeting_id: int, email_request: schemas.EmailRequest, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    html_content = document_service.markdown_to_html(email_request.markdown_content)

    result = email_service.send_email(
        to_emails=email_request.to_emails,
        subject=email_request.subject,
        markdown_content=email_request.markdown_content,
        html_content=html_content,
    )

    return result


@router.get("/{meeting_id}/dialogue", response_model=List[schemas.DialogueTurn])
def get_meeting_dialogue(meeting_id: int, db: Session = Depends(get_db)):
    dialogue = db.query(models.DialogueTurn).filter(
        models.DialogueTurn.meeting_id == meeting_id
    ).order_by(models.DialogueTurn.id).all()
    return dialogue
