import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from streamlit_qrcode_scanner import qrcode_scanner

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
# --- TON EMAIL EST MAINTENANT CONFIGURÉ COMME ADMIN ---
ADMIN_EMAIL = "douglaceb@gmail.com" 

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()

# ---------------- STYLE CSS (FORCER LE NOIR ET BLANC) ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; }
    input, textarea, [data-baseweb="input"] { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
    }
    .stForm, div[data-testid="stExpander"], .stTabs { color: #000000 !important; }
    .product-card, .gift-card {
        border: 1px solid #ddd; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff; margin-bottom: 20px; color: #000 !important;
    }
    .gift-card { border: 2px dashed #28a745; background-color: #f9fff9; }
    .point-badge { background-color: #28a745; color: white !important; padding: 5px 10px; border-radius: 20px; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #343a40; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #ffffff !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- NAVIGATION SIDEBAR ---------------- #
with st.sidebar:
    st.title("VM Magasin")
    if "user_connected" not in st.session_state:
        st.session_state.user_connected = None

    if st.session_state.user_connected:
        user = st.session_state.user_connected
        # Vérification si l'utilisateur est l'admin
        is_admin = (user['Email'] == ADMIN_EMAIL)
        
        st.success(f"Connecté : {user['Prenom']}")
        
        if is_admin:
            st.warning("🔒 ESPACE GÉRANT")
            menu = st.radio("Actions", ["📟 CAISSE (Scanner)", "👥 Liste Clients", "🛒 Rayons"])
        else:
            # Refresh points pour le client
            pts = st.session_state.clients[st.session_state.clients['Email'] == user['Email']]['Points'].values[0]
            st.metric("⭐ Mes Points", f"{pts} pts")
            menu = st.radio("Menu", ["📱 Mon Badge QR", "🛒 Rayons", "🎁 Cadeaux"])
        
        if st.button("Déconnexion"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["🔑 Connexion", "🛒 Rayons"])

# ---------------- LOGIQUE DES PAGES ---------------- #

# --- PAGE : CAISSE (RÉSERVÉ ADMIN) ---
if menu == "📟 CAISSE (Scanner)":
    st.title("📟 Interface Encaissement")
    st.write("Scannez le badge du client pour ajouter des points.")
    
    scanned_email = qrcode_scanner(key='scanner_admin')
    target = scanned_email if scanned_email else st.selectbox("Ou chercher un email :", [""] + list(st.session_state.clients['Email'].unique()))

    if target and target != "":
        user_row = st.session_state.clients[st.session_state.clients['Email'] == target]
        if not user_row.empty:
            c = user_row.iloc[0]
            st.markdown(f"### Client : {c['Prenom']} {c['Nom']}")
            st.write(f"Solde actuel : {c['Points']} points")
            
            montant = st.number_input("Montant total payé (€)", min_value=0.0, step=1.0)
            bonus = int(montant / 10)
            
            if st.button(f"Créditer {bonus} points"):
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == target][0]
                st.session_state.clients.at[idx, 'Points'] += bonus
                sauvegarder_donnees(st.session_state.clients)
                st.success("Points ajoutés avec succès !")
                st.balloons()
                st.rerun()

# --- PAGE : LISTE CLIENTS (RÉSERVÉ ADMIN) ---
elif menu == "👥 Liste Clients":
    st.title("👥 Gestion des Clients")
    st.write("Liste complète des membres du programme de fidélité :")
    st.dataframe(st.session_state.clients[["Nom", "Prenom", "Email", "Points", "Statut"]])

# --- PAGE : MON BADGE QR (CLIENT UNIQUEMENT) ---
elif menu == "📱 Mon Badge QR":
    st.title("Mon Badge Fidélité")
    email_client = st.session_state.user_connected['Email']
    qr = qrcode.make(email_client)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="À scanner lors de votre passage en caisse", width=300)

# --- PAGE : RAYONS (ACCESSIBLE À TOUS) ---
elif menu == "🛒 Rayons":
    st.title("Nos Rayons & Promos")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Voir les offres de :", rayons)
    st.info(f"Les meilleures offres pour {choix} s'afficheront ici.")

# --- PAGE : CADEAUX (CLIENT UNIQUEMENT) ---
elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique de récompenses")
    cadeaux = [("Lait 1L", 2), ("Farine 1kg", 3), ("Couscous 500g", 1)]
    cols = st.columns(3)
    for i, (prod, coût) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span class="point-badge">{coût} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}", key=prod):
                u_email = st.session_state.user_connected['Email']
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == u_email][0]
                if st.session_state.clients.at[idx, 'Points'] >= coût:
                    st.session_state.clients.at[idx, 'Points'] -= coût
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Cadeau validé !")
                    st.rerun()
                else:
                    st.error("Points insuffisants.")

# --- PAGE : CONNEXION ---
elif menu == "🔑 Connexion":
    st.title("Bienvenue chez VM Magasin")
    t1, t2 = st.tabs(["Se connecter", "S'inscrire"])
    with t1:
        e = st.text_input("Email", key="log_e")
        p = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Connexion"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == e) & (st.session_state.clients["Password"] == p)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
    with t2:
        with st.form("inscription"):
            st.write("### Créer votre compte")
            n, pr = st.columns(2)
            nom = n.text_input("Nom")
            prenom = pr.text_input("Prénom")
            mail = st.text_input("Email")
            passw = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Valider l'inscription"):
                if mail and passw:
                    new_cl = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Email": mail, "Password": passw, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_cl], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé ! Connectez-vous sur l'onglet d'à côté.")
