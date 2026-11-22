{{/*
Edge AI 共用樣板（由 tools/edgeai/build.py 複製到每個自寫 chart，請改 tools/edgeai/common 再重新產生）。
*/}}
{{- define "eai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "eai.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/* 元件資源名稱：<fullname>-<component>；serviceName 可覆寫（例如 EdgeX 需固定主機名）。 */}}
{{- define "eai.componentName" -}}
{{- $root := index . 0 -}}{{- $name := index . 1 -}}{{- $c := index . 2 -}}
{{- if $c.serviceName -}}
{{- $c.serviceName | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" (include "eai.fullname" $root) $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "eai.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/name: {{ include "eai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: edge-ai
{{- end -}}

{{- define "eai.selectorLabels" -}}
{{- $root := index . 0 -}}{{- $name := index . 1 -}}
app.kubernetes.io/name: {{ include "eai.name" $root }}
app.kubernetes.io/instance: {{ $root.Release.Name }}
app.kubernetes.io/component: {{ $name }}
{{- end -}}

{{- define "eai.image" -}}
{{- $c := index . 0 -}}{{- $name := index . 1 -}}
{{- $repo := required (printf "components.%s.image.repository 必填（映像位置，見 README）" $name) $c.image.repository -}}
{{- if $c.image.digest -}}
{{- printf "%s@%s" $repo $c.image.digest -}}
{{- else -}}
{{- printf "%s:%s" $repo (required (printf "components.%s.image.tag 必填" $name) (toString $c.image.tag)) -}}
{{- end -}}
{{- end -}}

{{/* ServiceAccount 名稱（骨架 chart 的 controller 用）。 */}}
{{- define "eai.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "eai.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
