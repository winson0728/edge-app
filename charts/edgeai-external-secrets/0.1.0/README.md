# edgeai-external-secrets（External Secrets Operator）

External Secrets（中央 Vault／KMS → 各站 Secret）

- Pack：Security（預設 namespace `edgeai-security`）
- 層級：Hub、Node、Gateway
- 架構：amd64, arm64
- 上游專案：https://external-secrets.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`external-secrets` 2.15.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `external-secrets` 2.15.0，repo：`https://charts.external-secrets.io`；官方 chart

上游參數全部放在 `external-secrets:` 底下（例如 `external-secrets.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
external-secrets: {}
```

## 驗證
```bash
helm lint . 
helm template t . 
```
