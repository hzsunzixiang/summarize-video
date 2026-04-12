#!/usr/bin/env python3
"""Deduplicate extracted video frames by comparing image similarity.

Uses only PIL (Pillow) - no external dependencies beyond standard library + Pillow.
Compares consecutive frames using difference hash (dhash) and keeps only
frames whose hamming distance exceeds the threshold.

Usage:
    python3 dedup_slides.py --input <frames_dir> --output <key_slides_dir> [--threshold 20]
"""

import argparse
import os
import shutil
from pathlib import Path
from PIL import Image


def dhash(image, hash_size=16):
    """Compute difference hash of an image.
    Returns a list of booleans representing the hash bits.
    """
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.LANCZOS)
    pixels = list(resized.getdata())

    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            diff.append(left > right)
    return diff


def hamming_distance(hash1, hash2):
    """Compute Hamming distance between two hashes."""
    return sum(a != b for a, b in zip(hash1, hash2))


def deduplicate_frames(input_dir, output_dir, threshold=20):
    """Keep only frames that differ significantly from the previous kept frame.

    Args:
        input_dir: Directory containing extracted frames (frame_XXXX.jpg)
        output_dir: Directory to store deduplicated key slides (slide_XXXX.jpg)
        threshold: Hash distance threshold; higher = fewer slides kept
    """
    os.makedirs(output_dir, exist_ok=True)

    frames = sorted(Path(input_dir).glob("frame_*.jpg"))
    if not frames:
        print("No frames found!")
        return

    print(f"Total frames: {len(frames)}")

    kept = []
    prev_hash = None

    for frame_path in frames:
        img = Image.open(frame_path)
        curr_hash = dhash(img)

        if prev_hash is None or hamming_distance(curr_hash, prev_hash) > threshold:
            kept.append(frame_path)
            prev_hash = curr_hash

    print(f"Unique slides after dedup: {len(kept)}")

    for i, frame_path in enumerate(kept, 1):
        dest = os.path.join(output_dir, f"slide_{i:04d}.jpg")
        shutil.copy2(str(frame_path), dest)
        # Extract timestamp from frame number (each frame = 30 seconds)
        frame_num = int(frame_path.stem.split("_")[1])
        timestamp_sec = (frame_num - 1) * 30
        minutes = timestamp_sec // 60
        seconds = timestamp_sec % 60
        print(f"  slide_{i:04d}.jpg <- {frame_path.name} (timestamp: {minutes:02d}:{seconds:02d})")

    print(f"\nDone! {len(kept)} key slides saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate extracted video frames using difference hash (dhash)."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Directory containing extracted frames (frame_XXXX.jpg)"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Directory to store deduplicated key slides"
    )
    parser.add_argument(
        "--threshold", "-t", type=int, default=20,
        help="Hamming distance threshold (default: 20). Higher = fewer slides."
    )
    args = parser.parse_args()

    deduplicate_frames(args.input, args.output, args.threshold)


if __name__ == "__main__":
    main()
