# Ollama UX Personas

> Data-backed AI persona agents for automated UX research — 6 locally-deployed Ollama models representing real user archetypes.

## Overview

Traditional UX research creates static persona documents. This project turns personas into **live AI agents** you can interview, test with, and iterate against — all running locally on Ollama.

**Tech Stack**: Ollama + Llama 3/3.2 + Mistral + Python

## Persona Agents

| Agent | Archetype | Background |
|-------|-----------|------------|
| **Ming** | HK UI/UX Designer | 28yo, stressed from deadlines, uses games for emotional relief |
| **Jake** | International Gamer | 18-28yo, fun-focused, skeptical of NFT games |
| **Chen** | Mainland IT Worker | 22-30yo, 996 overtime, values fairness and social connection |
| **Mirror** | Jungian Reflective AI | Therapeutic persona based on analytical psychology |
| **Shangguan** | DBT Emotional AI | Mental health support based on Dialectical Behavior Therapy |
| **Yu** | Additional persona | Extended user archetype |

## How It Works

1. Each persona is defined as an Ollama Modelfile with detailed system prompts derived from real user data (1,012 game reviews)
2. `persona_chat.py` — Interactive 1-on-1 conversation with any persona
3. `persona_batch_interview.py` — Automated batch interviews across all personas

## Usage

```bash
# Create a persona model
ollama create ming -f modelfiles/Modelfile.ming

# Interactive chat
python persona_chat.py --persona ming

# Batch interview all personas
python persona_batch_interview.py
```

## Data Foundation

These personas are NOT fictional — they are synthesized from:
- 1,012 multilingual game reviews (Steam/LIHKG/Bahamut/Threads)
- NLP sentiment analysis across 3 languages
- 784-word in-depth Hong Kong player testimonial
- Affinity mapping and competitive analysis

See [niuma-nlp-research](https://github.com/naturejx-source/niuma-nlp-research) for the full dataset.

## Related Repositories

- [niuma-nlp-research](https://github.com/naturejx-source/niuma-nlp-research) — Source data for persona generation
- [cangjie-ai](https://github.com/naturejx-source/cangjie-ai) — Another Ollama-based AI assistant
- [niuma-party-godot](https://github.com/naturejx-source/niuma-party-godot) — The game these personas test

## Author

**WU, JINXIA (Rucia Woo)** — BSc Software Engineering | AI-Augmented UX Researcher
