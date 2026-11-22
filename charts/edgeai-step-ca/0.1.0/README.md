# edgeai-step-ca（step-ca 私有 CA）

smallstep step-ca（私有 CA、ACME／EST，裝置身分與 mTLS）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://smallstep.com/docs/step-ca/
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`step-certificates` 1.30.1（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `step-certificates` 1.30.1，repo：`https://smallstep.github.io/helm-charts`；官方 chart

上游參數全部放在 `step-certificates:` 底下（例如 `step-certificates.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
step-certificates:
  ca:
    name: Edge AI Private CA
    db:
      persistent: true
      size: 2Gi
```

## 說明
預設由上游的 bootstrap Job 在叢集內產生 CA 與密碼並存成 Secret（不經過 values）。正式站建議用 `step ca init --helm` 離線產生後以 `inject`／`existingSecrets` 帶入，CA 私鑰另行保管。

## 驗證
```bash
helm lint . 
helm template t . 
```
