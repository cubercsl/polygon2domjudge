#!/usr/bin/env bash
#
# Wrapper script for running problemtools directly from within the
# problemtools repo without installing it on the system.  When
# installing problemtools on the system properly, this script should
# not be used.

export PYTHONPATH
PYTHONPATH="$(dirname "$(dirname "$(readlink -f "$0")")"):$PYTHONPATH"
exec python -m p2d.main "$@"