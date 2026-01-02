from fastapi import FastAPI
import whisper
import subprocess
import requests

app = FastAPI()
model = whisper.load_model("base")

@app.post("/process")
def process_video(video_url: str, shorts: int = 3, length: int = 30):

    # 1. Download video (yt-dlp)
    subprocess.run(["yt-dlp", "-f", "mp4", video_url, "-o", "video.mp4"])

    # 2. Transcribe
    result = model.transcribe("video.mp4")

    # 3. Pick best timestamps (simple logic)
    segments = result["segments"]
    picks = segments[:shorts]

    outputs = []

    for i, seg in enumerate(picks):
        start = max(0, seg["start"])
        subprocess.run([
            "ffmpeg", "-i", "video.mp4",
            "-ss", str(start),
            "-t", str(length),
            f"short_{i}.mp4"
        ])

        # 4. Generate title (Groq / LLM)
        title = f"Viral Moment #{i+1}"
        desc = f"Best part from the video\n#shorts #viral"

        outputs.append({
            "file": f"short_{i}.mp4",
            "title": title,
            "description": desc
        })

    return outputs
