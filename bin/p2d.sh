#!/usr/bin/env bash
#
# Wrapper script for running polygon2domjudge directly from within the
# polygon2domjudge repo without installing it on the system.  When
# installing polygon2domjudge on the system properly, this script should
# not be used.

export PYTHONPATH
PYTHONPATH="$(dirname "$(dirname "$(readlink -f "$0")")"):$PYTHONPATH"
exec python -m p2d.main "$@"
