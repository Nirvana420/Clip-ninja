import subprocess
import json
import sys
import os
import re

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
    # Remove special characters and sanitize
    title = re.sub(r'[^\w\-_\. ]', '_', title)
    return title[:50]  # Limit length to avoid long filenames

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
    """Convert video to Premiere-compatible format, copying audio when possible"""
    video_args = [
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p"
    ]

    # Detect audio codec
    audio_codec = get_audio_codec(input_file)

    ffmpeg_cmd = ["ffmpeg", "-i", input_file]

    # Map video stream
    ffmpeg_cmd += ["-map", "0:v:0"]

    # Copy or re-encode audio based on codec
    if audio_codec in ['aac', 'mp3']:
        # Copy audio directly if it's already compatible
        ffmpeg_cmd += ["-c:a", "copy", "-map", "0:a:0"]
    else:
        # Re-encode audio to AAC at 256k (one step below 320k) if not compatible
        ffmpeg_cmd += [
            "-c:a", "aac", "-b:a", "256k", "-map", "0:a:0"
        ]

    # Add video args and output options
    ffmpeg_cmd += video_args + [
        "-movflags", "+faststart",
        "-threads", "4",
        output_file
    ]

    subprocess.run(ffmpeg_cmd, check=True)

def main():
    if len(sys.argv) < 4:
        print("Usage: python trim_youtube.py <youtube_url> <start_time> <duration>")
        print("Example: python trim_youtube.py 'https://youtu.be/dQw4w9WgXcQ'  00:01:30 00:00:15")
        sys.exit(1)

    youtube_url = sys.argv[1]
    start_time = sys.argv[2]
    duration = sys.argv[3]

    # Get video title for filename
    video_title = get_video_title(youtube_url)
    base_filename = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
    temp_file = f"temp_{base_filename}.mp4"
    output_file = f"{base_filename}.mp4"

    # Avoid overwriting existing files
    counter = 1
    while os.path.exists(output_file):
        output_file = f"{base_filename}_{counter}.mp4"
        counter += 1

    # Step 1: Download only the trimmed segment
    print(f"⏳ Downloading trimmed segment: {start_time} to {duration}...")
    download_trimmed_segment(youtube_url, start_time, duration, temp_file)

    # Step 2: Convert only if needed
    if is_premiere_compatible(temp_file):
        os.rename(temp_file, output_file)
        print("✅ Trimmed clip is already Premiere-compatible!")
    else:
        print("🔄 Converting to Premiere-compatible format...")
        convert_to_premiere(temp_file, output_file)
        os.remove(temp_file)
        print("✅ Conversion complete!")

    print(f"Saved to: {os.path.abspath(output_file)}")


# Add this to logic.py (at the bottom, before the if __name__ block)
def process_video(youtube_url, start_time, duration, progress_callback=None):
    """Main processing function for Flask API"""
    try:
        # Get video title
        video_title = get_video_title(youtube_url)
        base_filename = f"{video_title}_{start_time.replace(':', '-')}_{duration.replace(':', '-')}"
        temp_file = f"temp_{base_filename}.mp4"
        output_file = f"{base_filename}.mp4"

        # Handle duplicate filenames
        counter = 1
        while os.path.exists(output_file):
            output_file = f"{base_filename}_{counter}.mp4"
            counter += 1

        # Step 1: Download trimmed segment
        if progress_callback:
            progress_callback(10)
        download_trimmed_segment(youtube_url, start_time, duration, temp_file)
        if progress_callback:
            progress_callback(60)

        # Step 2: Convert if needed
        if is_premiere_compatible(temp_file):
            os.rename(temp_file, output_file)
        else:
            convert_to_premiere(temp_file, output_file)
            os.remove(temp_file)
        if progress_callback:
            progress_callback(90)

        if progress_callback:
            progress_callback(100)
        return output_file  # Return the final filename
        
    except Exception as e:
        # Clean up if something went wrong
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        raise  # Re-raise the exception for Flask to handle



if __name__ == "__main__":
    main()