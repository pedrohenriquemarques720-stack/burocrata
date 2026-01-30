import streamlit as st
import pdfplumber
import re
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DE DESIGN (ESTILO DEVTOOLS)
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .devtools-panel {
        background-color: #ffffff;
        border-left: 2px solid #e2e8f0;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE AUDITORIA (BLINDADA)
# --------------------------------------------------

def realizar_auditoria(texto):
    problemas = []
    # Não convertemos o texto aqui para não perder a formatação original na exibição
    
    regras = [
        {"id": "guarantee", "regex": r"fiador.*(caução|depósito|seguro|título)|(caução|depósito|seguro|título).*fiador", "nome": "Garantia Dupla", "gravidade": "RED", "emoji": "🚫", "exp": "A lei proíbe exigir mais de uma garantia no mesmo contrato.", "lei": "Art. 37, Lei 8.245/91"},
        {"id": "fees", "regex": r"taxa.*(elaboração|confecção|contrato|cadastro|adm|reserva)", "nome": "Taxas de Intermediação", "gravidade": "RED", "emoji": "💸", "exp": "Custos de elaboração de contrato e taxas administrativas cabem ao locador.", "lei": "Art. 22, VII, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*(3|três).*alugue", "check_not": "proporcional", "nome": "Multa Rescisória", "gravidade": "RED", "emoji": "⚠️", "exp": "A multa deve ser obrigatoriamente proporcional ao tempo restante.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*trimestral|mensal", "nome": "Reajuste em Prazo Ilegal", "gravidade": "RED", "emoji": "📉", "exp": "O reajuste de aluguel só pode ocorrer a cada 12 meses.", "lei": "Lei 10.192/01"},
        {"id": "visit", "regex": r"(qualquer|a qualquer|sem aviso|independente de).*visita|vistoria|ingressar", "nome": "Invasão de Privacidade", "gravidade": "RED", "emoji": "🏠", "exp": "O locador não pode entrar sem dia e hora previamente combinados.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "structure", "regex": r"responsabilidade.*(telhado|estrutural|vício oculto|tubulação)", "nome": "Manutenção Estrutural Invertida", "gravidade": "RED", "emoji": "🛠️", "exp": "Problemas na estrutura do imóvel são obrigação do proprietário.", "lei": "Art. 22, I e IV, Lei 8.245/91"}
    ]
    
    for r in regras:
        # Usamos re.IGNORECASE e re.DOTALL para garantir que ele ache mesmo com quebras de linha ou maiúsculas
        if re.search(r["regex"], texto, re.IGNORECASE | re.DOTALL):
            # Se a regra exige que NÃO tenha uma palavra (ex: proporcional)
            if "check_not" in r and r["check_not"].lower() in texto.lower():
                continue
            problemas.append(r)
    return problemas

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso</h1>", unsafe_allow_html=True)
st.write("---")

col_main, col_devtools = st.columns([1.5, 1])

with col_main:
    st.subheader("📂 Upload do Documento")
    uploaded_file = st.file_uploader("Arraste o contrato para inspeção", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Analisando todas as cláusulas..."):
            with pdfplumber.open(uploaded_file) as pdf:
                full_text = "".join([p.extract_text() or "" for p in pdf.pages])
            
            # Executa a auditoria
            problemas = realizar_auditoria(full_text)
            
            st.success(f"Análise Completa. Detectamos {len(problemas)} pontos críticos.")
            
            score = max(100 - (len(problemas) * 20), 0)
            st.metric("Health Check Jurídico", f"{score}/100")
            st.progress(score / 100)
            
            with st.expander("📝 Ver Contraproposta para WhatsApp"):
                msg = "Olá, analisei o contrato e gostaria de ajustar os seguintes pontos:\n\n"
                for p in problemas:
                    msg += f"• {p['nome']} (Ref: {p['lei']})\n"
                st.code(msg, language="text")

# --------------------------------------------------
# PAINEL DE INSPEÇÃO (ESTILO DEVTOOLS / CONSOLE)
# --------------------------------------------------
with col_devtools:
    st.markdown("### 🖥️ Console de Auditoria")
    st.write("---")
    
    if uploaded_file:
        # Aqui ele lista todos os problemas encontrados com o visual de chat/alerta
        if problemas:
            for p in problemas:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(f"**ALERTA: {p['nome']}** {p['emoji']}")
                    st.write(p['exp'])
                    st.caption(f"📍 Base Legal: {p['lei']}")
                    st.divider()
            
            if prompt := st.chat_input("Dúvida sobre o log acima?"):
                st.info(f"O Burocrata está processando sua dúvida sobre: {prompt}")
        else:
            st.success("Console: 0 erros encontrados. O contrato está aderente às regras de teste.")
    else:
        st.markdown("<p style='color: #94a3b8;'>Aguardando entrada de dados para depuração...</p>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #94a3b8;'>Burocrata de Bolso | Auditoria de Precisão</p>", unsafe_allow_html=True)
