import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from streamlit_qrcode_scanner import qrcode_scanner

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
ADMIN_EMAIL = "douglaceb@gmail.com" 

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()

# ---------------- STYLE CSS (NETTOYAGE ABSOLU V4) ---------------- #
st.markdown("""
    <style>
    /* 1. SUPPRESSION TOTALE ET INVISIBLE DES ÉLÉMENTS STREAMLIT */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* CIBLAGE DE TOUS LES BADGES POSSIBLES (Même les nouveaux) */
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="styles_viewerBadge"] {display: none !important;}
    div[class*="Mui"] {display: none !important;} /* Parfois utilisé pour les popups */
    iframe[title="Managed Hosting Badge"] {display: none !important;}
    #streamlitDetails {display: none !important;}
    
    /* 2. STYLE GÉNÉRAL MEGA MARKET */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; }
    
    /* Forcer le noir pour les inputs */
    input, textarea, [data-baseweb="input"] { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
    }

    /* Sidebar Sombre */
    [data-testid="stSidebar"] { background-color: #1a1a1a; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #ffffff !important; 
    }

    /* Cartes Cadeaux */
    .gift-card {
        border: 2px dashed #007bff; border-radius: 15px; padding: 15px;
        text-align: center; background-color: #f0f7ff; color: #000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- NAVIGATION SIDEBAR ---------------- #
with st.sidebar:
    st.title("🛒 Mega Market")
    if "user_connected" not in st.session_state:
        st.session_state.user_connected = None

    if st.session_state.user_connected:
        user = st.session_state.user_connected
        is_admin = (user['Email'] == ADMIN_EMAIL)
        st.success(f"Bonjour, {user['Prenom']}")
        
        if is_admin:
            st.warning("🔒 MODE GÉRANT ACTIVÉ")
            menu = st.radio("Actions", ["📟 CAISSE (Scanner)", "👥 Liste Clients", "🛒 Rayons"])
        else:
            pts = st.session_state.clients[st.session_state.clients['Email'] == user['Email']]['Points'].values[0]
            st.metric("⭐ Mes Points Mega Market", f"{pts}")
            menu = st.radio("Menu", ["📱 Mon Badge QR", "🛒 Rayons", "🎁 Cadeaux"])
        
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["🔑 Connexion", "🛒 Rayons"])

# ---------------- LOGIQUE DES PAGES ---------------- #

if menu == "📟 CAISSE (Scanner)":
    st.title("📟 Caisse Mega Market")
    scanned_email = qrcode_scanner(key='scanner_vfinal')
    target = scanned_email if scanned_email else st.selectbox("Ou choisir manuellement :", [""] + list(st.session_state.clients['Email'].unique()))
    if target and target != "":
        user_row = st.session_state.clients[st.session_state.clients['Email'] == target]
        if not user_row.empty:
            c = user_row.iloc[0]
            st.markdown(f"### Client : {c['Prenom']} {c['Nom']}")
            montant = st.number_input("Montant de l'achat (€)", min_value=0.0, step=1.0)
            if st.button(f"Confirmer l'ajout"):
                bonus = int(montant / 10)
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == target][0]
                st.session_state.clients.at[idx, 'Points'] += bonus
                sauvegarder_donnees(st.session_state.clients)
                st.success("Points mis à jour !")
                st.rerun()

elif menu == "👥 Liste Clients":
    st.title("👥 Gestionnaire de Clients")
    st.dataframe(st.session_state.clients[["Nom", "Prenom", "Email", "Points", "Statut"]])

elif menu == "📱 Mon Badge QR":
    st.title("Mon Badge Mega Market")
    email_client = st.session_state.user_connected['Email']
    qr = qrcode.make(email_client)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="À scanner en caisse", width=300)

elif menu == "🛒 Rayons":
    st.title("Rayons Mega Market")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    st.selectbox("Choisir un rayon :", rayons)

elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique Cadeaux")
    cadeaux = [("Lait 1L", 2), ("Farine 1kg", 3), ("Couscous 500g", 1)]
    cols = st.columns(3)
    for i, (prod, coût) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span style="color:blue">{coût} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}", key=f"gift_{prod}"):
                u_email = st.session_state.user_connected['Email']
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == u_email][0]
                if st.session_state.clients.at[idx, 'Points'] >= coût:
                    st.session_state.clients.at[idx, 'Points'] -= coût
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Cadeau validé !")
                    st.rerun()

elif menu == "🔑 Connexion":
    st.title("Espace Fidélité Mega Market")
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        e = st.text_input("Email", key="login_e")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            u = st.session_state.clients[(st.session_state.clients["Email"] == e) & (st.session_state.clients["Password"] == p)]
            if not u.empty:
                st.session_state.user_connected = u.iloc[0].to_dict()
                st.rerun()
