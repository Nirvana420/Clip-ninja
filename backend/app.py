from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logic
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuration - Use the same output directory as logic.py
OUTPUT_FOLDER = 'outputs'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/trim-video", methods=["POST"])
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)