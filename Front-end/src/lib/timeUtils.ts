export function timeStringToSeconds(timeStr: string): number {
  const parts = timeStr.split(':').map(Number);
  if (parts.some(isNaN)) return NaN;

  if (parts.length === 2) { // MM:SS
    if (parts[0] < 0 || parts[0] > 59 || parts[1] < 0 || parts[1] > 59) return NaN;
    return parts[0] * 60 + parts[1];
  } else if (parts.length === 3) { // HH:MM:SS
    if (parts[0] < 0 || parts[1] < 0 || parts[1] > 59 || parts[2] < 0 || parts[2] > 59) return NaN;
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }
  return NaN; // Invalid format
}

export function secondsToTimeString(totalSeconds: number): string {
  if (isNaN(totalSeconds) || totalSeconds < 0) return "00:00";
  
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  const paddedMinutes = String(minutes).padStart(2, '0');
  const paddedSeconds = String(seconds).padStart(2, '0');

  if (hours > 0) {
    const paddedHours = String(hours).padStart(2, '0');
    return `${paddedHours}:${paddedMinutes}:${paddedSeconds}`;
  }
  return `${paddedMinutes}:${paddedSeconds}`;
}

export function extractYouTubeVideoId(url: string): string | null {
  const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
