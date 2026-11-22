#!/usr/bin/env bash
# 把 charts/*/*/ 打包成 tgz 並產生 HTTP 型 Helm repo 的 index.yaml。
# 用法：tools/edgeai/package-index.sh <輸出目錄> [對外 URL，例如 https://winson0728.github.io/edge-app]
# 輸出目錄請放在 repo 外或 gh-pages 分支；不要在 main 的根目錄放 index.yaml（會改變 Rancher Git 型 repo 的讀法）。
set -euo pipefail
out=${1:?輸出目錄}; url=${2:-}
cd "$(dirname "$0")/../.."
mkdir -p "$out"
for d in charts/*/*/; do helm package "$d" -d "$out" >/dev/null; done
if [ -n "$url" ]; then helm repo index "$out" --url "$url"; else helm repo index "$out"; fi
echo "packaged $(ls "$out"/*.tgz | wc -l) charts → $out/index.yaml"
