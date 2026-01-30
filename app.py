import streamlit as st
import pdfplumber
import re
import unicodedata

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

# --------------------------------------------------
# LÓGICA DE AUDITORIA BLINDADA (DETECTA OS 4 ERROS)
# --------------------------------------------------

def normalizar_texto(t):
    # Remove acentos e caracteres especiais para facilitar a busca
    if t:
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        # Transforma quebras de linha em espaços e remove espaços duplos
        return " ".join(t.lower().split())
    return ""

def realizar_auditoria_total(arquivo_pdf):
    problemas_detectados = []
    
    # Regras com Regex ultra-flexíveis (.*?) para ignorar palavras intermediárias
    regras = [
        {"id": "readjust", "regex": r"reajuste.*?(trimestral|mensal|semestral|3|três|6|seis)", "nome": "Reajuste em Prazo Ilegal", "exp": "O reajuste de aluguel residencial deve ser obrigatoriamente ANUAL.", "lei": "Lei 10.192/01"},
        {"id": "improvements", "regex": r"(renuncia|nao indeniza|sem direito).*?(benfeitoria|reforma|obra)", "nome": "Renúncia de Benfeitorias", "exp": "Cláusula abusiva: o inquilino tem direito a indenização por reformas necessárias.", "lei": "Art. 35, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*?(12|doze|integral|total).*?(aluguel|meses)", "nome": "Multa Rescisória Abusiva", "exp": "A multa deve ser sempre proporcional ao tempo restante, nunca o valor total do contrato.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente de|qualquer hora|livre).*?(visita|vistoria|ingresso|entrar)", "nome": "Violação de Privacidade", "exp": "O dono não pode entrar no imóvel sem aviso prévio e concordância do inquilino.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "guarantee", "regex": r"fiador.*?(caucao|deposito|seguro)|(caucao|deposito|seguro).*?fiador", "nome": "Garantia Dupla", "exp": "É proibido exigir mais de uma garantia no mesmo contrato.", "lei": "Art. 37, Lei 8.245/91"}
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            # Normaliza o texto da página (remove acentos e limpa espaços)
            texto_limpo = normalizar_texto(texto_pag)
            
            for r in reglas:
                if re.search(r["regex"], texto_limpo, re.IGNORECASE):
                    # Evita duplicatas na mesma página
                    if not any(p['id'] == r['id'] and p['pagina'] == i+1 for p in problemas_detectados):
                        problemas_detectados.append({**r, "pagina": i + 1})
                        
    return problemas_detectados

# --------------------------------------------------
# INTERFACE
# --------------------------------------------------

st.title("⚖️ Burocrata de Bolso v4.5")
st.write("---")

col_esq, col_dir = st.columns([1.5, 1])

with col_esq:
    st.subheader("📄 Análise do Documento")
    arquivo = st.file_uploader("Suba o PDF do contrato para auditoria final", type=["pdf"])
    
    if arquivo:
        achados = realizar_auditoria_total(arquivo)
        
        score = max(100 - (len(achados) * 20), 0)
        st.metric("Score de Proteção", f"{score}/100")
        st.progress(score / 100)
        
        if achados:
            st.error(f"🔍 Detectamos {len(achados)} irregularidades críticas.")
            for a in achados:
                with st.expander(f"📍 Página {a['pagina']}: {a['nome']}"):
                    st.write(f"**Diagnóstico:** {a['exp']}")
                    st.caption(f"Base Legal: {a['lei']}")
        else:
            st.success("Nenhuma irregularidade detectada. O contrato parece estar limpo.")

# --------------------------------------------------
# CONSOLE DE AUDITORIA (LADO DIREITO)
# --------------------------------------------------
with col_dir:
    st.subheader("🖥️ Console de Auditoria")
    st.write("---")
    
    if arquivo:
        for a in achados:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"**[PÁGINA {a['pagina']}]**")
                st.markdown(f"**Erro:** `{a['nome']}`")
                st.info(f"Violação: {a['lei']}")
            st.write("") 
        
        if prompt := st.chat_input("Dúvidas sobre esses erros?"):
            with st.chat_message("user"): st.write(prompt)
            with st.chat_message("assistant"): st.write("Essa análise baseia-se na Lei do Inquilinato. Recomendo solicitar a alteração desses pontos antes da assinatura.")
    else:
        st.info("Aguardando PDF para depuração...")

st.markdown("---")
st.caption("Burocrata de Bolso - Modo Auditoria Total Ativado © 2026")
