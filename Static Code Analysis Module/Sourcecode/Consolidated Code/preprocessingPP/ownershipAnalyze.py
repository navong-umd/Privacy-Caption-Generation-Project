import pandas as pd
import re
from urllib.parse import urlparse


INPUT_CSV = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output\apps_kh_top100_per_group_with_privacy_2371_2026-01-26.csv"
OUTPUT_CSV = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output\Ownership.csv"


# -------------------------------------------------------------------
# 1) Configuration: known multinational publishers + strong domains
# -------------------------------------------------------------------

# If developer name contains any of these tokens -> Foreign-owned (high confidence)
FOREIGN_DEV_TOKENS = [
    # Big tech / major global brands
    "google", "google llc", "alphabet",
    "apple",
    "microsoft", "microsoft corporation",
    "meta", "facebook", "instagram", "whatsapp",
    "amazon",
    "bytedance", "tiktok",
    "samsung",
    "xiaomi",
    "netflix",
    "spotify",
    "telegram",
    "zoom",
    "paypal",
    "adobe",
    "waze",  # Google-owned but shows up sometimes
]

# If privacy policy domain matches any of these -> Foreign-owned (high confidence)
FOREIGN_POLICY_DOMAINS = [
    "google.com", "policies.google.com",
    "apple.com",
    "microsoft.com", "go.microsoft.com",
    "meta.com", "facebook.com", "instagram.com", "whatsapp.com",
    "amazon.com",
    "tiktok.com", "bytedance.com",
    "samsung.com",
    "netflix.com",
    "spotify.com",
    "telegram.org",
    "zoom.us",
    "paypal.com",
    "adobe.com",
]

# Foreign-ish generic or non-Cambodian TLDs (weak hints)
FOREIGN_TLDS = [
    ".com", ".net", ".org",  # generic, but useful if no local signals
    ".io", ".ai",
    ".cn", ".jp", ".kr",
    ".uk", ".de", ".fr", ".sg", ".th", ".vn",
]

# Local signals (stronger and weaker)
LOCAL_DOMAIN_TLDS = [".kh"]  # Cambodia ccTLD

# Local hint tokens in names/URLs
LOCAL_HINT_TOKENS = [
    "cambodia", "cambodian",
    "khmer",
    "phnom penh", "siem reap", "battambang",
    "pp", "ppc", "capital phnom penh",
    "cambo", "kampuchea",
    "kh "
]

# Strong local institutions / brands (telcos, banks, etc.) [web:18][web:21][web:23][web:26][web:25]
LOCAL_STRONG_TOKENS = [
    # Telcos
    "cellcard", "camgsm",
    "smart axiata", "smart cambodia", "smartmobile", "smart cam",
    "metfone", "viettel cambodia",

    # Selected banks & financial institutions (add more as needed)
    "acleda", "canadia bank", "prince bank", "vattanac bank",
    "cambodia post bank", "sathapana bank", "hattha bank",
    "kb prasac", "prasac", "phillip bank",
]


# -------------------------------------------------------------------
# 2) Helper functions
# -------------------------------------------------------------------

def normalize_text(x: str) -> str:
    x = "" if pd.isna(x) else str(x)
    x = x.strip().lower()
    x = re.sub(r"\s+", " ", x)
    return x


def extract_domain(url: str) -> str:
    url = "" if pd.isna(url) else str(url).strip()
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        dom = (parsed.netloc or "").lower()
        dom = dom.replace("www.", "")
        return dom
    except Exception:
        return ""


def contains_any(text: str, tokens) -> str | None:
    """Return matched token if any token is found, else None."""
    for t in tokens:
        if t and t in text:
            return t
    return None


def domain_matches(domain: str, known_domains) -> str | None:
    """Return matched domain if domain endswith or equals a known domain."""
    if not domain:
        return None
    for kd in known_domains:
        kd = kd.lower()
        if domain == kd or domain.endswith("." + kd) or domain.endswith(kd):
            return kd
    return None


# -------------------------------------------------------------------
# 3) Ownership inference with scoring
# -------------------------------------------------------------------

def infer_ownership(row) -> tuple[str, str]:
    dev_raw = row.get("developer", "")
    pp_url = row.get("privacy_policy_url", "")
    app_url = row.get("url", "")

    dev = normalize_text(dev_raw)
    pp_dom = extract_domain(pp_url)
    app_dom = extract_domain(app_url)

    score_foreign = 0
    score_local = 0
    reasons: list[str] = []

    # 1) Strong foreign: developer tokens (weight 3)
    hit = contains_any(dev, FOREIGN_DEV_TOKENS)
    if hit:
        score_foreign += 3
        reasons.append(f"Developer name contains foreign multinational token '{hit}'.")

    # 2) Strong foreign: policy/app domain against known list (weight 3)
    for dom, label in [(pp_dom, "privacy policy"), (app_dom, "storefront/app URL")]:
        hit_dom = domain_matches(dom, FOREIGN_POLICY_DOMAINS)
        if hit_dom:
            score_foreign += 3
            reasons.append(
                f"{label.capitalize()} domain '{dom}' matches known multinational domain '{hit_dom}'."
            )

    # 3) Foreign TLD hints (weak, weight 1) – only if no strong local ccTLD
    for dom, label in [(pp_dom, "privacy policy"), (app_dom, "storefront/app URL")]:
        if dom and any(dom.endswith(tld) for tld in FOREIGN_TLDS):
            score_foreign += 1
            reasons.append(
                f"{label.capitalize()} domain '{dom}' uses generic/non-Cambodian TLD."
            )

    # 4) Strong local: .kh domains (weight 3 for policy, 2 for app)
    if pp_dom and any(pp_dom.endswith(tld) for tld in LOCAL_DOMAIN_TLDS):
        score_local += 3
        reasons.append(
            f"Privacy policy domain '{pp_dom}' ends with Cambodia ccTLD '.kh'."
        )

    if app_dom and any(app_dom.endswith(tld) for tld in LOCAL_DOMAIN_TLDS):
        score_local += 2
        reasons.append(
            f"Storefront/app domain '{app_dom}' ends with Cambodia ccTLD '.kh'."
        )

    # 5) Strong local: known Cambodian institutions / brands (weight 4)
    strong_local_hit = (
        contains_any(dev, LOCAL_STRONG_TOKENS)
        or contains_any(normalize_text(pp_url), LOCAL_STRONG_TOKENS)
        or contains_any(normalize_text(app_url), LOCAL_STRONG_TOKENS)
    )
    if strong_local_hit:
        score_local += 4
        reasons.append(
            f"Name or URL contains known Cambodian brand/institution '{strong_local_hit}'."
        )

    # 6) Local hints in dev name or URLs (weight 2)
    policy_text = normalize_text(pp_url)
    app_text = normalize_text(app_url)
    hit_local = (
        contains_any(dev, LOCAL_HINT_TOKENS)
        or contains_any(policy_text, LOCAL_HINT_TOKENS)
        or contains_any(app_text, LOCAL_HINT_TOKENS)
    )
    if hit_local:
        score_local += 2
        reasons.append(
            f"Local geographic/linguistic hint '{hit_local}' found in developer name or URLs."
        )

    # 7) Heuristic: Khmer script in developer name (weight 3) [web:24][web:27]
    # Khmer block U+1780–U+17FF in Unicode
    if re.search(r"[\u1780-\u17FF]", dev_raw or ""):
        score_local += 3
        reasons.append(
            "Developer name contains Khmer script characters, suggesting Cambodian ownership."
        )

    # 8) Final decision with margins
    margin = score_local - score_foreign
    if margin >= 3:
        label = "Local-owned (likely)"
    elif margin <= -3:
        label = "Foreign-owned"
    else:
        label = "Ambiguous"

    # Optional textual confidence
    abs_margin = abs(margin)
    if abs_margin >= 5:
        confidence = "high"
    elif abs_margin >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    if not reasons:
        reasons.append(
            "No strong ownership signals in developer metadata or domains; cannot infer beyond storefront region."
        )

    justification = (
        f"Inferred as '{label}' with {confidence} confidence "
        f"(local score={score_local}, foreign score={score_foreign}). "
        + " | ".join(reasons)
    )

    return label, justification


# -------------------------------------------------------------------
# 4) Main pipeline
# -------------------------------------------------------------------

def main():
    df = pd.read_csv(INPUT_CSV)

    labels = []
    justifications = []

    for _, row in df.iterrows():
        label, why = infer_ownership(row)
        labels.append(label)
        justifications.append(why)

    df["ownership_label"] = labels
    df["ownership_justification"] = justifications

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUTPUT_CSV}")
    print(df["ownership_label"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
