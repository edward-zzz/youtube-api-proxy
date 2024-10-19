import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .youtube_reader import TranscriptRequest, TranscriptResponse, YoutubeReader


logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

app = FastAPI()

youtube_reader = YoutubeReader()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"message": "OK"}


@app.post("/v1/transcripts", response_model=List[TranscriptResponse])
async def get_transcripts(request: TranscriptRequest):
    try:
        transcripts = youtube_reader.load_data(request.ytlinks)
        response = [
            TranscriptResponse(video_id=video_id, transcript=transcript)
            for (video_id, transcript) in transcripts
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return response
