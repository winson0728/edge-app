# edgeai-model-release-controller（model-release-controller）

MLflow → Triton 安全上架（按 GPU 世代建 TensorRT engine、benchmark Gate、cosign 簽章、shadow／promote／rollback）

- Pack：MLOps（預設 namespace `edgeai-mlops`）
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
  clusterWide: false
  rules:
  - apiGroups:
    - batch
    resources:
    - jobs
    verbs:
    - get
    - list
    - watch
    - create
    - delete
  - apiGroups:
    - ''
    resources:
    - pods
    - pods/log
    verbs:
    - get
    - list
    - watch
  - apiGroups:
    - ''
    resources:
    - configmaps
    - events
    verbs:
    - get
    - list
    - watch
    - create
    - update
    - patch
release:
  mlflowUrl: http://edgeai-mlflow.edgeai-mlops.svc:5000
  registry: harbor.example.com/edgeai-models
  runnerPools:
    orin:
      nodeSelector:
        edge-ai/gpu-gen: orin
    thor:
      nodeSelector:
        edge-ai/gpu-gen: thor
    rtx-pro:
      nodeSelector:
        edge-ai/gpu-gen: rtx-pro
    spark:
      nodeSelector:
        edge-ai/gpu-gen: spark
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
          mlflow: {{ .Values.release.mlflowUrl | quote }}
          registry: {{ .Values.release.registry | quote }}     # 帳密走 Secret：REGISTRY_USER／REGISTRY_PASSWORD
          runnerPools: {{ toJson .Values.release.runnerPools }}
          gates:
            maxMapDropPercent: 1
```

## 說明
介面：C10 以 K8s Job 派到各 GPU 世代的 runner（依 `edge-ai/gpu-gen` 節點標籤）。TensorRT engine 綁 compute capability，必須在目標世代上建置。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
