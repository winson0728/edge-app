# edgeai-argo-cd（Argo CD（選配））

Argo CD（GitOps；Rancher 已內建 Fleet，兩者擇一）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://argo-cd.readthedocs.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`argo-cd` 10.18.2（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `argo-cd` 10.18.2，repo：`https://argoproj.github.io/argo-helm`；官方 chart

上游參數全部放在 `argo-cd:` 底下（例如 `argo-cd.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
argo-cd:
  dex:
    enabled: false
  notifications:
    enabled: false
```

## 說明
初始 admin 密碼由上游隨機產生在 `argocd-initial-admin-secret`。Rancher 已內建 Fleet，文件 C9 介面兩者皆可；同一叢集不要同時讓 Fleet 與 Argo 管同一批資源。

## 驗證
```bash
helm lint . 
helm template t . 
```
