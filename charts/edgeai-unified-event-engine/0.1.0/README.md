# edgeai-unified-event-engine（unified-event-engine）

AI／IoT／PTT／網路事件編排（CloudEvents 驗證、去重、關聯、CEL 規則、動作派送、升級鏈、Incident Timeline）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub、Node
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
events:
  mqttUrl: mqtt://edgeai-mosquitto-mosquitto.edgeai-iot.svc:1883
  redisUrl: redis://edgeai-valkey.edgeai-platform.svc:6379
  databaseHost: pg-rw.edgeai-platform.svc
  pttGatewayUrl: http://edgeai-ptt-gateway-app.edgeai-voice.svc:8080
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
          ingest:
            mqtt: {{ .Values.events.mqttUrl | quote }}
            topics: ["edge/+/+/events/#"]
            dlqTopic: edge/_dlq
          state:
            redis: {{ .Values.events.redisUrl | quote }}
            database: {{ .Values.events.databaseHost | quote }}
          actions:
            pttGateway: {{ .Values.events.pttGatewayUrl | quote }}
          rulesDir: /etc/edgeai
        rules.yaml: |
          # 規則範例（宣告式 YAML＋CEL）；正式規則以 GitOps 下發
          - name: restricted-zone-intrusion
            when: "event.type == 'restricted_zone_intrusion' && event.data.severity >= 3"
            actions:
              - {type: ptt-broadcast, group: security, tts: "倉庫 A 禁區有人員進入"}
            escalation:
              - {afterMinutes: 5, action: {type: webhook, target: duty-manager}}
```

## 說明
介面：C5 MQTT／HTTP（CloudEvents，schema 失敗進 DLQ）、C6 `POST /v1/broadcast` 到 ptt-gateway。規則檔在 `components.app.config.files.rules.yaml`。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
