# edgeai-grafana（Grafana（AGPL））

Grafana（Pack 儀表板，Console 以嵌入方式復用）

- Pack：Observability（預設 namespace `edgeai-observability`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://grafana.com/oss/grafana/
- 授權：AGPL-3.0；商用打包風險 **中**。不修改原始碼、保留 source offer 即合規；長期可評估 Perses。Rancher Monitoring 已內建一份 Grafana，這份給 Pack 儀表板／Console 嵌入用。
- chart 類型：上游 chart wrapper：`grafana` 10.5.15（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `grafana` 10.5.15，repo：`https://grafana.github.io/helm-charts`；官方 chart

上游參數全部放在 `grafana:` 底下（例如 `grafana.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
grafana:
  admin:
    existingSecret: ''
    userKey: admin-user
    passwordKey: admin-password
  persistence:
    enabled: false
```

## 驗證
```bash
helm lint . 
helm template t . 
```
