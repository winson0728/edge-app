# edgeai-device-adapter（device-adapter（範本））

device-adapter-sdk 產出的設備接入範本（Connector → MQTT 標準 telemetry；可選 EdgeX Device Service 出口）

- Pack：IoT/OT（預設 namespace `edgeai-iot`）
- 層級：Node、Gateway
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
  - port: 9090
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
adapter:
  protocol: modbus-tcp
  target: 192.0.2.10:502
  pollIntervalSeconds: 5
  mqttUrl: mqtt://edgeai-mosquitto-mosquitto.edgeai-iot.svc:1883
  topicPrefix: edge/default/site-a/telemetry
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
          connector:
            protocol: {{ .Values.adapter.protocol }}
            target: {{ .Values.adapter.target | quote }}
            pollIntervalSeconds: {{ .Values.adapter.pollIntervalSeconds }}
          output:
            mqtt: {{ .Values.adapter.mqttUrl | quote }}
            topicPrefix: {{ .Values.adapter.topicPrefix | quote }}
```

## 說明
每種設備一個 release（例如 `plc-line1`、`cpe-vendor-x`）。之後 SDK 會直接產出 app-pack，本 chart 是其中 `chart/` 的範本。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
