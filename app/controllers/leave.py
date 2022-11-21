from typing import Optional

from flask import abort

from app import db
from app.models import Leave


def create(leave_type: str, start: int, duration: float, note: str = "") -> Leave:
    leave = Leave(leave_type=leave_type, start=start, duration=duration, note=note)
    db.session.add(leave)
    db.session.commit()

    return leave


def update(row_id: int, leave_type: str, start: int, duration: float, note: Optional[str] = None) -> Leave:
    leave = db.session.scalars(db.select(Leave).where(Leave.id == row_id)).first()
    if not leave:
        abort(403)

    leave.leave_type = leave_type
    leave.start = start
    leave.duration = duration
    leave.note = note
    db.session.commit()

    return leave
