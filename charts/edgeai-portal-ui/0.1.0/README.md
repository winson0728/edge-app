# edgeai-portal-ui（edge-portal-ui（EdgeOne Console））

EdgeOne Console（React UI＋Go BFF；聚合各模組 Admin API、Keycloak OIDC、嵌入 Grafana）

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
  component: ui
  servicePort: http
existingSecret: ''
serviceAccount:
  create: true
  name: ''
rbac:
  create: false
  clusterWide: false
  rules: []
portal:
  oidcIssuer: https://keycloak.example.com/realms/edge-ai
  oidcClientId: edge-portal
  grafanaUrl: http://edgeai-grafana.edgeai-observability.svc
components:
  ui:
    enabled: true
    replicas: 1
    image: &id001
      repository: ''
      tag: ''
      pullPolicy: IfNotPresent
    env: &id002
    - name: EDGEAI_CONFIG
      value: /etc/edgeai/config.yaml
    envFrom: []
    ports:
    - name: http
      containerPort: 8080
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 8080
    livenessProbe:
      httpGet:
        path: /
        port: http
      periodSeconds: 20
    readinessProbe:
      httpGet:
        path: /
        port: http
      periodSeconds: 10
    securityContext: &id003
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources: &id004
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        memory: 256Mi
    config: null
  bff:
    enabled: true
    replicas: 1
    image: *id001
    env: *id002
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
    securityContext: *id003
    resources: *id004
    config:
      mountPath: /etc/edgeai
      files:
        config.yaml: |
          oidc:
            issuer: {{ .Values.portal.oidcIssuer | quote }}
            clientId: {{ .Values.portal.oidcClientId | quote }}   # client secret 走 Secret：OIDC_CLIENT_SECRET
          grafana: {{ .Values.portal.grafanaUrl | quote }}
          upstreams:
            accessPolicy: http://edgeai-access-policy-service-app.edgeai-access.svc:8080
            simAaa: http://edgeai-sim-aaa-adapter-app.edgeai-access.svc:8080
            catalog: http://edgeai-app-catalog-controller-app.edgeai-platform.svc:8080
            events: http://edgeai-unified-event-engine-app.edgeai-platform.svc:8080
            ptt: http://edgeai-ptt-gateway-app.edgeai-voice.svc:8080
            audit: http://edgeai-audit-service-app.edgeai-platform.svc:8080
```

## 說明
UI 只是殼：每頁只消費既有模組的 Admin API（文件 §3.9、R18）。BFF 的 upstreams 預設指向各骨架 chart 用預設 release 名稱安裝後的 Service。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
