# edgeai-seaweedfs（SeaweedFS（S3））

SeaweedFS 物件儲存（S3 相容，MinIO 的 Apache-2.0 替代，平台預設）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://github.com/seaweedfs/seaweedfs
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`seaweedfs` 4.54.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `seaweedfs` 4.54.0，repo：`https://seaweedfs.github.io/seaweedfs/helm`；官方 chart

上游參數全部放在 `seaweedfs:` 底下（例如 `seaweedfs.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
seaweedfs:
  filer:
    s3:
      enabled: true
```

## 說明
v2 Roadmap §5 建議以 SeaweedFS 取代 MinIO（AGPL）。S3 帳密用上游的 `filer.s3.enableAuth` + `existingConfigSecret`，不要寫進 values。

## 驗證
```bash
helm lint . 
helm template t . 
```
