{{- define "zerotier-planet.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "zerotier-planet.fullname" -}}
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

{{- define "zerotier-planet.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "zerotier-planet.labels" -}}
helm.sh/chart: {{ include "zerotier-planet.chart" . }}
app.kubernetes.io/name: {{ include "zerotier-planet.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "zerotier-planet.selectorLabels" -}}
app.kubernetes.io/name: {{ include "zerotier-planet.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "zerotier-planet.namespace" -}}
{{- default .Release.Namespace .Values.namespaceOverride -}}
{{- end -}}

{{- define "zerotier-planet.secretName" -}}
{{- if .Values.secret.existingSecret -}}
{{- .Values.secret.existingSecret -}}
{{- else -}}
{{- .Values.secret.name -}}
{{- end -}}
{{- end -}}

{{- define "zerotier-planet.zerotierOneClaimName" -}}
{{- if .Values.persistence.zerotierOne.existingClaim -}}
{{- .Values.persistence.zerotierOne.existingClaim -}}
{{- else -}}
{{- .Values.persistence.zerotierOne.claimName -}}
{{- end -}}
{{- end -}}

{{- define "zerotier-planet.ztncuiEtcClaimName" -}}
{{- if .Values.persistence.ztncuiEtc.existingClaim -}}
{{- .Values.persistence.ztncuiEtc.existingClaim -}}
{{- else -}}
{{- .Values.persistence.ztncuiEtc.claimName -}}
{{- end -}}
{{- end -}}
