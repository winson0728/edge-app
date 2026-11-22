# edgeai-qdrant（Qdrant）

Qdrant 向量資料庫（RAG 知識庫、人物／事件向量搜尋）

- Pack：RAG（預設 namespace `edgeai-rag`）
- 層級：Hub、Node
- 架構：amd64, arm64
- 上游專案：https://qdrant.tech
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`qdrant` 1.20.2（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `qdrant` 1.20.2，repo：`https://qdrant.github.io/qdrant-helm`；官方 chart

上游參數全部放在 `qdrant:` 底下（例如 `qdrant.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
qdrant:
  replicaCount: 1
  persistence:
    size: 10Gi
```

## 驗證
```bash
helm lint . 
helm template t . 
```
