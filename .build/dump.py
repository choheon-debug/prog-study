import json,sys
P=json.load(open(sys.argv[1])); pi,si=int(sys.argv[2]),int(sys.argv[3]); a,b=int(sys.argv[4]),int(sys.argv[5])
s=P[pi]["secs"][si]; print("##",P[pi]["title"],"/ 제%d절"%s["n"],s["title"])
for x in s["blocks"][a:b]:
    if x["t"]=="code": print("```\n"+x["x"]+"\n```")
    elif x["t"]=="box": print(f"[{x['k']}] {x['x']}")
    else: print({"h2":"### ","h3":"#### ","h4":"- ","li":"","p":"  "}[x["t"]]+x["x"])
