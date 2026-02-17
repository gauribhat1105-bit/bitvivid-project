import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
from models import Place, Camera

from ai.deepgram_stt import transcribe_audio
from ai.llm import analyze_command
from logic.command_parser import process_command
from database import get_db
from sqlalchemy.orm import Session

from logic.command_executor import execute_command

app = FastAPI()


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
def root():
    return {"status": "CCTV Voice Agent Backend Running"}


# Voice endpoint
@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    audio_bytes = await file.read()

    transcript = await transcribe_audio(audio_bytes)

    if not transcript:
        return {
            "success": False,
            "error": "Could not transcribe audio"
        }

    llm_output = await analyze_command(transcript)

    command = process_command(llm_output)

    execution = await execute_command(command, db)

    return {
        "spoken_text": transcript,
        "command": command,
        "execution": execution
    }



# GET places
@app.get("/places")
def get_places(db: Session = Depends(get_db)):

    places = db.query(Place).all()

    return places


# POST place
@app.post("/places")
def create_place(place: dict, db: Session = Depends(get_db)):

    new_place = Place(
        name=place.get("name"),
        location=place.get("location"),
        description=place.get("description"),
        cameras=place.get("cameras", 0)
    )

    db.add(new_place)
    db.commit()
    db.refresh(new_place)

    return new_place


# DELETE place
@app.delete("/places/{id}")
def delete_place(id: str, db: Session = Depends(get_db)):

    place = db.query(Place).filter(Place.id == id).first()

    if not place:
        raise HTTPException(404, "Place not found")

    db.delete(place)
    db.commit()

    return {"message": "Place deleted"}


# GET cameras
@app.get("/cameras")
def get_cameras(
    placeId: str = None,
    db: Session = Depends(get_db)
):

    if placeId:
        cameras = db.query(Camera).filter(Camera.placeId == placeId).all()
    else:
        cameras = db.query(Camera).all()

    return cameras


# POST camera
@app.post("/cameras")
def create_camera(camera: dict, db: Session = Depends(get_db)):

    new_camera = Camera(
        name=camera.get("name"),
        streamUrl=camera.get("streamUrl"),
        type=camera.get("type"),
        status=camera.get("status"),
        placeId=camera.get("placeId")
    )

    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)

    return new_camera


# DELETE camera
@app.delete("/cameras/{id}")
def delete_camera(id: str, db: Session = Depends(get_db)):

    camera = db.query(Camera).filter(Camera.id == id).first()

    if not camera:
        raise HTTPException(404, "Camera not found")

    db.delete(camera)
    db.commit()

    return {"message": "Camera deleted"}

from vision.vision_executor import process_vision

@app.get("/test-vlm")
async def test_vlm():

    result = await process_vision(
        "https://www.w3schools.com/html/mov_bbb.mp4"
    )

    return result
