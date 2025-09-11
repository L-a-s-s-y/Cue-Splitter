#!/bin/bash
set -euo pipefail

TARGET_DIR="/tmp/splitter"

find "$TARGET_DIR" -type f -mmin +10 -print -delete
find "$TARGET_DIR" -type d -empty -mmin +10 -print -delete

