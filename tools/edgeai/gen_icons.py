"""自研模組 logo：同一套外框（圓角方塊＋Pack 色漸層），白色線條圖示。輸出 assets/logos/<chart>.svg（python tools/edgeai/gen_icons.py）"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "assets" / "logos"
OUT.mkdir(exist_ok=True)

PACK = {  # (亮, 暗)
    "access":   ("#14B8A6", "#0F766E"),
    "platform": ("#3B82F6", "#1E40AF"),
    "voice":    ("#FB923C", "#C2410C"),
    "vision":   ("#A78BFA", "#6D28D9"),
    "mlops":    ("#FBBF24", "#B45309"),
    "iot":      ("#4ADE80", "#15803D"),
    "audit":    ("#64748B", "#1E293B"),
    "network":  ("#38BDF8", "#0369A1"),
}

S = 'fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"'
F = 'fill="#fff"'

GLYPH = {
 # SIM 卡＋晶片格線
 "edgeai-sim-aaa-adapter": ("access", f'''
  <path {S} stroke-width="7" d="M40 26h34l18 18v58a6 6 0 0 1-6 6H40a6 6 0 0 1-6-6V32a6 6 0 0 1 6-6z"/>
  <rect {S} stroke-width="7" x="47" y="56" width="34" height="34" rx="4"/>
  <path {S} stroke-width="5" d="M64 56v34M47 73h34"/>'''),
 # 盾牌＋勾
 "edgeai-access-policy-service": ("access", f'''
  <path {S} stroke-width="7" d="M64 22l34 12v26c0 22-14 38-34 46-20-8-34-24-34-46V34z"/>
  <path {S} stroke-width="7" d="M48 64l11 11 22-23"/>'''),
 # 2x2 應用方塊，其中一格是加號
 "edgeai-app-catalog-controller": ("platform", f'''
  <rect {F} x="28" y="28" width="30" height="30" rx="7"/>
  <rect {F} x="70" y="28" width="30" height="30" rx="7"/>
  <rect {F} x="28" y="70" width="30" height="30" rx="7"/>
  <path {S} stroke-width="7" d="M85 72v26M72 85h26"/>'''),
 # 循環箭頭圍著一個方塊（安裝／升級／回滾）
 "edgeai-app-lifecycle-operator": ("platform", f'''
  <path {S} stroke-width="7" d="M98 60a34 34 0 0 0-60-18"/>
  <path {S} stroke-width="7" d="M30 68a34 34 0 0 0 60 18"/>
  <path {S} stroke-width="7" d="M36 26v17h17M92 102V85H75"/>
  <rect {F} x="52" y="52" width="24" height="24" rx="5"/>'''),
 # 中心閃電＋周圍節點
 "edgeai-unified-event-engine": ("platform", f'''
  <circle {S} stroke-width="5" cx="64" cy="64" r="40"/>
  <circle {F} cx="64" cy="24" r="7"/><circle {F} cx="104" cy="64" r="7"/>
  <circle {F} cx="64" cy="104" r="7"/><circle {F} cx="24" cy="64" r="7"/>
  <path {F} d="M70 38L48 68h14l-6 22 24-32H66z"/>'''),
 # 對講機
 "edgeai-ptt-gateway": ("voice", f'''
  <path {S} stroke-width="7" d="M52 22v20"/>
  <rect {S} stroke-width="7" x="40" y="42" width="48" height="64" rx="10"/>
  <rect {F} x="50" y="52" width="28" height="16" rx="3"/>
  <path {S} stroke-width="5" d="M52 80h24M52 92h24"/>
  <path {S} stroke-width="5" d="M98 50a14 14 0 0 1 0 20M106 42a26 26 0 0 1 0 36"/>'''),
 # 攝影機 → 偵測 → 覆核 三節點流程
 "edgeai-ai-workflow-controller": ("vision", f'''
  <circle {S} stroke-width="7" cx="30" cy="64" r="12"/>
  <rect {S} stroke-width="7" x="54" y="52" width="24" height="24" rx="5"/>
  <path {S} stroke-width="7" d="M98 50l12 14-12 14-12-14z"/>
  <path {S} stroke-width="5" d="M42 64h12M78 64h8"/>
  <path {S} stroke-width="5" d="M30 40V30h68v10"/>'''),
 # 模型方塊＋上架箭頭
 "edgeai-model-release-controller": ("mlops", f'''
  <path {S} stroke-width="7" d="M64 44l30 16v32L64 108 34 92V60z"/>
  <path {S} stroke-width="7" d="M34 60l30 16 30-16M64 76v32"/>
  <path {S} stroke-width="7" d="M64 16v22M54 26l10-10 10 10"/>'''),
 # 晶片＋接腳
 "edgeai-device-adapter": ("iot", f'''
  <rect {S} stroke-width="7" x="40" y="40" width="48" height="48" rx="8"/>
  <rect {F} x="54" y="54" width="20" height="20" rx="3"/>
  <path {S} stroke-width="5" d="M54 26v14M74 26v14M54 88v14M74 88v14M26 54h14M26 74h14M88 54h14M88 74h14"/>'''),
 # 瀏覽器視窗＋儀表板長條
 "edgeai-portal-ui": ("platform", f'''
  <rect {S} stroke-width="7" x="22" y="28" width="84" height="72" rx="9"/>
  <path {S} stroke-width="7" d="M22 46h84"/>
  <circle {F} cx="34" cy="37" r="3.5"/><circle {F} cx="45" cy="37" r="3.5"/>
  <rect {F} x="38" y="72" width="10" height="16" rx="2"/>
  <rect {F} x="56" y="60" width="10" height="28" rx="2"/>
  <rect {F} x="74" y="66" width="10" height="22" rx="2"/>'''),
 # 文件＋雜湊鏈
 "edgeai-audit-service": ("audit", f'''
  <path {S} stroke-width="7" d="M38 22h36l16 16v28M38 22a6 6 0 0 0-6 6v72a6 6 0 0 0 6 6h22"/>
  <path {S} stroke-width="5" d="M44 46h24M44 60h28M44 74h14"/>
  <rect {S} stroke-width="6" x="66" y="80" width="18" height="12" rx="6" transform="rotate(-35 75 86)"/>
  <rect {S} stroke-width="6" x="82" y="92" width="18" height="12" rx="6" transform="rotate(-35 91 98)"/>'''),
 # 監視攝影機＋AI 星芒
 "vlm-app": ("vision", f'''
  <path {S} stroke-width="7" d="M24 50l52-14 6 22-52 14z"/>
  <path {S} stroke-width="7" d="M82 50l14-6v20l-14-4"/>
  <path {S} stroke-width="7" d="M44 68l6 18H30M30 76v20"/>
  <path {F} d="M92 76l4 10 10 4-10 4-4 10-4-10-10-4 10-4z"/>'''),
 # 兩個扣在一起的鏈結（Doublinks SD-WAN）
 "doublinks": ("network", f'''
  <rect {S} stroke-width="7" x="20" y="46" width="52" height="36" rx="18"/>
  <rect {S} stroke-width="7" x="56" y="46" width="52" height="36" rx="18"/>
  <circle {F} cx="38" cy="64" r="5"/><circle {F} cx="90" cy="64" r="5"/>'''),
}

for name, (pack, body) in GLYPH.items():
    a, b = PACK[pack]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>
  <rect width="128" height="128" rx="28" fill="url(#g)"/>{body}
</svg>
'''
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
print(len(GLYPH), "icons")
