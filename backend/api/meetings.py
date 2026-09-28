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
    if hall_id:
        query = query.filter(models.Meeting.hall_id == hall_id)
    meetings = query.offset(skip).limit(limit).all()
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

    os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)
    file_location = os.path.join(settings.TEMP_AUDIO_DIR, f"meeting_{meeting_id}_{file.filename}")
    
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

        dialogue_turns = db.query(models.DialogueTurn).filter(
            models.DialogueTurn.meeting_id == meeting_id
        ).all()

        dialogue_list = [
            {
                "speaker": d.speaker,
                "speaker_role": d.speaker_role,
                "content": d.content,
                "timestamp": d.timestamp,
            }
            for d in dialogue_turns
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
