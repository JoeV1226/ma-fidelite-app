import streamlit as st
import pandas as pd
import os
import datetime

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Nom", "Prenom", "Age", "Email", "Password", "Points", "Statut"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

if "clients" not in st.session_state:
    st.session_state.clients = charger_donnees()
if "user_connected" not in st.session_state:
    st.session_state.user_connected = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# ---------------- STYLE CSS (Professionnel) ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    p, span, label, h1, h2, h3 { color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #343a40; color: white; }
    
    /* Cartes Produits */
    .product-card {
        border: 1px solid #eee;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff;
        margin-bottom: 20px;
    }
    
    /* Cartes Cadeaux */
    .gift-card {
        border: 2px dashed #28a745;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        background-color: #f9fff9;
        margin-bottom: 10px;
    }
    .point-badge {
        background-color: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
    }
    .old-price { text-decoration: line-through; color: #cc0000; }
    .new-price { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIQUE POINTS ---------------- #
def modifier_points(email, montant, operation="ajout"):
    idx = st.session_state.clients.index[st.session_state.clients['Email'] == email]
    if not idx.empty:
        if operation == "ajout":
            st.session_state.clients.at[idx[0], 'Points'] += montant
        else:
            if st.session_state.clients.at[idx[0], 'Points'] >= montant:
                st.session_state.clients.at[idx[0], 'Points'] -= montant
            else:
                return False
        sauvegarder_donnees(st.session_state.clients)
        return True
    return False

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("VM Magasin")
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Connexion")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        col_l, col_s = st.columns(2)
        if col_l.button("Connexion"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Erreur d'identifiants")
        if col_s.button("S'inscrire"):
            st.session_state.show_signup = True
    else:
        # Refresh points display
        u_email = st.session_state.user_connected['Email']
        pts_actuels = st.session_state.clients[st.session_state.clients['Email'] == u_email]['Points'].values[0]
        st.success(f"Salut {st.session_state.user_connected['Prenom']} !")
        st.markdown(f"### ⭐ Points : **{pts_actuels}**")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

    st.divider()
    menu = st.radio("Aller vers", ["🔥 Offres Rayons", "🎁 Cadeaux Fidélité", "📟 CAISSE (Admin)"])

# ---------------- INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    with st.expander("📝 CRÉER MON COMPTE", expanded=True):
        with st.form("inscription"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            mdp = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Valider"):
                new_u = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"}])
                st.session_state.clients = pd.concat([st.session_state.clients, new_u], ignore_index=True)
                sauvegarder_donnees(st.session_state.clients)
                st.success("Compte créé ! Connectez-vous à gauche.")
                st.session_state.show_signup = False

# ---------------- PAGE RAYONS ---------------- #
if menu == "🔥 Offres Rayons":
    st.title("Nos Rayons")
    rayons = ["🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boison", "🧂 Condiment", "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", "🥫 Conserve/Bocaux", "🌱 Leguminseuse", "🥜 Fruit sec", "📦 Rayon sec", "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", "🍳 Espace cuisine", "👕 Pret a porter", "🥦 Produit frais", "🌻 Huile"]
    choix = st.selectbox("Choisir un rayon", rayons)
    
    st.header(f"Promo {choix}")
    col1, col2 = st.columns(2)
    
    if choix == "🥩 Boucherie":
        with col1:
            st.markdown('<div class="product-card"><b>Viande Hachée</b><br><span class="old-price">9,99€</span> <span class="new-price">8,99€/kg</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="product-card"><b>Merguez</b><br><span class="old-price">13,99€</span> <span class="new-price">12,99€/kg</span></div>', unsafe_allow_html=True)
    elif choix == "🍎 Fruits & Légumes":
        with col1:
            st.markdown('<div class="product-card"><b>Bananes</b><br><span class="old-price">2,00€</span> <span class="new-price">1,59€/kg</span></div>', unsafe_allow_html=True)
    else:
        st.info("Arrivage en cours pour ce rayon...")

# ---------------- PAGE CADEAUX ---------------- #
elif menu == "🎁 Cadeaux Fidélité":
    st.title("🎁 Produits Gratuits")
    st.write("Échangez vos points ici :")
    
    cadeaux = [("Lait", 2), ("Farine", 3), ("Couscous", 1)]
    cols = st.columns(3)
    
    for i, (prod, prix) in enumerate(cadeaux):
        with cols[i]:
            st.markdown(f'<div class="gift-card"><b>{prod}</b><br><span class="point-badge">{prix} Pts</span></div>', unsafe_allow_html=True)
            if st.button(f"Prendre {prod}", key=prod):
                if st.session_state.user_connected:
                    if modifier_points(st.session_state.user_connected['Email'], prix, "deduction"):
                        st.balloons()
                        st.success(f"Cadeau récupéré !")
                        st.rerun()
                    else:
                        st.error("Pas assez de points !")
                else:
                    st.error("Connectez-vous !")

# ---------------- PAGE CAISSE (ADMIN) ---------------- #
elif menu == "📟 CAISSE (Admin)":
    st.title("📟 Interface Gérant")
    st.write("Ajouter des points aux clients lors de leur passage en caisse.")
    
    with st.form("ajout_points"):
        c_email = st.selectbox("Sélectionner le client", st.session_state.clients['Email'].unique())
        c_points = st.number_input("Nombre de points à ajouter", min_value=1, value=5)
        if st.form_submit_button("Ajouter les points"):
            modifier_points(c_email, c_points, "ajout")
            st.success(f"{c_points} points ajoutés à {c_email}")
            st.rerun()
