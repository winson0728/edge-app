# edgeai-otel-collector（OpenTelemetry Collector）

OpenTelemetry Collector（各模組 telemetry-client 的收集點）

- Pack：Observability（預設 namespace `edgeai-observability`）
- 層級：Hub、Node、Gateway
- 架構：amd64, arm64
- 上游專案：https://opentelemetry.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`opentelemetry-collector` 0.182.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `opentelemetry-collector` 0.182.0，repo：`https://open-telemetry.github.io/opentelemetry-helm-charts`；官方 chart

上游參數全部放在 `opentelemetry-collector:` 底下（例如 `opentelemetry-collector.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
opentelemetry-collector:
  mode: deployment
  image:
    repository: otel/opentelemetry-collector-k8s
```

## 驗證
```bash
helm lint . 
helm template t . 
```
