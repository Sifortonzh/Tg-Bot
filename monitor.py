KEYWORDS = ["合租", "Netflix", "Apple Music", "iCloud", "拼车", "上车", "共享", "会员"]

def check_keywords(text):
    hits = [kw for kw in KEYWORDS if kw in text]
    return ", ".join(hits) if hits else None
