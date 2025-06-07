from flask import Flask, request, jsonify
from flask_cors import CORS
import logic  # Import your logic module

app = Flask(__name__)
CORS(app)

@app.route("/trim-video", methods=["POST"])
def trim_video():
    data = request.get_json()

    youtube_url = data.get("youtube_url")
    start_time = data.get("start_time")
    duration = data.get("duration")

    if not all([youtube_url, start_time, duration]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        output_file = logic.process_video(youtube_url, start_time, duration)
        return jsonify({
            "message": "Video processed successfully!",
            "output_file": output_file
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)