import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(req: NextRequest) {
  try {
    const { videoUrl, startTime, endTime } = await req.json();
    if (!videoUrl || !startTime || !endTime) {
      return NextResponse.json({ error: "Missing parameters" }, { status: 400 });
    }

    // Calculate duration in HH:MM:SS
    function toSeconds(time: string) {
      const parts = time.split(":").map(Number);
      if (parts.length === 2) return parts[0] * 60 + parts[1];
      if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
      return 0;
    }
    const durationSec = toSeconds(endTime) - toSeconds(startTime);
    if (durationSec <= 0) {
      return NextResponse.json({ error: "End time must be after start time." }, { status: 400 });
    }
    const duration = [
      Math.floor(durationSec / 3600).toString().padStart(2, "0"),
      Math.floor((durationSec % 3600) / 60).toString().padStart(2, "0"),
      (durationSec % 60).toString().padStart(2, "0"),
    ].join(":");

    // Path to the Python script
    const scriptPath = path.join(process.cwd(), "server", "deepseek-v.4.py");

    // Spawn the Python process
    const py = spawn("python", [scriptPath, videoUrl, startTime, duration]);

    let output = "";
    let error = "";
    py.stdout.on("data", (data) => {
      output += data.toString();
    });
    py.stderr.on("data", (data) => {
      error += data.toString();
    });

    return await new Promise((resolve) => {
      py.on("close", (code) => {
        if (code === 0) {
          // Try to extract the output file path from the script's output
          const match = output.match(/Saved to: (.*\.mp4)/);
          const filePath = match ? match[1] : null;
          resolve(
            NextResponse.json({
              message: "Clip processed successfully!",
              filePath,
              output,
            })
          );
        } else {
          resolve(
            NextResponse.json({
              error: error || "Python script failed",
              output,
            }, { status: 500 })
          );
        }
      });
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
