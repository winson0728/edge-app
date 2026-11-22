# edgeai-keycloak（Keycloak）

Keycloak（OIDC／SSO，平台與各模組的身分來源）

- Pack：Access & NAC（預設 namespace `edgeai-access`）
- 層級：Hub
- 架構：amd64, arm64
- 上游專案：https://www.keycloak.org
- 授權：Apache-2.0；商用打包風險 **低**
- chart 類型：上游 chart wrapper：`keycloakx` 7.4.0（上游原封打包於 charts/，只加平台預設值）

## 上游 chart
- `keycloakx` 7.4.0，repo：`https://codecentric.github.io/helm-charts`；社群（codecentric）chart，使用 Keycloak 官方映像 quay.io/keycloak/keycloak

上游參數全部放在 `keycloakx:` 底下（例如 `keycloakx.xxx`），可照上游文件覆寫。

## 平台預設值
```yaml
keycloakx:
  adminExistingSecret: ''
  command:
  - /opt/keycloak/bin/kc.sh
  - start
  - --http-port=8080
  - --hostname-strict=false
  - --http-enabled=true
  extraEnv: |
    - name: KC_BOOTSTRAP_ADMIN_USERNAME
      valueFrom: {secretKeyRef: {name: {{ .Values.adminExistingSecret | quote }}, key: username}}
    - name: KC_BOOTSTRAP_ADMIN_PASSWORD
      valueFrom: {secretKeyRef: {name: {{ .Values.adminExistingSecret | quote }}, key: password}}
    - name: KC_HEALTH_ENABLED
      value: "true"
  proxy:
    mode: xforwarded
  database:
    vendor: postgres
    hostname: ''
    port: 5432
    database: keycloak
    username: keycloak
    existingSecret: ''
    existingSecretKey: password
```

## 必填（安裝前檢查）
- keycloakx.adminExistingSecret 必填（含 username／password 的 Secret）
- keycloakx.database.hostname 必填（PostgreSQL，例如 edgeai-cloudnative-pg 建的叢集）
- keycloakx.database.existingSecret 必填

## 驗證
```bash
helm lint . -f ci/test-values.yaml
helm template t . -f ci/test-values.yaml
```
