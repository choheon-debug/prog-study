import re, json, sys
sys.path.insert(0, "/tmp/claude-0/prog/build")
from kjoin import join as KJ
HANG = re.compile(r"[가-힣]")
C4 = "①②③④"
def pages(fn, hdr):
    out = []
    for pg in open(fn, encoding="utf-8").read().split("\f"):
        for ln in pg.split("\n"):
            st = ln.strip()
            if st.startswith(hdr) or re.fullmatch(r"\d{1,3}", st): continue
            out.append(ln.rstrip())
    return out
# ---------- 필기 ----------
L = pages(sys.argv[1], "프로그래밍기능사 필기 모의고사집")
rounds = {}; r = None; mode = None; q = None; cur = None; blank = 0; ex = None
for ln in L:
    st = ln.strip(); ind = len(ln) - len(ln.lstrip())
    if not st: blank += 1; continue
    b0, blank = blank, 0
    m = re.fullmatch(r"제(\d)절 필기 모의고사 제(\d)회", st)
    if m: r = int(m.group(2)); rounds[r] = {}; mode = "q"; q = None; continue
    if r is None: continue
    if st == "Ⅱ. 정답 및 해설": mode = "a"; continue
    if mode == "q":
        m = re.fullmatch(r"문제 (\d+)", st)
        if m: q = {"n": int(m.group(1)), "code": "", "q": "", "o": []}; rounds[r][q["n"]] = q; cur = None; continue
        if not q or re.match(r"\d+\. \d과목", st) or re.match(r"^[ⅠⅡ]\.", st): continue
        if st[0] in C4 and ind <= 4: q["o"].append(st[1:].strip()); cur = "o"; continue
        if cur == "o" and ind >= 4 and b0 == 0: q["o"][-1] = KJ(q["o"][-1], st); continue
        if ind == 4 or (cur == "code" and ind >= 4 and not (ind >= 7 and HANG.search(st) and not re.search(r"[;{}()=#\[\]\"']", st))):
            if ind >= 4 and (cur == "code" or not HANG.search(st) or re.search(r"[;{}()=#\[\]]", st)) and not (ind >= 7 and cur != "code"):
                q["code"] += ("\n" * (min(b0, 1) + 1) if q["code"] else "") + ln[4:]; cur = "code"; continue
        q["q"] = KJ(q["q"], st) if cur == "q" and b0 <= 1 else (q["q"] + ("\n" if q["q"] else "") + st); cur = "q"
    else:
        m = re.match(r"정답·해설 (\d+)번 정답 ([①②③④])\s*(.*)", st)
        if m: ex = rounds[r][int(m.group(1))]; ex["a"] = C4.index(m.group(2)); ex["e"] = m.group(3); continue
        if ex and b0 == 0 and not st.startswith(("정답·해설", "1. 정답표")) and not re.match(r"\d+\. \d과목", st) and not re.match(r"번호|\d+\s+[①②③④]", st):
            ex["e"] = KJ(ex["e"], st)
        else: ex = None
W = []
SUB = lambda n: "PASI"[(n - 1) // 15]
for rn, qs in sorted(rounds.items()):
    for n, q in sorted(qs.items()):
        q["code"] = q["code"].strip("\n")
        cl = q["code"].split("\n")
        while cl and HANG.search(cl[-1]) and cl[-1].startswith(" ") and re.search(r"[?.]\s*$", cl[-1]) and not re.search(r"[;{}]", cl[-1]):
            q["q"] = cl.pop().strip() + ("\n" + q["q"] if q["q"] else ""); 
        q["code"] = "\n".join(cl).strip("\n")
        W.append({"id": f"w{rn}-{n:02d}", "r": rn, "n": n, "s": SUB(n), "q": q["q"].strip(), "code": q["code"], "o": q["o"], "a": q.get("a"), "e": q.get("e", "")})
bad = [w["id"] for w in W if len(w["o"]) != 4 or w["a"] is None or not w["q"]]
print("필기", len(W), "문제, 이상:", bad[:20])
json.dump(W, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False)
