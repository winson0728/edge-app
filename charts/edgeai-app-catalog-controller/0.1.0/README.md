# edgeai-app-catalog-controller（edge-app-catalog-controller）

App Catalog（AppPack 目錄、preflight、授權 JWT 驗證、GitOps values commit；ZTP／OTA 子系統掛點）

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
  allowedPorts: []
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
  create: true
  clusterWide: true
  rules:
  - apiGroups:
    - catalog.edgeai.internal
    resources:
    - apppacks
    - apppacks/status
    - edgeapps
    - edgeapps/status
    verbs:
    - get
    - list
    - watch
    - create
    - update
    - patch
    - delete
  - apiGroups:
    - ''
    resources:
    - nodes
    verbs:
    - get
    - list
    - watch
  - apiGroups:
    - ''
    resources:
    - events
    verbs:
    - create
    - patch
catalog:
  giteaUrl: http://edgeai-gitea-http.edgeai-platform.svc:3000
  registry: harbor.example.com/edgeai-packs
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
          catalog:
            registry: {{ .Values.catalog.registry | quote }}   # app-pack（OCI Artifact）
          gitops:
            giteaUrl: {{ .Values.catalog.giteaUrl | quote }}   # token 走 Secret：GITEA_TOKEN
          entitlement:
            publicKeyPath: /etc/edgeai/license/cosign.pub      # 授權 JWT 驗簽公鑰（待以 Secret 掛載）
```

## 說明
CRD `AppPack`（`catalog.edgeai.internal/v1alpha1`，叢集範圍）隨 chart 的 `crds/` 安裝；Helm 不會在升級或移除時改動 CRD。
`EdgeApp` CRD 由每個受管叢集的 edgeai-app-lifecycle-operator 提供。API group 用 `.internal`（私用保留網域），GA 前確認正式名稱。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
