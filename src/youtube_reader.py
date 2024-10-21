import re
from typing import Any, List, Optional

from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi


YOUTUBE_URL_PATTERNS = [
    r"^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)",
    r"^https?://(?:www\.)?youtube\.com/embed/([\w-]+)",
    r"^https?://youtu\.be/([\w-]+)",  # youtu.be does not use www
]


class YoutubeReader:

    def load_data(
        self,
        ytlinks: List[str],
        languages: List[str] | None = ["en"],
        proxies: Any | None = None,
    ):
        """Load data from the input directory.

        Args:
            pages (List[str]): List of youtube links \
                for which transcripts are to be read.

        """
        results = []
        for link in ytlinks:
            video_id = self._extract_video_id(link)
            if not video_id:
                raise ValueError(
                    f"Supplied url {link} is not a supported youtube URL."
                    "Supported formats include:"
                    "  youtube.com/watch?v=\\{video_id\\} "
                    "(with or without 'www.')\n"
                    "  youtube.com/embed?v=\\{video_id\\} "
                    "(with or without 'www.')\n"
                    "  youtu.be/{video_id\\} (never includes www subdomain)"
                )
            transcript_chunks = YouTubeTranscriptApi.get_transcript(
                video_id, languages=languages, proxies=proxies
            )
            # chunk_text = [chunk["text"] for chunk in transcript_chunks]
            # transcript = "\n".join(chunk_text)

            transcript = self.aggregate_transcript(transcript_chunks, 90)
            results.append((video_id, transcript))
        return results

    def aggregate_transcript(self, chunks: Any, min_duration: int = 60):
        cur_text = ""
        cur_start = 0.0

        aggregated_transcript = []
        for i, snippet in enumerate(chunks):
            text = snippet["text"]
            start_time = snippet["start"]
            duration = snippet["duration"]

            cur_text += text
            cur_duration = round(start_time + duration - cur_start, 3)

            if cur_duration > min_duration:
                aggregated_transcript.append(
                    {
                        "text": cur_text.strip(),
                        "start": cur_start,
                        "duration": cur_duration,
                    }
                )
                cur_text = ""
                cur_start = round(start_time + duration, 3)
                continue

            if i == len(chunks) - 1:
                aggregated_transcript.append(
                    {
                        "text": cur_text.strip(),
                        "start": cur_start,
                        "duration": cur_duration,
                    }
                )

        return aggregated_transcript

    @staticmethod
    def _extract_video_id(yt_link) -> Optional[str]:
        for pattern in YOUTUBE_URL_PATTERNS:
            match = re.search(pattern, yt_link)
            if match:
                return match.group(1)

        # return None if no match is found
        return None


class TranscriptRequest(BaseModel):
    ytlinks: List[str]


class TranscriptResponse(BaseModel):
    video_id: str
    transcript: Any
