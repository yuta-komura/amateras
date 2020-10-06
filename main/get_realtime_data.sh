#!/bin/sh

SCRIPT_DIR=$(
    cd $(dirname $0)
    cd ../
    pwd
)

. ${SCRIPT_DIR}/venv/bin/activate

python ${SCRIPT_DIR}/get_realtime_data.py

wait
