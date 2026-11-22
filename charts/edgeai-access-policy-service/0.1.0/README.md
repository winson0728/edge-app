# edgeai-access-policy-service（access-policy-service）

統一 5G／Wi-Fi／有線授權政策（PDP、session registry、CoA、Policy Bundle、下游 MQTT ACL／Keycloak／5GC 同步）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub（＋Node 決策快取）
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
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: edgeai-platform
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
policy:
  failMode: close
  quarantineVlan: '999'
  databaseHost: pg-rw.edgeai-platform.svc
  mosquittoDynsecUrl: mqtt://edgeai-mosquitto-mosquitto.edgeai-iot.svc:1883
  keycloakUrl: http://edgeai-keycloak-http.edgeai-access.svc
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
          decision:
            failMode: {{ .Values.policy.failMode }}        # close＝不可達時 FreeRADIUS 丟隔離 VLAN
            quarantineVlan: {{ .Values.policy.quarantineVlan | quote }}
          database:
            host: {{ .Values.policy.databaseHost | quote }}  # 帳密走 Secret：DB_USER／DB_PASSWORD
          downstream:
            mosquittoDynsec: {{ .Values.policy.mosquittoDynsecUrl | quote }}
            keycloak: {{ .Values.policy.keycloakUrl | quote }}
          coa:
            port: 3799
```

## 說明
介面：C2 `POST /v1/decision`（P95 ≤ 50ms）、C3 CoA／Disconnect（RFC 5176，往 NAS UDP 3799）、C4 下游同步。
政策以版本化 Policy Bundle（YAML）匯入匯出，之後可用 ConfigMap／GitOps 下發。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
