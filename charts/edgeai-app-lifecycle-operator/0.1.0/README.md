# edgeai-app-lifecycle-operator（app-lifecycle-operator）

每叢集的 App 生命週期 operator（EdgeApp CR：安裝／升級／回滾，GitOps 或 air-gap 模式）

- Pack：Platform（預設 namespace `edgeai-platform`）
- 層級：Hub、Node、Gateway（每個受管叢集一份）
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
  create: true
  clusterWide: true
  rules:
  - apiGroups:
    - catalog.edgeai.internal
    resources:
    - edgeapps
    - edgeapps/status
    - edgeapps/finalizers
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
    - configmaps
    - secrets
    - namespaces
    - events
    verbs:
    - get
    - list
    - watch
    - create
    - update
    - patch
  - apiGroups:
    - ''
    resources:
    - nodes
    verbs:
    - get
    - list
    - watch
operator:
  mode: gitops
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
          mode: {{ .Values.operator.mode }}   # gitops＝commit values 到 Gitea 交給 Argo／Fleet；airgap＝Helm SDK 直接安裝（需更大 RBAC）
          history: 10
```

## 說明
air-gap 模式要以 Helm SDK 直接安裝 App，需要的 RBAC 遠大於骨架預設（目前只給 EdgeApp、ConfigMap、Secret、Namespace）；實作時依實際安裝範圍收斂，不建議直接給 cluster-admin。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
