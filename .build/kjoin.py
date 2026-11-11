# 줄바꿈으로 잘린 한글 단어를 다시 붙이는 도구 (세탁기능사 때 쓴 규칙)
import re, collections
_st = lambda w: re.sub(r"[^0-9A-Za-z가-힣]", "", w)
VOC = collections.Counter()
for ln in open("/tmp/claude-0/prog/pdf/all.txt", encoding="utf-8"):
    t = ln.split()
    for w in t[1:-1]: VOC[_st(w)] += 1
END = "게고며면서는은을를의에와과로도만나이가요지해"
hang = lambda c: "가" <= c <= "힣"
def join(a, b):
    if not a: return b
    if a.endswith(("(", "“", '"', "·", "/", "-", "~")): return a + b
    A, B = a.split()[-1], b.split()[0]
    if hang(A[-1]) and hang(B[0]):
        sA, sB = _st(A), _st(B)
        if VOC[sA + sB] > VOC[sA] + VOC[sB] or _st(A + B.split('"')[0]) in VOC and VOC[sB] == 0: return a + b
        if B.startswith(("입니다", "이다", "니다", "다.", "다,", "습니다", "된다", "한다")): return a + b
        if len(sB) == 1 and sB in "지다요고게며서도에를은는이가의로": return a + b
        if len(sA) >= 3 and sA[-1] in END: return a + " " + b
        if VOC[sA] and VOC[sB]: return a + " " + b
        if not VOC[sB]: return a + b
    return a + " " + b
