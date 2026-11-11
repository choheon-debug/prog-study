import json, re
B = json.load(open("/tmp/claude-0/prog/book.json"))
W = json.load(open("/tmp/claude-0/prog/w.json"))
S = json.load(open("/tmp/claude-0/prog/s.json"))
for s in S:
    # 문제 문장이 두 번 반복되면 한 번만
    lines = s["q"].split("\n")
    if len(lines) > 1 and lines[-1] in " ".join(lines[:-1]): lines = lines[:-1]
    s["q"] = "\n".join(lines)
    s["g"] = "C" if s["type"].startswith("C ") else "J" if s["type"].startswith("Java") else "Y" if s["type"].startswith("Python") else "Q" if s["type"].startswith("SQL") else "T"
C = []
for i, ln in enumerate(open("/tmp/claude-0/prog/build/cards.txt", encoding="utf-8").read().strip().split("\n")):
    d, f, b = ln.split("|"); C.append({"id": f"k{i+1:03d}", "d": d, "f": f, "b": b.split(";;")})
parts = [{"t": p["title"], "s": [{"n": s["n"], "t": s["title"], "b": s["blocks"]} for s in p["secs"]]} for p in B]
hdr = "// 「프로그래밍기능사 통합 정리서·필기 모의고사집·실기 모의고사집」(2026년 11월 8일 기준) 내용\n"
open("/home/user/prog-study/qs.js", "w", encoding="utf-8").write(hdr + "window.WQ=" + json.dumps(W, ensure_ascii=False, separators=(",", ":")) + ";\nwindow.SQ=" + json.dumps(S, ensure_ascii=False, separators=(",", ":")) + ";\nwindow.CARDS=" + json.dumps(C, ensure_ascii=False, separators=(",", ":")) + ";\n")
open("/home/user/prog-study/book.js", "w", encoding="utf-8").write(hdr + "window.BOOK=" + json.dumps(parts, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(len(W), len(S), len(C), [ (p["t"][:20], len(p["s"])) for p in parts][:3])
