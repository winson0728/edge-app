# edgeai-kea-dhcp（Kea DHCP）

ISC Kea DHCPv4（hostNetwork，直接服務指定網卡）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub、Node
- 架構：amd64（ISC 官方映像只有 amd64；arm64 需自建映像）
- 上游專案：https://www.isc.org/kea/
- 授權：MPL-2.0；商用打包風險 **低**。修改 Kea 原始檔需公開該檔；純部署無義務。
- chart 類型：自寫 chart（tools/edgeai/common 樣板）

## 平台預設值
```yaml
nameOverride: ''
fullnameOverride: ''
imagePullSecrets: []
podSecurityContext: {}
nodeSelector:
  kubernetes.io/os: linux
  kubernetes.io/arch: amd64
tolerations: []
affinity: {}
networkPolicy:
  enabled: false
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
dhcp:
  interface: eth0
  subnet: 192.0.2.0/24
  poolStart: 192.0.2.100
  poolEnd: 192.0.2.200
  router: 192.0.2.1
  dnsServers: 192.0.2.1
  validLifetime: 4000
components:
  kea:
    enabled: true
    hostNetwork: true
    image:
      repository: docker.cloudsmith.io/isc/docker/kea-dhcp4
      tag: 3.0.5
      pullPolicy: IfNotPresent
    securityContext:
      capabilities:
        add:
        - NET_ADMIN
        - NET_RAW
        - NET_BIND_SERVICE
    config:
      mountPath: /etc/kea
      files:
        kea-dhcp4.conf: |
          {
            "Dhcp4": {
              "interfaces-config": { "interfaces": [ {{ .Values.dhcp.interface | quote }} ] },
              "lease-database": { "type": "memfile", "persist": true, "name": "/var/lib/kea/dhcp4.leases" },
              "valid-lifetime": {{ .Values.dhcp.validLifetime }},
              "subnet4": [
                {
                  "id": 1,
                  "subnet": {{ .Values.dhcp.subnet | quote }},
                  "pools": [ { "pool": "{{ .Values.dhcp.poolStart }} - {{ .Values.dhcp.poolEnd }}" } ],
                  "option-data": [
                    { "name": "routers", "data": {{ .Values.dhcp.router | quote }} },
                    { "name": "domain-name-servers", "data": {{ .Values.dhcp.dnsServers | quote }} }
                  ]
                }
              ],
              "loggers": [ { "name": "kea-dhcp4", "output-options": [ { "output": "stdout" } ], "severity": "INFO" } ]
            }
          }
    persistence:
      enabled: false
      mountPath: /var/lib/kea
      size: 1Gi
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        memory: 256Mi
```

## 說明
- 用 hostNetwork 直接在節點網卡收送 DHCP；請用 `nodeSelector` 鎖定要服務的節點，避免同網段出現兩台 DHCP。
- HA（Kea hot-standby）與 Site Survival 副本是 v2 Roadmap §3.2 的工作，本 chart 先提供單機版。
- 預設位址是文件用的 192.0.2.0/24（RFC 5737），安裝時務必改成現場網段。

## 驗證
```bash
helm lint . 
helm template t . 
```
