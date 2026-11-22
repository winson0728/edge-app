# edgeai-thingsboard（ThingsBoard CE（選配））

ThingsBoard CE 單機版（內建 PostgreSQL 的 tb-postgres 映像，IoT 儀表板）

- Pack：IoT/OT（預設 namespace `edgeai-iot`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://thingsboard.io
- 授權：Apache-2.0；商用打包風險 **低**。注意 ThingsBoard 商標與 PE 版功能界線。
- chart 類型：自寫 chart（tools/edgeai/common 樣板）

## 平台預設值
```yaml
nameOverride: ''
fullnameOverride: ''
imagePullSecrets: []
podSecurityContext:
  fsGroup: 799
nodeSelector:
  kubernetes.io/os: linux
tolerations: []
affinity: {}
networkPolicy:
  enabled: true
  allowedPorts:
  - port: 9090
  - port: 1883
  - port: 7070
  - port: 5683
    protocol: UDP
  allowFrom: []
ingress:
  enabled: false
  className: ''
  host: ''
  tlsSecret: ''
  annotations: {}
  component: thingsboard
  servicePort: http
components:
  thingsboard:
    enabled: true
    kind: StatefulSet
    image:
      repository: docker.io/thingsboard/tb-postgres
      tag: 4.2.1
      pullPolicy: IfNotPresent
    env:
    - name: TB_QUEUE_TYPE
      value: in-memory
    ports:
    - name: http
      containerPort: 9090
    - name: mqtt
      containerPort: 1883
    - name: edge-rpc
      containerPort: 7070
    - name: coap
      containerPort: 5683
      protocol: UDP
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 9090
      - name: mqtt
        port: 1883
      - name: edge-rpc
        port: 7070
      - name: coap
        port: 5683
        protocol: UDP
    startupProbe:
      tcpSocket:
        port: http
      periodSeconds: 10
      failureThreshold: 60
    readinessProbe:
      tcpSocket:
        port: http
      periodSeconds: 10
    persistence:
      enabled: true
      mountPath: /data
      size: 10Gi
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        memory: 3Gi
```

## 說明
- 首次登入用 ThingsBoard 預設系統帳號（見官方文件），**登入後立刻改密碼**；本 chart 不帶任何帳密。
- 文件把 ThingsBoard 列為選配（EdgeX 為主），多節點／外部 PostgreSQL 請改用官方 K8s manifest。

## 驗證
```bash
helm lint . 
helm template t . 
```
