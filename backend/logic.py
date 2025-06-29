import subprocess
import json
import sys
import os
import re
import uuid
from pathlib import Path
from datetime import datetime
import shutil
from flask import Flask, Response, request, stream_with_context, jsonify
import time

class FileManager:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.temp_dir = self.base_dir / "temp"
        self.output_dir = self.base_dir / "outputs"
        self._setup_directories()
        
    def _setup_directories(self):
        """Create required directories if they don't exist"""
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def create_temp_file(self, prefix="temp_", suffix=".mp4"):
        """Create a unique temp file path"""
        temp_filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
        return self.temp_dir / temp_filename
        
    def create_output_filename(self, base_name):
        """Create a collision-free output filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = self.sanitize_filename(base_name)
        return self.output_dir / f"{timestamp}_{base_name}.mp4"
        
    @staticmethod
    def sanitize_filename(filename):
        """Make filenames safe"""
        filename = re.sub(r'[^\w\-_\. ]', '_', filename)
        return filename[:100]  # Reasonable length limit
    
file_manager = FileManager()

def get_video_title(youtube_url):
    """Extract video title using yt-dlp"""
    result = subprocess.run(
        ["yt-dlp", "--get-title", youtube_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print("Error getting video title:", result.stderr)
        return "trimmed_video"
    title = result.stdout.strip()
    title = re.sub(r'[^\w\-_\. ]', '_', title)
    return title[:50]

def is_premiere_compatible(file_path):
    """Check if file is natively Premiere Pro compatible"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name", "-of", "json", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        return False
    info = json.loads(result.stdout)
    video_codec = info['streams'][0]['codec_name'].lower()
    return video_codec in ['h264', 'avc', 'prores', 'dnxhd']

def get_audio_codec(file_path):
    """Detect audio codec using ffprobe"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name", "-of", "json", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        return None
    try:
        info = json.loads(result.stdout)
        return info['streams'][0]['codec_name'].lower()
    except (IndexError, KeyError):
        return None

def download_trimmed_segment(youtube_url, start_time, duration, temp_file):
    """Download only the trimmed segment without full download"""
    urls = subprocess.run(
        ["yt-dlp", "-f", "bestvideo+bestaudio", "-g", youtube_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    ).stdout.strip().split('\n')
    ffmpeg_cmd = [
        "ffmpeg",
        "-ss", start_time,
        "-i", urls[0],
        *(["-ss", start_time, "-i", urls[1]] if len(urls) > 1 else []),
        "-t", duration,
        "-c", "copy",
        temp_file
    ]
    if len(urls) > 1:
        ffmpeg_cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
    subprocess.run(ffmpeg_cmd, check=True)

def convert_to_premiere(input_file, output_file):
    """Convert video to Premiere-compatible format with faster conversion"""
    video_args = [
    "-c:v", "libx264", 
    "-crf", "21",  
    "-preset", "superfast",
    "-pix_fmt", "yuv420p",
    "-x264-params", "ref=4:me=hex"
]

    audio_codec = get_audio_codec(input_file)

    ffmpeg_cmd = ["ffmpeg", "-i", input_file]
    ffmpeg_cmd += ["-map", "0:v:0"]

    if audio_codec in ['aac', 'mp3']:
        ffmpeg_cmd += ["-c:a", "copy"]
    else:
        ffmpeg_cmd += [
            "-c:a", "aac", 
            "-b:a", "192k"  # Reduced from 256k for faster encoding
        ]
    ffmpeg_cmd += ["-map", "0:a:0"]

    ffmpeg_cmd += video_args + [
        "-movflags", "+faststart",
        "-threads", "0",  # Let ffmpeg decide optimal thread count
        output_file
    ]

    subprocess.run(ffmpeg_cmd, check=True)

def process_video(youtube_url, start_time, duration, progress_callback=None):
    """Main processing function for both Flask API and CLI"""
    try:
        video_title = get_video_title(youtube_url)
        base_name = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
        
        temp_file = file_manager.create_temp_file()
        output_file = file_manager.create_output_filename(base_name)
        
        if progress_callback:
            progress_callback(10)
            
        download_trimmed_segment(youtube_url, start_time, duration, str(temp_file))
        
        if progress_callback:
            progress_callback(60)
            
        if is_premiere_compatible(str(temp_file)):
            temp_file.rename(output_file)
        else:
            convert_to_premiere(str(temp_file), str(output_file))
            temp_file.unlink()
            
        if progress_callback:
            progress_callback(100)
            
        return {
            "status": "success",
            "output_file": str(output_file),
            "file_size": output_file.stat().st_size // (1024 * 1024)
        }
        
    except Exception as e:
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        raise

# SSE streaming generator
def process_video_sse(youtube_url, start_time, duration):
    def sse_progress(percent, message=None):
        data = {'progress': percent}
        if message:
            data['message'] = message
        yield f"data: {json.dumps(data)}\n\n"

    try:
        video_title = get_video_title(youtube_url)
        base_name = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
        temp_file = file_manager.create_temp_file()
        output_file = file_manager.create_output_filename(base_name)

        yield from sse_progress(10, "Downloading trimmed segment...")
        download_trimmed_segment(youtube_url, start_time, duration, str(temp_file))

        yield from sse_progress(60, "Checking/Converting for Premiere compatibility...")
        if is_premiere_compatible(str(temp_file)):
            temp_file.rename(output_file)
        else:
            convert_to_premiere(str(temp_file), str(output_file))
            temp_file.unlink()

        yield from sse_progress(100, "Done!")
        result = {
            "status": "success",
            "output_file": str(output_file),
            "file_size": output_file.stat().st_size // (1024 * 1024)
        }
        yield f"data: {json.dumps(result)}\n\n"
    except Exception as e:
        error = {'status': 'error', 'message': str(e)}
        yield f"data: {json.dumps(error)}\n\n"

def main():
    if len(sys.argv) < 4:
        print("Usage: python trim_youtube.py <youtube_url> <start_time> <duration>")
        print("Example: python trim_youtube.py 'https://youtu.be/dQw4w9WgXcQ' 00:01:30 00:00:15")
        sys.exit(1)

    youtube_url = sys.argv[1]
    start_time = sys.argv[2]
    duration = sys.argv[3]

    result = process_video(youtube_url, start_time, duration)
    print(f"✅ Processing complete! Saved to: {result['output_file']} ({result['file_size']} MB)")

if __name__ == "__main__":
    main()