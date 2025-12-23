import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from streamlit_qrcode_scanner import qrcode_scanner

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"

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
    /* Fond de l'application blanc et texte général noir */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    
    /* Forcer le noir sur TOUS les éléments de texte */
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; }
    
    /* Forcer le noir dans les champs de saisie (Inputs) */
    input, textarea, [data-baseweb="input"] { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
    }
    
    /* Forcer le noir dans les formulaires et les expanders */
    .stForm, div[data-testid="stExpander"], .stTabs { color: #000000 !important; }

    /* Cartes Produits et Cadeaux */
    .product-card, .gift-card {
        border: 1px solid #ddd; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff; margin-bottom: 20px; color: #000 !important;
    }
    .gift-card { border: 2px dashed #28a745; background-color: #f9fff9; }
    .point-badge { background-color: #28a745; color: white !important; padding: 5px 10px; border-radius: 20px; font-weight: bold; }

    /* Style Sidebar (Garder sombre pour le contraste) */
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
        user_email = st.session_state.user_connected['Email']
        # Refresh points en temps réel
        pts_actuels = st.session_state.clients[st.session_state.clients['Email'] == user_email]['Points'].values[0]
        st.success(f"Client : {st.session_state.user_connected['Prenom']}")
        st.markdown(f"### ⭐ Mes Points : **{pts_actuels}**")
        menu = st.radio("Navigation", ["📱 Mon Badge QR", "🛒 Rayons", "🎁 Cadeaux", "📟 CAISSE"])
        if st.button("Déconnexion"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        menu = st.radio("Navigation", ["🔑 Connexion", "🛒 Rayons"])

# ---------------- PAGE : CAISSE (SCANNER & POINTS) ---------------- #
if menu == "📟 CAISSE":
    st.title("📟 Interface Caisse")
    st.write("Scannez le badge du client pour créditer les points :")
    
    email_scanne = qrcode_scanner(key='scanner_caisse')
    
    # Choix du client (automatique par scan ou manuel)
    target_email = email_scanne if email_scanne else st.selectbox("Ou sélectionnez manuellement :", [""] + list(st.session_state.clients['Email'].unique()))

    if target_email and target_email != "":
        user_row = st.session_state.clients[st.session_state.clients['Email'] == target_email]
        if not user_row.empty:
            client = user_row.iloc[0]
            st.markdown(f"**Client détecté :** {client['Prenom']} {client['Nom']}")
            st.markdown(f"**Solde actuel :** {client['Points']} points")
            
            montant = st.number_input("Montant de l'achat (€)", min_value=0.0, step=1.0)
            points_gagnes = int(montant / 10)
            
            st.write(f"📈 Points à ajouter (10%) : **{points_gagnes}**")
            
            if st.button("Valider l'achat"):
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == target_email][0]
                st.session_state.clients.at[idx, 'Points'] += points_gagnes
                sauvegarder_donnees(st.session_state.clients)
                st.success(f"Transaction réussie ! +{points_gagnes} points.")
                st.balloons()
                st.rerun()

# ---------------- PAGE : MON BADGE QR ---------------- #
elif menu == "📱 Mon Badge QR":
    st.title("Mon Badge Fidélité")
    email = st.session_state.user_connected['Email']
    
    # Génération du QR Code basé uniquement sur l'email
    qr = qrcode.make(email)
    buf = BytesIO()
    qr.save(buf)
    
    st.write("Présentez ce code à la caisse pour vos points.")
    st.image(buf.getvalue(), caption=f"ID Client : {email}", width=300)
    st.info("Ce badge permet au gérant de vous identifier rapidement.")

# ---------------- PAGE : RAYONS (LES 19) ---------------- #
elif menu == "🛒 Rayons":
    st.title("Nos Rayons")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Choisir un rayon", rayons)
    
    st.header(f"Rayon {choix}")
    st.info(f"Les promotions du rayon {choix} arrivent bientôt !")

# ---------------- PAGE : CADEAUX FIDÉLITÉ ---------------- #
elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique Cadeaux")
    st.write("Échangez vos points contre ces articles gratuits :")
    
    cadeaux = [("Lait 1L", 2), ("Farine 1kg", 3), ("Couscous 500g", 1)]
    cols = st.columns(3)
    
    for i, (prod, coût) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><br><span class="point-badge">{coût} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}", key=f"btn_{prod}"):
                u_email = st.session_state.user_connected['Email']
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == u_email][0]
                
                if st.session_state.clients.at[idx, 'Points'] >= coût:
                    st.session_state.clients.at[idx, 'Points'] -= coût
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Cadeau obtenu !")
                    st.rerun()
                else:
                    st.error("Points insuffisants.")

# ---------------- PAGE : CONNEXION & INSCRIPTION ---------------- #
elif menu == "🔑 Connexion":
    st.title("Espace Client VM")
    tab1, tab2 = st.tabs(["Se connecter", "Créer un compte"])
    
    with tab1:
        e = st.text_input("Email", key="login_email")
        p = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Entrer"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == e) & (st.session_state.clients["Password"] == p)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
                
    with tab2:
        with st.form("form_inscription"):
            st.write("### Nouveau client")
            n = st.text_input("Nom")
            pr = st.text_input("Prénom")
            em = st.text_input("Email professionnel ou perso")
            md = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("S'inscrire"):
                if em and md:
                    new_u = pd.DataFrame([{"Nom": n, "Prenom": pr, "Email": em, "Password": md, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_u], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé ! Connectez-vous sur l'onglet d'à côté.")
                else:
                    st.warning("Veuillez remplir les champs Email et Mot de passe.")
