# Triton Inference Server

NVIDIA Triton 推論伺服器（YOLO／TensorRT 模型服務，需 GPU）

| 項目 | 內容 |
|---|---|
| Pack | Vision |
| 層級 | Hub、Node |
| 架構 | amd64, arm64（Thor／Spark 用同一個多架構映像；Orin 需 JetPack 版映像） |
| 授權 | BSD-3-Clause（程式）＋ NVIDIA 映像 EULA　⚠ 商用打包風險：低中 |
| 來源 | 自寫 chart（tools/edgeai/common 樣板） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
