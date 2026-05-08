"""
牛馬派對 AI Persona 面板
用 Ollama 本地模型模擬 4 個用戶角色
可以對每個角色提同一個問題，比較不同用戶群的回應

用法:
  python persona_chat.py                    # 互動模式
  python persona_chat.py --ask "你的問題"    # 一次問所有人
  python persona_chat.py --who ming         # 只跟阿明聊
"""
import requests, json, sys, io, argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API = "http://localhost:11434/api/generate"

PERSONAS = {
    "ming": {"name": "阿明 Ming", "desc": "28歲香港設計師 | 粵語 | 情感治癒派", "icon": "HK"},
    "chen": {"name": "小陳 Chen", "desc": "24歲深圳工程師 | 簡中 | 技術分析派", "icon": "CN"},
    "jake": {"name": "Jake",      "desc": "22歲美國大學生 | English | 休閒社交派", "icon": "US"},
    "yu":   {"name": "小雨 Yu",   "desc": "23歲台灣行銷 | 繁中 | 社群歸屬派",   "icon": "TW"},
}

def ask_persona(model, prompt, timeout=120):
    try:
        resp = requests.post(API, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        }, timeout=timeout)
        data = resp.json()
        return data.get("response", "(no response)")
    except requests.exceptions.ConnectionError:
        return "(Ollama 未啟動 — 請先執行 ollama serve)"
    except Exception as e:
        return f"(Error: {e})"

def ask_all(prompt):
    print(f"\n{'='*60}")
    print(f"  問題: {prompt}")
    print(f"{'='*60}")
    for key, info in PERSONAS.items():
        print(f"\n  [{info['icon']}] {info['name']} ({info['desc']})")
        print(f"  {'─'*50}")
        answer = ask_persona(key, prompt)
        # Indent answer
        for line in answer.strip().split('\n'):
            print(f"  {line}")
    print(f"\n{'='*60}\n")

def chat_one(who):
    info = PERSONAS[who]
    print(f"\n  正在和 {info['name']} 對話 (輸入 quit 退出)")
    print(f"  {info['desc']}\n")
    while True:
        try:
            q = input(f"  你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ('quit', 'exit', 'q'):
            break
        answer = ask_persona(who, q)
        print(f"\n  {info['name']}: {answer}\n")

def interactive():
    print(f"""
  ╔══════════════════════════════════════════════╗
  ║   牛馬派對 AI Persona 面板                    ║
  ║   4 個用戶角色，本地 Ollama 驅動              ║
  ╚══════════════════════════════════════════════╝

  指令:
    all  <問題>    問所有人同一個問題 (比較回應)
    ming <問題>    只問阿明 (香港設計師)
    chen <問題>    只問小陳 (深圳工程師)
    jake <問題>    只問 Jake (美國大學生)
    yu   <問題>    只問小雨 (台灣行銷)
    chat <名字>    進入單人對話模式
    quit           退出
""")
    while True:
        try:
            cmd = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd or cmd.lower() in ('quit', 'exit', 'q'):
            break

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()

        if action == 'all' and len(parts) > 1:
            ask_all(parts[1])
        elif action == 'chat' and len(parts) > 1:
            who = parts[1].lower()
            if who in PERSONAS:
                chat_one(who)
            else:
                print(f"  未知角色: {who} (可選: ming/chen/jake/yu)")
        elif action in PERSONAS and len(parts) > 1:
            info = PERSONAS[action]
            print(f"\n  [{info['icon']}] {info['name']}:")
            answer = ask_persona(action, parts[1])
            print(f"  {answer}\n")
        else:
            # Default: ask all
            ask_all(cmd)

def main():
    parser = argparse.ArgumentParser(description="牛馬派對 AI Persona Chat")
    parser.add_argument("--ask", type=str, help="問所有 Persona 一個問題")
    parser.add_argument("--who", type=str, choices=["ming","chen","jake","yu"], help="指定角色")
    args = parser.parse_args()

    if args.ask:
        if args.who:
            info = PERSONAS[args.who]
            print(f"\n  [{info['icon']}] {info['name']}:")
            print(f"  {ask_persona(args.who, args.ask)}\n")
        else:
            ask_all(args.ask)
    else:
        interactive()

if __name__ == "__main__":
    main()
