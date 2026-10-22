#!/usr/bin/env bash
# Rebuilds assets/banner.webp from the portfolio's hero frames.
# Usage: scripts/banner.sh [path/to/portfolio]   (needs imagemagick)
set -euo pipefail

PORTFOLIO=${1:-../portfolio}
OUT=$(cd "$(dirname "$0")/.." && pwd)/assets
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

RED='rgb(226,40,39)' # same as the frames' backdrop, so the photo edge disappears
W=1200 H=480 STEP=4  # every 4th of 192 frames = 48-frame loop

for w in 400 700; do
  url=$(curl -s -A "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@$w" | grep -oE 'https://[^)]+')
  curl -s -o "$TMP/sg$w.ttf" "$url"
done

# Static text layer, laid out like the site hero (bottom-left).
magick -size ${W}x${H} xc:none \
  -font "$TMP/sg400.ttf" -fill 'rgba(255,255,255,0.75)' -pointsize 22 -annotate +64+64 'harshmaroo.web.app' \
  -fill 'rgba(255,255,255,0.9)' -pointsize 26 -annotate +68+212 "Hi, I'm" \
  \( -size ${W}x${H} xc:none -font "$TMP/sg700.ttf" -fill 'rgba(0,0,0,0.35)' -pointsize 150 -kerning -6 -annotate +66+344 'Harsh' -blur 0x8 \) -composite \
  -font "$TMP/sg700.ttf" -fill white -pointsize 150 -kerning -6 -annotate +60+336 'Harsh' \
  -font "$TMP/sg400.ttf" -fill 'rgba(255,255,255,0.85)' -pointsize 22 -kerning 0 \
  -annotate +66+386 'I write code so your phone does cool things.' \
  -annotate +66+416 'Powered by Flutter & AI. Loved by 3M+ users.' \
  "$TMP/text.png"

i=0
for f in $(seq 0 $STEP 191); do
  magick -size ${W}x${H} "xc:$RED" \
    \( "$PORTFOLIO/public/frames/$f.webp" -resize 1050x \) -geometry +270-10 -composite \
    "$TMP/text.png" -composite "$TMP/$(printf %03d $i).png"
  i=$((i + 1))
done

mkdir -p "$OUT"
# ponytail: animated webp over gif, ~10x smaller and no gifsicle needed
magick -delay 7 -loop 0 "$TMP"/[0-9]*.png -quality 72 "$OUT/banner.webp"
ls -lh "$OUT/banner.webp"
