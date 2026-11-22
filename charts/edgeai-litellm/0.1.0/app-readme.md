# LiteLLM Proxy

LiteLLM（統一 LLM 閘道、金鑰／用量與 AI Agent 稽核日誌）

| 項目 | 內容 |
|---|---|
| Pack | RAG |
| 層級 | Hub |
| 架構 | amd64, arm64 |
| 授權 | MIT（enterprise/ 目錄除外） |
| 來源 | 上游 chart wrapper：`litellm-helm` 1.110.2（上游原封打包於 charts/，只加平台預設值） |

密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。
