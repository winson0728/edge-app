# edgeai-asterisk（Asterisk（IP PBX））

Asterisk 22 LTS（SIP／RTP、ConfBridge、ARI，ptt-gateway 的媒體面）

- Pack：Voice/PTT（預設 namespace `edgeai-voice`）
- 層級：Hub、Node（Survivable Gateway）
- 架構：amd64, arm64（映像需自建）
- 上游專案：https://www.asterisk.org
- 授權：GPL-2.0；商用打包風險 **中**。不修改、獨立部署；或向 Sangoma 購買商業授權。上游沒有官方容器映像，映像由我們自建並自行承擔散布義務（附原始碼取得方式）。
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
ari:
  existingSecret: ''
pjsip:
  existingSecret: ''
components:
  asterisk:
    enabled: true
    hostNetwork: true
    image:
      repository: ''
      tag: '22'
      pullPolicy: IfNotPresent
    ports:
    - name: sip-udp
      containerPort: 5060
      protocol: UDP
    - name: sip-tcp
      containerPort: 5060
    - name: http
      containerPort: 8088
    config:
      mountPath: /etc/asterisk
      files:
        http.conf: |
          [general]
          enabled=yes
          bindaddr=0.0.0.0
          bindport=8088
        rtp.conf: |
          [general]
          rtpstart={{ .Values.rtp.start }}
          rtpend={{ .Values.rtp.end }}
        logger.conf: |
          [logfiles]
          console => notice,warning,error,verbose
    secretMounts:
    - secretName: '{{ .Values.ari.existingSecret }}'
      mountPath: /etc/asterisk/ari.conf
      subPath: ari.conf
    - secretName: '{{ .Values.pjsip.existingSecret }}'
      mountPath: /etc/asterisk/pjsip.conf
      subPath: pjsip.conf
    persistence:
      enabled: false
      mountPath: /var/spool/asterisk
      size: 10Gi
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        memory: 1Gi
rtp:
  start: 10000
  end: 10199
```

## 說明
- **映像要自建**：Asterisk 官方不發容器映像，`components.asterisk.image.repository` 必填（README 的「映像清單」列出建置來源）。
- 用 hostNetwork 讓 SIP／RTP 直接走節點網卡（RTP 埠段無法用 Service 對應）。
- 分機密碼、ARI 帳密都放 Secret（`pjsip.conf`、`ari.conf`），不要放 values。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
