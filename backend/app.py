from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logic
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)
limiter = Limiter(app=app, key_func=get_remote_address)

# Configuration - Use the same output directory as logic.py
OUTPUT_FOLDER = 'outputs'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/trim-video", methods=["POST"])
@limiter.limit("5 per minute")
def trim_video():
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ["youtube_url", "start_time", "duration"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Process video with progress tracking
        result = logic.process_video(
            youtube_url=data["youtube_url"],
            start_time=data["start_time"],
            duration=data["duration"],
            progress_callback=None  # Add real progress callback if needed
        )
        
        # Verify the file exists
        output_path = Path(result["output_file"])
        if not output_path.exists():
            raise FileNotFoundError("Processed file not found")
        
        return jsonify({
            "status": "success",
            "download_url": f"/download/{output_path.name}",
            "filename": output_path.name,
            "file_size": result["file_size"]
        })
        
    except Exception as e:
        # Clean up any partial files
        if 'output_path' in locals() and output_path.exists():
            output_path.unlink()
        return jsonify({
            "error": str(e),
            "message": "Video processing failed"
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        OUTPUT_FOLDER,
        filename,
        as_attachment=True,
        mimetype='video/mp4'
    )

@app.route('/api/process_video_sse', methods=['POST'])
def api_process_video_sse():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    start_time = data.get('start_time')
    duration = data.get('duration')
    return Response(stream_with_context(logic.process_video_sse(youtube_url, start_time, duration)), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)