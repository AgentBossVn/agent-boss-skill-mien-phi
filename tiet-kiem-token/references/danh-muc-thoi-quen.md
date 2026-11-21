# Danh mục thói quen tốn token (nguồn: tài liệu chính thức Anthropic, tra 20/11/2026)

> Đọc khi viết đề xuất ở Bước 3. Giá, tên lệnh, yêu cầu phiên bản có thể đổi — nghi thì tra lại code.claude.com/docs/en/costs.

Ký hiệu: [CC] = code.claude.com/docs/en/ · [API] = platform.claude.com/docs/en/ . Lệnh/cài đặt trích từ tài liệu chính thức; yêu cầu phiên bản ghi kèm.

## A. Cơ chế tính token

- Mỗi tin nhắn = 1 yêu cầu API mới; mô hình không nhớ gì giữa các yêu cầu nên Claude Code gửi lại TOÀN BỘ ngữ cảnh (system prompt, CLAUDE.md, trí nhớ, mọi tin nhắn và kết quả công cụ trước đó). Mỗi lần Claude gọi công cụ cũng là một yêu cầu mới mang theo toàn bộ. [CC prompt-caching, costs#why-usage-climbs]
- Cache khớp theo TIỀN TỐ chính xác: đổi bất kỳ chỗ nào trong tiền tố thì mọi thứ phía sau tính lại. Thứ tự: system prompt+định nghĩa công cụ → CLAUDE.md/auto memory/rules → hội thoại. [CC prompt-caching]
- Nạp sẵn trước khi gõ: system prompt, auto memory (MEMORY.md: 200 dòng đầu hoặc 25KB), thông tin môi trường, TÊN công cụ MCP (định nghĩa hoãn nạp mặc định), mô tả skill, ~/.claude/CLAUDE.md, CLAUDE.md dự án, ảnh chụp git status. Ví dụ minh hoạ của Anthropic: ~7.850 token trước khi gõ. [CC context-window, memory]
- Trợ lý con (subagent): cửa sổ ngữ cảnh riêng, yêu cầu riêng, VẪN tính vào cùng hạn mức; chỉ bản tóm tắt quay về. Lượt đầu của nó không đọc cache của cha. Explore/Plan không nạp CLAUDE.md. [CC sub-agents, prompt-caching#subagents]
- Auto-compact: mặc định nén khi chạm giới hạn ngữ cảnh của mô hình. Sonnet 4.6/Opus 4.6 không bật 1M: ở mốc 200K; mô hình 1M gốc: ~967K token. Chỉnh bằng `/autocompact 500k` hoặc `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` (chỉ hạ được, không nâng). [CC model-config#default-auto-compact-thresholds, env-vars]
- Giá tương đối (so với input gốc): ghi cache 5 phút 1,25x; ghi cache 1 giờ 2x; đọc cache 0,1x (0,05x với Opus 5.5 và Sonnet 5.5; 0,025x dòng Fable/Mythos 5.1–5.2). Output đắt gấp 5x input ở các mô hình Opus 5.5/Sonnet 5.5/Opus 4.x/Sonnet 4.x (vd Sonnet 5.5: input $2, ghi 5m $2,5, ghi 1h $4, đọc $0,10, output $10 /MTok). Token "suy nghĩ" tính như output. [API prompt-caching, pricing; CC costs#adjust-extended-thinking]
- Số đo thực nghiệm 1 người dùng nặng (66 phiên, 4.339 lượt, $2.650): chi phí = 60% ngữ cảnh gửi lại (đọc cache), 25% ghi cache mới, 15% output, ~0% input không cache. Chỉ là dữ liệu của một người, không đại diện. [dev.to/wartzarbee/where-your-claude-code-bill-actually-goes-i-measured-66-of-my-own-sessions-471e]

## C. TTL cache (xác minh chính thức)

- Mặc định 5 phút, làm mới miễn phí mỗi lần trúng; tuỳ chọn 1 giờ (ghi 2x). Thời hạn tính từ lúc BẮT ĐẦU yêu cầu. [API prompt-caching]
- Claude Code: thuê bao Claude, trong hạn mức gói: hội thoại chính được 1 giờ. API key / vượt hạn mức (dùng credit) / Bedrock...: 5 phút. Mọi thứ ngoài hội thoại chính (subagent, workflow, compaction, đặt tên phiên): 5 phút (trừ vài yêu cầu phụ do Anthropic điều khiển). [CC prompt-caching#which-ttl]
- Tự chọn: `promptCacheTtl` / `CLAUDE_CODE_PROMPT_CACHE_TTL` (`5m`|`1h`); `subagentPromptCacheTtl` / `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` (cần v2.1.242+); `ENABLE_PROMPT_CACHING_1H=1`; `FORCE_PROMPT_CACHING_5M=1`. Kiểm tra: `claude -p "hello" --output-format json` rồi đọc `usage.cache_creation.ephemeral_1h_input_tokens` / `ephemeral_5m_input_tokens`.
- Nghỉ quá TTL: tin đầu quay lại xử lý lại toàn bộ ngữ cảnh. `/compact` sau khi nghỉ lâu tốn nhất (đọc lại lịch sử không cache). Idle compaction (`idleCompaction`, v2.1.290+) có thể tự nén phiên bỏ dở ở TTL 1 giờ. [CC prompt-caching]
- Cache theo máy+thư mục: hai phiên khác thư mục không dùng chung cache.

## B. Danh mục thói quen tốn token

Cột đo = trường trong ~/.claude/projects/*/*.jsonl. Đã kiểm tra trên nhật ký thật: mỗi dòng assistant có `message.usage` {input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, cache_creation.{ephemeral_5m,ephemeral_1h}_input_tokens}, `message.model`, `timestamp`, `isSidechain`; subagent nằm ở thư mục `<sessionId>/subagents/`. Cột "Nguồn" mặc định [CC costs] trừ khi ghi khác.

| # | Thói quen | Vì sao tốn | Đo trong nhật ký | Cách sửa |
|---|---|---|---|---|
| 1 | Một phiên kéo dài nhiều giờ/nhiều việc | Ngữ cảnh phình, mỗi lượt đọc lại toàn bộ | tổng (input+cache_read+cache_creation) mỗi lượt tăng dần; số lượt/phiên lớn; đỉnh >150K | `/clear` giữa việc không liên quan (`/rename` trước để `/resume` sau); `/compact` ở điểm nghỉ tự nhiên |
| 2 | Không nén kịp, để auto-compact giữa việc | Nén giữa việc mất chi tiết, ghi lại cache | dòng tóm tắt compact; cache_creation nhảy vọt sau đó | `/compact tập trung vào ...`; `/autocompact 500k`; mục "Compact instructions" trong CLAUDE.md |
| 3 | Nghỉ >TTL rồi nhắn tiếp trong phiên to | Cache hết hạn, ghi lại toàn bộ | khoảng cách `timestamp` giữa 2 lượt > 5 phút (hoặc >1 giờ) và lượt sau có cache_creation lớn, cache_read ≈ 0 | Việc mới thì `/clear`; trước khi đi xa `/compact`; tự đặt `promptCacheTtl=1h` nếu dùng API key (cân nhắc ghi 2x) |
| 4 | Đổi `/model` hoặc effort giữa phiên | Mỗi mô hình một cache riêng | `message.model` đổi giữa 2 lượt liên tiếp + cache_creation lớn | Chọn mô hình/effort ở đầu phiên. `opusplan` mỗi lần bật plan là một lần đổi mô hình |
| 5 | Dùng mô hình đắt nhất cho việc đơn giản | Giá/MTok chênh 2–40 lần (Haiku 5.5 $0,10 vs Opus 5.5 $4 input) | phân bố `message.model` × tổng token | `/model` Sonnet cho việc thường; Opus cho thiết kế khó; subagent `model: haiku` [CC costs, API pricing] |
| 6 | Để thinking/effort tối đa cho việc nhỏ | Thinking tính như output (đắt 5x); ngân sách có thể hàng chục nghìn token/yêu cầu | output_tokens trung bình/lượt cao dù trả lời ngắn | `/effort` thấp hơn; `MAX_THINKING_TOKENS=8000` (mô hình ngân sách cố định); Opus 5.5/Sonnet 5.5/Haiku 5.5 không tắt được thinking |
| 7 | CLAUDE.md / MEMORY.md quá dài | Nạp mọi phiên, mọi lượt, cả lúc làm việc khác | độ dài khối nạp đầu phiên (cache_creation của lượt đầu); đo trực tiếp bằng wc -l | <200 dòng; chuyển quy trình riêng sang skill hoặc rules có `paths:`; `/context`; `/usage` có dòng khuyến nghị "Trim ... CLAUDE.md" [CC memory, costs] |
| 8 | Nhiều MCP server bật sẵn | Tên + hướng dẫn server vào ngữ cảnh mỗi phiên (định nghĩa hoãn nạp mặc định); tắt/bật giữa phiên có thể huỷ cache khi không hoãn nạp | tên công cụ `mcp__*` trong tool_use; kích thước kết quả | `/mcp` tắt server không dùng; ưu tiên CLI (`gh`, `aws`); `ENABLE_TOOL_SEARCH=auto:5` |
| 9 | Kết quả công cụ khổng lồ (cat log, test dài, đọc cả tệp lớn) | Nằm trong ngữ cảnh và bị gửi lại mọi lượt về sau | độ dài nội dung `tool_result` (ký tự/4 ≈ token); `tool_use.input.command` kiểu `cat`, `npm test` không lọc | Hook PreToolUse rút gọn (`tail -n 100`); `BASH_MAX_OUTPUT_LENGTH` (mặc định 30000 ký tự); `MAX_MCP_OUTPUT_TOKENS` (25000); đọc tệp mặc định giới hạn 25.000 token (`CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`), dùng offset/limit |
| 10 | Đọc lại cùng tệp nhiều lần / quét rộng bằng yêu cầu mơ hồ | Mỗi lần đọc thêm vào ngữ cảnh | `tool_use` Read lặp cùng `file_path`; nhiều Grep/Glob liên tiếp | Prompt cụ thể ("thêm kiểm tra đầu vào hàm login trong auth.ts"); plugin code intelligence; skill tổng quan dự án |
| 11 | Việc đọc/tìm nhiều làm ngay trong phiên chính | Dữ liệu thô ở lại ngữ cảnh chính | chuỗi dài tool_use Read/Grep/WebFetch trong phiên chính (isSidechain=false) | Giao cho subagent; chỉ tóm tắt quay về (Anthropic: thường 1.000–2.000 token) [anthropic.com/engineering/effective-context-engineering-for-ai-agents] |
| 12 | Lạm dụng subagent/agent team cho việc nhỏ | Mỗi cái cửa sổ riêng, không dùng chung cache, TTL 5 phút; agent team ~7x token | tỉ lệ dòng `isSidechain=true`, số tệp trong `subagents/`, token của chúng | Chỉ dùng cho việc đọc nhiều; `model: haiku`; `CLAUDE_CODE_SUBAGENT_MODEL` ép một mô hình |
| 13 | Đi sai hướng rồi sửa dài dòng | Lượt sai và chữa sai nằm mãi trong ngữ cảnh | cụm nhiều lượt Edit rồi Edit lại cùng tệp; tin người dùng kiểu "sai rồi/làm lại" | Plan mode (Shift+Tab); Esc dừng sớm; `/rewind` (cắt về tiền tố đã cache, rẻ hơn compact); đưa tiêu chí kiểm tra vào prompt |
| 14 | Vòng lặp/lịch (`/loop`, scheduled task), goal check-in, tin giữa các phiên khi phiên rảnh | Cứ đến hạn gửi lại TOÀN BỘ ngữ cảnh | các lượt có `timestamp` đều đặn không có tin người dùng ở giữa | `/usage` mục Loops; `CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0`; `crossSessionInbound=hold` |
| 15 | Tích nhiều ảnh/PDF chụp màn hình | Ảnh nặng; khi vượt giới hạn Claude Code cắt ảnh cũ làm đổi tin nhắn và tính lại từ đó | `content.type=image` trong tin người dùng; cache_creation vọt | Dán ít ảnh, cắt nhỏ; `/clear` sau khi xong việc cần ảnh |
| 16 | Thêm/bớt plugin-MCP, bật fast mode giữa phiên | Đổi system prompt/công cụ, cache riêng cho fast mode | cache_read≈0 ở một lượt giữa chuỗi lượt đều trúng; `usage.speed` | Cấu hình ở đầu phiên; xem dòng `Prompt cache (main)` ... "likely cause" trong `/usage` (v2.1.251+/2.1.260+) |
| 17 | Nhiều phiên song song cùng một ngữ cảnh lớn, mở nhiều cửa sổ rồi bỏ quên | Mỗi phiên đọc lại ngữ cảnh khi chạm lại sau khi hết TTL | nhiều `sessionId` cùng `cwd` xen kẽ trong ngày | Đóng phiên xong việc; mỗi việc một phiên ngắn |
| 18 | Resume phiên rất cũ rồi `/compact` | Cache nguội: đọc lại toàn bộ lịch sử không cache, kể cả để tóm tắt | lượt đầu sau resume: cache_creation lớn; timestamp cách xa | Resume chỉ khi thật cần; ưu tiên phiên mới + ghi chú ngắn |
| 19 | Dài dòng ở đầu ra (giải thích, báo cáo dài) | Output đắt 5x input | output_tokens/lượt | Yêu cầu trả lời ngắn; output style gọn; (chưa có nguồn chính thức nói cụ thể về hiệu quả, ghi chú: suy luận từ giá) |
| 20 | Hook/skill/plugin nhét văn bản vào ngữ cảnh mỗi lượt | Văn bản hook thêm sau mỗi sự kiện | `attachment` hook output lặp lại | Hook chỉ in dòng cần thiết; skill: chỉ tên+mô tả nạp sẵn, nội dung chỉ nạp khi dùng; mô tả skill ngắn; giới hạn ngân sách `SLASH_COMMAND_TOOL_CHAR_BUDGET` [anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills] |

Mô hình tính chi phí từ nhật ký: cost_lượt = input×p_in + cache_creation×p_ghi (tách 5m/1h) + cache_read×p_đọc + output×p_out, theo `message.model`. Dòng `model:"<synthetic>"` toàn 0: bỏ qua.

## D. Thuê bao vs API

- API/Console: tính tiền theo token ở bảng giá trên; `/usage` hiện chi phí ước tính (tính cục bộ theo giá niêm yết). [CC costs]
- Thuê bao Pro/Max/Ultra: không tính tiền theo token nhưng token vẫn quyết định tốc độ cạn hạn mức. Có hạn mức phiên 5 giờ (tính từ tin đầu) và hạn mức tuần; claude.ai, Claude Code, Claude Desktop dùng chung. Độ dài/độ phức tạp hội thoại, mô hình, effort, công cụ/connector đều làm cạn nhanh hơn. [support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work]
- Chưa xác minh: trọng số chính xác của cache_read so với input trong hạn mức thuê bao (trang trợ giúp không nói; tài liệu CC chỉ nói phiên dài "vẫn tính cho cả cuộc hội thoại" ở giá cache).
- Xem mức dùng: `/usage` (thanh hạn mức, thống kê, phân bổ theo skill/subagent/plugin/MCP, khuyến nghị ≥10%, phím `d`/`w` đổi 24 giờ/7 ngày, phím `f` áp khuyến nghị v2.1.305+); `/context` (ngữ cảnh theo nhóm); `/insights` (báo cáo HTML, cũng tốn token); Settings > Usage trên claude.ai; thanh trạng thái (`current_usage`, `prompt_cache`). Số liệu `/usage` lấy từ lịch sử cục bộ máy này, không gồm thiết bị khác. [CC costs]
- Công cụ cộng đồng (bên thứ ba — chỉ chạy khi người dùng đồng ý): ccusage (`npx ccusage daily|session|blocks`, đọc dữ liệu cục bộ, giá từ bảng LiteLLM nên chỉ là ước tính; hỗ trợ cả Codex, Gemini CLI) [github.com/ryoppippi/ccusage].

## Bài học chung cho Codex/Cursor/Gemini
Chỉ xác minh được ccusage đọc nhật ký Codex/Gemini CLI. Trang Codex CLI lấy được không nói gì về nén ngữ cảnh/hạn AGENTS.md: chưa xác minh. Cursor: chưa tra. Nguyên lý chung (ngữ cảnh finite, nén, xoá kết quả công cụ cũ, truy xuất đúng lúc, subagent) có nguồn Anthropic: anthropic.com/engineering/effective-context-engineering-for-ai-agents.

## Khuyến nghị cho skill kiểm kê (xếp hạng)
1. Đo được ngay từ JSONL, ưu tiên: #1/#3/#4 (khoảng cách timestamp, đổi model), #5 (phân bố model), #9 (tool_result lớn), #7 (khối đầu phiên), #12 (isSidechain), #14 (lượt đều đặn).
2. Tách chi phí theo cache_read/cache_creation/output và theo model; dùng bảng giá trên (ghi rõ ngày giá).
3. Gợi ý sửa luôn đi kèm lệnh thật ở bảng; nhắc `/usage` nếu bản CC đủ mới.

## Hạn chế / chưa xác minh
- Tài liệu CC thay đổi theo phiên bản; số v2.1.x ghi theo trang hiện tại. Giá có thể đổi.
- Chưa tìm thấy thử nghiệm có kiểm soát; chỉ có 1 số đo cá nhân.
- Cursor, Gemini CLI, Codex: chưa xác minh đặc thù.
- Mục 16, 17, 19: một phần là suy luận từ cơ chế, không có số đo nguồn.

