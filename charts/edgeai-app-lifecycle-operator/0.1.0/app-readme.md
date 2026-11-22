# app-lifecycle-operator

每叢集的 App 生命週期 operator（EdgeApp CR：安裝／升級／回滾，GitOps 或 air-gap 模式）

| 項目 | 內容 |
|---|---|
| Pack | Platform |
| 層級 | Hub、Node、Gateway（每個受管叢集一份） |
| 架構 | amd64, arm64 |
| 授權 | 自研（專有） |
| 來源 | **骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
