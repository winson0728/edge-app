# Kyverno

Kyverno 準入策略（cosign verifyImages、default-deny 等平台策略）

| 項目 | 內容 |
|---|---|
| Pack | Security |
| 層級 | Hub、Node、Gateway |
| 架構 | amd64, arm64 |
| 授權 | Apache-2.0 |
| 來源 | 上游 chart wrapper：`kyverno` 3.10.0（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
