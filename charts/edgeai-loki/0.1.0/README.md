# edgeai-loki（Loki（AGPL））

Loki 日誌（SingleBinary＋filesystem，單站 Hub）

- Pack：Observability（預設 namespace `edgeai-observability`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://grafana.com/oss/loki/
- 授權：AGPL-3.0；商用打包風險 **中**。同 Grafana；替代方案 edgeai-victoria（VictoriaLogs，Apache-2.0）。
- chart 類型：上游 chart wrapper：`loki` 7.7.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `loki` 7.7.0，repo：`https://grafana.github.io/helm-charts`；官方 chart

上游參數全部放在 `loki:` 底下（例如 `loki.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
loki:
  deploymentMode: SingleBinary
  loki:
    auth_enabled: false
    commonConfig:
      replication_factor: 1
    storage:
      type: filesystem
    schemaConfig:
      configs:
      - from: '2024-04-01'
        store: tsdb
        object_store: filesystem
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
  singleBinary:
    replicas: 1
  read:
    replicas: 0
  write:
    replicas: 0
  backend:
    replicas: 0
  chunksCache:
    enabled: false
  resultsCache:
    enabled: false
  lokiCanary:
    enabled: false
  test:
    enabled: false
```

## 驗證
```bash
helm lint . 
helm template t . 
```
