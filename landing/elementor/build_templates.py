#!/usr/bin/env python3
"""Generate Elementor Pro (Containers) template JSON files from the live landing pages.

Usage:  python3 build_templates.py
Reads ../index.html (EN) and ../de/index.html (DE), writes
laoret-tcworld-2026-en.json and laoret-tcworld-2026-de.json next to this script.
Re-run after any copy change so the WordPress templates stay in sync with the pages.
"""
import hashlib, json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://mhellawygap-ui.github.io/laoret-tcworld-2026/landing/'
TCWORLD_LOGO = 'https://tcworldconference.tekom.de/fileadmin/tagungen.tekom.de/H26/Logos_Banner_Keyvisual/Logos_Banner_Tagung/Logos_pur/tcworld-conference_Vektordatei.svg'
TEKOM_LOGO = 'https://jahrestagung.tekom.de/fileadmin/tagungen.tekom.de/H26/Logos_Banner_Keyvisual/Logos_Banner_Tagung/Logos_pur/tekom-jahrestagung_transparent.svg'
# Page URLs on WordPress for the EN/DE switcher (change if you publish under other slugs)
PAGE_URL = {'en': '/tcworld-2026/', 'de': '/de/tcworld-2026/'}

# ---------------------------------------------------------------- tokens
NAVY, BRAND, BRAND_D, ICON, CYAN, CORAL = '#0B233F', '#00A2AE', '#008B96', '#1EC0CC', '#00C0CF', '#F05A5C'
DARK, AQUA, BODY, MUTED, LINE, SOFT = '#000915', '#E1F6F6', '#4A5B6D', '#7A8898', '#E3EAF0', '#F5FAFB'
OPEN, LATO = 'Open Sans', 'Lato'

# ---------------------------------------------------------------- helpers
_n = [0]
def uid(lang):
    _n[0] += 1
    return hashlib.md5(f'{lang}-{_n[0]}'.encode()).hexdigest()[:7]

def px(v): return {'unit': 'px', 'size': v, 'sizes': []}
def box(t, r=None, b=None, l=None, unit='px'):
    r = t if r is None else r; b = t if b is None else b; l = r if l is None else l
    return {'unit': unit, 'top': str(t), 'right': str(r), 'bottom': str(b), 'left': str(l), 'isLinked': len({t, r, b, l}) == 1}
def gap(row, col=None):
    col = row if col is None else col
    return {'unit': 'px', 'row': str(row), 'column': str(col), 'isLinked': row == col}
def shadow(h, v, blur, spread, color):
    return {'horizontal': h, 'vertical': v, 'blur': blur, 'spread': spread, 'color': color}

def typo(prefix, font, size, weight, lh=None, ls=None, transform=None, size_m=None, style=None):
    p = f'{prefix}_' if prefix else ''
    d = {f'{p}typography_typography': 'custom', f'{p}typography_font_family': font,
         f'{p}typography_font_size': px(size), f'{p}typography_font_weight': str(weight)}
    if size_m: d[f'{p}typography_font_size_mobile'] = px(size_m)
    if lh: d[f'{p}typography_line_height'] = {'unit': 'em', 'size': lh, 'sizes': []}
    if ls is not None: d[f'{p}typography_letter_spacing'] = {'unit': 'em', 'size': ls, 'sizes': []}
    if transform: d[f'{p}typography_text_transform'] = transform
    if style: d[f'{p}typography_font_style'] = style
    return d

# type scale (laoret.com)
DISPLAY = lambda p='': typo(p, OPEN, 72, 700, 1.08, -0.02, size_m=40)
H2 = lambda p='': typo(p, OPEN, 36, 700, 1.22, -0.02, size_m=28)
H3 = lambda p='': typo(p, OPEN, 24, 700, 1.3, size_m=20)
H4 = lambda p='': typo(p, OPEN, 20, 700, 1.35)
H5 = lambda p='': typo(p, OPEN, 17, 700, 1.4)
H6 = lambda p='': typo(p, OPEN, 15, 700, 1.4, 0.04)
INTRO = lambda p='': typo(p, LATO, 20, 300, 1.6, size_m=18)
BODY_L = lambda p='': typo(p, LATO, 18, 400, 1.65)
BODY_ = lambda p='': typo(p, LATO, 16, 400, 1.7)
SMALL = lambda p='': typo(p, LATO, 14, 400, 1.55)
CAPTION = lambda p='': typo(p, OPEN, 12, 700, 1.4, 0.08, 'uppercase')

def anim(container=False, delay=0):
    if container:
        d = {'animation': 'fadeInUp', 'animation_duration': ''}
        if delay: d['animation_delay'] = delay
    else:
        d = {'_animation': 'fadeInUp', 'animation_duration': ''}
        if delay: d['_animation_delay'] = delay
    return d

class B:
    """Element builders. Every element gets a stable 7-char id."""
    def __init__(self, lang): self.lang = lang

    def con(self, children, top=False, direction='column', grid=None, **s):
        st = {'content_width': 'boxed' if top else 'full'}
        if top: st['boxed_width'] = px(1180)
        if grid:
            st.update({'container_type': 'grid',
                       'grid_columns_grid': grid[0], 'grid_rows_grid': {'unit': 'custom', 'size': 'auto', 'sizes': []},
                       'grid_gaps': grid[1], 'grid_auto_flow': 'row'})
            if len(grid) > 2 and grid[2] is not None: st['grid_columns_grid_tablet'] = grid[2]
            if len(grid) > 3 and grid[3] is not None: st['grid_columns_grid_mobile'] = grid[3]
        else:
            st.update({'container_type': 'flex', 'flex_direction': direction})
        st.setdefault('padding', box(0))
        st.update(s)
        if 'flex_gap' not in st and not grid: st['flex_gap'] = gap(0)
        return {'id': uid(self.lang), 'elType': 'container', 'settings': st, 'elements': children, 'isInner': not top}

    def w(self, wtype, **s):
        return {'id': uid(self.lang), 'elType': 'widget', 'settings': s, 'elements': [], 'widgetType': wtype}

    def heading(self, title, tag='h2', color=NAVY, t=None, align=None, link=None, **s):
        d = {'title': title, 'header_size': tag, 'title_color': color}
        d.update(t or {})
        if align: d['align'] = align
        if link: d['link'] = {'url': link, 'is_external': '', 'nofollow': ''}
        d.update(s)
        return self.w('heading', **d)

    def text(self, html, color=BODY, t=None, align=None, **s):
        d = {'editor': html if html.lstrip().startswith('<') else f'<p>{html}</p>', 'text_color': color}
        d.update(t or BODY_())
        if align: d['align'] = align
        d.update(s)
        return self.w('text-editor', **d)

    def image(self, url, alt='', width=None, height=None, fit=None, radius=None, align=None, **s):
        d = {'image': {'url': url, 'id': '', 'alt': alt, 'source': 'library', 'size': ''}, 'image_size': 'full'}
        if width: d['width'] = width
        if height: d['height'] = px(height)
        if fit: d['object-fit'] = fit
        if radius is not None: d['image_border_radius'] = box(radius)
        if align: d['align'] = align
        d.update(s)
        return self.w('image', **d)

    def button(self, label, url, kind='primary', icon=False, size_pad=(14, 30), **s):
        bg = {'primary': BRAND, 'outline': '#FFFFFF', 'cyan': CYAN, 'light': 'transparent'}[kind]
        fg = {'primary': '#FFFFFF', 'outline': BRAND, 'cyan': '#FFFFFF', 'light': '#FFFFFF'}[kind]
        hover_bg = {'primary': BRAND_D, 'outline': BRAND, 'cyan': '#00AAB8', 'light': '#FFFFFF'}[kind]
        hover_fg = {'primary': '#FFFFFF', 'outline': '#FFFFFF', 'cyan': '#FFFFFF', 'light': DARK}[kind]
        cls = {'primary': 'lt-btn-glow', 'outline': 'lt-btn-glow-soft', 'cyan': 'lt-btn-glow-cyan', 'light': 'lt-btn-light'}[kind]
        d = {'text': label, 'link': {'url': url, 'is_external': '', 'nofollow': ''},
             'background_background': 'classic', 'background_color': bg, 'button_text_color': fg,
             'button_background_hover_background': 'classic', 'button_background_hover_color': hover_bg, 'hover_color': hover_fg,
             'border_radius': box(999), 'text_padding': box(size_pad[0], size_pad[1]), '_css_classes': cls}
        d.update(typo('', OPEN, 15, 700))
        if kind in ('outline', 'light'):
            d.update({'border_border': 'solid', 'border_width': box(1.5),
                      'border_color': 'rgba(0,162,174,.45)' if kind == 'outline' else 'rgba(255,255,255,.6)',
                      'button_hover_border_color': hover_bg})
        if icon:
            d.update({'selected_icon': {'value': 'fas fa-arrow-right', 'library': 'fa-solid'}, 'icon_align': 'row-reverse', 'icon_indent': px(8)})
        d.update(s)
        return self.w('button', **d)

    def icon_box(self, icon, title, desc='', title_t=None, desc_t=None, icon_color=ICON, title_color=NAVY, desc_color=BODY, size=30, **s):
        lib = 'fa-regular' if icon.startswith('far ') else 'fa-solid'
        d = {'selected_icon': {'value': icon, 'library': lib}, 'view': 'default', 'position': 'inline-start',
             'title_text': title, 'description_text': desc, 'title_size': 'div', 'primary_color': icon_color,
             'icon_size': px(size), 'icon_space': px(14), 'title_bottom_space': px(2), 'title_color': title_color,
             'description_color': desc_color, 'text_align': 'start', 'content_vertical_alignment': 'top'}
        d.update(title_t or H5('title')); d.update(desc_t or SMALL('description'))
        d.update(s)
        return self.w('icon-box', **d)

    def html(self, code, **s):
        return self.w('html', html=code, **s)


def card(**extra):
    d = {'background_background': 'classic', 'background_color': '#FFFFFF', 'border_radius': box(12),
         'box_shadow_box_shadow_type': 'yes', 'box_shadow_box_shadow': shadow(0, 10, 30, 0, 'rgba(11,35,63,0.07)')}
    d.update(extra)
    return d

# ---------------------------------------------------------------- copy extraction
def extract(path):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    T = lambda sel, el=None: ' '.join((el or soup).select_one(sel).get_text(' ', strip=True).split())
    inner = lambda el: el.decode_contents().strip()
    c = {}
    c['lang'] = soup.html['lang']
    c['title'] = soup.title.get_text(strip=True)
    c['desc'] = soup.find('meta', attrs={'name': 'description'})['content']
    c['nav'] = [(a.get_text(strip=True), a['href']) for a in soup.select('.nav-links a')]
    c['hero_btns'] = [a.get_text(' ', strip=True) for a in soup.select('.hero .cta-row a')]
    c['nav_btn'] = soup.select_one('.nav-actions .btn').get_text(strip=True)
    h1 = soup.select_one('#hero-title'); c['h1'] = inner(h1)
    c['lead'] = T('.hero .lead')
    kb = soup.select_one('.kv-badge')
    c['badge'] = (kb.strong.get_text(strip=True), kb.select('span')[-1].get_text(' ', strip=True))
    c['kv_alt'] = soup.select_one('.kv img')['alt']
    c['bar'] = [(d.small.get_text(strip=True), d.strong.get_text(strip=True)) for d in soup.select('.event-bar > div')]
    c['logos_title'] = T('.logos-title')
    c['logos'] = [(i['src'], i['alt']) for i in soup.select('.logos img')]
    c['certs_line'] = T('.certs-row p')
    c['certs'] = [(i['src'], i['alt']) for i in soup.select('.certs img')]
    c['pillars'] = [li.get_text(strip=True) for li in soup.select('.pillars li')]
    c['fy_h'] = T('#fy-title')
    c['checks'] = [' '.join(li.get_text(' ', strip=True).split()) for li in soup.select('.check-grid li')]
    c['fy_btn'] = T('.foryou .btn')
    c['who_h'] = T('#about-title')
    ps = soup.select('.who-intro p'); c['who_p'] = ps[0].get_text(' ', strip=True); c['who_note'] = ps[1].get_text(' ', strip=True)
    c['points'] = [(li.strong.get_text(' ', strip=True), li.select('div > span')[0].get_text(' ', strip=True)) for li in soup.select('.points li')]
    c['svc_h'] = T('#svc-title'); c['svc_p'] = T('#services .sec-head p')
    c['help'] = [(a.h3.get_text(' ', strip=True), a.p.get_text(' ', strip=True)) for a in soup.select('.help-item')]
    c['why_h'] = T('#why-title'); c['why_p'] = T('#why .sec-head p')
    c['why'] = [(a.select_one('img')['src'].split('/')[-1], a.h3.get_text(' ', strip=True), a.p.get_text(' ', strip=True), a['data-accent']) for a in soup.select('.why-card')]
    c['why_hint'] = T('.why-hint'); c['why_foot'] = T('.why-foot p'); c['why_btn'] = T('.why-foot .btn')
    c['trust_h'] = T('#trust-title'); c['trust_p'] = T('#trust .sec-head p')
    c['stats'] = [(inner(s.b), s.span.get_text(' ', strip=True)) for s in soup.select('.stat')]
    c['quotes'] = [(q.p.get_text(' ', strip=True), q.footer.strong.get_text(strip=True), q.footer.span.get_text(strip=True), q.select_one('.stars')['aria-label']) for q in soup.select('.quote')]
    c['wael_alt'] = soup.select_one('.wael-photo img')['alt']
    tag = soup.select_one('.wael-photo .tag'); c['wael_tag'] = (tag.small.get_text(strip=True), tag.strong.get_text(strip=True))
    c['wael_h'] = T('#wael-title'); c['wael_role'] = T('.wael-copy .role')
    c['wael_p'] = soup.select('.wael-copy > p')[1].get_text(' ', strip=True)
    c['talk_h'] = T('.talk h4'); c['tags'] = [s.get_text(' ', strip=True) for s in soup.select('.tags span')]
    c['wael_btn'] = T('.wael-copy .btn')
    c['book_h'] = T('#book-title'); c['book_p'] = T('.book-side > p')
    c['benefits'] = [' '.join(li.get_text(' ', strip=True).split()) for li in soup.select('.benefits li')]
    c['ways'] = [(li.strong.get_text(' ', strip=True), li.select('div > span')[0].get_text(' ', strip=True)) for li in soup.select('.ways li')]
    cm = soup.select_one('.contact-mini'); c['contact'] = (cm.strong.get_text(strip=True), cm.select('div > span')[0].get_text(' ', strip=True))
    # form
    f = {}
    lab = lambda fid: soup.select_one(f'label[for="{fid}"]').find(string=True, recursive=False).strip()
    for fid in ('name', 'email', 'company', 'title', 'phone', 'country', 'msg'): f[fid] = lab(fid)
    f['optional'] = soup.select_one('label[for="phone"] .opt').get_text(strip=True)
    f['countries'] = [o.get_text(strip=True) for o in soup.select('#country option')]
    f['topics_label'] = T('.chips').strip() and soup.select('legend')[0].get_text(strip=True)
    f['topics'] = [(i['value'], i.find_next_sibling('span').get_text(strip=True)) for i in soup.select('.chips input')]
    f['timing_label'] = soup.select('legend')[1].get_text(strip=True)
    f['timing'] = [i.find_next_sibling('span').get_text(strip=True) for i in soup.select('.seg input')]
    f['placeholder'] = soup.select_one('#msg')['placeholder']
    f['submit'] = T('.submit-row .btn'); f['privacy'] = T('.privacy')
    f['success'] = T('.success h3') + ' ' + T('.success p')
    f['page_language'] = soup.select_one('input[name="page_language"]')['value']
    c['form'] = f
    c['close_h'] = inner(soup.select_one('#close-title')); c['close_p'] = T('.closing p')
    c['close_btns'] = [(a.get_text(strip=True), a['href']) for a in soup.select('.closing .btn')]
    fs = soup.select('footer.site span'); c['foot_mid'] = inner(fs[0]); c['foot_copy'] = fs[1].get_text(strip=True)
    c['mobile_cta'] = T('.mobile-cta span')
    return c

# ---------------------------------------------------------------- page
def build(c, css):
    lang = c['lang']; b = B(lang); _n[0] = 0
    img = lambda name: BASE + name
    DE = lang == 'de'

    # ---- header (sticky)
    lang_html = (f'<div class="lt-lang"><a href="{PAGE_URL["en"]}"{" class=\"is-active\"" if not DE else ""}>EN</a>'
                 f'<a href="{PAGE_URL["de"]}"{" class=\"is-active\"" if DE else ""}>DE</a></div>')
    header = b.con([
        b.con([
            b.image(img('assets/laoret-logo.png'), 'Laoret', width={'unit': 'px', 'size': 120, 'sizes': []}, link_to='custom',
                    link={'url': 'https://laoret.com', 'is_external': '', 'nofollow': ''}, width_mobile={'unit': 'px', 'size': 96, 'sizes': []}),
            b.heading('×', 'span', MUTED, typo('', LATO, 18, 400)),
            b.html(f'<img src="{TCWORLD_LOGO}" alt="tcworld conference" class="lt-event-logo">'),
        ], direction='row', flex_gap=gap(14), flex_gap_mobile=gap(8), css_classes='lt-brand', flex_align_items='center'),
        b.con([b.heading(t, 'div', NAVY, typo('', OPEN, 15, 400), link=h, _css_classes='lt-navlink') for t, h in c['nav']],
              direction='row', flex_gap=gap(28), flex_align_items='center', hide_tablet='hidden-tablet', hide_mobile='hidden-mobile'),
        b.con([b.html(lang_html), b.button(c['nav_btn'], '#book', size_pad=(11, 22), hide_mobile='hidden-mobile')],
              direction='row', flex_gap=gap(14), flex_align_items='center'),
    ], top=True, direction='row', flex_justify_content='space-between', flex_align_items='center', flex_wrap='nowrap',
        min_height=px(72), padding=box(0, 24), padding_mobile=box(0, 18),
        background_background='classic', background_color='rgba(255,255,255,0.94)',
        border_border='solid', border_width=box(0, 0, 1, 0), border_color=LINE, _element_id='top', css_classes='lt-header',
        sticky='top', sticky_on=['desktop', 'tablet', 'mobile'], z_index=50)

    # ---- hero
    hero_left = b.con([
        b.heading(c['h1'], 'h1', NAVY, DISPLAY(), _css_classes='lt-hero-title'),
        b.text(c['lead'], NAVY, INTRO(), _css_classes='lt-maxw-540'),
        b.con([b.button(c['hero_btns'][0], '#book', icon=True), b.button(c['hero_btns'][1], '#booth', 'outline')],
              direction='row', flex_gap=gap(14), flex_wrap='wrap', margin=box(12, 0, 0, 0)),
    ], flex_gap=gap(22), flex_justify_content='center')
    hero_right = b.con([
        b.image(img('assets/tekom-2026-keyvisual.jpg'), c['kv_alt'], width={'unit': '%', 'size': 100, 'sizes': []},
                height=400, fit='cover', radius=22, height_mobile=px(260),
                image_box_shadow_box_shadow_type='yes', image_box_shadow_box_shadow=shadow(0, 24, 60, 0, 'rgba(11,35,63,0.12)')),
        b.html(f'<img src="{TEKOM_LOGO}" alt="tekom Jahrestagung">', _css_classes='lt-kv-logos',
               _position='absolute', _offset_orientation_h='end', _offset_x_end=px(18), _offset_y=px(18), hide_mobile='hidden-mobile'),
        b.con([
            b.image(img('wael-makram.jpg'), 'Wael Makram', _css_classes='lt-avatar', width={'unit': 'px', 'size': 52, 'sizes': []}),
            b.con([b.heading(c['badge'][0], 'div', NAVY, H5()), b.text(c['badge'][1], MUTED, SMALL())], flex_gap=gap(2)),
        ], direction='row', flex_gap=gap(12), flex_align_items='center', padding=box(14, 18, 14, 14),
            position='absolute', _offset_orientation_h='start', _offset_x=px(-28), _offset_orientation_v='end', _offset_y=px(36),
            css_classes='lt-kv-badge', width={'unit': 'px', 'size': 300},
            **card(box_shadow_box_shadow=shadow(0, 24, 60, 0, 'rgba(11,35,63,0.12)'), border_radius=box(14))),
    ], css_classes='lt-hero-visual')
    icons = ['far fa-calendar-alt', 'fas fa-map-marker-alt', 'far fa-building', 'far fa-comments']
    bar = b.con([b.icon_box(icons[i], lab, val, title_t=CAPTION('title'), desc_t=H5('description'),
                            title_color=MUTED, desc_color=NAVY, size=26, _padding=box(22, 26), _css_classes='lt-bar-item')
                 for i, (lab, val) in enumerate(c['bar'])],
                grid=({'unit': 'fr', 'size': 4, 'sizes': []}, gap(0), {'unit': 'fr', 'size': 2, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
                css_classes='lt-event-bar', margin=box(64, 0, -60, 0), margin_mobile=box(40, 0, 0, 0), z_index=2,
                **card(border_border='solid', border_width=box(1), border_color=LINE, border_radius=box(16)))
    hero = b.con([
        b.con([hero_left, hero_right], grid=({'unit': 'custom', 'size': '1.1fr 0.9fr', 'sizes': []}, gap(48, 56), {'unit': 'fr', 'size': 1, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
              grid_align_items='center'),
        bar,
    ], top=True, padding=box(72, 24, 0, 24), padding_mobile=box(48, 18, 0, 18), flex_gap=gap(0),
        background_background='gradient', background_color='#FFFFFF', background_color_stop={'unit': '%', 'size': 35, 'sizes': []},
        background_color_b=AQUA, background_gradient_type='linear', background_gradient_angle={'unit': 'deg', 'size': 180, 'sizes': []},
        _element_id='hero')

    # ---- proof strip
    proof = b.con([
        b.heading(c['logos_title'], 'p', MUTED, CAPTION(), align='center'),
        b.con([b.image(u, a, width={'unit': '%', 'size': 100, 'sizes': []}, height=84, fit='cover', _css_classes='lt-logo') for u, a in c['logos']],
              grid=({'unit': 'fr', 'size': 7, 'sizes': []}, gap(28, 56), {'unit': 'fr', 'size': 4, 'sizes': []}, {'unit': 'fr', 'size': 2, 'sizes': []}),
              grid_gaps_mobile=gap(24, 40), **anim(True)),
        b.con([
            b.heading(c['certs_line'], 'p', MUTED, CAPTION()),
            b.con([b.image(u, a, width={'unit': 'px', 'size': 'auto', 'sizes': []}, height=58, fit='contain', _css_classes='lt-cert') for u, a in c['certs']],
                  direction='row', flex_gap=gap(22), flex_wrap='wrap', flex_justify_content='center', flex_align_items='center'),
        ], direction='row', flex_gap=gap(28, 40), flex_wrap='wrap', flex_justify_content='center', flex_align_items='center',
            padding=box(28, 0, 0, 0), border_border='solid', border_width=box(1, 0, 0, 0), border_color=LINE, margin=box(14, 0, 0, 0), **anim(True)),
    ], top=True, flex_gap=gap(22), padding=box(110, 24, 48, 24), padding_mobile=box(48, 18, 40, 18),
        border_border='solid', border_width=box(0, 0, 1, 0), border_color=LINE)

    # ---- this page is for you if (dark)
    pill = lambda t, acc: b.heading(t, 'div', '#FFFFFF', typo('', LATO, 15, 700), _css_classes='lt-pill',
                                    _padding=box(8, 16), _border_border='solid', _border_width=box(1.5), _border_color=acc,
                                    _border_radius=box(999), _background_background='classic', _background_color='rgba(255,255,255,0.06)')
    checks = []
    for i, t in enumerate(c['checks']):
        checks.append(b.con([b.icon_box('far fa-check-circle', t, '', title_t=BODY_('title'), icon_color=CYAN, title_color='#E6EEF5', size=22)],
                            padding=box(22, 24), background_background='classic', background_color='rgba(255,255,255,0.05)',
                            border_border='solid', border_width=box(1), border_color='rgba(255,255,255,0.1)', border_radius=box(12),
                            **anim(True, (i % 2) * 100)))
    foryou = b.con([
        b.con([pill(t, ['rgba(0,192,207,0.55)', 'rgba(240,90,92,0.6)', 'rgba(0,192,207,0.55)'][i]) for i, t in enumerate(c['pillars'])],
              direction='row', flex_gap=gap(10), flex_wrap='wrap', flex_justify_content='center', **anim(True)),
        b.heading(c['fy_h'], 'h2', '#FFFFFF', H2(), align='center', _margin=box(22, 0, 44, 0), **anim()),
        b.con(checks, grid=({'unit': 'fr', 'size': 2, 'sizes': []}, gap(16), None, {'unit': 'fr', 'size': 1, 'sizes': []}),
              css_classes='lt-maxw-980'),
        b.con([b.button(c['fy_btn'], '#book', 'cyan')], flex_align_items='center', margin=box(44, 0, 0, 0)),
    ], top=True, padding=box(96, 24), padding_mobile=box(72, 18), background_background='classic', background_color=DARK,
        css_classes='lt-dark-band', overflow='hidden')

    # ---- who we are
    pts = []
    for i, (h, s) in enumerate(c['points']):
        pts.append(b.con([
            b.heading(f'0{i+1}', 'div', BRAND, typo('', OPEN, 14, 700), _css_classes='lt-num' + (' lt-num-coral' if i % 2 else '')),
            b.con([b.heading(h, 'h3', NAVY, H4()), b.text(s, BODY, BODY_())], flex_gap=gap(4)),
        ], direction='row', flex_gap=gap(20), padding=box(22, 24), css_classes='lt-point', **card(), **anim(True, i * 100)))
    who = b.con([
        b.con([
            b.heading(c['who_h'], 'h2', NAVY, H2()),
            b.text(c['who_p'], BODY, BODY_L()),
            b.text(c['who_note'], NAVY, BODY_L(), _padding=box(4, 0, 4, 18), _border_border='solid',
                   _border_width=box(0, 0, 0, 3), _border_color=BRAND),
        ], flex_gap=gap(18), **anim(True)),
        b.con(pts, flex_gap=gap(14)),
    ], top=True, grid=({'unit': 'custom', 'size': '0.9fr 1.1fr', 'sizes': []}, gap(48, 72), {'unit': 'fr', 'size': 1, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
        padding=box(96, 24), padding_mobile=box(72, 18), _element_id='about')

    # ---- what we help with
    coral_rows = {1, 2, 5}
    helps = []
    for i, (h, p) in enumerate(c['help']):
        col = CORAL if i in coral_rows else BRAND
        helps.append(b.con([
            b.heading(f'0{i+1}', 'div', col, CAPTION(), _padding=box(4, 0, 0, 0)),
            b.con([b.heading(h, 'h3', NAVY, H3()), b.text(p, BODY, BODY_(), _css_classes='lt-maxw-440')], flex_gap=gap(8)),
        ], grid=({'unit': 'custom', 'size': '56px 1fr', 'sizes': []}, gap(6), None, {'unit': 'custom', 'size': '44px 1fr', 'sizes': []}),
            padding=box(30, 0), padding_mobile=box(24, 0), border_border='solid',
            border_width=box(1, 0, 1 if i >= len(c['help']) - 2 else 0, 0), border_color=LINE,
            css_classes='lt-help-item' + (' lt-acc-coral' if i in coral_rows else ''), **anim(True, (i % 2) * 100)))
    services = b.con([
        b.heading(c['svc_h'], 'h2', NAVY, H2(), align='center', **anim()),
        b.text(c['svc_p'], NAVY, INTRO(), align='center', _css_classes='lt-maxw-720', _margin=box(14, 0, 56, 0), **anim()),
        b.con(helps, grid=({'unit': 'fr', 'size': 2, 'sizes': []}, gap(0, 72), None, {'unit': 'fr', 'size': 1, 'sizes': []}),
              grid_gaps_tablet=gap(0, 48), css_classes='lt-maxw-1080'),
    ], top=True, padding=box(96, 24), padding_mobile=box(72, 18), background_background='classic', background_color=SOFT,
        flex_gap=gap(0), _element_id='services')

    # ---- why meet (illustrated)
    acc_col = {'teal': BRAND, 'coral': CORAL, 'navy': NAVY}
    acc_cls = {'teal': '', 'coral': ' lt-acc-coral', 'navy': ' lt-acc-navy'}
    cards = []
    for i, (fname, h, p, acc) in enumerate(c['why']):
        cards.append(b.con([
            b.image(img('assets/' + fname), '', width={'unit': '%', 'size': 100, 'sizes': []}, height=260, fit='contain', radius=10,
                    _css_classes='lt-why-visual', _background_background='classic', _background_color='#F6F9FB', _border_radius=box(10),
                    height_tablet=px(240), height_mobile=px(220)),
            b.con([
                b.heading(f'0{i+1}', 'div', acc_col[acc], CAPTION()),
                b.heading(h, 'h3', NAVY, H4()),
                b.text(p, BODY, BODY_()),
            ], flex_gap=gap(8), padding=box(22, 16, 18, 16)),
        ], padding=box(12), css_classes='lt-why-card' + acc_cls[acc], **card(border_radius=box(14)), **anim(True, i * 120)))
    why = b.con([
        b.heading(c['why_h'], 'h2', NAVY, H2(), align='center', **anim()),
        b.text(c['why_p'], NAVY, INTRO(), align='center', _css_classes='lt-maxw-720', _margin=box(14, 0, 56, 0), **anim()),
        b.con(cards, grid=({'unit': 'fr', 'size': 3, 'sizes': []}, gap(28), {'unit': 'fr', 'size': 2, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
              css_classes='lt-why-grid'),
        b.heading(c['why_hint'], 'p', MUTED, CAPTION(), align='center', hide_desktop='hidden-desktop', hide_tablet='hidden-tablet', _margin=box(4, 0, 0, 0)),
        b.text(c['why_foot'], NAVY, BODY_L(), align='center', _css_classes='lt-maxw-680', _margin=box(48, 0, 22, 0), **anim()),
        b.con([b.button(c['why_btn'], '#book')], flex_align_items='center'),
    ], top=True, padding=box(96, 24), padding_mobile=box(72, 18), flex_gap=gap(0), _element_id='why')

    # ---- trust: stats + testimonials
    stats = [b.con([b.heading(v, 'div', NAVY, typo('', OPEN, 34, 700, 1.1, -0.02, size_m=28), align='center', _css_classes='lt-stat'),
                    b.text(l, BODY, SMALL(), align='center')], flex_gap=gap(8), padding=box(30, 20), **card(), **anim(True, i * 100))
             for i, (v, l) in enumerate(c['stats'])]
    quotes = [b.con([b.text('★★★★★', CORAL, typo('', LATO, 15, 400, ls=0.12), _css_classes='lt-stars'),
                     b.text(q, NAVY, BODY_(), _css_classes='lt-grow'),
                     b.con([b.heading(n, 'div', NAVY, H5()), b.text(r, MUTED, SMALL())], flex_gap=gap(2))],
                    flex_gap=gap(14), padding=box(30, 28), flex_justify_content='space-between', **card(), **anim(True, i * 100))
              for i, (q, n, r, st) in enumerate(c['quotes'])]
    trust = b.con([
        b.heading(c['trust_h'], 'h2', NAVY, H2(), align='center', **anim()),
        b.text(c['trust_p'], NAVY, INTRO(), align='center', _css_classes='lt-maxw-720', _margin=box(14, 0, 56, 0), **anim()),
        b.con(stats, grid=({'unit': 'fr', 'size': 4, 'sizes': []}, gap(24), {'unit': 'fr', 'size': 2, 'sizes': []}, {'unit': 'fr', 'size': 2, 'sizes': []}),
              grid_gaps_mobile=gap(14), margin=box(0, 0, 64, 0)),
        b.con(quotes, grid=({'unit': 'fr', 'size': 3, 'sizes': []}, gap(24), {'unit': 'fr', 'size': 2, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []})),
    ], top=True, padding=box(96, 24), padding_mobile=box(72, 18), flex_gap=gap(0),
        background_background='classic', background_color=SOFT, _element_id='trust')

    # ---- meet wael
    tag_pill = lambda t: b.heading(t, 'div', NAVY, typo('', LATO, 16, 400), _padding=box(8, 15), _border_border='solid', _border_width=box(1),
                                   _border_color='#D2F0F2', _border_radius=box(999), _background_background='classic', _background_color='#EBF8F9')
    wael = b.con([
        b.con([
            b.image(img('wael-makram.jpg'), c['wael_alt'], width={'unit': '%', 'size': 100, 'sizes': []}, height=440, fit='cover', radius=24,
                    height_mobile=px(340), image_box_shadow_box_shadow_type='yes', image_box_shadow_box_shadow=shadow(0, 24, 60, 0, 'rgba(11,35,63,0.12)'),
                    **{'object-position': 'center center'}),
            b.con([b.heading(c['wael_tag'][0], 'div', CYAN, CAPTION()), b.heading(c['wael_tag'][1], 'div', '#FFFFFF', typo('', OPEN, 15, 700))],
                  flex_gap=gap(2), padding=box(14, 18), background_background='classic', background_color=DARK, border_radius=box(14),
                  position='absolute', _offset_orientation_h='end', _offset_x_end=px(-18), _offset_orientation_v='end', _offset_y_end=px(28),
                  _offset_x_end_mobile=px(12), width={'unit': 'px', 'size': 'auto'},
                  box_shadow_box_shadow_type='yes', box_shadow_box_shadow=shadow(0, 24, 60, 0, 'rgba(11,35,63,0.2)')),
        ], css_classes='lt-wael-photo', **anim(True)),
        b.con([
            b.heading(c['wael_h'], 'h2', NAVY, H2()),
            b.heading(c['wael_role'], 'p', BRAND, typo('', OPEN, 16, 600)),
            b.text(c['wael_p'], BODY, BODY_L(), _margin=box(10, 0, 8, 0)),
            b.heading(c['talk_h'], 'h4', NAVY, H6()),
            b.con([tag_pill(t) for t in c['tags']], direction='row', flex_gap=gap(10), flex_wrap='wrap', margin=box(0, 0, 18, 0)),
            b.con([b.button(c['wael_btn'], '#book', icon=True)], flex_align_items='flex-start'),
        ], flex_gap=gap(12), **anim(True, 120)),
    ], top=True, grid=({'unit': 'custom', 'size': '0.8fr 1.2fr', 'sizes': []}, gap(48, 64), {'unit': 'fr', 'size': 1, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
        grid_align_items='center', padding=box(96, 24), padding_mobile=box(72, 18), _element_id='wael')

    # ---- book a meeting (form)
    f = c['form']
    def fld(ftype, label, cid, width='50', required=True, **extra):
        d = {'_id': uid(lang), 'field_type': ftype, 'field_label': label, 'custom_id': cid, 'width': width,
             'required': 'true' if required else '', 'placeholder': ''}
        d.update(extra); return d
    countries = '\n'.join([f'{f["countries"][0]}|'] + f['countries'][1:])
    form_fields = [
        fld('text', f['name'], 'full_name'),
        fld('email', f['email'], 'work_email'),
        fld('text', f['company'], 'company'),
        fld('text', f['title'], 'job_title'),
        fld('tel', f'{f["phone"]} {f["optional"]}', 'phone', required=False),
        fld('select', f['country'], 'country', field_options=countries),
        fld('checkbox', f['topics_label'], 'topics', '100', False,
            field_options='\n'.join(f'{lbl}|{val}' for val, lbl in f['topics']), inline_list='elementor-subgroup-inline'),
        fld('radio', f['timing_label'], 'timing', '100', False,
            field_options='\n'.join(f'{lbl}|{val}' for val, lbl in zip(['During the event', 'After the event', 'Either works'], f['timing'])),
            inline_list='elementor-subgroup-inline', field_value='During the event'),
        fld('textarea', f'{f["msg"]} {f["optional"]}', 'message', '100', False, rows=4, placeholder=f['placeholder']),
        fld('hidden', 'page_language', 'page_language', '100', False, field_value=f['page_language']),
    ]
    form = b.w('form',
        form_name=f'tcworld 2026 meeting request ({lang.upper()})',
        form_fields=form_fields, input_size='md', show_labels='yes', mark_required='yes',
        button_text=f['submit'], button_size='md', button_width='100', button_align='stretch',
        selected_button_icon={'value': 'fas fa-arrow-right', 'library': 'fa-solid'}, button_icon_align='row-reverse',
        submit_actions=['email', 'collect_submissions'],
        email_subject=('Neue Terminanfrage tcworld 2026' if DE else 'New tcworld 2026 meeting request'),
        success_message=f['success'], form_id=f'tcworld2026_{lang}',
        column_gap=px(20), row_gap=px(18), label_spacing=px(7), label_color=NAVY, mark_required_color=CORAL,
        **H6('label'), **BODY_('field'),
        field_text_color=NAVY, field_background_color='#FBFDFE', field_border_color=LINE, field_border_width=box(1.5),
        field_border_radius=box(10),
        button_background_color=BRAND, button_text_color='#FFFFFF', button_background_hover_color=BRAND_D, button_hover_color='#FFFFFF',
        button_border_radius=box(999), button_text_padding=box(17, 30), **typo('button', OPEN, 16, 700),
        _css_classes='lt-form lt-btn-glow')
    book = b.con([
        b.con([
            b.heading(c['book_h'], 'h2', NAVY, H2()),
            b.text(c['book_p'], BODY, BODY_L(), _margin=box(4, 0, 10, 0)),
            b.w('icon-list', icon_list=[{'_id': uid(lang), 'text': t, 'selected_icon': {'value': 'far fa-check-circle', 'library': 'fa-regular'}} for t in c['benefits']],
                space_between=px(14), icon_color=NAVY, icon_size=px(20), text_color=NAVY, text_indent=px(10), icon_self_vertical_align='flex-start',
                **BODY_L('icon')),
            b.con([b.con([b.icon_box(ic, t, d, size=28)], padding=box(16, 18), **card())
                   for ic, (t, d) in zip(['fas fa-map-marker-alt', 'far fa-envelope'], c['ways'])],
                  flex_gap=gap(12), margin=box(16, 0, 8, 0), _element_id='booth'),
            b.con([b.image(img('wael-makram.jpg'), 'Wael Makram', _css_classes='lt-avatar', width={'unit': 'px', 'size': 52, 'sizes': []}),
                   b.con([b.heading(c['contact'][0], 'div', NAVY, H5()), b.text(c['contact'][1], MUTED, SMALL())], flex_gap=gap(2))],
                  direction='row', flex_gap=gap(14), flex_align_items='center', padding=box(18), **card()),
        ], flex_gap=gap(14), **anim(True)),
        b.con([form, b.text(f'<p>🔒 {f["privacy"]}</p>', MUTED, SMALL(), align='center', _margin=box(14, 0, 0, 0))],
              padding=box(40), padding_mobile=box(26, 20), **card(border_radius=box(14), box_shadow_box_shadow=shadow(0, 18, 50, 0, 'rgba(11,35,63,0.1)')),
              **anim(True, 120)),
    ], top=True, grid=({'unit': 'custom', 'size': '0.85fr 1.15fr', 'sizes': []}, gap(48, 56), {'unit': 'fr', 'size': 1, 'sizes': []}, {'unit': 'fr', 'size': 1, 'sizes': []}),
        padding=box(96, 24), padding_mobile=box(72, 18), _element_id='book',
        background_background='gradient', background_color=SOFT, background_color_b='#FFFFFF',
        background_gradient_angle={'unit': 'deg', 'size': 180, 'sizes': []})

    # ---- closing (dark)
    closing = b.con([
        b.heading(c['close_h'], 'h2', '#FFFFFF', H2(), align='center', _css_classes='lt-closing-title'),
        b.text(c['close_p'], '#C9D5E1', BODY_L(), align='center', _margin=box(14, 0, 30, 0)),
        b.con([b.button(c['close_btns'][0][0], '#book', 'cyan'), b.button(c['close_btns'][1][0], c['close_btns'][1][1], 'light')],
              direction='row', flex_gap=gap(14), flex_wrap='wrap', flex_justify_content='center'),
    ], top=True, padding=box(88, 24), padding_mobile=box(72, 18), background_background='classic', background_color=DARK,
        css_classes='lt-dark-band', overflow='hidden', flex_gap=gap(0))

    # ---- footer
    footer = b.con([
        b.image(img('assets/laoret-logo.png'), 'Laoret', width={'unit': 'px', 'size': 92, 'sizes': []}),
        b.text(f'<p>{c["foot_mid"]}</p>', BODY, SMALL(), _css_classes='lt-footer-links'),
        b.text(c['foot_copy'], BODY, SMALL()),
    ], top=True, direction='row', flex_justify_content='space-between', flex_align_items='center', flex_wrap='wrap', flex_gap=gap(20),
        padding=box(32, 24), padding_mobile=box(32, 18, 96, 18), border_border='solid', border_width=box(1, 0, 0, 0), border_color=LINE,
        background_background='classic', background_color='#FFFFFF')

    # ---- mobile sticky CTA
    mobile_cta = b.con([
        b.heading(c['mobile_cta'], 'div', '#FFFFFF', typo('', OPEN, 14, 600)),
        b.button(c['nav_btn'], '#book', 'cyan', size_pad=(11, 18)),
    ], top=True, direction='row', flex_justify_content='space-between', flex_align_items='center',
        padding=box(8, 8, 8, 20), margin=box(0, 12, 12, 12), css_classes='lt-mobile-cta', background_background='classic', background_color=DARK, border_radius=box(999),
        hide_desktop='hidden-desktop', hide_tablet='hidden-tablet', sticky='bottom', sticky_on=['mobile'], sticky_offset=12, z_index=60,
        box_shadow_box_shadow_type='yes', box_shadow_box_shadow=shadow(0, 24, 60, 0, 'rgba(11,35,63,0.25)'))

    content = [header, hero, proof, foryou, who, services, why, trust, wael, book, closing, footer, mobile_cta]
    return {
        'content': content,
        'page_settings': {'template': 'elementor_canvas', 'hide_title': 'yes', 'custom_css': css,
                          'background_background': 'classic', 'background_color': '#FFFFFF'},
        'version': '0.4',
        'title': c['title'],
        'type': 'page',
    }

EXTRA_CSS = '''
/* ===== Page-level styles used by the template (classes set in Advanced → CSS Classes) ===== */
html{scroll-behavior:smooth;scroll-padding-top:84px}
.elementor-widget-text-editor p:last-child{margin-bottom:0}
.lt-maxw-540{max-width:540px}.lt-maxw-440{max-width:440px}.lt-maxw-680,.lt-maxw-720,.lt-maxw-980,.lt-maxw-1080{margin-left:auto!important;margin-right:auto!important}
.lt-maxw-680{max-width:680px}.lt-maxw-720{max-width:720px}.lt-maxw-980{max-width:980px}.lt-maxw-1080{max-width:1080px}
/* Header */
.elementor .lt-brand img.lt-event-logo{height:32px;width:auto;max-width:none;display:block}
@media (max-width:767px){.elementor .lt-brand img.lt-event-logo{height:20px;max-width:110px;object-fit:contain}.lt-brand{min-width:0;flex-shrink:1;overflow:hidden}.lt-lang a{padding:5px 8px}}
.lt-mobile-cta.e-con{--width:auto;width:auto}
.lt-header>.e-con-inner>.e-con{--width:auto;width:auto;flex:0 1 auto}
.lt-navlink .elementor-heading-title a{position:relative;padding:6px 0;color:inherit}
.lt-navlink .elementor-heading-title a::after{content:"";position:absolute;left:0;bottom:0;height:2px;width:0;background:var(--lt-teal);transition:width .2s}
.lt-navlink .elementor-heading-title a:hover{color:var(--lt-teal)}
.lt-navlink .elementor-heading-title a:hover::after{width:100%}
.lt-lang{display:flex;gap:2px;border:1px solid var(--lt-line);border-radius:999px;padding:3px;font:600 13px/1 "Open Sans",sans-serif;background:#fff}
.lt-lang a{padding:6px 11px;border-radius:999px;color:#7A8898}
.lt-lang a.is-active{background:var(--lt-teal);color:#fff}
/* Hero */
.lt-hero-title .elementor-heading-title span{display:block;color:var(--lt-coral)}
.lt-closing-title .elementor-heading-title span{color:var(--lt-coral)}
.lt-kv-logos{background:#fff;border-radius:12px;padding:10px 14px;box-shadow:0 10px 30px rgba(11,35,63,.07)}
.elementor .lt-kv-logos img{height:26px;width:auto;max-width:none;display:block}
@media (max-width:767px){.lt-kv-badge{position:relative!important;inset:auto!important;margin:-36px 16px 0!important;width:auto!important;max-width:none!important}}
.elementor .lt-avatar img{width:52px!important;height:52px!important;border-radius:50%;object-fit:cover}
.lt-bar-item+.lt-bar-item{border-left:1px solid var(--lt-line)}
@media (max-width:1024px){.lt-bar-item:nth-child(3){border-left:0}.lt-bar-item:nth-child(n+3){border-top:1px solid var(--lt-line)}}
@media (max-width:767px){.lt-bar-item+.lt-bar-item{border-left:0;border-top:1px solid var(--lt-line)}}
.lt-cert img{height:58px!important;width:auto!important}
@media (max-width:767px){.lt-cert img{height:46px!important}}
/* Who we are: number badges */
.lt-num .elementor-heading-title{width:38px;height:38px;border-radius:50%;background:var(--lt-aqua);display:grid;place-items:center}
.lt-num-coral .elementor-heading-title{background:#FDEEEE;color:var(--lt-coral)!important}
.lt-point{transition:box-shadow .2s}.lt-point:hover{box-shadow:0 16px 36px rgba(11,35,63,.1)!important}
/* Stats, testimonials */
.lt-stat .elementor-heading-title em{font-style:normal;color:var(--lt-coral)}
.lt-grow{flex-grow:1}
/* Wael */
.lt-wael-photo{position:relative}
.lt-wael-photo::before{content:"";position:absolute;width:90px;height:90px;left:-24px;top:-24px;border-radius:50%;border:10px solid var(--lt-coral);opacity:.15;z-index:0}
.lt-wael-photo img{object-position:center 20%}
/* Footer links */
.lt-footer-links a{color:var(--lt-navy)}.lt-footer-links a:hover{color:var(--lt-teal)}
/* Button on dark band */
.lt-btn-light .elementor-button{box-shadow:0 0 20px rgba(0,192,207,.22)}
'''

def main():
    base_css = open(os.path.join(HERE, 'laoret-tcworld.css'), encoding='utf-8').read()
    css = base_css + EXTRA_CSS
    for lang, src in (('en', '../index.html'), ('de', '../de/index.html')):
        c = extract(os.path.join(HERE, src))
        tpl = build(c, css)
        out = os.path.join(HERE, f'laoret-tcworld-2026-{lang}.json')
        with open(out, 'w', encoding='utf-8') as fh:
            json.dump(tpl, fh, ensure_ascii=False, indent=1)
        print(out, os.path.getsize(out), 'bytes')

if __name__ == '__main__':
    main()
