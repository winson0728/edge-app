# edgeai-triton（Triton Inference Server）

NVIDIA Triton 推論伺服器（YOLO／TensorRT 模型服務，需 GPU）

- Pack：Vision（預設 namespace `edgeai-vision`）
- 層級：Hub、Node
- 架構：amd64, arm64（Thor／Spark 用同一個多架構映像；Orin 需 JetPack 版映像）
- 上游專案：https://github.com/triton-inference-server/server
- 授權：BSD-3-Clause（程式）＋ NVIDIA 映像 EULA；商用打包風險 **低中**。映像含 CUDA／TensorRT，依 NVIDIA 再散布條款；不重新打包映像即可。
- chart 類型：自寫 chart（tools/edgeai/common 樣板）

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
triton:
  modelRepository: /models
  extraArgs:
  - --model-control-mode=poll
  - --repository-poll-secs=30
components:
  triton:
    enabled: true
    runtimeClassName: nvidia
    image:
      repository: nvcr.io/nvidia/tritonserver
      tag: 26.11-py3
      pullPolicy: IfNotPresent
    command:
    - tritonserver
    args:
    - --model-repository={{ .Values.triton.modelRepository }}
    - '{{ join " " .Values.triton.extraArgs }}'
    ports:
    - name: http
      containerPort: 8000
    - name: grpc
      containerPort: 8001
    - name: metrics
      containerPort: 8002
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 8000
      - name: grpc
        port: 8001
      - name: metrics
        port: 8002
    readinessProbe:
      httpGet:
        path: /v2/health/ready
        port: http
      periodSeconds: 10
    startupProbe:
      httpGet:
        path: /v2/health/live
        port: http
      periodSeconds: 10
      failureThreshold: 60
    persistence:
      enabled: true
      mountPath: /models
      size: 20Gi
    extraVolumes:
    - name: dshm
      emptyDir:
        medium: Memory
        sizeLimit: 1Gi
    extraVolumeMounts:
    - name: dshm
      mountPath: /dev/shm
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        memory: 16Gi
        nvidia.com/gpu: 1
```

## 說明
- 需要 NVIDIA GPU Operator（或 k3s 的 nvidia runtime）與 `nvidia` RuntimeClass。
- 模型的 TensorRT engine 綁 GPU 世代（Orin sm_87、Thor、RTX PRO 各不同），由 model-release-controller（自研）按世代建置後放進模型庫。

## 驗證
```bash
helm lint . 
helm template t . 
```
