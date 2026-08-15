import os
import glob
import subprocess

ARTIST = "The Weeknd"
ALBUM = "The Weeknd Live At Strawberry Arena 2026"
DISC = "1"

def get_duration(filepath):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0

mov_files = glob.glob("*.MOV")
if not mov_files:
    print("No MOV files found in current directory.")
    exit(1)

# Sort tracks by duration ascending
files_with_durations = [(f, get_duration(f)) for f in mov_files]
files_with_durations.sort(key=lambda x: x[1])

total_tracks = len(files_with_durations)
print(f"Renaming and tagging {total_tracks} video files...\n")

for idx, (filename, duration) in enumerate(files_with_durations, start=1):
    base_name = os.path.splitext(filename)[0]

    if not base_name.lower().endswith("(live)"):
        clean_title = f"{base_name} (live)"
    else:
        clean_title = base_name

    new_filename = f"{clean_title}.MOV"
    tmp_filename = f"temp_{idx}.MOV"

    # Embed metadata into MOV container using stream copy (no re-encoding)
    cmd = [
        "ffmpeg", "-y", "-i", filename,
        "-metadata", f"title={clean_title}",
        "-metadata", f"artist={ARTIST}",
        "-metadata", f"album={ALBUM}",
        "-metadata", f"track={idx}/{total_tracks}",
        "-metadata", f"disc={DISC}",
        "-c", "copy",
        tmp_filename
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Replace original with tagged temp file
    if os.path.exists(tmp_filename):
        if filename != new_filename and os.path.exists(filename):
            os.remove(filename)
        os.rename(tmp_filename, new_filename)

    mins, secs = divmod(int(duration), 60)
    print(f"[{idx:02d}/{total_tracks}] {new_filename} ({mins}:{secs:02d})")

print("\nAll MOV files successfully renamed and tagged!")
