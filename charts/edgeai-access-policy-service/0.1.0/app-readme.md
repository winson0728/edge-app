# access-policy-service

統一 5G／Wi-Fi／有線授權政策（PDP、session registry、CoA、Policy Bundle、下游 MQTT ACL／Keycloak／5GC 同步）

| 項目 | 內容 |
|---|---|
| Pack | Access & NAC |
| 層級 | Hub（＋Node 決策快取） |
| 架構 | amd64, arm64 |
| 授權 | 自研（專有） |
| 來源 | **骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
