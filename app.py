import streamlit as st
import pdfplumber
import re
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DE DESIGN PREMIUM
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

# CSS Customizado para transformar o visual do Streamlit
st.markdown("""
    <style>
    /* Fundo e Fonte */
    .main { background-color: #f8f9fa; }
    
    /* Customização dos Cards de Problemas */
    .status-card {
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #1e3a8a;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Estilo do Título Principal */
    .main-title {
        color: #1e3a8a;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Botões Customizados */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #1e3a8a;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        border: none;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE ANÁLISE (O Cérebro Atualizado)
# --------------------------------------------------

def buscar_padroes(texto):
    problemas = []
    texto = texto.lower()

    # Base de Regras Expandida para detectar as armadilhas de teste
    regras = [
        {"id": "guarantee", "regex": r"fiador.*(caução|depósito|seguro|título)|(caução|depósito|seguro|título).*fiador", "nome": "Garantia Dupla", "gravidade": "RED", "emoji": "🚫", "exp": "A lei proíbe exigir mais de uma garantia. Isso anula a cláusula.", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "regex": r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", "nome": "Taxas de Intermediação", "gravidade": "RED", "emoji": "💸", "exp": "Taxas de contrato são custos do proprietário, não do inquilino.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*(3|três).*alugue", "check_not": "proporcional", "nome": "Multa Rescisória Sem Proporcionalidade", "gravidade": "RED", "emoji": "⚠️", "exp": "A multa deve ser sempre proporcional ao tempo restante do contrato.", "lei": "Art. 4º da Lei 8.245/91"},
        {"id": "reserve", "regex": r"fundo.*reserva|despesas.*extraordinária", "nome": "Fundo de Reserva", "gravidade": "YELLOW", "emoji": "🏢", "exp": "Despesas extraordinárias de condomínio cabem ao locador.", "lei": "Art. 22, Parágrafo Único, Lei 8.245/91"},
        
        # NOVAS REGRAS ADICIONADAS:
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*trimestral|mensal", "nome": "Reajuste em Prazo Ilegal", "gravidade": "RED", "emoji": "📉", "exp": "O reajuste de aluguel só pode ocorrer a cada 12 meses. Prazos menores são nulos.", "lei": "Lei 10.192/01 e Lei 8.245/91"},
        {"id": "visit", "regex": r"(qualquer|a qualquer|sem aviso|independente de).*visita|vistoria|ingressar", "nome": "Invasão de Privacidade", "gravidade": "RED", "emoji": "🏠", "exp": "O locador não pode entrar no imóvel sem dia e hora previamente combinados.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "structure", "regex": r"responsabilidade.*(telhado|estrutural|vício oculto|tubulação)", "nome": "Manutenção Estrutural Invertida", "gravidade": "RED", "emoji": "🛠️", "exp": "Problemas na estrutura ou telhado são obrigação do dono (Locador).", "lei": "Art. 22, I e IV, Lei 8.245/91"},
        {"id": "full_fine", "regex": r"multa.*total.*restante|sem.*proporcionalidade", "nome": "Multa Rescisória Abusiva", "gravidade": "RED", "emoji": "⚖️", "exp": "Cobrar o valor integral dos meses restantes sem proporcionalidade é ilegal.", "lei": "Art. 4º, Lei 8.245/91"}
    ]

    for r in regras:
        found = re.search(r["regex"], texto, re.DOTALL)
        if found:
            if "check_not" in r and r["check_not"] in texto: 
                continue
            problemas.append(r)
    return problemas

# --------------------------------------------------
# INTERFACE
# --------------------------------------------------

with st.container():
    st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso</h1>", unsafe_allow_html=True)
    st.markdown("#### O seu aliado contra cláusulas abusivas e letras miúdas.")
    st.write("---")

col_l, col_r = st.columns([2, 1])

with col_l:
    uploaded_file = st.file_uploader("📂 Arraste seu contrato em PDF aqui", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Analisando segurança jurídica..."):
            with pdfplumber.open(uploaded_file) as pdf:
                full_text = "".join([p.extract_text() or "" for p in pdf.pages]).lower()
            
            problemas = buscar_padroes(full_text)
            
            # Cálculo de Score ajustado (Penaliza mais erros graves)
            score = 100
            for p in problemas:
                if p['gravidade'] == 'RED': score -= 25
                elif p['gravidade'] == 'YELLOW': score -= 10
            score = max(score, 0)

            # Dashboard de Score
            st.markdown(f"<div style='background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            st.write(f"### Score de Proteção: **{score}/100**")
            st.progress(score / 100)
            st.markdown("</div><br>", unsafe_allow_html=True)

            if problemas:
                st.subheader(f"🔍 Detectamos {len(problemas)} pontos de atenção:")
                for p in problemas:
                    with st.expander(f"{p['emoji']} {p['nome']}"):
                        st.write(f"**O Diagnóstico:** {p['exp']}")
                        st.caption(f"📍 Base Legal: {p['lei']}")
                        
                        st.markdown("**Sugestão de mensagem:**")
                        txt = f"Olá, notei no contrato a cláusula de {p['nome']}. De acordo com o {p['lei']}, esse ponto precisa ser ajustado por ser considerado abusivo/ilegal. Podemos revisar?"
                        st.code(txt, language="text")
                
                if st.button("✨ Gerar E-mail de Contraproposta"):
                    data = datetime.now().strftime("%d/%m/%Y")
                    corpo = f"Prezados,\n\nApós análise técnica do contrato (Data: {data}), solicito a revisão dos seguintes pontos que divergem da legislação vigente (Lei 8.245/91):\n\n"
                    for p in problemas: 
                        corpo += f"- {p['nome']}: Baseado em {p['lei']}.\n"
                    corpo += "\nFico no aguardo da minuta corrigida para darmos prosseguimento à assinatura.\n\nAtenciosamente."
                    st.text_area("E-mail pronto para envio:", corpo, height=250)
            else:
                st.success("✅ Contrato limpo! Nenhuma das abusividades comuns foi detectada em nossa base de regras.")

with col_r:
    st.markdown("""
        <div style='background-color: #eef2ff; padding: 20px; border-radius: 15px;'>
            <h4 style='color: #1e3a8a;'>🛡️ Modo Guardião</h4>
            <p style='font-size: 0.9em;'>Mantenha-se protegido durante toda a vigência do contrato. Monitoramos prazos de reajuste e notificações.</p>
        </div>
    """, unsafe_allow_html=True)
    
    data_in = st.date_input("Início da Locação", datetime.now())
    if st.button("Ativar Monitoramento"):
        st.balloons()
        st.success(f"Guardião ativado para o contrato iniciado em {data_in.strftime('%d/%m/%Y')}!")

st.markdown("<br><p style='text-align: center; color: #94a3b8;'>Burocrata de Bolso © 2026 | Focado em Transparência Imobiliária</p>", unsafe_allow_html=True)
