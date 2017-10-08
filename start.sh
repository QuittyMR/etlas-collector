#!/bin/bash
set -e

pushd build
source bin/activate
python ../app/appapi/__init__.py
popd

echo -ne "\n\nServer terminated.\n\n"
