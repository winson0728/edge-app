# edgeai-trivy-operator（Trivy Operator）

Trivy Operator（叢集內映像弱點／組態掃描，CVE SLA 依據）

- Pack：Security（預設 namespace `edgeai-security`）
- 層級：Hub、Node
- 架構：amd64, arm64
- 上游專案：https://aquasecurity.github.io/trivy-operator/
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`trivy-operator` 0.38.1（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `trivy-operator` 0.38.1，repo：`https://aquasecurity.github.io/helm-charts/`；官方 chart

上游參數全部放在 `trivy-operator:` 底下（例如 `trivy-operator.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
trivy-operator:
  operator:
    scanJobsConcurrentLimit: 1
  trivy:
    ignoreUnfixed: true
```

## 說明
弱點資料庫預設從網路下載（ghcr.io）；離線站點改指向 Harbor 內的鏡像（`trivy.dbRegistry`）。

## 驗證
```bash
helm lint . 
helm template t . 
```
