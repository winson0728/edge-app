# ai-workflow-controller

Vision Pipeline 編排（VisionPipeline CR、Camera 註冊、YOLO 偵測→VLM 覆核、VLM 預算、Privacy 遮罩、Evidence）

| 項目 | 內容 |
|---|---|
| Pack | Vision |
| 層級 | Node、Hub |
| 架構 | amd64, arm64（ds-worker 只有 Jetson／arm64） |
| 授權 | 自研（專有） |
| 來源 | **骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
