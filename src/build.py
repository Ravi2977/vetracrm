#!/usr/bin/env python3
"""
Vetra CRM website builder.

    python3 src/build.py

src/content/ se saare pages padh kar repo root me final HTML likhta hai
(GitHub Pages root se hi serve karta hai). Generated HTML files ko haath se
edit mat karo — agla build unhe overwrite kar dega. Badlav src/ me karo.

  src/build.py              layout: <head>, header, footer, contact form, SEO schema
  src/catalog.py            products + services ka data (product/service pages yahin se bante hain)
  src/content/pages/*.html  hand-written pages (home, features, pricing, about ...)
  src/content/blog/*.html   blog posts (upar JSON front-matter, neeche article HTML)
"""
import datetime as dt
import html
import json
import math
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
from catalog import PRODUCTS, SERVICES, BLOG_CATEGORIES, INTERESTS  # noqa: E402
import crm  # noqa: E402

SITE = "https://vetracrm.in"
BRAND = "Vetra CRM"
GA_ID = "G-WYN8PXTC22"
WHATSAPP_NUMBER = "918604275934"
WA_TEXT = "Hi, I'd like a demo of Vetra CRM."
OFFER_END = "2026-12-26T00:00:00+05:30"   # is time ke baad offer bar/chip/prices apne aap chhup jaate hain
CSS_VERSION = "7"                          # CSS badlo to ise badhao (browser cache tod deta hai)
SOCIAL = [
    ("Facebook", "https://www.facebook.com/people/Vetra-Crm/61596019807651/", '<path d="M13.4 21v-8.2h2.8l.4-3.2h-3.2V7.5c0-.9.3-1.5 1.6-1.5h1.7V3.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.4H7.2v3.2H10V21h3.4Z"/>'),
    ("Instagram", "https://www.instagram.com/vetracrm/", '<rect x="3.2" y="3.2" width="17.6" height="17.6" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.7" cy="6.6" r="1.2"/>'),
    ("YouTube", "https://www.youtube.com/@VetraCRM", '<path d="M23.2 7a3 3 0 0 0-2.1-2.1C19.2 4.4 12 4.4 12 4.4s-7.2 0-9.1.5A3 3 0 0 0 .8 7 31 31 0 0 0 .3 12a31 31 0 0 0 .5 5 3 3 0 0 0 2.1 2.1c1.9.5 9.1.5 9.1.5s7.2 0 9.1-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-5 31 31 0 0 0-.5-5ZM9.6 15.4V8.6l6 3.4-6 3.4Z"/>'),
]
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89A11.82 11.82 0 0 0 12.05 0Zm5.42 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49 2.54 1.1 3.06.88 3.61.83.57-.05 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.27-.2-.57-.35Z"/></svg>'
CHEVRON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'

esc = html.escape


def wa_href():
    return f"https://wa.me/{WHATSAPP_NUMBER}?text=" + WA_TEXT.replace(" ", "%20").replace(",", "%2C").replace("'", "%27")


def wa_button(location, cls="btn-wa", label="Chat on WhatsApp"):
    # Server par hi visible + sahi href, taaki JS load hone par button "achanak" na aaye (no layout shift)
    return (f'<a class="{cls}" data-wa="{location}" href="{wa_href()}" target="_blank" rel="noopener noreferrer">'
            f'{WA_SVG}<span>{label}</span></a>')


# ---------------------------------------------------------------- <head>
def head(meta):
    url = SITE + meta["url"]
    title = meta["title"]
    desc = meta["description"]
    og_type = meta.get("og_type", "website")
    robots = meta.get("robots", "index,follow,max-image-preview:large")
    schema = meta.get("schema", [])
    og_img = SITE + (meta.get("image") or "/assets/og-image.png")
    og_w, og_h = ("960", "504") if meta.get("image") else ("1200", "630")
    parts = [
        '<!doctype html>\n<html lang="en-IN">\n<head>',
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f'  <title>{esc(title)}</title>',
        f'  <meta name="description" content="{esc(desc)}">',
        f'  <meta name="robots" content="{robots}">',
        f'  <link rel="canonical" href="{url}">',
        f'  <link rel="alternate" hreflang="en-IN" href="{url}">',
        f'  <link rel="alternate" hreflang="x-default" href="{url}">',
        '  <meta name="theme-color" content="#0a0f1f">',
        '  <link rel="icon" href="/favicon.ico" sizes="any">',
        '  <link rel="icon" href="/assets/favicon-48.png" type="image/png" sizes="48x48">',
        '  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
        '  <link rel="manifest" href="/site.webmanifest">',
        f'  <meta property="og:type" content="{og_type}">',
        f'  <meta property="og:title" content="{esc(meta.get("og_title", title))}">',
        f'  <meta property="og:description" content="{esc(desc)}">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:site_name" content="{BRAND}">',
        '  <meta property="og:locale" content="en_IN">',
        f'  <meta property="og:image" content="{og_img}">',
        f'  <meta property="og:image:width" content="{og_w}">',
        f'  <meta property="og:image:height" content="{og_h}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{esc(meta.get("og_title", title))}">',
        f'  <meta name="twitter:description" content="{esc(desc)}">',
        f'  <meta name="twitter:image" content="{og_img}">',
    ]
    if meta.get("published"):
        parts.append(f'  <meta property="article:published_time" content="{meta["published"]}">')
        parts.append(f'  <meta property="article:modified_time" content="{meta.get("modified", meta["published"])}">')
    parts += [
        # Font preload + font-display: optional => font swap se zero layout shift
        '  <link rel="preload" href="/assets/fonts/jakarta-latin.woff2" as="font" type="font/woff2" crossorigin>',
        f'  <link rel="stylesheet" href="/assets/css/v2.css?v={CSS_VERSION}">',
        # Offer khatam => paint se pehle hi chhupa do (no shift)
        f"  <script>if(Date.now()>=Date.parse('{OFFER_END}'))document.documentElement.classList.add('offer-over')</script>",
    ]
    for block in schema:
        parts.append('  <script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + '</script>')
    parts += [
        '  <link rel="preconnect" href="https://www.googletagmanager.com">',
        f'  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>',
        f"  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>",
        '</head>',
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------- header / footer
def header(current_url):
    def drop(label, items):
        links = "".join(
            f'<a href="{i["url"]}"><span class="ni">{i["nav_icon"]}</span><span><b>{esc(i["nav_name"])}</b><small>{esc(i["nav_hint"])}</small></span></a>'
            for i in items)
        return (f'<div class="nav-drop"><button type="button" aria-haspopup="true">{label} {CHEVRON}</button>'
                f'<div class="nav-panel">{links}</div></div>')

    def top(url, label):
        cur = ' aria-current="page"' if current_url.startswith(url) else ""
        return f'<a href="{url}"{cur}>{label}</a>'

    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="offer-bar" role="region" aria-label="Christmas offer"><b>Christmas offer:</b> 20% off Vetra Cloud CRM plans and setup, till 25 December 2026. <a href="/#contact">Claim the offer →</a></div>
<header class="header">
  <nav class="nav wrap" aria-label="Main navigation">
    <a class="brand" href="/" aria-label="{BRAND} home"><img src="/assets/logo-v2.png" alt="Vetra" width="99" height="34"><span>CRM</span></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Open navigation"><i></i><i></i></button>
    <div class="nav-menu" id="nav-menu">
      {drop("Products", PRODUCTS)}
      {drop("Services", SERVICES)}
      {top("/pricing/", "Pricing")}{top("/blog/", "Blog")}{top("/about/", "About")}{top("/contact/", "Contact")}
      <a class="btn btn-primary nav-cta" href="#contact">Book a free demo</a>
    </div>
  </nav>
</header>'''


def footer():
    prods = "".join(f'<a href="{p["url"]}">{esc(p["nav_name"])}</a>' for p in PRODUCTS)
    svcs = "".join(f'<a href="{s["url"]}">{esc(s["nav_name"])}</a>' for s in SERVICES)
    social = "".join(
        f'<a href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{BRAND} on {n}"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg></a>'
        for n, u, p in SOCIAL)
    return f'''<footer class="footer">
  <div class="wrap footer-top">
    <div class="footer-about">
      <a class="brand" href="/" aria-label="{BRAND} home"><img src="/assets/logo-v2.png" alt="Vetra" width="99" height="34" loading="lazy"><span>CRM</span></a>
      <p>Business software and app development for Indian businesses. Cloud, desktop and mobile.</p>
    </div>
    <nav class="footer-col" aria-label="Products"><h4>Products</h4><a href="/cloud-crm/">Cloud CRM</a><a href="/self-hosted-crm/">Self-Hosted CRM</a>{prods}</nav>
    <nav class="footer-col" aria-label="Services"><h4>Services</h4>{svcs}</nav>
    <nav class="footer-col" aria-label="Company"><h4>Company</h4><a href="/about/">About</a><a href="/pricing/">Pricing</a><a href="/integrations/">Integrations</a><a href="/blog/">Blog</a><a href="/contact/">Contact</a><a href="/privacy.html">Privacy</a></nav>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span id="year">{dt.date.today().year}</span> {BRAND}. All rights reserved.</span>
    <div class="social-links" aria-label="{BRAND} social media">{social}</div>
  </div>
</footer>
{wa_button("float", "wa-float")}'''


# ---------------------------------------------------------------- contact form
def contact_section(interest=None, title=None, lede=None, heading_level="h2"):
    title = title or "Ready to run your business on better software?"
    lede = lede or "Tell us what you need: a product demo, a quote, or a custom project. We'll get back to you quickly."
    opts = "".join(
        f'<option{" selected" if o == interest else ""}>{esc(o)}</option>' for o in INTERESTS)
    first = '' if interest else ' selected'
    btypes = ["IndiaMART seller", "Manufacturer or supplier", "Wholesaler or distributor", "Medical store or pharmacy",
              "Pathology lab or diagnostic centre", "Hospital or clinic", "Electronics or retail shop", "E-commerce",
              "Professional or service business", "Startup or agency", "Other"]
    bt = "".join(f"<option>{esc(b)}</option>" for b in btypes)
    return f'''<section class="section contact" id="contact" aria-labelledby="contact-title">
  <div class="wrap contact-grid">
    <div>
      <span class="eyebrow" style="background:rgba(255,255,255,.08);color:#93c5fd">Let's talk</span>
      <{heading_level} id="contact-title">{title}</{heading_level}>
      <p class="lede">{lede}</p>
      <ul class="contact-points">
        <li><span>✓</span>Free demo tailored to your business</li>
        <li><span>✓</span>Clear written quote, no hidden costs</li>
        <li><span>✓</span>Setup, training and support included</li>
      </ul>
      {wa_button("contact")}
    </div>
    <form class="contact-form" id="contact-form" name="contact" method="POST">
      <p class="hidden-field"><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
      <div class="form-heading"><h3>Get your free demo or quote</h3><p>Fields marked * are required.</p></div>
      <div class="form-grid">
        <label>Full name <em>*</em><input required name="name" autocomplete="name" placeholder="Your name"></label>
        <label>Business name <em>*</em><input required name="business" autocomplete="organization" placeholder="Your business"></label>
        <label>Work email <em>*</em><input required type="email" name="email" autocomplete="email" placeholder="you@company.com"></label>
        <label>Mobile / WhatsApp <em>*</em><input required type="tel" name="phone" autocomplete="tel" inputmode="tel" pattern="[0-9+\\s\\-]{{10,15}}" title="Enter a valid mobile number, 10 to 15 digits" placeholder="+91 98765 43210"></label>
        <label>Business type <em>*</em><select required name="business_type"><option value="" disabled selected>Select your business type</option>{bt}</select></label>
        <label>Interested in <select name="interest"><option value="" disabled{first}>Select one</option>{opts}</select></label>
        <label class="form-full">What do you need? <span class="optional">Optional</span><textarea name="message" rows="3" placeholder="A little about your business or project…"></textarea></label>
      </div>
      <div class="form-bottom"><p>By submitting, you agree we may contact you about your enquiry. See our <a href="/privacy.html">privacy notice</a>.</p><button class="btn btn-primary" type="submit">Send my enquiry</button></div>
      <p class="form-status" id="contact-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>'''


# ---------------------------------------------------------------- reusable bits
def crumbs(items):
    """items: [(name, url), ...] last one = current page. Returns (html, schema)."""
    lis = []
    for i, (name, url) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{esc(name)}</span></li>')
        else:
            lis.append(f'<li><a href="{url}">{esc(name)}</a></li>')
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}
    return f'<ol class="crumbs" aria-label="Breadcrumb">{"".join(lis)}</ol>', schema


def faq_block(faqs, open_first=True):
    out = []
    for i, (q, a) in enumerate(faqs):
        o = " open" if open_first and i == 0 else ""
        out.append(f'<details{o}><summary>{esc(q)}</summary><p>{a}</p></details>')
    return '<div class="faq-list">' + "".join(out) + "</div>"


def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}


def faq_section(faqs, title="Questions, answered", sub="Can't find what you're looking for? Talk to our team.", sid="faq"):
    return f'''<section class="section" id="{sid}" aria-labelledby="{sid}-title">
  <div class="wrap faq-grid">
    <div class="faq-side">
      <div class="sec-head"><span class="eyebrow">FAQ</span><h2 id="{sid}-title">{title}</h2><p>{sub}</p></div>
      <a class="btn btn-blue" href="#contact">Ask a question</a>
    </div>
    {faq_block(faqs)}
  </div>
</section>'''


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def org_schema():
    return {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE + "/",
            "logo": SITE + "/assets/favicon.png", "sameAs": [u for _, u, _ in SOCIAL]}


def expand_tokens(body, meta):
    """{{wa:location}}  {{contact}}  {{contact:Interest option}}  {{crm_nav}} {{crm_groups}} {{crm_matrix}} {{crm_plans}} {{crm_plans_detailed}}"""
    body = (body.replace("{{crm_nav}}", crm.features_nav()).replace("{{crm_groups}}", crm.features_groups())
            .replace("{{crm_matrix}}", crm.matrix()).replace("{{crm_plans_detailed}}", crm.plans_html(True))
            .replace("{{crm_plans}}", crm.plans_html(False)))
    body = re.sub(r"\{\{wa:([\w-]+)\}\}", lambda m: wa_button(m.group(1)), body)
    body = re.sub(r"\{\{contact(?::([^}]*))?\}\}", lambda m: contact_section(m.group(1) or meta.get("interest")), body)
    return body


def render(meta, body, contact=True):
    body = expand_tokens(body, meta)
    if contact and 'id="contact"' not in body:
        body += "\n" + contact_section(meta.get("interest"), meta.get("contact_title"), meta.get("contact_lede"))
    out = (head(meta) + "\n<body>\n" + header(meta["url"]) + '\n<main id="main">\n' + body + "\n</main>\n"
           + footer() + f'\n<script src="/site.js?v={CSS_VERSION}" defer></script>\n<script src="/script.js?v={CSS_VERSION}" defer></script>\n</body>\n</html>\n')
    if 'id="contact"' not in body:
        out = out.replace('href="#contact"', 'href="/contact/"')
    return out


SITEMAP = []


def write(url, html_text, sitemap=True, priority="0.7", lastmod=None):
    path = url.lstrip("/")
    if path == "" or path.endswith("/"):
        path += "index.html"
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html_text)
    if sitemap:
        SITEMAP.append((url, priority, lastmod or TODAY))


TODAY = dt.date.today().isoformat()


# ---------------------------------------------------------------- front-matter files
def read_fm(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", s, re.S)
    if not m:
        raise SystemExit(f"{path}: front-matter missing")
    return json.loads(m.group(1)), s[m.end():]


# ---------------------------------------------------------------- pages
def build_pages():
    pdir = os.path.join(SRC, "content", "pages")
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".html"):
            continue
        meta, body = read_fm(os.path.join(pdir, fn))
        schema = []
        if meta.get("crumbs"):
            c_html, c_schema = crumbs([tuple(x) for x in meta["crumbs"]])
            body = body.replace("{{crumbs}}", c_html)
            schema.append(c_schema)
        if meta.get("faqs"):
            faqs = [tuple(x) for x in meta["faqs"]]
            body = body.replace("{{faq}}", faq_section(faqs, meta.get("faq_title", "Questions, answered")))
            schema.append(faq_schema(faqs))
        meta["schema"] = meta.get("schema", []) + schema
        if meta["url"] == "/":
            meta["schema"].insert(0, org_schema())
        noindex = "noindex" in meta.get("robots", "")
        write(meta["url"], render(meta, body, contact=meta.get("contact", True)),
              sitemap=not noindex, priority=meta.get("priority", "0.7"))


# ---- product & service pages (template)
def visual(v):
    kind = v["type"]
    bar = f'<div class="mock-bar"><i></i><i></i><i></i><span>{esc(v.get("bar", "app.vetracrm.in"))}</span></div>'
    if kind == "code":
        return f'<div class="vis" aria-hidden="true">{bar}<div class="vis-code">{v["code"]}</div></div>'
    rows = "".join(
        "<div>" + "".join(f'<span class="{c[1]}">{esc(c[0])}</span>' if isinstance(c, list) else f"<span>{esc(c)}</span>" for c in r) + "</div>"
        for r in v["rows"])
    total = f'<div class="vis-total"><span>{esc(v["total"][0])}</span><b>{esc(v["total"][1])}</b></div>' if v.get("total") else ""
    return (f'<div class="vis" aria-label="Illustrative {esc(v["title"])} screen">{bar}<div class="vis-body">'
            f'<div class="vis-title"><b>{esc(v["title"])}</b><em>{esc(v["tag"])}</em></div>'
            f'<div><div class="vis-table">{rows}</div>{total}</div></div></div>')


def related_posts(cat_key, exclude=None, limit=3):
    posts = [p for p in POSTS if p["category"] == cat_key and p["slug"] != exclude]
    return posts[:limit]


def post_card(p, h="h3"):
    cat = BLOG_CATEGORIES[p["category"]]
    img = post_image(p)
    art = (f'<img src="{img["src"]}" alt="" width="{IMG_W}" height="{IMG_H}" loading="lazy" decoding="async">' if img
           else f'<span>{esc(cat["art"])}</span>')
    return (f'<a class="post" href="{p["url"]}"><div class="post-art" style="--g:{cat["gradient"]}" aria-hidden="true">{art}</div>'
            f'<div class="post-body"><small>{esc(cat["name"])}</small><{h}>{esc(p["h1"])}</{h}><p>{esc(p["description"])}</p>'
            f'<em>{p["read"]} min read</em></div></a>')


def offering_page(item, kind):
    cr_html, cr_schema = crumbs([("Home", "/"), ("Products" if kind == "product" else "Services", "/#products" if kind == "product" else "/#services"), (item["nav_name"], item["url"])])
    chips = "".join(f'<span class="chip"><i style="--c:{c}"></i>{esc(n)}</span>' for n, c in item["platforms"])
    feats = "".join(
        f'<article class="card highlight-card"><span class="ti">{f[0]}</span><h3>{esc(f[1])}</h3><p>{f[2]}</p></article>'
        for f in item["features"])
    who = "".join(f'<div class="card"><span class="ti">{w[0]}</span><h3>{esc(w[1])}</h3><p>{esc(w[2])}</p></div>' for w in item["who"])
    steps = "".join(f'<li class="step journey-step"><span class="step-n">{i + 1 if i < len(item["steps"]) - 1 else "✓"}</span><h3>{esc(s[0])}</h3><p>{esc(s[1])}</p></li>'
                    for i, s in enumerate(item["steps"]))
    bad = "".join(f"<li>{esc(x)}</li>" for x in item["problems"]["bad"])
    good = "".join(f"<li>{esc(x)}</li>" for x in item["problems"]["good"])
    extra = item.get("extra_html", "")
    posts = related_posts(item["blog"])
    cat = BLOG_CATEGORIES[item["blog"]]
    blog_html = ""
    if posts:
        blog_html = f'''<section class="section bg-paper" aria-labelledby="guides-title"><div class="wrap">
  <div class="cat-block-head"><div><span class="eyebrow">Guides</span><h2 id="guides-title" style="font-size:clamp(26px,3.4vw,36px)">{esc(cat["name"])} guides</h2></div><a class="link-arrow" href="/blog/category/{cat["slug"]}/">All {esc(cat["name"].lower())} articles <span>→</span></a></div>
  <div class="post-grid">{"".join(post_card(p) for p in posts)}</div>
</div></section>'''
    others = [x for x in (PRODUCTS if kind == "product" else SERVICES) if x["url"] != item["url"]][:3]
    other_html = "".join(f'<a class="card" href="{o["url"]}"><span class="ti">{o["nav_icon"]}</span><h3>{esc(o["nav_name"])}</h3><p>{esc(o["nav_hint"])}</p></a>' for o in others)
    faqs = [tuple(x) for x in item["faqs"]]

    if kind == "product":
        main_schema = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": item["schema_name"],
                       "applicationCategory": "BusinessApplication", "operatingSystem": item["os"],
                       "description": item["description"], "url": SITE + item["url"],
                       "publisher": {"@type": "Organization", "name": BRAND, "url": SITE + "/"},
                       "featureList": [strip_tags(f[1]) for f in item["features"]]}
    else:
        main_schema = {"@context": "https://schema.org", "@type": "Service", "name": item["schema_name"],
                       "serviceType": item["schema_name"], "description": item["description"], "url": SITE + item["url"],
                       "areaServed": {"@type": "Country", "name": "India"},
                       "provider": {"@type": "Organization", "name": BRAND, "url": SITE + "/"}}

    body = f'''<section class="page-hero">
  <div class="wrap hero-grid">
    <div>
      {cr_html}
      <span class="eyebrow">{esc(item["eyebrow"])}</span>
      <h1>{item["h1"]}</h1>
      <p class="hero-lede">{esc(item["lede"])}</p>
      <div class="hero-actions"><a class="btn btn-primary" href="#contact">{esc(item["cta"])} <span aria-hidden="true">→</span></a>{wa_button("hero")}</div>
      <div class="chip-row">{chips}</div>
    </div>
    {visual(item["visual"])}
  </div>
</section>

<section class="section" aria-labelledby="why-title"><div class="wrap">
  <div class="sec-head center"><span class="eyebrow">Why {esc(item["short"])}</span><h2 id="why-title">{item["why_title"]}</h2></div>
  <div class="ps"><div class="bad"><h3>{esc(item["problems"]["bad_title"])}</h3><ul>{bad}</ul></div><div class="good"><h3>{esc(item["problems"]["good_title"])}</h3><ul>{good}</ul></div></div>
</div></section>

<section class="section bg-paper" id="features" aria-labelledby="feat-title"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">{"Features" if kind == "product" else "What we build"}</span><h2 id="feat-title">{item["features_title"]}</h2><p>{esc(item["features_lede"])}</p></div>
  <div class="cards">{feats}</div>
</div></section>
{extra}
<section class="section" aria-labelledby="who-title"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">{"Who it's for" if kind == "product" else "Who we work with"}</span><h2 id="who-title">{item["who_title"]}</h2></div>
  <div class="cards">{who}</div>
</div></section>

<section class="section journey" aria-labelledby="how-title"><div class="wrap">
  <div class="sec-head center"><span class="eyebrow">How it works</span><h2 id="how-title">{item["steps_title"]}</h2></div>
  <ol class="steps">{steps}</ol>
</div></section>

{faq_section(faqs, item.get("faq_title", "Questions, answered"))}
{blog_html}
<section class="section-tight"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Explore more</span><h2 style="font-size:clamp(24px,3vw,32px)">Other {"products" if kind == "product" else "services"}</h2></div>
  <div class="cards">{other_html}</div>
</div></section>'''
    meta = {"url": item["url"], "title": item["title"], "description": item["description"],
            "interest": item["interest"], "schema": [main_schema, cr_schema, faq_schema(faqs)],
            "contact_title": item.get("contact_title")}
    write(item["url"], render(meta, body), priority="0.9")


# ---------------------------------------------------------------- blog
POSTS = []
IMAGES = json.load(open(os.path.join(SRC, "content", "blog-images.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(SRC, "content", "blog-images.json")) else {}
IMG_W, IMG_H = 960, 504


def post_image(p):
    """Blog cover image info (src/fetch_images.py se), ya None."""
    m = IMAGES.get(p["slug"])
    if not m or not os.path.exists(os.path.join(ROOT, "assets", "blog", p["slug"] + ".jpg")):
        return None
    alt = m.get("alt") or (m.get("query") or "").capitalize()
    return {"src": f"/assets/blog/{p['slug']}.jpg", "alt": alt, **m}


def image_credit(img):
    title = esc(img.get("title") or "Photo")
    creator = esc(img.get("creator") or "unknown")
    src_name = {"wordpress": "WordPress Photo Directory", "flickr": "Flickr"}.get(img.get("source"), img.get("source") or "")
    lic = f'<a href="{esc(img["license_url"])}" rel="license noopener" target="_blank">{esc(img["license"])}</a>' if img.get("license_url") else esc(img.get("license", ""))
    link = f'<a href="{esc(img["landing_url"])}" rel="noopener" target="_blank">{title}</a>' if img.get("landing_url") else title
    cropped = ", cropped" if img.get("attribution_required") else ""
    return f'Photo: {link} by {creator} via {esc(src_name)} ({lic}{cropped})'


def load_posts():
    bdir = os.path.join(SRC, "content", "blog")
    for fn in sorted(os.listdir(bdir)):
        if not fn.endswith(".html"):
            continue
        meta, body = read_fm(os.path.join(bdir, fn))
        meta["slug"] = fn[:-5]
        meta["url"] = f"/blog/{meta['slug']}.html"   # purane URLs (.html) waise hi rehte hain
        meta["body"] = body
        words = len(strip_tags(body).split())
        meta["words"] = words
        meta["read"] = max(2, math.ceil(words / 200))
        if meta["category"] not in BLOG_CATEGORIES:
            raise SystemExit(f"{fn}: unknown category {meta['category']}")
        POSTS.append(meta)
    POSTS.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def add_heading_ids(body):
    seen = set()

    def fix(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "id=" in attrs:
            return m.group(0)
        hid = slugify(strip_tags(inner))[:60] or "section"
        while hid in seen:
            hid += "-2"
        seen.add(hid)
        return f'<{tag}{attrs} id="{hid}">{inner}</{tag}>'
    return re.sub(r"<(h2)([^>]*)>(.*?)</h2>", fix, body, flags=re.S)


def build_post(p):
    cat = BLOG_CATEGORIES[p["category"]]
    body = p["body"]
    if p.get("faqs") and p.get("render_faq", True) and "Frequently asked questions" not in body:
        # FAQ schema sirf tab valid hai jab wahi sawal page par dikhte hon — isliye body me bhi render karo
        body += '\n<h2 id="faq">Frequently asked questions</h2>\n' + "".join(
            f"<h3>{esc(q)}</h3>\n<p>{a}</p>\n" for q, a in p["faqs"])
    if cat.get("product") and "article-next" not in body:
        body += (f'\n<div class="article-next"><span>SEE IT IN ACTION</span>'
                 f'<a href="{cat["product"][1]}">Explore {esc(cat["product"][0])} →</a></div>')
    body = add_heading_ids(body)
    toc = "".join(f'<li><a href="#{m.group(1)}">{esc(strip_tags(m.group(2)))}</a></li>'
                  for m in re.finditer(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', body, re.S))
    cr_html, cr_schema = crumbs([("Home", "/"), ("Blog", "/blog/"), (cat["name"], f"/blog/category/{cat['slug']}/"), (p.get("crumb", p["h1"]), p["url"])])
    date_h = dt.date.fromisoformat(p["date"]).strftime("%-d %B %Y")
    img = post_image(p)
    hero = ""
    if img:
        hero = (f'<figure class="post-hero"><img src="{img["src"]}" alt="{esc(img["alt"])}" width="{IMG_W}" height="{IMG_H}" fetchpriority="high" decoding="async">'
                f'<figcaption>{image_credit(img)}</figcaption></figure>')
    modified = p.get("modified", p["date"])
    product = cat.get("product")
    schema = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["h1"], "description": p["description"],
               "datePublished": p["date"], "dateModified": modified, "inLanguage": "en-IN", "articleSection": cat["name"],
               "keywords": p.get("keywords", ""), "wordCount": p["words"], "image": SITE + (img["src"] if img else "/assets/og-image.png"),
               "author": {"@type": "Organization", "name": BRAND, "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": SITE + "/assets/favicon.png"}},
               "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + p["url"]}}, cr_schema]
    if p.get("faqs"):
        schema.append(faq_schema([tuple(x) for x in p["faqs"]]))
    rel = related_posts(p["category"], exclude=p["slug"])
    rel_html = ""
    if rel:
        rel_html = f'''<section class="section bg-paper" aria-labelledby="rel-title"><div class="wrap">
  <div class="cat-block-head"><h2 id="rel-title">More {esc(cat["name"].lower())} guides</h2><a class="link-arrow" href="/blog/category/{cat["slug"]}/">View all <span>→</span></a></div>
  <div class="post-grid">{"".join(post_card(x) for x in rel)}</div>
</div></section>'''
    side_product = ""
    if product:
        side_product = f'<a class="btn btn-primary" href="{product[1]}">Explore {esc(product[0])}</a>'
    body_html = f'''<article>
<header class="article-head"><div class="wrap">
  {cr_html}
  <a class="cat-chip" href="/blog/category/{cat["slug"]}/">{esc(cat["name"])}</a>
  <h1>{esc(p["h1"])}</h1>
  <p class="dek">{esc(p["dek"])}</p>
  <div class="byline"><span>By {BRAND}</span><time datetime="{p["date"]}">{date_h}</time><span>{p["read"]} min read</span></div>
</div></header>
<div class="wrap article-grid">
  <div class="prose">
{hero}
{body}
  </div>
  <aside class="article-aside">
    {"<nav class='toc' aria-label='On this page'><b>On this page</b><ol>" + toc + "</ol></nav>" if toc else ""}
    <div class="side-cta"><small>FREE DEMO</small><h3>{esc(cat["cta_title"])}</h3><p>{esc(cat["cta_text"])}</p>{side_product if product else ""}<a class="btn {"btn-light" if product else "btn-primary"}" href="#contact">Book a free demo</a>{wa_button("blog-side")}</div>
  </aside>
</div>
</article>
{rel_html}'''
    meta = {"url": p["url"], "title": p["title"], "description": p["description"], "og_type": "article",
            "published": p["date"], "modified": modified, "schema": schema, "interest": cat.get("interest"),
            "image": img["src"] if img else None}
    write(p["url"], render(meta, body_html), priority="0.6", lastmod=modified)


def build_blog_index():
    counts = {k: sum(1 for p in POSTS if p["category"] == k) for k in BLOG_CATEGORIES}

    def catnav(active=None):
        a = ' aria-current="page"' if active is None else ""
        out = [f'<a href="/blog/"{a}>All<span>{len(POSTS)}</span></a>']
        for k, c in BLOG_CATEGORIES.items():
            if counts[k]:
                cur = ' aria-current="page"' if k == active else ""
                out.append(f'<a href="/blog/category/{c["slug"]}/"{cur}>{esc(c["name"])}<span>{counts[k]}</span></a>')
        return '<nav class="cat-nav" aria-label="Blog categories">' + "".join(out) + "</nav>"

    # /blog/
    cr_html, cr_schema = crumbs([("Home", "/"), ("Blog", "/blog/")])
    blocks = []
    for k, c in BLOG_CATEGORIES.items():
        ps = [p for p in POSTS if p["category"] == k]
        if not ps:
            continue
        blocks.append(f'''<div class="cat-block"><div class="cat-block-head"><h2>{esc(c["name"])}</h2><a class="link-arrow" href="/blog/category/{c["slug"]}/">View all {len(ps)} <span>→</span></a></div>
<div class="post-grid">{"".join(post_card(p, "h3") for p in ps[:3])}</div></div>''')
    body = f'''<section class="page-hero solo"><div class="wrap">
  {cr_html}
  <span class="eyebrow">Vetra blog</span>
  <h1>Practical guides for <span class="grad-text">running a better business</span></h1>
  <p class="hero-lede">CRM and lead management, billing, pharmacy, lab, hospital and inventory software, plus website and app development. Written for Indian businesses.</p>
</div></section>
<section class="section"><div class="wrap">{catnav()}{"".join(blocks)}</div></section>'''
    schema = [cr_schema, {"@context": "https://schema.org", "@type": "Blog", "name": f"{BRAND} Blog", "url": SITE + "/blog/",
                          "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": SITE + p["url"], "datePublished": p["date"]} for p in POSTS[:30]]}]
    meta = {"url": "/blog/", "title": "Vetra Blog | CRM, Billing, Pharmacy, Lab & Software Guides",
            "description": "Practical guides for Indian businesses on CRM, lead management, billing, medical store, lab, hospital and inventory software, and website and app development.",
            "schema": schema}
    write("/blog/", render(meta, body), priority="0.8")

    # /blog/category/<slug>/
    for k, c in BLOG_CATEGORIES.items():
        ps = [p for p in POSTS if p["category"] == k]
        if not ps:
            continue
        url = f"/blog/category/{c['slug']}/"
        cr_html, cr_schema = crumbs([("Home", "/"), ("Blog", "/blog/"), (c["name"], url)])
        prod_link = f'<div class="hero-actions"><a class="btn btn-primary" href="{c["product"][1]}">Explore {esc(c["product"][0])} <span aria-hidden="true">→</span></a></div>' if c.get("product") else ""
        body = f'''<section class="page-hero solo"><div class="wrap">
  {cr_html}
  <span class="eyebrow">Blog category</span>
  <h1>{esc(c["h1"])}</h1>
  <p class="hero-lede">{esc(c["intro"])}</p>
  {prod_link}
</div></section>
<section class="section"><div class="wrap">{catnav(k)}<div class="post-grid">{"".join(post_card(p, "h2") for p in ps)}</div></div></section>'''
        schema = [cr_schema, {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["h1"], "url": SITE + url,
                              "hasPart": [{"@type": "BlogPosting", "headline": p["h1"], "url": SITE + p["url"]} for p in ps]}]
        meta = {"url": url, "title": c["title"], "description": c["intro"][:158], "schema": schema, "interest": c.get("interest")}
        write(url, render(meta, body), priority="0.6")


# ---------------------------------------------------------------- sitemap
def build_sitemap():
    seen = set()
    rows = []
    for url, pr, lm in sorted(SITEMAP, key=lambda x: (-float(x[1]), x[0])):
        if url in seen:
            continue
        seen.add(url)
        rows.append(f"  <url><loc>{SITE}{url}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def main():
    load_posts()
    build_pages()
    for p in PRODUCTS:
        if not p.get("external"):
            offering_page(p, "product")
    for s in SERVICES:
        offering_page(s, "service")
    for p in POSTS:
        build_post(p)
    build_blog_index()
    build_sitemap()
    print(f"Built {len(SITEMAP)} indexable pages ({len(POSTS)} blog posts).")


if __name__ == "__main__":
    main()
