from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path, Request
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
import asyncio
import sqlite3

app = FastAPI(title="WhatsApp Announcement Chatbot")

# Create an SQLite3 database file
conn = sqlite3.connect("announcements.db")

# Create a table to store the announcements
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    send_at DATETIME NOT NULL,
    sent_to TEXT NOT NULL
)"""
)

conn.commit()

# Define the employee list
employees = range(1, 1001)


class AnnouncementRequestBody(BaseModel):
    content: str
    send_at: datetime


class Announcement:
    def __init__(self, content: str, send_at: datetime):
        self.content = content
        self.send_at = send_at
        self.sent_to: List[int] = []


class AnnouncementManager:
    def __init__(self):
        self.announcements = []
        self.conn = sqlite3.connect("announcements.db")
        self.c = self.conn.cursor()

    async def create_announcement(self, content: str, send_at: datetime) -> None:
        announcement = Announcement(content, send_at)
        self.announcements.append(announcement)

        # Convert the send_at datetime object to an offset-aware datetime object
        send_at = send_at.astimezone(timezone.utc)

        # Calculate time to wait until sending
        delay = (send_at - datetime.now()).total_seconds()
        if delay < 0:
            delay = 0

        # Schedule the job
        asyncio.create_task(self.send_announcement(announcement, delay))

    async def send_announcement(self, announcement: Announcement, delay: float) -> None:
        """
        This function waits for the necessary time, then "sends" the announcement.

        In a real-world application, this would be a call to the WhatsApp API or another messaging platform.
        """
        await asyncio.sleep(delay)

        # Insert the announcement into the database
        self.c.execute(
            "INSERT INTO announcements (content, send_at, sent_to) VALUES (?, ?, ?)",
            (announcement.content, announcement.send_at, ""),
        )
        announcement_id = self.c.lastrowid

        self.conn.commit()

        # Send the announcement to the employees
        for employee in employees:
            if employee not in announcement.sent_to:
                print(f"Sending '{announcement.content}' to employee number {employee}")
                announcement.sent_to.append(employee)

                # Update the announcement in the database
                self.c.execute(
                    "UPDATE announcements SET sent_to = ? WHERE id = ?",
                    (f"{announcement.sent_to}, {employee}", announcement_id),
                )

                self.conn.commit()

    async def get_announcement_by_id(self, announcement_id: int) -> Announcement:
        """
        Returns an announcement by its ID.
        """
        self.c.execute("SELECT * FROM announcements WHERE id = ?", (announcement_id,))
        announcement = self.c.fetchone()

        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        return Announcement(announcement[1], announcement[2], announcement[3])

    async def get_all_announcements(self) -> List[Announcement]:
        """
        Returns all announcements.
        """
        self.c.execute("SELECT * FROM announcements ORDER BY send_at DESC")
        announcements = self.c.fetchall()

        return [
            Announcement(announcement[1], announcement[2], announcement[3])
            for announcement in announcements
        ]

    async def get_announcement_sent_to(self, announcement_id: int) -> List[int]:
        """
        Returns a list of the employees to whom the announcement was sent.
        """
        self.c.execute(
            "SELECT sent_to FROM announcements WHERE id = ?", (announcement_id,)
        )
        sent_to = self.c.fetchone()[0].split(",")

        return sent_to


# Create an instance of the announcement manager
announcement_manager = AnnouncementManager()


# Endpoint to send an announcement
@app.post("/send_announcement/")
async def send_announcement(request: Request) -> dict:
    """
    This endpoint creates an announcement and schedules it to be sent at the specified time.
    And validates the request body using Pydantic
    Args:
        request: The request object.

    Returns:
        A JSON object containing the message "Announcement created and scheduled".
    """
    try:
        announcement_request_body = AnnouncementRequestBody(**request.json())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    # Create the announcement
    await announcement_manager.create_announcement(
        announcement_request_body.content,
        announcement_request_body.send_at,
    )

    return {"message": "Announcement created and scheduled"}


@app.get("/announcements/{announcement_id}/")
async def get_announcement_by_id(announcement_id: int):
    """
    This endpoint gets an announcement by its ID.

    Args:
        announcement_id: The ID of the announcement to get.

    Returns:
        A JSON object containing the announcement.
    """
    try:
        announcement = await announcement_manager.get_announcement_by_id(
            announcement_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return announcement


@app.get("/announcements/")
async def get_all_announcements():
    """
    This endpoint gets all announcements.

    Returns:
        A JSON list containing the announcements.
    """
    try:
        announcements = await announcement_manager.get_all_announcements()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return announcements


@app.get("/announcements/{announcement_id}/sent_to/")
async def get_announcement_sent_to(announcement_id: int) -> List[int]:
    """
    This endpoint gets the employees to whom an announcement was sent.

    Args:
        announcement_id: The ID of the announcement to get the sent_to list for.

    Returns:
        A JSON list containing the employee IDs.
    """
    try:
        sent_to = await announcement_manager.get_announcement_sent_to(announcement_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return sent_to


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
