# edgeai-kyverno（Kyverno）

Kyverno 準入策略（cosign verifyImages、default-deny 等平台策略）

- Pack：Security（預設 namespace `edgeai-security`）
- 層級：Hub、Node、Gateway
- 架構：amd64, arm64
- 上游專案：https://kyverno.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`kyverno` 3.10.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `kyverno` 3.10.0，repo：`https://kyverno.github.io/kyverno/`；官方 chart

上游參數全部放在 `kyverno:` 底下（例如 `kyverno.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
kyverno: {}
```

## 說明
策略（ClusterPolicy）不放在同一個 release（CRD 尚未建立時無法一起安裝），之後以 Pack 的 policy bundle 另外下發。

## 驗證
```bash
helm lint . 
helm template t . 
```
