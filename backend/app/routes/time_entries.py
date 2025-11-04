from fastapi import APIRouter, Depends, HTTPException
from app.models.time_entry import TimeEntryCreate, TimeEntryResponse
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.db.supabase_client import supabase
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/time-entries", tags=["time-entries"])

@router.post("/start", response_model=TimeEntryResponse)
def start_tracking(
    entry_data: TimeEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """Start tracking time on a task"""

    # Check if user already has a running entry
    response = supabase.from_("time_entries") \
        .select("*") \
        .eq("user_id", str(current_user.id)) \
        .is_("end_time", "null") \
        .execute()

    # Auto-stop existing running entry if found
    if response.data and len(response.data) > 0:
        running_entry = response.data[0]
        start_time = datetime.fromisoformat(running_entry["start_time"].replace("Z", "+00:00"))
        now = datetime.utcnow()
        duration = int((now - start_time).total_seconds())

        supabase.from_("time_entries") \
            .update({
                "end_time": now.isoformat(),
                "duration": duration,
                "updated_at": now.isoformat()
            }) \
            .eq("id", running_entry["id"]) \
            .execute()

    # Create new entry
    now = datetime.utcnow()
    new_entry_data = {
        "task_id": str(entry_data.task_id),
        "user_id": str(current_user.id),
        "start_time": now.isoformat(),
        "description": entry_data.description
    }

    response = supabase.from_("time_entries") \
        .insert(new_entry_data) \
        .execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=500, detail="Failed to create time entry")

    entry = response.data[0]
    return TimeEntryResponse(
        id=entry["id"],
        task_id=entry["task_id"],
        start_time=datetime.fromisoformat(entry["start_time"].replace("Z", "+00:00")),
        status="running"
    )


@router.post("/{entry_id}/stop", response_model=TimeEntryResponse)
def stop_tracking(
    entry_id: int,
    current_user: User = Depends(get_current_user)
):
    """Stop tracking time"""

    # Get entry
    response = supabase.from_("time_entries") \
        .select("*") \
        .eq("id", entry_id) \
        .execute()

    if not response.data or len(response.data) == 0:  # ✅ FIX: Check properly
        raise HTTPException(status_code=404, detail="Time entry not found")

    entry = response.data[0]

    # Verify ownership
    if entry["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to stop this time entry")

    # Check if already stopped
    if entry["end_time"] is not None:
        raise HTTPException(status_code=400, detail="Time entry already stopped")

    # Calculate duration
    start_time = datetime.fromisoformat(entry["start_time"].replace("Z", "+00:00"))
    now = datetime.utcnow()
    duration = int((now - start_time).total_seconds())

    # Update entry
    response = supabase.from_("time_entries") \
        .update({
            "end_time": now.isoformat(),
            "duration": duration,
            "updated_at": now.isoformat()
        }) \
        .eq("id", entry_id) \
        .execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=500, detail="Failed to stop time entry")

    updated_entry = response.data[0]
    return TimeEntryResponse(
        id=updated_entry["id"],
        task_id=updated_entry["task_id"],
        start_time=datetime.fromisoformat(updated_entry["start_time"].replace("Z", "+00:00")),
        status="stopped"
    )


@router.get("/current", response_model=Optional[TimeEntryResponse])
def get_current_entry(
    current_user: User = Depends(get_current_user)
):
    """Get currently running time entry"""

    response = supabase.from_("time_entries") \
        .select("*") \
        .eq("user_id", str(current_user.id)) \
        .is_("end_time", "null") \
        .execute()

    if not response.data or len(response.data) == 0:
        return None

    entry = response.data[0]
    return TimeEntryResponse(
        id=entry["id"],
        task_id=entry["task_id"],
        start_time=datetime.fromisoformat(entry["start_time"].replace("Z", "+00:00")),
        status="running"
    )
