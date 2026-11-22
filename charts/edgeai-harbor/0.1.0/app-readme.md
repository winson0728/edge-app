# Harbor

Harbor 映像／OCI Artifact 倉庫（模型包、app-pack、cosign 簽章）

| 項目 | 內容 |
|---|---|
| Pack | Platform |
| 層級 | Hub |
| 架構 | amd64（官方映像未提供 arm64） |
| 授權 | Apache-2.0 |
| 來源 | 上游 chart wrapper：`harbor` 1.19.4（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
