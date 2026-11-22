# edgeai-valkey（Valkey）

Valkey（Redis 相容；sim-aaa-adapter AV 快取、event engine 去重）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub、Node
- 架構：amd64, arm64
- 上游專案：https://valkey.io
- 授權：BSD-3-Clause；商用打包風險 **低**。Redis 7.4 起改 RSALv2／SSPL（8.0 加 AGPL），以 Valkey 取代。
- chart 類型：上游 chart wrapper：`valkey` 1.0.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `valkey` 1.0.0，repo：`https://valkey.io/valkey-helm/`；官方 chart

上游參數全部放在 `valkey:` 底下（例如 `valkey.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
valkey:
  auth:
    enabled: false
```

## 驗證
```bash
helm lint . 
helm template t . 
```
