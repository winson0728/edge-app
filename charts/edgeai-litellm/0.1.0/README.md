# edgeai-litellm（LiteLLM Proxy）

LiteLLM（統一 LLM 閘道、金鑰／用量與 AI Agent 稽核日誌）

- Pack：RAG（預設 namespace `edgeai-rag`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://docs.litellm.ai
- 授權：MIT（enterprise/ 目錄除外）；商用打包風險 **低**。不啟用 enterprise 功能；Agent 稽核用其 logging。
- chart 類型：上游 chart wrapper：`litellm-helm` 1.110.2（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `litellm-helm` 1.110.2，repo：`oci://ghcr.io/berriai`；官方 chart（OCI）

上游參數全部放在 `litellm-helm:` 底下（例如 `litellm-helm.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
litellm-helm:
  masterkeySecretName: ''
  masterkeySecretKey: masterkey
```

## 必填（安裝前檢查）
- litellm-helm.masterkeySecretName 必填（含 masterkey 鍵的 Secret）

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
