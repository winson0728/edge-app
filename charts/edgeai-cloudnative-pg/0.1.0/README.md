# edgeai-cloudnative-pg（CloudNativePG Operator）

CloudNativePG（PostgreSQL operator；自研模組、Keycloak、MLflow 的資料庫）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub、Node
- 架構：amd64, arm64
- 上游專案：https://cloudnative-pg.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`cloudnative-pg` 0.29.2（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `cloudnative-pg` 0.29.2，repo：`https://cloudnative-pg.github.io/charts`；官方 chart

上游參數全部放在 `cloudnative-pg:` 底下（例如 `cloudnative-pg.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
cloudnative-pg: {}
```

## 說明
裝好 operator 後建立資料庫叢集（範例）：
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: {name: pg, namespace: edgeai-platform}
spec:
  instances: 1
  storage: {size: 10Gi}
```
密碼由 operator 產生在 `pg-app` Secret。HA（Hub Duo）把 `instances` 改 2～3。

## 驗證
```bash
helm lint . 
helm template t . 
```
