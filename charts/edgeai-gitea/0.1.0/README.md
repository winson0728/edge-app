# edgeai-gitea（Gitea）

Gitea（GitOps values repo，edge-app-catalog-controller 寫入）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://gitea.com
- 授權：MIT；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`gitea` 12.7.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `gitea` 12.7.0，repo：`https://dl.gitea.com/charts/`；官方 chart

上游參數全部放在 `gitea:` 底下（例如 `gitea.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
gitea:
  postgresql-ha:
    enabled: false
  postgresql:
    enabled: false
  valkey-cluster:
    enabled: false
  valkey:
    enabled: false
  gitea:
    admin:
      existingSecret: ''
    config:
      database:
        DB_TYPE: sqlite3
      session:
        PROVIDER: memory
      cache:
        ADAPTER: memory
      queue:
        TYPE: level
  persistence:
    enabled: true
    size: 10Gi
```

## 必填（安裝前檢查）
- gitea.gitea.admin.existingSecret 必填（含 username／password，避免上游預設管理者密碼）

## 說明
預設 SQLite＋記憶體 cache（單站 Hub 夠用、少一個資料庫要維運）；要 HA 時改開上游的 `postgresql-ha`／`valkey-cluster` 或接 CloudNativePG。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
