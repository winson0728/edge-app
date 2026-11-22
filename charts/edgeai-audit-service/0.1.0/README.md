# edgeai-audit-service（edge-audit-service）

稽核服務（append-only 雜湊鏈、每日 anchor、四維查詢、簽章匯出、保留政策）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub
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
audit:
  databaseHost: pg-rw.edgeai-platform.svc
  anchorS3Url: http://edgeai-seaweedfs-s3.edgeai-platform.svc:8333/audit-anchors
  retentionDays: 365
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
          store:
            database: {{ .Values.audit.databaseHost | quote }}   # 帳密走 Secret：DB_USER／DB_PASSWORD
          anchor:
            s3: {{ .Values.audit.anchorS3Url | quote }}           # 憑證走 Secret：S3_ACCESS_KEY／S3_SECRET_KEY
            schedule: daily
          retentionDays: {{ .Values.audit.retentionDays }}
          spool: /var/spool/edgeai-audit
    persistence:
      enabled: true
      mountPath: /var/spool/edgeai-audit
      size: 5Gi
```

## 說明
介面：C11 所有模組經 telemetry-client 非同步送入（MQTT／HTTP），稽核不可阻塞主流程；本地 spool 斷線緩衝。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
