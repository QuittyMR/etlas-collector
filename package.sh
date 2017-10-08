#!/bin/bash
set -e

sudo echo -ne "\n\nPackaging application...\n\n"
source build/bin/activate
python app/setup.py bdist_wheel

echo -ne "\n\nDone!\n\n"
