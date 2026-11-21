#!/usr/bin/env python3
"""Dò CHỖ GỌI AI trong code của bạn (bot, web, máy tự chạy): tệp nào gọi hãng AI nào, model nào.
Tầng này KHÔNG nằm trong nhật ký Claude Code nhưng thường là chỗ tốn TIỀN THẬT (trả theo token qua API key).
Chỉ đọc mã nguồn; bỏ qua tệp khoá (.env, .dev.vars…), node_modules, .git. Không in nội dung dòng.

Dùng: python3 do-cho-goi-ai-trong-code.py <thư mục 1> [thư mục 2 …]"""
import collections, os, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BO_THU_MUC = {"node_modules", ".git", "dist", "build", ".next", ".venv", "venv", "__pycache__", ".wrangler",
              ".claude", "vendor", "coverage", ".cache", "worktrees", "secrets", ".ssh", ".aws", ".gnupg"}
DUOI = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php", ".sh", ".toml", ".yaml", ".yml", ".json"}
# Tệp có thể chứa khoá: KHÔNG mở (kể cả chỉ để dò chữ)
TEP_KHOA = re.compile(r"(^\.env|\.dev\.vars$|secret|credential|token|passw|private|service.?account"
                      r"|(^|[-_.])(auth|keys?)([-_.]|$)|\.pem$)", re.I)
MODEL = re.compile(r"\b(claude-(?:opus|sonnet|haiku|fable|3)[\w.-]*|gpt-[\w.-]+|(?<=[\"'])o[134](?:-mini|-pro)?(?=[\"'])|gemini-[\w.-]+"
                   r"|deepseek-[\w-]+|grok-[\w.-]+|llama-?[\d.]+[\w.-]*|mistral-[\w-]+|whisper-[\w-]+|@cf/[\w/.-]+)", re.I)
RE_DUOI_TEP = re.compile(r"\.(txt|md|py|js|mjs|ts|json|sh|html|png|jpg|yml|yaml)$|-(review|report|test)s?$", re.I)
# Model thuộc hãng nào — theo TÊN model, không theo tệp (1 tệp có thể gọi nhiều hãng)
CHU_MODEL = [("claude-", ("Anthropic (Claude)", "Claude Code chạy tự động (claude -p)")), ("gpt-", ("OpenAI", "Groq")),
             ("o1", ("OpenAI",)), ("o3", ("OpenAI",)), ("o4", ("OpenAI",)), ("gemini-", ("Google Gemini",)),
             ("deepseek-", ("DeepSeek", "Cloudflare Workers AI")), ("@cf/", ("Cloudflare Workers AI",)),
             ("llama", ("Cloudflare Workers AI", "Groq")), ("mistral-", ("Cloudflare Workers AI",)),
             ("whisper-", ("OpenAI", "Groq", "Cloudflare Workers AI")), ("grok-", ("xAI",))]


def cua_hang(model, hang):
    return any(model.startswith(tien_to) and hang in chu for tien_to, chu in CHU_MODEL)


HANG = [("Anthropic (Claude)", re.compile(r"api\.anthropic\.com|@anthropic-ai/sdk|from anthropic|import anthropic", re.I)),
        ("OpenAI", re.compile(r"api\.openai\.com|from openai|['\"]openai['\"]", re.I)),
        ("Google Gemini", re.compile(r"generativelanguage\.googleapis|@google/gen(erative-)?ai|google\.genai|google\.generativeai", re.I)),
        ("OpenRouter", re.compile(r"openrouter\.ai", re.I)), ("DeepSeek", re.compile(r"api\.deepseek\.com", re.I)),
        ("Groq", re.compile(r"api\.groq\.com", re.I)), ("fal.ai", re.compile(r"fal\.(ai|run)", re.I)),
        ("Cloudflare Workers AI", re.compile(r"env\.AI\.run|@cf/", re.I)),
        ("Claude Code chạy tự động (claude -p)", re.compile(r"\bclaude\s+(-p|--print)\b|claude-agent-sdk|claude_agent_sdk", re.I))]


def quet(goc):
    for thu_muc, con, tep in os.walk(goc):
        con[:] = [c for c in con if c not in BO_THU_MUC]
        for t in tep:
            p = Path(thu_muc) / t
            if not p.is_symlink() and p.suffix.lower() in DUOI and not TEP_KHOA.search(t) and not t.endswith((".lock", "-lock.json")):
                try:
                    if p.stat().st_size < 2_000_000:
                        yield p, p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    theo_hang = collections.defaultdict(lambda: {"tep": set(), "model": collections.Counter()})
    da_quet = set()
    for goc in sys.argv[1:]:
        goc = Path(goc).expanduser().resolve()
        if not goc.is_dir():
            print(f"(bỏ qua: không có thư mục {goc})", file=sys.stderr)
            continue
        for p, chu in quet(goc):
            p = p.absolute()  # truyền thư mục cha + con chồng nhau vẫn không đếm đôi (không theo symlink)
            if p in da_quet:
                continue
            da_quet.add(p)
            hang = [ten for ten, re_ in HANG if re_.search(chu)]
            if not hang:
                continue
            models = collections.Counter(m.lower().rstrip(".-") for m in MODEL.findall(chu)
                                         if not RE_DUOI_TEP.search(m))
            for h in hang:
                theo_hang[h]["tep"].add(str(p).replace(str(Path.home()), "~"))
                theo_hang[h]["model"].update({m: n for m, n in models.items() if cua_hang(m, h)})
    print("# Chỗ gọi AI trong code\n")
    if not theo_hang:
        print("Không thấy code nào gọi AI trong các thư mục đã dò.")
        return
    print("| Hãng | số tệp | model nhắc tới (số lần) |\n|---|---|---|")
    for h, v in sorted(theo_hang.items(), key=lambda kv: -len(kv[1]["tep"])):
        print(f"| {h} | {len(v['tep'])} | {', '.join(f'{m} {n}' for m, n in v['model'].most_common(6)) or '-'} |")
    print("\n## Tệp (tối đa 8 mỗi hãng)")
    for h, v in theo_hang.items():
        print(f"- **{h}**: " + " · ".join(sorted(v["tep"])[:8]) + (" …" if len(v["tep"]) > 8 else ""))
    print("\nModel ghi trong tệp chưa chắc là model đang chạy (có thể là chú thích, tệp cũ). "
          "Số tiền thật: trang Usage/Billing của từng hãng (Anthropic: platform.claude.com → Usage).")


if __name__ == "__main__":
    main()
