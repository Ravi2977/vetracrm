# Vetra CRM website — source

Ye folder website ka "source" hai. Repo root ki HTML files (index.html, blog/*.html, product pages)
**generated** hain — unhe haath se edit mat karo, agla build unhe overwrite kar dega.

## Roz ka kaam

```bash
python3 src/build.py     # saare pages + sitemap.xml banao
python3 src/check.py     # toote links, duplicate id, H1, title/description, image size check
python3 -m http.server 8080   # preview: http://localhost:8080
```

Preview me demo form submit mat karna — wo asli CRM me lead bana deta hai.

## Kya kahan hai

| Badlav | File |
|---|---|
| Header menu, footer, contact form, SEO tags, WhatsApp number, offer ki last date | `src/build.py` (upar ke constants) |
| Products / services pages ka content, form ke "Interested in" options, blog categories | `src/catalog.py` |
| CRM features list + plan comparison + CRM prices | `src/crm.py` |
| Homepage, CRM pages, Pricing, About, Contact, Integrations, Privacy | `src/content/pages/*.html` |
| Blog posts | `src/content/blog/<url-slug>.html` |
| Design (colors, spacing, components) | `assets/css/v2.css` (CSS badlo to `build.py` me `CSS_VERSION` badhao) |
| Form submit, offer popup | `script.js` · WhatsApp buttons, UTM, analytics events: `site.js` |

## Naya blog post

1. `src/content/blog/my-new-post.html` banao (URL hoga `/blog/my-new-post.html`):

```html
<!--
{
  "title": "SEO title (max ~60 chars)",
  "description": "Meta description, 120-160 chars.",
  "h1": "Page heading",
  "dek": "One-line intro under the heading.",
  "category": "billing",
  "date": "2026-12-01",
  "keywords": "main keyword, second keyword",
  "faqs": [["Question?", "Answer."]]
}
-->
<p>Intro…</p>
<h2>Section</h2>
<p>…</p>
```

   `category` keys: `src/catalog.py` → `BLOG_CATEGORIES`. FAQs apne aap page par dikhte hain aur FAQ schema bhi banta hai.
2. Cover image: `src/fetch_images.py` me `QUERIES` me slug + search words daalo, phir `python3 src/fetch_images.py`.
3. `python3 src/build.py && python3 src/check.py`

**Purane blog URLs kabhi rename mat karna** — Google ranking unhi URLs par hai.

## Blog images

`python3 src/fetch_images.py` Openverse se sirf **CC0** (WordPress Photo Directory) ya **CC BY / CC BY-SA** (Flickr) photos laata hai —
dono commercial use ke liye allowed hain. CC BY/BY-SA wali photo ke neeche credit (title, photographer, license) apne aap dikhta hai;
use hatana mat. Kharab image badalne ke liye: `python3 src/fetch_images.py --redo <slug>`.
Apni photo lagani ho to `assets/blog/<slug>.jpg` (960×504) rakho aur `src/content/blog-images.json` me us slug par
`"locked": true`, `"alt"`, aur credit details likh do.

## Layout shift (CLS) niyam

- Har `<img>` par `width` + `height` (check.py isse pakadta hai)
- Font self-hosted + preload + `font-display: optional` (koi font swap shift nahi)
- Koi bhi cheez JS se baad me upar insert mat karo; offer bar date ke baad `<head>` ka script hi chhupata hai
