# edgeai-harbor（Harbor）

Harbor 映像／OCI Artifact 倉庫（模型包、app-pack、cosign 簽章）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
- 架構：amd64（官方映像未提供 arm64）
- 上游專案：https://goharbor.io
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`harbor` 1.19.4（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `harbor` 1.19.4，repo：`https://helm.goharbor.io`；官方 chart

上游參數全部放在 `harbor:` 底下（例如 `harbor.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
harbor:
  expose:
    type: clusterIP
    tls:
      enabled: false
  externalURL: https://harbor.example.com
  existingSecretAdminPassword: ''
  existingSecretAdminPasswordKey: HARBOR_ADMIN_PASSWORD
  nodeSelector:
    kubernetes.io/arch: amd64
```

## 必填（安裝前檢查）
- harbor.existingSecretAdminPassword 必填（避免上游預設管理者密碼）

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
