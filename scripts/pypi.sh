#!/usr/bin/env sh

set -eux

main() {
    python3 -m build
    python3 -m twine upload dist/*
}

main "$@"
