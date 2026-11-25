{{- define "vlm-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "vlm-app.fullname" -}}
{{- printf "%s" (default .Chart.Name .Values.nameOverride) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "vlm-app.labels" -}}
app.kubernetes.io/name: {{ include "vlm-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{- define "vlm-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "vlm-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Image tag: explicit image.tag, else "<platform>-<appVersion>" (0.1.2+) */}}
{{- define "vlm-app.imageTag" -}}
{{- default (printf "%s-%s" .Values.image.platform .Chart.AppVersion) .Values.image.tag -}}
{{- end -}}

{{/* Resolve the Ollama URL the app should use */}}
{{- define "vlm-app.ollamaUrl" -}}
{{- if .Values.ollama.enabled -}}
http://{{ include "vlm-app.fullname" . }}-ollama:{{ .Values.ollama.service.port }}
{{- else -}}
{{ .Values.externalOllamaUrl }}
{{- end -}}
{{- end -}}
