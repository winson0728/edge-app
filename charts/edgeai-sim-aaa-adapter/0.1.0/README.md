# edgeai-sim-aaa-adapter（sim-aaa-adapter）

Wi-Fi EAP-AKA／AKA′ 與 Harmony UDM／AUSF 介接（只做認證：AV 取得、SQN resync、pseudonym／fast re-auth）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub（＋Node Survival 副本）
- 架構：amd64, arm64
- 上游專案：https://github.com/winson0728/edge-app
- 授權：自研（專有）；商用打包風險 **低**
- chart 類型：**骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數）

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
  - port: 8080
  allowFrom:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: edgeai-access
    podSelector:
      matchLabels:
        app.kubernetes.io/name: edgeai-freeradius
ingress:
  enabled: false
  className: ''
  host: ''
  tlsSecret: ''
  annotations: {}
  component: ''
  servicePort: ''
existingSecret: ''
serviceAccount:
  create: true
  name: ''
rbac:
  create: false
  clusterWide: false
  rules: []
adapter:
  anid: WLAN
  mcc: '001'
  mnc: '01'
  avPrefetch: 5
  udmUrl: https://udm.example.internal
  redisUrl: redis://edgeai-valkey.edgeai-platform.svc:6379
  requestTimeoutMs: 1000
components:
  app:
    enabled: true
    replicas: 2
    image:
      repository: ''
      tag: ''
      pullPolicy: IfNotPresent
    env:
    - name: EDGEAI_CONFIG
      value: /etc/edgeai/config.yaml
    envFrom:
    - secretRef:
        name: '{{ .Values.existingSecret | default (printf "%s-secrets" (include "eai.fullname" .)) }}'
        optional: true
    ports:
    - name: http
      containerPort: 8080
    - name: metrics
      containerPort: 9090
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 8080
      - name: metrics
        port: 9090
    livenessProbe:
      httpGet:
        path: /healthz
        port: http
      initialDelaySeconds: 10
      periodSeconds: 20
    readinessProbe:
      httpGet:
        path: /readyz
        port: http
      periodSeconds: 10
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        memory: 256Mi
    config:
      mountPath: /etc/edgeai
      files:
        config.yaml: |
          # sim-aaa-adapter 設定（金鑰材料不在這裡：Ki/OPc 永不經手；UDM 憑證與 token 走 Secret）
          eapAka:
            anid: {{ .Values.adapter.anid | quote }}
            realm: "wlan.mnc{{ printf "%03s" .Values.adapter.mnc }}.mcc{{ .Values.adapter.mcc }}.3gppnetwork.org"
            avPrefetch: {{ .Values.adapter.avPrefetch }}
          udm:
            url: {{ .Values.adapter.udmUrl | quote }}
            timeoutMs: {{ .Values.adapter.requestTimeoutMs }}
          cache:
            redisUrl: {{ .Values.adapter.redisUrl | quote }}
```

## 說明
介面：C1 `POST /v1/auth/vectors`、`/v1/auth/resync`、`/v1/auth/result`（FreeRADIUS rlm_python3 呼叫，逾時 1s）。
NetworkPolicy 只放行 `edgeai-access` namespace 內的 FreeRADIUS。Secret 建議鍵：`UDM_TOKEN`、`REDIS_PASSWORD`；UDM mTLS 憑證另以 Secret 掛載（待實作）。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
