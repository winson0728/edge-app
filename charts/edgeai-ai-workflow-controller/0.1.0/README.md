# edgeai-ai-workflow-controller（ai-workflow-controller）

Vision Pipeline 編排（VisionPipeline CR、Camera 註冊、YOLO 偵測→VLM 覆核、VLM 預算、Privacy 遮罩、Evidence）

- Pack：Vision（預設 namespace `edgeai-vision`）
- 層級：Node、Hub
- 架構：amd64, arm64（ds-worker 只有 Jetson／arm64）
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
    - vision.edgeai.internal
    resources:
    - visionpipelines
    - visionpipelines/status
    verbs:
    - get
    - list
    - watch
    - update
    - patch
  - apiGroups:
    - apps
    resources:
    - deployments
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
    - events
    verbs:
    - get
    - list
    - watch
    - create
    - update
    - patch
workflow:
  mediamtxApi: http://edgeai-mediamtx-mediamtx.edgeai-vision.svc:9997
  tritonUrl: edgeai-triton-triton.edgeai-vision.svc:8001
  vlmUrl: http://edgeai-vllm-router-service.edgeai-rag.svc/v1
  vlmMaxConcurrent: 2
workers:
  ds:
    repository: ''
    tag: ''
  gst:
    repository: ''
    tag: ''
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
          media:
            mediamtxApi: {{ .Values.workflow.mediamtxApi | quote }}
          inference:
            triton: {{ .Values.workflow.tritonUrl | quote }}
            vlm: {{ .Values.workflow.vlmUrl | quote }}
            vlmBudget: {maxConcurrent: {{ .Values.workflow.vlmMaxConcurrent }}}
          workers:
            dsImage: "{{ .Values.workers.ds.repository }}:{{ .Values.workers.ds.tag }}"     # DeepStream（Jetson）
            gstImage: "{{ .Values.workers.gst.repository }}:{{ .Values.workers.gst.tag }}"   # GStreamer＋Triton client（通用）
```

## 說明
介面：C8 Triton gRPC／vLLM OpenAI 相容 API。worker 由 controller 依節點類型動態建立 Deployment（因此 RBAC 只給本 namespace 的 deployments）。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
