import subprocess
import json
import sys
import os
import re
import uuid
from pathlib import Path
from datetime import datetime
import shutil
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

# Add cookies support
COOKIES_PATH = os.environ.get("COOKIES_PATH", "cookies.txt")

def get_cookies_args():
    """Return cookies arguments if valid cookies file exists"""
    if Path(COOKIES_PATH).exists():
        return ["--cookies", COOKIES_PATH]
    print("⚠️ Cookies file not found, proceeding without authentication")
    return []

def get_video_info(youtube_url):
    """Get video title and stream URLs in one request"""
    try:
        def yt_dlp_command(args):
            return ["yt-dlp", *args]

        cmd = yt_dlp_command([
            "--get-title",
            "--get-url",
            "-f", "bestvideo+bestaudio",
            *get_cookies_args(),
            "--", youtube_url
        ])

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        output = result.stdout.strip().split('\n')
        if not output:
            raise ValueError("No data received from YouTube")

        title = output[0].strip()
        title = re.sub(r'[\w\-_\. ]', '_', title)
        stream_urls = [url.strip() for url in output[1:] if url.strip()]

        if not stream_urls:
            raise ValueError("No stream URLs found")

        return {
            'title': title[:50],
            'stream_urls': stream_urls
        }
    except subprocess.CalledProcessError as e:
        error_msg = f"Error getting video info: {e.stderr}"
        print(error_msg)
        raise ValueError(error_msg) from e

def is_editing_compatible(file_path):
    """Check if file is compatible with editing software (Premiere, DaVinci, Final Cut)"""
    try:
        # Get both video and audio codecs in one command
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", 
             "-select_streams", "v:0,a:0", "-of", "json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        info = json.loads(result.stdout)
        
        video_codec = ""
        audio_codec = ""
        
        # Extract codecs from streams
        for stream in info.get('streams', []):
            codec_type = stream.get('codec_type', '')
            codec_name = stream.get('codec_name', '').lower()
            
            if codec_type == 'video' and not video_codec:
                video_codec = codec_name
            elif codec_type == 'audio' and not audio_codec:
                audio_codec = codec_name
        
        # Supported codecs for major editing software
        supported_video = {'h264', 'avc', 'prores', 'dnxhd', 'dnxhr', 'mpeg4', 'h265', 'hevc'}
        supported_audio = {'aac', 'mp3', 'pcm_s16le', 'pcm_s24le', 'flac'}
        
        return (video_codec in supported_video and 
                audio_codec in supported_audio)
                
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Compatibility check failed: {str(e)}")
        return False

def get_audio_codec(file_path):
    """Detect audio codec using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        info = json.loads(result.stdout)
        return info['streams'][0]['codec_name'].lower()
    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError, KeyError) as e:
        print(f"Audio codec detection failed: {str(e)}")
        return None

def download_trimmed_segment(stream_urls, start_time, duration, temp_file):
    """Download only the trimmed segment using pre-fetched URLs"""
    try:
        if not stream_urls:
            raise ValueError("No streams provided for download")
            
        ffmpeg_cmd = [
            "ffmpeg",
            "-ss", start_time,
            "-i", stream_urls[0],
        ]
        
        # Add audio stream if available
        if len(stream_urls) > 1:
            ffmpeg_cmd.extend(["-ss", start_time, "-i", stream_urls[1]])
        
        ffmpeg_cmd.extend([
            "-t", duration,
            "-c:v", "copy",
            "-c:a", "copy"
        ])
        
        # Handle stream mapping
        if len(stream_urls) > 1:
            ffmpeg_cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
        else:
            ffmpeg_cmd.extend(["-map", "0:v:0", "-map", "0:a:0?"])
        
        ffmpeg_cmd.append(str(temp_file))
        
        subprocess.run(ffmpeg_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Download failed: {e.stderr}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

def convert_to_premiere(input_file, output_file):
    """Convert video to editing-compatible format"""
    try:
        video_args = [
            "-c:v", "libx264", 
            "-crf", "21",  
            "-preset", "superfast",
            "-pix_fmt", "yuv420p",
            "-x264-params", "ref=4:me=hex"
        ]

        audio_codec = get_audio_codec(input_file)
        ffmpeg_cmd = ["ffmpeg", "-i", str(input_file)]

        # Handle audio streams
        if audio_codec in ['aac', 'mp3']:
            ffmpeg_cmd.extend(["-c:a", "copy"])
        else:
            ffmpeg_cmd.extend([
                "-c:a", "aac", 
                "-b:a", "192k"
            ])
        
        ffmpeg_cmd.extend([
            "-map", "0:v:0",
            "-map", "0:a:0?"
        ])
        
        ffmpeg_cmd.extend(video_args)
        ffmpeg_cmd.extend([
            "-movflags", "+faststart",
            "-threads", "0",
            str(output_file)
        ])

        subprocess.run(ffmpeg_cmd, check=True)
    
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e.stderr}")
        raise

def process_video_sse(youtube_url, start_time, duration):
    """SSE version of process_video that yields progress updates"""
    print("[DEBUG] process_video_sse called")
    try:
        try:
            from .logger import log_video_event  # Try relative import (package mode)
        except ImportError:
            from logger import log_video_event  # Fallback to absolute import (script mode)
    except Exception as import_err:
        print(f"Logger import failed: {import_err}")
        def log_video_event(*a, **kw):
            pass  # Dummy logger if import fails
    try:
        # Get all info in one request
        video_info = get_video_info(youtube_url)
        video_title = video_info['title']
        stream_urls = video_info['stream_urls']
        
        base_name = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
        
        temp_file = file_manager.create_temp_file()
        output_file = file_manager.create_output_filename(base_name)
        
        # Progress update: 10%
        yield f"data: {json.dumps({'progress': 10})}\n\n"
        
        # Simulate more granular progress during download
        time.sleep(0.2)
        yield f"data: {json.dumps({'progress': 20})}\n\n"
        time.sleep(0.2)
        yield f"data: {json.dumps({'progress': 30})}\n\n"
        time.sleep(0.2)
        yield f"data: {json.dumps({'progress': 40})}\n\n"
        
        # Download phase
        download_trimmed_segment(stream_urls, start_time, duration, temp_file)
        
        # Progress update: 60%
        yield f"data: {json.dumps({'progress': 60})}\n\n"
        
        # Check compatibility and convert if needed
        if is_editing_compatible(str(temp_file)):
            temp_file.rename(output_file)
            message = "File is already editing-compatible"
        else:
            convert_to_premiere(str(temp_file), str(output_file))
            temp_file.unlink()
            message = "File converted to editing-compatible format"
        
        # Progress update: 100%
        yield f"data: {json.dumps({'progress': 100})}\n\n"
        # Final result
        log_video_event(youtube_url, "success")
        yield f"data: {json.dumps({
            'status': 'success',
            'output_file': str(output_file),
            'file_size': output_file.stat().st_size // (1024 * 1024),
            'message': message
        })}\n\n"
    except Exception as e:
        error_msg = str(e)
        log_video_event(youtube_url, "error", error_msg)
        yield f"data: {json.dumps({
            'status': 'error',
            'message': error_msg
        })}\n\n"
        
        # Clean up files if they exist
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        if 'output_file' in locals() and output_file.exists():
            output_file.unlink()

def process_video(youtube_url, start_time, duration, progress_callback=None):
    """Main processing function for both Flask API and CLI"""
    
    print("[DEBUG] process_video called")
    try:
        try:
            from .logger import log_video_event  # Try relative import (package mode)
        except ImportError:
            from logger import log_video_event  # Fallback to absolute import (script mode)
    except Exception as import_err:
        print(f"Logger import failed: {import_err}")
        def log_video_event(*a, **kw):
            pass  # Dummy logger if import fails
    temp_file = None
    output_file = None
    
    try:
        # Get all info in one request
        video_info = get_video_info(youtube_url)
        video_title = video_info['title']
        stream_urls = video_info['stream_urls']
        
        base_name = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
        
        temp_file = file_manager.create_temp_file()
        output_file = file_manager.create_output_filename(base_name)
        
        if progress_callback:
            progress_callback(10)
            
        # Download using pre-fetched URLs
        download_trimmed_segment(stream_urls, start_time, duration, str(temp_file))
        
        if progress_callback:
            progress_callback(60)
            
        if is_editing_compatible(str(temp_file)):
            temp_file.rename(output_file)
            print("File is already editing-compatible, skipping conversion")
        else:
            convert_to_premiere(str(temp_file), str(output_file))
            temp_file.unlink()
            print("File converted to editing-compatible format")
            
        if progress_callback:
            progress_callback(100)
            
        # Log success
        log_video_event(youtube_url, "success")
        
        return {
            "status": "success",
            "output_file": str(output_file),
            "file_size": output_file.stat().st_size // (1024 * 1024)
        }
        
    except Exception as e:
        print(f"Processing failed: {str(e)}")
        
        # Clean up temporary files
        if temp_file and temp_file.exists():
            temp_file.unlink()
        
        # Clean up output file if partially created
        if output_file and output_file.exists():
            output_file.unlink()
        
        # Log error
        log_video_event(youtube_url, "error", str(e))
        
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    if len(sys.argv) < 4:
        print("Usage: python trim_youtube.py <youtube_url> <start_time> <duration>")
        print("Example: python trim_youtube.py 'https://youtu.be/dQw4w9WgXcQ' 00:01:30 00:00:15")
        sys.exit(1)

    youtube_url = sys.argv[1]
    start_time = sys.argv[2]
    duration = sys.argv[3]

    result = process_video(youtube_url, start_time, duration)
    if result["status"] == "success":
        print(f"✅ Processing complete! Saved to: {result['output_file']} ({result['file_size']} MB)")
    else:
        print(f"❌ Processing failed: {result['message']}")

if __name__ == "__main__":
    main()