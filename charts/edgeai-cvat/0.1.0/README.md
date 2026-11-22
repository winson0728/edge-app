# edgeai-cvat（CVAT）

CVAT 標註平台（Model Flywheel 的難例標註佇列）

- Pack：MLOps（預設 namespace `edgeai-mlops`）
- 層級：Hub
- 架構：amd64
- 上游專案：https://www.cvat.ai
- 授權：MIT；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`cvat` 2.83.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `cvat` 2.83.0，repo：`（無 chart repo，見下方）`；官方 chart 放在 cvat repo 的 helm-chart/（沒有 chart repo），以 v2.83.0 原樣 helm package 後放入

上游參數全部放在 `cvat:` 底下（例如 `cvat.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
cvat:
  analytics:
    enabled: false
```

## 說明
CVAT 的子 chart 含 Bitnami PostgreSQL／Redis（Bitnami 免費映像 2025-08 後改到 `bitnamilegacy`），資源需求高（建議 Hub ≥ 8 GiB 可用記憶體）。

## 驗證
```bash
helm lint . 
helm template t . 
```
