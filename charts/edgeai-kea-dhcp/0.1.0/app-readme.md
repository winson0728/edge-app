# Kea DHCP

ISC Kea DHCPv4（hostNetwork，直接服務指定網卡）

| 項目 | 內容 |
|---|---|
| Pack | Access & NAC |
| 層級 | Hub、Node |
| 架構 | amd64（ISC 官方映像只有 amd64；arm64 需自建映像） |
| 授權 | MPL-2.0 |
| 來源 | 自寫 chart（tools/edgeai/common 樣板） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
