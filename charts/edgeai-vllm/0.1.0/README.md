# edgeai-vllm（vLLM（production-stack））

vLLM production-stack（OpenAI 相容 LLM／VLM 服務＋路由器，需 GPU）

- Pack：RAG（預設 namespace `edgeai-rag`）
- 層級：Hub、Node
- 架構：amd64（Thor／Spark 需改用 NVIDIA 提供的 arm64 vLLM 映像）
- 上游專案：https://docs.vllm.ai/projects/production-stack
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`vllm-stack` 0.1.14（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `vllm-stack` 0.1.14，repo：`https://vllm-project.github.io/production-stack`；官方 chart

上游參數全部放在 `vllm-stack:` 底下（例如 `vllm-stack.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
vllm-stack:
  routerSpec:
    serviceType: ClusterIP
```

## 說明
模型清單在 `vllm-stack.servingEngineSpec.modelSpec`（陣列，Rancher 表單不適合填），請在 Rancher 安裝畫面切到 **Edit YAML** 填寫：`name`、`repository`、`tag`、`modelURL`、`requestGPU`；HF token 用 `hf_token.secretName`。

## 驗證
```bash
helm lint . 
helm template t . 
```
