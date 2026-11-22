# edgeai-mlflow（MLflow）

MLflow Tracking／Model Registry（model-release-controller 的上游）

- Pack：MLOps（預設 namespace `edgeai-mlops`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://mlflow.org
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`mlflow` 1.11.7（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `mlflow` 1.11.7，repo：`https://community-charts.github.io/helm-charts`；社群（community-charts）chart

上游參數全部放在 `mlflow:` 底下（例如 `mlflow.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
mlflow:
  artifactRoot:
    proxiedArtifactStorage: true
```

## 說明
預設 backend 為 SQLite（單機試用）；正式站接 CloudNativePG（`backendStore.postgres.*` + `existingDatabaseSecret`），artifact 接 SeaweedFS S3（`artifactRoot.s3.*` + `existingSecret`）。

## 驗證
```bash
helm lint . 
helm template t . 
```
