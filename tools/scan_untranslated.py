import json, pathlib, re, sys

repo = pathlib.Path(__file__).resolve().parent.parent
CYR = set(range(0x0400, 0x0500))
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`]*`")


def cyr(text):
    return any(ord(c) in CYR for c in text)


findings = []
for p in sorted((repo / "skills").rglob("*.md")):
    rel = p.relative_to(repo).as_posix()
    text = p.read_text(encoding="utf-8", errors="replace")
    body = INLINE.sub(" ", FENCE.sub(" ", text))
    # strip frontmatter
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end > 0:
            body = body[end + 4:]
    for i, line in enumerate(body.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "- ", "* ", "1.")):
            # allow headings only if they have cyrillic or are short
            pass
        words = re.findall(r"[A-Za-z][A-Za-z'\-]+", s)
        if len(words) >= 8 and not cyr(s):
            findings.append({"file": rel, "line": i, "text": s[:160]})

print(json.dumps(findings[:40], ensure_ascii=False, indent=1))
print("подозрительных строк:", len(findings))
