# edgeai-ptt-gateway（ptt-gateway）

企業 PTT 控制層（群組、floor control、優先權／緊急搶占、事件臨時群組；媒體面交給 Asterisk ARI）

- Pack：Voice/PTT（預設 namespace `edgeai-voice`）
- 層級：Hub、Node（Survivable）
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
  - port: 8081
  allowFrom: []
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
ptt:
  ariUrl: http://asterisk.edgeai-voice.svc:8088/ari
  speakerTimeoutSeconds: 30
components:
  app:
    enabled: true
    replicas: 1
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
    - name: ws
      containerPort: 8081
    - name: metrics
      containerPort: 9090
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 8080
      - name: ws
        port: 8081
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
          asterisk:
            ariUrl: {{ .Values.ptt.ariUrl | quote }}   # ARI 帳密走 Secret：ARI_USER／ARI_PASSWORD
          floor:
            speakerTimeoutSeconds: {{ .Values.ptt.speakerTimeoutSeconds }}
            priorities: 4
```

## 說明
floor control 走 WebSocket（8081）；edgeai-asterisk 用 hostNetwork，`ptt.ariUrl` 請填節點位址或另建指向節點的 Service。單一 replica（群組狀態機在記憶體），HA 待設計。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
