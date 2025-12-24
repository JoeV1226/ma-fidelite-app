import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from streamlit_qrcode_scanner import qrcode_scanner

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
# TON EMAIL CONFIGURÉ COMME SEUL ADMINISTRATEUR
ADMIN_EMAIL = "douglaceb@gmail.com" 

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()

# ---------------- STYLE CSS (MEGA MARKET BRANDING) ---------------- #
st.markdown("""
    <style>
    /* Fond blanc et texte noir forcé */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; }
    
    /* Correction visibilité des champs de saisie */
    input, textarea, [data-baseweb="input"] { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
    }
    .stForm, div[data-testid="stExpander"], .stTabs { color: #000000 !important; }

    /* Cartes Produits et Cadeaux */
    .product-card, .gift-card {
        border: 1px solid #ddd; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff; margin-bottom: 20px; color: #000 !important;
    }
    .gift-card { border: 2px dashed #007bff; background-color: #f0f7ff; }
    .point-badge { background-color: #007bff; color: white !important; padding: 5px 10px; border-radius: 20px; font-weight: bold; }

    /* Sidebar Sombre */
    [data-testid="stSidebar"] { background-color: #1a1a1a; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #ffffff !important; 
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
            # Refresh points client
            pts = st.session_state.clients[st.session_state.clients['Email'] == user['Email']]['Points'].values[0]
            st.metric("⭐ Mes Points Mega Market", f"{pts}")
            menu = st.radio("Menu", ["📱 Mon Badge QR", "🛒 Rayons", "🎁 Cadeaux"])
        
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["🔑 Connexion", "🛒 Rayons"])

# ---------------- LOGIQUE DES PAGES ---------------- #

# --- PAGE CAISSE (ADMIN SEULEMENT) ---
if menu == "📟 CAISSE (Scanner)":
    st.title("📟 Caisse Mega Market")
    st.write("Scannez le badge pour créditer le client.")
    
    scanned_email = qrcode_scanner(key='scanner_mega')
    target = scanned_email if scanned_email else st.selectbox("Ou choisir manuellement :", [""] + list(st.session_state.clients['Email'].unique()))

    if target and target != "":
        user_row = st.session_state.clients[st.session_state.clients['Email'] == target]
        if not user_row.empty:
            c = user_row.iloc[0]
            st.markdown(f"### Client : {c['Prenom']} {c['Nom']}")
            montant = st.number_input("Montant de l'achat (€)", min_value=0.0, step=1.0)
            bonus = int(montant / 10) # 1 point tous les 10€
            
            if st.button(f"Ajouter {bonus} points"):
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == target][0]
                st.session_state.clients.at[idx, 'Points'] += bonus
                sauvegarder_donnees(st.session_state.clients)
                st.success("Points mis à jour !")
                st.balloons()
                st.rerun()

# --- PAGE LISTE CLIENTS (ADMIN SEULEMENT) ---
elif menu == "👥 Liste Clients":
    st.title("👥 Gestionnaire de Clients")
    st.dataframe(st.session_state.clients[["Nom", "Prenom", "Email", "Points", "Statut"]])

# --- PAGE MON BADGE (CLIENT UNIQUEMENT) ---
elif menu == "📱 Mon Badge QR":
    st.title("Mon Badge Mega Market")
    email_client = st.session_state.user_connected['Email']
    qr = qrcode.make(email_client)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Présentez ce code en caisse", width=300)

# --- PAGE RAYONS (TOUS) ---
elif menu == "🛒 Rayons":
    st.title("Rayons Mega Market")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Choisir un rayon :", rayons)
    st.info(f"Consultez nos arrivages pour le rayon {choix} en magasin !")

# --- PAGE CADEAUX (CLIENT UNIQUEMENT) ---
elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique Cadeaux")
    cadeaux = [("Lait 1L", 2), ("Farine 1kg", 3), ("Couscous 500g", 1)]
    cols = st.columns(3)
    for i, (prod, coût) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span class="point-badge">{coût} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}", key=f"gift_{prod}"):
                u_email = st.session_state.user_connected['Email']
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == u_email][0]
                if st.session_state.clients.at[idx, 'Points'] >= coût:
                    st.session_state.clients.at[idx, 'Points'] -= coût
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Cadeau validé !")
                    st.rerun()
                else:
                    st.error("Points insuffisants.")

# --- PAGE CONNEXION ---
elif menu == "🔑 Connexion":
    st.title("Espace Fidélité Mega Market")
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    with tab1:
        e = st.text_input("Email", key="login_e")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            u = st.session_state.clients[(st.session_state.clients["Email"] == e) & (st.session_state.clients["Password"] == p)]
            if not u.empty:
                st.session_state.user_connected = u.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    with tab2:
        with st.form("inscription"):
            st.write("### Devenir membre Mega Market")
            n = st.text_input("Nom")
            pr = st.text_input("Prénom")
            mail = st.text_input("Email")
            passw = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("S'inscrire"):
                if mail and passw:
                    new_cl = pd.DataFrame([{"Nom": n, "Prenom": pr, "Email": mail, "Password": passw, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_cl], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé avec succès !")
