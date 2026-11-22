# Velero

Velero 備份／還原（應用資料與 PV，上送 SeaweedFS／S3）

| 項目 | 內容 |
|---|---|
| Pack | Platform |
| 層級 | Hub、Node |
| 架構 | amd64, arm64 |
| 授權 | Apache-2.0 |
| 來源 | 上游 chart wrapper：`velero` 12.2.5（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
