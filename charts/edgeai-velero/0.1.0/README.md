# edgeai-velero（Velero）

Velero 備份／還原（應用資料與 PV，上送 SeaweedFS／S3）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub、Node
- 架構：amd64, arm64
- 上游專案：https://velero.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`velero` 12.2.5（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `velero` 12.2.5，repo：`https://vmware-tanzu.github.io/helm-charts`；官方 chart

上游參數全部放在 `velero:` 底下（例如 `velero.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
velero:
  credentials:
    useSecret: true
    existingSecret: ''
```

## 說明
備份位置（`configuration.backupStorageLocation`）與 plugin（`initContainers`，例如 velero-plugin-for-aws）是陣列，請在 Rancher 安裝畫面用 **Edit YAML** 填寫；指向 edgeai-seaweedfs 的 S3。

## 驗證
```bash
helm lint . 
helm template t . 
```
