# VLM-APP Helm chart

Runs VLM-APP — and optionally Ollama — on a single-node k3s or RKE2 cluster
with an NVIDIA GPU (x86 RTX 50 series, Jetson AGX Thor, DGX Spark).

## Prerequisites

### 1. NVIDIA runtime and device plugin

The pod requests `nvidia.com/gpu: 1` (`gpu.exclusive: true`), so the node needs
the NVIDIA device plugin (or the GPU Operator) and a `nvidia` RuntimeClass.
On k3s without the GPU Operator:

```bash
sudo nvidia-ctk runtime configure --runtime=containerd \
  --config=/var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl
sudo systemctl restart k3s

kubectl apply -f - <<'EOF'
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata: { name: nvidia }
handler: nvidia
EOF
```

To share one physical GPU between vlm-app and the bundled Ollama pod, enable
time-slicing in the device plugin so the node advertises more than one
`nvidia.com/gpu`.

### 2. Load the image on the node

The image is not published to a registry. Build it from the VLM-APP source
(x86: `Dockerfile`; ARM64: `Dockerfile.spark-gpu`) and import it into the
node's containerd, then install with that tag. `image.pullPolicy` defaults to
`Never`, so the node must already have the image.

```bash
docker save vlm-app:<tag> | sudo k3s ctr images import -
```

## Install

From the Rancher UI (Apps → Charts → vlm-app) the form asks for the values
below. From the command line:

```bash
helm install vlm ./charts/vlm-app/0.1.1 -n vlm --create-namespace \
  --set image.tag=<tag> \
  --set admin.password='<strong password>' \
  --set ollama.enabled=false --set externalOllamaUrl=http://<ollama-host>:11434 \
  --set service.web.type=NodePort --set service.web.nodePort=<port> --set ingress.enabled=false
```

`admin.password` (or `admin.existingSecret`) is required: the chart ships no
default password.

## Key values

| Value | Default | Notes |
|-------|---------|-------|
| `image.repository` / `image.tag` | `vlm-app` / `latest` | the image you loaded on the node |
| `image.pullPolicy` | `Never` | local image only |
| `gpu.runtimeClassName` | `nvidia` | `""` = CPU only |
| `gpu.exclusive` | `true` | requests `nvidia.com/gpu: 1` |
| `admin.password` | `""` | **required** unless `admin.existingSecret` is set |
| `service.web.type` / `nodePort` | `ClusterIP` / `""` | `NodePort` to skip the ingress |
| `service.mqtt.type` / `nodePort` | `NodePort` / `31883` | signal lights connect here |
| `ingress.enabled` / `host` | `true` / `vlm.local` | Traefik (k3s default) |
| `persistence.size` | `20Gi` | DB, media, clips, backups (`VLM_DATA_DIR=/data`) |
| `ollama.enabled` | `true` | run Ollama as a pod |
| `ollama.pullModel` | `ministral-3:8b` | pulled on first start |
| `externalOllamaUrl` | `""` | used when `ollama.enabled=false` |

## Persistence

All writable state (SQLite event DB, event keyframes, video clips, backups,
camera settings) lives under `VLM_DATA_DIR=/data`, backed by one
`ReadWriteOnce` PVC. The Deployment uses `Recreate` so the single SQLite
writer never overlaps.

## Health

The readiness and liveness probes use `/healthz`, which returns 503 when the
object detector has stalled; `/metrics` serves Prometheus metrics.
