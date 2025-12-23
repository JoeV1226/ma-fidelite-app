import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
# REMPLACE PAR TON URL REELLE :
APP_URL = "https://ma-fidelite-app.streamlit.app" 

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()

# --- DETECTION AUTOMATIQUE DU SCAN (PARAMETRE URL) ---
query_params = st.query_params
scanned_client = query_params.get("client")

# ---------------- STYLE CSS (Noir sur Blanc) ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    [data-testid="stSidebar"] { background-color: #343a40; color: white; }
    .product-card {
        border: 1px solid #eee; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff; margin-bottom: 20px;
    }
    .gift-card {
        border: 2px dashed #28a745; border-radius: 15px; padding: 15px;
        text-align: center; background-color: #f9fff9; margin-bottom: 10px;
    }
    .point-badge {
        background-color: #28a745; color: white; padding: 5px 10px;
        border-radius: 20px; font-weight: bold;
    }
    .qr-container { text-align: center; border: 2px solid #000; padding: 20px; border-radius: 20px; margin: 10px 0; }
    .stat-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- NAVIGATION SIDEBAR ---------------- #
with st.sidebar:
    st.title("VM Magasin")
    
    if "user_connected" not in st.session_state:
        st.session_state.user_connected = None

    if st.session_state.user_connected:
        user_email = st.session_state.user_connected['Email']
        # Rafraîchir les points depuis la DB
        pts_actuels = st.session_state.clients[st.session_state.clients['Email'] == user_email]['Points'].values[0]
        st.success(f"Client : {st.session_state.user_connected['Prenom']}")
        st.markdown(f"### ⭐ Points : **{pts_actuels}**")
        
        menu = st.radio("Navigation", ["📱 Mon Badge QR", "🛒 Rayons", "🎁 Cadeaux", "📟 CAISSE"])
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        st.info("Veuillez vous connecter")
        menu = st.radio("Navigation", ["🔑 Connexion", "🛒 Rayons"])

# ---------------- PAGE : CAISSE (SCAN AUTOMATIQUE OU MANUEL) ---------------- #
if menu == "📟 CAISSE" or scanned_client:
    st.title("📟 Interface Caisse")
    
    # On détermine quel client on traite (soit par scan URL, soit par menu)
    target_email = scanned_client if scanned_client else st.selectbox("Sélectionner le client", st.session_state.clients['Email'].unique())
    
    if target_email:
        user_row = st.session_state.clients[st.session_state.clients['Email'] == target_email]
        if not user_row.empty:
            client = user_row.iloc[0]
            st.markdown(f"""<div class="stat-box">
                <h3>Client : {client['Prenom']} {client['Nom']}</h3>
                <p style='font-size: 1.2em;'>Solde : <b>{client['Points']} Points</b></p>
            </div>""", unsafe_allow_html=True)
            
            montant = st.number_input("Montant total des courses (€)", min_value=0.0, step=0.5)
            # Calcul : 1 point pour 10€
            points_gagnes = int(montant / 10)
            
            st.write(f"📈 Points à ajouter : **{points_gagnes}**")
            
            if st.button("Valider et Créditer"):
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == target_email][0]
                st.session_state.clients.at[idx, 'Points'] += points_gagnes
                sauvegarder_donnees(st.session_state.clients)
                st.success(f"Succès ! {points_gagnes} points ajoutés.")
                st.balloons()
                # On nettoie l'URL et on refresh
                st.query_params.clear()
                st.rerun()

# ---------------- PAGE : MON BADGE QR ---------------- #
elif menu == "📱 Mon Badge QR":
    st.title("Mon Badge Fidélité")
    email = st.session_state.user_connected['Email']
    # Le QR code contient le LIEN de l'app avec l'email en paramètre
    qr_link = f"{APP_URL}?client={email}"
    
    qr = qrcode.make(qr_link)
    buf = BytesIO()
    qr.save(buf)
    
    st.write("Présentez ce code à la caisse pour vos points.")
    st.markdown('<div class="qr-container">', unsafe_allow_html=True)
    st.image(buf.getvalue(), width=300)
    st.markdown('</div>', unsafe_allow_html=True)
    st.info("Ce code ouvre directement votre fiche client sur le téléphone du gérant.")

# ---------------- PAGE : RAYONS (LES 19) ---------------- #
elif menu == "🛒 Rayons":
    st.title("Nos Promotions")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Choisir un rayon", rayons)
    
    col1, col2 = st.columns(2)
    if choix == "🥩 Boucherie":
        with col1: st.markdown('<div class="product-card"><b>Viande Hachée</b><br><span style="text-decoration:line-through; color:red;">9,99€</span> <span style="color:green; font-weight:bold;">8,99€/kg</span></div>', unsafe_allow_html=True)
        with col2: st.markdown('<div class="product-card"><b>Merguez</b><br><span style="text-decoration:line-through; color:red;">13,99€</span> <span style="color:green; font-weight:bold;">12,99€/kg</span></div>', unsafe_allow_html=True)
    elif choix == "🍎 Fruits & Légumes":
        with col1: st.markdown('<div class="product-card"><b>Bananes</b><br><span style="text-decoration:line-through; color:red;">2,00€</span> <span style="color:green; font-weight:bold;">1,59€/kg</span></div>', unsafe_allow_html=True)
    else:
        st.info(f"Consultez les arrivages du rayon {choix} en magasin.")

# ---------------- PAGE : CADEAUX ---------------- #
elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique Fidélité")
    st.write("Échangez vos points contre des produits gratuits.")
    cadeaux = [("Lait 1L", 2), ("Farine 1kg", 3), ("Couscous 500g", 1)]
    cols = st.columns(3)
    for i, (prod, prix) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span class="point-badge">{prix} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}"):
                email = st.session_state.user_connected['Email']
                idx = st.session_state.clients.index[st.session_state.clients['Email'] == email][0]
                if st.session_state.clients.at[idx, 'Points'] >= prix:
                    st.session_state.clients.at[idx, 'Points'] -= prix
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Cadeau validé !")
                    st.rerun()
                else:
                    st.error("Points insuffisants.")

# ---------------- PAGE : CONNEXION & INSCRIPTION ---------------- #
elif menu == "🔑 Connexion":
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    with tab1:
        email = st.text_input("Email")
        mdp = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email) & (st.session_state.clients["Password"] == mdp)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
    with tab2:
        with st.form("inscription"):
            n = st.text_input("Nom")
            p = st.text_input("Prénom")
            e = st.text_input("Email")
            m = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Valider"):
                new_u = pd.DataFrame([{"Nom": n, "Prenom": p, "Email": e, "Password": m, "Points": 0, "Statut": "Actif"}])
                st.session_state.clients = pd.concat([st.session_state.clients, new_u], ignore_index=True)
                sauvegarder_donnees(st.session_state.clients)
                st.success("Compte créé ! Connectez-vous.")
