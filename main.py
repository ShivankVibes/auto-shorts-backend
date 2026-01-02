from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper
import subprocess
import os

app = FastAPI()

# CORS (needed for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model("base")

class VideoRequest(BaseModel):
    video_url: str
    shorts: int = 3
    length: int = 30

@app.post("/process")
def process(req: VideoRequest):

    # Clean old files
    for f in os.listdir():
        if f.endswith(".mp4"):
            os.remove(f)

    # Download video
    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        req.video_url,
        "-o", "video.mp4"
    ], check=True)

    # Transcribe
    result = model.transcribe("video.mp4")
    segments = result["segments"][:req.shorts]

    outputs = []

    for i, seg in enumerate(segments):
        start = max(0, seg["start"])

        out_file = f"short_{i+1}.mp4"

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", "video.mp4",
            "-ss", str(start),
            "-t", str(req.length),
            "-vf", "scale=1080:1920",
            out_file
        ], check=True)

        outputs.append({
            "file": out_file,
            "title": f"Viral Moment #{i+1}",
            "description": "Best moment from the video\n#shorts #viral"
        })

    return outputs
