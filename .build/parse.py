import re, json, sys
sys.path.insert(0, "/tmp/claude-0/prog/build")
from kjoin import join as KJ
src = open(sys.argv[1], encoding="utf-8").read()
BOXK = ["시험 포인트", "쉬운 예", "실제 사례", "예제", "정답·해설", "해설", "모범답안"]
CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
HANG = re.compile(r"[가-힣]")
parts = []; part = None; sec = None; last = None; blank = 0; pb = False
def newpart(title):
    global part, sec, last
    part = {"title": title, "secs": []}; parts.append(part); sec = None; last = None
def add(b):
    global last
    if sec is None: return
    sec["blocks"].append(b); last = b
def join(a, b):
    if not a: return b
    if a.endswith(("(", "“", '"', "·", "/", "-")): return a + b
    A, B = a.split()[-1], b.split()[0]
    # 한글 단어가 줄 끝에서 잘린 경우는 붙이고, 아니면 띄운다
    if HANG.match(A[-1]) and HANG.match(B[0]):
        if B.startswith(("다.", "다,", "니다", "이다", "한다", "된다", "있다", "없다")) or len(B) == 1 or (len(re.sub(r"[^가-힣]", "", B)) <= 2 and not re.search(r"[은는이가을를의에와과로도만]$", A)):
            return a + b
    return a + " " + b
pages = src.split("\f")
for pi, pg in enumerate(pages):
    if pi < 16: continue            # 표지·목차
    pb = True
    for raw in pg.split("\n"):
        if not raw.strip(): blank += 1; continue
        s = raw.rstrip(); st = s.strip(); ind = len(s) - len(s.lstrip(" "))
        if st.startswith("프로그래밍기능사 통합 정리서") or re.fullmatch(r"\d{1,3}", st): continue
        b0 = 0 if pb else blank; blank = 0; wasPb = pb; pb = False
        m = re.fullmatch(r"(PART [AB]\. .+|시작하기 · .+|부록 · .+)", st)
        if m and 3 <= ind <= 10 and ". . ." not in st:
            if not part or part["title"] != st: newpart(st)
            continue
        m = re.fullmatch(r"제(\d+)절 (.+)", st)
        if m and ind <= 2 and part is not None:
            sec = {"n": int(m.group(1)), "title": m.group(2).strip(), "blocks": []}; part["secs"].append(sec); last = None; continue
        if sec is None: continue
        if re.match(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s", st) and ind <= 1: add({"t": "h2", "x": st}); continue
        if re.match(r"\d+\.\s", st) and 1 <= ind <= 2 and not (last and last["t"] == "code"): add({"t": "h3", "x": st}); continue
        if re.match(r"\(\d+\)\s", st) and 2 <= ind <= 3: add({"t": "h4", "x": st}); continue
        if st[0] in CIRC and 2 <= ind <= 4: add({"t": "li", "x": st}); continue
        bx = next((k for k in BOXK if st.startswith(k + " ")), None)
        if bx and 3 <= ind <= 6 and not (last and last["t"] == "code" and b0 == 0):
            add({"t": "box", "k": bx, "x": st[len(bx) + 1:].strip()}); continue
        # 이어지는 줄
        if last:
            if last["t"] == "code" and ind >= 4 and b0 <= 2 and not (HANG.search(st) and ind == 5 and not re.search(r"[;{}()=#\[\]:<>\"']", st)):
                last["x"] += "\n" * (b0 + 1) + s[4:]; continue
            if last["t"] == "box" and b0 == 0 and ind >= 3: last["x"] = KJ(last["x"], st); continue
            if last["t"] == "li" and b0 == 0 and ind >= 4: last["x"] = KJ(last["x"], st); continue
            if last["t"] == "p" and b0 <= 1 and ind >= 4 and ind == last.get("i", ind): last["x"] = KJ(last["x"], st); continue
        if ind == 4 and (not HANG.search(st) or re.search(r"[;{}()=#\[\]]", st)):
            add({"t": "code", "x": s[4:]}); continue
        add({"t": "p", "x": st, "i": ind})
for p in parts:
    for s in p["secs"]:
        for b in s["blocks"]:
            b.pop("i", None)
            if b["t"] == "code": b["x"] = b["x"].rstrip("\n")
json.dump(parts, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
tot = {}
for p in parts:
    c = {}
    for s in p["secs"]:
        for b in s["blocks"]: c[b["t"]] = c.get(b["t"], 0) + 1
    print(p["title"][:40], len(p["secs"]), c)
