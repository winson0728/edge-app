# edgeai-victoria（VictoriaMetrics＋VictoriaLogs）

VictoriaMetrics／VictoriaLogs（Prometheus 長留存與日誌，Grafana／Loki 的 Apache-2.0 替代）

- Pack：Observability（預設 namespace `edgeai-observability`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://victoriametrics.com
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`victoria-metrics-single` 0.51.0、`victoria-logs-single` 0.13.13（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `victoria-metrics-single` 0.51.0，repo：`https://victoriametrics.github.io/helm-charts/`
- `victoria-logs-single` 0.13.13，repo：`https://victoriametrics.github.io/helm-charts/`
- 官方 chart（兩個 single 版合成一個安裝項）

各上游參數放在各自的 key 底下。

## 平台預設值
```yaml
victoria-metrics-single:
  enabled: true
  server:
    persistentVolume:
      enabled: true
      size: 20Gi
victoria-logs-single:
  enabled: true
  server:
    persistentVolume:
      enabled: true
      size: 20Gi
```

## 驗證
```bash
helm lint . 
helm template t . 
```
