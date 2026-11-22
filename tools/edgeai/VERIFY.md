# Edge AI 開源 chart 驗證紀錄

## 1. helm lint／template（2026-11-22，helm v3.19.0）
`bash tools/edgeai/check.sh`：32 個 `edgeai-*` chart **全部 lint PASS、template PASS**（有 `ci/test-values.yaml` 的帶入測試值，只含 Secret 名稱）。
另外確認：
- 沒給必填 Secret 時，Harbor、Gitea、Keycloak、MinIO、LiteLLM、FreeRADIUS、Mosquitto、EdgeX 會在 template 階段就拒絕（避免落到上游預設密碼）。
- 表單（questions.yaml）每個變數都對得到 values 或上游 chart 的參數（Headscale storageClass、Triton existingClaim、Qdrant storageClassName／apiKey 是樣板或上游 template 支援的選填參數）。

## 2. Lab 127 實裝（k3s v1.33.5 單節點、Rancher 2.14.3；只在 Lab）
做法：每個 chart 獨立 namespace `edgeai-verify-<name>`，不要求 GPU、不建 PV，Ready 後做功能測試，然後 `helm uninstall` 並刪 namespace。測試用密碼都是當下隨機產生，沒有印出或存檔。

| Chart | 類型 | 結果 | 功能測試 |
|---|---|---|---|
| edgeai-mosquitto | 自寫 | ✅ 10 秒 Ready | 帳密登入 pub/sub 收到訊息；錯誤密碼與匿名都被拒（not authorised） |
| edgeai-freeradius | 自寫 | ✅ 10 秒 Ready | 正確共用密鑰的 Access-Request 收到 Access-Reject（伺服器正常回應、使用者不存在）；錯誤密鑰被丟棄（log：Shared secret is incorrect） |
| edgeai-mediamtx | 自寫 | ✅ 10 秒 Ready | ffmpeg 以 RTSP 推流，ffprobe 讀回 h264 320×240；API／metrics 被 NetworkPolicy 擋在 release 外（設計如此） |
| edgeai-edgex | 自寫（7 元件＋bootstrap Job） | ✅ 15 秒 Ready | core-metadata／data／command ping 回應、UI 200、deviceprofile API 回 200 |
| edgeai-valkey | wrapper | ✅ 20 秒 Ready | SET／GET 成功，valkey 9.1.3 |
| edgeai-victoria | wrapper（2 個上游） | ✅ 30 秒 Ready | VictoriaMetrics、VictoriaLogs `/health` 皆 200 |

驗證中修正的問題（已改進 chart）：
- FreeRADIUS：官方映像設定目錄是 `/etc/freeradius`；預設 site 聽 IPv6 `::` 在 Pod 網路會失敗 → 改提供只聽 IPv4 的 default site。
- MediaMTX：補 RTP／RTCP UDP 8000／8001（UDP 傳輸的攝影機需要）。
- EdgeX：服務會綁 `SERVICE_HOST`（在 K8s 解析成 Service IP）→ 加 `SERVICE_SERVERBINDADDR=0.0.0.0`；DB 密碼要經 bootstrapper 的 `ALL_SERVICES_*` 下發；core-data／command 加等待 metadata 的 initContainer；core 服務加 `/api/v3/ping` readiness／liveness。

## 3. Rancher 讀取（127 `local` 叢集）
不推 GitHub 的前提下，暫時在 127 起一個只服務打包檔的 HTTP（`tools/edgeai/package-index.sh` 產生的 index.yaml），
建臨時 ClusterRepo `edgeai-verify-http` → `Downloaded=True`，Rancher 索引列出 **36 個 chart**（32 個 `edgeai-*`＋既有 4 個），
display-name、Pack 側標（certified）、預設 namespace 都正確；vlm-app 0.1.1 原樣在列。驗證後已刪 ClusterRepo、停 HTTP、刪暫存目錄。
Git 型 `edge-app` 套件庫要在推到 `main` 後 Refresh 才會出現新 chart。

## 4. 還原確認
127 驗證後：沒有 `edgeai*` namespace、ClusterRepo 剩原本 4 個、helm release 17 個（與驗證前相同）、pod 狀態與驗證前相同（31 Running、4 Completed、1 個原本就有的 Init）。

## 5. 未實裝（只 lint／template）
- 需要 GPU：Triton、vLLM（127 的 2 顆 GPU 已被既有服務配發）。
- 需要 PVC：127 沒有 StorageClass（Qdrant、Harbor、Gitea、Headscale、ThingsBoard、CVAT 等預設會建 PVC）。
- 叢集層級 operator／webhook，可能影響既有服務：CloudNativePG、Kyverno、Trivy Operator、External Secrets、Velero、Argo CD。
- hostNetwork 會占用節點埠：Kea DHCP、Asterisk（Asterisk 另需自建映像）。
- 需要外部資料庫或 Secret 的整合件：Keycloak、LiteLLM、MLflow、Open WebUI、step-ca、Loki、Grafana、MinIO、SeaweedFS、OTel Collector。
建議在有 StorageClass 的 Lab 叢集（或 127 裝 local-path 後）再做第二輪。

## 6. 第二輪：Layer 2 自研模組骨架（11 個）
- `check.sh`：11 個全部 lint PASS、template PASS；沒填映像位置時 template 階段即拒絕。
- 127 server 端驗證（不建立任何物件）：11 個 `helm install --dry-run=server` 全部 PASS（5～7 個物件），
  3 個 CRD `kubectl apply --dry-run=server` 通過；驗證後 127 沒有 `*.edgeai.internal` CRD、helm release 仍 17 個、暫存目錄已刪。
- 沒有實裝：模組尚無映像。
- 共用樣板 `tools/edgeai/common` 這輪加了 ServiceAccount 支援（沒設定 `serviceAccount` 時輸出不變）；第一輪 9 個自寫 chart 沒有重產，下次重產時要一併升版。
