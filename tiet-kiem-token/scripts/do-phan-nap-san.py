#!/usr/bin/env python3
"""Đo PHẦN NẠP SẴN đầu mỗi phiên Claude Code (thứ máy đọc trước khi bạn gõ chữ nào): CLAUDE.md, rules,
mô tả skill / agent, máy chủ MCP, hook. Chỉ đếm ký tự + tên; KHÔNG in giá trị khoá trong cấu hình.

Dùng: python3 do-phan-nap-san.py [--du-an <thư mục dự án>] [--goc ~/.claude]
Ước token = ký tự / 3,5 (tiếng Việt có dấu ra nhiều token hơn tiếng Anh — chỉ để so nặng nhẹ)."""
import argparse, json, os, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--du-an", default=os.getcwd())
ap.add_argument("--goc", default=os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude"))
A = ap.parse_args()
GOC, DU_AN = Path(A.goc).expanduser().resolve(), Path(A.du_an).expanduser().resolve()
# Thư mục cấu hình cần quét, loại trùng (chạy ở thư mục home thì DU_AN/.claude chính là GOC)
CAU_HINH = list(dict.fromkeys([GOC, (DU_AN / ".claude").resolve()]))
RE_IMPORT = re.compile(r"(?:^|\s)@(~?[\w./-]+\.md)\b")
RE_MOTA = re.compile(r"^description:\s*(.+?)(?=^\w[\w-]*:|^---)", re.M | re.S)


def json_dict(tep):
    try:
        d = json.loads(doc(tep) or "{}")
    except ValueError:
        return {}
    return d if isinstance(d, dict) else {}


def doc(p):
    try:
        return Path(p).expanduser().read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def claude_md(p, da=None):
    """Ký tự của 1 CLAUDE.md + các tệp nó @import (1 tầng sâu là đủ để thấy chỗ nặng)."""
    da = da if da is not None else set()
    p = Path(p).expanduser()
    if p in da or not p.is_file():
        return []
    da.add(p)
    t = doc(p)
    ra = [(str(p), len(t))]
    for im in RE_IMPORT.findall(t):
        q = (p.parent / im).expanduser() if not im.startswith(("~", "/")) else Path(im).expanduser()
        ra += [(f, n) for f, n in claude_md(q, da)] if q.is_file() else []
    return ra


def mo_ta(thu_muc, mau):
    """[(tên, số ký tự description)] của các SKILL.md / agent .md."""
    ra = []
    for p in sorted(Path(thu_muc).glob(mau)):
        m = RE_MOTA.search(doc(p).split("\n---", 2)[0] + "\n---")
        if m:
            ra.append((p.parent.name if p.name == "SKILL.md" else p.stem, len(m.group(1).strip())))
    return ra


def mcp():
    ten = set()
    cau_hinh_chinh = GOC / ".claude.json" if os.environ.get("CLAUDE_CONFIG_DIR") else Path.home() / ".claude.json"
    for tep in (cau_hinh_chinh, DU_AN / ".mcp.json", *(c / "settings.json" for c in CAU_HINH)):
        d = json_dict(tep)
        ten |= set(d.get("mcpServers") or {})
        pj = d.get("projects") or {}
        for khoa in {str(DU_AN), DU_AN.as_posix()}:
            ten |= set(((pj.get(khoa) or {}) if isinstance(pj, dict) else {}).get("mcpServers") or {})
    return sorted(ten)


def hook():
    n = 0
    teps = [c / ten for c in CAU_HINH for ten in ("settings.json", "settings.local.json")]
    for tep in dict.fromkeys(t.resolve() for t in teps):
        h = json_dict(tep).get("hooks")
        if isinstance(h, dict):
            n += sum(len(x.get("hooks") or []) for v in h.values() if isinstance(v, list) for x in v if isinstance(x, dict))
    return n


tk = lambda c: f"~{c / 3.5 / 1000:,.1f}k token"
md = claude_md(GOC / "CLAUDE.md") + sum((claude_md(p) for p in sorted((GOC / "rules").rglob("*.md"))), [])
cha = DU_AN
while True:  # CLAUDE.md của dự án và mọi thư mục cha (Claude Code đọc cả)
    for ten in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md"):
        if cha != GOC.parent or ten != ".claude/CLAUDE.md":
            md += claude_md(cha / ten)
    if cha.parent == cha:
        break
    cha = cha.parent
md = list(dict(md).items())
sk = sum((mo_ta(c / "skills", "*/SKILL.md") for c in CAU_HINH), [])
pl = mo_ta(GOC / "plugins", "**/skills/*/SKILL.md")  # có thể gồm plugin đã tải mà chưa bật
ag = sum((mo_ta(c / "agents", "*.md") for c in CAU_HINH), [])
m = mcp()
c_md, c_sk, c_ag = sum(n for _, n in md), sum(n for _, n in sk), sum(n for _, n in ag)

print(f"# Phần nạp sẵn đầu phiên — dự án {str(DU_AN).replace(str(Path.home()), '~')}\n")
print(f"| Khối | số mục | ký tự | ước |\n|---|---|---|---|")
print(f"| CLAUDE.md + rules + @import | {len(md)} | {c_md:,} | {tk(c_md)} |")
print(f"| Mô tả skill | {len(sk)} | {c_sk:,} | {tk(c_sk)} |")
print(f"| Mô tả skill của plugin (gồm cả plugin chưa bật — ước TRẦN) | {len(pl)} | {sum(n for _, n in pl):,} | {tk(sum(n for _, n in pl))} |")
print(f"| Mô tả agent (trợ lý con tự tạo) | {len(ag)} | {c_ag:,} | {tk(c_ag)} |")
print(f"| Máy chủ MCP (mỗi cái thêm mô tả công cụ) | {len(m)} | — | xem /context |")
print(f"| Hook đang cài | {hook()} | — | mỗi lần hook chặn = 1 lượt làm lại |")
print("\n## Tệp chỉ dẫn nặng nhất")
for f, n in sorted(md, key=lambda x: -x[1])[:8]:
    print(f"- {n:,} ký tự · {f.replace(str(Path.home()), '~')}")
print("\n## Mô tả skill dài nhất (>500 ký tự là dài)")
for t, n in sorted(sk, key=lambda x: -x[1])[:8]:
    print(f"- {n:,} · {t}")
if m:
    print("\n## Máy chủ MCP: " + ", ".join(m))
print("\nĐối chiếu số THẬT: gõ /context trong Claude Code (đếm chính xác từng khối).")
