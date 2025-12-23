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

# ---------------- IMAGES RÉALISTES ---------------- #
# (Tu pourras les remplacer par tes propres photos plus tard)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3724/3724720.png"
IMG_VIANDE_HACHE = "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?q=80&w=400"
IMG_MERGUEZ = "https://images.unsplash.com/photo-1532636875304-0c89119d9b1d?q=80&w=400"
IMG_BANANE = "https://images.unsplash.com/photo-1571771894821-ad990241274d?q=80&w=400"
IMG_POMMES = "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?q=80&w=400"

# ---------------- STYLE CSS (Noir sur Blanc) ---------------- #
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    p, span, label, h1, h2, h3 { color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #343a40; color: white; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
    
    .product-card {
        border: 1px solid #eee;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        background-color: #fff;
        margin-bottom: 20px;
    }
    .product-img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }
    .old-price { text-decoration: line-through; color: #cc0000; font-size: 0.9em; }
    .new-price { color: #28a745; font-weight: bold; font-size: 1.3em; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- NAVIGATION SIDEBAR ---------------- #
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.title("VM Magasin")
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Accès Client")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        
        col_login, col_sign = st.columns(2)
        with col_login:
            if st.button("Connexion"):
                user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
                if not user.empty:
                    st.session_state.user_connected = user.iloc[0].to_dict()
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        with col_sign:
            if st.button("S'inscrire"):
                st.session_state.show_signup = True
                st.rerun()
    else:
        st.success(f"Bonjour {st.session_state.user_connected['Prenom']}")
        st.write(f"💎 Points : {st.session_state.user_connected['Points']}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

    st.divider()
    menu = st.radio("Navigation", ["🔥 Offres par Rayon", "📋 Catalogue Complet", "👤 Mon Espace Fidélité"])

# ---------------- PAGE INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    st.markdown("---")
    st.subheader("📝 Créer votre compte client")
    with st.form("form_inscription"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nom")
        prenom = c2.text_input("Prénom")
        age = st.number_input("Âge", min_value=12)
        email = st.text_input("Adresse Email")
        mdp = st.text_input("Choisir un Mot de passe", type="password")
        
        if st.form_submit_button("Confirmer l'inscription"):
            if not email or not mdp:
                st.error("Veuillez remplir tous les champs.")
            else:
                new_user = pd.DataFrame([{
                    "Nom": nom, "Prenom": prenom, "Age": age, "Email": email, 
                    "Password": mdp, "Points": 0, "Statut": "Actif"
                }])
                st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
                sauvegarder_donnees(st.session_state.clients)
                st.success("✅ Compte créé ! Connectez-vous dans la barre latérale.")
                st.session_state.show_signup = False
    st.markdown("---")

# ---------------- CONTENU PRINCIPAL ---------------- #
if menu == "🔥 Offres par Rayon":
    st.title("Nos Promotions du moment")
    rayon = st.selectbox("Choisir un rayon :", ["🥩 Boucherie", "🍎 Fruits & Légumes"])
    
    if rayon == "🥩 Boucherie":
        st.subheader("Sélection Boucherie")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''<div class="product-card">
                <img src="{IMG_VIANDE_HACHE}" class="product-img">
                <p><b>Viande Hachée Pure Bœuf</b></p>
                <span class="old-price">9,99€</span> <span class="new-price">8,99€ / kg</span>
            </div>''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''<div class="product-card">
                <img src="{IMG_MERGUEZ}" class="product-img">
                <p><b>Merguez Véritable</b></p>
                <span class="old-price">13,99€</span> <span class="new-price">12,99€ / kg</span>
            </div>''', unsafe_allow_html=True)

    elif rayon == "🍎 Fruits & Légumes":
        st.subheader("Sélection Fraîcheur")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''<div class="product-card">
                <img src="{IMG_BANANE}" class="product-img">
                <p><b>Bananes Cavendish</b></p>
                <span class="old-price">2,00€</span> <span class="new-price">1,59€ / kg</span>
            </div>''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''<div class="product-card">
                <img src="{IMG_POMMES}" class="product-img">
                <p><b>Pommes Gala</b></p>
                <span class="old-price">3,20€</span> <span class="new-price">2,49€ / 2kg</span>
            </div>''', unsafe_allow_html=True)

elif menu == "📋 Catalogue Complet":
    st.title("Catalogue de tous les produits")
    # Simulation de stock global
    df_cat = pd.DataFrame([
        {"Rayon": "Boucherie", "Produit": "Viande Hachée", "Prix": "8.99€", "Stock": "En stock"},
        {"Rayon": "Boucherie", "Produit": "Merguez", "Prix": "12.99€", "Stock": "En stock"},
        {"Rayon": "Frais", "Produit": "Bananes", "Prix": "1.59€", "Stock": "En stock"},
        {"Rayon": "Frais", "Produit": "Lait", "Prix": "1.20€", "Stock": "En stock"},
        {"Rayon": "Épicerie", "Produit": "Huile", "Prix": "2.99€", "Stock": "Rupture"},
    ])
    st.table(df_cat)

elif menu == "👤 Mon Espace Fidélité":
    st.title("💎 Ma Fidélité VM")
    if st.session_state.user_connected:
        user_mail = st.session_state.user_connected['Email']
        user_data = st.session_state.clients[st.session_state.clients["Email"] == user_mail].iloc[0]
        
        st.header(f"Bienvenue, {user_data['Prenom']} !")
        st.metric("Solde de points", f"{user_data['Points']} pts")
        st.progress(min(int(user_data['Points'])/100, 1.0))
        st.write("Plus que quelques points pour votre prochain cadeau !")
    else:
        st.warning("Veuillez vous connecter pour accéder à vos points.")
