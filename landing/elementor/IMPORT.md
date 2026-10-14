# Import the tcworld 2026 landing page into WordPress (Elementor Pro, Containers)

Files:
- `laoret-tcworld-2026-en.json` (English page)
- `laoret-tcworld-2026-de.json` (German page)

Both were test-imported into WordPress with Elementor 4.4 (laoret.com runs 4.3.4). All 266 elements per page came through and render; only the Pro form needs Pro to appear.

## Steps (per language)

1. **WordPress → Templates → Saved Templates → Import Templates**, choose the JSON file, click **Import Now**.
   Elementor downloads the images (logo, key visual, illustrations, Wael's photo, client logos, ISO badges) into your Media Library during import.
2. **Pages → Add New**, title e.g. *Laoret at tcworld 2026*, slug `tcworld-2026` (German: `tcworld-2026` under `/de/`, or whatever your language setup uses). Click **Edit with Elementor**.
3. In the editor: folder icon (Add Template) → **My Templates** → **Insert** the imported template. Elementor carries over the page's Custom CSS with it.
4. **Page Settings (gear icon) → Page Layout: Elementor Canvas.** The import doesn't keep this setting, and it hides the theme header and footer because the page has its own.
5. **Form (Book a Meeting section) → Actions After Submit:** check that **Email** is set to the right recipient (it defaults to the site admin email) and that **Collect Submissions** is on. Add your CRM / Webhook action here.
6. **Publish.**

## Check after importing

- **EN/DE switcher** (header, HTML widget) links to `/tcworld-2026/` and `/de/tcworld-2026/`. If your slugs differ, edit both links in that widget on both pages.
- **QR codes:** point them at the page with tracking, e.g. `https://laoret.com/tcworld-2026/?utm_source=booth&utm_medium=qr&utm_campaign=tcworld2026`.
- **tcworld and tekom logos** are loaded from tekom.de in two HTML widgets (header, hero), because WordPress does not accept SVG uploads by default. If you prefer, upload PNG versions and swap them in.
- **Fonts:** the template sets Open Sans and Lato on every element. If your Site Settings already define them as global fonts, nothing else is needed.
- **Images:** if any image shows a grey placeholder, your server couldn't download it during import. Re-select it from `/landing/assets/` in the repo.

## What uses which Elementor feature

- Layout: Flexbox and Grid **Containers** only (no sections/columns).
- Widgets: Heading, Text Editor, Image, Button, Icon Box, Icon List, HTML (free) and **Form** (Pro).
- **Sticky** header and the mobile "Book a Meeting" bar: Motion Effects → Sticky (Pro).
- Entrance animations: Fade In Up with staggered delays.
- Hover effects, floating illustrations, dark-band shapes, pill-style form options and the mobile swipe row for the "Why Meet" cards come from the **page Custom CSS** (Pro) and the CSS classes listed in `ELEMENTOR-BUILD-GUIDE.md`.

## Regenerating after copy changes

Edit `../index.html` / `../de/index.html`, then run `python3 build_templates.py` in this folder. It rebuilds both JSON files from the pages, so the WordPress version never drifts from the approved copy.
