# edgeai-minio（MinIO（選配，AGPL））

MinIO 物件儲存（選配；AGPL 授權風險）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://min.io
- 授權：AGPL-3.0；商用打包風險 **中高**。社群版功能縮減；上游 chart 5.4.0（2024-12）已停止更新。預設請用 edgeai-seaweedfs，或採購 MinIO 商業授權。
- chart 類型：上游 chart wrapper：`minio` 5.4.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `minio` 5.4.0，repo：`https://charts.min.io/`；官方 chart（已停止更新）

上游參數全部放在 `minio:` 底下（例如 `minio.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
minio:
  mode: standalone
  replicas: 1
  existingSecret: ''
  persistence:
    size: 50Gi
  resources:
    requests:
      memory: 1Gi
```

## 必填（安裝前檢查）
- minio.existingSecret 必填（含 rootUser／rootPassword 的 Secret）

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
