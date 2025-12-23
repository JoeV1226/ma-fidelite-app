import streamlit as st
import pandas as pd
import datetime
import os

# ---------------- CONFIGURATION & BDD ---------------- #
DB_FILE = "clients_db.csv"
# Remplace ces liens par tes propres images si besoin
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3724/3724720.png"
IMG_VIANDE = "https://images.unsplash.com/photo-1607623814075-e512199b028f?q=80&w=400&auto=format&fit=crop"
IMG_FRUITS = "https://images.unsplash.com/photo-1610832958506-aa56368176cf?q=80&w=400&auto=format&fit=crop"

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

# ---------------- STYLE VM MAGASIN (Noir sur Blanc) ---------------- #
st.markdown("""
    <style>
    /* Fond blanc et écriture noire partout */
    .stApp { background-color: #ffffff; color: #000000; }
    
    /* Forcer le texte noir pour les labels et paragraphes */
    p, span, label, .stMarkdown { color: #000000 !important; }
    
    /* Sidebar reste foncée pour le contraste */
    [data-testid="stSidebar"] { background-color: #343a40; color: white; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
    
    /* Cartes des offres avec de vraies images */
    .offer-card {
        background-color: #ffffff;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        overflow: hidden;
        text-align: center;
        padding-bottom: 15px;
    }
    .offer-img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    .new-price { color: #28a745; font-weight: bold; font-size: 1.4em; }
    .old-price { text-decoration: line-through; color: #dc3545; font-size: 1em; }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #000000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown("<h2 style='color:white;'>VM Magasin</h2>", unsafe_allow_html=True)
    
    if st.session_state.user_connected is None:
        st.subheader("🔑 Connexion")
        email_log = st.text_input("Email")
        pass_log = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            user = st.session_state.clients[(st.session_state.clients["Email"] == email_log) & (st.session_state.clients["Password"] == pass_log)]
            if not user.empty:
                st.session_state.user_connected = user.iloc[0].to_dict()
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        
        st.write("---")
        if st.button("🆕 Créer un compte"):
            st.session_state.show_signup = True
            st.rerun()
    else:
        st.success(f"Connecté : {st.session_state.user_connected['Prenom']}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# ---------------- FORMULAIRE D'INSCRIPTION ---------------- #
if st.session_state.show_signup and st.session_state.user_connected is None:
    with st.expander("📝 INSCRIPTION - REMPLISSEZ VOS INFORMATIONS", expanded=True):
        with st.form("inscription"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prénom")
            age = st.number_input("Âge", min_value=12)
            email = st.text_input("Email")
            mdp = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Créer mon compte"):
                if email and mdp:
                    new_user = pd.DataFrame([{"Nom": nom, "Prenom": prenom, "Age": age, "Email": email, "Password": mdp, "Points": 0, "Statut": "Actif"}])
                    st.session_state.clients = pd.concat([st.session_state.clients, new_user], ignore_index=True)
                    sauvegarder_donnees(st.session_state.clients)
                    st.success("Compte créé ! Connectez-vous à gauche.")
                    st.session_state.show_signup = False
                else:
                    st.error("Champs requis manquants.")

# ---------------- CONTENU PRINCIPAL ---------------- #
st.title("🛒 Bienvenue chez VM Magasin")

tabs = st.tabs(["⭐ Nos Offres", "📋 Catalogue", "💎 Ma Fidélité"])

with tabs[0]:
    st.subheader("Promotions de la semaine")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
            <div class="offer-card">
                <img src="{IMG_VIANDE}" class="offer-img">
                <div style="padding:10px;">
                    <b style="color:black;">🥩 BOUCHERIE</b><br>
                    <span style="color:black;">1kg Escalope de dinde</span><br>
                    <span class="old-price">9,59€</span> <span class="new-price">8,59€</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''
            <div class="offer-card">
                <img src="{IMG_FRUITS}" class="offer-img">
                <div style="padding:10px;">
                    <b style="color:black;">🍎 RAYON FRAIS</b><br>
                    <span style="color:black;">Filet de pommes (2kg)</span><br>
                    <span class="old-price">3,50€</span> <span class="new-price">2,49€</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Stock et Catalogue")
    df_prod = pd.DataFrame({
        "Produit": ["Lait", "Pain", "Pommes", "Escalope"],
        "Prix": ["1.20€", "0.90€", "2.49€", "8.59€"],
        "Disponibilité": ["En stock", "En stock", "En stock", "Dernières pièces"]
    })
    st.table(df_prod)

with tabs[2]:
    st.subheader("Espace Fidélité")
    if st.session_state.user_connected:
        st.write(f"Titulaire : **{st.session_state.user_connected['Prenom']} {st.session_state.user_connected['Nom']}**")
        pts = st.session_state.user_connected['Points']
        st.metric("Points cumulés", f"{pts} pts")
        st.progress(min(int(pts)/100, 1.0))
    else:
        st.info("Connectez-vous pour voir vos points.")
