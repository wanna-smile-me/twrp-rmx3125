#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(cd -- "$script_dir/.." && pwd -P)
export PATH=/opt/twrp/prebuilts/go/linux-x86/bin:/usr/bin:/bin
export GOMAXPROCS=4
export GOWORK=off
cd /opt/twrp/build/blueprint
gofmt -w context.go provider_test.go
go test -p 2 ./...
git diff --check
git diff -- context.go provider_test.go > "$project_root/evidence/blueprint-memory.patch"
