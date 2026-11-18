#!/usr/bin/env python3
"""Merge src/curated.json with the newest contacts from the outreach trackers.

The networking job keeps appending verified contacts and drafts to the
"24-hour networking run" sections of
  ../philippines-outreach-2026-11-17.md
  ../japan-outreach-2026-11-17.md
This script reads every draft there (**Name @handle** followed by > lines),
skips anyone already in curated.json, and writes src/data.json, the single
file the page renders from.

Privacy: only names, public handles, public profile/booking links and the
drafts are carried over. Phone numbers and email addresses in the trackers
are never copied.
Run: python3 src/import_outreach.py
"""
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
PROJECTS = SITE.parent
FILES = {"ph": PROJECTS / "philippines-outreach-2026-11-17.md", "jp": PROJECTS / "japan-outreach-2026-11-17.md"}

# Short "City · role" lines for contacts the job has already added.
# New handles not listed here fall back to what the tracker table says.
ROLES = {
    "tennisnomad": ("Cebu", "Traveling tennis creator"),
    "g2play_tennis": ("Pasig", "Courts and open plays"),
    "coachwaldobernardo": ("Manila", "Open Play & Away coach"),
    "kamon": ("Antipolo", "Matchplay nights"),
    "philta_official": ("Manila", "National federation"),
    "vey": ("Manila", "Manila Tennis Enthusiasts admin"),
    "cots.jr.flores": ("Pasig", "Pasig City head coach"),
    "anotherdayanothercourt": ("Manila", "Creator, open plays"),
    "the.tennisloft": ("Cebu", "Ball machine court, IT Park"),
    "coach.jedaquino": ("Quezon City", "Serve & Beyond coach"),
    "jjktennis": ("Manila", "Tour coach"),
    "gamepoint.tennis": ("Parañaque", "Indoor court"),
    "austennis_": ("Makati", "Pro coach, game nights"),
    "faye_oncourt": ("Manila", "ITF coach"),
    "aryoncourt": ("Manila", "Tennis creator"),
    "dropshot.ph": ("Manila", "Tennis photographers"),
    "tennishub_100": ("Pasig", "New courts"),
    "asmaraurbanresort": ("Cebu", "Asmara Open host"),
    "tipsytennispodcast": ("Cebu", "Traveling creator"),
    "citigreentennisresort": ("Cebu", "Red clay court"),
    "openplayandaway": ("Philippines", "Tennis retreats, match days"),
    "gentry_open": ("Manila", "Open tournament"),
    "tennismnl": ("Manila", "Rec tournaments"),
    "7_7_shin": ("Tokyo", "Movement coach"),
    "ta1_saito": ("Saitama", "UTR Pro Tour player"),
    "ctc.chitose_tennis_club": ("Setagaya", "Tennis school"),
    "chikayasato": ("Tokyo", "Player"),
    "erikasematennis": ("Tokyo", "Pro, All-Japan champion"),
    "godaikameido": ("Kameido", "Indoor school"),
    "t_socialt": ("Tokyo", "All-Japan qualifier, creator"),
    "salute_tennis": ("Tokyo", "Competitive academy"),
    "uno_maaya": ("Tokyo", "Former pro, events"),
    "amechan_59": ("Tokyo", "Tennis creator"),
    "mieri_yao": ("Shibuya", "Tennis creator"),
    "nanagram_128": ("Tokyo", "THE CLUBHOUSE creator"),
    "komae_indoor_tennis_school": ("Komae", "Indoor school"),
    "tennis.boys.tokyo": ("Tokyo", "20s-30s community"),
    "will.tennis25": ("Tokyo", "Social circle"),
    "otona_tennis.summer_flat": ("Koto", "Social circle"),
    "sketch2_tennis": ("Kameido", "Social circle"),
    "tautenikun": ("Nerima", "Club and school"),
    "epsom_tennis": ("Koto", "Pro hitting sessions"),
    "yuya_045": ("Tokyo", "Coach, Tennis Pot"),
    "ryusei__tennis": ("Tokyo", "Pro, English lessons"),
    "utr_protennistour_japan": ("Kanto", "Prize-money tour"),
    "ryotatanuma_tennis": ("Japan", "Pro, private lessons"),
    "raimu__.4": ("Yokohama", "Traveling coach"),
    "chuouniv_tennis": ("Tokyo", "Chuo University varsity team"),
    "agu_tennis": ("Shibuya", "Aoyama Gakuin varsity team"),
    "nodai_tennis_man": ("Setagaya", "Tokyo Nodai varsity team"),
}
NAMES = {"tennis.boys.tokyo": "Tennis Boys Tokyo", "t_socialt": "t_social", "kamon": "KAMON! Tennis", "vey": "Vey", "chuouniv_tennis": "Chuo University tennis team", "agu_tennis": "Aoyama Gakuin tennis team", "nodai_tennis_man": "Tokyo Nodai men's tennis"}
CITY_WORDS = ["Manila", "Cebu", "Pasig", "Makati", "Parañaque", "Antipolo", "Quezon City", "Siargao",
              "Setagaya", "Shibuya", "Koto", "Kameido", "Nerima", "Komae", "Yokohama", "Saitama", "Tokyo"]
FB = re.compile(r"https://www\.facebook\.com/[\w.]+/?")


def section(text):
    m = re.search(r"^## 24-hour networking run.*?(?=^## (?!#))", text, re.S | re.M)
    return m.group(0) if m else ""


def table_rows(sec):
    rows = {}
    for line in sec.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        handles = re.findall(r"instagram\.com/([\w.]+)/", cells[2])
        fb = FB.findall(cells[2])
        row = {"person": cells[1], "facts": cells[3], "fb": fb[0] if fb else None}
        for h in handles:
            rows[h] = row
        if fb:
            rows[fb[0]] = row
    return rows


def drafts(sec):
    out = []
    lines = sec.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", lines[i])
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if m and j < len(lines) and lines[j].startswith(">"):
            label, note = m.group(1), m.group(2)
            body = []
            i = j
            while i < len(lines) and lines[i].startswith(">"):
                body.append(lines[i][1:].strip())
                i += 1
            text = "\n".join(body).strip()
            text = re.sub(r"\n{3,}", "\n\n", text)
            hm = re.search(r"@([\w.]+)", label)
            out.append({"label": label, "handle": hm.group(1) if hm else None,
                        "name": re.sub(r"\s*@[\w.]+", "", label).strip(), "note": note, "send": text})
            continue
        i += 1
    return out


def clean_name(name, handle):
    if handle in NAMES:
        return NAMES[handle]
    if handle and not name:
        return handle
    return name.split(",")[0].strip()


def build_entry(list_key, d, rows):
    h = d["handle"]
    row = rows.get(h) if h else None
    key = h
    if not h:
        low = d["label"].lower()
        key = "kamon" if "kamon" in low else "vey" if "vey" in low else re.sub(r"\W+", "-", low).strip("-")
        row = next((r for k, r in rows.items() if k.startswith("https://") and (
            ("kamon" in k and key == "kamon") or ("vee.amb" in k and key == "vey"))), None)
    city, role = ROLES.get(key, (None, None))
    if not city:
        facts = (row or {}).get("facts", "") + " " + (row or {}).get("person", "")
        city = next((c for c in CITY_WORDS if c in facts), "Tokyo" if list_key == "jp" else "Philippines")
        pm = re.search(r"\(([^)]+)\)", (row or {}).get("person", ""))
        role = pm.group(1) if pm else "New contact"
    links = []
    if h:
        links.append({"label": "Instagram", "url": f"https://ig.me/m/{h}"})
    elif row and row.get("fb"):
        links.append({"label": "Facebook", "url": row["fb"]})
    if key == "kamon":
        links.append({"label": "Reclub", "url": "https://reclub.co/clubs/@kamon"})
    status = None
    note = d["note"].lower()
    if "confirm" in note:
        status = "Confirm city"
    img = f"{h}.jpg" if h and (SITE / "public" / "img" / f"{h}.jpg").exists() else None
    e = {"id": f"{list_key}-{key}", "name": NAMES.get(key) or clean_name(d["name"], h), "city": city, "role": role,
         "action": "SEND", "send": d["send"], "links": links, "new": True}
    if h:
        e["handle"] = h
    if img:
        e["img"] = img
    if status:
        e["status"] = status
    return e


def main():
    data = json.loads((SITE / "src" / "curated.json").read_text())
    added = {}
    for key, path in FILES.items():
        sec = section(path.read_text())
        rows = table_rows(sec)
        known = {x.get("handle") for x in data[key]} | {x["id"] for x in data[key]}
        new = []
        for d in drafts(sec):
            e = build_entry(key, d, rows)
            if (e.get("handle") and e["handle"] in known) or e["id"] in known:
                continue
            known.add(e.get("handle"))
            known.add(e["id"])
            new.append(e)
        data[key].extend(new)
        added[key] = len(new)
    blob = json.dumps(data, ensure_ascii=False, indent=1)
    for k in ("ph", "jp"):
        for x in data[k]:
            for l in x["links"]:
                assert not l["url"].startswith("tel:") or x["id"] in ("asmara",), x["id"]
    (SITE / "src" / "data.json").write_text(blob + "\n")
    print(f"imported new: {added}; totals ph {len(data['ph'])}, jp {len(data['jp'])}, plan {len(data['plan'])}")
    missing = [x.get("handle") for k in ("ph", "jp") for x in data[k] if x.get("handle") and not x.get("img")]
    print("no image yet:", " ".join(missing))


if __name__ == "__main__":
    main()
