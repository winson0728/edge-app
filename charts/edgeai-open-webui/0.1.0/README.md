# edgeai-open-webui（Open WebUI）

Open WebUI（RAG／Assistant 前端，接 vLLM 或 LiteLLM）

- Pack：RAG（預設 namespace `edgeai-rag`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://openwebui.com
- 授權：Open WebUI License（BSD-3 衍生＋品牌條款，v0.6+）；商用打包風險 **中**。白牌／移除品牌需確認條款或替換前端；GA 前法務確認。
- chart 類型：上游 chart wrapper：`open-webui` 18.4.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `open-webui` 18.4.0，repo：`https://helm.openwebui.com/`；官方 chart

上游參數全部放在 `open-webui:` 底下（例如 `open-webui.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
open-webui:
  ollama:
    enabled: false
  pipelines:
    enabled: false
  openaiBaseApiUrl: http://edgeai-litellm.edgeai-rag.svc:4000/v1
  persistence:
    enabled: true
    size: 5Gi
```

## 驗證
```bash
helm lint . 
helm template t . 
```
