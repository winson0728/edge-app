# edgeai-mosquitto（Eclipse Mosquitto）

Eclipse Mosquitto MQTT broker（事件匯流排、IoT 上報；可開 dynamic security）

- Pack：IoT/OT（預設 namespace `edgeai-iot`）
- 層級：Hub、Node、Gateway
- 架構：amd64, arm64
- 上游專案：https://mosquitto.org
- 授權：EPL-2.0 / EDL-1.0；商用打包風險 **低**
- chart 類型：自寫 chart（tools/edgeai/common 樣板）

## 平台預設值
```yaml
nameOverride: ''
fullnameOverride: ''
imagePullSecrets: []
podSecurityContext:
  fsGroup: 1883
nodeSelector:
  kubernetes.io/os: linux
tolerations: []
affinity: {}
networkPolicy:
  enabled: true
  allowedPorts:
  - port: 1883
  - port: 9001
  allowFrom: []
ingress:
  enabled: false
  className: ''
  host: ''
  tlsSecret: ''
  annotations: {}
  component: ''
  servicePort: ''
mqtt:
  allowAnonymous: false
  passwordSecret: ''
  dynamicSecurity: false
  websockets: false
components:
  mosquitto:
    enabled: true
    image:
      repository: docker.io/library/eclipse-mosquitto
      tag: 2.0.23
      pullPolicy: IfNotPresent
    ports:
    - name: mqtt
      containerPort: 1883
    - name: ws
      containerPort: 9001
    service:
      enabled: true
      type: ClusterIP
      ports:
      - name: mqtt
        port: 1883
      - name: ws
        port: 9001
    readinessProbe:
      tcpSocket:
        port: mqtt
      periodSeconds: 10
    config:
      mountPath: /mosquitto/config
      files:
        mosquitto.conf: |
          persistence true
          persistence_location /mosquitto/data/
          log_dest stdout
          per_listener_settings false
          listener 1883
          {{- if .Values.mqtt.websockets }}
          listener 9001
          protocol websockets
          {{- end }}
          allow_anonymous {{ .Values.mqtt.allowAnonymous }}
          {{- if .Values.mqtt.passwordSecret }}
          password_file /mosquitto/secret/passwd
          {{- end }}
          {{- if .Values.mqtt.dynamicSecurity }}
          plugin /usr/lib/mosquitto_dynamic_security.so
          plugin_opt_config_file /mosquitto/data/dynamic-security.json
          {{- end }}
    secretMounts:
    - secretName: '{{ .Values.mqtt.passwordSecret }}'
      mountPath: /mosquitto/secret
      defaultMode: 288
    persistence:
      enabled: false
      mountPath: /mosquitto/data
      size: 1Gi
    resources:
      requests:
        cpu: 20m
        memory: 32Mi
      limits:
        memory: 256Mi
```

## 說明
建立帳密檔（雜湊，不是明碼）：
```bash
docker run --rm -it eclipse-mosquitto:2.0.23 sh -c 'mosquitto_passwd -c /tmp/passwd edge && cat /tmp/passwd' > passwd
kubectl -n edgeai-iot create secret generic mosquitto-passwd --from-file=passwd=./passwd
```
Dynamic Security 的初始 admin 需在 Pod 內用 `mosquitto_ctrl dynsec init` 建立（密碼互動輸入）。

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
