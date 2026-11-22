#!/usr/bin/env bash
# 對 charts/edgeai-*/<version>/ 逐一跑 helm lint 與 helm template（有 ci/test-values.yaml 就帶入）。
# 用法：tools/edgeai/check.sh [chart-name ...]；結果寫到 stdout，失敗時 exit 1。
set -u
cd "$(dirname "$0")/../.."
fail=0
dirs=()
if [ $# -gt 0 ]; then for n in "$@"; do dirs+=(charts/$n/*/); done; else dirs=(charts/edgeai-*/*/); fi
printf '%-28s %-8s %-6s %-9s %s\n' CHART VERSION LINT TEMPLATE OBJECTS
for d in "${dirs[@]}"; do
  d=${d%/}; name=$(basename "$(dirname "$d")"); ver=$(basename "$d")
  args=(); [ -f "$d/ci/test-values.yaml" ] && args=(-f "$d/ci/test-values.yaml")
  if helm lint "$d" "${args[@]}" >/tmp/eai_lint.$$ 2>&1; then lint=PASS; else lint=FAIL; fi
  if helm template t "$d" -n edgeai-test "${args[@]}" >/tmp/eai_tpl.$$ 2>&1; then tpl=PASS; else tpl=FAIL; fi
  objs=$(grep -c '^kind:' /tmp/eai_tpl.$$ || true)
  printf '%-28s %-8s %-6s %-9s %s\n' "$name" "$ver" "$lint" "$tpl" "$objs"
  if [ "$lint" = FAIL ] || [ "$tpl" = FAIL ]; then
    fail=1; echo "---- $name"; grep -E 'ERROR|Error|error' /tmp/eai_lint.$$ /tmp/eai_tpl.$$ | head -5
  fi
done
rm -f /tmp/eai_lint.$$ /tmp/eai_tpl.$$
exit $fail
