#!/bin/bash
set -e

GCCVERSION="$(gcc -dumpversion)"
REQUIREDVERSION="4.9"

 if [ "$(printf "${REQUIREDVERSION}\n${GCCVERSION}" | sort -V | head -n1)" == "${GCCVERSION}" ] && [ "${GCCVERSION}" != "${REQUIREDVERSION}" ]; then
        echo -ne "Upgrading GCC and replacing symlinks..."
        rm /usr/bin/x86_64-linux-gnu-gcc
        ln -s /usr/bin/gcc-4.9 /usr/bin/x86_64-linux-gnu-gcc
        echo -ne "\n\nDone!\n\n"
 else
        echo -ne "Found suitable GCC version"
 fi
