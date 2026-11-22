#!/usr/bin/env python3
"""
Blog cover images — free CC0 photos download karke 960x504 me crop karta hai.

    python3 src/fetch_images.py                 # jin posts ki image nahi hai, unke liye laao
    python3 src/fetch_images.py --redo slug1 slug2   # in posts ki image badlo (agla candidate)

Source: Openverse API (api.openverse.org) — sirf CC0 license, WordPress Photo Directory (wordpress.org/photos).
CC0 = public domain: commercial use allowed, attribution zaroori nahi (phir bhi credit record karte hain).
Result: assets/blog/<slug>.jpg  +  src/content/blog-images.json (source, creator, license).
Image resize/crop macOS ke `sips` se hota hai.
Apni khud ki image lagani ho: assets/blog/<slug>.jpg (960x504) rakho aur JSON me "locked": true kar do.
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT_DIR = os.path.join(ROOT, "assets", "blog")
META = os.path.join(SRC, "content", "blog-images.json")
W, H = 960, 504
UA = "vetra-site-image-fetch/1.0"

# slug -> search query (English stock-photo keywords)
QUERIES = {
    # CRM / leads / WhatsApp (existing posts)
    "what-is-crm": "business laptop", "best-crm-software-india": "laptop office work",
    "crm-software-price-india": "calculator money", "cloud-vs-self-hosted-crm": "server room",
    "excel-to-crm": "spreadsheet laptop", "crm-roles-permissions-audit-logs": "security lock",
    "crm-for-manufacturers": "factory", "crm-for-distributors-wholesalers": "warehouse boxes",
    "crm-for-ecommerce-business": "online shopping laptop", "crm-for-sales-team": "laptops table meeting",
    "gst-invoice-crm": "invoice paperwork", "quotation-software-with-payment-link": "payment terminal",
    "indiamart-crm-integration": "handshake business", "indiamart-lead-management": "phone call business",
    "facebook-lead-ads-crm": "facebook smartphone", "google-ads-lead-form-crm": "google search laptop",
    "lead-management-system": "sticky notes", "round-robin-lead-assignment": "office desks",
    "sales-lead-follow-up-system": "calendar", "b2b-sales-pipeline-india": "laptop chart",
    "whatsapp-crm": "smartphone chat", "ai-whatsapp-agent": "smartphone hand",
    "whatsapp-marketing-crm": "phone marketing", "email-open-tracking-crm": "email inbox",
    # Billing
    "best-billing-software-india": "cash register", "gst-invoice-format": "receipt paper",
    "desktop-vs-cloud-billing-software": "desktop computer", "billing-software-for-retail-shop": "checkout counter",
    "track-customer-outstanding-payments": "receipts",
    # Pharmacy
    "medical-store-software-features": "pills medicine", "pharmacy-expiry-management": "pills bottle",
    "pharmacy-inventory-management": "pharmacy", "pharma-wholesale-distributor-software": "pharmacy shelves",
    "medical-store-billing-process": "pills",
    # Lab
    "pathology-lab-software-features": "lab test tubes", "lab-report-format": "microscope",
    "reduce-lab-report-turnaround-time": "laboratory scientist", "lab-sample-tracking-barcode": "test tubes",
    "home-sample-collection-management": "blood sample nurse",
    # Hospital
    "hospital-management-system-modules": "hospital", "reduce-opd-waiting-time": "hospital waiting room",
    "ipd-billing-process": "hospital bed", "clinic-management-software": "stethoscope desk",
    "choose-hospital-management-software": "stethoscope",
    # Inventory
    "inventory-management-electronics-shop": "electronics", "imei-serial-number-tracking": "smartphones",
    "reorder-level-formula": "shelves store", "stock-audit-retail-shop": "clipboard",
    "reduce-dead-stock": "boxes warehouse",
    # Website
    "website-development-cost-india": "web design", "business-website-must-have-pages": "website laptop",
    "seo-for-small-business-website": "laptop analytics", "core-web-vitals-explained": "code screen",
    "own-website-vs-marketplace": "ecommerce",
    # Mobile apps
    "mobile-app-development-cost-india": "smartphone screen", "flutter-vs-react-native-vs-native": "mobile app development",
    "does-my-business-need-an-app": "smartphone home screen", "publish-app-play-store-app-store": "iphone",
    "field-sales-order-app": "tablet hand",
    # Desktop apps
    "desktop-vs-web-application": "computer desk", "offline-first-software": "laptop coffee",
    "upgrade-legacy-software": "old computer", "billing-counter-hardware": "receipt printer",
    "desktop-app-technology-choice": "developer coding",
    # Custom software
    "custom-software-vs-off-the-shelf": "whiteboard planning", "erp-for-small-business-india": "factory machine",
    "custom-software-development-cost": "budget calculator", "software-requirements-document": "notebook writing",
    "tally-integration-custom-software": "accounting",
    # Maintenance
    "website-maintenance-checklist": "checklist", "what-is-software-amc": "computer repair",
    "website-backup-strategy": "hard disk", "ssl-certificate-expired": "https padlock",
    "developer-left-take-over-website": "laptop programmer",
}


# (license, source) stages — pehle CC0, phir commercial-use allowed CC BY / BY-SA (credit dikhana zaroori).
# NC (non-commercial) aur ND (no-derivatives) kabhi nahi — business site + crop ke liye allowed nahi.
STAGES = [("cc0", "wordpress"), ("by,by-sa", "flickr")]
LICENSE_URLS = {"cc0": "https://creativecommons.org/publicdomain/zero/1.0/"}


def search(q, license_, source, page=1):
    params = urllib.parse.urlencode({"q": q, "license": license_, "source": source,
                                     "page_size": 20, "page": page, "mature": "false"})
    req = urllib.request.Request(f"https://api.openverse.org/v1/images/?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("results", [])


def candidate_queries(q):
    # Sirf poori query — single-word fallback se bilkul unrelated photos aati thi
    return [q]


def sips_dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    vals = [int(line.split(":")[1]) for line in out.splitlines() if "pixel" in line]
    return vals[0], vals[1]


def process(src, dst):
    w, h = sips_dims(src)
    if w < W or h < H:
        return False
    if w / h > W / H:
        subprocess.run(["sips", "--resampleHeight", str(H), src], capture_output=True, check=True)
    else:
        subprocess.run(["sips", "--resampleWidth", str(W), src], capture_output=True, check=True)
    subprocess.run(["sips", "--cropToHeightWidth", str(H), str(W), "-s", "format", "jpeg",
                    "-s", "formatOptions", "72", src, "--out", dst], capture_output=True, check=True)
    return sips_dims(dst) == (W, H)


def main():
    redo = set(sys.argv[sys.argv.index("--redo") + 1:]) if "--redo" in sys.argv else set()
    os.makedirs(OUT_DIR, exist_ok=True)
    meta = json.load(open(META)) if os.path.exists(META) else {}
    used = {m["id"] for m in meta.values()}
    rejected = {}
    for slug, m in meta.items():
        rejected.setdefault(slug, set()).update(m.get("rejected", []))
    posts = sorted(f[:-5] for f in os.listdir(os.path.join(SRC, "content", "blog")) if f.endswith(".html"))
    for slug in posts:
        cur = meta.get(slug)
        if cur and (cur.get("locked") or slug not in redo) and os.path.exists(os.path.join(OUT_DIR, slug + ".jpg")):
            continue
        if cur and slug in redo:
            rejected.setdefault(slug, set()).add(cur["id"])
            used.discard(cur["id"])
        q = QUERIES.get(slug)
        if not q:
            print(f"! {slug}: no query in QUERIES, skipped")
            continue
        done = False
        for license_, source in STAGES:
            for qq in candidate_queries(q):
                try:
                    results = search(qq, license_, source)
                except Exception as e:  # noqa: BLE001
                    print(f"  search failed for {qq!r}: {e}")
                    continue
                for r in results:
                    if r["id"] in used or r["id"] in rejected.get(slug, set()) or (r.get("width") or 0) < W:
                        continue
                    if r.get("license") not in ("cc0", "by", "by-sa"):
                        continue
                    with tempfile.TemporaryDirectory() as td:
                        tmp = os.path.join(td, "in.jpg")
                        try:
                            req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
                            with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
                                f.write(resp.read())
                            ok = process(tmp, os.path.join(OUT_DIR, slug + ".jpg"))
                        except Exception:  # noqa: BLE001
                            ok = False
                    if not ok:
                        continue
                    lic = r.get("license")
                    meta[slug] = {"id": r["id"], "title": r.get("title"), "creator": r.get("creator"),
                                  "creator_url": r.get("creator_url"), "source": r.get("source"),
                                  "landing_url": r.get("foreign_landing_url"),
                                  "license": ("CC0 1.0" if lic == "cc0" else f"CC {lic.upper()} {r.get('license_version', '')}".strip()),
                                  "license_url": r.get("license_url") or LICENSE_URLS.get(lic),
                                  "attribution_required": lic != "cc0", "query": qq,
                                  "rejected": sorted(rejected.get(slug, set()))}
                    used.add(r["id"])
                    print(f"✓ {slug:45} ← [{lic}] {str(r.get('title'))[:50]}")
                    done = True
                    break
                if done:
                    break
            if done:
                break
        if not done:
            print(f"✗ {slug}: no usable CC0 image for '{q}'")
        json.dump(meta, open(META, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
