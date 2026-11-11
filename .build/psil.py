import re, json, sys
sys.path.insert(0, "/tmp/claude-0/prog/build")
from kjoin import join as KJ
sys.path.insert(0, "/tmp/claude-0/prog/build")
HANG = re.compile(r"[가-힣]")
L = []
for pg in open(sys.argv[1], encoding="utf-8").read().split("\f"):
    for ln in pg.split("\n"):
        st = ln.strip()
        if st.startswith("프로그래밍기능사 실기 모의고사집") or re.fullmatch(r"\d{1,3}", st): continue
        L.append(ln.rstrip())
R = {}; r = None; mode = None; q = None; cur = None; blank = 0
for ln in L:
    st = ln.strip(); ind = len(ln) - len(ln.lstrip())
    if not st: blank += 1; continue
    b0, blank = blank, 0
    m = re.fullmatch(r"제(\d)절 실기 모의고사 제(\d)회", st)
    if m: r = int(m.group(2)); R[r] = {}; mode = "q"; continue
    if r is None: continue
    if st == "Ⅱ. 배점표와 모범답안": mode = "x"; continue
    if mode == "x" and st.startswith("2. 모범답안"): mode = "a"; continue
    if mode == "q":
        m = re.fullmatch(r"문제 (\d+) \[(.+?)\] \(배점 (\d+)점\)", st)
        if m: q = {"n": int(m.group(1)), "type": m.group(2), "pt": int(m.group(3)), "q": "", "code": "", "a": "", "acode": "", "e": ""}; R[r][q["n"]] = q; cur = None; continue
        if not q or re.match(r"\d+\. .+ 영역$", st): continue
        if st.startswith("답: ") or re.fullmatch(r"답:\s*_+", st): cur = None; continue
        if ind == 4 or (cur == "code" and ind > 4 and not (HANG.search(st) and not re.search(r"[;{}()=#\[\]\"'<>]", st) and ind >= 5 and ind <= 9 and not q["code"].endswith("\n") and False)):
            if cur == "code" or not HANG.search(st) or re.search(r"[;{}()=#\[\]]", st):
                if not (cur != "code" and ind > 4):
                    q["code"] += ("\n" * (min(b0, 1) + 1) if q["code"] else "") + ln[4:]; cur = "code"; continue
        q["q"] = KJ(q["q"], st) if cur == "q" and b0 == 0 else (q["q"] + ("\n" if q["q"] else "") + st); cur = "q"
    elif mode == "a":
        m = re.fullmatch(r"모범답안 문제 (\d+) \[.+?\] \(\d+점\)", st)
        if m: q = R[r][int(m.group(1))]; cur = None; continue
        if not q: continue
        m2 = re.match(r"답\s?(?!:)(.+)", st)
        if m2 and not st.startswith("답:"): q["a"] = m2.group(1).strip(); cur = "a"; continue
        if st.startswith("해설 "): q["e"] = st[3:].strip(); cur = "e"; continue
        if cur == "e" and b0 == 0: q["e"] = KJ(q["e"], st); continue
        if cur in ("a", "ac") and ind >= 4:
            q["acode"] += ("\n" * (min(b0, 1) + 1) if q["acode"] else "") + ln[4:]; cur = "ac"; continue
S = []
for rn, qs in sorted(R.items()):
    for n, q in sorted(qs.items()):
        for k in ("code", "acode"): q[k] = q[k].strip("\n")
        cl = q["code"].split("\n")
        tail = []
        while cl and HANG.search(cl[-1]) and re.search(r"(쓰시오|오\.|\?)\s*$", cl[-1]) and not re.search(r"[;{}]", cl[-1]): tail.insert(0, cl.pop().strip())
        q["code"] = "\n".join(cl).strip("\n"); 
        if tail: q["q"] = (q["q"] + "\n" if q["q"] else "") + "\n".join(tail)
        if q["a"].startswith("모범답안은 아래"): q["a"] = ""
        S.append({"id": f"s{rn}-{n:02d}", "r": rn, **q})
print("실기", len(S), [x["id"] for x in S if not (x["a"] or x["acode"]) or not x["e"]])
json.dump(S, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
