# -*- coding: utf-8 -*-
"""Générateur du site PROSERVICE 83.

Usage : python3 src/build.py
Produit le site statique complet dans ./public (pages, sitemap.xml, robots.txt, llms.txt…).
Aucune dépendance externe.
"""
import html
import json
import os
import shutil
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
import data_business as B  # noqa: E402
from data_cities import CITIES, CITY_BY_SLUG, ALL_CITIES, EXTRA_CITIES, SECTORS  # noqa: E402
from data_guides import GUIDES  # noqa: E402
from data_services import SERVICES, SERVICE_ICONS, ASSURANCE_PAGE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public")
SRC_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
TODAY = date.today().isoformat()
SITE = B.SITE_URL.rstrip("/")
SCHEMA_TYPE = "Locksmith"  # type schema.org de l'entreprise
WARNINGS = []  # éléments à compléter, rappelés à la fin du build
def _file_hash(*names):
    import hashlib
    h = hashlib.md5()
    for n in names:
        with open(os.path.join(SRC_ASSETS, n), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:10]


# Version des fichiers CSS/JS calculée à partir de leur contenu : chaque modification
# change l'URL, ce qui force les navigateurs à recharger la nouvelle version.
ASSET_VERSION = _file_hash("style.css", "main.js")

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}
CORE_CITIES = [c for c in CITIES if c["core"]]
# Communes du menu « Zones » : communes principales + celles marquées "menu" (agglomération toulonnaise).
MENU_CITIES = CORE_CITIES + [c for c in CITIES if c.get("menu") and not c["core"]]
PAGES = []  # (chemin, priorité) pour le sitemap


def esc(s):
    return html.escape(s, quote=True)


def strip_tags(s):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def abs_url(path):
    return SITE + path


def city_path(c):
    return "/serrurier-%s/" % c["slug"]


def combo_path(s, c):
    return "/%s-%s/" % (s["combo"], c["slug"])


def service_path(s):
    return "/%s/" % s["slug"]


def guide_path(g):
    return "/conseils/%s/" % g["slug"]


def delay_label(c):
    return "sur place" if c["delay"] == 0 else "~%d min" % c["delay"]


def delay_sentence(c):
    if c["delay"] == 0:
        return "Notre base est à Vidauban : nous y intervenons sans délai de route, souvent dans l'heure."
    return "Comptez environ %d minutes pour notre arrivée %s, hors trafic. Le délai précis vous est donné au moment de l'appel." % (c["delay"], c["a"])


def delay_txt(c):
    return "Intervention rapide" if c["delay"] == 0 else "Arrivée estimée ~%d min" % c["delay"]


def picture(name, alt, width, height, sizes, cls="", attrs=""):
    """Image en <picture> : variantes WebP (assets/img/webp/, créées par src/make_webp.py) + JPEG de secours."""
    import glob
    base = os.path.splitext(name)[0]
    widths = sorted(int(os.path.basename(f)[len(base) + 1:-5]) for f in glob.glob(os.path.join(SRC_ASSETS, "img", "webp", base + "-*.webp"))
                    if os.path.basename(f)[len(base) + 1:-5].isdigit())
    img = '<img%s src="/assets/img/%s" alt="%s" width="%d" height="%d"%s>' % (' class="%s"' % cls if cls else "", name, esc(alt), width, height, attrs)
    if not widths:
        return img
    srcset = ", ".join("/assets/img/webp/%s-%d.webp %dw" % (base, w, w) for w in widths)
    return '<picture><source type="image/webp" srcset="%s" sizes="%s">%s</picture>' % (srcset, sizes, img)


# ---------------------------------------------------------------- tarifs
def eur(v):
    return ("%d" % v if float(v).is_integer() else ("%.2f" % v).replace(".", ",")) + "\u00a0€"


def pct(coef):
    return "+%d\u00a0%%" % round((coef - 1) * 100)


def period_coef(pid):
    return {p: coef for p, _, coef in B.RATE_PERIODS}[pid]


def deplacement_txt():
    if B.DEPLACEMENT is True:
        return "inclus dans le prix"
    if B.DEPLACEMENT:
        return "%s TTC" % eur(B.DEPLACEMENT)
    return "annoncé au téléphone, avant le départ"


def majorations():
    """[(créneau, majoration)] : soir, nuit, dimanche et jours fériés."""
    d, e, n = B.RATE_DAY_START, B.RATE_EVENING_START, B.RATE_NIGHT_START
    return [("Soir, %dh – %dh (lun-sam)" % (e, n), pct(period_coef("soir"))),
            ("Nuit, %dh – %dh" % (n, d), pct(period_coef("nuit"))),
            ("Dimanche et jour férié", pct(B.RATE_SUNDAY_COEF))]


def majorations_sentence():
    m = majorations()
    return ("Prix TTC en journée (lun-sam, %dh – %dh), majorés de %s le soir (%dh – %dh), de %s la nuit (%dh – %dh) "
            "et de %s les dimanches et jours fériés." % (B.RATE_DAY_START, B.RATE_EVENING_START, m[0][1].replace("+", ""),
                                                        B.RATE_EVENING_START, B.RATE_NIGHT_START, m[1][1].replace("+", ""),
                                                        B.RATE_NIGHT_START, B.RATE_DAY_START, m[2][1].replace("+", "")))


def price_conditions_html(cls="price-conds"):
    items = [("Prix", "TTC, en journée (lun-sam, %dh – %dh)" % (B.RATE_DAY_START, B.RATE_EVENING_START)),
             ("Déplacement", deplacement_txt())]
    if B.TAUX_HORAIRE:
        items.append(("Main-d'œuvre", "%s TTC de l'heure" % eur(B.TAUX_HORAIRE)))
    items += [("Majoration " + label[0].lower() + label[1:], val) for label, val in majorations()]
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li><b>%s</b><span>%s</span></li>" % (esc(k), esc(v)) for k, v in items))


def delay_faq():
    """Réponse « En combien de temps arrivez-vous ? » construite à partir des délais de data_cities.py."""
    groups = {}
    for slug in ["le-muy", "les-arcs-sur-argens", "le-cannet-des-maures", "le-luc", "la-garde-freinet", "gonfaron",
                 "draguignan", "frejus", "saint-raphael", "hyeres", "toulon"]:
        c = CITY_BY_SLUG.get(slug)
        if c:
            groups.setdefault(c["delay"], []).append(c["name"])
    parts = []
    for d in sorted(groups):
        ns = groups[d]
        parts.append("%d minutes pour %s" % (d, ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " ou " + ns[-1]))
    return ("Selon votre commune, comptez environ %s, hors trafic. Ces délais sont indicatifs : "
            "le délai précis vous est donné au moment de l'appel, avant tout déplacement." % ", ".join(parts))


# ---------------------------------------------------------------- icônes
PHONE_SVG = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6.6 10.8c1.5 3 3.9 5.4 6.9 6.9l2.3-2.3c.3-.3.7-.4 1.1-.2 1.2.4 2.5.6 3.9.6.6 0 1 .4 1 1V21c0 .6-.4 1-1 1C10.6 22 2 13.4 2 3c0-.6.4-1 1-1h4.2c.6 0 1 .4 1 1 0 1.4.2 2.7.6 3.9.1.4 0 .8-.2 1.1L6.6 10.8Z" {paint}/></svg>'


def phone_icon(size=16, filled=False):
    paint = 'fill="currentColor"' if filled else 'stroke="currentColor" stroke-width="1.8"'
    return PHONE_SVG.format(s=size, paint=paint)


def svc_icon(key, size=24):
    return '<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" aria-hidden="true">%s</svg>' % (size, size, SERVICE_ICONS[key])


LOGO_SVG = '<svg class="logo-mark" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#ffd400"/><circle cx="32" cy="32" r="24.5" fill="none" stroke="#111" stroke-width="2.2"/><g transform="translate(20 9.5)"><circle cx="12" cy="9.6" r="3.9" fill="#111"/><path d="M10 11.8 8.6 19.6h6.8L14 11.8Z" fill="#111"/></g><text x="32" y="47" text-anchor="middle" font-family="Space Grotesk, Arial, sans-serif" font-weight="700" font-size="12.5" fill="#111">24/7</text></svg>'


# ---------------------------------------------------------------- données structurées
def business_schema():
    area = [{"@type": "City", "name": c["name"], "postalCode": c["cp"]} for c in CITIES]
    area.append({"@type": "AdministrativeArea", "name": "Var (83)"})
    address = {
        "@type": "PostalAddress",
        "addressLocality": B.ADDRESS_CITY,
        "postalCode": B.ADDRESS_CP,
        "addressRegion": B.REGION,
        "addressCountry": "FR",
    }
    if B.ADDRESS_STREET:
        address["streetAddress"] = B.ADDRESS_STREET
    data = {
        "@context": "https://schema.org",
        "@type": SCHEMA_TYPE,
        "@id": SITE + "/#entreprise",
        "name": B.NAME,
        "legalName": B.LEGAL_NAME,
        "description": "Artisan serrurier intervenant dans tout le Var (83). Dépannage serrurerie 24h/24 et 7j/7 : ouverture de porte, changement de serrure, porte blindée, reproduction de clés, serrure connectée, rideaux métalliques et sécurisation après effraction.",
        "url": SITE + "/",
        "telephone": B.PHONE_TEL,
        "email": B.EMAIL,
        "image": SITE + "/assets/og-image.png",
        "logo": SITE + "/assets/logo-512.png",
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "foundingDate": str(B.SINCE),
        "address": address,
        "geo": {"@type": "GeoCoordinates", "latitude": B.GEO[0], "longitude": B.GEO[1]},
        "areaServed": area,
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        }],
        "knowsAbout": ["Serrurerie", "Ouverture de porte", "Changement de serrure", "Porte blindée",
                       "Reproduction de clés", "Serrure connectée", "Rideau métallique", "Sécurisation après effraction"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Prestations de serrurerie",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": abs_url(service_path(s))}}
                for s in SERVICES
            ],
        },
    }
    same_as = [u for u in [B.GOOGLE_BUSINESS_URL] + list(B.SAME_AS) if u]
    if same_as:
        data["sameAs"] = same_as
    if B.SIRET:
        data["identifier"] = {"@type": "PropertyValue", "propertyID": "SIRET", "value": B.SIRET.replace(" ", "")}
    if B.TVA:
        data["vatID"] = B.TVA.replace(" ", "")
    return data


def breadcrumb_schema(crumbs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(path)}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def faq_schema(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in faq
        ],
    }


def service_schema(name, desc, path, area_name, price_min=None):
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "serviceType": name,
        "description": desc,
        "url": abs_url(path),
        "provider": {"@id": SITE + "/#entreprise"},
        "areaServed": {"@type": "City" if area_name != "Var (83)" else "AdministrativeArea", "name": area_name},
        "availableChannel": {"@type": "ServiceChannel", "servicePhone": B.PHONE_TEL},
    }
    if price_min:
        data["offers"] = {"@type": "Offer", "priceCurrency": "EUR",
                          "priceSpecification": {"@type": "PriceSpecification", "minPrice": price_min, "priceCurrency": "EUR"}}
    return data


# ---------------------------------------------------------------- gabarit
NAV = [
    ("Prestations", "/prestations/"),
    ("Zones", "/zones-intervention/"),
    ("Tarifs", "/tarifs/"),
    ("Conseils", "/conseils/"),
    ("À propos", "/a-propos/"),
    ("Contact", "/contact/"),
]


def head(title, desc, path, schemas, og_type="website", noindex=False):
    canonical = abs_url(path)
    schema_tags = "\n".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False, separators=(",", ":"))
        for s in schemas
    )
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1"
    verif = ""
    if B.GOOGLE_SITE_VERIFICATION:
        verif += '<meta name="google-site-verification" content="%s">\n' % esc(B.GOOGLE_SITE_VERIFICATION)
    if B.BING_SITE_VERIFICATION:
        verif += '<meta name="msvalidate.01" content="%s">\n' % esc(B.BING_SITE_VERIFICATION)
    gtm_tag = ""
    if getattr(B, "GTM_ID", ""):
        # Google Tag Manager (conversions Google Ads). Chargé après le Consent Mode par défaut ci-dessus.
        gtm_tag = ("<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
                   "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
                   "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','%s');</script>\n") % B.GTM_ID
    phone_fwd = ""
    if B.CONV_CALL_FORWARDING:
        # Appels depuis le site : Google remplace le numéro affiché par un numéro de transfert
        # et compte l'appel comme conversion au-delà de la durée minimale réglée dans Google Ads.
        phone_fwd = "\n  gtag('config', '%s', {'phone_conversion_number': '%s'});" % (B.CONV_CALL_FORWARDING, B.PHONE)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
{verif}<meta name="geo.region" content="FR-83">
<meta name="geo.placename" content="{esc(B.BASE_CITY)}">
<meta name="geo.position" content="{B.GEO[0]};{B.GEO[1]}">
<meta name="ICBM" content="{B.GEO[0]}, {B.GEO[1]}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{esc(B.NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#111111">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<!-- Google tag (gtag.js) + Consent Mode v2 -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  (function(){{
    /* Consentement par défaut : refusé tant que le visiteur n'a pas choisi (CNIL / RGPD) */
    var c = null; try {{ c = JSON.parse(localStorage.getItem('ps83-consent')); }} catch(e) {{}}
    var ok = c && (Date.now() - c.t) < 182*24*3600*1000;
    var ads = ok && c.ads ? 'granted' : 'denied';
    var perso = ok && c.ads && c.perso ? 'granted' : 'denied';
    gtag('consent', 'default', {{ad_storage:ads, ad_user_data:ads, ad_personalization:perso, analytics_storage:ads, functionality_storage:'granted', security_storage:'granted', wait_for_update:500}});
    gtag('set', 'ads_data_redaction', ads === 'denied');
    gtag('set', 'url_passthrough', true);
  }})();
  gtag('js', new Date());
  gtag('config', '{B.GTAG_ID}');
  window.PS83_CONV = {{call: '{B.CONV_CALL}', form: '{B.CONV_FORM}'}};{phone_fwd}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={B.GTAG_ID}"></script>
{gtm_tag}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&amp;family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={ASSET_VERSION}">
{schema_tags}
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
"""


def header(path):
    def cur(href):
        return ' aria-current="page"' if path.startswith(href) and href != "/" else ""
    svc_items = [(s["short"], service_path(s)) for s in SERVICES] + [(ASSURANCE_PAGE["name"], "/%s/" % ASSURANCE_PAGE["slug"]), ("Toutes les prestations", "/prestations/")]
    zone_items = [("Serrurier %s" % c["name"], city_path(c)) for c in MENU_CITIES] + [("Toutes nos zones (%d communes)" % len(ALL_CITIES), "/zones-intervention/")]

    def dropdown(label, href, items):
        sub = "".join('<a href="%s">%s</a>' % (h, esc(t)) for t, h in items)
        return ('<div class="has-sub"><a href="%s"%s>%s <span class="caret" aria-hidden="true">▾</span></a>'
                '<div class="sub%s">%s</div></div>') % (href, cur(href), label, " cols-2" if len(items) > 10 else "", sub)
    links = '<a class="nav-urgent" href="/serrurier-urgence-24h-var/"%s><span class="dot dot-pulse"></span>Urgence 24h/24</a>' % cur("/serrurier-urgence-24h-var/")
    links += dropdown("Prestations", "/prestations/", svc_items)
    links += dropdown("Zones", "/zones-intervention/", zone_items)
    links += "".join('<a href="%s"%s>%s</a>' % (href, cur(href), label) for label, href in NAV[2:])
    mgroup = lambda title, items: '<div class="mgroup"><span>%s</span>%s</div>' % (title, "".join('<a href="%s">%s</a>' % (h, esc(t)) for t, h in items))
    mlinks = mgroup("Menu", [("Accueil", "/")])
    mlinks += mgroup("Prestations", svc_items)
    mlinks += mgroup("Zones d'intervention", zone_items)
    mlinks += mgroup("Informations", [(l, h) for l, h in NAV[2:]] + [("Questions fréquentes", "/faq/")])
    mlinks += '<a class="btn btn-orange" style="margin:16px 24px 20px" href="tel:%s">%s Appeler le %s</a>' % (B.PHONE_TEL, phone_icon(18, True), B.PHONE)
    return f"""<header class="site">
  <div class="wrap headbar">
    <a class="logo" href="/" aria-label="{B.NAME}, accueil">
      {LOGO_SVG}
      <span class="logo-text"><span class="l2" style="display:block">Proservice</span><span class="l1" style="display:block">Serrurerie · Var</span></span>
    </a>
    <nav class="main" aria-label="Navigation principale">{links}</nav>
    <a href="tel:{B.PHONE_TEL}" class="call-pill">
      {phone_icon(16)}
      <span class="dot dot-pulse"></span>
      <span class="txt">{B.PHONE}</span>
    </a>
    <button class="menu-btn" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="mobile-nav">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Navigation mobile">{mlinks}</nav>
</header>
<main id="contenu">
"""


def footer(form_anchor="#devis"):
    svc_links = "".join('<li><a href="%s">%s</a></li>' % (service_path(s), esc(s["short"])) for s in SERVICES)
    svc_links += '<li><a href="/%s/">%s</a></li>' % (ASSURANCE_PAGE["slug"], ASSURANCE_PAGE["name"])
    city_links = "".join('<li><a href="%s">Serrurier %s</a></li>' % (city_path(c), esc(c["name"])) for c in CORE_CITIES)
    city_links += '<li><a href="/zones-intervention/">Toutes les communes</a></li>'
    return f"""</main>
<footer class="site">
  <div class="wrap">
    <div class="foot-cols">
      <div>
        <a class="logo" href="/">{LOGO_SVG.replace('class="logo-mark"', 'class="logo-mark" width="34" height="34"')}<span class="logo-text"><span class="l2" style="display:block">Proservice</span><span class="l1" style="display:block">Serrurerie · Var</span></span></a>
        <p class="foot-about">Artisan serrurier indépendant depuis {B.SINCE}. Dépannage <b>24h/24 et 7j/7</b> dans <b>tout le Var (83)</b> : ouverture de porte, serrure, porte blindée, clés, rideaux métalliques.</p>
        <p class="foot-about"><a href="tel:{B.PHONE_TEL}"><b>{B.PHONE}</b></a><br><a href="mailto:{B.EMAIL}">{B.EMAIL}</a></p>
      </div>
      <div><h2>Prestations</h2><ul>{svc_links}</ul></div>
      <div><h2>Zones d'intervention</h2><ul>{city_links}</ul></div>
      <div><h2>Informations</h2><ul>
        <li><a href="/serrurier-urgence-24h-var/">Urgence serrurier 24h/24</a></li>
        <li><a href="/tarifs/">Tarifs</a></li>
        <li><a href="/a-propos/">À propos &amp; engagements</a></li>{'<li><a href="/realisations/">Nos chantiers en images</a></li>' if B.REALISATIONS else ""}
        <li><a href="/conseils/">Conseils serrurerie</a></li>
        <li><a href="/faq/">Questions fréquentes</a></li>
        <li><a href="/contact/">Contact &amp; devis</a></li>
        <li><a href="/plan-du-site/">Plan du site</a></li>
      </ul></div>
    </div>
    <div class="foot-bottom">
      <span>© {date.today().year} {B.LEGAL_NAME} — Artisan serrurier dans tout le Var (83){" · SIRET " + B.SIRET if B.SIRET else ""}{" · " + B.RCS_RM if B.RCS_RM else ""}.</span>
      <span><a href="/mentions-legales/">Mentions légales</a> · <a href="/politique-confidentialite/">Confidentialité</a> · <button type="button" data-consent="open">Cookies</button></span>
    </div>
  </div>
</footer>

<a href="tel:{B.PHONE_TEL}" class="float-call" aria-label="Appeler {B.NAME}">{phone_icon(24, True)}</a>
<div class="mobile-bar">
  <a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(18, True)} Appeler</a>
  <button type="button" class="btn btn-purple svc-quote" data-service="Demande de devis">Devis gratuit</button>
</div>
{quote_modal()}

<div class="consent" id="consent" role="dialog" aria-labelledby="consent-title">
  <h2 id="consent-title">Vos choix en matière de cookies</h2>
  <p>Avec votre accord, nous utilisons des cookies Google Ads pour mesurer l'efficacité de nos annonces. Le site fonctionne dans tous les cas. <a href="/politique-confidentialite/">En savoir plus</a></p>
  <div class="consent-prefs" id="consent-prefs" hidden>
    <label class="toggle"><input type="checkbox" checked disabled><span><b>Cookies nécessaires</b> — mémorisation de votre choix. Toujours actifs.</span></label>
    <label class="toggle"><input type="checkbox" id="c-ads"><span><b>Mesure publicitaire (Google Ads)</b> — savoir quelles annonces génèrent des appels et des demandes de devis.</span></label>
    <label class="toggle"><input type="checkbox" id="c-perso"><span><b>Personnalisation des annonces</b> — vous montrer des annonces adaptées sur les services Google.</span></label>
  </div>
  <div class="row">
    <button type="button" class="btn btn-purple" data-consent="granted">Tout accepter</button>
    <button type="button" class="btn btn-purple" data-consent="denied">Tout refuser</button>
    <button type="button" class="btn btn-outline" data-consent="custom" id="consent-custom">Personnaliser</button>
  </div>
</div>

<script src="/assets/main.js?v={ASSET_VERSION}" defer></script>
</body>
</html>
"""


def write_page(path, content, priority="0.6", sitemap=True):
    target = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    if sitemap:
        PAGES.append((path, priority))


# ---------------------------------------------------------------- blocs réutilisables
def crumbs_html(crumbs):
    parts = []
    for i, (name, path) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append('<span aria-current="page">%s</span>' % esc(name))
        else:
            parts.append('<a href="%s">%s</a><span class="sep">›</span>' % (path, esc(name)))
    return '<nav class="crumbs" aria-label="Fil d\'Ariane">%s</nav>' % "".join(parts)


def page_hero(crumbs, h1, lead, checks=None, badge=None, image=None, image_alt="", quote_service="Demande de devis"):
    checks_html = ""
    if checks:
        checks_html = '<div class="hero-checks">%s</div>' % "".join(
            '<div class="check-row"><span class="check-circle gr">✓</span>%s</div>' % esc(c) for c in checks)
    badge_html = ""
    if badge:
        badge_html = '<div class="pill avail-badge" style="margin:18px 0 0"><span class="dot dot-pulse"></span><span>%s</span></div>' % badge
    media = ""
    if image:
        media = ('<div class="hero-media">%s'
                 '<div class="hero-tag"><b>Prix annoncé</b><span>avant toute intervention</span></div></div>') % picture(image, image_alt, 560, 440, "(max-width: 900px) 100vw, 560px", attrs=' fetchpriority="high"')
    return f"""<section class="page-hero{' with-media' if image else ''}">
  <div class="wrap">
    {crumbs_html(crumbs)}
    <div class="ph-grid">
      <div>
        {badge_html}
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
        <div class="actions">
          <a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(18, True)} {B.PHONE}</a>
          <button type="button" class="btn btn-ghost svc-quote" data-service="{esc(quote_service)}">Demander un devis gratuit</button>
        </div>
        {checks_html}
      </div>
      {media}
    </div>
  </div>
</section>
"""


def trust_items_short():
    items = ["Plus de %s ans d'expérience en serrurerie" % B.YEARS.rstrip("+"), "Disponible 24h/24 et 7j/7",
             "Prix annoncé avant toute intervention", "Devis gratuit, sans engagement",
             "Facture détaillée acceptée par votre assureur", "Artisan local, partout dans le Var",
             "Intervention dans tout le Var (83)", "Travaux garantis"]
    if B.ASSURANCE_DECENNALE:
        items.insert(1, "Assurance décennale & RC professionnelle")
    return items


def trust_marquee():
    one = "".join('<li><span class="check-circle gr">✓</span>%s</li>' % esc(t) for t in trust_items_short())
    return ('<div class="trust-band"><div class="marquee" aria-label="Nos engagements"><ul class="marquee-track">%s%s</ul></div></div>\n'
            % (one, one.replace("<li>", '<li aria-hidden="true">')))


def urgent_band():
    links = [("Porte claquée", "/ouverture-de-porte-var/"), ("Clés perdues", "/serrurier-urgence-24h-var/"),
             ("Cambriolage", "/%s/" % ASSURANCE_PAGE["slug"]), ("Rideau bloqué", "/rideau-metallique-var/")]
    chips = "".join('<a href="%s">%s</a>' % (h, t) for t, h in links)
    return f"""<div class="urgent-band"><div class="wrap urgent-inner">
  <b class="urgent-title"><span class="urgent-dot"></span>Une urgence serrurerie ?</b>
  <div class="urgent-links">{chips}</div>
  <div class="urgent-cta"><a href="/conseils/porte-claquee-que-faire/" class="urgent-help">Que faire maintenant</a><a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(16, True)} Appeler</a></div>
</div></div>
"""


def cta_band(title="Porte claquée, serrure, projet de sécurité ?", text="Un artisan serrurier joignable 24h/24 et 7j/7 dans tout le Var (83)."):
    return f"""<section class="cta-band"><div class="wrap cta-inner">
  <div><h2>{title}</h2><p>{text}</p></div>
  <div class="cta-actions">
    <a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(18, True)} Appeler le {B.PHONE}</a>
    <a href="/serrurier-urgence-24h-var/" class="btn btn-ghost">Que faire en urgence ?</a>
  </div>
</div></section>
"""


def guarantees_section(cls="alt"):
    cards = [
        ("Plus de %s ans d'expérience" % B.YEARS.rstrip("+"), "Un serrurier de métier, en activité dans le Var depuis %d, qui a déjà rencontré à peu près toutes les pannes." % B.SINCE),
        ("Prix annoncé avant travaux", "Diagnostic d'abord, prix ensuite, intervention seulement avec votre accord. Aucune mauvaise surprise."),
        ("Facture pour l'assurance", "Facture détaillée remise systématiquement, reconnue par les assureurs habitation en cas de sinistre."),
        ("Artisan local, 24h/24", "Un seul numéro, un serrurier qui connaît le Var et qui reste votre interlocuteur après l'intervention."),
    ]
    if B.ASSURANCE_DECENNALE:
        cards[3] = ("Artisan assuré", "Assurance décennale et responsabilité civile professionnelle, garantie sur la prestation réalisée.")
    items = "".join('<div class="g-card"><div class="icon-sq la">%s</div><h3>%s</h3><p>%s</p></div>' % (svc_icon("shield", 22), esc(t), esc(d)) for t, d in cards)
    return f"""<section class="{cls}">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-green sec-badge">Nos garanties</div>
      <h2>Pourquoi nous faire confiance</h2>
      <p>Les mêmes engagements pour chaque intervention, de la porte claquée à la pose d'une porte blindée.</p>
    </div>
    <div class="g-grid">{items}</div>
  </div>
</section>
"""


def other_services_section(current=None, city=None):
    items = []
    for s in SERVICES:
        if s is current:
            continue
        href = combo_path(s, city) if city and not city.get("extra") else service_path(s)
        items.append('<a class="os-card" href="%s"><span class="icon-sq pu">%s</span><span>%s%s</span><span class="arrow">→</span></a>'
                     % (href, svc_icon(s["icon"], 22), esc(s["short"]), (" " + city["a"]) if city else ""))
    if not city:
        items.append('<a class="os-card" href="/%s/"><span class="icon-sq pu">%s</span><span>%s</span><span class="arrow">→</span></a>'
                     % (ASSURANCE_PAGE["slug"], svc_icon("shield", 22), ASSURANCE_PAGE["name"]))
    return f"""<section>
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">Nos autres prestations</div>
      <h2>Nous pouvons aussi vous aider pour</h2>
    </div>
    <div class="os-grid">{"".join(items)}</div>
  </div>
</section>
"""


def realisations_section(limit=6, cls=""):
    if not B.REALISATIONS:
        return ""
    cards = "".join(
        '<figure class="ch-card"><a href="/assets/chantiers/%s" data-lightbox data-caption="%s"><img src="/assets/chantiers/%s" alt="%s" loading="lazy"></a><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
        % (r["image"], esc(r["title"]), r["image"], esc(r["title"]), esc(r["title"]), esc(r.get("text", ""))) for r in B.REALISATIONS[:limit])
    more = '<div class="center" style="margin-top:28px"><a class="btn btn-outline" href="/realisations/">Voir tous nos chantiers</a></div>' if len(B.REALISATIONS) > limit else ""
    return f"""<section class="{cls}" id="realisations">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">Réalisations</div>
      <h2>Nos chantiers en images</h2>
      <p>Quelques interventions réalisées dans le Var.</p>
    </div>
    <div class="ch-grid">{cards}</div>
    {more}
  </div>
</section>
"""


def strip_band():
    items = [
        ('<path d="M12 2 4 5v6c0 5 3.4 8.7 8 11 4.6-2.3 8-6 8-11V5l-8-3Z" stroke="currentColor" stroke-width="1.8"/>', "Facture détaillée acceptée par votre assureur"),
        ('<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M12 7v5l3.5 2" stroke="currentColor" stroke-width="1.8"/>', "Disponible 24h/24 et 7j/7"),
        ('<path d="M4 6h16M4 12h16M4 18h10" stroke="currentColor" stroke-width="1.8"/>', "Prix annoncé avant intervention"),
        ('<path d="M3 12h4l3-8 4 16 3-8h4" stroke="currentColor" stroke-width="1.8"/>', "Artisan local depuis %d" % B.SINCE),
    ]
    inner = "".join('<div class="strip-item"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">%s</svg>%s</div>' % (p, t) for p, t in items)
    return '<div class="strip"><div class="wrap strip-grid">%s</div></div>\n' % inner


def service_options(selected=None):
    names = [s["short"] for s in SERVICES] + ["Cambriolage / mise en sécurité", "Autre demande"]
    return "".join('<option%s>%s</option>' % (" selected" if n == selected else "", esc(n)) for n in names)


def city_options(selected=None):
    opts = ['<option value="">Choisir…</option>']
    opts += ['<option%s>%s</option>' % (" selected" if c["name"] == selected else "", esc(c["name"])) for c in sorted(ALL_CITIES, key=lambda c: c["name"])]
    opts.append("<option>Autre commune du Var</option>")
    return "".join(opts)


def consent_field(prefix):
    return ('<div class="frow consent-row"><label class="check"><input type="checkbox" name="consentement" value="oui" required id="%s-consent">'
            '<span>J\'accepte d\'être recontacté au sujet de ma demande, conformément à la <a href="/politique-confidentialite/">politique de confidentialité</a>.</span></label></div>') % prefix


def quote_modal():
    """Fenêtre « Demander un devis » (Netlify Forms : « devis-express »), ouverte par les boutons .svc-quote."""
    return f"""<div class="modal-overlay" id="quote-modal" aria-hidden="true">
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="quote-title">
    <button type="button" class="modal-close" id="quote-close" aria-label="Fermer">✕</button>
    <span class="pill pill-orange" id="quote-service-label">Demande de devis</span>
    <h2 id="quote-title">Demander un devis gratuit</h2>
    <p class="modal-sub">Réponse rapide. Pour une urgence, appelez le <a href="tel:{B.PHONE_TEL}">{B.PHONE}</a>.</p>
    <form class="quote" name="devis-express" method="POST" data-netlify="true" netlify-honeypot="adresse-web" action="/merci/" style="padding:0">
      <input type="hidden" name="form-name" value="devis-express">
      <input type="hidden" name="page" value="">
      <input type="hidden" name="besoin" value="Demande de devis" id="quote-service-input">
      <p class="hp"><label>Ne pas remplir : <input name="adresse-web" tabindex="-1" autocomplete="off"></label></p>
      <div class="frow-2">
        <div class="frow"><label for="q-prenom">Prénom *</label><input id="q-prenom" name="prenom" type="text" required autocomplete="given-name"></div>
        <div class="frow"><label for="q-nom">Nom *</label><input id="q-nom" name="nom" type="text" required autocomplete="family-name"></div>
      </div>
      <div class="frow-2">
        <div class="frow"><label for="q-tel">Téléphone *</label><input id="q-tel" name="telephone" type="tel" required autocomplete="tel" placeholder="06 00 00 00 00"></div>
        <div class="frow"><label for="q-ville">Commune</label><select id="q-ville" name="commune">{city_options()}</select></div>
      </div>
      <div class="frow"><label for="q-msg">Votre message *</label><textarea id="q-msg" name="message" rows="2" required placeholder="Décrivez rapidement la situation"></textarea></div>
      {consent_field("q")}
      <button type="submit" class="btn btn-orange">Envoyer ma demande</button>
      <p class="form-status" role="status"></p>
    </form>
  </div>
</div>
"""


def contact_section(path, title="Besoin d'un serrurier maintenant ?", service=None, city=None):
    """Formulaire de devis complet (Netlify Forms : « devis »), présent en bas de chaque page."""
    return f"""<section class="contact" id="devis">
  <div class="wrap contact-grid">
    <div>
      <div class="pill pill-orange">Contact &amp; devis gratuit</div>
      <h2>{title}</h2>
      <p class="lead">Pour une urgence, l'appel reste le plus rapide : un serrurier vous répond directement. Pour une demande de devis, remplissez le formulaire, nous vous rappelons rapidement (sous 1 h en journée).</p>
      <div class="contact-info">
        <div class="cinfo">
          <div class="icon-sq">{phone_icon(18)}</div>
          <div><b><a href="tel:{B.PHONE_TEL}">{B.PHONE}</a></b><span>Ligne directe, 24h/24 et 7j/7</span></div>
        </div>
        <div class="cinfo">
          <div class="icon-sq"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 6h16v12H4z" stroke="currentColor" stroke-width="1.8"/><path d="M4 7l8 6 8-6" stroke="currentColor" stroke-width="1.8"/></svg></div>
          <div><b><a href="mailto:{B.EMAIL}">{B.EMAIL}</a></b><span>Devis et demandes non urgentes</span></div>
        </div>
        <div class="cinfo">
          <div class="icon-sq">{svc_icon("shield", 18)}</div>
          <div><b>Tout le Var (83)</b><span>Diagnostic téléphonique et devis gratuits</span></div>
        </div>
      </div>
    </div>
    <form class="quote" name="devis" method="POST" data-netlify="true" netlify-honeypot="adresse-web" action="/merci/">
      <input type="hidden" name="form-name" value="devis">
      <input type="hidden" name="page" value="{esc(path)}">
      <p class="hp"><label>Ne pas remplir : <input name="adresse-web" tabindex="-1" autocomplete="off"></label></p>
      <div class="frow-2">
        <div class="frow">
          <label for="d-prenom">Prénom *</label>
          <input id="d-prenom" name="prenom" type="text" required autocomplete="given-name" placeholder="Votre prénom">
        </div>
        <div class="frow">
          <label for="d-nom">Nom *</label>
          <input id="d-nom" name="nom" type="text" required autocomplete="family-name" placeholder="Votre nom">
        </div>
      </div>
      <div class="frow-2">
        <div class="frow">
          <label for="d-tel">Téléphone *</label>
          <input id="d-tel" name="telephone" type="tel" required autocomplete="tel" placeholder="06 00 00 00 00">
        </div>
        <div class="frow">
          <label for="d-email">E-mail</label>
          <input id="d-email" name="email" type="email" autocomplete="email" placeholder="vous@exemple.fr">
        </div>
      </div>
      <div class="frow-2">
        <div class="frow">
          <label for="d-ville">Commune</label>
          <select id="d-ville" name="commune">{city_options(city)}</select>
        </div>
        <div class="frow">
          <label for="d-service">Type de besoin</label>
          <select id="d-service" name="besoin">{service_options(service)}</select>
        </div>
      </div>
      <div class="frow">
        <label for="d-urgence">Urgence</label>
        <select id="d-urgence" name="urgence"><option>Urgent (aujourd'hui)</option><option>Dans la semaine</option><option>Pas urgent / projet</option></select>
      </div>
      <div class="frow">
        <label for="d-msg">Votre message *</label>
        <textarea id="d-msg" name="message" rows="3" required placeholder="Décrivez rapidement la situation"></textarea>
      </div>
      {consent_field("d")}
      <button type="submit" class="btn btn-orange">Envoyer ma demande</button>
      <p class="form-status" role="status"></p>
      <p class="form-note">En urgence, appelez directement le {B.PHONE}.</p>
    </form>
  </div>
</section>
"""


def quick_form(path, service=None, city=None, title="Rappel rapide"):
    """Formulaire court (Netlify Forms : « rappel »), dans la colonne latérale des pages de service."""
    return f"""<div class="side-card" id="rappel">
  <h2>{title}</h2>
  <p style="color:var(--gray-600)">Laissez votre numéro, un serrurier vous rappelle au plus vite.</p>
  <form class="quote" name="rappel" method="POST" data-netlify="true" netlify-honeypot="adresse-web" action="/merci/" style="padding:0">
    <input type="hidden" name="form-name" value="rappel">
    <input type="hidden" name="page" value="{esc(path)}">
    <p class="hp"><label>Ne pas remplir : <input name="adresse-web" tabindex="-1" autocomplete="off"></label></p>
    <div class="frow"><label for="r-nom">Nom *</label><input id="r-nom" name="nom" type="text" required autocomplete="name" placeholder="Votre nom"></div>
    <div class="frow"><label for="r-tel">Téléphone *</label><input id="r-tel" name="telephone" type="tel" required autocomplete="tel" placeholder="06 00 00 00 00"></div>
    <div class="frow"><label for="r-ville">Commune</label><select id="r-ville" name="commune">{city_options(city)}</select></div>
    <div class="frow"><label for="r-besoin">Besoin</label><select id="r-besoin" name="besoin">{service_options(service)}</select></div>
    {consent_field("r")}
    <button type="submit" class="btn btn-orange">Être rappelé</button>
    <p class="form-status" role="status"></p>
  </form>
</div>
"""


def call_card(price=None, extra=""):
    price_html = '<div class="price-big">%s</div>' % esc(price) if price else ""
    return f"""<div class="side-card dark">
  <h2>Urgence ? Appelez</h2>
  {price_html}
  <p>Un serrurier vous répond directement, 24h/24 et 7j/7. Prix annoncé avant le déplacement.</p>
  <a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(18, True)} {B.PHONE}</a>
  {extra}
</div>
"""


def faq_block(faq, title="Questions fréquentes", sub=None, cls="alt", anchor="faq"):
    items = "".join(
        '<details class="faq-item"%s><summary>%s <span class="plus" aria-hidden="true">+</span></summary><div class="faq-a"><p>%s</p></div></details>'
        % (" open" if i == 0 else "", esc(q), a) for i, (q, a) in enumerate(faq))
    sub_html = "<p>%s</p>" % sub if sub else ""
    return f"""<section class="{cls}" id="{anchor}">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">FAQ</div>
      <h2>{title}</h2>
      {sub_html}
    </div>
    <div class="faq-list">{items}</div>
  </div>
</section>
"""


def process_section(title="De l'appel à la réparation"):
    steps = [
        ("Appel &amp; diagnostic", "Vous décrivez le problème, nous estimons le type d'intervention et vous annonçons une fourchette de prix, gratuitement."),
        ("Départ", "Un serrurier part avec le matériel adapté. Vous connaissez l'heure d'arrivée estimée."),
        ("Devis sur place", "Le prix est confirmé et validé avec vous avant de commencer. Vous restez libre de refuser."),
        ("Intervention &amp; garantie", "Réparation propre, facture détaillée remise, utile pour votre assurance. Travaux garantis."),
    ]
    items = "".join('<div class="proc-item"><div class="n">%d</div><h3>%s</h3><p>%s</p></div>' % (i + 1, t, d) for i, (t, d) in enumerate(steps))
    return f"""<section class="process">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-orange sec-badge">Déroulé</div>
      <h2>{title}</h2>
      <p>Quatre étapes claires, pour un tarif annoncé avant toute intervention.</p>
    </div>
    <div class="proc-list">{items}</div>
  </div>
</section>
"""


def insurers_section(cls=""):
    return f"""<section class="{cls}" id="assurances">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-green sec-badge">{svc_icon("shield", 15)}Assurances</div>
      <h2>Facture détaillée acceptée par votre assureur</h2>
      <p>En cas de sinistre (cambriolage, tentative d'effraction, perte de clés…), la facture détaillée remise après chaque intervention vous permet de faire valoir vos droits auprès de votre assureur habitation.</p>
    </div>
    <p class="ins-note">Nous remettons une facture détaillée décrivant l'intervention et les dégâts constatés, le justificatif demandé par les assureurs. Remboursement selon les garanties et franchises de votre contrat. <a href="/{ASSURANCE_PAGE['slug']}/" style="color:var(--purple-700);font-weight:600;text-decoration:underline">Cambriolage : comment ça marche ?</a></p>
  </div>
</section>
"""


def reviews_section(cls="", city=None):
    """Avis clients réels uniquement (B.REVIEWS), chacun avec un lien vers sa source. Masqué si la liste est vide."""
    if not B.REVIEWS:
        return ""
    cards = []
    for r in B.REVIEWS:
        src_html = ""
        if r.get("url"):
            src_html = ' · <a href="%s" target="_blank" rel="noopener">avis %s</a>' % (esc(r["url"]), esc(r.get("source", "Google")))
        cards.append('<div class="testi"><div class="stars" aria-label="%d étoiles sur 5">%s</div><p>« %s »</p><div class="who"><span class="av">%s</span><span>%s — %s%s</span></div></div>'
                     % (r["stars"], "★" * r["stars"] + "☆" * (5 - r["stars"]), esc(r["text"]),
                        "".join(w[0] for w in r["name"].replace(".", "").split()), esc(r["name"]), esc(r["city"]), src_html))
    links = ""
    if B.GOOGLE_BUSINESS_URL:
        links += '<a class="btn btn-outline" href="%s" target="_blank" rel="noopener">Voir tous les avis sur Google</a>' % esc(B.GOOGLE_BUSINESS_URL)
    if B.GOOGLE_REVIEW_URL:
        links += '<a class="btn btn-outline" href="%s" target="_blank" rel="noopener">Laisser un avis sur Google</a>' % esc(B.GOOGLE_REVIEW_URL)
    if links:
        links = '<div class="center" style="margin-top:28px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">%s</div>' % links
    return f"""<section class="{cls}" id="avis">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">Avis clients</div>
      <h2>Ce que disent nos clients</h2>
    </div>
    <div class="testi-grid">{"".join(cards)}</div>
    {links}
  </div>
</section>
"""


def services_grid(city=None):
    cards = []
    for s in SERVICES:
        href = combo_path(s, city) if city else service_path(s)
        title = s["short"] + (" " + city["a"] if city else "")
        checks = "".join('<div class="check-row"><span class="check-circle la">✓</span>%s</div>' % esc(c) for c in s["card_checks"])
        cards.append(f"""<article class="svc-card has-img">
  <a class="svc-img" href="{href}" tabindex="-1" aria-hidden="true">{picture(s["image"], "", 400, 240, "(max-width: 700px) 100vw, 400px", attrs=' loading="lazy"')}<span class="pill {'pill-orange' if 'Urgence' in s['badge'] or s['badge'] == 'Dépannage' else 'pill-lav'}">{esc(s["badge"])}</span></a>
  <div class="svc-body">
    <h3><a href="{href}">{esc(title)}</a></h3>
    <p class="desc">{esc(s["card_desc"])}</p>
    <div class="svc-checks">{checks}</div>
    <div class="svc-foot"><span class="svc-price">{esc(s["price_label"])}</span><a class="more" href="{href}">En savoir plus →</a></div>
    <div class="svc-actions"><a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(16, True)} Appeler</a><button type="button" class="btn btn-outline svc-quote" data-service="{esc(s["short"])}">Demander un devis</button></div>
  </div>
</article>""")
    return '<div class="svc-grid">%s</div>' % "".join(cards)


def rate_hours(pid):
    d, e, n = B.RATE_DAY_START, B.RATE_EVENING_START, B.RATE_NIGHT_START
    return {"jour": "%dh – %dh" % (d, e), "soir": "%dh – %dh" % (e, n), "nuit": "%dh – %dh" % (n, d)}[pid]


def rate_price(base, coef):
    import math
    return "%d\u00a0€" % math.floor(base * coef + 0.5)


def pricing_section():
    """Carte « Dépannage d'urgence » : prix selon le créneau horaire, créneau en cours choisi par main.js."""
    first = B.RATE_PERIODS[0][0]
    tabs = "".join(
        '<button type="button" class="period-tab" data-period="%s" aria-pressed="%s"><b>%s</b><span>%s</span></button>'
        % (pid, "true" if pid == first else "false", esc(label), rate_hours(pid))
        for pid, label, coef in B.RATE_PERIODS)
    rows = ""
    for s in SERVICES:
        if not s["price_min"]:
            continue
        prices = "".join('<b data-p="%s">%s</b>' % (pid, rate_price(s["price_min"], coef)) for pid, label, coef in B.RATE_PERIODS)
        rows += '<li><a href="%s">%s</a><span class="rate-price"><small>à partir de</small>%s</span></li>' % (service_path(s), esc(s["short"]), prices)
    return f"""<section class="rate-section" id="tarifs-horaires">
  <div class="wrap">
    <div class="rate-card" data-active="{first}" data-day="{B.RATE_DAY_START}" data-evening="{B.RATE_EVENING_START}" data-night="{B.RATE_NIGHT_START}">
      <p class="rate-kicker">24H/24 · 7J/7</p>
      <h2>Dépannage d'urgence</h2>
      <p class="rate-sub">Prix TTC « à partir de ». Le tarif dépend de l'heure d'intervention.</p>
      <div class="rate-tabs" role="group" aria-label="Créneau horaire">{tabs}</div>
      <ul class="rate-list">{rows}</ul>
      <p class="rate-now" data-price-now>Dimanches et jours fériés : tarif de nuit toute la journée.</p>
      {price_conditions_html("rate-conds")}
      <p class="rate-legal">Devis écrit remis avant tout travail estimé à plus de 150&nbsp;€ TTC. <a href="/tarifs/">Détail de nos tarifs</a></p>
    </div>
  </div>
</section>
"""


def stats_block():
    stats = [
        ('<path d="M3 17 9 11 13 15 21 7M21 7h-5M21 7v5" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>', B.YEARS, "Années d'expérience", "Depuis %d" % B.SINCE),
        ('<circle cx="12" cy="12" r="9" stroke="#fff" stroke-width="1.8"/><path d="M12 7v5l3.5 2" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>', "24h/24", "Disponible 7j/7", "Jours fériés compris"),
        ('<path d="M4 6h16M4 12h16M4 18h10" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>', "0\u00a0€", "De surprise sur la facture", "Prix validé avant travaux"),
        ('<path d="M12 2 4 5v6c0 5 3.4 8.7 8 11 4.6-2.3 8-6 8-11V5l-8-3Z" stroke="#fff" stroke-width="1.8"/><path d="M8.5 12l2.3 2.3L15.5 9.5" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>', "Gratuit", "Diagnostic et devis", "Sans engagement"),
    ]
    items = "".join('<div class="stat"><div class="icon-sq"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">%s</svg></div><b>%s</b><div class="lbl">%s</div><div class="sub">%s</div></div>' % s for s in stats)
    return '<div class="stats-card">%s</div>' % items


def zones_section(current=None, service=None, cls=""):
    """Section « Un serrurier proche de chez vous » : toutes les communes avec le temps d'arrivée."""
    pool = list(CITIES)
    if current and not service and current.get("extra"):
        pool += [current] + [CITY_BY_SLUG[n] for n in current["near"] if n in CITY_BY_SLUG and CITY_BY_SLUG[n].get("extra")]
    seen = set()
    pool = [c for c in pool if not (c["slug"] in seen or seen.add(c["slug"]))]
    cities = sorted(pool, key=lambda c: (c["delay"], c["name"]))
    items = []
    for c in cities:
        href = combo_path(service, c) if service else city_path(c)
        label = ("%s %s" % (service["short"], c["name"])) if service else c["name"]
        items.append('<a href="%s"%s>%s <span class="d">%s</span></a>' % (
            href, ' class="current" aria-current="page"' if current and c["slug"] == current["slug"] else "", esc(label), delay_label(c)))
    return f"""<section class="zones {cls}" id="zones">
  <div class="wrap zones-inner">
    <div>
      <div class="pill pill-lav">Zone d'intervention</div>
      <h2>Un serrurier proche de chez vous</h2>
      <p class="intro">Temps d'arrivée indicatifs, hors trafic. Le délai exact vous est confirmé au moment de l'appel.</p>
      <div class="zone-list">{"".join(items)}</div>
    </div>
    <div class="zone-note">
      <span class="pill pill-orange">Hors zone ?</span>
      <h3>On couvre tout le Var</h3>
      <p>Les délais ci-contre sont indicatifs, hors trafic. Pour une commune qui n'y figure pas, le délai précis est donné au téléphone, avant tout déplacement.</p>
      <a href="tel:{B.PHONE_TEL}" class="btn btn-purple">{phone_icon(18, True)} Vérifier mon secteur</a>
      <a href="/zones-intervention/" class="btn btn-outline">Toutes nos zones d'intervention</a>
    </div>
  </div>
</section>
"""


def sector_blocks():
    """Toutes les communes du Var, regroupées par secteur (intercommunalité)."""
    out = ""
    for key, (lab, lab_de, desc) in SECTORS.items():
        cs = sorted([c for c in ALL_CITIES if c.get("sector") == key], key=lambda c: c["name"])
        if cs:
            out += '<h3 class="sector-title">%s</h3>%s' % (esc(lab[0].upper() + lab[1:]), zone_cards(cs))
    return out


def zone_cards(cities, link_fn=city_path):
    return '<div class="zone-grid">%s</div>' % "".join(
        '<a class="zone-card" href="%s"><span>%s<small>%s</small></span><span class="d">%s</span></a>'
        % (link_fn(c), esc(c["name"]), c["cp"], delay_label(c)) for c in cities)


def guides_teaser(guides, title="Nos conseils de serrurier", cls=""):
    cards = "".join(
        '<article class="post-card"><span class="pill pill-lav" style="align-self:flex-start">Guide pratique</span><h3><a href="%s">%s</a></h3><p>%s</p><a class="more" href="%s">Lire le guide →</a></article>'
        % (guide_path(g), esc(g["h1"]), esc(g["excerpt"]), guide_path(g)) for g in guides)
    return f"""<section class="{cls}">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">Conseils</div>
      <h2>{title}</h2>
    </div>
    <div class="cards-3">{cards}</div>
  </div>
</section>
"""


def trust_items():
    return [
        ("Prix annoncé avant de partir", "Diagnostic téléphonique gratuit et fourchette de prix avant tout déplacement, suppléments de nuit ou de week-end compris."),
        ("Devis validé avant les travaux", "Le prix est confirmé sur place et vous le validez avant que nous commencions. Vous restez libre de refuser."),
        ("Pas de travaux inutiles", "Si une réparation suffit, nous ne remplaçons pas. Si l'intervention peut attendre, nous vous le disons."),
        ("Facture détaillée", "Déplacement, main-d'œuvre et pièces détaillés : un document clair, accepté par les assureurs habitation."),
        ("Un artisan local, joignable en direct", "Pas de plateforme ni de centre d'appel : vous parlez directement à un serrurier du Var."),
        ("Travaux garantis", "Nos interventions sont garanties. En cas de souci, nous revenons."),
        ("Chantier propre", "Protection des sols, nettoyage en fin d'intervention et évacuation des anciennes pièces."),
        ("Ponctualité et transparence", "Un imprévu ? Nous vous prévenons à l'avance, avec un nouvel horaire."),
    ]


def trust_list_html():
    return '<ul class="trust-list">%s</ul>' % "".join(
        '<li><span class="check-circle gr">✓</span><div><b>%s</b><span class="t">%s</span></div></li>' % (t, d) for t, d in trust_items())


# ---------------------------------------------------------------- pages
HOME_FAQ = [
    ("Combien coûte une ouverture de porte ?", "Le tarif de base démarre à 69 € en journée. Il dépend du type de serrure et de l'horaire ; il est toujours annoncé au téléphone et confirmé avant intervention, jamais après. <a href=\"/tarifs/\">Voir nos tarifs</a>."),
    ("Intervenez-vous vraiment la nuit et le week-end ?", "Oui, un serrurier est joignable 24h/24 et 7j/7 au 06 75 93 19 04, jours fériés compris. " + majorations_sentence() + " La majoration est toujours annoncée avant le déplacement."),
    ("Faut-il justifier son identité pour une ouverture ?", "Oui, une pièce d'identité ou un justificatif de domicile est demandé sur place, pour la sécurité de l'occupant réel du logement."),
    ("La porte sera-t-elle abîmée pour l'ouvrir ?", "Dans la majorité des cas, non : une porte claquée s'ouvre sans dégât. Si la serrure doit être forcée ou percée, c'est toujours annoncé et validé avant."),
    ("Le devis est-il vraiment gratuit ?", "Oui, le diagnostic téléphonique et le devis sur place sont gratuits et sans engagement, que vous acceptiez ou non l'intervention."),
    ("Dans quelles communes intervenez-vous ?", "Nous intervenons dans tout le Var (83), notamment à Toulon et dans son agglomération, à Fréjus, Saint-Raphaël, Draguignan, ainsi qu\'à Le Muy, Les Arcs-sur-Argens, Le Cannet-des-Maures, Le Luc, La Garde-Freinet, Gonfaron, Draguignan, Lorgues, Taradeau, Le Thoronet, mais aussi Fréjus, Saint-Raphaël, Toulon et son agglomération (La Seyne-sur-Mer, La Garde, La Valette-du-Var, Hyères, Six-Fours-les-Plages, Ollioules). <a href=\"/zones-intervention/\">Voir toutes les communes</a>."),
    ("En combien de temps arrivez-vous ?", delay_faq()),
    ("Vos factures sont-elles acceptées par les assurances ?", "Oui. Après un cambriolage ou une tentative d'effraction, nous remettons une facture détaillée. Nos clients se font rembourser auprès de leur assureur habitation, selon les garanties de leur contrat."),
    ("Faut-il changer la serrure après une perte de clés ?", "C'est recommandé, surtout si vos clés étaient accompagnées d'un document portant votre adresse. Changer le cylindre suffit souvent et coûte moins cher que la serrure complète."),
    ("Qui va intervenir chez moi ?", "Un serrurier de " + B.NAME + ", artisan local. Vous l'avez au téléphone avant son arrivée, il vous annonce le prix avant de commencer et vous remet une facture détaillée. Après l'intervention, vous gardez le même numéro pour tout suivi."),
    ("Que faire en attendant le serrurier ?", "Vérifiez les autres accès et s'il existe un double chez un proche, ne forcez pas la porte et préparez un justificatif d'identité ou de domicile. Après une effraction, appelez le 17 et ne touchez à rien avant le passage des enquêteurs."),
    ("Comment être sûr de ne pas tomber sur un serrurier arnaqueur ?", "Exigez un prix avant le déplacement et un devis avant les travaux, méfiez-vous des faux documents « officiels » dans les boîtes aux lettres et préférez un artisan réellement local. <a href=\"/conseils/choisir-serrurier-eviter-arnaques/\">Lire notre guide</a>."),
]


def build_home():
    path = "/"
    title = "Serrurier dans le Var (83) 24h/24 — %s, dépannage 7j/7" % B.NAME
    desc = "Serrurier dans tout le Var (83), 24h/24 et 7j/7 : ouverture de porte, changement de serrure, porte blindée, clés, rideau métallique. Prix annoncé avant intervention. ☎ 06 75 93 19 04"
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#site", "name": B.NAME, "url": SITE + "/", "inLanguage": "fr-FR", "publisher": {"@id": SITE + "/#entreprise"}}
    out = head(title, desc, path, [business_schema(), website, faq_schema(HOME_FAQ)])
    out += header(path)
    out += f"""<section class="hero hero-split">
  <div class="wrap hero-inner">
    <div class="hero-text">
    <div class="pill avail-badge"><span class="dot dot-pulse"></span><span>Artisan serrurier · Tout le Var (83)</span></div>
    <h1>Votre serrurier<br><span class="accent">dans tout le Var, 24h/24</span></h1>
    <p class="lead">Porte claquée, clés perdues, serrure bloquée ? <b>Un artisan local vous répond en direct, jour et nuit, 7j/7</b>, et intervient avec un prix annoncé avant de commencer. Plus de {B.YEARS.rstrip("+")} ans d'expérience, travail soigné, facture détaillée acceptée par votre assureur.</p>
    <a href="tel:{B.PHONE_TEL}" class="hero-cta">
      <span class="num">{phone_icon(24, True)} {B.PHONE}</span>
      <span class="sub">Appel direct, disponible 24/7</span>
    </a>
    <button type="button" class="hero-devis svc-quote" data-service="Demande de devis">Ou demandez un devis gratuit</button>
    <div class="hero-checks">
      <div class="check-row"><span class="check-circle gr">✓</span>Diagnostic gratuit</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Prix annoncé à l'avance</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Travaux garantis</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Facture détaillée acceptée par votre assureur</div>
    </div>
    </div>
    <div class="hero-media">
      {picture("serrurier-devis-client.jpg", "Serrurier présentant le devis à une cliente avant l'intervention", 560, 560, "(max-width: 900px) 100vw, 560px", attrs=' fetchpriority="high"')}
      <div class="hero-tag"><b>Sur place</b><span>Devis annoncé avant travaux</span></div>
    </div>
  </div>
</section>
"""
    out += trust_marquee()
    out += urgent_band()
    out += pricing_section()
    out += f"""<section id="services">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-purple sec-badge">{svc_icon("shield", 15)}Services professionnels</div>
      <h2>Nos services de serrurerie dans le Var</h2>
      <p>Un artisan serrurier à votre service pour l'urgence comme pour les travaux, 24h/24 et 7j/7, dans tout le Var (83).</p>
    </div>
    {services_grid()}
  </div>
</section>
<div class="alt" style="padding:0 0 10px"><div class="wrap">{stats_block()}</div></div>
<section class="alt">
  <div class="wrap text-block prose">
    <h2>Un serrurier de confiance dans tout le Var depuis {B.SINCE}</h2>
    <p><strong>{B.NAME}</strong> est une entreprise artisanale de serrurerie qui intervient dans <strong>tout le Var (83)</strong>. Depuis {B.SINCE}, nous dépannons et équipons les particuliers, propriétaires, locataires, gestionnaires de résidences secondaires et petites entreprises de tout le département : Toulon, La Seyne-sur-Mer, Hyères, Fréjus, Saint-Raphaël, Draguignan, Le Muy, Le Luc et les communes voisines.</p>
    <p>Notre métier, c'est de régler vos problèmes de serrurerie <strong>rapidement, proprement et au juste prix</strong>. Une porte claquée un dimanche soir, des clés perdues en rentrant de vacances, une serrure forcée après un cambriolage : vous joignez directement un serrurier au <a href="tel:{B.PHONE_TEL}">{B.PHONE}</a>, sans plateforme ni centre d'appel. Il vous écoute, vous aide à sécuriser la situation et vous annonce une fourchette de prix <strong>avant</strong> de prendre la route.</p>
    <p>Nous intervenons sur toute la serrurerie de la maison et du commerce : <a href="/ouverture-de-porte-var/">ouverture de porte</a>, <a href="/changement-serrure-var/">changement de serrure et de cylindre A2P</a>, <a href="/porte-blindee-var/">porte blindée et blindage de porte</a>, <a href="/reproduction-cles-var/">reproduction de clés</a>, <a href="/serrure-connectee-var/">serrure connectée</a> et <a href="/rideau-metallique-var/">dépannage de rideaux métalliques</a>. Après un cambriolage, nous sécurisons votre logement et fournissons les <a href="/{ASSURANCE_PAGE['slug']}/">justificatifs demandés par votre assurance</a>.</p>
    <p>Ce qui nous distingue ? Des engagements simples et tenus : un prix annoncé à l'avance, un devis validé avant les travaux, aucune intervention inutile et une facture détaillée. Des engagements tenus à chaque intervention, de jour comme de nuit.</p>
  </div>
</section>
<section id="pourquoi">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">{svc_icon("shield", 15)}Entreprise de confiance</div>
      <h2>Notre charte de confiance</h2>
      <p>Le dépannage d'urgence a mauvaise réputation. Nous avons choisi de faire l'inverse, et de l'écrire noir sur blanc.</p>
    </div>
    {trust_list_html()}
    <div class="center" style="margin-top:34px"><a class="btn btn-outline" href="/a-propos/">En savoir plus sur nous</a></div>
  </div>
</section>
"""
    out += process_section("Simple, clair, sans surprise")
    out += insurers_section("alt")
    out += cta_band("Porte claquée, clés perdues ?", "Nous intervenons dans tout le Var (83), tous les jours, 24h/24.")
    out += zones_section()
    out += realisations_section(cls="alt")
    out += reviews_section("alt" if not B.REALISATIONS else "")
    out += guides_teaser(GUIDES[:3])
    out += faq_block(HOME_FAQ, "Avant d'appeler : vos questions", cls="alt")
    out += contact_section(path)
    out += footer()
    write_page(path, out, "1.0")


def build_service(s, idx):
    path = service_path(s)
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (s["name"], path)]
    schemas = [business_schema(), breadcrumb_schema(crumbs),
               service_schema(s["name"], strip_tags(s["lead"]), path, "Var (83)", s["price_min"]),
               faq_schema(s["faq"])]
    out = head(s["title"], s["meta"], path, schemas)
    out += header(path)
    out += page_hero(crumbs, s["h1"], s["lead"], s["checks"], badge="Disponible 24h/24 · 7j/7", image=s["image"], image_alt=s["image_alt"], quote_service=s["short"])
    out += trust_marquee()
    sections = "".join("<h2>%s</h2>%s" % (h, body) for h, body in s["sections"])
    others = "".join('<li><a href="%s"><span>%s</span><span>→</span></a></li>' % (service_path(o), esc(o["short"])) for o in SERVICES if o is not s)
    city_chips = "".join('<a class="chip" href="%s">%s %s <span class="d">%s</span></a>' % (combo_path(s, c), esc(s["short"]), esc(c["name"]), delay_label(c)) for c in CORE_CITIES)
    other_chips = "".join('<a class="chip" href="%s">%s %s <span class="d">%s</span></a>' % (combo_path(s, c), esc(s["short"]), esc(c["name"]), delay_label(c)) for c in CITIES if not c["core"])
    related_guides = [g for g in GUIDES if s["slug"] in g["services"]]
    guides_html = ""
    if related_guides:
        guides_html = "<h2>Nos guides sur le sujet</h2><ul>%s</ul>" % "".join('<li><a href="%s">%s</a></li>' % (guide_path(g), esc(g["h1"])) for g in related_guides)
    out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      {sections}
      <h2>{esc(s["short"])} : où intervenons-nous ?</h2>
      <p>Nous intervenons dans tout le Var (83). Retrouvez le détail de notre intervention dans votre commune :</p>
      <div class="chips" style="margin-bottom:14px">{city_chips}</div>
      <p>Nous intervenons aussi dans les communes voisines : </p>
      <div class="chips">{other_chips}</div>
      {guides_html}
    </article>
    <aside class="side">
      {quick_form(path, service=s["short"], title="Rappel rapide : " + s["short"].lower())}
      {call_card(s["price_label"])}
      <div class="side-card"><h2>Nos autres prestations</h2><ul class="side-links">{others}</ul></div>
    </aside>
  </div>
</section>
"""
    out += guarantees_section()
    out += zones_section(service=s)
    out += process_section()
    out += faq_block(s["faq"], "Questions fréquentes : " + s["short"].lower(), cls="")
    out += other_services_section(s)
    out += cta_band()
    out += contact_section(path, "Un besoin en %s ?" % s["short"].lower(), service=s["short"])
    out += footer()
    write_page(path, out, "0.9")


def build_combo(s, c, si, ci):
    path = combo_path(s, c)
    v = (si + ci) % 3
    title = s["combo_title"].format(city=c["name"], cp=c["cp"])
    desc = s["combo_meta"].format(a=c["a"], delay_txt=delay_txt(c))
    h1 = "%s %s" % (s["combo_h1"], c["a"])
    lead = s["combo_intros"][v].format(a=c["a"], de=c["de"], city=c["name"])
    crumbs = [("Accueil", "/"), (s["name"], service_path(s)), ("%s %s" % (s["short"], c["name"]), path)]
    near = [CITY_BY_SLUG[n] for n in c["near"] if n in CITY_BY_SLUG]
    near_names = ", ".join(n["name"] for n in near[:5])
    # FAQ : délai local + deux questions du service (rotation) + communes voisines
    sf = s["faq"]
    faq = [
        ("En combien de temps intervenez-vous %s ?" % c["a"], delay_sentence(c) + " Pour une urgence, appelez le 06 75 93 19 04."),
        sf[v % len(sf)],
        sf[(v + 1) % len(sf)],
        ("Intervenez-vous aussi autour %s ?" % c["de"], "Oui, nous intervenons également à %s et dans tout le Var. <a href=\"/zones-intervention/\">Voir toutes nos zones</a>." % near_names),
    ]
    schemas = [business_schema(), breadcrumb_schema(crumbs),
               service_schema("%s %s" % (s["combo_h1"], c["a"]), strip_tags(lead), path, c["name"], s["price_min"]),
               faq_schema(faq)]
    out = head(title, desc, path, schemas)
    out += header(path)
    out += page_hero(crumbs, h1, lead, s["checks"], badge="%s · %s" % (delay_txt(c), "24h/24, 7j/7"), image=s["image"], image_alt="%s %s" % (s["image_alt"], c["a"]), quote_service="%s %s" % (s["short"], c["a"]))
    out += trust_marquee()
    n = len(s["combo_points"])
    points = [s["combo_points"][(v * 2 + k) % n] for k in range(n)]
    points_html = "".join("<li>%s</li>" % esc(p) for p in points)
    other_services = "".join('<li><a href="%s"><span>%s %s</span><span>→</span></a></li>' % (combo_path(o, c), esc(o["short"]), esc(c["name"])) for o in SERVICES if o is not s)
    near_chips = "".join('<a class="chip" href="%s">%s %s</a>' % (combo_path(s, n), esc(s["short"]), esc(n["name"])) for n in near)
    first_section = s["sections"][0]
    out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      <h2>{esc(s["short"])} {c["a"]} : nos interventions</h2>
      <ul>{points_html}</ul>
      <h2>Un serrurier proche de chez vous {c["a"]}</h2>
      <p>{esc(c["context"])}</p>
      <p>{delay_sentence(c)}</p>
      <div class="callout info"><strong>Notre conseil :</strong> {esc(s["combo_tip"])}</div>
      <h2>Prix et engagements</h2>
      <p>{"" if s["price_label"].lower().startswith("tarif") else "Tarif : "}<strong>{esc(s["price_label"])}</strong>. Le diagnostic téléphonique est gratuit, le prix est annoncé avant le déplacement et confirmé sur place avant les travaux. En fin d'intervention, vous recevez une facture détaillée, acceptée par les assureurs habitation pour vos démarches de remboursement. Prix TTC en journée ; déplacement : {deplacement_txt()}. Majorations : {', '.join('%s %s' % (l[0].lower() + l[1:], v) for l, v in majorations())}, toujours annoncées à l'avance.</p>
      <h2>{first_section[0]}</h2>
      {first_section[1]}
      <p>Pour tout savoir sur cette prestation, consultez notre page <a href="{service_path(s)}">{esc(s["name"].lower())} dans le Var</a>, ou découvrez <a href="{city_path(c)}">toutes nos interventions de serrurier {c["a"]}</a>.</p>
      <h2>Nous intervenons aussi autour {c["de"]}</h2>
      <div class="chips">{near_chips}</div>
    </article>
    <aside class="side">
      {quick_form(path, service=s["short"], city=c["name"], title="Rappel rapide " + c["a"])}
      {call_card(s["price_label"])}
      <div class="side-card"><h2>Autres services {c["a"]}</h2><ul class="side-links">{other_services}</ul></div>
    </aside>
  </div>
</section>
"""
    out += guarantees_section()
    out += zones_section(current=c, service=s)
    out += faq_block(faq, "%s %s : vos questions" % (s["short"], c["a"]), cls="")
    out += other_services_section(s, c)
    out += contact_section(path, "%s %s : contactez-nous" % (s["short"], c["a"]), service=s["short"], city=c["name"])
    out += footer()
    write_page(path, out, "0.7" if c["core"] else "0.6")


def charter_section(cls=""):
    return f"""<section id="pourquoi" class="{cls}">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-lav sec-badge">{svc_icon("shield", 15)}Entreprise de confiance</div>
      <h2>Notre charte de confiance</h2>
      <p>Le dépannage d'urgence a mauvaise réputation. Nous avons choisi de faire l'inverse, et de l'écrire noir sur blanc.</p>
    </div>
    {trust_list_html()}
    <div class="center" style="margin-top:34px"><a class="btn btn-outline" href="/a-propos/">En savoir plus sur nous</a></div>
  </div>
</section>
"""


def city_hero(c, crumbs):
    """Héros de la page d'accueil, version commune."""
    return f"""<section class="hero hero-split hero-city">
  <div class="wrap hero-inner">
    <div class="hero-text">
    {crumbs_html(crumbs)}
    <div class="pill avail-badge"><span class="dot dot-pulse"></span><span>{esc(delay_txt(c))} · {c["cp"]}</span></div>
    <h1>Votre serrurier<br><span class="accent">{c["a"]}, 24h/24</span></h1>
    <p class="lead">Porte claquée, clés perdues, serrure bloquée ? <b>Un artisan serrurier vous répond en direct, jour et nuit, 7j/7</b>, et intervient {c["a"]} avec un prix annoncé avant de commencer. Plus de {B.YEARS.rstrip("+")} ans d'expérience dans le Var, facture détaillée acceptée par votre assureur.</p>
    <a href="tel:{B.PHONE_TEL}" class="hero-cta">
      <span class="num">{phone_icon(24, True)} {B.PHONE}</span>
      <span class="sub">Appel direct, disponible 24/7</span>
    </a>
    <button type="button" class="hero-devis svc-quote" data-service="Serrurier {esc(c["a"])}">Ou demandez un devis gratuit</button>
    <div class="hero-checks">
      <div class="check-row"><span class="check-circle gr">✓</span>Diagnostic gratuit</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Prix annoncé à l'avance</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Travaux garantis</div>
      <div class="check-row"><span class="check-circle gr">✓</span>Facture détaillée acceptée par votre assureur</div>
    </div>
    </div>
    <div class="hero-media">
      {picture("serrurier-intervention-var.jpg", "Serrurier " + c["a"] + " en train de poser une serrure", 452, 452, "(max-width: 900px) 100vw, 560px", attrs=' fetchpriority="high"')}
      <div class="hero-tag"><b>{esc(c["name"])}</b><span>{esc(delay_label(c))} · prix annoncé avant travaux</span></div>
    </div>
  </div>
</section>
"""


def build_city(c):
    path = city_path(c)
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/"), ("Serrurier " + c["name"], path)]
    title = "Serrurier %s (%s) — dépannage 24h/24, 7j/7 | %s" % (c["name"], c["cp"], B.NAME)
    desc = "Serrurier %s (%s) : ouverture de porte, changement de serrure, porte blindée, clés, rideau métallique. %s. Prix annoncé avant intervention. ☎ %s" % (c["a"], c["cp"], delay_txt(c), B.PHONE)
    near = [CITY_BY_SLUG[n] for n in c["near"] if n in CITY_BY_SLUG]
    faq = [
        ("Quel est le délai d'intervention d'un serrurier %s ?" % c["a"], delay_sentence(c)),
        ("Intervenez-vous %s la nuit et le week-end ?" % c["a"], "Oui, nous intervenons 24h/24 et 7j/7, jours fériés compris. " + majorations_sentence() + " La majoration vous est annoncée avant le déplacement."),
        ("Combien coûte un serrurier %s ?" % c["a"], "Nos interventions démarrent à 69 € pour une ouverture de porte, 129 € pour un changement de serrure et 15 € pour un double de clé, en journée. Le prix est annoncé au téléphone avant le départ et confirmé sur place. <a href=\"/tarifs/\">Voir nos tarifs</a>."),
        ("Vos factures sont-elles prises en charge par mon assurance ?", "Après une effraction, nous remettons une facture détaillée que nos clients transmettent à leur assureur habitation pour se faire rembourser, selon les garanties de leur contrat."),
        ("Quelles communes desservez-vous autour %s ?" % c["de"], "Nous intervenons notamment à %s, et dans tout le Var." % ", ".join(n["name"] for n in near)),
    ]
    schemas = [business_schema(), breadcrumb_schema(crumbs), faq_schema(faq)]
    out = head(title, desc, path, schemas)
    out += header(path)
    lead = "Ouverture de porte, changement de serrure, porte blindée, reproduction de clés : un artisan serrurier intervient <b>%s 24h/24 et 7j/7</b>, avec un prix annoncé avant de partir." % c["a"]
    out += city_hero(c, crumbs)
    out += trust_marquee()
    out += urgent_band()
    out += pricing_section()
    near_html = "".join('<a class="chip" href="%s">Serrurier %s <span class="d">%s</span></a>' % (city_path(n), esc(n["name"]), delay_label(n)) for n in near)
    out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      <h2>Votre serrurier {c["a"]}</h2>
      <p>{esc(c["intro"])}</p>
      <p>{esc(c["context"])}</p>
      <h2>Nos prestations de serrurerie {c["a"]}</h2>
      <ul>
        <li><strong>Urgence serrurerie 24h/24</strong> : porte claquée, clés perdues, serrure bloquée, effraction.</li>
        <li><strong>Ouverture de porte</strong> claquée ou fermée à clé, sans casse dans la majorité des cas.</li>
        <li><strong>Changement de serrure et de cylindre</strong>, serrures certifiées A2P, garantie 2 ans.</li>
        <li><strong>Porte blindée</strong> : pose de bloc-porte et blindage de porte existante.</li>
        <li><strong>Reproduction de clés</strong> standards et sécurisées.</li>
        <li><strong>Serrure connectée</strong> : à code, biométrique ou pilotée par téléphone.</li>
        <li><strong>Rideaux métalliques et volets</strong> : dépannage et réparation.</li>
      </ul>
      <h2>Pourquoi faire appel à nous {c["a"]} ?</h2>
      <p>Vous parlez directement à un artisan serrurier local, pas à une plateforme. Le diagnostic téléphonique est gratuit, le prix est annoncé avant le déplacement puis validé avec vous avant les travaux. Nous ne proposons que les interventions utiles et vous remettons une facture détaillée. Nous intervenons dans le Var depuis {B.SINCE}.</p>
      <h2>Communes voisines {c["de"]}</h2>
      <p>Nous intervenons aussi dans les communes proches :</p>
      <div class="chips">{near_html}</div>
    </article>
    <aside class="side">
      {quick_form(path, city=c["name"], title="Rappel rapide " + c["a"])}
      {call_card(None)}
    </aside>
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <div class="sec-head">
      <div class="pill pill-purple sec-badge">Prestations</div>
      <h2>Nos services de serrurier {c["a"]}</h2>
    </div>
    {services_grid(c)}
  </div>
</section>
"""
    out += '<div class="alt" style="padding:0 0 10px"><div class="wrap">%s</div></div>' % stats_block()
    out += charter_section()
    out += guarantees_section("alt")
    out += process_section("Simple, clair, sans surprise")
    out += insurers_section("alt")
    out += cta_band("Porte claquée, clés perdues ?", "Nous intervenons %s et dans les communes voisines, tous les jours, 24h/24." % c["a"])
    out += zones_section(current=c)
    out += realisations_section(cls="alt")
    out += reviews_section("alt" if not B.REALISATIONS else "", city=c)
    out += guides_teaser(GUIDES[:3])
    out += faq_block(faq, "Serrurier %s : vos questions" % c["a"], cls="alt")
    out += contact_section(path, "Un serrurier %s ? Contactez-nous" % c["a"], city=c["name"])
    out += footer()
    write_page(path, out, "0.8" if c["core"] else "0.7")


def build_prestations():
    path = "/prestations/"
    crumbs = [("Accueil", "/"), ("Prestations", path)]
    out = head("Prestations de serrurerie dans le Var — " + B.NAME,
               "Toutes nos prestations de serrurerie dans le Var : urgence 24h/24, ouverture de porte, changement de serrure, porte blindée, clés, serrure connectée, rideau métallique.",
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Nos prestations de serrurerie dans le Var", "De la porte claquée en pleine nuit à la pose d'une porte blindée, <b>un seul artisan</b> pour toute la serrurerie de votre logement, partout dans le Var.", ["Devis gratuit", "Prix annoncé à l'avance", "Travaux garantis"], image="serrurier-devis-client.jpg", image_alt="Serrurier présentant le devis à une cliente")
    out += trust_marquee()
    out += f"""<section><div class="wrap">{services_grid()}</div></section>
<section class="alt"><div class="wrap text-block prose">
  <h2>Cambriolage : nous gérons aussi le volet assurance</h2>
  <p>Après une effraction, nous sécurisons votre logement le jour même et vous remettons les justificatifs attendus par votre assureur habitation. <a href="/{ASSURANCE_PAGE['slug']}/">Découvrir notre accompagnement après cambriolage</a>.</p>
</div></section>
"""
    out += zones_section()
    out += process_section()
    out += contact_section(path)
    out += footer()
    write_page(path, out, "0.8")


def build_assurance():
    path = "/%s/" % ASSURANCE_PAGE["slug"]
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (ASSURANCE_PAGE["name"], path)]
    faq = [
        ("Le changement de serrure après un cambriolage est-il remboursé ?", "Les frais de remplacement de serrure et de mise en sécurité après une effraction sont souvent pris en charge par les contrats habitation, selon les garanties, plafonds et franchises. Conservez la facture détaillée et le récépissé de plainte."),
        ("Quels documents me remettez-vous ?", "Une facture détaillée qui précise l'intervention (mise en sécurité, ouverture, remplacement de serrure, pièces) et les dégâts constatés sur la porte et la serrure."),
        ("Dans quel délai dois-je déclarer un cambriolage ?", "En cas de vol, vous disposez de 2 jours ouvrés pour le déclarer à votre assureur, sauf délai plus long prévu par votre contrat. Déposez plainte avant : le récépissé vous sera demandé."),
        ("Dois-je attendre l'expert pour faire sécuriser la porte ?", "Non : vous devez protéger votre logement. Prenez des photos de la porte et de la serrure avant l'intervention et conservez les pièces endommagées. Pour un remplacement complet de porte, demandez l'accord de votre assureur."),
        ("Pouvez-vous intervenir le soir même ?", "Oui, 24h/24 et 7j/7. Nous sécurisons le logement le jour même, par un remplacement de serrure ou une fermeture provisoire, puis proposons une solution durable."),
    ]
    schemas = [business_schema(), breadcrumb_schema(crumbs),
               service_schema("Mise en sécurité et changement de serrure après cambriolage", "Sécurisation du logement, remplacement de serrure et facture pour l'assurance habitation dans le Var.", path, "Var (83)", None),
               faq_schema(faq)]
    out = head("Serrurier après cambriolage dans le Var — mise en sécurité & assurance",
               "Cambriolage ou tentative d'effraction dans le Var : mise en sécurité le jour même, changement de serrure, facture pour votre assurance. ☎ 06 75 93 19 04",
               path, schemas)
    out += header(path)
    out += page_hero(crumbs, "Serrurier après cambriolage : mise en sécurité et justificatifs pour l'assurance",
                     "Porte forcée, serrure endommagée : nous <b>sécurisons votre logement le jour même</b> et vous remettons une facture détaillée pour être remboursé par votre assurance habitation.",
                     ["Intervention le jour même", "Facture détaillée", "Facture détaillée acceptée par votre assureur"], badge="Disponible 24h/24 · 7j/7",
                     image=ASSURANCE_PAGE["image"], image_alt=ASSURANCE_PAGE["image_alt"], quote_service="Cambriolage / mise en sécurité")
    out += trust_marquee()
    out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      <h2>Ce que nous faisons pour vous après une effraction</h2>
      <ol>
        <li><strong>Mise en sécurité</strong> le jour même : remplacement de la serrure endommagée ou fermeture provisoire de l'accès.</li>
        <li><strong>Diagnostic</strong> de la porte, du cadre et de la serrure : réparation possible ou remplacement nécessaire.</li>
        <li><strong>Solution durable</strong> : serrure certifiée A2P, serrure multipoints, blindage de porte ou bloc-porte blindé.</li>
        <li><strong>Justificatifs</strong> : facture détaillée de l'intervention et des dégâts constatés.</li>
      </ol>
      <p>Ces documents permettent à votre assureur d'instruire votre dossier rapidement. Nos clients les transmettent à leur assureur habitation pour se faire rembourser, selon les garanties de leur contrat.</p>
      <h2>Facture détaillée acceptée par votre assureur</h2>
      <p>Quel que soit votre assureur habitation, la facture détaillée d'un professionnel est le justificatif qu'il demande. Le remboursement dépend ensuite des garanties, plafonds et franchises de votre contrat.</p>
      <h2>Les étapes après un cambriolage</h2>
      <ul>
        <li>Appelez le <strong>17</strong> et ne touchez à rien avant le passage des enquêteurs.</li>
        <li>Déposez <strong>plainte</strong> et conservez le récépissé.</li>
        <li>Déclarez le vol à votre assureur dans les <strong>2 jours ouvrés</strong>.</li>
        <li>Faites <strong>sécuriser l'accès</strong> et conservez la facture du serrurier.</li>
      </ul>
      <p>Tout est détaillé dans notre guide : <a href="/conseils/cambriolage-que-faire-assurance/">cambriolage, les démarches et la sécurisation du logement</a>.</p>
      <h2>Renforcer sa porte après un cambriolage</h2>
      <p>Un cambriolage révèle souvent une faiblesse de la porte ou de la serrure. C'est le moment de passer à une serrure certifiée A2P ou de blinder la porte. <a href="/conseils/choisir-serrure-a2p/">Bien choisir sa serrure</a>.</p>
    </article>
    <aside class="side">
      {quick_form(path, service="Cambriolage / mise en sécurité", title="Rappel rapide : cambriolage")}
      {call_card("Intervention le jour même")}
    </aside>
  </div>
</section>
"""
    out += guarantees_section()
    out += zones_section()
    out += faq_block(faq, "Cambriolage et assurance : vos questions")
    out += other_services_section()
    out += contact_section(path, "Un cambriolage ? Contactez-nous", service="Cambriolage / mise en sécurité")
    out += footer()
    write_page(path, out, "0.9")


def build_zones():
    path = "/zones-intervention/"
    crumbs = [("Accueil", "/"), ("Zones d'intervention", path)]
    out = head("Zones d'intervention — serrurier dans tout le Var (83) : Toulon, Fréjus, Draguignan…",
               "Serrurier dans tout le Var (83), intervention 24h/24 : Toulon, La Seyne-sur-Mer, Hyères, Le Muy, Les Arcs, Le Cannet-des-Maures, Le Luc, La Garde-Freinet, Gonfaron, Draguignan, Fréjus, Saint-Raphaël, Toulon, Hyères et plus.",
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Nos zones d'intervention dans le Var", "Nous intervenons 24h/24 dans <b>tout le Var (83)</b>. Délais indicatifs hors trafic, confirmés au moment de l'appel.", ["Artisan local", "Délai annoncé à l'appel", "7j/7"])
    rows = ""
    for c in CITIES:
        links = " · ".join('<a href="%s">%s</a>' % (combo_path(s, c), esc(s["short"])) for s in SERVICES)
        rows += '<tr><td><a href="%s"><strong>Serrurier %s</strong></a></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (city_path(c), esc(c["name"]), c["cp"], delay_label(c), links)
    out += f"""<section>
  <div class="wrap">
    <div class="sec-head"><h2>Communes principales</h2><p>Nous y intervenons tous les jours de l'année, pour l'urgence comme pour les travaux.</p></div>
    {zone_cards(CORE_CITIES)}
    <div class="sec-head" style="margin-top:56px"><h2>Autres communes desservies</h2></div>
    {zone_cards([c for c in CITIES if not c["core"]])}
    <div class="sec-head" style="margin-top:56px"><h2>Toutes les communes du Var ({len(ALL_CITIES)})</h2><p>Chaque commune a sa page. Délais estimés hors trafic, confirmés au téléphone avant tout déplacement.</p></div>
    {sector_blocks()}
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <div class="sec-head"><h2>Toutes nos prestations, commune par commune</h2></div>
    <div class="table-scroll"><table class="prices"><thead><tr><th>Commune</th><th>Code postal</th><th>Délai</th><th>Prestations</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="ins-note">Votre commune n'apparaît pas ? Nous couvrons tout le Var : appelez le {B.PHONE}, nous vous indiquons le délai.</p>
  </div>
</section>
"""
    out += contact_section(path)
    out += footer()
    write_page(path, out, "0.8")


def build_tarifs():
    path = "/tarifs/"
    crumbs = [("Accueil", "/"), ("Tarifs", path)]
    faq = [
        ("Le déplacement est-il payant ?", ("Non, le déplacement est inclus dans nos prix." if B.DEPLACEMENT is True else
                                            "Le déplacement est facturé %s, annoncé au téléphone avant notre départ." % deplacement_txt() if B.DEPLACEMENT else
                                            "Les éventuels frais de déplacement vous sont annoncés au téléphone, avant notre départ.") + " Rien ne s'ajoute sur la facture sans votre accord."),
        ("Y a-t-il un supplément la nuit et le week-end ?", "Oui. " + majorations_sentence() + " La majoration vous est toujours communiquée avant le déplacement."),
        ("Le devis est-il gratuit ?", "Oui, le diagnostic téléphonique et le devis sur place sont gratuits et sans engagement."),
        ("Puis-je refuser le devis sur place ?", "Oui. Le prix est confirmé avant de commencer et vous restez libre de refuser."),
    ]
    out = head("Tarifs serrurier dans le Var — prix ouverture de porte, serrure, clés",
               "Tarifs de serrurier dans le Var : ouverture de porte dès 69 €, changement de serrure dès 129 €, double de clé dès 15 €, rideau métallique dès 79 €. Devis gratuit, prix annoncé avant intervention.",
               path, [business_schema(), breadcrumb_schema(crumbs), faq_schema(faq)])
    out += header(path)
    out += page_hero(crumbs, "Nos tarifs de serrurier dans le Var", "Des <b>prix clairs, annoncés avant le déplacement</b> et confirmés sur place avant les travaux. Pas de mauvaise surprise sur la facture.", ["Devis gratuit", "Sans frais cachés", "Facture détaillée"])
    def price_cells(price_min, label):
        if not price_min:
            return '<td colspan="3">%s</td>' % esc(label)
        return "".join("<td>dès %s</td>" % rate_price(price_min, coef) for _, _, coef in B.RATE_PERIODS)
    rows = "".join('<tr><td><a href="%s"><strong>%s</strong></a></td>%s</tr>' % (service_path(s), esc(s["name"]), price_cells(s["price_min"], s["price_label"])) for s in SERVICES)
    rows += "".join('<tr><td><strong>%s</strong></td>%s</tr>' % (esc(label), price_cells(p, "sur devis")) for label, p in getattr(B, "PRICE_DETAILS", []))
    hours = "".join("<th>%s<br><small>%s</small></th>" % (esc(label), rate_hours(pid)) for pid, label, _ in B.RATE_PERIODS)
    out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      <h2>Grille de prix indicative</h2>
      <div class="table-scroll"><table><thead><tr><th>Prestation (prix TTC)</th>{hours}</tr></thead><tbody>{rows}
        <tr><td><strong>Diagnostic téléphonique</strong></td><td colspan="3">gratuit</td></tr>
        <tr><td><strong>Devis sur place</strong></td><td colspan="3">gratuit, sans engagement</td></tr></tbody></table></div>
      <p>Prix TTC « à partir de ». Dimanches et jours fériés : tarif de nuit toute la journée.</p>
      <h2>Déplacement, main-d'œuvre et majorations</h2>
      {price_conditions_html()}
      <h2>Ce qui fait varier le prix</h2>
      <ul>
        <li><strong>L'état de la porte</strong> : une porte claquée s'ouvre plus simplement qu'une porte fermée à clé ou blindée.</li>
        <li><strong>Le type de serrure</strong> : cylindre standard, serrure multipoints, serrure haute sécurité.</li>
        <li><strong>Les pièces</strong> : nous vous présentons les options (gamme, marque) avant de commander.</li>
        <li><strong>L'horaire</strong> : nuit, week-end et jours fériés.</li>
      </ul>
      <h2>Notre engagement prix</h2>
      <ol>
        <li>Au téléphone, vous décrivez le problème : nous annonçons une fourchette de prix.</li>
        <li>Sur place, nous confirmons le prix avant de commencer. Vous validez, ou vous refusez.</li>
        <li>En fin d'intervention, la facture correspond au prix validé, détaillée poste par poste.</li>
      </ol>
      <div class="callout info">Conformément à l'arrêté du 24 janvier 2017 sur le dépannage, la réparation et l'entretien à domicile, un devis écrit détaillé vous est remis avant les travaux dont le montant estimé dépasse 150 € TTC.</div>
    </article>
    <aside class="side">
      {quick_form(path, title="Demander un prix")}
      {call_card(None)}
    </aside>
  </div>
</section>
"""
    out += insurers_section("alt")
    out += zones_section()
    out += faq_block(faq, "Questions sur nos tarifs")
    out += contact_section(path, "Obtenez votre devis gratuit")
    out += footer()
    write_page(path, out, "0.8")


def build_about():
    path = "/a-propos/"
    crumbs = [("Accueil", "/"), ("À propos", path)]
    out = head("À propos de %s — artisan serrurier dans le Var depuis %d" % (B.NAME, B.SINCE),
               "%s, artisan serrurier indépendant présent dans tout le Var (83) depuis %d : notre histoire, nos engagements et notre charte de confiance." % (B.NAME, B.SINCE),
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Un artisan serrurier local, des engagements tenus", "%s est une entreprise artisanale de serrurerie présente dans <b>tout le Var (83) depuis %d</b>. Voici qui nous sommes et comment nous travaillons." % (B.NAME, B.SINCE), ["Plus de %s ans d'expérience" % B.YEARS.rstrip("+"), "Artisan local, partout dans le Var", "Disponible 24h/24 et 7j/7"])
    out += f"""<section>
  <div class="wrap text-block prose">
    <h2>Notre histoire</h2>
    <p>{B.NAME} est né d'une idée simple : proposer aux habitants du Var un serrurier <strong>joignable, honnête et efficace</strong>. Depuis {B.SINCE}, nous intervenons au quotidien, de la simple porte claquée à la pose de portes blindées.</p>
    <p>Nous connaissons les logements du secteur : maisons de village aux portes anciennes, villas avec portail et garage, résidences secondaires du massif des Maures inoccupées une partie de l'année, appartements de Draguignan aux portes palières, commerces à rideau métallique.</p>
    <h2>Pourquoi un artisan local change tout</h2>
    <p>Quand vous cherchez « serrurier urgence » sur internet, beaucoup de numéros mènent à des plateformes nationales qui revendent votre appel à un intervenant parfois éloigné, avec des prix difficiles à prévoir. Avec nous, vous appelez directement le serrurier qui va intervenir. Il connaît le secteur, il est proche, et il a tout intérêt à bien faire : sa réputation se joue ici, auprès de vos voisins.</p>
    <h2>Notre charte de confiance</h2>
  </div>
  <div class="wrap" style="margin-top:20px">{trust_list_html()}</div>
</section>
"""
    out += f'<div class="alt" style="padding:56px 0"><div class="wrap">{stats_block()}</div></div>'
    out += insurers_section()
    out += zones_section(cls="alt")
    out += reviews_section()
    out += contact_section(path)
    out += footer()
    write_page(path, out, "0.6")


def build_faq_page():
    path = "/faq/"
    crumbs = [("Accueil", "/"), ("FAQ", path)]
    groups = [("Général", HOME_FAQ)] + [(s["short"], s["faq"]) for s in SERVICES]
    all_faq = [qa for _, g in groups for qa in g]
    out = head("FAQ serrurier Var — prix, délais, urgence, assurance | " + B.NAME,
               "Toutes les réponses à vos questions de serrurerie : prix, délais d'intervention, urgence de nuit, ouverture de porte, changement de serrure, porte blindée, assurance.",
               path, [business_schema(), breadcrumb_schema(crumbs), faq_schema(all_faq)])
    out += header(path)
    out += page_hero(crumbs, "Questions fréquentes", "Prix, délais, urgences, assurance : les réponses aux questions qu'on nous pose le plus souvent.")
    for i, (name, faq) in enumerate(groups):
        out += faq_block(faq, name, cls="alt" if i % 2 else "", anchor="faq-%d" % i)
    out += contact_section(path, "Votre question n'y est pas ? Écrivez-nous")
    out += footer()
    write_page(path, out, "0.6")


def build_contact():
    path = "/contact/"
    crumbs = [("Accueil", "/"), ("Contact", path)]
    out = head("Contact & devis gratuit — serrurier " + B.NAME + ", tout le Var (83)",
               "Contactez " + B.NAME + " : 06 75 93 19 04, 24h/24 et 7j/7, ou demandez un devis gratuit en ligne. Serrurier intervenant dans tout le Var (83).",
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Contact et devis gratuit", "Urgence : appelez le <b>%s</b>, 24h/24. Pour un devis, remplissez le formulaire ci-dessous, nous vous rappelons rapidement." % B.PHONE)
    out += contact_section(path, "Demandez votre devis gratuit")
    out += f"""<section>
  <div class="wrap text-block prose">
    <h2>Comment nous joindre</h2>
    <ul>
      <li><strong>Téléphone (24h/24, 7j/7)</strong> : <a href="tel:{B.PHONE_TEL}">{B.PHONE}</a></li>
      <li><strong>E-mail</strong> : <a href="mailto:{B.EMAIL}">{B.EMAIL}</a></li>
      <li><strong>Zone</strong> : tout le Var (83). <a href="/zones-intervention/">Voir nos zones</a></li>
    </ul>
    <h2>Pour un devis plus rapide</h2>
    <p>Indiquez votre commune, le type de besoin et, si possible, envoyez quelques photos par e-mail (porte, serrure, cylindre, rideau métallique). Nous pourrons vous donner une estimation plus précise dès le premier échange.</p>
  </div>
</section>
"""
    out += footer()
    write_page(path, out, "0.7")


def build_guides():
    path = "/conseils/"
    crumbs = [("Accueil", "/"), ("Conseils", path)]
    out = head("Conseils serrurerie — guides pratiques d'un serrurier du Var",
               "Guides pratiques : porte claquée, clé cassée, cambriolage et assurance, choisir une serrure A2P, résidence secondaire, serrure en location, éviter les arnaques.",
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Conseils de serrurier", "Nos guides pratiques pour réagir face à une panne, entretenir votre installation et éviter les mauvaises surprises.")
    out += guides_teaser(GUIDES, "Tous nos guides")
    out += zones_section(cls="alt")
    out += contact_section(path)
    out += footer()
    write_page(path, out, "0.6")
    for g in GUIDES:
        gp = guide_path(g)
        gcrumbs = crumbs + [(g["h1"], gp)]
        article = {
            "@context": "https://schema.org", "@type": "Article",
            "headline": g["h1"], "description": g["meta"], "inLanguage": "fr-FR",
            "mainEntityOfPage": abs_url(gp), "datePublished": TODAY, "dateModified": TODAY,
            "image": SITE + "/assets/og-image.png",
            "author": {"@type": "Organization", "name": B.NAME, "url": SITE + "/"},
            "publisher": {"@id": SITE + "/#entreprise"},
        }
        out = head(g["title"], g["meta"], gp, [business_schema(), breadcrumb_schema(gcrumbs), article], og_type="article")
        out += header(gp)
        out += page_hero(gcrumbs, g["h1"], esc(g["excerpt"]))
        svc_links = "".join('<li><a href="/%s/"><span>%s</span><span>→</span></a></li>' % (sl, esc(SERVICE_BY_SLUG[sl]["name"] if sl in SERVICE_BY_SLUG else ASSURANCE_PAGE["name"])) for sl in g["services"])
        others = "".join('<li><a href="%s"><span>%s</span><span>→</span></a></li>' % (guide_path(o), esc(o["h1"])) for o in GUIDES if o is not g)
        out += f"""<section>
  <div class="wrap layout">
    <article class="prose">
      <p class="meta-line">Par l'équipe {B.NAME}, artisan serrurier dans le Var · Mis à jour le {date.today().strftime("%d/%m/%Y")}</p>
      {g["body"]}
      <div class="callout"><strong>Besoin d'un serrurier ?</strong> Nous intervenons 24h/24 et 7j/7 dans tout le Var (83). Appelez le <a href="tel:{B.PHONE_TEL}">{B.PHONE}</a>.</div>
    </article>
    <aside class="side">
      {call_card(None)}
      <div class="side-card"><h2>Prestations liées</h2><ul class="side-links">{svc_links}</ul></div>
      <div class="side-card"><h2>Autres guides</h2><ul class="side-links">{others}</ul></div>
    </aside>
  </div>
</section>
"""
        out += contact_section(gp)
        out += footer()
        write_page(gp, out, "0.6")


def build_merci():
    path = "/merci/"
    out = head("Merci, votre demande est envoyée — %s" % B.NAME, "Votre demande a bien été envoyée à %s." % B.NAME, path, [], noindex=True)
    out = out.replace("<body>", '<body data-page="merci">', 1)
    out += header(path)
    out += f"""<section class="page-hero"><div class="wrap merci">
  <div class="merci-icon">✓</div>
  <h1>Merci, votre demande est bien envoyée</h1>
  <p class="lead">Un serrurier de {B.NAME} vous rappelle rapidement (sous 1 h en journée). <b>Pour une urgence, n'attendez pas : appelez directement le {B.PHONE}.</b></p>
  <div class="actions"><a href="tel:{B.PHONE_TEL}" class="btn btn-orange">{phone_icon(18, True)} {B.PHONE}</a><a href="/" class="btn btn-ghost">Retour à l'accueil</a></div>
</div></section>
<section><div class="wrap text-block prose">
  <h2>En attendant notre appel</h2>
  <ul>
    <li><strong>Porte claquée</strong> : vérifiez les autres accès et si un proche a un double, sans forcer la porte.</li>
    <li><strong>Ouverture de porte</strong> : préparez une pièce d'identité ou un justificatif de domicile.</li>
    <li><strong>Cambriolage</strong> : appelez le 17 et ne touchez à rien avant le passage des enquêteurs.</li>
    <li><strong>Rideau métallique bloqué</strong> : ne forcez pas à la main, un ressort sous tension peut céder.</li>
  </ul>
  <p>Nos guides pratiques peuvent aussi vous aider : <a href="/conseils/">voir les conseils</a>.</p>
</div></section>
"""
    out += footer("/contact/")
    write_page(path, out, sitemap=False)


def build_realisations():
    if not B.REALISATIONS:
        return
    path = "/realisations/"
    crumbs = [("Accueil", "/"), ("Réalisations", path)]
    out = head("Nos chantiers de serrurerie dans le Var — avant / après | %s" % B.NAME,
               "Photos de chantiers de serrurerie réalisés dans le Var : portes blindées, serrures, rideaux métalliques.",
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Nos chantiers en images", "Avant / après : quelques interventions réalisées par %s dans le Var." % B.NAME)
    out += realisations_section(limit=len(B.REALISATIONS))
    out += contact_section(path)
    out += footer()
    write_page(path, out, "0.6")


def build_plan():
    path = "/plan-du-site/"
    crumbs = [("Accueil", "/"), ("Plan du site", path)]
    out = head("Plan du site — %s, serrurier dans le Var" % B.NAME,
               "Plan du site de %s : toutes les prestations de serrurerie, toutes les communes desservies et tous les guides pratiques." % B.NAME,
               path, [business_schema(), breadcrumb_schema(crumbs)])
    out += header(path)
    out += page_hero(crumbs, "Plan du site", "Toutes les pages du site, classées par thème.")
    def ul(items):
        return "<ul>%s</ul>" % "".join('<li><a href="%s">%s</a></li>' % (h, esc(t)) for t, h in items)
    main_pages = [("Accueil", "/"), ("Prestations", "/prestations/"), ("Zones d'intervention", "/zones-intervention/"),
                  ("Tarifs", "/tarifs/"), ("À propos", "/a-propos/"), ("Conseils", "/conseils/"), ("FAQ", "/faq/"),
                  ("Contact & devis", "/contact/"), ("Mentions légales", "/mentions-legales/"), ("Confidentialité", "/politique-confidentialite/")]
    svc = [(s["name"], service_path(s)) for s in SERVICES] + [(ASSURANCE_PAGE["name"], "/%s/" % ASSURANCE_PAGE["slug"])]
    cities = [("Serrurier %s (%s)" % (c["name"], c["cp"]), city_path(c)) for c in sorted(ALL_CITIES, key=lambda c: c["name"])]
    guides = [(g["h1"], guide_path(g)) for g in GUIDES]
    out += f"""<section><div class="wrap">
  <div class="sitemap-cols">
    <div><h2>Pages principales</h2>{ul(main_pages)}<h2 style="margin-top:24px">Guides pratiques</h2>{ul(guides)}</div>
    <div><h2>Prestations</h2>{ul(svc)}</div>
    <div><h2>Communes</h2>{ul(cities)}</div>
  </div>
</div></section>
<section class="alt"><div class="wrap">
  <div class="sec-head"><h2>Prestations par commune</h2></div>
  <div class="sitemap-cols">{"".join('<div><h2>%s</h2>%s</div>' % (esc(s["short"]), ul([("%s %s" % (s["short"], c["name"]), combo_path(s, c)) for c in CITIES])) for s in SERVICES)}</div>
</div></section>
"""
    out += footer("/contact/")
    write_page(path, out, "0.3")


def build_legal():
    path = "/mentions-legales/"
    crumbs = [("Accueil", "/"), ("Mentions légales", path)]
    def li(label, value):
        return "<li><strong>%s</strong> : %s</li>" % (label, value)
    siege = "%s%s %s, France" % (B.ADDRESS_STREET + ", " if B.ADDRESS_STREET else "", B.ADDRESS_CP, B.ADDRESS_CITY)
    lines = [li("Dénomination", esc(B.LEGAL_NAME))]
    if B.LEGAL_FORM:
        lines.append(li("Forme juridique", esc(B.LEGAL_FORM)))
    lines.append(li("Activité", "artisan serrurier, dépannage et travaux de serrurerie"))
    lines.append(li("Siège social", esc(siege)))
    for label, value in (("SIRET", B.SIRET), ("Immatriculation", B.RCS_RM), ("N° de TVA intracommunautaire", B.TVA),
                         ("Directeur de la publication", B.DIRECTEUR_PUBLICATION)):
        if value:
            lines.append(li(label, esc(value)))
    lines += [li("Téléphone", B.PHONE), li("E-mail", '<a href="mailto:%s">%s</a>' % (B.EMAIL, B.EMAIL))]

    def insurance(title, a):
        if not a.get("assureur"):
            return ""
        parts = [esc(a["assureur"])]
        if a.get("contrat"):
            parts.append("contrat n° " + esc(a["contrat"]))
        if a.get("zone"):
            parts.append("couverture géographique : " + esc(a["zone"]))
        return li(title, ", ".join(parts))
    assurances = insurance("Assurance décennale", B.DECENNALE) + insurance("Responsabilité civile professionnelle", B.RC_PRO)
    assurances_html = "<h2>Assurances professionnelles</h2><ul>%s</ul>" % assurances if assurances else ""
    if B.MEDIATEUR.get("nom"):
        site = B.MEDIATEUR.get("site", "")
        mediation = ("En cas de litige non résolu après réclamation écrite auprès de l'entreprise, le client consommateur peut recourir gratuitement "
                     "au médiateur de la consommation dont relève l'entreprise : <strong>%s</strong>%s (articles L.612-1 et suivants du Code de la consommation)."
                     % (esc(B.MEDIATEUR["nom"]), ' — <a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(site), esc(site.replace("https://", "").rstrip("/"))) if site else ""))
    else:
        mediation = ("En cas de litige non résolu après réclamation écrite auprès de l'entreprise, le client consommateur peut recourir gratuitement "
                     "au médiateur de la consommation dont relève l'entreprise (articles L.612-1 et suivants du Code de la consommation).")
    missing = [label for label, v in (("forme juridique et capital", B.LEGAL_FORM), ("SIRET", B.SIRET), ("RCS / RM", B.RCS_RM),
                                      ("n° de TVA", B.TVA), ("adresse du siège", B.ADDRESS_STREET),
                                      ("directeur de la publication", B.DIRECTEUR_PUBLICATION),
                                      ("assurance décennale", B.DECENNALE.get("assureur")), ("RC pro", B.RC_PRO.get("assureur")),
                                      ("médiateur de la consommation", B.MEDIATEUR.get("nom"))) if not v]
    if missing:
        WARNINGS.append("Mentions légales : " + ", ".join(missing))
    out = head("Mentions légales — %s" % B.NAME, "Mentions légales du site de %s, artisan serrurier dans le Var (83)." % B.NAME, path, [breadcrumb_schema(crumbs)], noindex=True)
    out += header(path)
    out += page_hero(crumbs, "Mentions légales", "Informations légales relatives au site et à l'entreprise.")
    out += f"""<section><div class="wrap text-block prose">
  <h2>Éditeur du site</h2><ul>{"".join(lines)}</ul>
  {assurances_html}
  <h2>Hébergement</h2><p>Netlify, Inc. — 512 2nd Street, Suite 200, San Francisco, CA 94107, États-Unis — <a href="https://www.netlify.com" target="_blank" rel="noopener">www.netlify.com</a></p>
  <h2>Propriété intellectuelle</h2><p>Les textes, illustrations et éléments graphiques de ce site sont la propriété de {B.LEGAL_NAME}, sauf mention contraire. Toute reproduction sans autorisation est interdite.</p>
  <h2>Médiation de la consommation</h2><p>{mediation}</p>
  <h2>Données personnelles</h2><p>Voir notre <a href="/politique-confidentialite/">politique de confidentialité</a>.</p>
</div></section>
"""
    out += footer("/contact/")
    write_page(path, out, sitemap=False)

    path = "/politique-confidentialite/"
    crumbs = [("Accueil", "/"), ("Politique de confidentialité", path)]
    out = head("Politique de confidentialité — %s" % B.NAME, "Politique de confidentialité et de cookies du site de %s." % B.NAME, path, [breadcrumb_schema(crumbs)], noindex=True)
    out += header(path)
    out += page_hero(crumbs, "Politique de confidentialité", "Comment nous utilisons les informations que vous nous transmettez.")
    out += f"""<section><div class="wrap text-block prose">
  <h2>Données collectées</h2><p>Via nos formulaires, nous collectons les informations que vous saisissez : nom, téléphone, e-mail, commune, type de besoin et message. Elles servent uniquement à vous recontacter et à traiter votre demande. Elles ne sont ni vendues ni cédées.</p>
  <h2>Durée de conservation</h2><p>Les demandes sans suite sont supprimées au plus tard 3 ans après le dernier contact. Les factures sont conservées pendant la durée légale.</p>
  <h2>Cookies et mode de consentement</h2>
  <p>Lors de votre première visite, un bandeau vous permet de <strong>tout accepter</strong>, <strong>tout refuser</strong> ou de <strong>personnaliser</strong> vos choix. Tant que vous n'avez pas choisi, aucun cookie publicitaire n'est déposé.</p>
  <ul>
    <li><strong>Cookies nécessaires</strong> : mémorisation de votre choix dans votre navigateur. Toujours actifs.</li>
    <li><strong>Mesure publicitaire (Google Ads)</strong> : savoir quelles annonces génèrent des appels et des demandes de devis.</li>
    <li><strong>Personnalisation des annonces</strong> : affichage d'annonces adaptées sur les services Google.</li>
  </ul>
  <p>Le site utilise le mode de consentement de Google (Consent Mode v2) : si vous refusez, la balise Google n'enregistre aucun cookie publicitaire et n'envoie que des signaux anonymes, sans identifiant. Votre choix est conservé 6 mois, puis vous est redemandé. Vous pouvez le modifier à tout moment via le lien « Cookies » en bas de chaque page.</p>
  <h2>Vos droits</h2><p>Vous disposez d'un droit d'accès, de rectification, d'effacement et d'opposition sur vos données. Écrivez-nous à <a href="mailto:{B.EMAIL}">{B.EMAIL}</a>. Vous pouvez également saisir la CNIL (www.cnil.fr).</p>
</div></section>
"""
    out += footer("/contact/")
    write_page(path, out, sitemap=False)


def build_404():
    path = "/404/"
    out = head("Page introuvable — %s" % B.NAME, "Cette page n'existe pas.", "/", [], noindex=True)
    out += header(path)
    out += f"""<section class="page-hero"><div class="wrap">
  <h1>Page introuvable</h1>
  <p class="lead">Cette page n'existe pas ou a été déplacée. Besoin d'un serrurier ? Appelez le <b>{B.PHONE}</b>.</p>
  <div class="actions"><a href="/" class="btn btn-orange">Retour à l'accueil</a><a href="/prestations/" class="btn btn-ghost">Nos prestations</a></div>
</div></section>
"""
    out += footer("/contact/")
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(out)


# ---------------------------------------------------------------- fichiers techniques
AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
    "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot",
    "DuckAssistBot", "MistralAI-User", "Meta-ExternalAgent", "Amazonbot", "CCBot", "cohere-ai", "YouBot",
]


def build_robots():
    lines = [
        "# robots.txt — %s, serrurier dans tout le Var (83)" % B.NAME,
        "# Tout le site est ouvert aux moteurs de recherche et aux assistants IA.",
        "",
        "User-agent: *",
        "Allow: /",
        "Disallow: /404.html",
        "",
        "# Moteurs de recherche et assistants IA explicitement autorisés",
    ]
    for bot in ["Googlebot", "Googlebot-Image"] + AI_BOTS:
        lines += ["User-agent: %s" % bot]
    lines += ["Allow: /", "Disallow: /404.html", "",
              "Sitemap: %s/sitemap.xml" % SITE,
              "",
              "# Résumé du site pour les modèles de langage : %s/llms.txt" % SITE,
              "# Version complète : %s/llms-full.txt" % SITE, ""]
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def build_sitemap():
    urls = "".join(
        "<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (abs_url(p), TODAY, pr)
        for p, pr in PAGES)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def build_llms():
    summary = ("%s est un artisan serrurier indépendant qui intervient dans tout le Var (83, France), en activité depuis %d (siège à Vidauban). "
               "Il intervient 24h/24 et 7j/7 dans tout le Var pour les urgences et les travaux de serrurerie : ouverture de porte, "
               "changement de serrure, porte blindée, reproduction de clés, serrure connectée et rideaux métalliques. Téléphone : %s." % (B.NAME, B.SINCE, B.PHONE))
    lines = ["# %s — Serrurier dans tout le Var (83)" % B.NAME, "", "> " + summary, "",
             "Informations clés :",
             "- Téléphone (24h/24, 7j/7) : %s" % B.PHONE,
             "- E-mail : %s" % B.EMAIL,
             "- Base : %s (%s), %s" % (B.BASE_CITY, B.BASE_CP, B.DEPARTEMENT),
             "- Expérience : artisan dans le Var depuis %d (siège à Vidauban)" % B.SINCE,
             "- Tarifs : ouverture de porte dès 69 €, changement de serrure dès 129 € (garantie 2 ans), double de clé dès 15 €, dépannage de rideau métallique dès 79 €, porte blindée et serrure connectée sur devis. Diagnostic téléphonique et devis gratuits. " + majorations_sentence(),
             "- Tarifs selon l'heure d'intervention (heure de Paris) : " + " ; ".join("%s %s : %s" % (label.lower(), rate_hours(pid), ", ".join("%s %s" % (sv["short"], rate_price(sv["price_min"], coef)) for sv in SERVICES if sv["price_min"])) for pid, label, coef in B.RATE_PERIODS) + " (prix TTC à partir de). Dimanches et jours fériés : tarif de nuit. Déplacement : " + deplacement_txt() + "." + (" Main-d'œuvre : %s TTC de l'heure." % eur(B.TAUX_HORAIRE) if B.TAUX_HORAIRE else ""),
             "- Engagements : prix annoncé avant le déplacement, devis validé avant les travaux, facture détaillée, travaux garantis.",
             "- Assurance : facture détaillée acceptée par votre assureur habitation, remboursement selon les garanties du contrat.",
             "- Communes desservies : %s." % ", ".join("%s (%s, %s)" % (c["name"], c["cp"], delay_label(c)) for c in CITIES),
             "", "## Prestations", ""]
    for s in SERVICES:
        lines.append("- [%s](%s%s) : %s %s." % (s["name"], SITE, service_path(s), strip_tags(s["lead"]), s["price_label"][0].upper() + s["price_label"][1:] if s["price_label"].lower().startswith("tarif") else "Tarif : " + s["price_label"]))
    lines.append("- [Cambriolage & assurance](%s/%s/) : mise en sécurité après effraction, changement de serrure et justificatifs pour l'assurance habitation." % (SITE, ASSURANCE_PAGE["slug"]))
    lines += ["", "## Zones d'intervention", ""]
    for c in ALL_CITIES:
        lines.append("- [Serrurier %s (%s)](%s%s) : %s" % (c["name"], c["cp"], SITE, city_path(c), delay_sentence(c)))
    lines += ["", "Chaque prestation existe aussi en page dédiée par commune, selon le modèle %s/{prestation}-{commune}/ (ex. %s%s, %s%s). Liste complète : %s/plan-du-site/" % (
        SITE, SITE, combo_path(SERVICES[2], CITIES[1]), SITE, combo_path(SERVICES[0], CITIES[7]), SITE)]
    lines += ["", "## Guides pratiques", ""]
    for g in GUIDES:
        lines.append("- [%s](%s%s) : %s" % (g["h1"], SITE, guide_path(g), g["excerpt"]))
    lines += ["", "## Pages utiles", "",
              "- [Tarifs](%s/tarifs/) : grille de prix et engagement prix" % SITE,
              "- [À propos](%s/a-propos/) : histoire et charte de confiance" % SITE,
              "- [FAQ](%s/faq/) : questions fréquentes" % SITE,
              "- [Contact](%s/contact/) : téléphone, e-mail et formulaire de devis" % SITE,
              "", "## Optional", "",
              "- [Version complète pour les LLM](%s/llms-full.txt) : tout le contenu textuel du site" % SITE, ""]
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # llms-full.txt : contenu intégral en texte brut
    full = ["# %s — contenu complet du site" % B.NAME, "", "> " + summary, "", "Site : %s/" % SITE, ""]
    full += ["## Charte de confiance", ""] + ["- %s : %s" % (t, d) for t, d in trust_items()] + [""]
    for s in SERVICES:
        full += ["## %s" % s["h1"], "", "URL : %s%s" % (SITE, service_path(s)), "Tarif : %s" % s["price_label"], "", strip_tags(s["lead"]), ""]
        for h, body in s["sections"]:
            full += ["### %s" % h, "", strip_tags(body.replace("</li>", "</li>\n").replace("</p>", "</p>\n")), ""]
        full += ["### Questions fréquentes", ""]
        for q, a in s["faq"]:
            full += ["Q : %s" % q, "R : %s" % strip_tags(a), ""]
    full += ["## Questions générales", ""]
    for q, a in HOME_FAQ:
        full += ["Q : %s" % q, "R : %s" % strip_tags(a), ""]
    full += ["## Zones d'intervention", ""]
    for c in CITIES:
        full += ["### Serrurier %s (%s)" % (c["name"], c["cp"]), "", c["intro"], c["context"], delay_sentence(c), ""]
    for g in GUIDES:
        full += ["## %s" % g["h1"], "", "URL : %s%s" % (SITE, guide_path(g)), "", strip_tags(g["body"].replace("</p>", "</p>\n").replace("</li>", "</li>\n").replace("</h2>", "</h2>\n")), ""]
    with open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(full))


def build_static():
    shutil.copytree(SRC_ASSETS, os.path.join(OUT, "assets"), dirs_exist_ok=True)
    for name in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
        src = os.path.join(SRC_ASSETS, name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, name))
    manifest = {
        "name": B.NAME + " — Serrurier Var", "short_name": B.NAME, "lang": "fr",
        "start_url": "/", "display": "browser", "background_color": "#ffffff", "theme_color": "#111111",
        "icons": [{"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
                  {"src": "/assets/logo-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    with open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_static()
    build_home()
    build_prestations()
    for i, s in enumerate(SERVICES):
        build_service(s, i)
    build_assurance()
    build_zones()
    for c in EXTRA_CITIES:
        build_city(c)
    for ci, c in enumerate(CITIES):
        build_city(c)
        for si, s in enumerate(SERVICES):
            build_combo(s, c, si, ci)
    build_tarifs()
    build_about()
    build_faq_page()
    build_contact()
    build_guides()
    build_plan()
    build_merci()
    build_realisations()
    build_legal()
    build_404()
    build_robots()
    build_sitemap()
    build_llms()
    print("%d pages indexables générées dans %s" % (len(PAGES), OUT))
    if not B.SIRET:
        WARNINGS.append("SIRET absent du pied de page et du JSON-LD")
    if not (B.CONV_CALL and B.CONV_FORM) and not getattr(B, "GTM_ID", ""):
        WARNINGS.append("Conversions Google Ads : CONV_CALL / CONV_FORM vides, aucune conversion envoyée")
    if not B.CONV_CALL_FORWARDING:
        WARNINGS.append("Appels depuis le site (numéro de transfert Google, 60 s) : CONV_CALL_FORWARDING vide")
    if B.DEPLACEMENT is None:
        WARNINGS.append("Tarifs : DEPLACEMENT non renseigné (inclus ou prix)")
    if not B.TAUX_HORAIRE:
        WARNINGS.append("Tarifs : TAUX_HORAIRE non renseigné")
    if B.RATE_SUNDAY_COEF != period_coef("nuit"):
        WARNINGS.append("Tarifs : RATE_SUNDAY_COEF différent du tarif de nuit, la carte de l'accueil affiche le tarif de nuit le dimanche")
    WARNINGS.append("Délais estimés automatiquement (distance depuis Vidauban) pour %d communes : à vérifier dans src/data_communes_var.py" % len(EXTRA_CITIES))
    unconfirmed = [c["name"] for c in CITIES if c.get("delay_todo")]
    if unconfirmed:
        WARNINGS.append("Délais à confirmer : " + ", ".join(unconfirmed))
    if WARNINGS:
        print("\nÀ compléter :")
        for w in WARNINGS:
            print("  - " + w)


if __name__ == "__main__":
    main()
