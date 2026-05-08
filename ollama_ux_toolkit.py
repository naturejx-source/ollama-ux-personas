"""
Ollama UX 工具箱 — 讓羊駝幹活
12 個 UX 研究/設計工具，全部跑在本地 Ollama（零成本）

用法:
  python ollama_ux_toolkit.py                          # 互動選單
  python ollama_ux_toolkit.py --tool 3 --input "描述"   # 直接跑某工具
  python ollama_ux_toolkit.py --tool 9 --file data.csv  # 批量分析
"""
import requests, json, sys, io, csv, argparse, os
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API = "http://localhost:11434/api/generate"
BASE = "C:/Users/natur/Desktop/1/"
MODEL = "llama3"

PERSONAS = {
    "ming": "阿明 (HK設計師/粵語/情感治癒)",
    "chen": "小陳 (深圳工程師/簡中/技術分析)",
    "jake": "Jake (美國大學生/EN/休閒社交)",
    "yu":   "小雨 (台灣行銷/繁中/社群歸屬)",
}

# ── 核心 API ───────────────────────────────────────────
def ask(model, prompt, timeout=180):
    try:
        resp = requests.post(API, json={
            "model": model, "prompt": prompt, "stream": False,
        }, timeout=timeout)
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "(Ollama 未啟動 — 請先執行 ollama serve)"
    except Exception as e:
        return f"(Error: {e})"

def load_csv_comments(path, col="comment"):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            text = r.get(col) or r.get("review") or r.get("answer") or ""
            if text.strip():
                rows.append(text.strip())
    return rows

# ── 12 個 UX 工具 ─────────────────────────────────────

TOOLS = {}

def tool(tid, name, desc):
    def decorator(fn):
        TOOLS[tid] = {"name": name, "desc": desc, "fn": fn}
        return fn
    return decorator

# ────────────────────────────────────────────────────────
# 1. Persona 問答
# ────────────────────────────────────────────────────────
@tool(1, "Persona 問答", "問 4 個 AI 角色同一個問題，比較回應")
def tool_persona(user_input, **kw):
    print(f"\n  問題: {user_input}\n")
    for key, desc in PERSONAS.items():
        print(f"  [{key}] {desc}")
        print(f"  {'─'*50}")
        answer = ask(key, user_input)
        for line in answer.split('\n'):
            print(f"    {line}")
        print()

# ────────────────────────────────────────────────────────
# 2. 親和圖分類
# ────────────────────────────────────────────────────────
@tool(2, "親和圖分類", "把用戶回饋自動分成主題群組")
def tool_affinity(user_input, **kw):
    file_path = kw.get("file")
    if file_path and os.path.exists(file_path):
        comments = load_csv_comments(file_path)
        if len(comments) > 30:
            comments = comments[:30]
        data = "\n".join(f"- {c[:100]}" for c in comments)
    else:
        data = user_input

    prompt = f"""你是一個 UX 研究員，擅長親和圖法 (Affinity Mapping)。
請將以下用戶回饋分成 5-8 個主題群組。

每個群組需要：
1. 群組名稱
2. 包含哪些回饋（編號）
3. 核心洞察（一句話）

用戶回饋：
{data}

用繁體中文回答，格式清晰。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 3. 啟發式評估 (Nielsen 10)
# ────────────────────────────────────────────────────────
@tool(3, "啟發式評估", "用 Nielsen 10 原則評估設計")
def tool_heuristic(user_input, **kw):
    prompt = f"""你是資深 UX 顧問。請用 Jakob Nielsen 的 10 條可用性啟發式原則評估以下設計：

設計描述：{user_input}

對每條原則：
- 原則名稱
- 評分 (1-5)
- 具體問題或優點
- 改進建議

最後給出總體評分和 Top 3 優先改進項。
用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 4. 用戶故事生成
# ────────────────────────────────────────────────────────
@tool(4, "用戶故事生成", "從 Persona 角度寫 User Story")
def tool_userstory(user_input, **kw):
    prompt = f"""你是一個產品經理。根據以下功能描述，為 4 個不同的用戶角色各寫一條 User Story。

功能描述：{user_input}

4 個角色：
1. 阿明 — 28歲香港設計師，工作壓力大，玩遊戲是治癒方式
2. 小陳 — 24歲深圳工程師，Steam重度用戶，重視技術品質
3. Jake — 22歲美國大學生，Discord社交派，喜歡派對遊戲
4. 小雨 — 23歲台灣行銷，重視社群歸屬，喜歡可愛風格

格式：As a [角色], I want [功能], so that [價值]。
每條附加：驗收標準 (Acceptance Criteria) 2-3 條。
用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 5. 訪談腳本生成
# ────────────────────────────────────────────────────────
@tool(5, "訪談腳本生成", "根據研究目標生成半結構式訪談問題")
def tool_interview(user_input, **kw):
    prompt = f"""你是一個 UX 研究員，擅長設計用戶訪談。
根據以下研究目標，生成一份半結構式訪談腳本。

研究目標：{user_input}

請包含：
1. 暖場問題 (2題) — 讓受訪者放鬆
2. 核心問題 (5-6題) — 探索研究目標
3. 深入追問 (每題附 1-2 個 follow-up)
4. 收尾問題 (1-2題) — 開放式總結

注意事項：
- 避免引導性問題
- 使用開放式提問
- 按邏輯順序排列（從一般到具體）
用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 6. 競品分析
# ────────────────────────────────────────────────────────
@tool(6, "競品分析", "分析競品優缺點和差異化機會")
def tool_competitor(user_input, **kw):
    prompt = f"""你是一個產品策略師。請對以下產品/競品進行比較分析：

產品列表：{user_input}

請輸出：
1. 每個產品的核心賣點 (1-2句)
2. 優缺點對比表
3. 功能差異矩陣
4. 差異化機會 (3-5個)
5. 對「牛馬派對」(一款香港文化主題的派對遊戲DAPP) 的啟示

用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 7. 旅程地圖
# ────────────────────────────────────────────────────────
@tool(7, "旅程地圖", "生成用戶旅程（階段、接觸點、情緒、痛點）")
def tool_journey(user_input, **kw):
    prompt = f"""你是一個 UX 設計師，擅長用戶旅程地圖 (User Journey Map)。
根據以下場景生成一份旅程地圖：

場景：{user_input}

請用表格格式輸出：
| 階段 | 用戶行為 | 接觸點 | 情緒(高/中/低) | 痛點 | 機會點 |

至少包含 5-6 個階段，從發現到留存。
最後總結 Top 3 關鍵痛點和設計機會。
用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 8. UX 文案
# ────────────────────────────────────────────────────────
@tool(8, "UX 文案", "生成 UI 文案（按鈕、提示、錯誤訊息）")
def tool_copy(user_input, **kw):
    prompt = f"""你是一個 UX Writer，專門寫介面文案。
目標產品是「牛馬派對」— 一款融入香港打工文化的派對遊戲。
語氣：幽默、親切、帶港式風味。

需要文案的場景：{user_input}

請提供：
1. 主文案 — 3 個版本（正式/幽默/港式）
2. 按鈕文字 — 2-3 個選項
3. 錯誤/空狀態文案 — 2 個版本
4. 微文案建議（tooltip、placeholder 等）

每個版本附一句設計理由。
用繁體中文回答（港式版用粵語）。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 9. 情緒分析
# ────────────────────────────────────────────────────────
@tool(9, "情緒分析", "批量分析用戶回饋的正負面情緒")
def tool_sentiment(user_input, **kw):
    file_path = kw.get("file")
    if file_path and os.path.exists(file_path):
        comments = load_csv_comments(file_path)
        if len(comments) > 20:
            comments = comments[:20]
        data = "\n".join(f"{i+1}. {c[:80]}" for i, c in enumerate(comments))
    else:
        data = user_input

    prompt = f"""你是 UX 研究員，請對以下用戶回饋做情緒分析。

回饋列表：
{data}

對每條回饋：
- 情緒：正面 / 負面 / 中性
- 強度：強 / 中 / 弱
- 關鍵詞：提取 2-3 個情緒關鍵詞

最後統計：
- 正面/負面/中性 比例
- 最常出現的正面和負面主題
- 改進建議 Top 3
用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 10. 卡片分類
# ────────────────────────────────────────────────────────
@tool(10, "卡片分類", "模擬卡片分類，建議資訊架構")
def tool_cardsort(user_input, **kw):
    prompt = f"""你是一個資訊架構師 (Information Architect)。
請對以下功能/內容項目做卡片分類 (Card Sorting)。

項目列表：{user_input}

請：
1. 將項目分成 4-6 個邏輯類別
2. 為每個類別命名
3. 說明分類邏輯
4. 建議導航結構（主選單 → 子選單）
5. 標注哪些項目可能讓用戶困惑（跨類別）

用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 11. A/B 假設
# ────────────────────────────────────────────────────────
@tool(11, "A/B 測試假設", "從設計問題生成可測試的 A/B 假設")
def tool_abtest(user_input, **kw):
    prompt = f"""你是一個 Growth/UX 分析師，擅長設計 A/B 測試。
根據以下設計問題，生成 3 組可測試的 A/B 假設。

設計問題：{user_input}

每組假設需要：
1. 假設陳述：If [改變], then [效果], because [原因]
2. 變體 A（對照組）描述
3. 變體 B（實驗組）描述
4. 主要指標 (Primary Metric)
5. 次要指標 (Secondary Metrics)
6. 最小樣本量建議
7. 預期效果大小

用繁體中文回答。"""
    print(ask(MODEL, prompt))

# ────────────────────────────────────────────────────────
# 12. 設計批評
# ────────────────────────────────────────────────────────
@tool(12, "設計批評", "從可用性角度批評設計方案")
def tool_critique(user_input, **kw):
    prompt = f"""你是一位有 10 年經驗的 UX 設計總監，正在做設計評審 (Design Critique)。

設計描述：{user_input}

請從以下角度評價：
1. 可用性 — 用戶能完成目標嗎？有哪些障礙？
2. 可學習性 — 新用戶能快速上手嗎？
3. 一致性 — 和常見設計模式一致嗎？
4. 可及性 — 有無障礙問題？
5. 情感設計 — 用戶感受如何？

格式：
- 做得好的（2-3點）
- 需要改進的（3-5點，按優先級排序）
- 具體改進建議

語氣直接但建設性。用繁體中文回答。"""
    print(ask(MODEL, prompt))


# ── 互動界面 ───────────────────────────────────────────

def show_menu():
    print(f"""
  {'='*56}
   Ollama UX 工具箱  |  本地 llama3 驅動  |  零成本
  {'='*56}
""")
    for tid in sorted(TOOLS):
        t = TOOLS[tid]
        print(f"   {tid:>2}. {t['name']:<12} — {t['desc']}")
    print(f"""
  {'─'*56}
   輸入工具編號開始，或:
   help  查看工具說明    quit  退出
   file <路徑>  設定 CSV 檔案（用於工具 2, 9）
  {'='*56}
""")

def interactive():
    show_menu()
    csv_file = None

    while True:
        try:
            cmd = input("  [UX] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue
        if cmd.lower() in ('quit', 'exit', 'q'):
            break
        if cmd.lower() == 'help':
            show_menu()
            continue
        if cmd.lower().startswith('file '):
            csv_file = cmd[5:].strip()
            if os.path.exists(csv_file):
                print(f"  CSV 已設定: {csv_file}")
            else:
                print(f"  找不到檔案: {csv_file}")
                csv_file = None
            continue

        parts = cmd.split(maxsplit=1)
        try:
            tid = int(parts[0])
        except ValueError:
            print(f"  請輸入工具編號 (1-12)")
            continue

        if tid not in TOOLS:
            print(f"  未知工具: {tid} (可選: 1-12)")
            continue

        t = TOOLS[tid]
        if len(parts) > 1:
            user_input = parts[1]
        else:
            user_input = input(f"  [{t['name']}] 輸入: ").strip()
            if not user_input:
                continue

        print(f"\n  {'─'*50}")
        print(f"  {t['name']} | 處理中...\n")
        t["fn"](user_input, file=csv_file)
        print(f"\n  {'─'*50}\n")


def main():
    parser = argparse.ArgumentParser(description="Ollama UX 工具箱")
    parser.add_argument("--tool", type=int, help="工具編號 (1-12)")
    parser.add_argument("--input", type=str, help="輸入文字")
    parser.add_argument("--file", type=str, help="CSV 檔案路徑")
    parser.add_argument("--list", action="store_true", help="列出所有工具")
    args = parser.parse_args()

    if args.list:
        for tid in sorted(TOOLS):
            t = TOOLS[tid]
            print(f"  {tid:>2}. {t['name']:<12} — {t['desc']}")
        return

    if args.tool:
        if args.tool not in TOOLS:
            print(f"  未知工具: {args.tool}")
            return
        t = TOOLS[args.tool]
        inp = args.input or ""
        if not inp and args.tool not in (2, 9):
            print(f"  請用 --input 提供輸入")
            return
        print(f"\n  {t['name']} | 處理中...\n")
        t["fn"](inp, file=args.file)
        return

    interactive()


if __name__ == "__main__":
    main()
