#!/bin/sh
# Bootstrap-only exception: lifecycle operations remain in stdlib Python.
set -eu
script_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
genie_data_root=${GENIE_BOOTSTRAP_HOME:-"$HOME/.genie"}
previous=''
for argument in "$@"; do
    if [ "$previous" = '--home' ]; then genie_data_root=$argument; fi
    previous=$argument
done
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3,11))' >/dev/null 2>&1; then
        exec "$candidate" "$script_root/bootstrap.py" "$@"
    fi
done
if [ "$(uname -s)" != Darwin ] || [ "$(uname -m)" != arm64 ]; then
    printf '%s\n' 'Managed runtime currently supports Apple Silicon macOS. Compatible existing Python >=3.11 can run bootstrap.py on qualified platforms.' >&2
    exit 2
fi
# Generated from bootstrap-registry.json upstream release digest, never guessed.
runtime_version='3.12.15+20261003'
runtime_url='https://github.com/astral-sh/python-build-standalone/releases/download/20261003/cpython-3.12.15%2B20261003-aarch64-apple-darwin-install_only.tar.gz'
runtime_sha256='316a463172740e71d8dca1f2730784e325f3f720941137b5d674d5801a632213'
runtime_root="$genie_data_root/bootstrap/runtime/$runtime_version"
if [ ! -x "$runtime_root/python/bin/python3" ] || [ ! -f "$runtime_root/.verified" ]; then
    mkdir -p "$genie_data_root/bootstrap/runtime"
    temporary=$(mktemp -d "$genie_data_root/bootstrap/runtime/.stage.XXXXXX")
    trap 'rm -rf "$temporary"' EXIT HUP INT TERM
    curl --fail --location --proto '=https' --tlsv1.2 "$runtime_url" -o "$temporary/runtime.tar.gz"
    actual=$(shasum -a 256 "$temporary/runtime.tar.gz" | awk '{print $1}')
    if [ "$actual" != "$runtime_sha256" ]; then
        printf '%s\n' 'Managed Python checksum mismatch; nothing activated.' >&2
        exit 1
    fi
    mkdir "$temporary/stage"
    tar -xzf "$temporary/runtime.tar.gz" -C "$temporary/stage"
    "$temporary/stage/python/bin/python3" -c 'import sys; raise SystemExit(sys.version_info < (3,11))'
    printf '%s\n' "$runtime_sha256" > "$temporary/stage/.verified"
    if [ -e "$runtime_root" ]; then
        printf '%s\n' 'Existing managed runtime is incomplete; preserve it and repair before retry.' >&2
        exit 2
    fi
    mv "$temporary/stage" "$runtime_root"
    rm -rf "$temporary"
    trap - EXIT HUP INT TERM
fi
exec "$runtime_root/python/bin/python3" "$script_root/bootstrap.py" "$@"
