import streamlit as st
import pdfplumber
import re
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stColumn > div { padding: 10px; }
    .main-title { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE AUDITORIA REFINADA
# --------------------------------------------------

def realizar_auditoria_total(arquivo_pdf):
    problemas_detectados = []
    
    # Regras ultra-sensíveis para detectar os 4 erros + extras
    regras = [
        {"id": "readjust", "regex": r"(reajuste|aumento|atualização).*?(trimestral|mensal|semestral|3 meses)", "nome": "Reajuste em Prazo Ilegal", "exp": "O reajuste só pode ser anual (12 meses).", "lei": "Lei 10.192/01"},
        {"id": "improvements", "regex": r"(renúncia|não indenizar|sem direito).*?(benfeitoria|reforma|obra)", "nome": "Cláusula de Benfeitorias Abusiva", "exp": "O inquilino tem direito a indenização por benfeitorias necessárias.", "lei": "Art. 35, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*?(12|doze|integral|total).*?(aluguel|meses)", "nome": "Multa Rescisória Abusiva", "exp": "A multa deve ser sempre proporcional ao tempo restante do contrato.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente de|qualquer hora).*?(visita|vistoria|ingresso|entrar)", "nome": "Violação de Privacidade", "exp": "O locador precisa de aviso prévio e horário combinado para entrar.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "guarantee", "regex": r"fiador.*?(caução|depósito|seguro)|(caução|depósito|seguro).*?fiador", "nome": "Garantia Dupla", "exp": "É proibido exigir mais de uma garantia no mesmo contrato.", "lei": "Art. 37, Lei 8.245/91"}
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            if not texto_pag: continue
            
            # Limpeza: remove múltiplas quebras de linha para o regex "dar match" em frases quebradas
            texto_limpo = " ".join(texto_pag.split())
            
            for r in regras:
                if re.search(r["regex"], texto_limpo, re.IGNORECASE | re.DOTALL):
                    # Evita duplicatas na mesma página
                    if not any(p['id'] == r['id'] and p['pagina'] == i+1 for p in problemas_detectados):
                        problemas_detectados.append({**r, "pagina": i + 1})
                        
    return problemas_detectados

# --------------------------------------------------
# INTERFACE
# --------------------------------------------------

st.markdown("<h1 class='main-title'>⚖️ Burocrata de Bolso v4.0</h1>", unsafe_allow_html=True)
st.write("---")

col_esq, col_dir = st.columns([1.5, 1])

with col_esq:
    st.subheader("📄 Análise do Documento")
    arquivo = st.file_uploader("Suba o PDF do contrato para auditoria total", type=["pdf"])
    
    if arquivo:
        achados = realizar_auditoria_total(arquivo)
        
        # Dashboard de Score
        score = max(100 - (len(achados) * 20), 0)
        st.metric("Score de Proteção", f"{score}/100")
        st.progress(score / 100)
        
        if achados:
            st.error(f"🔍 Detectamos {len(achados)} irregularidades críticas.")
            for a in achados:
                with st.expander(f"📍 Página {a['pagina']}: {a['nome']}"):
                    st.write(f"**Análise:** {a['exp']}")
                    st.caption(f"Base Legal: {a['lei']}")
        else:
            st.success("Nenhum erro detectado com base nas regras atuais.")

# --------------------------------------------------
# CONSOLE DE AUDITORIA (LADO DIREITO)
# --------------------------------------------------
with col_dir:
    st.subheader("🖥️ Console de Auditoria")
    
    if arquivo:
        for a in achados:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"**[PÁGINA {a['pagina']}]**")
                st.markdown(f"**Erro:** `{a['nome']}`")
                st.info(f"Violação detectada: {a['lei']}")
                st.divider()
        
        if prompt := st.chat_input("Dúvidas sobre esses pontos?"):
            with st.chat_message("user"): st.write(prompt)
            with st.chat_message("assistant"): st.write("Essa cláusula que você citou é comum, mas o STJ entende que a proteção ao locatário é prioritária nesses casos.")
    else:
        st.info("Aguardando PDF...")

st.markdown("---")
st.caption("Burocrata de Bolso - Modo Auditoria Total Ativado © 2026")
