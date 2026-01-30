import streamlit as st
import pdfplumber
import re
import unicodedata

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

# --------------------------------------------------
# LÓGICA DE AUDITORIA REFINADA (FIX: NameError corregido)
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        # Remove acentos e simplifica o texto para busca
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        return " ".join(t.lower().split())
    return ""

def realizar_auditoria_total(arquivo_pdf):
    problemas_detectados = []
    
    # Lista de regras (Variável: regras)
    regras = [
        {"id": "readjust", "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis)", "nome": "Reajuste Ilegal", "exp": "O reajuste de aluguel deve ser ANUAL (12 meses).", "lei": "Lei 10.192/01"},
        {"id": "improvements", "regex": r"(renuncia|nao indeniza|sem direito).*?(benfeitoria|reforma|obra)", "nome": "Cláusula de Benfeitorias", "exp": "O inquilino tem direito a indenização por reformas necessárias.", "lei": "Art. 35, Lei 8.245/91"},
        {"id": "proportion", "regex": r"multa.*?(12|doze|integral|total).*?(aluguel|meses)", "nome": "Multa s/ Proporcionalidade", "exp": "A multa deve ser proporcional ao tempo que resta de contrato.", "lei": "Art. 4º, Lei 8.245/91"},
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente|livre).*?(visita|vistoria|ingresso|entrar)", "nome": "Violação de Privacidade", "exp": "O locador não pode entrar no imóvel sem aviso e hora combinada.", "lei": "Art. 23, IX, Lei 8.245/91"},
        {"id": "guarantee", "regex": r"fiador.*?(caucao|deposito|seguro)|(caucao|deposito|seguro).*?fiador", "nome": "Garantia Dupla", "exp": "É proibido exigir mais de uma garantia no mesmo contrato.", "lei": "Art. 37, Lei 8.245/91"}
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text()
            texto_limpo = normalizar_texto(texto_pag)
            
            # Aqui estava o erro: usei 'reglas' em vez de 'regras'
            for r in regras:
                if re.search(r["regex"], texto_limpo, re.IGNORECASE):
                    if not any(p['id'] == r['id'] and p['pagina'] == i+1 for p in problemas_detectados):
                        problemas_detectados.append({**r, "pagina": i + 1})
                        
    return problemas_detectados

# --------------------------------------------------
# INTERFACE EM COLUNAS
# --------------------------------------------------

st.markdown("<h1 style='color: #1e3a8a;'>⚖️ Burocrata de Bolso v5.0</h1>", unsafe_allow_html=True)
st.write("---")

col_esq, col_dir = st.columns([1.5, 1])

with col_esq:
    st.subheader("📄 Análise Técnica")
    arquivo = st.file_uploader("Suba o contrato em PDF", type=["pdf"])
    
    if arquivo:
        # Chama a função corrigida
        achados = realizar_auditoria_total(arquivo)
        
        score = max(100 - (len(achados) * 20), 0)
        st.metric("Score de Segurança", f"{score}/100")
        st.progress(score / 100)
        
        if achados:
            st.error(f"🔍 Auditoria concluiu: {len(achados)} pontos críticos encontrados.")
            for a in achados:
                with st.expander(f"📍 Página {a['pagina']}: {a['nome']}"):
                    st.write(f"**Análise:** {a['exp']}")
                    st.caption(f"Base Legal: {a['lei']}")
        else:
            st.success("Nenhuma irregularidade detectada nos padrões de auditoria.")

with col_dir:
    st.subheader("🖥️ Console (DevTools)")
    st.write("---")
    
    if arquivo:
        if achados:
            for a in achados:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(f"**[PÁGINA {a['pagina']}] DETECTADO**")
                    st.code(f"ID: {a['id']}\nMOTIVO: {a['nome']}\nLEI: {a['lei']}", language="text")
            
            if prompt := st.chat_input("Pergunte ao Burocrata..."):
                with st.chat_message("user"): st.write(prompt)
                with st.chat_message("assistant"): st.write("Análise adicional: As cláusulas detectadas são nulas perante a Lei 8.245/91.")
        else:
            st.success("Console: Estéril. Nenhuma ameaça detectada.")
    else:
        st.info("Aguardando entrada de dados...")

st.markdown("---")
st.caption("Burocrata de Bolso | Auditoria de Precisão © 2026")
