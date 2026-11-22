# vLLM（production-stack）

vLLM production-stack（OpenAI 相容 LLM／VLM 服務＋路由器，需 GPU）

| 項目 | 內容 |
|---|---|
| Pack | RAG |
| 層級 | Hub、Node |
| 架構 | amd64（Thor／Spark 需改用 NVIDIA 提供的 arm64 vLLM 映像） |
| 授權 | Apache-2.0 |
| 來源 | 上游 chart wrapper：`vllm-stack` 0.1.14（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
