import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # On s'assure que les colonnes nécessaires existent
    return pd.DataFrame(columns=["Nom", "Prenom", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# ---------------- STYLE CSS PROFESSIONNEL ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
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
    .old-price { text-decoration: line-through; color: #cc0000; }
    .new-price { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIQUE POINTS ---------------- #
def modifier_points(email, valeur, operation="ajout"):
    idx = st.session_state.clients.index[st.session_state.clients['Email'] == email]
    if not idx.empty:
        if operation == "ajout":
            st.session_state.clients.at[idx[0], 'Points'] += valeur
        else:
            if st.session_state.clients.at[idx[0], 'Points'] >= valeur:
                st.session_state.clients.at[idx[0], 'Points'] -= valeur
            else:
                return False
        sauvegarder_donnees(st.session_state.clients)
        return True
    return False

# ---------------- NAVIGATION SIDEBAR ---------------- #
with st.sidebar:
    st.title("VM Magasin")
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Accès Client")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        if st.button("Créer un compte"):
            st.session_state.show_signup = True
        menu = st.radio("Navigation", ["🔥 Offres Rayons"])
    else:
        # Update point display
        u_email = st.session_state.user_connected['Email']
        pts = st.session_state.clients[st.session_state.clients['Email'] == u_email]['Points'].values[0]
        st.success(f"Client : {st.session_state.user_connected['Prenom']}")
        st.markdown(f"### ⭐ Points : **{pts}**")
        
        menu = st.radio("Menu", ["📱 Mon QR Code", "🔥 Offres Rayons", "🎁 Cadeaux", "📟 CAISSE (Admin)"])
        
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# ---------------- INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    with st.expander("📝 INSCRIPTION NOUVEAU CLIENT", expanded=True):
        with st.form("form_reg"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            mdp = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                if email and mdp:
                    new_u = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_u], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé ! Connectez-vous.")
                    st.session_state.show_signup = False
                else:
                    st.warning("Veuillez remplir les champs obligatoires.")

# ---------------- PAGE : MON QR CODE ---------------- #
if menu == "📱 Mon QR Code":
    st.title("Mon Badge Fidélité")
    user_email = st.session_state.user_connected['Email']
    st.write("Présentez ce code à la caisse pour accumuler vos points automatiquement.")
    
    # Génération du QR Code basé sur l'email
    qr = qrcode.make(user_email)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption=f"ID Client : {user_email}", width=250)
    st.info("Prenez une capture d'écran pour l'avoir toujours sur vous !")

# ---------------- PAGE : RAYONS ---------------- #
elif menu == "🔥 Offres Rayons":
    st.title("Découvrez nos rayons")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boisson", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Choisir un rayon pour voir les promos", rayons)
    
    col1, col2 = st.columns(2)
    if choix == "🥩 Boucherie":
        with col1: st.markdown('<div class="product-card"><b>Viande Hachée</b><br><span class="old-price">9,99€</span> <span class="new-price">8,99€/kg</span></div>', unsafe_allow_html=True)
    elif choix == "🍎 Fruits & Légumes":
        with col1: st.markdown('<div class="product-card"><b>Pommes Bio</b><br><span class="old-price">3,50€</span> <span class="new-price">2,80€/kg</span></div>', unsafe_allow_html=True)
    else:
        st.info("Promotions bientôt disponibles dans ce rayon.")

# ---------------- PAGE : CADEAUX ---------------- #
elif menu == "🎁 Cadeaux":
    st.title("🎁 Boutique Cadeaux")
    st.write("Échangez vos points contre des produits gratuits.")
    
    items = [("Lait 1L", 2), ("Farine 1kg", 3), ("Paquet de Sucre", 5)]
    cols = st.columns(3)
    for i, (prod, coût) in enumerate(items):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span class="point-badge">{coût} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}"):
                if modifier_points(st.session_state.user_connected['Email'], coût, "deduction"):
                    st.success("Cadeau validé !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Points insuffisants.")

# ---------------- PAGE : CAISSE (SCAN & PAY) ---------------- #
elif menu == "📟 CAISSE (Admin)":
    st.title("📟 Interface Encaissement")
    st.write("Scannez le code du client ou sélectionnez son email ci-dessous.")
    
    with st.form("form_caisse"):
        client_id = st.selectbox("Client à créditer", st.session_state.clients['Email'].unique())
        montant_total = st.number_input("Montant total payé par le client (€)", min_value=0.0, step=0.1)
        
        # Calcul automatique : 1 point par tranche de 10€ (ex: 150€ -> 15 points)
        points_a_ajouter = int(montant_total / 10)
        
        st.write(f"👉 **Points à créditer : {points_a_ajouter}**")
        
        if st.form_submit_button("Valider le paiement"):
            if client_id and points_a_ajouter > 0:
                modifier_points(client_id, points_a_ajouter, "ajout")
                st.success(f"Paiement de {montant_total}€ enregistré. {points_a_ajouter} points ajoutés à {client_id}")
                st.rerun()
            else:
                st.warning("Montant insuffisant pour générer des points.")
