# Chart 圖示（Rancher Apps 卡片用）

每個 chart 的 `Chart.yaml` 以 `icon: file://assets/logos/<chart>.<ext>` 指到這裡，路徑相對 repo 根目錄，Rancher 從套件庫直接讀取，不需要對外連線。
`tools/edgeai/build.py` 產生 `edgeai-*` chart 時，若這裡有同名的 `.svg`／`.png` 會自動寫入 `icon:`。新增 chart 時請一併放圖。

檢查：`python3 tools/check_icons.py .`（repo 根目錄執行）會逐一確認每個 chart 都有 `icon:`、路徑在 `assets/logos/`、檔案存在且 SVG／PNG 格式正確，並列出沒被用到的圖檔；有錯誤時 exit 1。測試：`cd tools && python3 -m unittest test_check_icons`。

## 開源專案：使用官方 logo

商標與 logo 版權屬各專案／公司所有，這裡只用來在套件目錄標示對應軟體。

| Chart | 檔案 | 來源 |
|---|---|---|
| `edgeai-argo-cd` | `edgeai-argo-cd.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/argo/icon/color/argo-icon-color.svg |
| `edgeai-asterisk` | `edgeai-asterisk.svg` | https://commons.wikimedia.org/wiki/File:Asterisk_logo.svg |
| `edgeai-cloudnative-pg` | `edgeai-cloudnative-pg.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/cloudnativepg/icon/color/cloudnativepg-icon-color.svg |
| `edgeai-cvat` | `edgeai-cvat.png` | GitHub 組織 cvat-ai 頭像（https://github.com/cvat-ai） |
| `edgeai-edgex` | `edgeai-edgex.svg` | https://raw.githubusercontent.com/lf-edge/artwork/master/edgexfoundry/icon/color/edgexfoundry-icon-color.svg |
| `edgeai-external-secrets` | `edgeai-external-secrets.svg` | https://raw.githubusercontent.com/external-secrets/external-secrets/main/assets/eso-round-logo.svg |
| `edgeai-freeradius` | `edgeai-freeradius.png` | https://freeradius.org/favicon-194x194.png |
| `edgeai-gitea` | `edgeai-gitea.svg` | https://raw.githubusercontent.com/go-gitea/gitea/main/public/assets/img/logo.svg |
| `edgeai-grafana` | `edgeai-grafana.svg` | https://raw.githubusercontent.com/grafana/grafana/main/public/img/grafana_icon.svg |
| `edgeai-harbor` | `edgeai-harbor.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/harbor/icon/color/harbor-icon-color.svg |
| `edgeai-headscale` | `edgeai-headscale.svg` | https://raw.githubusercontent.com/juanfont/headscale/main/docs/assets/logo/headscale3-dots.svg |
| `edgeai-kea-dhcp` | `edgeai-kea-dhcp.png` | https://raw.githubusercontent.com/isc-projects/kea/master/doc/images/kea-logo-100x70.png |
| `edgeai-keycloak` | `edgeai-keycloak.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/keycloak/icon/color/keycloak-icon-color.svg |
| `edgeai-kyverno` | `edgeai-kyverno.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/kyverno/icon/color/kyverno-icon-color.svg |
| `edgeai-litellm` | `edgeai-litellm.png` | https://raw.githubusercontent.com/BerriAI/litellm/main/litellm/proxy/logo_monogram.png |
| `edgeai-loki` | `edgeai-loki.png` | https://raw.githubusercontent.com/grafana/loki/main/docs/sources/logo.png |
| `edgeai-mediamtx` | `edgeai-mediamtx.png` | https://raw.githubusercontent.com/bluenviron/mediamtx/main/logo.png |
| `edgeai-minio` | `edgeai-minio.svg` | https://raw.githubusercontent.com/minio/minio/master/.github/logo.svg |
| `edgeai-mlflow` | `edgeai-mlflow.svg` | https://raw.githubusercontent.com/mlflow/mlflow/master/assets/icon.svg |
| `edgeai-mosquitto` | `edgeai-mosquitto.svg` | https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/master/logo/mosquitto-logo-only.svg |
| `edgeai-open-webui` | `edgeai-open-webui.png` | https://raw.githubusercontent.com/open-webui/open-webui/main/static/favicon.png |
| `edgeai-otel-collector` | `edgeai-otel-collector.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/opentelemetry/icon/color/opentelemetry-icon-color.svg |
| `edgeai-qdrant` | `edgeai-qdrant.svg` | https://raw.githubusercontent.com/qdrant/qdrant/master/docs/logo.svg |
| `edgeai-seaweedfs` | `edgeai-seaweedfs.png` | https://raw.githubusercontent.com/seaweedfs/seaweedfs/master/note/seaweedfs.png |
| `edgeai-step-ca` | `edgeai-step-ca.png` | https://raw.githubusercontent.com/smallstep/certificates/master/icon.png |
| `edgeai-thingsboard` | `edgeai-thingsboard.png` | https://raw.githubusercontent.com/thingsboard/thingsboard/master/img/logo.png |
| `edgeai-triton` | `edgeai-triton.svg` | NVIDIA 標誌（simple-icons nvidia.svg，加 NVIDIA 綠 #76B900）；Triton 本身沒有獨立 logo |
| `edgeai-trivy-operator` | `edgeai-trivy-operator.png` | https://raw.githubusercontent.com/aquasecurity/trivy/main/docs/imgs/logo.png |
| `edgeai-valkey` | `edgeai-valkey.png` | https://raw.githubusercontent.com/valkey-io/valkey-io.github.io/main/static/img/favicon/apple-touch-icon-144x144.png |
| `edgeai-velero` | `edgeai-velero.svg` | https://raw.githubusercontent.com/vmware-tanzu/velero/main/assets/stacked/199150-vmw-os-lgo-velero-final_stacked-gry.svg |
| `edgeai-victoria` | `edgeai-victoria.png` | GitHub 組織 VictoriaMetrics 頭像（上游 chart 的 icon 也用這張） |
| `edgeai-vllm` | `edgeai-vllm.png` | https://raw.githubusercontent.com/vllm-project/vllm/main/docs/assets/logos/vllm-logo-only-light.png |
| `srs` | `srs.png` | https://raw.githubusercontent.com/ossrs/srs/develop/trunk/doc/srs-logo.png |
| `zerotier-planet` | `zerotier-planet.svg` | ZeroTier 標誌（simple-icons zerotier.svg，加品牌色 #FFB441） |

## 自研模組：自製 logo（2026-11-23）

沒有既有 logo，以同一套樣式製作：128×128 圓角方塊、依 Pack 上色的漸層底、白色線條圖示。產生程式見 `tools/edgeai/gen_icons.py`。

| Pack 顏色 | Chart |
|---|---|
| Access & NAC（青綠） | `edgeai-access-policy-service`（盾牌＋勾）、`edgeai-sim-aaa-adapter`（SIM 卡） |
| Platform（藍） | `edgeai-app-catalog-controller`（應用方塊＋加號）、`edgeai-app-lifecycle-operator`（循環箭頭）、`edgeai-unified-event-engine`（事件閃電＋節點）、`edgeai-portal-ui`（主控台視窗） |
| Platform 稽核（灰） | `edgeai-audit-service`（文件＋雜湊鏈） |
| Vision（紫） | `edgeai-ai-workflow-controller`（偵測→覆核流程）、`vlm-app`（監視攝影機＋AI） |
| Voice/PTT（橘） | `edgeai-ptt-gateway`（對講機） |
| MLOps（琥珀） | `edgeai-model-release-controller`（模型方塊＋上架箭頭） |
| IoT/OT（綠） | `edgeai-device-adapter`（晶片接腳） |
| 網路（天藍） | `doublinks`（雙鏈結） |
