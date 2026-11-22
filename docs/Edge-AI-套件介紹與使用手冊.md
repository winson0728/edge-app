# Edge AI 平台套件介紹與功能使用手冊（含 5G 專網使用情境）

- 版本：1.0（2026-11-22）
- 適用：`winson0728/edge-app` 套件庫中的 `edgeai-*` chart（開源套件 32 個、自研模組骨架 11 個）
- 讀者：售前／方案工程師、現場部署工程師、平台維運人員
- 相關文件：
  - 套件庫怎麼加進 Rancher、怎麼維護 → `docs/操作手冊.md`（目前在分支 `claude/aplus-manual-20261122`，尚未合併到 main；要點也寫在 `EDGE-AI-CHARTS.md` §6～§7）
  - 清單、授權、更新版本 → `EDGE-AI-CHARTS.md`
  - 驗證紀錄 → `tools/edgeai/VERIFY.md`
  - 規劃依據 → 《EDGE AI 平台 v2 實行計劃》（三層架構、Pack、Feature F1～F21、§3.3.1 QoS 對照）與《自研模組實行細節規劃》（12 個模組、介面 C1～C11）

> 本手冊不含任何位址、帳號或密碼。範例中的 `example.com`、`192.0.2.x`（文件用位址）都要換成現場值。

---

## 目錄
1. 平台簡介
2. 5G 專網整體架構與資料流
3. 套件介紹與功能使用（依 Pack）
4. 5G 專網使用情境（端到端）
5. 建議部署組合與安裝順序
6. 附錄：Secret 清單、QoS 對照、授權速查、名詞、待確認

---

## 1. 平台簡介

### 1.1 一句話
Edge AI 平台把「5G 專網＋Wi-Fi＋有線接入、SIM 認證與 NAC、AI 影像／IoT／PTT 應用、本地 MLOps、可觀測與資安」做成一組**可以在 Rancher 上點選安裝**的套件，讓同一套軟體跑在中央 Hub、現場 Node、末端 Gateway 三種硬體上，資料與推論都留在場域內。

### 1.2 三層部署角色

| 層級 | 參考硬體 | 架構 | 典型角色 |
|---|---|---|---|
| **Hub**（中央） | x86＋RTX PRO 6000 96GB | amd64 | 身分／政策／目錄／MLOps／Console／長期儲存，5GC 控制面所在 |
| **Node**（現場） | DGX Spark、Jetson Thor 128GB | arm64 | 影像密集推論、VLM 覆核、Site Survival（RADIUS／DHCP／PBX 本地副本） |
| **Gateway**（末端） | Jetson Orin NX 16GB／Orin Nano 8GB | arm64（L4T） | 少量 Camera、IoT 接入、MQTT 上報 |

### 1.3 三種軟體
- **Layer 1 開源套件（32 個）**：直接部署的成熟開源軟體，例如 FreeRADIUS、Asterisk、MediaMTX、Triton、MLflow、Grafana。上游已有 chart 的做成 **wrapper**，原封引用上游 chart、只加平台預設；上游沒有的由我們**自寫**。
- **Layer 2 自研模組（11 個骨架）**：產品 IP 所在的整合控制層，例如 sim-aaa-adapter、access-policy-service、unified-event-engine。**目前只有骨架 chart，沒有程式與映像，無法實際運作**；本手冊說明它們的設計角色，方便規劃。
- **Layer 3 不自研**：K8s、GPU 驅動、推論引擎核心、SIP／RTP 核心、5GC（Harmony／Chorus）等，不在套件庫內。

### 1.4 Pack（Rancher 卡片上的側標）

| Pack | 解決什麼 | 套件 |
|---|---|---|
| Access & NAC | 誰能連網、拿到哪個 VLAN／切片 | FreeRADIUS、Kea DHCP、Keycloak、step-ca、Headscale；自研 sim-aaa-adapter、access-policy-service |
| Vision | Camera 串流、偵測、VLM 覆核 | MediaMTX、Triton、vlm-app（既有）；自研 ai-workflow-controller |
| Voice/PTT | 對講、廣播、派遣 | Asterisk；自研 ptt-gateway |
| IoT/OT | 設備資料接入 | Mosquitto、EdgeX、ThingsBoard；自研 device-adapter |
| RAG | 現場知識助理、LLM 服務 | vLLM、LiteLLM、Open WebUI、Qdrant |
| MLOps | 標註、訓練紀錄、模型上架 | MLflow、CVAT；自研 model-release-controller |
| Platform | 平台底座 | Harbor、Gitea、Argo CD、CloudNativePG、Valkey、SeaweedFS、MinIO、Velero；自研 catalog-controller、lifecycle-operator、event-engine、portal-ui、audit-service |
| Observability | 指標、日誌、追蹤 | Grafana、Loki、VictoriaMetrics＋Logs、OTel Collector |
| Security | 準入、弱點、秘密 | Kyverno、Trivy Operator、External Secrets |

---

## 2. 5G 專網整體架構與資料流

### 2.1 架構圖

```text
             ┌──────────────── 終端 ────────────────┐
             │ 5G 手持機／CPE／5G Camera／AGV／IoT 閘道 │   Wi-Fi 手機（EAP-AKA′）  有線設備（802.1X／MAB）
             └───────────────┬──────────────────────┘          │                      │
                         gNB（RAN）                            AP                  Switch
                             │ N2/N3                            │ RADIUS              │ RADIUS
          ┌──────────────────▼─────────────────┐              │                      │
          │ 5GC：AMF／SMF／UDM／AUSF（Harmony）  │◀── AV ── sim-aaa-adapter ◀── FreeRADIUS ─┘
          │ UPF（local breakout → 場域 DNN）     │              access-policy-service（VLAN／角色／CoA）
          └──────────────────┬─────────────────┘
                             │ 場域 DNN（不出場域）
   ┌─────────────────────────▼──────────────────────────────────────────────────────┐
   │ Edge 叢集（K3s／RKE2，Rancher 管理）                                              │
   │  Vision：Camera ─RTSP→ MediaMTX → ai-workflow → Triton（偵測）→ vLLM（VLM 覆核） │
   │  IoT：設備 → device-adapter／EdgeX → Mosquitto（MQTT）                           │
   │  事件：unified-event-engine（去重／關聯／規則）→ ptt-gateway → Asterisk（廣播）  │
   │  RAG：手持機 → Open WebUI → LiteLLM → vLLM ＋ Qdrant                             │
   │  底座：Keycloak／step-ca／Harbor／Gitea／CloudNativePG／Valkey／SeaweedFS         │
   │  觀測：OTel → VictoriaMetrics／Logs → Grafana；資安：Kyverno／Trivy／ESO          │
   └────────────────────────────────────────────────────────────────────────────────┘
                 │ Headscale／WireGuard（站點 Mesh、遠端維運）
             中央 Hub ⇄ 各站 Node ⇄ Gateway
```

### 2.2 5G 專網和這些套件的關係
- **UPF local breakout**：終端流量在場域 UPF 直接進「場域 DNN」，再到 Edge 叢集服務，影像與推論不回中央、不出場域。這是 Vision、RAG、PTT 低延遲的前提。
- **同一張 SIM 走兩種網**：5G 用 5G-AKA（UDM／AUSF）；同一張 SIM 在 Wi-Fi 用 EAP-AKA′，經 FreeRADIUS → sim-aaa-adapter 向同一個 UDM 取認證向量（AV）。授權（VLAN／角色）統一由 access-policy-service 決定。
- **QoS 一致**：同一類業務在 5G（5QI）、Wi-Fi（WMM）、有線（DSCP／802.1p）用同一套等級（§6.2 對照表）。套件本身不設 5QI；5QI 在 5GC 的 DNN／切片設定，套件端負責「用對的 DNN、對的埠、對的 DSCP」。
- **Windows 筆電不支援 Wi-Fi EAP-AKA′**：改走 EAP-TLS（step-ca 發憑證）；老舊 IoT 走 MAB＋隔離 VLAN。

---

## 3. 套件介紹與功能使用（依 Pack）

每個套件都依同樣格式說明：
- **是什麼**：套件本身。
- **在平台的角色**。
- **主要功能**。
- **安裝前準備**：要先建立的 Secret 與關鍵參數。安裝表單在 Rancher → Apps → Charts → 套件名稱。
- **基本使用**。
- **5G 專網情境**。

通用規則：
- 密碼、金鑰一律先建 Secret，表單只填 Secret 名稱。需要 Secret 的 chart 沒給就會拒絕安裝。
- 陣列型參數請在安裝畫面切到 **Edit YAML** 填寫，例如 vLLM 的模型清單、Velero 的備份位置。
- 預設 namespace 是每個 Pack 一個：`edgeai-access`、`edgeai-vision`、`edgeai-voice`、`edgeai-iot`、`edgeai-rag`、`edgeai-mlops`、`edgeai-platform`、`edgeai-observability`、`edgeai-security`。

### 3.1 Access & NAC

#### FreeRADIUS（`edgeai-freeradius`，自寫，GPL-2.0）
- **是什麼**：RADIUS 伺服器 3.2，Wi-Fi／有線 802.1X 認證的核心。
- **角色**：AP／Switch 的 RADIUS server。之後經 sim-aaa-adapter 做 SIM 的 EAP-AKA′，並向 access-policy-service 取授權結果。
- **主要功能**：
  - 認證 1812／UDP、帳務 1813／UDP；
  - 內建 PAP／CHAP／MSCHAP／EAP 框架；
  - chart 提供只聽 IPv4 的預設 site（多數 Pod 網路沒有 IPv6）。
- **安裝前準備**：建 NAS 共用密鑰 Secret，內含 `clients.conf`：
  ```bash
  kubectl -n edgeai-access create secret generic freeradius-clients --from-file=clients.conf=./clients.conf
  ```
  表單填「NAS clients Secret 名稱」。AP／Switch 在叢集外時，「Service 類型」選 NodePort 或 LoadBalancer。
- **基本使用**：
  - AP／Switch 的 RADIUS server 指到 Service 位址，共用密鑰用 `clients.conf` 裡的值。
  - 連線測試：在 Pod 內 `radclient` 送 Access-Request。未建使用者時回 Access-Reject，代表連線與密鑰都正確。
- **5G 專網情境**：
  - 與 5G 同一張 SIM 的手機在 Wi-Fi 也能用 SIM 認證，要等 sim-aaa-adapter 完成。
  - Node 上跑一份副本做 Site Survival：WAN 斷線時，現場 Wi-Fi 認證不中斷。

#### Kea DHCP（`edgeai-kea-dhcp`，自寫，MPL-2.0）
- **是什麼**：ISC Kea DHCPv4 3.0。
- **角色**：場域 VLAN 的 DHCP；Site Survival 時由 Node 在本地續租。
- **主要功能**：
  - 以 hostNetwork 直接在節點網卡服務；
  - 表單可設網卡、子網、位址池、閘道、DNS；
  - 租約檔可持久化。
- **安裝前準備**：用 `nodeSelector` 鎖定要服務的節點，避免同網段出現兩台 DHCP。官方映像只有 amd64。
- **基本使用**：預設值是文件用的 192.0.2.0/24，**一定要改成現場網段**。查租約：`kubectl exec` 進 Pod 看 `/var/lib/kea/dhcp4.leases`。
- **5G 專網情境**：
  - 5G 終端的 IP 由 SMF／UPF 依 DNN 位址池配發，**不經 Kea**。
  - Kea 服務的是 Wi-Fi／有線網段。Camera 用 5G 時走 UPF 位址池，用有線時走 Kea。

#### Keycloak（`edgeai-keycloak`，wrapper：codecentric keycloakx，Apache-2.0）
- **是什麼**：OIDC／SSO 身分服務。
- **角色**：
  - 平台與各模組的登入來源，Console、Grafana、Harbor、Gitea 都可以接；
  - 也是 access-policy-service 同步 App 權限（client scopes）的對象。
- **安裝前準備**：
  - 管理者 Secret（`username`、`password`）；
  - PostgreSQL：可用 CloudNativePG 建，主機與密碼 Secret。
- **基本使用**：
  - 建 realm `edge-ai`，各系統建 OIDC client；
  - 角色對應部門，例如保全、維修、醫護。
- **5G 專網情境**：同一個人的 SIM（IMSI）、手機 App 登入身分、PTT 群組，對應到同一個 Keycloak 使用者與角色。角色一改，網路與 App 權限一起改（由 access-policy-service 負責）。

#### step-ca 私有 CA（`edgeai-step-ca`，wrapper：smallstep 官方，Apache-2.0）
- **是什麼**：私有憑證機構，支援 ACME、EST。
- **角色**：
  - 裝置身分：ZTP 時的裝置憑證；
  - 服務間 mTLS；
  - Windows 筆電改走 EAP-TLS 時的使用者／裝置憑證。
- **安裝前準備**：預設由上游 bootstrap Job 在叢集內產生 CA 並存成 Secret。正式站建議離線 `step ca init --helm` 後帶入，CA 私鑰另外保管。
- **基本使用**：搭配 cert-manager 的 ACME Issuer 自動簽發服務憑證；裝置用 `step ca certificate` 申請。
- **5G 專網情境**：
  - 5G CPE、Camera、Gateway 上電後以裝置憑證 call-home（mTLS）完成綁定，對應 v2 的 F2 ZTP；
  - 不支援 Wi-Fi EAP-AKA′ 的終端，改用 EAP-TLS 憑證上網。

#### Headscale（`edgeai-headscale`，自寫，BSD-3）
- **是什麼**：自架的 Tailscale 控制面（WireGuard Mesh）。
- **角色**：串接 Hub 與各站 Node／Gateway 的管理網，用於遠端維運與 GitOps 同步。
- **安裝前準備**：
  - 對外 URL（經 Ingress／反向代理）；
  - MagicDNS 網域，不可與 server_url 網域相同；
  - 預設資料存 PVC。
- **基本使用**：
  - 建使用者與預授權金鑰：`kubectl exec deploy/<release>-headscale -- headscale users create site-a`；
  - 節點以 `tailscale up --login-server <URL>` 加入。
- **5G 專網情境**：
  - 行動指揮車以 5G／LTE 動態 IP 回連 Hub，NAT 穿透後維持同一個管理位址；
  - 離線站點可改用內建 DERP。

#### sim-aaa-adapter（`edgeai-sim-aaa-adapter`，**自研骨架**）
- **角色**：Wi-Fi EAP-AKA／AKA′ 與 Harmony UDM／AUSF 的介接，**只做認證**。
  - 認證向量（AV）的預取與一次性使用；
  - SQN resync；
  - pseudonym 與 fast re-auth。
- **介面**：FreeRADIUS 經 rlm_python3 呼叫 `/v1/auth/vectors`、`/v1/auth/resync`、`/v1/auth/result`，逾時 1 秒。
- **安全設計**：Ki／OPc 永不經手；AV 只放記憶體與短 TTL 的 Valkey；NetworkPolicy 只放行 FreeRADIUS。
- **5G 專網情境**：5G 的 SIM 不用另外發 Wi-Fi 帳號，同一張卡在 Wi-Fi 也通。目標是 full auth P95 ≤ 800ms、fast re-auth ≤ 200ms。

#### access-policy-service（`edgeai-access-policy-service`，**自研骨架**）
- **角色**：統一 5G、Wi-Fi、有線的授權（PDP），也就是決定 VLAN、角色、dACL、session timeout。
  - 維護即時 session 表；
  - 政策改變時發 CoA／Disconnect；
  - 同步 MQTT ACL、Keycloak 權限、5GC 的 DNN／切片。
- **安全預設**：決策服務不可達時，FreeRADIUS 把終端放進隔離 VLAN（fail-close）。
- **5G 專網情境**：
  - 一個員工被停權，5G、Wi-Fi、App、MQTT 權限同時收回；
  - 交接班時，角色依時段自動切換 PTT 群組與可看到的 Camera。

### 3.2 Vision

#### MediaMTX（`edgeai-mediamtx`，自寫，MIT）
- **是什麼**：串流伺服器，支援 RTSP、RTMP、HLS、WebRTC、SRT。
- **角色**：
  - Camera 串流的匯流點，推論 worker 從這裡拉流；
  - 觀看端用 HLS／WebRTC；
  - Evidence 錄影（環形）。
- **主要功能**：
  - RTSP 8554（RTP／RTCP UDP 8000／8001）、RTMP 1935、HLS 8888、WebRTC 8889＋8189／UDP、SRT 8890／UDP；
  - 有 API 9997 與 metrics 9998，只開給 `apiAllowedCIDRs`，NetworkPolicy 也只放行同一個 release。
- **安裝前準備**：Camera 或觀看端在叢集外時選 NodePort／LoadBalancer。要錄影就開「環形錄影」並設保留時間與 PVC。
- **基本使用**：
  - Camera 推流到 `rtsp://<服務位址>:8554/<路徑名>`，或在 config 用 `source:` 主動拉 Camera；
  - 觀看：`http://<服務位址>:8888/<路徑名>`（HLS）。
  - 已在 Lab 驗證：推流後可讀回 h264。
- **5G 專網情境**：
  - 5G Camera／5G CPE 後的 Camera，經 UPF local breakout 直接推到場域 MediaMTX，影像不出場域；
  - 上行 Camera 流建議用 5QI-7（AF41）：可丟幀，但不能有高延遲抖動；
  - 5G 上行頻寬有限時，用 SRT（抗丟包）或降解析度。
- **注意**：預設任何來源都能推流、觀看。正式站要改成帳號制，密碼用 `MTX_*` 環境變數從 Secret 帶入。

#### Triton Inference Server（`edgeai-triton`，自寫，BSD-3＋NVIDIA EULA）
- **是什麼**：NVIDIA 推論伺服器。
- **角色**：YOLO、TensorRT 等偵測模型的服務端，ai-workflow-controller 以 gRPC 呼叫。
- **主要功能**：HTTP 8000、gRPC 8001、metrics 8002；模型庫輪詢載入（`--model-control-mode=poll`）。
- **安裝前準備**：
  - 需要 GPU 與 `nvidia` RuntimeClass；
  - 模型庫用 PVC 或 `s3://`；
  - x86／Thor／Spark 用 `26.11-py3`，Orin（JetPack 6）要改 JetPack 版映像。
- **基本使用**：把模型以 Triton 目錄結構（`<模型>/<版本>/model.plan` 與 `config.pbtxt`）放進模型庫，30 秒內自動載入；用 `/v2/health/ready` 確認。
- **5G 專網情境**：
  - Thor／Spark Node 在場域端做多路偵測，事件端到端 P95 目標 ≤ 500ms；
  - TensorRT engine 綁 GPU 世代，要由 model-release-controller 在對應世代建置。

#### vlm-app（既有 chart `vlm-app` 0.1.1）
- 本套件庫原有的 CCTV 監控應用（YOLO11＋本地 VLM）。已在 127 與 Thor 實裝，說明見 VLM-APP 專案的操作手冊。
- 它是 Vision Pack 目前「可以直接 demo」的應用，與 MediaMTX／Triton 的平台化路線並行。

#### ai-workflow-controller（`edgeai-ai-workflow-controller`，**自研骨架**）
- **角色**：
  - 以 `VisionPipeline` CR 描述一條影像管線：Camera 來源、區域、偵測模型、觸發規則、VLM 覆核、隱私遮罩、輸出事件；
  - controller 依節點類型建立 worker：Jetson 用 DeepStream 的 ds-worker，其他用 gst-worker。
- **重點**：VLM 有硬性併發預算（保護 VRAM）；隱私遮罩是 F6 Privacy Shield 的掛點。
- **5G 專網情境**：低層用 YOLO 預篩 → 中層 VLM 覆核定級 → 事件送 event engine，對應 F8 Event Triage，目標是誤報降低 60% 以上。

### 3.3 Voice/PTT

#### Asterisk（`edgeai-asterisk`，自寫，GPL-2.0）
- **是什麼**：IP PBX 22 LTS，提供 SIP／RTP、ConfBridge、ARI。
- **角色**：分機、對講群組的媒體面（混音、播放、錄音）；ptt-gateway 經 ARI 控制。
- **安裝前準備**：
  - **映像要自建**：官方不發容器映像，「映像位置」必填；
  - 分機與密碼放 `pjsip.conf` Secret，ARI 帳密放 `ari.conf` Secret；
  - 使用 hostNetwork，RTP 埠段預設 10000～10199。
- **基本使用**：SIP 終端或軟體電話註冊到節點位址的 5060；ptt-gateway 經 `http://<節點>:8088/ari` 控制 ConfBridge。
- **5G 專網情境**：
  - 5G 手持機的語音建議走 5QI-1（EF）；目標口到耳 P95 ≤ 300ms（LAN）／600ms（5G）；
  - Node 上跑一份 Survivable Gateway：WAN 斷時，現場分機互打與 PTT 群組照常。

#### ptt-gateway（`edgeai-ptt-gateway`，**自研骨架**）
- **角色**：企業 PTT 控制層，媒體交給 Asterisk。
  - 群組、floor control（誰在講）、4 級優先權、緊急搶占；
  - 事件觸發的臨時群組；
  - 錄音稽核。
- **介面**：App 以 WebSocket（8081）做 talk-request／grant；event engine 呼叫 `/v1/broadcast` 做 TTS 廣播。
- **5G 專網情境**：
  - 工廠禁區入侵 → event engine → 對「保全」群組廣播 TTS，P95 ≤ 3 秒；
  - 不做 3GPP MCPTT（v2.0 之後再評估）。

### 3.4 IoT/OT

#### Eclipse Mosquitto（`edgeai-mosquitto`，自寫，EPL-2.0）
- **是什麼**：MQTT broker 2.0。
- **角色**：平台事件匯流排，承接 AI 事件、IoT telemetry、5GC／UPF 告警；topic 慣例 `edge/{tenant}/{site}/events/{sourceType}/{severity}`。
- **安裝前準備**：
  - 預設不允許匿名，必須給帳密檔 Secret（`passwd` 鍵，由 `mosquitto_passwd` 產生的雜湊檔），或開 Dynamic Security；
  - WebSocket（9001）可選。
- **基本使用**：
  ```bash
  mosquitto_sub -h <broker> -u <user> -P <password> -t 'edge/#'
  mosquitto_pub -h <broker> -u <user> -P <password> -t edge/t1/site-a/events/ai/3 -m '{...}'
  ```
  已在 Lab 驗證：帳密正確可收發，錯誤密碼與匿名都被拒。
- **5G 專網情境**：
  - IoT 閘道與 AGV 經 5G 上報；
  - 告警類訊息建議 5QI-8（AF31），小流量、高優先；
  - 開 Dynamic Security 後，由 access-policy-service 依角色下發 ACL。

#### EdgeX Foundry core（`edgeai-edgex`，自寫，Apache-2.0）
- **是什麼**：EdgeX 4.0 核心服務：keeper、metadata、data、command、UI、內部 PostgreSQL 與 MQTT，以 no-secty 模式啟動。
- **角色**：設備抽象層，管理 Device Profile 與設備，收讀數、下命令。Modbus／ONVIF 等 Device Service 依現場另裝。
- **安裝前準備**：建資料庫密碼 Secret（`password` 鍵）。服務名稱沿用 EdgeX 慣例，**一個 namespace 只能裝一套**。
- **基本使用**：
  - UI 在 4000 埠；
  - REST：`/api/v3/ping`、`/api/v3/deviceprofile/all`（metadata 59881）、`/api/v3/event`（core-data 59880）；
  - 已在 Lab 驗證：各服務 ping 與 UI 正常。
- **5G 專網情境**：
  - 產線 PLC 經 5G 工業閘道（Modbus TCP over 5G）接入 EdgeX，讀數轉 MQTT 給 event engine；
  - 設備下命令走 core-command，建議與控制類同一個 DNN，並開 QoS（AGV 控制可用 5QI-82／83）。

#### ThingsBoard CE（`edgeai-thingsboard`，自寫，Apache-2.0，選配）
- **是什麼**：IoT 平台（儀表板、規則鏈、設備管理），單機 tb-postgres 映像。
- **角色**：需要現成 IoT 儀表板時的選配；文件以 EdgeX 為主。
- **安裝前準備**：預設建 10Gi PVC；首次登入使用官方預設系統帳號，**登入後立刻改密碼**。
- **5G 專網情境**：
  - 5G 環境感測器（溫溼度、氣體）經 MQTT 1883 或 CoAP 5683 直接上報；
  - 園區、醫院的設施監控看板。

#### device-adapter（`edgeai-device-adapter`，**自研範本骨架**）
- **角色**：device-adapter-sdk 產出的設備接入程式範本。Connector 讀取專有協定 → 轉成標準 telemetry 送 MQTT，可選擇轉 EdgeX。
- **使用方式**：每種設備裝一個 release，例如 `plc-line1`、`cpe-vendor-x`；表單填協定、設備位址、topic 前綴。
- **5G 專網情境**：接 5G CPE 原廠 API，把訊號品質（RSRP／SINR）、流量轉成 telemetry，和網路告警一起進事件中心。

### 3.5 RAG

#### vLLM production-stack（`edgeai-vllm`，wrapper：vLLM 官方，Apache-2.0）
- **是什麼**：OpenAI 相容的 LLM／VLM 推論服務，含路由器。
- **角色**：VLM 覆核、RAG 問答、AIOps 對話的模型服務。
- **安裝前準備**：
  - 需要 GPU；
  - 模型清單 `vllm-stack.servingEngineSpec.modelSpec` 用 **Edit YAML** 填（`name`、`repository`、`tag`、`modelURL`、`requestGPU`）；
  - HF token 用 Secret；
  - Thor／Spark 要改用 NVIDIA 的 arm64 vLLM 映像。
- **基本使用**：路由器 Service 提供 `/v1/chat/completions`，任何 OpenAI SDK 都能呼叫。
- **5G 專網情境**：所有推論在場域內完成（「資料不出場域」）；手持機經 5G 呼叫，不依賴公有雲 API。

#### LiteLLM Proxy（`edgeai-litellm`，wrapper：官方 OCI chart，MIT）
- **是什麼**：統一的 LLM 閘道。
- **角色**：
  - 把 vLLM（以及未來其他模型）包成單一 API；
  - 金鑰、用量、限流；
  - AI Agent 動作的稽核日誌（v2 §3.5 Agent 治理）。
- **安裝前準備**：master key Secret（`masterkey` 鍵）。預設一併部署 PostgreSQL（Bitnami 子 chart），正式站建議改接 CloudNativePG。
- **基本使用**：在 LiteLLM 設定把 vLLM 路由器加為模型後端，為每個應用發虛擬金鑰。
- **5G 專網情境**：不同部門或租戶用不同虛擬金鑰與配額；Console 的 AIOps Chat 也從這裡出去，所有呼叫都可稽核。

#### Open WebUI（`edgeai-open-webui`，wrapper：官方，自訂授權）
- **是什麼**：聊天與 RAG 前端。
- **角色**：現場知識助理的使用者介面，例如 SOP、設備手冊、病房規範問答。
- **安裝前準備**：
  - 「OpenAI 相容 API 位址」預設指向 LiteLLM；
  - 預設不安裝 Ollama；
  - 資料存 5Gi PVC。
- **授權注意**：品牌條款（v0.6+），白牌前要法務確認。
- **5G 專網情境**：巡檢人員在現場用 5G 平板開網頁問「這台設備的 E-17 告警怎麼處理」，答案來自場域內的手冊向量庫。

#### Qdrant（`edgeai-qdrant`，wrapper：官方，Apache-2.0）
- **是什麼**：向量資料庫。
- **角色**：RAG 知識庫、事件與人物的向量搜尋。
- **安裝前準備**：預設建 10Gi PVC；可開「自動產生 API key」，由上游產生並存成 Secret。
- **基本使用**：REST 6333、gRPC 6334；用 collection 存放文件向量。
- **5G 專網情境**：場域文件只在本地向量化與檢索；Hub 統一建索引，再同步到需要的 Node。

### 3.6 MLOps

#### MLflow（`edgeai-mlflow`，wrapper：community-charts，Apache-2.0）
- **是什麼**：實驗紀錄與 Model Registry。
- **角色**：模型版本的單一來源，是 model-release-controller 的上游。
- **安裝前準備**：預設 SQLite 適合試用；正式站後端接 CloudNativePG，artifact 接 SeaweedFS S3，帳密都用 Secret。
- **基本使用**：訓練程式以 `MLFLOW_TRACKING_URI` 指向服務；模型註冊後晉升到 Production。
- **5G 專網情境**：Hub 上集中訓練與註冊，經 Harbor／GitOps 下發到各場域 Node。

#### CVAT（`edgeai-cvat`，wrapper：官方 repo 內 chart，MIT）
- **是什麼**：影像標註平台。
- **角色**：Model Flywheel（F9）的難例標註佇列：誤報、漏報片段進 CVAT，標註後回到訓練。
- **安裝前準備**：資源需求高，建議 Hub 有 8 GiB 以上可用記憶體；子 chart 含 Bitnami PostgreSQL／Redis；只有 amd64。
- **5G 專網情境**：現場人員在 Console 一鍵標記誤報，片段自動進 CVAT。影像不離開企業網路。

#### model-release-controller（`edgeai-model-release-controller`，**自研骨架**）
- **角色**：MLflow Production → 依 GPU 世代（Orin／Thor／RTX PRO／Spark）建 TensorRT engine 與 benchmark → 過 Gate（例如 mAP 下降不超過 1%）→ cosign 簽章 → 推 Harbor → 更新 GitOps → Triton shadow、晉升、回滾。
- **5G 專網情境**：新版安全帽模型先以 shadow 在一個站點比對，確認後再全站切換；失敗時一鍵回滾。

### 3.7 Platform

#### Harbor（`edgeai-harbor`，wrapper：官方，Apache-2.0）
- **角色**：映像、Helm chart、模型包、app-pack 的 OCI 倉庫；離線站點的映像來源。
- **安裝前準備**：
  - 管理者密碼 Secret（`HARBOR_ADMIN_PASSWORD` 鍵），沒給就拒絕安裝，避免落到上游預設密碼；
  - 對外 URL；
  - 官方映像只有 amd64，預設 nodeSelector 為 amd64。
- **5G 專網情境**：各站 Node 經 Headscale 從 Hub 的 Harbor 拉映像；GitOps 同步走 5QI-9（BE）、離峰、限速。

#### Gitea（`edgeai-gitea`，wrapper：官方，MIT）
- **角色**：GitOps 的 values repo。edge-app-catalog-controller 把客戶答案 commit 到這裡，再交給 Fleet 或 Argo CD 套用。
- **安裝前準備**：管理者 Secret（`username`、`password`）；預設 SQLite＋記憶體 cache；10Gi PVC。
- **5G 專網情境**：每個站點、每個 App 的設定都有版本可追溯；變更即稽核。

#### Argo CD（`edgeai-argo-cd`，wrapper：官方，Apache-2.0，選配）
- **角色**：GitOps 引擎。Rancher 已內建 Fleet，兩者擇一；不要讓兩者管同一批資源。
- **安裝後**：初始密碼在 `argocd-initial-admin-secret`，由上游隨機產生。

#### CloudNativePG Operator（`edgeai-cloudnative-pg`，wrapper：官方，Apache-2.0）
- **角色**：PostgreSQL operator。Keycloak、MLflow、LiteLLM 與自研模組（policy、event engine、audit、sim-aaa）的資料庫。
- **基本使用**：裝好 operator 後建 `Cluster` CR（範例見 chart README），密碼由 operator 產生在 `<叢集名>-app` Secret；Hub Duo HA 時 `instances` 設 2～3。

#### Valkey（`edgeai-valkey`，wrapper：官方，BSD-3）
- **角色**：Redis 相容快取。sim-aaa-adapter 存 AV，event engine 用來去重與延時佇列。Redis 7.4 起改了授權，因此改用 Valkey。
- **基本使用**：`valkey-cli` 連 6379。已在 Lab 驗證 SET／GET（9.1.3）；要認證就開 ACL 並給使用者 Secret。

#### SeaweedFS（`edgeai-seaweedfs`，wrapper：官方，Apache-2.0）
- **角色**：S3 相容物件儲存，平台預設（取代 AGPL 的 MinIO）。存放 MLflow artifact、Velero 備份、稽核 anchor、Evidence 歸檔。
- **安裝前準備**：S3 帳密用上游的 `filer.s3.enableAuth`＋`existingConfigSecret`。

#### MinIO（`edgeai-minio`，wrapper：官方，AGPL-3.0，選配）
- **授權與維護風險**：授權風險中高，上游 chart 已停止更新（5.4.0）。
- **建議**：優先用 SeaweedFS；必須用時要給 root 帳密 Secret，並確認授權。

#### Velero（`edgeai-velero`，wrapper：官方，Apache-2.0）
- **角色**：K8s 資源與 PV 的備份、還原，上送 SeaweedFS S3。
- **安裝前準備**：S3 憑證 Secret（`cloud` 鍵）。備份位置與 plugin 用 **Edit YAML** 填。
- **5G 專網情境**：站點級還原演練（v2 §3.1.3），目標 RTO ≤ 4h（Hub）、≤ 1h（Edge Node 重刷）。

#### edge-app-catalog-controller／app-lifecycle-operator（`edgeai-app-catalog-controller`、`edgeai-app-lifecycle-operator`，**自研骨架**）
- **角色**：
  - 把 Helm 包成「客戶可回答的問題」。Catalog（Hub）管理 `AppPack` 目錄、preflight（GPU、VRAM、K3s 版本、儲存、授權）、離線授權 JWT；
  - 每個叢集的 operator 以 `EdgeApp` CR 安裝、升級、回滾。
- **兩種部署模式**：GitOps（commit 到 Gitea）與 air-gap（Helm SDK 直接安裝）。
- **5G 專網情境**：新站點只要回答 6 個問題（Camera 數、區域、PTT 群組…），15 分鐘內 Pack Ready。

#### unified-event-engine（`edgeai-unified-event-engine`，**自研骨架**）
- **角色**：
  - 處理流程：收 CloudEvents（MQTT／HTTP）→ schema 驗證（失敗進 DLQ）→ 補充資訊 → 去重 → 跨來源關聯 → CEL 規則 → 動作派送（PTT 廣播、Webhook、Email、存 Evidence、開單）→ 升級鏈 → Incident Timeline；
  - chart 附一個規則檔範例。
- **5G 專網情境**：
  - 「UPF N3 丟包上升」＋「同區 Camera 斷流」關聯成一個網路事件，不讓值班者收到兩份通知；
  - 「禁區入侵」未確認 5 分鐘 → 自動升級給主管。

#### edge-portal-ui（EdgeOne Console，`edgeai-portal-ui`，**自研骨架**）
- **角色**：客戶日常的單一入口（F1）。
  - 頁面：站點／裝置總覽、App 安裝精靈、事件中心、SIM／用戶管理、Camera／Pipeline、PTT 派遣、稽核查詢；
  - BFF 聚合各模組的 Admin API，Keycloak 登入，Grafana 圖表以嵌入方式呈現。
- **5G 專網情境**：開卡、停卡、IMSI 對應角色（F5 SIM 生命週期）都在 Console 完成，客戶不需要進 5GC 的工程介面。

#### edge-audit-service（`edgeai-audit-service`，**自研骨架**）
- **角色**：append-only 雜湊鏈稽核：誰、何時、看了哪路 Camera、匯出了什麼、Agent 做了什麼；每日 anchor；簽章匯出；保留政策。本地 spool 在斷線時緩衝。
- **5G 專網情境**：醫院場域的個資稽核、Evidence 證據鏈（F14）。

### 3.8 Observability

#### Grafana（`edgeai-grafana`，wrapper：官方，AGPL-3.0）
- **角色**：Pack 儀表板，Console 以嵌入方式呈現；Rancher Monitoring 內建的那份給平台層用。
- **安裝前準備**：管理者 Secret（`admin-user`、`admin-password`），空白則上游隨機產生。
- **授權注意**：不修改原始碼、保留 source offer。

#### Loki（`edgeai-loki`，wrapper：官方，AGPL-3.0）
- **角色**：日誌，預設 SingleBinary＋檔案系統，適合單站 Hub。替代方案是 VictoriaLogs。

#### VictoriaMetrics＋VictoriaLogs（`edgeai-victoria`，wrapper：官方，Apache-2.0）
- **角色**：Prometheus 的長期留存與日誌，用來替代 AGPL 元件，兩者可個別開關。已在 Lab 驗證健康檢查。
- **基本使用**：
  - Prometheus 以 `remote_write` 寫到 `:8428/api/v1/write`；
  - 日誌送 `:9428`；
  - Grafana 加 Prometheus 型資料來源指向 8428。

#### OpenTelemetry Collector（`edgeai-otel-collector`，wrapper：官方，Apache-2.0）
- **角色**：各模組 telemetry-client 的收集點，接收 OTLP 後轉送 Victoria／Loki。可用 deployment 或 daemonset 模式。

**5G 專網情境（可觀測性）**：
- 5GC／UPF 與 gNB 的 KPI 由現有 Prometheus 收集，集中到 VictoriaMetrics。gNB 經 O1／SNMP／廠商 API 收集，屬 v2 §3.3.2 的「監控 in scope」。
- 套件 SLO 一起看，例如：
  - Attach 成功率 ≥ 99%；
  - UPF N3 丟包 ≤ 0.1%；
  - RADIUS 認證 P95 ≤ 800ms；
  - PTT 口到耳 P95 ≤ 300ms。

### 3.9 Security

#### Kyverno（`edgeai-kyverno`，wrapper：官方，Apache-2.0）
- **角色**：準入策略。例如 cosign 驗章（只允許簽章過的映像）、namespace 預設拒絕、禁止 privileged。策略不放在同一個 release，之後以 policy bundle 下發。

#### Trivy Operator（`edgeai-trivy-operator`，wrapper：官方，Apache-2.0）
- **角色**：叢集內映像弱點與組態掃描，作為 CVE SLA 的依據（Critical ≤ 14 天）。離線站點的弱點資料庫要指向 Harbor 內的鏡像。

#### External Secrets Operator（`edgeai-external-secrets`，wrapper：官方，Apache-2.0）
- **角色**：從中央 Vault／KMS 同步 Secret 到各站，取代手動 `kubectl create secret`。

**5G 專網情境（資安）**：
- 5G 終端都在場域 DNN 內，平台服務仍以 NetworkPolicy 預設限制來源；
- 自寫與骨架 chart 都內建 NetworkPolicy；
- 裝置以 step-ca 憑證取得身分；未註冊的裝置不得取得任何服務（v2 設計原則 8）。

---

## 4. 5G 專網使用情境（端到端）

以下情境的「狀態」欄：
- **可 demo**：用目前可安裝的套件就能展示；
- **部分**：平台底座可裝，自研模組完成後才完整；
- **規劃**：依賴的自研模組尚未實作。

### 情境 A：一張 SIM 通行 5G 與 Wi-Fi（Access & NAC）
- **目標**：員工手機的 SIM 在 5G 直接上網；進到 Wi-Fi 覆蓋區自動用同一張 SIM 認證（EAP-AKA′），拿到同一個角色的 VLAN。
- **流程**：
  1. 手機連 SSID → AP 送 RADIUS 給 FreeRADIUS；
  2. FreeRADIUS 經 sim-aaa-adapter 向 Harmony UDM 取 AV，完成 EAP-AKA′；
  3. FreeRADIUS 向 access-policy-service 取授權結果（VLAN、dACL、角色 VSA）；
  4. 角色變更時，policy 發 CoA 讓 AP 立即套用。
- **使用套件**：FreeRADIUS、sim-aaa-adapter（骨架）、access-policy-service（骨架）、Valkey、CloudNativePG、Keycloak；Windows 筆電改走 step-ca 的 EAP-TLS。
- **層級**：Hub（主）＋Node（Survival 副本）。
- **狀態**：**部分**。FreeRADIUS 可裝；EAP-AKA′ 要等自研模組。另有一個獨立的 EAP-AKA PoC 專案，可評估是否整合。

### 情境 B：工廠禁區入侵與安全帽偵測（Vision＋事件＋PTT）
- **目標**：5G Camera 拍到禁區有人或未戴安全帽 → 3 秒內對保全群組 PTT 廣播，並留存證片段。
- **流程**：
  1. 5G Camera → UPF local breakout → MediaMTX（RTSP）；
  2. ai-workflow worker 拉流 → Triton YOLO 偵測 → 命中區域規則 → vLLM VLM 覆核；
  3. 事件送 Mosquitto → unified-event-engine 去重、關聯、規則；
  4. → ptt-gateway → Asterisk 對「保全」群組播 TTS；
  5. MediaMTX 擷取前 5 秒、後 10 秒存成 Evidence；
  6. 未確認 5 分鐘 → 升級給主管。
- **QoS**：Camera 上行 5QI-7（AF41）；PTT 語音 5QI-1（EF）；告警 MQTT 5QI-8（AF31）。
- **使用套件**：MediaMTX、Triton、vLLM、Mosquitto、Asterisk；骨架 ai-workflow-controller、unified-event-engine、ptt-gateway；觀測用 Grafana／Victoria。
- **層級**：Thor／Spark Node 做推論；Hub 歸檔。
- **狀態**：**部分**。
  - 串流、MQTT 已在 Lab 驗證；Triton／vLLM 需要 GPU 環境另行驗證。
  - 現階段可先用既有的 **vlm-app** 展示「YOLO＋VLM 判讀」。

### 情境 C：廠區／院區 PTT 派遣（Voice/PTT）
- **目標**：5G 手持機與 Wi-Fi 手機在同一個對講群組。緊急呼叫可搶占；交接班時群組依角色自動調整。
- **流程**：
  1. App 以 WebSocket 向 ptt-gateway 申請發話權；
  2. ptt-gateway 經 ARI 讓 Asterisk ConfBridge 解除該成員靜音、靜音其他人；
  3. 群組成員來自 access-policy-service 的角色（pttGroup）。
- **QoS**：語音 5QI-1（EF，802.1p 5）；目標口到耳 ≤ 300ms（LAN）／600ms（5G）。
- **使用套件**：Asterisk（自建映像）、ptt-gateway（骨架）、Keycloak。
- **層級**：Hub＋Node 各一份（Survivable）。
- **狀態**：**規劃**，需要 ptt-gateway 與 Asterisk 映像。

### 情境 D：產線設備與 AGV 資料接入（IoT/OT）
- **目標**：產線 PLC、環境感測、5G CPE 的狀態進同一個事件中心；異常時通知維修群組。
- **流程**：
  1. PLC（Modbus TCP）經 5G 工業閘道 → device-adapter 或 EdgeX Device Service → Mosquitto（`edge/<tenant>/<site>/telemetry/...`）；
  2. 視需要用 ThingsBoard 看板；
  3. 超出門檻的讀數成為事件，進 event engine；
  4. AGV 控制流量走低延遲切片（5QI-82／83），與資料上報分開。
- **使用套件**：Mosquitto、EdgeX、ThingsBoard（選配）、device-adapter（骨架）。
- **層級**：Gateway／Node。
- **狀態**：**可 demo**（Mosquitto＋EdgeX，已在 Lab 驗證）；自動事件化要等 event engine。

### 情境 E：現場知識助理（RAG）
- **目標**：巡檢、維修、醫護人員用 5G 平板問 SOP 與設備手冊，資料不出場域。
- **流程**：
  1. 手冊與 SOP 向量化存進 Qdrant；
  2. Open WebUI → LiteLLM（虛擬金鑰、配額、稽核）→ vLLM 回答，引用場域文件。
- **使用套件**：vLLM、LiteLLM、Open WebUI、Qdrant、Keycloak（登入）。
- **層級**：Hub（或 DGX Spark Node）。
- **狀態**：**部分**。套件可裝；vLLM 需要 GPU 環境另行驗證，Open WebUI 白牌前要確認授權。

### 情境 F：模型持續改進（MLOps Flywheel）
- **目標**：現場誤報 → 標註 → 重訓 → 依 GPU 世代建置 → 灰度下發 → 監控漂移。
- **流程**：
  1. Console 標記誤報 → 片段進 CVAT；
  2. 訓練結果記錄在 MLflow；
  3. model-release-controller 建 engine、驗 Gate、簽章、推 Harbor；
  4. 經 GitOps（Gitea＋Fleet／Argo）下發各站 Triton。
- **QoS**：模型與映像同步走 5QI-9（BE）、離峰、限速，不影響業務流量。
- **使用套件**：CVAT、MLflow、Harbor、Gitea、Argo CD 或 Fleet、SeaweedFS；model-release-controller（骨架）。
- **狀態**：**部分**。

### 情境 G：WAN 斷線的站點求生（Site Survival，F4）
- **目標**：站點對 Hub 的 WAN 斷線 72 小時，現場認證、DHCP、PTT、推論、錄影都不中斷。
- **做法**：Node 上常駐以下本地副本，恢復連線後再把租約、CDR、事件、認證日誌回補中央：
  - FreeRADIUS（用戶與憑證快取）；
  - Kea（本地續租）；
  - Asterisk（Survivable，本地分機與 PTT）；
  - Mosquitto；
  - MediaMTX（本地錄影緩衝）；
  - Triton。
- **5G 部分**：
  - 若 UPF 在站點（local breakout），5G 使用者面不受 WAN 影響；
  - 控制面在 Hub 時，要看 5GC 供應商是否支援站點備援（v2 R1／R7）。
- **狀態**：**部分**。套件可分別安裝在 Node；回補與同步屬自研工作。

### 情境 H：行動指揮車／臨時站點
- **目標**：防災或活動現場用一台 Gateway（Orin）＋5G CPE 快速開站，回連指揮中心。
- **做法**：
  - Headscale 讓車上節點以動態 IP 加入 Mesh；
  - step-ca 憑證完成裝置身分與 ZTP；
  - MediaMTX 匯流車上 Camera，以 SRT 回傳；
  - Mosquitto 上報狀態。
- **狀態**：**部分**（Headscale、MediaMTX、Mosquitto 可裝；ZTP 流程屬自研）。

### 情境 I：專網維運與資安
- **目標**：5GC、RAN、Edge 平台用同一套觀測與資安。
- **做法**：
  - 觀測：OTel／Prometheus → VictoriaMetrics、Logs → Grafana，KPI 與 SLO 告警；
  - 資安：Kyverno 只允許簽章映像；Trivy 每日掃描；External Secrets 從中央同步 Secret；
  - 稽核：edge-audit-service 的雜湊鏈稽核；Velero 每日備份。
- **狀態**：**可 demo**：Victoria 已在 Lab 驗證，其餘可在有 StorageClass 的 Lab 叢集安裝。

---

## 5. 建議部署組合與安裝順序

### 5.1 依層級的建議組合

| 層級 | 必裝 | 依場景加裝 |
|---|---|---|
| Hub | CloudNativePG、Valkey、SeaweedFS、Keycloak、step-ca、Harbor、Gitea、Mosquitto、FreeRADIUS、Kea、VictoriaMetrics＋Logs、Grafana、OTel、Kyverno、Trivy、External Secrets、Velero | vLLM、LiteLLM、Open WebUI、Qdrant、MLflow、CVAT、Asterisk、Headscale、Argo CD |
| Node（Thor／Spark） | MediaMTX、Triton、Mosquitto、OTel、Kyverno | FreeRADIUS／Kea／Asterisk（Survival 副本）、vLLM（VLM 覆核）、EdgeX、vlm-app |
| Gateway（Orin） | Mosquitto、OTel | MediaMTX（少量 Camera）、EdgeX、device-adapter |

### 5.2 安裝順序（相依關係）
1. **底座**：
   - CloudNativePG → 建資料庫 Cluster；
   - Valkey、SeaweedFS；
   - step-ca。
2. **身分**：Keycloak（要用到資料庫）。
3. **倉庫與 GitOps**：Harbor、Gitea（Argo CD 選配）。
4. **觀測與資安**：OTel、Victoria／Grafana、Kyverno、Trivy、External Secrets、Velero。
5. **網路接入**：FreeRADIUS、Kea、Headscale、Mosquitto。
6. **應用**：
   - Vision：MediaMTX → Triton → vLLM；
   - Voice：Asterisk；
   - IoT：EdgeX、ThingsBoard；
   - RAG：Qdrant → vLLM → LiteLLM → Open WebUI；
   - MLOps：MLflow、CVAT。
7. **自研模組**：等映像就緒後，依 sim-aaa／policy → event engine → ptt-gateway → ai-workflow → catalog／operator → portal → audit 的順序。

### 5.3 安裝步驟（每個套件相同）
1. Rancher → 目標叢集 → Apps → Charts，搜尋 `edge-ai` 或依 Pack 側標找到套件。
2. 先依 chart README 的「安裝前」建立需要的 Secret（附錄 6.1）。
3. Install → 確認 namespace（預設 `edgeai-<pack>`）→ 填表單 → 進階參數用 Edit YAML → Install。
4. 看 NOTES 列出的 Service 與埠，按「基本使用」驗證。
5. 升級：Apps → Installed Apps → Upgrade 選新版本。
6. 移除：Delete。PVC 預設保留，要手動刪除。

---

## 6. 附錄

### 6.1 安裝前要建立的 Secret

| 套件 | Secret 內容（鍵名） | 表單欄位 |
|---|---|---|
| FreeRADIUS | `clients.conf` | NAS clients Secret 名稱 |
| Mosquitto | `passwd`（mosquitto_passwd 雜湊檔） | 帳密檔 Secret |
| EdgeX | `password` | 資料庫密碼 Secret |
| Keycloak | 管理者：`username`、`password`；資料庫：`password` | 管理者 Secret、資料庫密碼 Secret |
| Harbor | `HARBOR_ADMIN_PASSWORD` | 管理者密碼 Secret |
| Gitea | `username`、`password` | 管理者 Secret |
| MinIO | `rootUser`、`rootPassword` | Root 帳密 Secret |
| LiteLLM | `masterkey` | Master key Secret |
| Grafana | `admin-user`、`admin-password`（選填） | 管理者 Secret |
| Asterisk | `pjsip.conf`、`ari.conf` | PJSIP／ARI 設定 Secret |
| Velero | `cloud`（AWS credentials 格式） | S3 憑證 Secret |
| 自研骨架 | 以環境變數帶入（如 `DB_PASSWORD`、`UDM_TOKEN`、`ARI_PASSWORD`） | 秘密 Secret（空白則讀 `<release>-<chart>-secrets`） |

範例（值自行產生，不要寫進任何檔案或 repo）：
```bash
kubectl -n edgeai-platform create secret generic harbor-admin --from-literal=HARBOR_ADMIN_PASSWORD='<自行產生>'
```

### 6.2 端到端 QoS 對照（v2 §3.3.1）

| 業務 | 5G 5QI | DSCP | Wi-Fi WMM | 802.1p | 相關套件 |
|---|:-:|:-:|:-:|:-:|---|
| PTT／語音 | 5QI-1 | EF (46) | AC_VO | 5 | Asterisk、ptt-gateway |
| 視訊回傳（Camera 上行） | 5QI-7 | AF41 (34) | AC_VI | 4 | MediaMTX |
| AGV／Robot 控制 | 5QI-82/83 | CS5 (40) | AC_VI | 5 | EdgeX core-command、device-adapter |
| 告警／MQTT 事件 | 5QI-8 | AF31 (26) | AC_BE | 3 | Mosquitto、event engine |
| GitOps／映像／模型同步 | 5QI-9 | BE (0) | AC_BE | 0 | Harbor、Gitea、model-release |

### 6.3 授權速查（商用打包）
- **AGPL-3.0**：Grafana、Loki、MinIO。不修改、保留 source offer；MinIO 建議以 SeaweedFS 取代。
- **GPL-2.0**：FreeRADIUS、Asterisk。獨立部署、不修改；Asterisk 映像自建時附原始碼取得方式，或購買商業授權。
- **自訂授權**：Open WebUI（品牌條款）。
- **NVIDIA EULA**：Triton 映像。不重新打包。
- **其餘**：Apache-2.0、MIT、BSD、EPL、MPL。自研模組為專有。

### 6.4 名詞
- **UPF local breakout**：使用者面流量在場域 UPF 直接分流到場域網路（DNN），不回中央。
- **DNN**：5G 的資料網路名稱，相當於 4G 的 APN，決定終端接到哪個網段與政策。
- **5QI**：5G QoS 等級識別碼。
- **AV（Authentication Vector）**：UDM 產生的一次性認證資料（RAND／AUTN／XRES／CK／IK）。
- **CoA**：RADIUS Change-of-Authorization，政策改變時要求 AP／Switch 立即套用。
- **Site Survival**：WAN 斷線時站點自治運作的模式。
- **骨架 chart**：已定義部署結構與參數，但程式與映像尚未完成的 chart。

### 6.5 待確認事項
1. 情境 A：獨立的 EAP-AKA PoC 是否與 `edgeai-freeradius`／sim-aaa-adapter 整合（介面 C1）。
2. Harmony UDM 的 AV API 契約與速率（文件 R12）。
3. 5GC 控制面在 Hub 時的站點備援能力（v2 R1／R7）。
4. Triton、vLLM、Qdrant、Harbor 等需要 GPU 或 PVC 的套件，要在有 StorageClass 的 Lab 叢集做第二輪實裝。
5. Asterisk 自建映像的來源與建置流程。
6. 自研模組的 API group 正式名稱（目前暫用 `*.edgeai.internal`）。
7. 截圖：Rancher Apps 頁與各套件畫面待 Lab 擷取。
