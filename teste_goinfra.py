import streamlit as st
import hashlib
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Gestão Goinfra", layout="wide")

# ============================
# HASH DA SENHA
# ============================

HASH_CORRETO = "a584ba0fee587477162495574c8ad4e32c98c18787601826b3c6794c8f11fc68"

def hash_senha(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

def validar_senha(senha_digitada):
    return hash_senha(senha_digitada) == HASH_CORRETO

# ============================
# LOGIN
# ============================

if "logado" not in st.session_state:
    st.session_state.logado = False

# Se NÃO estiver logado, mostra o formulário e PARA o script aqui
if not st.session_state.logado:
    st.markdown("## 🔒 Monitoramento GOINFRA")
    
    # Use um formulário para evitar que a página recarregue a cada letra digitada
    with st.form("login_form"):
        senha = st.text_input("Digite a senha", type="password")
        botao_entrar = st.form_submit_button("Entrar")

        if botao_entrar:
            if validar_senha(senha):
                st.session_state.logado = True
                st.success("Acesso liberado!")
                st.rerun() # Recarrega para esconder o login e mostrar o app
            else:
                st.error("Senha incorreta")
    
    # ESTE STOP É ESSENCIAL: Ele impede que o resto do código (planilhas, mapas) 
    # carregue antes da senha ser validada.
    st.stop() 

# Se chegou aqui, é porque st.session_state.logado == True
# Todo o resto do seu código (Estilo, Carregar Planilha, etc.) vem abaixo...
# ===============================
# ESTILO VISUAL
# ===============================

st.markdown("""
<style>

.tabela-container{
overflow-x:auto;
}

.tabela-html{
width:100%;
border-collapse:collapse;
font-family:'Segoe UI';
font-size:11px;
}

.tabela-html th{
background-color:#004a99;
color:white;
padding:4px;
text-align:center;
}

.tabela-html td{
border:1px solid #ddd;
padding:3px;
text-align:center;
}

.concluido{
background:#d4edda;
color:#155724;
font-weight:bold;
}

.pendente{
background:#f8d7da;
color:#721c24;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# CARREGAR PLANILHA
# ===============================

@st.cache_data
def load_data():

    path = r"C:\Users\tsulidario\Documents\VISUAL_SISTEMA\cronograma_goinfra_visual.xlsx"

    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    # limpeza das coordenadas
    for col in ['LATITUDE','LONGITUDE']:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace("°","")
            .str.replace(",",".")
            .str.strip()
        )

        df[col] = pd.to_numeric(df[col], errors="coerce")

    # converter KM da rodovia para número
    if 'kmSre' in df.columns:

        df['kmSre'] = (
            df['kmSre']
            .astype(str)
            .str.replace(",",".")
            .str.strip()
        )

        df['kmSre'] = pd.to_numeric(df['kmSre'], errors="coerce")

    return df

df = load_data()

# ===============================
# DEFINIR REGIÃO
# ===============================

def definir_regiao(row):

    lat = row['LATITUDE']
    lon = row['LONGITUDE']

    if pd.isna(lat) or pd.isna(lon):
        return "SEM COORD"

    # NORTE
    if lat > -14.5:
        return "NORTE"

    # SUL
    if lat < -17.5:
        return "SUL"

    # NORDESTE
    if lat <= -14.5 and lat > -16 and lon > -49.6:
        return "NORDESTE"

    # OESTE
    if lon < -51:
        return "OESTE"

    # CENTRO
    return "CENTRO"


df['REGIAO'] = df.apply(definir_regiao, axis=1)

# ===============================
# SIDEBAR
# ===============================

st.sidebar.title("🏢 Painel Goinfra")

coluna_ni = 'NI' if 'NI' in df.columns else 'nis'

lista_ni = sorted(df[coluna_ni].dropna().astype(str).unique())

sel_ni = st.sidebar.selectbox(
"Filtrar por Lote (NI)",
["Todas"] + list(lista_ni)
)

menu = st.sidebar.radio(
"Navegação",
["📋 Cronograma Completo","🗺️ Rotas e Planejamento"]
)

df_f = df.copy()

if sel_ni != "Todas":
    df_f = df[df[coluna_ni].astype(str) == sel_ni]

# ===============================
# TELA CRONOGRAMA
# ===============================

if menu == "📋 Cronograma Completo":

    st.title(f"✅ Checklist Geral - {sel_ni}")

    equipes = sorted(list(
        set(df_f['Equipe_civil'].dropna()) |
        set(df_f['Equipe_eletronica'].dropna())
    ))

    sel_equipe = st.selectbox(
        "Filtrar por Equipe",
        ["Todas"] + equipes
    )

    if sel_equipe != "Todas":

        df_f = df_f[
            (df_f['Equipe_civil'] == sel_equipe) |
            (df_f['Equipe_eletronica'] == sel_equipe)
        ]

    etapas_check = {

        'Furação':'FURACAO_REALIZADO',
        'Fixação':'FIXACAO_POSTES_REALIZADO',
        'Estrut.':'ESTRUTURAS_REALIZADO',
        'Travessia':'TRAVESSIA_INTERLIGACAO_REALIZADO',
        'Sinal Base':'SINALIZACAO_AEREA_BASE_REALIZADO',
        'Sinal Içam':'SINALIZACAO_AEREA_ICAMENTO_REALIZADO',
        'Sinal Fix':'SINALIZACAO_TERRESTRE_FIZACAO_REALIZADO',
        'Sinal Conc':'SINALIZACAO_TERRESTRE_CONCRETAGEM_REALIZADO',
        'Montagem':'MONTAGEM_REALIZADO',
        'Mont Estr':'MONTAGEM_ESTRUTURAL_REALIZADO',
        'Aferição':'AFERICAO_REALIZADO'
    }

    html = "<div class='tabela-container'><table class='tabela-html'>"
    html += "<thead><tr>"

    html += f"<th>{coluna_ni}</th>"
    html += "<th>ID</th>"
    html += "<th>Município</th>"
    html += "<th>ONLINE</th>"
    html += "<th>Placas Aéreas</th>"

    for label in etapas_check.keys():
        html += f"<th>{label}</th>"

    html += "</tr></thead><tbody>"

    for _, row in df_f.iterrows():

        html += "<tr>"

        html += f"<td>{row.get(coluna_ni,'-')}</td>"
        html += f"<td>{row.get('ID_Equip','-')}</td>"
        html += f"<td>{row.get('municipio','-')}</td>"

        html += f"<td>{row.get('ONLINE','-')}</td>"
        html += f"<td>{row.get('PLACAS_AEREAS','-')}</td>"

        for col in etapas_check.values():

            if pd.notna(row.get(col)):
                html += "<td class='concluido'>✅</td>"
            else:
                html += "<td class='pendente'>❌</td>"

        html += "</tr>"

    html += "</tbody></table></div>"

    st.markdown(html, unsafe_allow_html=True)

# ===============================
# TELA MAPA E ROTAS
# ===============================

else:

    st.title(f"🗺️ Planejamento de Rotas - {sel_ni}")

    regioes = ["Todas"] + sorted(df_f['REGIAO'].dropna().unique())

    sel_regiao = st.selectbox(
        "Filtrar Região",
        regioes
    )

    if sel_regiao != "Todas":
        df_f = df_f[df_f['REGIAO'] == sel_regiao]

    col1,col2 = st.columns([1,2])

# -------------------------------
# TABELA ROTAS
# -------------------------------

    with col1:

        st.subheader("📍 Cidades na Rodovia")

        col_rodovia = 'RODOVIA' if 'RODOVIA' in df.columns else 'rodovia'

        rota = df_f.groupby(
            [col_rodovia,'municipio']
        ).size().reset_index(name='Qtd Equip.')

        st.dataframe(rota)

        st.subheader("📊 Equipamentos por Região")

        resumo = df_f.groupby(
            'REGIAO'
        )['ID_Equip'].count().reset_index()

        st.dataframe(resumo)

# -------------------------------
# MAPA
# -------------------------------

    with col2:

        df_mapa = df_f.dropna(subset=['LATITUDE','LONGITUDE'])

        # evitar duplicar pontos por equipamento
        df_mapa = (
            df_mapa
            .sort_values(by="kmSre")
            .groupby("municipio")
            .first()
            .reset_index()
        )

        if not df_mapa.empty:

            m = folium.Map(
                location=[
                    df_mapa['LATITUDE'].mean(),
                    df_mapa['LONGITUDE'].mean()
                ],
                zoom_start=7
            )

            for _, r in df_mapa.iterrows():

                # cor baseada no ONLINE
                cor = "green" if str(r.get('ONLINE')).upper() == "ONLINE" else "red"

                folium.Marker(

                    location=[
                        r['LATITUDE'],
                        r['LONGITUDE']
                    ],

                    popup=f"""
                    Município: {r['municipio']} <br>
                    Equipamento: {r['ID_Equip']} <br>
                    KM: {r.get('kmSre','-')}
                    """,

                    tooltip=r['municipio'],

                    icon=folium.Icon(
                        color=cor,
                        icon="truck",
                        prefix="fa"
                    )

                ).add_to(m)

            # -------------------------------
            # ROTA ENTRE CIDADES
            # -------------------------------

            coords = df_mapa[['LATITUDE','LONGITUDE']].values.tolist()

            if len(coords) > 1:

                folium.PolyLine(
                    coords,
                    color="blue",
                    weight=4
                ).add_to(m)

            st_folium(m, width=900, height=600)

        else:

            st.warning(
                "⚠️ Coordenadas não encontradas. Verifique o Excel."
            )

