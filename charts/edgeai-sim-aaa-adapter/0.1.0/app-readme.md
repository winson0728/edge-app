# sim-aaa-adapter

Wi-Fi EAP-AKA／AKA′ 與 Harmony UDM／AUSF 介接（只做認證：AV 取得、SQN resync、pseudonym／fast re-auth）

| 項目 | 內容 |
|---|---|
| Pack | Access & NAC |
| 層級 | Hub（＋Node Survival 副本） |
| 架構 | amd64, arm64 |
| 授權 | 自研（專有） |
| 來源 | **骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
