# Edge AI 開源套件 chart（edge-app 套件庫）

本 repo（`winson0728/edge-app`）是 Rancher 的 **Git 型套件庫**：Rancher 直接讀 `charts/<name>/<version>/`，不需要 `index.yaml`。
Edge AI 平台（v2 Roadmap 三層架構：Hub／Node／Gateway）Layer 1 直接部署的開源套件，都以 `edgeai-*` 為名放在這裡；
既有的 `vlm-app`、`srs`、`doublinks`、`zerotier-planet` 不受影響。

- 規劃依據：`edge-ai-plan-review-and-v2-roadmap.md`（§3.3 Pack、§5 OSS 授權）、`edge-ai-custom-modules-implementation-plan.md`（Layer 1 清單）
- 本輪範圍：**開源套件 32 個**（上游 wrapper 23、自寫 9）＋ 既有 vlm-app。Layer 2 自研模組（sim-aaa-adapter 等）的骨架 chart 另案。

## 1. 清單

層級：Hub＝x86（amd64）；Node＝DGX Spark／Jetson Thor（arm64）；Gateway＝Orin（arm64、L4T）。
「wrapper」＝引用上游官方或社群 chart（上游 tgz 原封放在 `charts/<name>/<version>/charts/`，只加平台預設值、Rancher 表單與說明，不改上游）；
「自寫」＝上游沒有可用 chart，用 `tools/edgeai/common` 的共用樣板（Deployment／Service／ConfigMap／PVC／NetworkPolicy／Ingress）寫成。

<!-- chart-table:start -->
| Pack | Chart | 軟體 | 來源 | 層級 | 架構 | 授權 |
|---|---|---|---|---|---|---|
| Access & NAC | `edgeai-freeradius` 0.1.0 | FreeRADIUS | 自寫 | Hub、Node（Site Survival 副本） | amd64, arm64 | GPL-2.0 ⚠中 |
| Access & NAC | `edgeai-headscale` 0.1.0 | Headscale | 自寫 | Hub | amd64, arm64 | BSD-3-Clause |
| Access & NAC | `edgeai-kea-dhcp` 0.1.0 | Kea DHCP | 自寫 | Hub、Node | amd64（ISC 官方映像只有 amd64；arm64 需自建映像） | MPL-2.0 |
| Access & NAC | `edgeai-keycloak` 0.1.0 | Keycloak | wrapper：keycloakx 7.4.0 | Hub | amd64, arm64 | Apache-2.0 |
| Access & NAC | `edgeai-step-ca` 0.1.0 | step-ca 私有 CA | wrapper：step-certificates 1.30.1 | Hub | amd64, arm64 | Apache-2.0 |
| Vision | `edgeai-mediamtx` 0.1.0 | MediaMTX | 自寫 | Node、Gateway | amd64, arm64 | MIT |
| Vision | `edgeai-triton` 0.1.0 | Triton Inference Server | 自寫 | Hub、Node | amd64, arm64（Thor／Spark 用同一個多架構映像；Orin 需 JetPack 版映像） | BSD-3-Clause（程式）＋ NVIDIA 映像 EULA ⚠低中 |
| Voice/PTT | `edgeai-asterisk` 0.1.0 | Asterisk（IP PBX） | 自寫 | Hub、Node（Survivable Gateway） | amd64, arm64（映像需自建） | GPL-2.0 ⚠中 |
| IoT/OT | `edgeai-edgex` 0.1.0 | EdgeX Foundry（core） | 自寫 | Node、Gateway | amd64, arm64 | Apache-2.0 |
| IoT/OT | `edgeai-mosquitto` 0.1.0 | Eclipse Mosquitto | 自寫 | Hub、Node、Gateway | amd64, arm64 | EPL-2.0 / EDL-1.0 |
| IoT/OT | `edgeai-thingsboard` 0.1.0 | ThingsBoard CE（選配） | 自寫 | Hub | amd64, arm64 | Apache-2.0 |
| RAG | `edgeai-litellm` 0.1.0 | LiteLLM Proxy | wrapper：litellm-helm 1.110.2 | Hub | amd64, arm64 | MIT（enterprise/ 目錄除外） |
| RAG | `edgeai-open-webui` 0.1.0 | Open WebUI | wrapper：open-webui 18.4.0 | Hub | amd64, arm64 | Open WebUI License（BSD-3 衍生＋品牌條款，v0.6+） ⚠中 |
| RAG | `edgeai-qdrant` 0.1.0 | Qdrant | wrapper：qdrant 1.20.2 | Hub、Node | amd64, arm64 | Apache-2.0 |
| RAG | `edgeai-vllm` 0.1.0 | vLLM（production-stack） | wrapper：vllm-stack 0.1.14 | Hub、Node | amd64（Thor／Spark 需改用 NVIDIA 提供的 arm64 vLLM 映像） | Apache-2.0 |
| MLOps | `edgeai-cvat` 0.1.0 | CVAT | wrapper：cvat 2.83.0 | Hub | amd64 | MIT |
| MLOps | `edgeai-mlflow` 0.1.0 | MLflow | wrapper：mlflow 1.11.7 | Hub | amd64, arm64 | Apache-2.0 |
| Platform | `edgeai-argo-cd` 0.1.0 | Argo CD（選配） | wrapper：argo-cd 10.18.2 | Hub | amd64, arm64 | Apache-2.0 |
| Platform | `edgeai-cloudnative-pg` 0.1.0 | CloudNativePG Operator | wrapper：cloudnative-pg 0.29.2 | Hub、Node | amd64, arm64 | Apache-2.0 |
| Platform | `edgeai-gitea` 0.1.0 | Gitea | wrapper：gitea 12.7.0 | Hub | amd64, arm64 | MIT |
| Platform | `edgeai-harbor` 0.1.0 | Harbor | wrapper：harbor 1.19.4 | Hub | amd64（官方映像未提供 arm64） | Apache-2.0 |
| Platform | `edgeai-minio` 0.1.0 | MinIO（選配，AGPL） | wrapper：minio 5.4.0 | Hub | amd64, arm64 | AGPL-3.0 ⚠中高 |
| Platform | `edgeai-seaweedfs` 0.1.0 | SeaweedFS（S3） | wrapper：seaweedfs 4.54.0 | Hub | amd64, arm64 | Apache-2.0 |
| Platform | `edgeai-valkey` 0.1.0 | Valkey | wrapper：valkey 1.0.0 | Hub、Node | amd64, arm64 | BSD-3-Clause |
| Platform | `edgeai-velero` 0.1.0 | Velero | wrapper：velero 12.2.5 | Hub、Node | amd64, arm64 | Apache-2.0 |
| Observability | `edgeai-grafana` 0.1.0 | Grafana（AGPL） | wrapper：grafana 10.5.15 | Hub | amd64, arm64 | AGPL-3.0 ⚠中 |
| Observability | `edgeai-loki` 0.1.0 | Loki（AGPL） | wrapper：loki 7.7.0 | Hub | amd64, arm64 | AGPL-3.0 ⚠中 |
| Observability | `edgeai-otel-collector` 0.1.0 | OpenTelemetry Collector | wrapper：opentelemetry-collector 0.182.0 | Hub、Node、Gateway | amd64, arm64 | Apache-2.0 |
| Observability | `edgeai-victoria` 0.1.0 | VictoriaMetrics＋VictoriaLogs | wrapper：victoria-metrics-single 0.51.0、victoria-logs-single 0.13.13 | Hub | amd64, arm64 | Apache-2.0 |
| Security | `edgeai-external-secrets` 0.1.0 | External Secrets Operator | wrapper：external-secrets 2.15.0 | Hub、Node、Gateway | amd64, arm64 | Apache-2.0 |
| Security | `edgeai-kyverno` 0.1.0 | Kyverno | wrapper：kyverno 3.10.0 | Hub、Node、Gateway | amd64, arm64 | Apache-2.0 |
| Security | `edgeai-trivy-operator` 0.1.0 | Trivy Operator | wrapper：trivy-operator 0.38.1 | Hub、Node | amd64, arm64 | Apache-2.0 |
<!-- chart-table:end -->

### 刻意不做成 chart 的
| 軟體 | 理由 |
|---|---|
| cert-manager、Rancher Monitoring（Prometheus／Alertmanager）、Longhorn、Fleet、system-upgrade-controller | Rancher 已內建或已安裝，重複上架會衝突 |
| PacketFence | 官方以 VM／ZEN appliance 發行，非 K8s 應用 |
| Mender／RAUC、Zarf／Hauler、Syft、cosign、Cilium | OS OTA、CLI 或 CNI，非 Helm 應用 |
| DeepStream、JetPack、CUDA | 併入 ai-workflow worker 映像（自研） |
| Harmony／Chorus 5GC | 供應商產品 |
| OPA、FreeSWITCH、Forgejo、Perses、Kafka／NATS | 文件列為備案，v1 不採用 |

## 2. Pack 分類在 Rancher 的呈現
- 卡片側標：`catalog.cattle.io/certified` 設為 Pack 名稱（Access & NAC／Vision／Voice/PTT／IoT/OT／RAG／MLOps／Platform／Observability／Security）。
  Rancher UI 對非官方 repo 會把這個值原樣顯示在卡片上（`rancher` 與 `partner` 兩個值保留給官方／合作夥伴，我們不用）。
- 分類篩選：`keywords` 帶 Rancher 允許的分類（Security、Networking、Database、Storage、Monitoring、Repository、Applications、Infrastructure），
  另加 `edge-ai`、`pack-<key>` 方便搜尋。
- 預設 namespace：`catalog.cattle.io/namespace`（每個 Pack 一個 `edgeai-*` namespace）；`catalog.cattle.io/os`／`permits-os` 為 linux。
- 每個 chart 有 `questions.yaml`（安裝表單）、`app-readme.md`（安裝頁頂端說明）、`README.md`（完整說明）。陣列型參數（vLLM 模型清單、Velero 備份位置）請在安裝畫面用 **Edit YAML**。

## 3. 授權注意事項（v2 Roadmap §5）
- **AGPL-3.0**：Grafana、Loki、MinIO — 不修改原始碼、保留 source offer；MinIO 另有社群版縮減與上游 chart 停更（5.4.0）問題，**物件儲存預設用 SeaweedFS**，日誌／長留存可改 VictoriaMetrics／VictoriaLogs（Apache-2.0）。
- **GPL-2.0**：FreeRADIUS、Asterisk — 獨立容器部署、不修改；Asterisk 映像要自建，散布時附原始碼取得方式（或購 Sangoma 商業授權）。
- **自訂授權**：Open WebUI（品牌條款）— 白牌前法務確認。
- **NVIDIA EULA**：Triton 映像（含 CUDA／TensorRT）— 不重新打包映像。
- 其餘為 Apache-2.0／MIT／BSD／EPL／MPL。商標（Rancher、ThingsBoard 等）依各自規範。
- 子 chart 用 Bitnami 映像的（LiteLLM、CVAT、MLflow、Gitea 的選用資料庫）：Bitnami 免費映像 2025-08 起移到 `bitnamilegacy`、不再更新，正式站建議改接 CloudNativePG／Valkey。

## 4. 秘密資料
chart 與 repo 不含任何密碼、金鑰或 token。需要秘密的地方都是「Secret 名稱」參數（`existingSecret` 類），安裝前先建立 Secret；
會落到上游預設密碼的 chart（Harbor、Gitea、Keycloak、MinIO、LiteLLM、FreeRADIUS、Mosquitto、EdgeX）加了安裝前檢查，沒給 Secret 會直接拒絕安裝。

## 5. 映像與架構
- 自寫 chart 的映像都是上游官方映像，位置是參數（`components.<name>.image.repository／tag`），離線站點改指向 Harbor。
- 例外：**Asterisk 沒有官方映像**，`image.repository` 必填（自建）；**Kea** 官方映像只有 amd64，arm64 需自建；**Harbor** 官方映像只有 amd64（chart 預設 nodeSelector amd64）；**vLLM** 官方映像以 amd64 為主，Thor／Spark 用 NVIDIA 的 arm64 映像。

## 6. 在 Rancher 加入
已加過 `edge-app`（127 的 `local`、`edge-thor`）的叢集：**不用重加**，到 Apps → Repositories → `edge-app` → ⋮ → **Refresh**，Apps → Charts 就會出現 `edgeai-*`。

新叢集（每個叢集要各加一次）：Cluster → Apps → Repositories → Create
- Target：**Git repository containing Helm chart or cluster template definitions**
- Git Repo URL：`https://github.com/winson0728/edge-app.git`
- Git Branch：`main`
- 或用 kubectl：
```yaml
apiVersion: catalog.cattle.io/v1
kind: ClusterRepo
metadata: {name: edge-app}
spec: {gitRepo: https://github.com/winson0728/edge-app.git, gitBranch: main}
```

### HTTP 型（index.yaml）
Git 型不需要 `index.yaml`；**不要把 index.yaml 放在 repo 根目錄**：Rancher 的 Git 型 repo 根目錄有 index.yaml 時會改讀它，沒列進去的 chart 會從 Apps 頁消失。
要用 HTTP（`helm repo add`、內部 web server、GitHub Pages）時，用下列指令打包並產生索引到另外的目錄或 `gh-pages` 分支：
```bash
tools/edgeai/package-index.sh <輸出目錄> <對外 URL>
```

## 7. 更新版本
1. 改 `tools/edgeai/catalog.yaml`（上游 `version`、自寫的 `appVersion`／映像 tag、平台預設值、表單）。
2. **chart 有任何改動就把該 chart 的 `version` 加一**，新版本會產生新目錄 `charts/<name>/<新版>/`；舊版目錄保留，Rancher 的已安裝 App 才能看到「可升級」。
3. 下載上游 tgz 到快取目錄（`helm pull`，見 `build.py` 開頭說明），執行：
```bash
python tools/edgeai/build.py --cache <快取目錄>      # 重產 chart 與本文件的清單表
bash tools/edgeai/check.sh                          # 全部 helm lint／template
```
4. 推送前掃描（不得含密碼、內網位址），推到 `main` 後在 Rancher Refresh。

## 8. 驗證紀錄
見 `tools/edgeai/VERIFY.md`。
