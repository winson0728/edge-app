# model-release-controller

MLflow → Triton 安全上架（按 GPU 世代建 TensorRT engine、benchmark Gate、cosign 簽章、shadow／promote／rollback）

| 項目 | 內容 |
|---|---|
| Pack | MLOps |
| 層級 | Hub |
| 架構 | amd64, arm64 |
| 授權 | 自研（專有） |
| 來源 | **骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
