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

# ---------------- IMAGES (Exemples) ---------------- #
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3724/3724720.png"
IMG_DEFAULT = "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=400" # Image par défaut pour les nouveaux rayons

# ---------------- STYLE CSS ---------------- #
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
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

    st.divider()
    menu = st.radio("Navigation", ["🔥 Offres par Rayon", "👤 Mon Espace Fidélité"])

# ---------------- PAGE INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    st.subheader("📝 Créer votre compte client")
    with st.form("form_inscription"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nom")
        prenom = c2.text_input("Prénom")
        email = st.text_input("Adresse Email")
        mdp = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Confirmer l'inscription"):
            new_user = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"}])
            st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
            sauvegarder_donnees(st.session_state.clients)
            st.success("✅ Compte créé ! Connectez-vous à gauche.")
            st.session_state.show_signup = False

# ---------------- CONTENU PRINCIPAL ---------------- #
if menu == "🔥 Offres par Rayon":
    st.title("Découvrez nos rayons")
    
    # LISTE DE TOUS TES NOUVEAUX RAYONS
    liste_rayons = [
        "🥩 Boucherie", "🍎 Fruits & Légumes", "🍾 Boisson", "🧂 Condiment", 
        "🍪 Gateaux/Chips", "☕ Thé/Café", "🍝 Pate", "🌾 Feculent/Cereal", 
        "🥫 Conserve/Bocaux", "🌱 Legumineuse", "🥜 Fruit sec", "📦 Rayon sec", 
        "🥖 Boulangerie", "🧼 Hygiene/Beauté", "🏠 Entretien maison", 
        "🍳 Espace cuisine", "👕 Pret à porter", "🥦 Produit frais", "🌻 Huile"
    ]
    
    rayon_choisi = st.selectbox("Sélectionnez un rayon pour voir les offres :", liste_rayons)
    
    st.divider()
    st.header(f"Rayon {rayon_choisi}")
    
    col1, col2 = st.columns(2)

    # Exemple dynamique pour les offres selon le rayon
    if rayon_choisi == "🥩 Boucherie":
        with col1:
            st.markdown(f'<div class="product-card"><img src="{IMG_DEFAULT}" class="product-img"><p><b>Viande Hachée</b></p><span class="old-price">9,99€</span> <span class="new-price">8,99€ / kg</span></div>', unsafe_allow_html=True)
    
    elif rayon_choisi == "🍾 Boisson":
        with col1:
            st.markdown(f'<div class="product-card"><img src="{IMG_DEFAULT}" class="product-img"><p><b>Jus d\'Orange Frais</b></p><span class="old-price">2,50€</span> <span class="new-price">1,99€</span></div>', unsafe_allow_html=True)

    elif rayon_choisi == "🌻 Huile":
        with col1:
            st.markdown(f'<div class="product-card"><img src="{IMG_DEFAULT}" class="product-img"><p><b>Huile d\'Olive Vierge</b></p><span class="old-price">7,50€</span> <span class="new-price">5,99€</span></div>', unsafe_allow_html=True)
            
    else:
        # Message par défaut pour les autres rayons
        st.info(f"Les offres pour le rayon {rayon_choisi} arrivent bientôt ! Restez connectés.")

elif menu == "👤 Mon Espace Fidélité":
    st.title("💎 Ma Fidélité VM")
    if st.session_state.user_connected:
        st.metric("Mon solde de points", f"{st.session_state.user_connected['Points']} pts")
    else:
        st.warning("Veuillez vous connecter pour voir vos points.")
