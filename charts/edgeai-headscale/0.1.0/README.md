# edgeai-headscale（Headscale）

Headscale（自架 Tailscale 控制面，站點 Mesh／行動指揮車）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://headscale.net
- 授權：BSD-3-Clause；商用打包風險 **低**
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
  allowedPorts:
  - port: 8080
  allowFrom: []
ingress:
  enabled: false
  className: ''
  host: ''
  tlsSecret: ''
  annotations: {}
  component: headscale
  servicePort: http
headscale:
  serverUrl: https://headscale.example.com
  baseDomain: mesh.edge.internal
  nameservers:
  - 1.1.1.1
components:
  headscale:
    enabled: true
    image:
      repository: docker.io/headscale/headscale
      tag: 0.29.7
      pullPolicy: IfNotPresent
    args:
    - serve
    ports:
    - name: http
      containerPort: 8080
    - name: metrics
      containerPort: 9090
    - name: grpc
      containerPort: 50443
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: http
        port: 8080
      - name: metrics
        port: 9090
      - name: grpc
        port: 50443
    readinessProbe:
      httpGet:
        path: /health
        port: http
      periodSeconds: 10
    config:
      mountPath: /etc/headscale
      files:
        config.yaml: |
          server_url: {{ .Values.headscale.serverUrl }}
          listen_addr: 0.0.0.0:8080
          metrics_listen_addr: 0.0.0.0:9090
          grpc_listen_addr: 0.0.0.0:50443
          grpc_allow_insecure: false
          noise:
            private_key_path: /var/lib/headscale/noise_private.key
          prefixes:
            v4: 100.64.0.0/10
            v6: fd7a:115c:a1e0::/48
            allocation: sequential
          derp:
            server:
              enabled: false
            urls:
              - https://controlplane.tailscale.com/derpmap/default
            auto_update_enabled: true
            update_frequency: 3h
          disable_check_updates: true
          database:
            type: sqlite
            sqlite:
              path: /var/lib/headscale/db.sqlite
              write_ahead_log: true
          log:
            level: info
          policy:
            mode: database
          dns:
            magic_dns: true
            base_domain: {{ .Values.headscale.baseDomain }}
            override_local_dns: true
            nameservers:
              global: {{ toJson .Values.headscale.nameservers }}
          unix_socket: /var/run/headscale/headscale.sock
          unix_socket_permission: "0770"
    extraVolumes:
    - name: run
      emptyDir: {}
    extraVolumeMounts:
    - name: run
      mountPath: /var/run/headscale
    persistence:
      enabled: true
      mountPath: /var/lib/headscale
      size: 1Gi
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        memory: 256Mi
```

## 說明
- DERP 預設用 Tailscale 公用 derpmap；離線站點請把 `derp.server.enabled` 打開並改 `components.headscale.config`。
- 建使用者／金鑰：`kubectl exec deploy/<release>-headscale -- headscale users create site-a`。

## 驗證
```bash
helm lint . 
helm template t . 
```
