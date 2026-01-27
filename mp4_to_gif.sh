#!/bin/bash

# Convert MP4 to GIF with quality control
# Usage: ./mp4_to_gif.sh input.mp4 output.gif [quality]
# Quality: 1-5 (1=lowest quality/smallest size, 5=highest quality/largest size, default=3)

if [ $# -lt 2 ]; then
    echo "Usage: $0 input.mp4 output.gif [quality]"
    echo "Quality: 1-5 (1=lowest, 5=highest, default=3)"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"
QUALITY="${3:-3}"

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found"
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg not found. Please install ffmpeg first."
    exit 1
fi

# Set parameters based on quality level
case $QUALITY in
    1)
        FPS=10
        SCALE=320
        COLORS=64
        ;;
    2)
        FPS=15
        SCALE=480
        COLORS=128
        ;;
    3)
        FPS=20
        SCALE=640
        COLORS=192
        ;;
    4)
        FPS=24
        SCALE=800
        COLORS=224
        ;;
    5)
        FPS=30
        SCALE=-1
        COLORS=256
        ;;
    *)
        echo "Error: Quality must be between 1 and 5"
        exit 1
        ;;
esac

echo "Converting $INPUT to $OUTPUT..."
echo "Quality: $QUALITY (FPS=$FPS, Scale=$SCALE, Colors=$COLORS)"

# Generate palette for better color quality
ffmpeg -i "$INPUT" -vf "fps=$FPS,scale=$SCALE:-1:flags=lanczos,palettegen=max_colors=$COLORS" -y /tmp/palette.png

# Generate GIF using the palette
ffmpeg -i "$INPUT" -i /tmp/palette.png -filter_complex "fps=$FPS,scale=$SCALE:-1:flags=lanczos[x];[x][1:v]paletteuse" -y "$OUTPUT"

# Clean up
rm /tmp/palette.png

echo "Done! Output saved to $OUTPUT"
ls -lh "$OUTPUT"
