#!/usr/bin/env bash

# build.sh - Compiles the custom bootstrap SCSS into CSS
# Usage: ./build.sh [--watch]
# --watch: Watch for changes and rebuild automatically (requires `entr`)

function build() {
    npx npm install > /dev/null
    npx sass custom.scss ../app/static/css/bootstrap.css > /dev/null
}

if [[ $1 == "--watch" ]]; then
    if ! command -v entr >/dev/null 2>&1; then
        echo "entr is not installed"
        echo "Please install it: https://github.com/eradman/entr"
        exit 1
    fi

    echo "custom.scss" | entr -s ./build.sh
else
    build
fi
