# 交接檔（handoff.md）

> 接手前必讀；收工、每完成一段、回報負責人前都要更新並 push。

## 本分支（claude/aplus-manual-20261122）交接

> 本 repo 是公開 repo：本段與手冊都不寫內部 IP、主機名稱、帳密或 token。

- **任務與對應查核點**：A+ 前瞻計畫 11/22 指示「各子專案產生操作手冊」，本 repo 新建 `docs/操作手冊.md`（Rancher 套件庫）。對應查核點：成果文件／操作手冊（編號由負責人維護，待確認）。
- **目前做到哪**：手冊 v1.0 完成並推送。涵蓋套件庫定位、結構與資料流（Mermaid）、既有 4 個與 32 個 `edgeai-*` chart 的 Pack 分類、Rancher 加入方式（UI／ClusterRepo／HTTP 型）、安裝與回復、維護者更新流程、Secret 與映像架構限制、授權注意、故障排除。
- **分支與最新 commit**：`claude/aplus-manual-20261122`，基底 origin/main @ `e560b71`。手冊 commit `251bcfe`；本交接段落為其後一個 commit。本分支不含另一個本機分支上尚未推送的 11 個 Layer 2 骨架 chart（那是其他工作的範圍，不要從這裡推）。
- **已驗證的證據**：
  - 2026-11-22 推送前掃描兩次：無私有網段 IP、主機名稱、帳密、token。
  - chart 清單對照 `EDGE-AI-CHARTS.md` 與 `git ls-tree origin/main charts/`；驗證狀態摘自 `tools/edgeai/VERIFY.md`（32 個 lint／template 全過，6 個在 Lab 單節點叢集實裝）。本 session 未安裝任何 chart。
- **未完成的工作與下一步**：
  1. 由負責人審閱後合併。
  2. 待確認：GPU／PVC／operator／hostNetwork 類 chart 第二輪實裝；根目錄 README 仍是 SRS 說明；各 chart Secret key 名稱未逐一列入手冊。
- **注意事項與禁區**
  - 本分支只做文件；不合併、不推 main、不改 AGENTS.md。手冊與交接不得寫入帳密、token、API key、Ki／OPc、IMSI。
  - 截圖只能在 Lab 擷取；Jetson Thor 目前只能唯讀（另有 session 在 Thor 做接管測試），不可為了截圖或驗證手冊去操作 Thor。
  - 手冊內容以程式與既有文件為準，未實測的寫「待確認」，不要改成肯定句。
- **回復點／回滾方式**：本分支只新增或修改文件。要撤掉就刪除遠端分支 `git push origin --delete claude/aplus-manual-20261122`，或 `git revert <commit>`；不影響任何部署。
- **更新時間與更新者**：2026-11-24，Claude Code（Edge 與核網系列手冊 session；派工者為 A+ 負責人 session）

---

