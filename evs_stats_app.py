"""
EVS/WVS 2017-2022 — Comparateur de pays
Application Streamlit pour statistiques comparatives agrégées
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings("ignore")

import zipfile

@st.cache_data(show_spinner=False)
def load_data_from_github():
    """Télécharge et décompresse le CSV depuis GitHub Release (fichier ZIP)"""
    
    url = "https://github.com/felixat13/evs_stats/releases/download/v1.0/data_evs_mapped.csv.zip"
    
    try:
        st.info("📥 Téléchargement des données...")
        response = requests.get(url, timeout=60)
        
        if response.status_code != 200:
            st.error(f"Erreur HTTP {response.status_code}")
            st.stop()
        
        st.info("📦 Décompression...")
        
        # Décompresser le ZIP
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            # Trouver le fichier CSV dans le ZIP
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
            
            if not csv_files:
                st.error("Aucun fichier CSV trouvé dans le ZIP")
                st.stop()
            
            # Lire le premier CSV trouvé
            with z.open(csv_files[0]) as csvfile:
                df = pd.read_csv(csvfile)
        
        st.success(f"✅ {len(df):,} lignes chargées")
        return df
        
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

# ─── HELPER : tableau HTML sans pyarrow ─────────────────────────────────────
def html_table(df, gradient_col=None, max_rows=200):
    """Affiche un DataFrame en HTML pur — zéro dépendance à pyarrow."""
    df = df.head(max_rows).copy()

    # Calcul des min/max par colonne pour le gradient optionnel
    grad_min = grad_max = None
    if gradient_col and gradient_col in df.columns:
        grad_min = df[gradient_col].min()
        grad_max = df[gradient_col].max()

    def cell_style(col, val):
        base = "padding:6px 12px;font-size:0.83rem;white-space:nowrap;color:#000000 !important;"
        if col == gradient_col and grad_max != grad_min:
            try:
                ratio = (float(val) - grad_min) / (grad_max - grad_min)
                r = int(220 - ratio * 120)
                g = int(80 + ratio * 130)
                b = 80
                return base + f"background:rgba({r},{g},{b},0.28);font-weight:600;"
            except (TypeError, ValueError):
                pass
        return base

    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            style = cell_style(col, val)
            cells += f"<td style='{style}'>{val}</td>"
        rows_html += f"<tr>{cells}</tr>"

    headers = "".join(
        f"<th style='padding:6px 12px;background:#1A1A2E;color:#FFFFFF !important;"
        f"font-size:0.78rem;text-transform:uppercase;letter-spacing:.06em;"
        f"font-family:monospace;font-weight:600;white-space:nowrap;'>{c}</th>"
        for c in df.columns
    )

    html = f"""
    <div style='overflow-x:auto;border:1px solid #E0D9CE;border-radius:6px;margin:8px 0'>
      <table style='border-collapse:collapse;width:100%;background:#FAFAF8'>
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ─── CONFIG PAGE ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EVS — Comparateur de pays",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

/* ══════════════════════════════════════════════════════════════════════════
   RÈGLE ABSOLUE : TEXTE NOIR SUR FOND CLAIR (sauf sidebar et tableaux)
   ══════════════════════════════════════════════════════════════════════════ */

/* Reset complet : fond clair partout sauf sidebar */
.stApp,
section.main,
.block-container,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
.main .block-container {
    background-color: #FFFFFF !important;
}

/* ── TEXTE EN NOIR par défaut (mais pas dans les tableaux) ── */
p, span:not(table *), div:not(table *), label, li, small, strong, em, b, i,
h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
.stSelectbox *, .stMultiSelect *,
.stTextInput *, .stNumberInput *,
.stSlider *, .stCheckbox *, .stToggle *,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
button:not(table button), button:not(table button) *,
input, textarea, select, option {
    color: #000000 !important;
}

/* Titres */
h1 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #000000 !important;
    border-bottom: 3px solid #E63946;
    padding-bottom: 0.4rem;
    margin-bottom: 0.2rem !important;
}
h2 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.1rem !important;
    color: #000000 !important;
    letter-spacing: 0.05em;
    margin-top: 1.5rem !important;
}
h3 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #000000 !important;
    font-weight: 600 !important;
}

/* ── WIDGETS : DROPDOWNS, INPUTS ── */
/* Fond blanc + texte noir pour tous les inputs */
[data-baseweb="select"],
[data-baseweb="input"],
[data-baseweb="base-input"],
.stSelectbox > div,
.stMultiSelect > div,
.stTextInput > div,
input, textarea, select {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* Texte dans les dropdowns sélectionnés */
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] input,
[class*="singleValue"],
[class*="placeholder"],
[class*="input"],
[data-baseweb="tag"],
[data-baseweb="tag"] span {
    color: #000000 !important;
    background-color: transparent !important;
}

/* Menu déroulant ouvert */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"],
.Select-menu-outer,
.Select-menu {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

[data-baseweb="menu"] li,
[data-baseweb="menu"] div,
[data-baseweb="menu"] span,
[role="option"],
[role="option"] * {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}

/* Hover dans les menus */
[role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background-color: #F0F0F0 !important;
    color: #000000 !important;
}

/* Labels des widgets */
label,
.stSelectbox label,
.stMultiSelect label,
.stSlider label,
.stCheckbox label,
.stToggle label,
.stTextInput label,
[data-testid="stWidgetLabel"] {
    color: #000000 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── MÉTRIQUES ── */
[data-testid="metric-container"] {
    background: #F8F8F8 !important;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 0.8rem 1rem;
}
[data-testid="metric-container"] *,
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] * {
    color: #000000 !important;
}

/* ── ONGLETS ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em;
    color: #000000 !important;
    background-color: #F0F0F0 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #E63946 !important;
    background-color: #FFFFFF !important;
    border-bottom: 2px solid #E63946 !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"],
details {
    background-color: #FFFFFF !important;
    border: 1px solid #DDDDDD !important;
}
[data-testid="stExpander"] summary,
details summary,
details summary * {
    color: #000000 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    background-color: #F8F8F8 !important;
}

/* ── ALERTES / INFO BOXES ── */
[data-testid="stInfo"],
[data-testid="stSuccess"],
[data-testid="stWarning"],
[data-testid="stError"] {
    color: #000000 !important;
}
[data-testid="stInfo"] *,
[data-testid="stSuccess"] *,
[data-testid="stWarning"] *,
[data-testid="stError"] * {
    color: #000000 !important;
}

/* ── BOUTONS ── */
button {
    background-color: #E63946 !important;
    color: #FFFFFF !important;
    border: none !important;
}
button * {
    color: #FFFFFF !important;
}
button:hover {
    background-color: #D62828 !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   SIDEBAR : EXCEPTION - FOND SOMBRE + TEXTE CLAIR
   ══════════════════════════════════════════════════════════════════════════ */

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] {
    background-color: #1A1A2E !important;
}

/* Tout le texte de la sidebar en clair */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] li {
    color: #F4F1EC !important;
}

/* Labels dans la sidebar */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
[data-testid="stSidebar"] label {
    color: #AAB4C8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Inputs et selects dans la sidebar */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="input"] *,
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] * {
    background: #2A2A4A !important;
    color: #F4F1EC !important;
}

/* Options des dropdowns dans la sidebar */
[data-testid="stSidebar"] [data-baseweb="popover"],
[data-testid="stSidebar"] [data-baseweb="menu"],
[data-testid="stSidebar"] [role="listbox"],
[data-testid="stSidebar"] [role="option"] {
    background-color: #2A2A4A !important;
    color: #F4F1EC !important;
}
[data-testid="stSidebar"] [role="option"] * {
    color: #F4F1EC !important;
}

/* Boutons dans la sidebar */
[data-testid="stSidebar"] button {
    background-color: #E63946 !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] button * {
    color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   COMPOSANTS PERSONNALISÉS
   ══════════════════════════════════════════════════════════════════════════ */

.country-badge {
    display: inline-block;
    background: #E63946 !important;
    color: #FFFFFF !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 3px;
    margin: 2px;
    font-weight: 600;
}

.subtitle {
    font-size: 0.85rem;
    color: #666666 !important;
    margin-bottom: 1.5rem;
    font-style: italic;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #E63946 !important;
    margin-bottom: 0.3rem;
}

.info-box {
    background: #E8F4FD !important;
    border-left: 3px solid #2196F3;
    padding: 0.6rem 0.9rem;
    font-size: 0.82rem;
    border-radius: 0 4px 4px 0;
    margin-bottom: 1rem;
    color: #000000 !important;
}
.info-box * {
    color: #000000 !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   TABLEAUX HTML PERSONNALISÉS (fonction html_table)
   ══════════════════════════════════════════════════════════════════════════ */

/* En-têtes des tableaux : BLANC sur FOND SOMBRE */
table th {
    background-color: #1A1A2E !important;
    color: #FFFFFF !important;
}

/* Cellules des tableaux : NOIR sur FOND CLAIR */
table td {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* S'assurer que RIEN ne surcharge ces couleurs */
table th *,
table th span,
table th div {
    color: #FFFFFF !important;
}

table td *,
table td span,
table td div {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── VARIABLES THÉMATIQUES ───────────────────────────────────────────────────
THEMES = {
    "😊 Bien-être": {
        "Satisfaction de vie": ("Satisfaction with your life", "1=Insatisfait → 10=Satisfait"),
        "Bonheur": ("Feeling of happiness", "1=Très heureux → 4=Pas du tout heureux"),
        "Santé subjective": ("State of health (subjective)", "1=Très bonne → 5=Très mauvaise"),
        "Liberté de choix": ("How much freedom of choice and control", "1=Aucune → 10=Totale"),
    },
    "🤝 Confiance": {
        "Confiance générale": ("Most people can be trusted", "1=Oui → 2=Non (% qui font confiance)"),
        "Confiance: Famille": ("How much you trust: Your family (B)", "1=Totale → 4=Aucune"),
        "Confiance: Voisinage": ("Trust: Your neighborhood (B)", "1=Totale → 4=Aucune"),
        "Confiance: Inconnus": ("Trust: People you meet for the first time (B)", "1=Totale → 4=Aucune"),
        "Confiance: Autre religion": ("Trust: People of another religion (B)", "1=Totale → 4=Aucune"),
        "Confiance: Autre nationalité": ("Trust: People of another nationality (B)", "1=Totale → 4=Aucune"),
    },
    "🏛️ Institutions & Démocratie": {
        "Importance démocratie": ("Importance of democracy", "1=Pas important → 10=Essentiel"),
        "Qualité démocratie nationale": ("Democraticness in own country", "1=Non démocratique → 10=Complètement"),
        "Satisfaction système politique": ("Satisfaction with the political system", "1=Très satisfait → 4=Pas du tout"),
        "Confiance: Gouvernement": ("Confidence: The Government", "1=Beaucoup → 4=Aucune"),
        "Confiance: Parlement": ("Confidence: Parliament", "1=Beaucoup → 4=Aucune"),
        "Confiance: Police": ("Confidence: The Police", "1=Beaucoup → 4=Aucune"),
        "Confiance: Justice": ("Confidence: Justice System/Courts", "1=Beaucoup → 4=Aucune"),
        "Confiance: Presse": ("Confidence: The Press", "1=Beaucoup → 4=Aucune"),
        "Confiance: UE": ("Confidence: The European Union", "1=Beaucoup → 4=Aucune"),
    },
    "📣 Politique": {
        "Intérêt politique": ("Interest in politics", "1=Très intéressé → 4=Pas du tout"),
        "Échelle politique (Gauche-Droite)": ("Self positioning in political scale", "1=Gauche → 10=Droite"),
        "Égalité des revenus": ("Income equality", "1=Égalité totale → 10=Inégalité totale"),
        "Rôle de l'État": ("Government responsibility", "1=État → 10=Individu"),
        "Pétition": ("Political action: signing a petition", "1=Déjà fait → 3=Jamais"),
        "Manifestation": ("Political action: attending lawful/peaceful demonstrations", "1=Déjà fait → 3=Jamais"),
    },
    "🙏 Religion": {
        "Importance de Dieu": ("How important is God in your life", "1=Pas important → 10=Très important"),
        "Pratique religieuse": ("How often do you attend religious services", "1=+ d'une fois/sem → 7=Jamais"),
        "Prière": ("How often do you pray (WVS7)", "1=Plusieurs fois/j → 8=Jamais"),
        "Se dit religieux": ("Religious person", "1=Religieux → 3=Athée convaincu"),
        "Croyance: Dieu": ("Believe in: God", "0=Non → 1=Oui (% croyants)"),
        "Croyance: Au-delà": ("Believe in: life after death", "0=Non → 1=Oui"),
    },
    "👥 Valeurs sociales": {
        "Homophobie (homosexualité justifiable)": ("Justifiable: Homosexuality", "1=Jamais → 10=Toujours"),
        "Avortement (justifiable)": ("Justifiable: Abortion", "1=Jamais → 10=Toujours"),
        "Divorce (justifiable)": ("Justifiable: Divorce", "1=Jamais → 10=Toujours"),
        "Euthanasie (justifiable)": ("Justifiable: Euthanasia", "1=Jamais → 10=Toujours"),
        "Leaders politiques hommes": ("Men make better political leaders than women do", "1=Fortement d'accord → 4=Pas du tout"),
        "Dirigeants d'entreprise hommes": ("Men make better business executives than women do", "1=Fortement d'accord → 4=Pas du tout"),
        "Impact immigration": ("Evaluate the impact of immigrants on the development of [your country]", "1=Positif → 3=Négatif (dans certains pays)"),
    },
    "👨‍👩‍👧 Famille & Travail": {
        "Importance famille": ("Important in life: Family", "1=Très important → 4=Pas du tout"),
        "Importance travail": ("Important in life: Work", "1=Très important → 4=Pas du tout"),
        "Importance religion": ("Important in life: Religion", "1=Très important → 4=Pas du tout"),
        "Importance politique": ("Important in life: Politics", "1=Très important → 4=Pas du tout"),
        "Importance amis": ("Important in life: Friends", "1=Très important → 4=Pas du tout"),
        "Le travail avant tout": ("Work should come first even if it means less spare time", "1=D'accord → 5=Pas d'accord"),
    },
}

# Noms complets des pays
COUNTRY_NAMES = {
    'AL': 'Albanie', 'AM': 'Arménie', 'AT': 'Autriche', 'AZ': 'Azerbaïdjan',
    'BA': 'Bosnie', 'BE': 'Belgique', 'BG': 'Bulgarie', 'BY': 'Biélorussie',
    'CH': 'Suisse', 'CY': 'Chypre', 'CZ': 'Tchéquie', 'DE': 'Allemagne',
    'DK': 'Danemark', 'EE': 'Estonie', 'ES': 'Espagne', 'FI': 'Finlande',
    'FR': 'France', 'GB': 'Royaume-Uni', 'GE': 'Géorgie', 'GR': 'Grèce',
    'HR': 'Croatie', 'HU': 'Hongrie', 'IE': 'Irlande', 'IS': 'Islande',
    'IT': 'Italie', 'LT': 'Lituanie', 'LU': 'Luxembourg', 'LV': 'Lettonie',
    'ME': 'Monténégro', 'MK': 'Macédoine', 'MT': 'Malte', 'NL': 'Pays-Bas',
    'NO': 'Norvège', 'PL': 'Pologne', 'PT': 'Portugal', 'RO': 'Roumanie',
    'RS': 'Serbie', 'RU': 'Russie', 'SE': 'Suède', 'SI': 'Slovénie',
    'SK': 'Slovaquie', 'TR': 'Turquie', 'UA': 'Ukraine',
    # WVS
    'AR': 'Argentine', 'AU': 'Australie', 'BD': 'Bangladesh', 'BO': 'Bolivie',
    'BR': 'Brésil', 'CA': 'Canada', 'CL': 'Chili', 'CN': 'Chine',
    'CO': 'Colombie', 'EC': 'Équateur', 'EG': 'Égypte', 'ET': 'Éthiopie',
    'GT': 'Guatemala', 'ID': 'Indonésie', 'IN': 'Inde', 'IQ': 'Irak',
    'IR': 'Iran', 'JP': 'Japon', 'KE': 'Kenya', 'KR': 'Corée du Sud',
    'KZ': 'Kazakhstan', 'LB': 'Liban', 'LY': 'Libye', 'MA': 'Maroc',
    'MM': 'Myanmar', 'MX': 'Mexique', 'NG': 'Nigeria', 'NI': 'Nicaragua',
    'NZ': 'Nouvelle-Zélande', 'PH': 'Philippines', 'PK': 'Pakistan',
    'PR': 'Porto Rico', 'PW': 'Palaos', 'QA': 'Qatar', 'SG': 'Singapour',
    'TH': 'Thaïlande', 'TJ': 'Tadjikistan', 'TN': 'Tunisie', 'TW': 'Taïwan',
    'TZ': 'Tanzanie', 'US': 'États-Unis', 'UZ': 'Ouzbékistan',
    'VN': 'Vietnam', 'ZA': 'Afrique du Sud', 'ZW': 'Zimbabwe',
    'AD': 'Andorre', 'KG': 'Kirghizistan', 'MN': 'Mongolie',
}

PALETTE = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A', '#F4A261',
           '#264653', '#A8DADC', '#6D6875', '#B5838D', '#FFAFCC',
           '#80B918', '#FF6B6B', '#4CC9F0', '#F72585', '#7209B7']

# ─── CHARGEMENT DONNÉES ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(path):
    return pd.read_csv(path)

# ─── UI SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 EVS/WVS Explorer")
    st.markdown("<div style='font-size:0.75rem;color:#AAB4C8;margin-bottom:1.5rem'>European & World Values Survey<br>2017–2022 · 157 000 répondants</div>", unsafe_allow_html=True)

    try:
        with st.spinner("Chargement…"):
            df_full = load_data_from_github()
        all_countries_raw = sorted(df_full['Country (ISO 3166-1 Alpha-2 code)'].dropna().unique())
        all_countries = [f"{c} – {COUNTRY_NAMES.get(c, c)}" for c in all_countries_raw]
        code_map = {f"{c} – {COUNTRY_NAMES.get(c, c)}": c for c in all_countries_raw}
        st.success(f"✅ {len(df_full):,} réponses · {len(all_countries_raw)} pays")
    except FileNotFoundError:
        st.error("Fichier introuvable. Vérifiez le chemin.")
        st.stop()

    st.markdown("---")
    st.markdown("<div class='section-label'>Sélection des pays</div>", unsafe_allow_html=True)

    # Présélection rapide
    presets = {
        "Europe Ouest": ["AT – Autriche", "BE – Belgique", "DE – Allemagne", "DK – Danemark",
                         "ES – Espagne", "FI – Finlande", "FR – France", "IT – Italie",
                         "NL – Pays-Bas", "NO – Norvège", "PT – Portugal"],
        "Europe Est": ["BG – Bulgarie", "BY – Biélorussie", "CZ – Tchéquie", "HR – Croatie",
                       "HU – Hongrie", "PL – Pologne", "RO – Roumanie", "RS – Serbie",
                       "RU – Russie", "SK – Slovaquie", "SI – Slovénie"],
        "Balkans": ["AL – Albanie", "BA – Bosnie", "HR – Croatie", "ME – Monténégro",
                    "RS – Serbie", "SI – Slovénie"],
        "Tous les pays": all_countries[:20],
    }

    preset_valid = {}
    for label, codes in presets.items():
        valid = [c for c in codes if c in all_countries]
        if valid:
            preset_valid[label] = valid

    preset_choice = st.selectbox("Présélection rapide", ["— Choisir —"] + list(preset_valid.keys()))

    default_sel = preset_valid.get(preset_choice, [])
    if not default_sel:
        # fallback: 8 premiers pays dispo
        default_sel = all_countries[:8]

    selected_labels = st.multiselect(
        "Pays à comparer",
        options=all_countries,
        default=[c for c in default_sel if c in all_countries][:12],
    )

    selected_codes = [code_map[l] for l in selected_labels if l in code_map]

    st.markdown("---")
    st.markdown("<div class='section-label'>Options</div>", unsafe_allow_html=True)

    show_n = st.toggle("Afficher N répondants", value=True)
    show_ci = st.toggle("Intervalle de confiance (95%)", value=False)
    sort_bars = st.toggle("Trier les barres", value=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown("# 🌍 EVS / WVS — Comparateur de pays")
st.markdown("<div class='subtitle'>European & World Values Survey 2017–2022 · Statistiques agrégées par pays</div>", unsafe_allow_html=True)

if not selected_codes:
    st.info("👈 Sélectionnez au moins deux pays dans la barre latérale pour commencer.")
    st.stop()

# Filtrer les données
df = df_full[df_full['Country (ISO 3166-1 Alpha-2 code)'].isin(selected_codes)].copy()
df['Pays'] = df['Country (ISO 3166-1 Alpha-2 code)'].map(lambda x: COUNTRY_NAMES.get(x, x))

st.markdown(f"**{len(df):,}** répondants · **{len(selected_codes)}** pays sélectionnés")
pays_badges = " ".join([f'<span class="country-badge">{COUNTRY_NAMES.get(c, c)}</span>' for c in selected_codes])
st.markdown(pays_badges, unsafe_allow_html=True)

# ─── ONGLETS ──────────────────────────────────────────────────────────────────
tab_names = ["📊 Analyse par variable", "🗺️ Vue d'ensemble", "📋 Tableau comparatif", "🔍 Profil détaillé", "🔬 Profil pays complet"]
tabs = st.tabs(tab_names)

# ════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — ANALYSE PAR VARIABLE
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    col_theme, col_var = st.columns([1, 2])

    with col_theme:
        theme = st.selectbox("Thème", list(THEMES.keys()))

    with col_var:
        vars_in_theme = THEMES[theme]
        var_label = st.selectbox("Variable", list(vars_in_theme.keys()))

    col_name, scale_desc = vars_in_theme[var_label]

    # Vérifier disponibilité
    if col_name not in df.columns:
        st.warning(f"Variable `{col_name}` non disponible dans le dataset.")
    else:
        data_var = df[['Pays', 'Country (ISO 3166-1 Alpha-2 code)', col_name]].dropna(subset=[col_name])

        st.markdown(f"<div class='info-box'>📐 <b>Échelle :</b> {scale_desc}</div>", unsafe_allow_html=True)

        # ── Calcul des stats ──
        def compute_stats(grp):
            vals = grp[col_name].dropna()
            n = len(vals)
            mean = vals.mean()
            std = vals.std()
            ci = 1.96 * std / np.sqrt(n) if n > 1 else 0
            pct_top = (vals == vals.max()).mean() * 100  # % à la valeur max
            return pd.Series({'Moyenne': mean, 'Écart-type': std, 'IC95': ci,
                               'N': n, 'Médiane': vals.median()})

        stats = data_var.groupby('Pays').apply(compute_stats).reset_index()

        if sort_bars:
            stats = stats.sort_values('Moyenne', ascending=True)

        # ── Graphique en barres ──
        fig, ax = plt.subplots(figsize=(10, max(4, len(stats) * 0.55)))
        fig.patch.set_facecolor('#FAFAF8')
        ax.set_facecolor('#FAFAF8')

        colors = [PALETTE[i % len(PALETTE)] for i in range(len(stats))]
        bars = ax.barh(stats['Pays'], stats['Moyenne'],
                       color=colors, alpha=0.85, height=0.6, zorder=3)

        if show_ci:
            ax.errorbar(stats['Moyenne'], stats['Pays'],
                        xerr=stats['IC95'], fmt='none', color='#333',
                        capsize=3, linewidth=1.2, zorder=4)

        # Labels valeurs
        for bar, (_, row) in zip(bars, stats.iterrows()):
            label = f"{row['Moyenne']:.2f}"
            if show_n:
                label += f"  (n={int(row['N']):,})"
            ax.text(bar.get_width() + ax.get_xlim()[1] * 0.01, bar.get_y() + bar.get_height() / 2,
                    label, va='center', fontsize=8.5, color='#333', fontfamily='monospace')

        ax.set_xlabel('Moyenne', fontsize=9, color='#555')
        ax.set_title(var_label, fontsize=13, fontweight='bold', color='#1A1A2E', pad=14)
        ax.tick_params(axis='both', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#DDD')
        ax.spines['bottom'].set_color('#DDD')
        ax.grid(axis='x', alpha=0.25, zorder=0)
        ax.set_xlim(0, stats['Moyenne'].max() * 1.22)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        # ── Distribution détaillée ──
        with st.expander("📊 Distribution des réponses par pays (% et volume)"):
            unique_vals = sorted(data_var[col_name].dropna().unique())

            if len(unique_vals) <= 12:
                col_pct, col_vol = st.columns(2)
                
                # Calcul pivot
                pivot = (data_var.groupby(['Pays', col_name])
                         .size()
                         .unstack(fill_value=0))
                pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

                if sort_bars:
                    pivot = pivot.loc[stats['Pays'].tolist()[::-1]]
                    pivot_pct = pivot_pct.loc[stats['Pays'].tolist()[::-1]]

                with col_pct:
                    st.markdown("**Distribution en pourcentages**")
                    fig2, ax2 = plt.subplots(figsize=(10, max(4, len(pivot_pct) * 0.55)))
                    fig2.patch.set_facecolor('#FAFAF8')
                    ax2.set_facecolor('#FAFAF8')

                    cmap_colors = plt.cm.RdYlGn(np.linspace(0.1, 0.9, len(unique_vals)))
                    left = np.zeros(len(pivot_pct))

                    for i, val in enumerate(pivot_pct.columns):
                        widths = pivot_pct[val].values
                        ax2.barh(pivot_pct.index, widths, left=left,
                                 color=cmap_colors[i], label=f"{int(val)}", height=0.6, zorder=3)
                        for j, (w, l) in enumerate(zip(widths, left)):
                            if w > 5:
                                ax2.text(l + w / 2, j, f"{w:.0f}%",
                                         ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
                        left += widths

                    ax2.set_xlabel('% des répondants', fontsize=9, color='#555')
                    ax2.set_title(f'Distribution % — {var_label}', fontsize=10, fontweight='bold', color='#1A1A2E')
                    ax2.legend(title='Valeur', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)
                    ax2.set_xlim(0, 100)
                    ax2.spines['top'].set_visible(False)
                    ax2.spines['right'].set_visible(False)
                    ax2.grid(axis='x', alpha=0.2, zorder=0)
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()

                with col_vol:
                    st.markdown("**Distribution en volume (nombre de répondants)**")
                    fig3, ax3 = plt.subplots(figsize=(10, max(4, len(pivot) * 0.55)))
                    fig3.patch.set_facecolor('#FAFAF8')
                    ax3.set_facecolor('#FAFAF8')

                    left_vol = np.zeros(len(pivot))
                    for i, val in enumerate(pivot.columns):
                        widths_vol = pivot[val].values
                        ax3.barh(pivot.index, widths_vol, left=left_vol,
                                 color=cmap_colors[i], label=f"{int(val)}", height=0.6, zorder=3)
                        for j, (w, l) in enumerate(zip(widths_vol, left_vol)):
                            if w > pivot[val].max() * 0.08:  # Affiche si > 8% du max
                                ax3.text(l + w / 2, j, f"{int(w):,}",
                                         ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
                        left_vol += widths_vol

                    ax3.set_xlabel('Nombre de répondants', fontsize=9, color='#555')
                    ax3.set_title(f'Distribution volume — {var_label}', fontsize=10, fontweight='bold', color='#1A1A2E')
                    ax3.legend(title='Valeur', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)
                    ax3.spines['top'].set_visible(False)
                    ax3.spines['right'].set_visible(False)
                    ax3.grid(axis='x', alpha=0.2, zorder=0)
                    plt.tight_layout()
                    st.pyplot(fig3)
                    plt.close()

        # ── Tableau stats ──
        with st.expander("📋 Tableau des statistiques"):
            display_stats = stats[['Pays', 'N', 'Moyenne', 'Médiane', 'Écart-type']].copy()
            display_stats['N'] = display_stats['N'].astype(int)
            display_stats['Moyenne'] = display_stats['Moyenne'].round(3)
            display_stats['Médiane'] = display_stats['Médiane'].round(1)
            display_stats['Écart-type'] = display_stats['Écart-type'].round(3)
            display_stats = display_stats.sort_values('Moyenne', ascending=False).reset_index(drop=True)
            html_table(display_stats, gradient_col='Moyenne')

            csv_dl = display_stats.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger ce tableau", csv_dl,
                               f"stats_{var_label[:30]}.csv", "text/csv")

# ════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — VUE D'ENSEMBLE (HEATMAP)
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## Vue d'ensemble — Carte de chaleur")

    # Sélectionner les variables à inclure
    all_flat_vars = {}
    for theme_name, theme_vars in THEMES.items():
        for var_label_k, (col, scale) in theme_vars.items():
            short = var_label_k
            all_flat_vars[short] = col

    available_vars = {k: v for k, v in all_flat_vars.items() if v in df.columns}

    selected_overview_vars = st.multiselect(
        "Variables à inclure dans la carte de chaleur",
        options=list(available_vars.keys()),
        default=list(available_vars.keys())[:15],
    )

    if len(selected_overview_vars) < 2:
        st.info("Sélectionnez au moins 2 variables.")
    else:
        cols_to_agg = {v: available_vars[v] for v in selected_overview_vars}

        # Agréger moyennes par pays
        agg_data = {}
        for label, col in cols_to_agg.items():
            means = df.groupby('Pays')[col].mean()
            agg_data[label] = means

        heatmap_df = pd.DataFrame(agg_data).dropna(how='all')

        # Normaliser chaque variable (z-score) pour comparer sur même échelle
        normalize = st.toggle("Normaliser (z-score, pour rendre comparables)", value=True)
        if normalize:
            heatmap_df_plot = (heatmap_df - heatmap_df.mean()) / heatmap_df.std()
            cmap_label = "Score standardisé"
        else:
            heatmap_df_plot = heatmap_df
            cmap_label = "Moyenne brute"

        if st.toggle("Regrouper les pays similaires (clustering)", value=False):
            from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
            from scipy.spatial.distance import pdist
            df_clean = heatmap_df_plot.dropna()
            if len(df_clean) > 2:
                Z = linkage(df_clean.values, method='ward')
                order = leaves_list(Z)
                heatmap_df_plot = df_clean.iloc[order]

        fig3, ax3 = plt.subplots(figsize=(max(10, len(selected_overview_vars) * 0.7),
                                          max(6, len(heatmap_df_plot) * 0.45)))
        fig3.patch.set_facecolor('#FAFAF8')

        cmap = LinearSegmentedColormap.from_list('evs', ['#D62828', '#F7F7F7', '#2A9D8F'])
        im = ax3.imshow(heatmap_df_plot.values, cmap=cmap, aspect='auto')

        ax3.set_xticks(range(len(heatmap_df_plot.columns)))
        ax3.set_xticklabels(heatmap_df_plot.columns, rotation=45, ha='right', fontsize=8.5)
        ax3.set_yticks(range(len(heatmap_df_plot.index)))
        ax3.set_yticklabels(heatmap_df_plot.index, fontsize=9)

        # Valeurs dans les cellules
        if st.toggle("Afficher les valeurs dans les cellules", value=False):
            for i in range(len(heatmap_df_plot.index)):
                for j in range(len(heatmap_df_plot.columns)):
                    val = heatmap_df.iloc[i, j] if not normalize else heatmap_df_plot.iloc[i, j]
                    if not np.isnan(val):
                        ax3.text(j, i, f"{val:.1f}", ha='center', va='center',
                                 fontsize=7, color='#111')

        cbar = fig3.colorbar(im, ax=ax3, shrink=0.6)
        cbar.set_label(cmap_label, fontsize=9)
        ax3.set_title("Comparaison pays × variables", fontsize=13, fontweight='bold',
                      color='#1A1A2E', pad=14)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

        st.markdown("""
        <div class='info-box'>
        🔴 Rouge = valeur plus basse · 🟢 Vert = valeur plus haute · ⚪ Blanc = moyenne<br>
        <b>Attention :</b> les échelles varient selon les variables — consultez l'onglet "Analyse" pour l'interprétation détaillée.
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — TABLEAU COMPARATIF
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## Tableau comparatif multi-variables")

    theme_table = st.selectbox("Thème", list(THEMES.keys()), key="table_theme")

    vars_table = THEMES[theme_table]
    available_table = {k: v for k, (v, _) in vars_table.items() if v in df.columns}

    if not available_table:
        st.warning("Aucune variable disponible pour ce thème.")
    else:
        agg_rows = {}
        for var_lbl, col in available_table.items():
            means = df.groupby('Pays')[col].mean().round(3)
            agg_rows[var_lbl] = means

        table_df = pd.DataFrame(agg_rows)

        # Tri par pays
        sort_col = st.selectbox("Trier par variable", ["(Pays)"] + list(table_df.columns))
        if sort_col == "(Pays)":
            table_df = table_df.sort_index()
        else:
            table_df = table_df.sort_values(sort_col, ascending=False)

        # Tableau HTML avec gradient sur la colonne de tri
        grad = sort_col if sort_col != "(Pays)" else None
        table_display = table_df.reset_index().rename(columns={'index': 'Pays'})
        html_table(table_display.round(3), gradient_col=grad)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_t = table_df.to_csv().encode('utf-8')
            st.download_button("📥 Télécharger CSV", csv_t,
                               f"comparaison_{theme_table[:20]}.csv", "text/csv")
        with col_dl2:
            # Export Excel
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    table_df.to_excel(writer, sheet_name='Comparaison')
                st.download_button("📥 Télécharger Excel", buffer.getvalue(),
                                   f"comparaison_{theme_table[:20]}.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except ImportError:
                pass

        # ── Top / Flop ──
        st.markdown("---")
        st.markdown("### 🏆 Classements")
        rank_var = st.selectbox("Variable à classer", list(table_df.columns), key="rank_var")

        col_top, col_bot = st.columns(2)
        ranked = table_df[rank_var].dropna().sort_values(ascending=False)

        with col_top:
            st.markdown(f"**🥇 Top 5 — {rank_var}**")
            for i, (pays, val) in enumerate(ranked.head(5).items(), 1):
                st.markdown(f"`{i}.` **{pays}** — {val:.3f}")

        with col_bot:
            st.markdown(f"**🔻 Bas de classement — {rank_var}**")
            for i, (pays, val) in enumerate(ranked.tail(5).iloc[::-1].items(), 1):
                st.markdown(f"`{i}.` **{pays}** — {val:.3f}")

# ════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — PROFIL D'UN PAYS
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## Profil détaillé d'un pays")

    avail_names = [COUNTRY_NAMES.get(c, c) for c in selected_codes]
    focus_country = st.selectbox("Pays à analyser", sorted(avail_names))

    # Récupérer code ISO
    focus_code = next((c for c in selected_codes if COUNTRY_NAMES.get(c, c) == focus_country), None)
    df_focus = df[df['Pays'] == focus_country]
    df_others = df[df['Pays'] != focus_country]

    if focus_code and len(df_focus) > 0:
        st.metric("Répondants", f"{len(df_focus):,}")
        st.markdown(f"**ISO :** `{focus_code}` · **Année :** {int(df_focus['Year survey'].mode()[0]) if 'Year survey' in df_focus.columns else 'N/A'}")

        st.markdown("---")
        st.markdown("### Comparaison avec les autres pays sélectionnés")

        # Radar-like : comparaison sur variables-clés
        key_profile_vars = {
            "Satisfaction vie": "Satisfaction with your life",
            "Bonheur": "Feeling of happiness",
            "Confiance générale": "Most people can be trusted",
            "Intérêt politique": "Interest in politics",
            "Importance démocratie": "Importance of democracy",
            "Importance Dieu": "How important is God in your life",
            "Homosexualité justifiable": "Justifiable: Homosexuality",
            "Importance famille": "Important in life: Family",
            "Confiance gouvernement": "Confidence: The Government",
        }

        profile_rows = []
        for label, col in key_profile_vars.items():
            if col in df.columns:
                val_focus = df_focus[col].mean()
                val_others = df_others[col].mean()
                val_all = df[col].mean()
                profile_rows.append({
                    'Variable': label,
                    focus_country: round(val_focus, 3),
                    'Autres pays (moy.)': round(val_others, 3),
                    'Écart': round(val_focus - val_others, 3),
                })

        profile_df = pd.DataFrame(profile_rows)

        # Graphique comparatif
        fig4, ax4 = plt.subplots(figsize=(10, max(5, len(profile_df) * 0.6)))
        fig4.patch.set_facecolor('#FAFAF8')
        ax4.set_facecolor('#FAFAF8')

        y = np.arange(len(profile_df))
        h = 0.35
        bars1 = ax4.barh(y + h/2, profile_df[focus_country], h,
                         color='#E63946', alpha=0.85, label=focus_country, zorder=3)
        bars2 = ax4.barh(y - h/2, profile_df['Autres pays (moy.)'], h,
                         color='#457B9D', alpha=0.7, label='Autres pays (moy.)', zorder=3)

        ax4.set_yticks(y)
        ax4.set_yticklabels(profile_df['Variable'], fontsize=9)
        ax4.set_xlabel('Moyenne', fontsize=9, color='#555')
        ax4.set_title(f"Profil de {focus_country} vs. autres pays", fontsize=13,
                      fontweight='bold', color='#1A1A2E', pad=14)
        ax4.legend(fontsize=9, loc='lower right')
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.grid(axis='x', alpha=0.25, zorder=0)

        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

        st.markdown("### Écarts par rapport aux autres pays sélectionnés")
        profile_display = profile_df[['Variable', focus_country, 'Autres pays (moy.)', 'Écart']].copy()
        html_table(profile_display.round(3), gradient_col='Écart')

        csv_profile = profile_display.to_csv(index=False).encode('utf-8')
        st.download_button(f"📥 Télécharger le profil de {focus_country}",
                           csv_profile, f"profil_{focus_code}.csv", "text/csv")

# ════════════════════════════════════════════════════════════════════════════
# ONGLET 5 — PROFIL PAYS COMPLET (toutes variables avec détail volume/%)
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## 🔬 Profil pays complet — Détail par variable")
    
    # Sélection du pays
    avail_names_full = [COUNTRY_NAMES.get(c, c) for c in selected_codes]
    country_full = st.selectbox("Pays à analyser en détail", sorted(avail_names_full), key="country_full")
    
    # Récupérer code ISO
    country_code_full = next((c for c in selected_codes if COUNTRY_NAMES.get(c, c) == country_full), None)
    
    if country_code_full:
        df_country = df[df['Country (ISO 3166-1 Alpha-2 code)'] == country_code_full].copy()
        
        st.metric("Nombre de répondants", f"{len(df_country):,}")
        st.markdown(f"**Code ISO :** `{country_code_full}`")
        
        st.markdown("---")
        
        # Sélection du thème
        theme_full = st.selectbox("📂 Thème", list(THEMES.keys()), key="theme_full")
        
        vars_in_theme_full = THEMES[theme_full]
        
        # Parcourir toutes les variables du thème
        st.markdown(f"### {theme_full}")
        
        for var_label_full, (col_name_full, scale_desc_full) in vars_in_theme_full.items():
            if col_name_full not in df_country.columns:
                continue
                
            with st.expander(f"📌 {var_label_full}"):
                st.markdown(f"<div style='font-size:0.8rem;color:#666;margin-bottom:0.8rem'><b>Échelle :</b> {scale_desc_full}</div>", unsafe_allow_html=True)
                
                data_country_var = df_country[col_name_full].dropna()
                
                if len(data_country_var) == 0:
                    st.warning("Aucune donnée disponible pour cette variable")
                    continue
                
                # Stats générales
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("N répondants", f"{len(data_country_var):,}")
                with col_stat2:
                    st.metric("Moyenne", f"{data_country_var.mean():.2f}")
                with col_stat3:
                    st.metric("Médiane", f"{data_country_var.median():.1f}")
                with col_stat4:
                    st.metric("Écart-type", f"{data_country_var.std():.2f}")
                
                # Distribution
                unique_vals_full = sorted(data_country_var.unique())
                
                if len(unique_vals_full) <= 15:
                    # Distribution détaillée pour variables catégorielles
                    value_counts = data_country_var.value_counts().sort_index()
                    total_resp = value_counts.sum()
                    
                    # Tableau volume + %
                    distrib_data = []
                    for val in value_counts.index:
                        count = value_counts[val]
                        pct = (count / total_resp) * 100
                        distrib_data.append({
                            'Valeur': int(val) if val == int(val) else val,
                            'Volume': int(count),
                            'Pourcentage': f"{pct:.1f}%"
                        })
                    
                    distrib_df = pd.DataFrame(distrib_data)
                    
                    col_table, col_chart = st.columns([1, 2])
                    
                    with col_table:
                        st.markdown("**Distribution**")
                        html_table(distrib_df)
                    
                    with col_chart:
                        st.markdown("**Visualisation**")
                        fig_d, ax_d = plt.subplots(figsize=(8, max(3, len(value_counts) * 0.4)))
                        fig_d.patch.set_facecolor('#FAFAF8')
                        ax_d.set_facecolor('#FAFAF8')
                        
                        colors_d = plt.cm.viridis(np.linspace(0.2, 0.9, len(value_counts)))
                        bars_d = ax_d.barh(range(len(value_counts)), value_counts.values, 
                                           color=colors_d, alpha=0.85, height=0.6)
                        
                        ax_d.set_yticks(range(len(value_counts)))
                        ax_d.set_yticklabels([f"Valeur {int(v)}" for v in value_counts.index], fontsize=9)
                        ax_d.set_xlabel('Nombre de répondants', fontsize=9)
                        ax_d.set_title(f'{var_label_full}', fontsize=10, fontweight='bold')
                        
                        # Ajouter les valeurs sur les barres
                        for i, (bar, val, pct_val) in enumerate(zip(bars_d, value_counts.values, 
                                                                      value_counts.values / total_resp * 100)):
                            ax_d.text(bar.get_width() + ax_d.get_xlim()[1] * 0.02, bar.get_y() + bar.get_height() / 2,
                                     f"{int(val):,} ({pct_val:.1f}%)", 
                                     va='center', fontsize=8, color='#000', fontweight='600')
                        
                        ax_d.spines['top'].set_visible(False)
                        ax_d.spines['right'].set_visible(False)
                        ax_d.grid(axis='x', alpha=0.2)
                        plt.tight_layout()
                        st.pyplot(fig_d)
                        plt.close()
                
                else:
                    # Variable continue : histogramme
                    fig_h, ax_h = plt.subplots(figsize=(10, 4))
                    fig_h.patch.set_facecolor('#FAFAF8')
                    ax_h.set_facecolor('#FAFAF8')
                    
                    ax_h.hist(data_country_var, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
                    ax_h.set_xlabel('Valeur', fontsize=9)
                    ax_h.set_ylabel('Fréquence', fontsize=9)
                    ax_h.set_title(f'{var_label_full}', fontsize=11, fontweight='bold')
                    ax_h.grid(axis='y', alpha=0.2)
                    plt.tight_layout()
                    st.pyplot(fig_h)
                    plt.close()
        
        # Export complet du profil pays
        st.markdown("---")
        st.markdown("### 💾 Export complet")
        
        # Générer un CSV avec toutes les stats du pays pour le thème
        export_rows = []
        for var_lbl, (col, scale) in vars_in_theme_full.items():
            if col in df_country.columns:
                vals = df_country[col].dropna()
                if len(vals) > 0:
                    value_counts_exp = vals.value_counts().sort_index()
                    # Une ligne par valeur possible
                    for val, count in value_counts_exp.items():
                        export_rows.append({
                            'Variable': var_lbl,
                            'Échelle': scale,
                            'Valeur': val,
                            'Volume': int(count),
                            'Pourcentage': f"{(count / len(vals)) * 100:.2f}%"
                        })
        
        if export_rows:
            export_df = pd.DataFrame(export_rows)
            csv_export = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📥 Télécharger le profil complet de {country_full} — {theme_full}",
                csv_export,
                f"profil_complet_{country_code_full}_{theme_full[:20]}.csv",
                "text/csv"
            )

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:0.75rem;color:#AAA;font-family:monospace'>"
    "EVS/WVS 2017–2022 · doi:10.4232/1.14320 · doi:10.14281/18241.26"
    "</div>",
    unsafe_allow_html=True
)
