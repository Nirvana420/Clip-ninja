from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logic
import os

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'processed_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/trim-video", methods=["POST"])
def trim_video():
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ["youtube_url", "start_time", "duration"]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Process video
        output_file = logic.process_video(
            data["youtube_url"],
            data["start_time"],
            data["duration"]
        )
        
        # Move to uploads folder
        final_path = os.path.join(UPLOAD_FOLDER, secure_filename(output_file))
        os.rename(output_file, final_path)
        
        return jsonify({
            "status": "success",
            "download_url": f"/download/{os.path.basename(final_path)}",
            "filename": os.path.basename(final_path)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        secure_filename(filename),
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(port=5000, debug=True)