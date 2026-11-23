#!/usr/bin/env python3
"""產生 Edge AI 開源套件 chart（charts/edgeai-*/<version>/）。

用法：
  python tools/edgeai/build.py --cache <上游 tgz 目錄>        # 全部產生
  python tools/edgeai/build.py --cache <dir> --only edgeai-qdrant

上游 tgz 準備（wrapper 用，檔名 <name>-<version>.tgz）：
  helm pull <repo>/<chart> --version <ver> -d <dir>
  helm pull oci://ghcr.io/berriai/litellm-helm --version <ver> -d <dir>
  CVAT：clone cvat-ai/cvat 該版 tag 的 helm-chart/，helm dependency build 後 helm package。

產生後請跑 tools/edgeai/check.sh（helm lint／template）。
"""
import argparse
import copy
import pathlib
import shutil
import sys
import tarfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
COMMON = HERE / "common" / "templates"
SKELETON = HERE / "common" / "skeleton"


class Dumper(yaml.SafeDumper):
    pass


def _str_rep(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


Dumper.add_representer(str, _str_rep)


def dump(obj):
    return yaml.dump(obj, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=200)


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


SELF_BASE = {
    "nameOverride": "",
    "fullnameOverride": "",
    "imagePullSecrets": [],
    "podSecurityContext": {},
    "nodeSelector": {"kubernetes.io/os": "linux"},
    "tolerations": [],
    "affinity": {},
    "networkPolicy": {"enabled": True, "allowedPorts": [], "allowFrom": []},
    "ingress": {"enabled": False, "className": "", "host": "", "tlsSecret": "", "annotations": {},
                "component": "", "servicePort": ""},
}


SKELETON_BASE = {
    "existingSecret": "",
    "serviceAccount": {"create": True, "name": ""},
    "rbac": {"create": False, "clusterWide": False, "rules": []},
}


def upstreams(c):
    u = c.get("upstream")
    if not u:
        return []
    return u if isinstance(u, list) else [u]


def upstream_chart_meta(cache, u):
    tgz = cache / f"{u['name']}-{u['version']}.tgz"
    if not tgz.exists():
        sys.exit(f"缺上游 tgz：{tgz}")
    with tarfile.open(tgz) as t:
        m = t.extractfile(f"{u['name']}/Chart.yaml")
        return tgz, yaml.safe_load(m.read())


def prefix_q(q, dep):
    q = copy.deepcopy(q)
    v = q["variable"]
    q["variable"] = v[1:] if v.startswith("^") else (f"{dep}.{v}" if dep else v)
    if "subquestions" in q:
        q["subquestions"] = [prefix_q(s, dep) for s in q["subquestions"]]
    return q


def build(c, cat, cache):
    pack = cat["packs"][c["pack"]]
    d = ROOT / "charts" / c["name"] / c["version"]
    if d.exists():
        shutil.rmtree(d)
    (d / "templates").mkdir(parents=True)

    ups = upstreams(c)
    deps, metas = [], []
    for u in ups:
        tgz, meta = upstream_chart_meta(cache, u)
        metas.append(meta)
        dep = {"name": u["name"], "version": u["version"], "repository": u["repository"]}
        if u.get("condition"):
            dep["condition"] = u["condition"]
        deps.append(dep)
        (d / "charts").mkdir(exist_ok=True)
        shutil.copy2(tgz, d / "charts" / tgz.name)

    single_dep = ups[0]["name"] if len(ups) == 1 else None
    app_version = c.get("appVersion") or (str(metas[0].get("appVersion", "")) if metas else "")
    home = c.get("upstreamHome") or (ups[0].get("home") if ups else None) or cat["defaults"]["home"]

    skel = bool(c.get("skeleton"))
    keywords = ["edge-ai", f"pack-{c['pack']}"] + (["skeleton"] if skel else []) + c.get("categories", [])
    chart = {
        "apiVersion": "v2",
        "name": c["name"],
        "description": c["description"],
        "type": "application",
        "version": c["version"],
        "appVersion": app_version,
        "kubeVersion": cat["defaults"]["kubeVersion"],
        "home": home,
    }
    # Rancher 卡片圖示：assets/logos/<chart>.<ext>（相對 repo 根目錄，Rancher 由套件庫直接讀取）
    for ext in ("svg", "png"):
        if (ROOT / "assets" / "logos" / f"{c['name']}.{ext}").exists():
            chart["icon"] = f"file://assets/logos/{c['name']}.{ext}"
            break
    chart["keywords"] = keywords
    if deps:
        chart["dependencies"] = deps
    chart["annotations"] = {
        "catalog.cattle.io/display-name": c["display"] + ("（骨架）" if skel else ""),
        # 非 Rancher 官方 repo 時，Rancher UI 會把 certified 的值當成卡片側標顯示：這裡放 Pack 名稱。
        "catalog.cattle.io/certified": pack["label"],
        "catalog.cattle.io/namespace": pack["namespace"],
        "catalog.cattle.io/release-name": c["name"],
        "catalog.cattle.io/os": "linux",
        "catalog.cattle.io/permits-os": "linux",
        "catalog.cattle.io/kube-version": cat["defaults"]["kubeVersion"],
        "edge-ai/pack": pack["label"],
        "edge-ai/tier": c["tier"],
        "edge-ai/arch": c["arch"],
        "edge-ai/license": c["license"],
        "edge-ai/chart-kind": "skeleton" if skel else ("upstream-wrapper" if ups else "edge-ai-authored"),
    }
    (d / "Chart.yaml").write_text(dump(chart), encoding="utf-8", newline=chr(10))

    # values
    if c["kind"] == "self":
        values = deep_merge(deep_merge(SELF_BASE, SKELETON_BASE) if skel else SELF_BASE, c.get("values", {}))
    else:
        values = {single_dep: c.get("values", {})} if single_dep else c.get("values", {})
    header = (f"# {c['display']} — Edge AI 平台預設值\n"
              f"# 由 tools/edgeai/build.py 依 tools/edgeai/catalog.yaml 產生；請改 catalog 後重產。\n")
    if single_dep:
        header += (f"# 上游 chart：{single_dep} {ups[0]['version']}（{ups[0]['repository'] or '見 README'}）。\n"
                   f"# 所有上游參數都放在 `{single_dep}:` 底下，可用上游文件的任何參數覆寫。\n")
    header += "# 密碼／金鑰一律用 Secret（existingSecret 類參數），不要寫進 values。\n"
    (d / "values.yaml").write_text(header + dump(values), encoding="utf-8", newline=chr(10))

    # questions
    qs = [prefix_q(q, single_dep) for q in c.get("questions", [])]
    (d / "questions.yaml").write_text(
        "# Rancher 安裝表單（Apps → Charts → " + c["display"] + "）\n" + dump({"questions": qs}),
        encoding="utf-8", newline=chr(10))

    # templates
    if c["kind"] == "self":
        for f in COMMON.iterdir():
            shutil.copy2(f, d / "templates" / f.name)
        if skel:
            for f in SKELETON.iterdir():
                shutil.copy2(f, d / "templates" / f.name)
    if c.get("crds"):
        (d / "crds").mkdir()
        for name, body in c["crds"].items():
            (d / "crds" / name).write_text(body, encoding="utf-8", newline=chr(10))
    for name, body in (c.get("extraTemplates") or {}).items():
        (d / "templates" / name).write_text(body, encoding="utf-8", newline=chr(10))
    if c.get("validate"):
        lines = []
        for v in c["validate"]:
            keys = " ".join(f'"{k}"' for k in v["path"].split("."))
            lines.append(f'{{{{- if not (index .Values {keys}) }}}}\n{{{{- fail "{v["msg"]}" }}}}\n{{{{- end }}}}')
        (d / "templates" / "validate.yaml").write_text(
            "{{- /* 安裝前檢查：必填的 Secret 名稱等 */ -}}\n" + "\n".join(lines) + "\n", encoding="utf-8", newline=chr(10))
    notes = [f"{c['display']} 已安裝（release {{{{ .Release.Name }}}}，namespace {{{{ .Release.Namespace }}}}）。",
             f"Pack：{pack['label']}；層級：{c['tier']}；架構：{c['arch']}。"]
    if ups:
        notes.append("上游 chart：" + "、".join(f"{u['name']} {u['version']}" for u in ups) + "。")
    if c["kind"] == "self":
        notes.append("{{- range $name, $c := .Values.components }}{{ if and $c.enabled $c.service $c.service.enabled }}\n"
                     "- {{ include \"eai.componentName\" (list $ $name $c) }}：{{ range $c.service.ports }}{{ .name }}={{ .port }}/{{ default \"TCP\" .protocol }} {{ end }}"
                     "{{ end }}{{ end }}")
    notes.append(f"授權：{c['license']}（商用打包風險：{c['licenseRisk']}）。說明見 chart README。")
    (d / "templates" / "NOTES.txt").write_text("\n".join(notes) + "\n", encoding="utf-8", newline=chr(10))

    # ci 值與 .helmignore
    if c.get("ci"):
        (d / "ci").mkdir()
        (d / "ci" / "test-values.yaml").write_text(
            "# helm lint／template 測試值：只放 Secret 名稱，不含任何密碼\n" + dump(c["ci"]), encoding="utf-8", newline=chr(10))
    (d / ".helmignore").write_text("ci/\n*.bak\n.DS_Store\n", encoding="utf-8", newline=chr(10))

    # app-readme（Rancher 安裝頁頂端）與 README
    lic = c["license"] + (f"　⚠ 商用打包風險：{c['licenseRisk']}" if c["licenseRisk"] not in ("低",) else "")
    src = ("**骨架 chart**（自研模組尚未有程式與映像；映像位置為必填參數）" if skel else
           "自寫 chart（tools/edgeai/common 樣板）" if not ups else
           "上游 chart wrapper：" + "、".join(f"`{u['name']}` {u['version']}" for u in ups)
           + "（上游原封打包於 charts/，只加平台預設值）")
    app_readme = (f"# {c['display']}\n\n{c['description']}\n\n"
                  f"| 項目 | 內容 |\n|---|---|\n"
                  f"| Pack | {pack['label']} |\n| 層級 | {c['tier']} |\n| 架構 | {c['arch']} |\n"
                  f"| 授權 | {lic} |\n| 來源 | {src} |\n\n"
                  "密碼與金鑰請先建立 Secret，再在表單填 Secret 名稱；進階參數用 **Edit YAML**。\n")
    (d / "app-readme.md").write_text(app_readme, encoding="utf-8", newline=chr(10))

    up_lines = ""
    for u in ups:
        up_lines += f"- `{u['name']}` {u['version']}，repo：`{u['repository'] or '（無 chart repo，見下方）'}`"
        if u.get("note"):
            up_lines += f"；{u['note']}"
        up_lines += "\n"
    if c.get("upstreamNote"):
        up_lines += f"- {c['upstreamNote']}\n"
    readme = (f"# {c['name']}（{c['display']}）\n\n{c['description']}\n\n"
              f"- Pack：{pack['label']}（預設 namespace `{pack['namespace']}`）\n"
              f"- 層級：{c['tier']}\n- 架構：{c['arch']}\n- 上游專案：{home}\n"
              f"- 授權：{c['license']}；商用打包風險 **{c['licenseRisk']}**"
              + (f"。{c['licenseNote']}" if c.get("licenseNote") else "") + "\n")
    readme += f"- chart 類型：{src}\n"
    if up_lines:
        readme += "\n## 上游 chart\n" + up_lines
        readme += (f"\n上游參數全部放在 `{single_dep}:` 底下（例如 `{single_dep}.xxx`），可照上游文件覆寫。\n"
                   if single_dep else "\n各上游參數放在各自的 key 底下。\n")
    readme += "\n## 平台預設值\n```yaml\n" + dump(values) + "```\n"
    if c.get("validate"):
        readme += "\n## 必填（安裝前檢查）\n" + "".join(f"- {v['msg']}\n" for v in c["validate"])
    if c.get("readme"):
        readme += "\n## 說明\n" + c["readme"]
    readme += ("\n## 驗證\n```bash\nhelm lint . " + ("-f ci/test-values.yaml" if c.get("ci") else "")
               + "\nhelm template t . " + ("-f ci/test-values.yaml" if c.get("ci") else "") + "\n```\n")
    (d / "README.md").write_text(readme, encoding="utf-8", newline=chr(10))
    return d


def chart_table(cat):
    rows = []
    order = list(cat["packs"].keys())
    for c in sorted(cat["charts"], key=lambda x: (order.index(x["pack"]), x["name"])):
        ups = upstreams(c)
        src = ("自寫" if not ups else "wrapper：" + "、".join(f"{u['name']} {u['version']}" for u in ups))
        risk = c["licenseRisk"]
        lic = c["license"] + ("" if risk == "低" else f" ⚠{risk}")
        rows.append(f"| {cat['packs'][c['pack']]['label']} | `{c['name']}` {c['version']} | {c['display']} | {src} | "
                    f"{c['tier']} | {c['arch']} | {lic} |")
    return ("| Pack | Chart | 軟體 | 來源 | 層級 | 架構 | 授權 |\n|---|---|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n")


def write_docs(cat):
    doc = ROOT / "EDGE-AI-CHARTS.md"
    text = doc.read_text(encoding="utf-8")
    start, end = "<!-- chart-table:start -->", "<!-- chart-table:end -->"
    if start in text and end in text:
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        doc.write_text(head + start + "\n" + chart_table(cat) + end + tail, encoding="utf-8", newline=chr(10))
        print("updated", doc.relative_to(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, type=pathlib.Path)
    ap.add_argument("--only", action="append")
    a = ap.parse_args()
    cat = yaml.safe_load((HERE / "catalog.yaml").read_text(encoding="utf-8"))
    for c in cat["charts"]:
        if a.only and c["name"] not in a.only:
            continue
        print("built", build(c, cat, a.cache).relative_to(ROOT))
    write_docs(cat)


if __name__ == "__main__":
    main()
