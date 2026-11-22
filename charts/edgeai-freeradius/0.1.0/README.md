# edgeai-freeradius（FreeRADIUS）

FreeRADIUS 3.2 RADIUS server（Wi-Fi／有線 802.1X、EAP-AKA′／EAP-TLS／MAB）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub、Node（Site Survival 副本）
- 架構：amd64, arm64
- 上游專案：https://freeradius.org
- 授權：GPL-2.0；商用打包風險 **中**。不修改原始碼、以獨立容器部署（非衍生作品）；修改需開源。
- chart 類型：自寫 chart（tools/edgeai/common 樣板）

## 平台預設值
```yaml
nameOverride: ''
fullnameOverride: ''
imagePullSecrets: []
podSecurityContext: {}
nodeSelector:
  kubernetes.io/os: linux
tolerations: []
affinity: {}
networkPolicy:
  enabled: true
  allowedPorts:
  - port: 1812
    protocol: UDP
  - port: 1813
    protocol: UDP
  allowFrom: []
ingress:
  enabled: false
  className: ''
  host: ''
  tlsSecret: ''
  annotations: {}
  component: ''
  servicePort: ''
clients:
  existingSecret: ''
components:
  freeradius:
    enabled: true
    image:
      repository: docker.io/freeradius/freeradius-server
      tag: 3.2.10
      pullPolicy: IfNotPresent
    args:
    - -f
    - -l
    - stdout
    ports:
    - name: auth
      containerPort: 1812
      protocol: UDP
    - name: acct
      containerPort: 1813
      protocol: UDP
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: auth
        port: 1812
        protocol: UDP
      - name: acct
        port: 1813
        protocol: UDP
    secretMounts:
    - secretName: '{{ .Values.clients.existingSecret }}'
      mountPath: /etc/freeradius/clients.conf
      subPath: clients.conf
    config:
      mountPath: /etc/freeradius/sites-enabled
      files:
        default: |
          # 平台預設 site：只聽 IPv4（多數 K8s Pod 網路沒有 IPv6）。EAP-AKA′／sim-aaa-adapter 掛點之後在此擴充。
          server default {
          listen {
            type = auth
            ipaddr = *
            port = 0
          }
          listen {
            type = acct
            ipaddr = *
            port = 0
          }
          authorize {
            filter_username
            preprocess
            chap
            mschap
            suffix
            eap {
              ok = return
            }
            files
            expiration
            logintime
            pap
          }
          authenticate {
            Auth-Type PAP {
              pap
            }
            Auth-Type CHAP {
              chap
            }
            Auth-Type MS-CHAP {
              mschap
            }
            mschap
            eap
          }
          preacct {
            preprocess
            acct_unique
            suffix
            files
          }
          accounting {
            detail
            attr_filter.accounting_response
          }
          session {
          }
          post-auth {
            update {
              &reply: += &session-state:
            }
            remove_reply_message_if_eap
            Post-Auth-Type REJECT {
              attr_filter.access_reject
              eap
              remove_reply_message_if_eap
            }
          }
          pre-proxy {
          }
          post-proxy {
            eap
          }
          }
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        memory: 256Mi
```

## 說明
## 安裝前
建立 NAS 共用密鑰（不要寫進 values）：
```bash
kubectl -n edgeai-access create secret generic freeradius-clients --from-file=clients.conf=./clients.conf
```
`clients.conf` 範例（密鑰自己產生）：
```
client ap-floor1 { ipaddr = 192.0.2.0/24  secret = <自行產生> }
```
官方映像的設定目錄是 `/etc/freeradius`。`default` site 由 `components.freeradius.config` 提供（只聽 IPv4）；EAP 等其他設定可再加 ConfigMap／Secret 覆蓋或額外 Secret 覆蓋，sim-aaa-adapter 掛點（rlm_python3）待自研模組完成後補。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
