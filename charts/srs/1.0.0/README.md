# SRS Media Server

This chart deploys SRS (Simple Realtime Server) on Kubernetes/Rancher.

## Exposed ports
- RTMP: 1935/TCP
- API: 1985/TCP
- HTTP-FLV/HLS: 8080/TCP
- WebRTC: 8000/UDP
- SRT: 10080/UDP

## Notes
- Ingress only handles the HTTP service on port 8080.
- RTMP, WebRTC, and SRT should be exposed through Service/LoadBalancer/NodePort.
- For WebRTC, set `config.candidate` to your public IP or resolvable FQDN.