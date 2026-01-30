import streamlit as st
import pdfplumber
import re
from datetime import datetime
import time

# --------------------------------------------------
# CONFIGURAÇÃO DE DESIGN
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -1px; }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE ANÁLISE (PADRÃO ORIGINAL RECUPERADO)
# --------------------------------------------------

def buscar_padroes(texto):
    problemas = []
    # Busca bruta para máxima sensibilidade
    regras = [
        {"id": "guarantee", "regex": r"fiador.*(caução|depósito|seguro|título)|(caução|depósito|seguro|título).*fiador", "nome": "Garantia Dupla", "gravidade": "RED", "emoji": "🚫", "exp": "A lei proíbe exigir mais de uma garantia. Isso anula a cláusula.", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "regex": r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", "nome": "Taxas de Intermediação", "gravidade": "RED", "emoji": "💸", "exp": "Taxas de contrato são custos do proprietário.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*(3|três).*alugue", "check_not": "proporcional", "nome": "Multa Rescisória", "gravidade": "RED", "emoji": "⚠️", "exp": "A multa deve ser proporcional ao tempo restante.", "lei": "Art. 4º da Lei 8.245/91"},
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*trimestral|mensal", "nome": "Reajuste Ilegal", "gravidade": "RED", "emoji": "📉", "exp": "O reajuste só pode ser anual.", "lei": "Lei 10.192/01"},
        {"id": "visit", "regex": r"(qualquer|a qualquer|sem aviso|independente de).*visita|vistoria|ingressar", "nome": "Invasão de Privacidade", "gravidade": "RED", "emoji": "🏠", "exp": "Exige aviso prévio combinado.", "lei": "Art. 23, IX, Lei 8.245/91"}
    ]

    for r in regras:
        # Busca ignorando maiúsculas/minúsculas e aceitando quebras de linha
        if re.search(r["regex"], texto, re.IGNORECASE | re.DOTALL):
            if "check_not" in r and r["check_not"].lower() in texto.lower():
                continue
            problemas.append(r)
    return problemas

# --------------------------------------------------
# INTERFACE PRINCIPAL (CONTEÚDO)
# --------------------------------------------------

st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso</h1>", unsafe_allow_html=True)
st.markdown("#### Analisador de Contratos Imobiliários")
st.write("---")

uploaded_file = st.file_uploader("📂 Arraste seu contrato em PDF aqui", type=["pdf"])

if uploaded_file:
    with st.spinner("Analisando segurança jurídica..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = "".join([p.extract_text() or "" for p in pdf.pages])
        
        problemas = buscar_padroes(full_text)
        
        # Dashboard de Resultado no Corpo da Página
        st.subheader("Resultado da Análise")
        col1, col2 = st.columns(2)
        
        with col1:
            score = max(100 - (len(problemas) * 20), 0)
            st.metric("Score de Proteção", f"{score}/100")
            st.progress(score / 100)
        
        with col2:
            st.write(f"🔍 **Status:** {len(problemas)} irregularidade(s) encontrada(s).")
            if problemas:
                st.warning("Verifique o Console do Burocrata na barra lateral para detalhes.")

        # --------------------------------------------------
        # CHAT EXTERNO (SIDEBAR / CONSOLE)
        # --------------------------------------------------
        with st.sidebar:
            st.markdown("### 🤖 Console do Burocrata")
            st.write("---")
            
            if problemas:
                for p in problemas:
                    with st.chat_message("assistant", avatar="⚖️"):
                        st.markdown(f"**{p['emoji']} {p['nome']}**")
                        st.write(p['exp'])
                        st.caption(f"Base Legal: {p['lei']}")
                    st.write("") # Espaçador
                
                # Input de chat apenas no final do console lateral
                if prompt := st.chat_input("Dúvida sobre o log?"):
                    st.session_state.last_query = prompt
                    st.sidebar.info(f"Processando dúvida sobre: {prompt}")
            else:
                st.success("Nenhum erro detectado no console.")
                
        # Listagem resumida no corpo (Interface Antiga)
        if problemas:
            st.write("---")
            for p in problemas:
                with st.expander(f"Ver Cláusula: {p['nome']}"):
                    st.write(f"**Por que é indevido?** {p['exp']}")
                    st.markdown(f"`Regra: {p['lei']}`")
    
else:
    st.info("Aguardando upload para iniciar auditoria.")

st.markdown("<br><p style='text-align: center; color: #94a3b8;'>Burocrata de Bolso © 2026</p>", unsafe_allow_html=True)
