#!/usr/bin/env bash
# Download public PDFs from jeta/knowledge/manifest.json (format: pdf) for JETA learning corpus.
# Run from repo root: bash scripts/fetch_jeta_public_sources.sh
# Requires: jq, curl

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/jeta/knowledge/pdfs"
MANIFEST="$ROOT/jeta/knowledge/manifest.json"
mkdir -p "$OUT"

if ! command -v jq &>/dev/null; then
  echo "Install jq (e.g. brew install jq) to parse manifest."
  exit 1
fi

echo "Downloading PDF sources into $OUT ..."

while IFS='|' read -r id url; do
  [ -z "$id" ] && continue
  dest="$OUT/${id}.pdf"
  if [[ -f "$dest" ]]; then
    echo "  skip (exists): ${id}.pdf"
    continue
  fi
  echo "  fetch: $id"
  curl -fsSL --connect-timeout 30 --max-time 180 \
    -A "Mozilla/5.0 (compatible; JETA-knowledge-fetch/1.0)" \
    -o "$dest" "$url" || { echo "  FAILED: $url"; rm -f "$dest"; }
done < <(jq -r '.sources[] | select(.format == "pdf") | "\(.id)|\(.url)"' "$MANIFEST")

echo "Done."
