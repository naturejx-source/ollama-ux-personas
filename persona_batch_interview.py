"""
牛馬派對設計驗證 — 4 Persona 批量訪談
問 6 個核心設計問題，存結果為報告
"""
import requests, json, sys, io, csv
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API = "http://localhost:11434/api/generate"
BASE = "C:/Users/natur/Desktop/1/"

PERSONAS = [
    ("ming", "阿明 Ming", "HK", "香港設計師"),
    ("chen", "小陳 Chen", "CN", "深圳工程師"),
    ("jake", "Jake", "US", "美國大學生"),
    ("yu",   "小雨 Yu", "TW", "台灣行銷"),
]

QUESTIONS = [
    {
        "id": "Q1_redvan",
        "theme": "核心玩法",
        "q_zh": "牛馬派對的核心玩法是開紅色小巴(紅VAN)互相撞對方下車。你覺得這個設定有趣嗎？你會想加什麼技能或道具？用三四句話回答",
        "q_en": "NiuMa Party's core gameplay is driving Hong Kong red minibuses and pushing each other off. Do you find this concept fun? What skills or items would you add? Answer in 3-4 sentences.",
    },
    {
        "id": "Q2_monetize",
        "theme": "付費模式",
        "q_zh": "你能接受的遊戲付費方式是什麼？皮膚購買、通行證、還是完全免費靠廣告？你最多願意花多少錢？用兩三句話回答",
        "q_en": "What payment model do you prefer in games? Skin purchases, battle pass, or free with ads? What's the most you'd spend? Answer in 2-3 sentences.",
    },
    {
        "id": "Q3_social",
        "theme": "社交機制",
        "q_zh": "你最希望遊戲裡有什麼社交功能？比如組隊、語音、好友系統、公會、還是其他？用兩三句話回答",
        "q_en": "What social features do you want most in a party game? Team-up, voice chat, friend system, guilds, or something else? Answer in 2-3 sentences.",
    },
    {
        "id": "Q4_web3",
        "theme": "Web3態度",
        "q_zh": "如果這個遊戲用區塊鏈技術讓你的遊戲資產(皮膚、角色)真正屬於你，可以自由交易，你覺得怎樣？你擔心什麼？用三四句話回答",
        "q_en": "If this game used blockchain so your game assets (skins, characters) truly belong to you and can be freely traded, what do you think? What concerns you? Answer in 3-4 sentences.",
    },
    {
        "id": "Q5_stress",
        "theme": "壓力釋放",
        "q_zh": "你平時工作/學業壓力大的時候會用什麼方式放鬆？遊戲在你的減壓方式裡排第幾？用兩三句話回答",
        "q_en": "How do you relax when stressed from work or school? Where does gaming rank in your stress relief methods? Answer in 2-3 sentences.",
    },
    {
        "id": "Q6_hk_culture",
        "theme": "香港文化",
        "q_zh": "牛馬派對融入了香港打工文化(紅VAN、牛馬、加班)，你覺得這種本土文化融入遊戲有吸引力嗎？會讓你更想玩嗎？用兩三句話回答",
        "q_en": "NiuMa Party incorporates Hong Kong work culture (red minibus, overwork slang). Do you find local cultural elements in games attractive? Would it make you want to play more? Answer in 2-3 sentences.",
    },
]

def ask(model, prompt):
    try:
        resp = requests.post(API, json={
            "model": model, "prompt": prompt, "stream": False,
        }, timeout=180)
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"(Error: {e})"

def main():
    results = []
    total = len(PERSONAS) * len(QUESTIONS)
    done = 0

    print(f"Running {total} interviews...\n")

    for q in QUESTIONS:
        print(f"{'='*60}")
        print(f"  {q['id']}: {q['theme']}")
        print(f"{'='*60}")

        for model, name, region, desc in PERSONAS:
            done += 1
            prompt = q["q_en"] if model == "jake" else q["q_zh"]
            print(f"  [{done}/{total}] Asking {name}...", end="", flush=True)

            answer = ask(model, prompt)
            print(f" done ({len(answer)} chars)")

            # Print answer
            print(f"    [{region}] {name}: {answer[:200]}")
            if len(answer) > 200:
                print(f"    ...({len(answer)} chars total)")
            print()

            results.append({
                "question_id": q["id"],
                "theme": q["theme"],
                "question": prompt,
                "persona_id": model,
                "persona_name": name,
                "region": region,
                "persona_desc": desc,
                "answer": answer,
                "answer_len": len(answer),
                "timestamp": datetime.now().isoformat(),
            })

    # Save CSV
    out_csv = BASE + "persona_interview_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    # Save markdown report
    out_md = BASE + "persona_interview_report.md"
    lines = []
    lines.append("# 牛馬派對 AI Persona 設計驗證報告")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> Models: Ollama llama3 x4 personas")
    lines.append(f"> Questions: {len(QUESTIONS)} | Personas: {len(PERSONAS)} | Total: {total}")
    lines.append("")

    for q in QUESTIONS:
        lines.append(f"---")
        lines.append(f"## {q['id']}: {q['theme']}")
        lines.append(f"**{q['q_zh']}**")
        lines.append("")

        q_results = [r for r in results if r["question_id"] == q["id"]]
        for r in q_results:
            lines.append(f"### [{r['region']}] {r['persona_name']} ({r['persona_desc']})")
            lines.append(f"> {r['answer']}")
            lines.append("")

        # Cross-persona comparison
        lines.append("### 比較分析")
        # Simple comparison
        answers = {r["persona_id"]: r["answer"] for r in q_results}
        len_parts = ', '.join(f'{r["persona_name"]}={r["answer_len"]}字' for r in q_results)
        lines.append(f"- 回應長度: {len_parts}")
        lines.append("")

    # Final summary section
    lines.append("---")
    lines.append("## 綜合洞察")
    lines.append("")
    lines.append("### 各 Persona 對牛馬派對的態度")
    lines.append("| Persona | 核心玩法 | 付費 | 社交 | Web3 | 壓力釋放 | 港文化 |")
    lines.append("|---------|---------|------|------|------|---------|--------|")
    for model, name, region, desc in PERSONAS:
        my = [r for r in results if r["persona_id"] == model]
        row = f"| {name} |"
        for r in my:
            # Extract first sentence as summary
            first = r["answer"].split(".")[0].split("!")[0].split("。")[0][:30]
            row += f" {first}... |"
        lines.append(row)
    lines.append("")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n{'='*60}")
    print(f"  CSV  -> {out_csv}")
    print(f"  報告 -> {out_md}")
    print(f"  Total: {len(results)} responses")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
