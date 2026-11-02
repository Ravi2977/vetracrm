# Vetra CRM website assets

- `logo.png` and `favicon.png` are used by the site header, footer and browser tab.
- `media/product-screen-*.jpg` are resized product screenshots used in the homepage product preview.
- `media/vetra-crm-audit-log-preview.mp4` and `media/vetra-crm-dashboard-preview.mp4` are compact clips used in the homepage product preview; the matching `*-poster.jpg` files are their preview images.
- `media/vetra-crm-walkthrough.mp4` is the 1:33 homepage walkthrough. Browser chrome is cropped and private chat/account areas are obscured in the website copy.

The larger original screenshots and screen recordings are retained in this folder as source assets. They include names, emails, phone numbers, business records and local development URLs. For public deployment, publish only the logo, favicon and referenced `media/` files, or anonymise/remove the raw source files first; deploying the entire `assets/` folder would make those originals directly accessible.
