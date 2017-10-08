#!/bin/bash
set -e

sudo echo -ne "\n\nGenerating Virtualenv...\n\n"
virtualenv -p python3.6 build
source build/bin/activate

echo  -ne "\n\nInstalling dependencies...\n\n"
sudo ./upgrade_gcc.sh
pip install -r dependencies.txt
pip install -r large_dependencies.txt

echo -ne "\n\nDone!\n\n"
