import streamlit as st
import pdfplumber
import re
import unicodedata

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT
# --------------------------------------------------
st.set_page_config(page_title="Burocrata de Bolso", page_icon="⚖️", layout="wide")

# --------------------------------------------------
# LÓGICA DE AUDITORIA REFINADA E AMPLIADA
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        # Remove acentos e simplifica o texto para busca
        t = "".join(ch for ch in unicodedata.normalize('NFKD', t) if not unicodedata.combining(ch))
        return " ".join(t.lower().split())
    return ""

def realizar_auditoria_total(arquivo_pdf):
    problemas_detectados = []
    problemas_ja_encontrados = set()  # Para evitar duplicatas
    
    # Lista expandida de regras com mais padrões
    regras = [
        # 1. Reajuste ilegal
        {"id": "readjust", "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis|bianual|bimestral|4|quatro)", 
         "nome": "Reajuste Ilegal", 
         "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.", 
         "lei": "Lei 10.192/01"},
        
        # 2. Benfeitorias não indenizadas
        {"id": "improvements", "regex": r"(renuncia|nao indeniza|sem direito|nao tem direito|nao recebera).*?(benfeitoria|reforma|obra|melhoria|investimento)", 
         "nome": "Cláusula de Benfeitorias", 
         "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.", 
         "lei": "Art. 35, Lei 8.245/91"},
        
        # 3. Multa desproporcional
        {"id": "proportion", "regex": r"(multa.*?(12|doze|integral|total|cheia|completa).*?(aluguel|meses))|(pagar.*?(12|doze).*?meses.*?multa)", 
         "nome": "Multa s/ Proporcionalidade", 
         "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.", 
         "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC"},
        
        # 4. Violação de privacidade
        {"id": "privacy", "regex": r"(qualquer|sem aviso|independente|livre|a qualquer).*?(visita|vistoria|ingresso|entrar|acesso|inspecao)", 
         "nome": "Violação de Privacidade", 
         "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.", 
         "lei": "Art. 23, IX, Lei 8.245/91"},
        
        # 5. Garantia dupla (NOVO: Esta pode ser o 4º erro que estava faltando)
        {"id": "guarantee_dupla", "regex": r"(fiador.*?(caucao|deposito|seguro|aval))|((caucao|deposito|seguro|aval).*?fiador)|(exige.*?(fiador.*?caucao|caucao.*?fiador))", 
         "nome": "Garantia Dupla Ilegal", 
         "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).", 
         "lei": "Art. 37, Lei 8.245/91"},
        
        # 6. Cláusula de despejo sumário (NOVO)
        {"id": "summary_eviction", "regex": r"(despejo|desocupacao).*?(imediata|sumario|automatico|sem notificacao)", 
         "nome": "Despejo Sumário Ilegal", 
         "exp": "O despejo requer processo judicial e não pode ser automático por cláusula contratual.", 
         "lei": "Art. 9º, Lei 8.245/91"},
        
        # 7. Venda despeja inquilino (NOVO)
        {"id": "sale_eviction", "regex": r"(venda|alienacao).*?(rescindir|terminar|desocupar|despejo)", 
         "nome": "Cláusula 'Venda Despeja'", 
         "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.", 
         "lei": "Art. 27, Lei 8.245/91"},
        
        # 8. Proibição de animais (NOVO)
        {"id": "no_pets", "regex": r"(proibido|nao permitido|vedado).*?(animais|pet|cao|gato|animal)", 
         "nome": "Proibição Total de Animais", 
         "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.", 
         "lei": "Art. 51, CDC e Súmula 482 STJ"},
    ]

    with pdfplumber.open(arquivo_pdf) as pdf:
        texto_completo = ""
        
        # Extrai todo o texto primeiro para análise contextual
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_completo += texto_pag + "\n"
        
        texto_normalizado = normalizar_texto(texto_completo)
        
        # Análise por página para localização
        for i, pagina in enumerate(pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_limpo = normalizar_texto(texto_pag)
            
            for r in regras:
                # Procura na página específica
                matches_pagina = list(re.finditer(r["regex"], texto_limpo, re.IGNORECASE))
                
                # Também procura no texto completo para contexto
                matches_completo = list(re.finditer(r["regex"], texto_normalizado, re.IGNORECASE))
                
                if matches_pagina:
                    for match in matches_pagina:
                        chave_duplicata = f"{r['id']}_{i+1}_{match.start()}"
                        if chave_duplicata not in problemas_ja_encontrados:
                            # Extrai contexto para melhor análise
                            inicio = max(0, match.start() - 50)
                            fim = min(len(texto_limpo), match.end() + 50)
                            contexto = texto_limpo[inicio:fim]
                            
                            problemas_detectados.append({
                                **r, 
                                "pagina": i + 1,
                                "contexto": f"...{contexto}..." if contexto else "",
                                "posicao": match.start()
                            })
                            problemas_ja_encontrados.add(chave_duplicata)
                
                # Se não encontrou na página mas encontrou no geral, marca na primeira página onde aparece
                elif matches_completo and not any(p['id'] == r['id'] for p in problemas_detectados):
                    # Encontra a primeira ocorrência no texto completo
                    for match in matches_completo:
                        # Determina em qual página está essa ocorrência
                        texto_antes = texto_normalizado[:match.start()]
                        quebras_pagina = texto_antes.count('\n')
                        # Estimativa simplificada da página
                        pagina_estimada = min(i+1, len(pdf.pages))
                        
                        chave_duplicata = f"{r['id']}_global_{match.start()}"
                        if chave_duplicata not in problemas_ja_encontrados:
                            problemas_detectados.append({
                                **r, 
                                "pagina": pagina_estimada,
                                "contexto": "Detectado no documento",
                                "posicao": match.start()
                            })
                            problemas_ja_encontrados.add(chave_duplicata)
                            break
    
    # Ordena por página e posição
    problemas_detectados.sort(key=lambda x: (x['pagina'], x.get('posicao', 0)))
    
    return problemas_detectados

# --------------------------------------------------
# INTERFACE EM COLUNAS
# --------------------------------------------------

st.markdown("<h1 style='color: #1e3a8a;'>⚖️ Burocrata de Bolso v6.0</h1>", unsafe_allow_html=True)
st.write("---")

col_esq, col_dir = st.columns([1.5, 1])

with col_esq:
    st.subheader("📄 Análise Técnica Avançada")
    arquivo = st.file_uploader("Suba o contrato em PDF", type=["pdf"])
    
    if arquivo:
        # Chama a função aprimorada
        achados = realizar_auditoria_total(arquivo)
        
        # Cálculo de score mais refinado
        penalidade = min(len(achados) * 15, 100)  # Máximo 15 pontos por problema
        score = max(100 - penalidade, 0)
        
        st.metric("Score de Segurança", f"{score}/100", 
                 delta="Alto Risco" if score < 60 else "Risco Moderado" if score < 80 else "Baixo Risco")
        st.progress(score / 100)
        
        if achados:
            st.error(f"🔍 Auditoria concluiu: {len(achados)} pontos críticos encontrados.")
            
            # Agrupa por tipo de problema
            tipos_problemas = {}
            for a in achados:
                if a['nome'] not in tipos_problemas:
                    tipos_problemas[a['nome']] = 0
                tipos_problemas[a['nome']] += 1
            
            st.warning(f"**Tipos de irregularidades:** {', '.join(tipos_problemas.keys())}")
            
            for a in achados:
                with st.expander(f"🚨 Página {a['pagina']}: {a['nome']} ({a['lei']})"):
                    st.write(f"**Análise Técnica:** {a['exp']}")
                    if a.get('contexto'):
                        st.write(f"**Trecho detectado:** `{a['contexto']}`")
                    st.caption(f"**Base Legal:** {a['lei']}")
                    st.caption(f"**ID da Regra:** {a['id']}")
        else:
            st.success("✅ Nenhuma irregularidade detectada nos padrões de auditoria.")

with col_dir:
    st.subheader("🖥️ Console (DevTools Avançado)")
    st.write("---")
    
    if arquivo:
        if achados:
            st.write(f"**DEBUG INFO:** {len(achados)} problemas encontrados")
            st.write(f"**Regras aplicadas:** {len(regras) if 'regras' in locals() else 'N/A'}")
            
            for a in achados:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(f"**[PÁG. {a['pagina']}] {a['nome']}**")
                    st.code(f"ID: {a['id']}\nLEI: {a['lei']}\nCONTEXTO: {a.get('contexto', 'N/A')}", 
                           language="text")
            
            st.divider()
            
            # Sistema de perguntas aprimorado
            if prompt := st.chat_input("Pergunte sobre alguma cláusula..."):
                with st.chat_message("user"): 
                    st.write(prompt)
                
                with st.chat_message("assistant", avatar="⚖️"): 
                    # Resposta contextual baseada nos problemas encontrados
                    if any(termo in prompt.lower() for termo in ['reajuste', 'aumento']):
                        st.write("**Resposta do Burocrata:** Reajustes devem ser anuais (12 meses). Trimestrais/mensais são ilegais pela Lei 10.192/01.")
                    elif any(termo in prompt.lower() for termo in ['multa', 'rescisão']):
                        st.write("**Resposta do Burocrata:** Multas devem ser proporcionais ao tempo restante. Multa integral de 12 meses é considerada abusiva.")
                    elif any(termo in prompt.lower() for termo in ['fiador', 'garantia', 'caução']):
                        st.write("**Resposta do Burocrata:** É proibido exigir mais de uma garantia (ex: fiador E caução). Art. 37, Lei 8.245/91.")
                    else:
                        st.write("**Resposta do Burocrata:** As cláusulas detectadas são nulas perante a Lei 8.245/91. Recomendo revisão por advogado especializado.")
        else:
            st.success("✅ Console: Auditoria limpa. Nenhuma ameaça detectada.")
            st.info("Dica: O sistema verifica 8 tipos de cláusulas problemáticas comuns em contratos de locação.")
    else:
        st.info("📁 Aguardando upload do contrato...")
        st.caption("Suporte: PDF com texto (não escaneado como imagem)")

st.markdown("---")
st.caption("Burocrata de Bolso | Auditoria de Precisão Avançada © 2026")

# Adiciona informações de ajuda
with st.sidebar:
    st.subheader("ℹ️ Tipos de Cláusulas Analisadas")
    st.write("""
    1. **Reajuste ilegal** - Períodos < 12 meses
    2. **Benfeitorias não indenizadas** - Renúncia a direito
    3. **Multa desproporcional** - 12 meses integrais
    4. **Violação de privacidade** - Entrada sem aviso
    5. **Garantia dupla** - Fiador + caução
    6. **Despejo sumário** - Automático sem processo
    7. **Venda despeja** - Rescisão por venda
    8. **Proibição de animais** - Restrição abusiva
    """)
    st.divider()
    st.caption("Versão 6.0 | Detecção aprimorada")
