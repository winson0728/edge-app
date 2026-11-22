# step-ca 私有 CA

smallstep step-ca（私有 CA、ACME／EST，裝置身分與 mTLS）

| 項目 | 內容 |
|---|---|
| Pack | Access & NAC |
| 層級 | Hub |
| 架構 | amd64, arm64 |
| 授權 | Apache-2.0 |
| 來源 | 上游 chart wrapper：`step-certificates` 1.30.1（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
