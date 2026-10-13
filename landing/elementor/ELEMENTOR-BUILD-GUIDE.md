# Laoret × tcworld 2026 — Elementor Pro (Containers) build guide

Reference design (live): `/landing/` (EN) and `/landing/de/` (DE).
Everything below uses **Elementor Pro with Flexbox/Grid Containers** only. No extra plugins needed (a translation plugin is optional, see section 13).

**Page order follows the visitor journey:** Hero (awareness) → Proof strip (instant credibility) → This Page Is For You If (relevance) → Who We Are (positioning) → What We Help With (their problems) → Why Meet at tcworld (reason to act now) → Stats + testimonials (trust) → Meet Wael (the person) → Form + ways to meet (action) → Closing.

---

## 0. One-time setup

**Site Settings → Global Colors**

| Name | Hex | Use |
|---|---|---|
| Laoret Navy | `#0B233F` | Headings, dark sections, outline buttons |
| Laoret Teal | `#37C1CC` | Primary buttons, accents |
| Teal Dark | `#2299A3` | Hover states, small teal text |
| Laoret Coral | `#F05A5C` | Accents, stars, required marks |
| Body Text | `#4A5B6D` | Paragraphs |
| Muted | `#7A8898` | Labels, captions |
| Line | `#E3EAF0` | Borders, dividers |
| Soft Background | `#F5F9FB` | Alternate section background |
| Teal Tint | `#EBF8F9` | Icon tiles, chips |
| Coral Tint | `#FDEEEE` | Icon tiles |
| Navy Tint | `#E8ECF1` | Icon tiles |

**Site Settings → Global Fonts** (swap for laoret.com's theme fonts if they differ)

| Name | Font | Weight | Size (desktop / mobile) |
|---|---|---|---|
| H1 | Lexend | 700 | 56 / 34 px, line-height 1.2 |
| H2 | Lexend | 600 | 40 / 28 px |
| H3 | Lexend | 600 | 20 / 19 px |
| Body | Inter | 400 | 16 px, line-height 1.65 |
| Button | Lexend | 600 | 15 px |

**Site Settings → Layout:** Content width **1180 px**, container padding 24 px (mobile 18 px).

**Site Settings → Custom CSS:** paste all of `elementor/laoret-tcworld.css`. Every special effect on the page is a class from that file.

**Media:** upload everything in `/landing/assets/` (logo, key visual, the six `why-*.webp` illustrations, `dots.svg`, `dots-light.svg`) and `wael-makram.jpg`.

**Page:** create the page → **Page Layout: Elementor Canvas** (no theme header/footer; the page has its own).

**Buttons (global style):** border-radius 999 px, padding 15/28 px.
- Primary: Teal background, Navy text. Hover: Teal Dark background, white text.
- Outline: transparent background, 2 px Navy border. Hover: Navy background.

**Section heading pattern** (used in every section): Image widget `dots.svg` (width 44 px, centred, margin-bottom 18 px) → Heading H2 → Text Editor (18 px, max-width 720 px).

**Entrance animations:** Advanced → Motion Effects → Entrance Animation **Fade In Up**, Animation Duration **Normal**. Use the delays listed per section to stagger.

---

## 1. Header (sticky)
`Container` Flexbox Row, Boxed, height 72 px, justify Space Between, align Center. Background white 94%, bottom border 1 px Line.
**Motion Effects → Sticky: Top** (Desktop, Tablet, Mobile).
- `Container` Row (gap 14): Image (logo, h 30 px) · Heading "×" (Muted) · Image (tcworld logo, h 32 px)
- `Nav Menu` widget **or** 4 Buttons styled as text links (About / What We Help With / Why Laoret / Meet Wael → `#about #services #why #wael`). Responsive: hide on Tablet & Mobile.
- `Container` Row (gap 14): Language switcher (2 small Buttons EN/DE, or your translation plugin's switcher) · Button Primary "Book a Meeting" → `#book` (hide on Mobile).

## 2. Hero
`Container` Boxed, padding 72/0 px, background gradient (white → `#F7FBFC`).
- `Container` **Grid 2 columns** (1.1fr / 0.9fr), gap 56, align center. Tablet & Mobile: 1 column.
  - Left `Container` Column: H1 "Your Workflow." + line break + "Our Localization." (wrap line 2 in a `<span>` coloured **Coral #F05A5C**; line 1 Navy, matching the booth) · Text Editor subtitle "We fit localization into the way your team already works, not the other way around." (Lexend 500, 21 px Navy) · `Container` Row gap 14: Button Primary "Book a Meeting" → `#book`, Button Outline "Visit Us at the Booth" → `#booth`.
  - Right `Container` (position relative): Image key visual (radius 22, shadow) · floating `Container` "Meet Wael Makram" card. **Advanced → Position: Absolute**, left -28, bottom 36, white, radius 14, shadow. Mobile: Position Default.
- **Info bar:** `Container` **Grid 4 columns** (Tablet 2, Mobile 1), white, border 1 px Line, radius 16, CSS class **`lt-event-bar`**, **Margin Top -60 px, Z-Index 2**. 4 × `Icon Box` (icon tile 42 px). Icon colours: Teal / Coral / Navy / Teal. Content: Dates · Venue "ICS Stuttgart, Germany" · Find us "Booth 2F27" · Talk to "Wael Makram".

## 3. Proof strip: client logos + certifications
`Container` Boxed, white, padding 110/48 (mobile 48/40; the top padding clears the overlapping info bar), bottom border 1 px Line.
- Text "Proud to work with" (Lexend 14 px Muted, centred, margin-bottom 22).
- `Container` **Grid 7 columns** (Tablet 4, Mobile 2), **column gap 56 / row gap 28**, margin-bottom 36: 7 × Image (client logos) height 84 px, **Object Fit: Cover**, CSS class **`lt-logo`**, no border/background. Entrance: Fade In Up.
- `Container` Row, centred, wrap, gap 28/40, padding-top 28, **Border Top 1 px Line**: Text "ISO-certified quality · 120+ languages · ATA member" + 4 Images (ISO badges, height 58).

## 4. This Page Is For You If… (dark): relevance check
`Container` background Navy, padding 96. Optional decorative glow: Background Overlay radial gradient Teal 22 %.
- `Container` Row, centred, wrap, gap 10: 3 pills (Headings or Buttons without links) "Localization support" · "Human-governed AI" · "Quality built to scale". White text Lexend 500 14.5 px, background white 6 %, border 1.5 px Teal at 55 % (middle pill Coral at 60 %), radius 999, padding 8/16.
- H2 white "This Page Is For You If…" directly under the pills (no dots, no description), margin-bottom 44.
- `Container` **Grid 2 columns**, gap 16, max-width 980. 6 × `Icon Box` (inline icon left) or `Container` Row: background white 5 %, border white 10 %, radius 16, padding 22/24. Check icon Teal (odd) / Coral (even).
- Button Primary "That's us. Let's talk" → `#book`.

## 5. Who We Are (`#about`)
`Container` **Grid 2 columns** (0.9fr / 1.1fr), gap 72. Mobile: 1 column.
- Left: dots (left-aligned) · H2 · Text · Text Editor with left border 3 px Teal.
- Right: `Container` Column gap 14 → 5 × `Container` Row cards (border Line, radius 16, padding 22/24). Each: number badge (Heading "01", 38 px circle, Teal Tint/Teal; even rows Coral Tint/Coral) + Heading H4 + Text.
- Entrance: Fade In Up, delays 0 / 100 / 200 / 300 / 400 ms.

## 6. What We Help With (`#services`): scannable list
`Container` Boxed, background **Soft**, padding 96.
- Heading pattern (centred).
- `Container` **Grid 2 columns**, column gap 72, row gap 0, max-width 1080, centred. Mobile: 1 column.
  - 6 × row `Container` **Grid 2 columns (56 px / 1fr)**, padding 30/0, **Border Top 1 px Line**, CSS class **`lt-help-item`** (+ **`lt-acc-coral`** on rows 2, 3, 6). Give the last row in each column a bottom border too.
    - Heading "01" (15 px Lexend 600, Teal Dark; Coral on rows 2, 3, 6)
    - `Container` Column: **Heading H3, 22 px Lexend 600 Navy** (the scannable title) + Text 16 px, max-width 440.
  - Entrance: Fade In Up, delay 0 ms (left column) / 100 ms (right column).
  - Hover (from the class file): title turns Teal Dark, a 2 px brand line sweeps along the top.

## 7. Why Meet Laoret at tcworld? (`#why`): illustrated, animated
`Container` Boxed, **white** background, padding 96/96.
- Heading pattern (centred).
- `Container` **Grid 3 columns, gap 28** (Tablet 2 columns), CSS class **`lt-why-grid`**.
  - 6 × card `Container` Column: white, border 1 px Line, radius 22, padding 12. CSS class **`lt-why-card`**, plus **`lt-acc-coral`** on cards 2 & 5 and **`lt-acc-navy`** on cards 3 & 6.
    - `Image` (the illustration): background `#F6F9FB`, radius 16, **aspect ratio 5:4, Object Fit: Contain**, CSS class **`lt-why-visual`**.
    - `Container` Column, padding 22/16/18: Heading "01" (13 px, Lexend 600; Teal / Coral / Navy by card) · Heading H3 · Text (15.5 px).
    - Entrance: **Fade In Up**, delays **0 / 120 / 240 / 360 / 480 / 600 ms**.
  - The class file adds the motion: gentle continuous float on each illustration (staggered), card lifts 8 px on hover, brand-colour top bar sweeps across, illustration zooms 7 %.
- **Mobile:** either (a) replace the grid with **Nested Carousel** (Pro), slides per view 1.2, space between 14, no arrows, pagination dots, with the same 6 card containers inside; or (b) keep the grid. The `lt-why-grid` class turns it into a swipe row on phones. Add a small Text "← Swipe to see all six →" visible on Mobile only.
- Below: Text (Lexend 19 px Navy, centred, max-width 680) + Button Primary "Book a Meeting".

| # | Illustration | Title | Accent |
|---|---|---|---|
| 01 | why-workflow.webp | Workflow-first thinking | Teal |
| 02 | why-human-ai.webp | Human-governed AI | Coral |
| 03 | why-quality.webp | Scalable quality | Navy |
| 04 | why-flexible.webp | Flexible support | Teal |
| 05 | why-collaboration.webp | Easy collaboration | Coral |
| 06 | why-expertise.webp | Practical localization expertise | Navy |

## 8. Why Companies Trust Laoret (`#trust`): stats + testimonials
`Container` Soft background.
- Heading pattern.
- `Container` **Grid 4 columns** (Tablet/Mobile 2), gap 24: 4 × `Counter` or Heading+Text cards (white, border Line, radius 16). Coral for the "+", "/" and "×3" accents.
- `Container` **Grid 3 columns** (Tablet 2, Mobile 1): 3 × testimonial cards. Stars in Coral. (Or the Pro **Testimonial Carousel** widget.)

## 9. Meet Wael Makram (`#wael`)
`Container` **Grid 2 columns** (0.8fr / 1.2fr), gap 64. Mobile: 1 column.
- Left `Container` (relative): Image `wael-makram.jpg` (aspect 1:1, radius 24, shadow) + absolute `Container` tag (Navy, radius 14): "At the booth" (11.5 px uppercase Teal) / "Booth 2F27 · 10–12 Nov".
- Right: dots (left) · H2 · Heading "Localization & Operations Director, Laoret" (Teal Dark) · Text · H4 "Let's talk about…" · 6 tags (Buttons styled as pills: Teal Tint background, Teal 100 border, Navy text, no link) · Button Primary "Schedule a Meeting with Wael".

## 10. Book a Meeting (`#book`): form + ways to meet
`Container` **Grid 2 columns** (0.85fr / 1.15fr), gap 56, background gradient Soft → white.
- Left: dots · H2 · Text · `Icon List` (3 benefits, Teal check icons) · small `Container` Row: Wael avatar Image (52 px circle) + name / "Your contact at Booth 2F27".
- **Ways to meet** (replaces the old "Let's Meet" section), placed between the benefits list and the Wael card. `Container` Column, gap 12, **CSS ID `booth`** (the hero's "Visit Us at the Booth" button jumps here): 2 × `Icon Box` (icon left, 40 px tile; white card, border Line, radius 16, padding 16/18):
  1. Map-pin icon on Coral Tint/Coral: **Stop by Booth 2F27**. "ICS Stuttgart, 10–12 November. Walk-ins are always welcome."
  2. Mail icon on Navy Tint/Navy: **Can't make it to Stuttgart?** "Choose 'After the event' in the form and we'll follow up."
- Right: **Form widget (Pro)**, white card, radius 22, padding 40, shadow. CSS class **`lt-form`**.

| Field | Type | Width | Required |
|---|---|---|---|
| Full name | Text | 50 % | Yes |
| Work email | Email | 50 % | Yes |
| Company name | Text | 50 % | Yes |
| Job title | Text | 50 % | Yes |
| Phone number | Tel | 50 % | No |
| Country | Select | 50 % | Yes |
| What would you like to discuss? | **Checkbox**, inline list | 100 % | No |
| Preferred meeting timing | **Radio**, inline list, default "During the event" | 100 % | No |
| Message / notes | Textarea (4 rows) | 100 % | No |
| page_language | Hidden, value `en` / `de` | | |

Submit button "Book My Meeting", full width, Primary style. Actions After Submit: **Collect Submissions + Email** (plus your CRM / Webhook). Success message: "Thank you, we've got it. Our team will be in touch shortly to confirm your meeting with Wael." Add the privacy line as a Text Editor under the form.
The `lt-form` class turns the checkbox and radio options into the pill "chips" shown in the reference.

## 11. Closing band + footer
- `Container` Navy, centred, padding 88: H2 white "Let's Connect at **tekom 2026**" ("tekom 2026" in Coral) · Text · Row: Button Primary "Connect with Laoret" → `#book`, Button outline white "Explore laoret.com".
- Footer `Container` Row, background `#071A30`, space-between: logo (CSS filter brightness 0, invert 1) · phone + hours + Contact link · ©.

**Mobile sticky CTA:** `Container` Row (Navy, radius 999, padding 8/8/8/20), **Motion Effects → Sticky: Bottom, offset 12**, **Responsive: hide on Desktop & Tablet**. Contents: Text "Meet us at tcworld" + Button "Book a Meeting" → `#book`.

## 12. German page
Duplicate the finished page (or use WPML/Polylang if installed) and replace the copy with `/landing/de/` text. Set the Hidden field `page_language` to `de`. Keep checkbox/radio *values* in English so CRM data stays consistent. Point the EN/DE buttons at each other.

## Notes
- **Illustration resolution:** the six source illustrations are 460 px, which is fine at the card size but slightly soft on retina screens. Re-export at ~900 px if originals exist.
- **Anchors:** set Advanced → CSS ID on sections: `about`, `services`, `why`, `trust`, `wael`, `book`, `booth`.
- **Reduced motion:** the class file switches off float/hover motion for visitors who disable animations in their OS.
