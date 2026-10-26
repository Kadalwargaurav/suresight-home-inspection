#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export SURESIGHT_SECRET_KEY="${SURESIGHT_SECRET_KEY:-change-this-before-public-deployment}"
export SURESIGHT_ADMIN_PASSWORD="${SURESIGHT_ADMIN_PASSWORD:-ChangeMe-Now-123!}"
python app.py
