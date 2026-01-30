import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd
import io

# --------------------------------------------------
# CONFIGURAÇÃO DE LAYOUT PROFISSIONAL
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Análise Jurídica de Documentos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# --------------------------------------------------
st.markdown("""
<style>
    .header-title {
        font-family: 'Georgia', serif;
        font-weight: 600;
        color: #1a365d;
        border-bottom: 2px solid #c9a96e;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    .header-subtitle {
        font-family: 'Helvetica', sans-serif;
        color: #4a5568;
        font-size: 16px;
        margin-top: -15px;
        margin-bottom: 30px;
    }
    
    .analysis-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #2c5282;
        margin-bottom: 15px;
    }
    
    .info-card {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    .metric-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .score-excellent { color: #276749; font-weight: 700; }
    .score-moderate { color: #d69e2e; font-weight: 700; }
    .score-critical { color: #c53030; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# INICIALIZAÇÃO DA SESSÃO
# --------------------------------------------------
if 'achados' not in st.session_state:
    st.session_state['achados'] = []
if 'tipo_doc' not in st.session_state:
    st.session_state['tipo_doc'] = 'desconhecido'
if 'analisado' not in st.session_state:
    st.session_state['analisado'] = False

# --------------------------------------------------
# SISTEMA DE DETECÇÃO DE TIPO DE DOCUMENTO
# --------------------------------------------------

class DocumentTypeDetector:
    @staticmethod
    def detectar_tipo(texto):
        if not texto or len(texto.strip()) < 50:
            return 'desconhecido'
            
        texto_lower = texto.lower()
        
        locacao_palavras = ['contrato de locação', 'locador', 'locatário', 'aluguel', 'imóvel', 
                           'vigência', 'fiador', 'caução', 'valor do aluguel', 'reajuste']
        
        nfe_palavras = ['nota fiscal', 'nfe', 'nf-e', 'chave de acesso', 'emitente', 'destinatário',
                       'cnpj', 'icms', 'ipi', 'danfe', 'número da nota']
        
        servico_palavras = ['contrato de prestação de serviços', 'contratante', 'contratada', 
                           'objeto do contrato', 'prestador de serviços', 'tomador de serviços']
        
        compra_venda_palavras = ['contrato de compra e venda', 'vendedor', 'comprador', 
                                'imóvel objeto', 'matrícula', 'preço total', 'sinal']
        
        contagem_locacao = sum(1 for palavra in locacao_palavras if palavra in texto_lower)
        contagem_nfe = sum(1 for palavra in nfe_palavras if palavra in texto_lower)
        contagem_servico = sum(1 for palavra in servico_palavras if palavra in texto_lower)
        contagem_cv = sum(1 for palavra in compra_venda_palavras if palavra in texto_lower)
        
        contagens = {
            'contrato_locacao': contagem_locacao,
            'nota_fiscal': contagem_nfe,
            'contrato_servico': contagem_servico,
            'contrato_compra_venda': contagem_cv
        }
        
        tipo_detectado = max(contagens.items(), key=lambda x: x[1])
        
        if tipo_detectado[1] < 2:
            return 'desconhecido'
        
        return tipo_detectado[0]

# --------------------------------------------------
# LÓGICA DE AUDITORIA PARA CONTRATO DE LOCAÇÃO - CORRIGIDA
# --------------------------------------------------

def normalizar_texto(t):
    if t:
        t = unicodedata.normalize('NFKD', t)
        t = ''.join([c for c in t if not unicodedata.combining(c)])
        t = t.lower()
        t = re.sub(r'\s+', ' ', t)
        return t.strip()
    return ""

def realizar_auditoria_contrato_locacao(arquivo_pdf):
    problemas_detectados = []
    
    # REGRAS CORRIGIDAS - MAIS FLEXÍVEIS E ABRANGENTES
    regras = [
        # 1. Reajuste ilegal - MAIS FLEXÍVEL
        {
            "id": "readjust", 
            "regex": r"reajuste.*?(trimestral|mensal|semestral|3|tres|6|seis|bianual|bimestral|4|quatro|quart[oe]|semestre|mes)", 
            "nome": "Reajuste Ilegal", 
            "gravidade": "critico",
            "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.", 
            "lei": "Lei 10.192/01"
        },
        
        # 2. Benfeitorias - MAIS FLEXÍVEL
        {
            "id": "improvements", 
            "regex": r"(renuncia|nao indeniza|sem direito|nao tem direito|nao recebera|abre mao|abdica).*?(benfeitoria|reforma|obra|melhoria|investimento|gasto|despesa)", 
            "nome": "Cláusula de Benfeitorias", 
            "gravidade": "critico",
            "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.", 
            "lei": "Art. 35, Lei 8.245/91"
        },
        
        # 3. Multa desproporcional - MAIS FLEXÍVEL
        {
            "id": "proportion", 
            "regex": r"(multa.*?(12|doze|integral|total|cheia|completa|inteira).*?(aluguel|meses|mensalidade))|(pagar.*?(12|doze).*?meses.*?multa)|(multa.*?12.*?meses)", 
            "nome": "Multa s/ Proporcionalidade", 
            "gravidade": "critico",
            "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.", 
            "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC"
        },
        
        # 4. Violação de privacidade - MAIS FLEXÍVEL
        {
            "id": "privacy", 
            "regex": r"(qualquer|sem aviso|independente|livre|a qualquer|sempre que|quando.*?quiser).*?(visita|vistoria|ingresso|entrar|acesso|inspecao|verificar|ver)", 
            "nome": "Violação de Privacidade", 
            "gravidade": "medio",
            "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.", 
            "lei": "Art. 23, IX, Lei 8.245/91"
        },
        
        # 5. Garantia dupla - CORRIGIDA E MAIS FLEXÍVEL
        {
            "id": "guarantee_dupla", 
            "regex": r"(fiador.*?(caucao|deposito|seguro|aval|garantia))|((caucao|deposito|seguro|aval|garantia).*?fiador)|(fiador.*?e.*?(caucao|deposito))|((caucao|deposito).*?e.*?fiador)|(exige.*?fiador.*?caucao)|(exige.*?caucao.*?fiador)", 
            "nome": "Garantia Dupla Ilegal", 
            "gravidade": "critico",
            "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).", 
            "lei": "Art. 37, Lei 8.245/91"
        },
        
        # 6. Despejo sumário - MAIS FLEXÍVEL
        {
            "id": "summary_eviction", 
            "regex": r"(despejo|desocupacao).*?(imediata|sumario|automatico|sem notificacao|automaticamente|de imediato)", 
            "nome": "Despejo Sumário Ilegal", 
            "gravidade": "critico",
            "exp": "O despejo requer processo judicial e não pode ser automático por cláusula contratual.", 
            "lei": "Art. 9º, Lei 8.245/91"
        },
        
        # 7. Venda despeja - MAIS FLEXÍVEL
        {
            "id": "sale_eviction", 
            "regex": r"(venda|alienacao|transferencia).*?(rescindir|terminar|desocupar|despejo|rescisao|fim)", 
            "nome": "Cláusula 'Venda Despeja'", 
            "gravidade": "medio",
            "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.", 
            "lei": "Art. 27, Lei 8.245/91"
        },
        
        # 8. Proibição de animais - MAIS FLEXÍVEL
        {
            "id": "no_pets", 
            "regex": r"(proibido|nao permitido|vedado|proibicao).*?(animais|pet|cao|gato|animal|estimacao)", 
            "nome": "Proibição Total de Animais", 
            "gravidade": "leve",
            "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.", 
            "lei": "Art. 51, CDC e Súmula 482 STJ"
        },
    ]

    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            texto_completo = ""
            
            for i, pagina in enumerate(pdf.pages):
                try:
                    texto_pag = pagina.extract_text() or ""
                    texto_completo += texto_pag + "\n"
                except:
                    continue
            
            texto_normalizado = normalizar_texto(texto_completo)
            
            # DEBUG: Mostrar texto normalizado
            with st.expander("🔍 Ver texto extraído e normalizado"):
                st.text("Texto normalizado (primeiros 2000 caracteres):")
                st.text(texto_normalizado[:2000])
                st.text(f"\nTotal de caracteres: {len(texto_normalizado)}")
            
            # Verificar cada regra
            for regra in regras:
                try:
                    # Usar findall para ver todas as correspondências
                    matches = re.findall(regra["regex"], texto_normalizado, re.IGNORECASE)
                    
                    if matches:
                        st.success(f"✅ Regra '{regra['nome']}' encontrada!")
                        # Pegar contexto da primeira ocorrência
                        match = re.search(regra["regex"], texto_normalizado, re.IGNORECASE)
                        if match:
                            inicio = max(0, match.start() - 150)
                            fim = min(len(texto_normalizado), match.end() + 150)
                            contexto = texto_normalizado[inicio:fim]
                            
                            problemas_detectados.append({
                                "id": regra["id"],
                                "nome": regra["nome"],
                                "gravidade": regra["gravidade"],
                                "exp": regra["exp"],
                                "lei": regra["lei"],
                                "contexto": f"...{contexto}..." if contexto else "",
                                "pagina": 1
                            })
                        
                except Exception as e:
                    st.warning(f"Erro na regra {regra['id']}: {str(e)}")
                    continue
        
        # Remover duplicatas
        problemas_unicos = []
        ids_vistos = set()
        for problema in problemas_detectados:
            if problema['id'] not in ids_vistos:
                problemas_unicos.append(problema)
                ids_vistos.add(problema['id'])
        
        # Ordenar por gravidade
        ordem_gravidade = {'critico': 0, 'medio': 1, 'leve': 2}
        problemas_unicos.sort(key=lambda x: ordem_gravidade.get(x.get('gravidade', 'leve'), 2))
        
        return problemas_unicos
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {str(e)}")
        return []

# --------------------------------------------------
# FUNÇÃO PRINCIPAL DE AUDITORIA
# --------------------------------------------------

def realizar_auditoria_total(arquivo_pdf):
    try:
        arquivo_bytes = arquivo_pdf.read()
        
        with pdfplumber.open(io.BytesIO(arquivo_bytes)) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                try:
                    texto = pagina.extract_text() or ""
                    texto_completo += texto + "\n"
                except:
                    continue
        
        if not texto_completo.strip():
            st.warning("Não foi possível extrair texto do PDF.")
            return [], 'desconhecido'
        
        detector = DocumentTypeDetector()
        tipo_documento = detector.detectar_tipo(texto_completo)
        
        if tipo_documento == 'contrato_locacao':
            problemas = realizar_auditoria_contrato_locacao(io.BytesIO(arquivo_bytes))
            return problemas, tipo_documento
        
        return [], tipo_documento
        
    except Exception as e:
        st.error(f"Erro ao processar documento: {str(e)}")
        return [], 'desconhecido'

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def obter_icone_documento(tipo_doc):
    icones = {
        'contrato_locacao': '🏠',
        'nota_fiscal': '🧾',
        'contrato_servico': '⚖️',
        'contrato_compra_venda': '💰',
        'desconhecido': '📄'
    }
    return icones.get(tipo_doc, '📄')

# --------------------------------------------------
# INTERFACE DO USUÁRIO
# --------------------------------------------------

st.markdown('<h1 class="header-title">Burocrata de Bolso v4.0</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Sistema de Análise Jurídica de Documentos</p>', unsafe_allow_html=True)

# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------
col_upload, col_status = st.columns([2, 1])

with col_upload:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.subheader("📄 Análise de Documento")
    
    arquivo = st.file_uploader(
        "Selecione um documento em formato PDF",
        type=["pdf"],
        help="Documentos suportados: Contratos de locação"
    )
    
    if arquivo:
        if st.button("🚀 Iniciar Análise Jurídica", type="primary", use_container_width=True):
            with st.spinner("Analisando documento..."):
                achados, tipo_doc = realizar_auditoria_total(arquivo)
                
                st.session_state['achados'] = achados
                st.session_state['tipo_doc'] = tipo_doc
                st.session_state['analisado'] = True
                st.session_state['arquivo_nome'] = arquivo.name
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_status:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    if st.session_state.get('analisado', False):
        achados = st.session_state.get('achados', [])
        tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
        
        penalidade_critico = sum(1 for a in achados if a.get('gravidade') == 'critico') * 25
        penalidade_medio = sum(1 for a in achados if a.get('gravidade') == 'medio') * 15
        penalidade_leve = sum(1 for a in achados if a.get('gravidade') == 'leve') * 5
        penalidade = min(penalidade_critico + penalidade_medio + penalidade_leve, 100)
        
        score = max(100 - penalidade, 0)
        
        st.markdown("**Índice de Conformidade**")
        
        if score >= 80:
            st.markdown(f'<h2 class="score-excellent">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Conforme")
        elif score >= 60:
            st.markdown(f'<h2 class="score-moderate">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Atenção")
        else:
            st.markdown(f'<h2 class="score-critical">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**Status:** Crítico")
        
        st.progress(score / 100)
        
        icone = obter_icone_documento(tipo_doc)
        st.markdown(f"**Documento:** {icone} {tipo_doc.replace('_', ' ').title()}")
        st.markdown(f"**Problemas:** {len(achados)}")
    else:
        st.markdown("**Índice de Conformidade**")
        st.markdown('<h2>--/100</h2>', unsafe_allow_html=True)
        st.markdown("**Status:** Aguardando")
        st.progress(0)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# RESULTADOS DA ANÁLISE
# --------------------------------------------------
if st.session_state.get('analisado', False):
    achados = st.session_state.get('achados', [])
    tipo_doc = st.session_state.get('tipo_doc', 'desconhecido')
    
    if achados:
        st.markdown("---")
        st.subheader("🔍 Resultados da Auditoria")
        
        col_summary, col_details = st.columns([1, 2])
        
        with col_summary:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**📊 Sumário Executivo**")
            
            icone = obter_icone_documento(tipo_doc)
            st.markdown(f"- **Tipo:** {icone} {tipo_doc.replace('_', ' ').title()}")
            st.markdown(f"- **Total de problemas:** {len(achados)}")
            
            criticos = sum(1 for a in achados if a.get('gravidade') == 'critico')
            medios = sum(1 for a in achados if a.get('gravidade') == 'medio')
            leves = sum(1 for a in achados if a.get('gravidade') == 'leve')
            
            if criticos > 0:
                st.markdown(f"- 🚨 **Críticos:** {criticos}")
            if medios > 0:
                st.markdown(f"- ⚠️ **Médios:** {medios}")
            if leves > 0:
                st.markdown(f"- ℹ️ **Leves:** {leves}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Mostrar quais regras foram detectadas
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**🔍 Regras Detectadas**")
            for a in achados:
                st.markdown(f"- {a['nome']}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_details:
            for a in achados:
                if a.get('gravidade') == 'critico':
                    border_color = '#c53030'
                    gravidade_texto = "CRÍTICO"
                    emoji = "🚨"
                elif a.get('gravidade') == 'medio':
                    border_color = '#d69e2e'
                    gravidade_texto = "MÉDIO"
                    emoji = "⚠️"
                elif a.get('gravidade') == 'leve':
                    border_color = '#38a169'
                    gravidade_texto = "LEVE"
                    emoji = "ℹ️"
                else:
                    border_color = '#2c5282'
                    gravidade_texto = ""
                    emoji = ""
                
                titulo = f"{emoji} {a['nome']} ({gravidade_texto})"
                
                with st.expander(titulo):
                    st.markdown(f"**📝 Descrição:** {a.get('exp', 'Descrição não disponível')}")
                    st.markdown(f"**⚖️ Fundamento Legal:** {a.get('lei', 'Não especificado')}")
                    
                    if a.get('contexto'):
                        st.markdown("**🔍 Contexto Encontrado:**")
                        st.markdown(f'<div style="background-color: #f7fafc; padding: 10px; border-radius: 4px; border-left: 3px solid {border_color}; font-size: 14px; font-family: monospace;">{a["contexto"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**📍 Localização:** Página {a.get('pagina', 1)}")
    
    else:
        st.markdown("---")
        st.markdown('<div class="analysis-card" style="border-left-color: #38a169;">', unsafe_allow_html=True)
        st.markdown("**✅ Resultado da Análise**")
        st.markdown("Nenhuma irregularidade detectada nas cláusulas verificadas.")
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# TEXTO DO CONTRATO DE TESTE COM TODAS AS ARMAZILHAS
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Contrato de Teste (Copie e cole)")

contrato_teste_completo = """CONTRATO DE LOCAÇÃO RESIDENCIAL

CLÁUSULA 1 - DO OBJETO
A LOCADORA dá em locação ao LOCATÁRIO o imóvel residencial situado à Avenida Paulista, 1000, apartamento 101, São Paulo-SP.

CLÁUSULA 2 - DO PRAZO
Contrato com vigência de 30 meses.

CLÁUSULA 3 - DO VALOR DO ALUGUEL
O aluguel mensal será de R$ 3.000,00. O reajuste será trimestral, conforme índices oficiais. [ARMADILHA 1]

CLÁUSULA 4 - DAS GARANTIAS
Para garantia do fiel cumprimento, o LOCATÁRIO deverá apresentar:
a) Dois fiadores com renda comprovada;
b) Depósito caução de três meses de aluguel. [ARMADILHA 2]

CLÁUSULA 5 - DAS BENFEITORIAS
O LOCATÁRIO renuncia a qualquer indenização por benfeitorias necessárias realizadas no imóvel, mesmo que indispensáveis. [ARMADILHA 3]

CLÁUSULA 6 - DAS VISITAS
A LOCADORA poderá realizar visitas ao imóvel a qualquer tempo, independentemente de aviso prévio, para vistorias e inspeções. [ARMADILHA 4]

CLÁUSULA 7 - DA MULTA
Em caso de rescisão antecipada pelo LOCATÁRIO, será devida multa correspondente a doze meses de aluguel, independentemente do tempo restante de contrato. [ARMADILHA 5]

CLÁUSULA 8 - DOS ANIMAIS
É vedada a permanência de quaisquer animais de estimação no imóvel locado.

CLÁUSULA 9 - DA VENDA DO IMÓVEL
Em caso de venda do imóvel, o presente contrato estará automaticamente rescindido, sem qualquer ônus para a LOCADORA.

CLÁUSULA 10 - DO FORO
Fica eleito o foro da Comarca de São Paulo.

São Paulo, 15 de dezembro de 2023
"""

st.code(contrato_teste_completo, language="text")

st.markdown("""
**🎯 Armadilhas que devem ser detectadas:**
1. 🚨 **Reajuste trimestral** (deve ser anual) - **CRÍTICO**
2. 🚨 **Garantia dupla** (fiador + caução é ilegal) - **CRÍTICO**
3. 🚨 **Renúncia a benfeitorias** (cláusula nula) - **CRÍTICO**
4. ⚠️ **Violação de privacidade** (visitas sem aviso) - **MÉDIO**
5. 🚨 **Multa desproporcional** (12 meses é abusivo) - **CRÍTICO**

**Total esperado: 5 problemas (4 críticos, 1 médio)**
""")

# --------------------------------------------------
# BARRA LATERAL
# --------------------------------------------------
with st.sidebar:
    st.markdown('<p class="sidebar-title">🔧 Módulos</p>', unsafe_allow_html=True)
    
    st.markdown("**🏠 Contratos de Locação**")
    st.markdown('<div style="font-size: 12px; color: #4a5568;">8 cláusulas problemáticas analisadas</div>', unsafe_allow_html=True)
    
    with st.expander("📋 Cláusulas analisadas"):
        st.markdown("""
        - 🚨 Reajuste (trimestral/mensal)
        - 🚨 Benfeitorias (renúncia)
        - 🚨 Multa (12 meses)
        - ⚠️ Privacidade (visitas)
        - 🚨 Garantia (dupla)
        - 🚨 Despejo (sumário)
        - ⚠️ Venda (despeja)
        - ℹ️ Animais (proibição)
        """)
    
    st.markdown("---")
    
    st.markdown("**🎯 Legenda**")
    st.markdown("""
    <div style="font-size: 12px;">
    🚨 **Crítico:** Cláusula ilegal<br>
    ⚠️ **Médio:** Potencialmente abusiva<br>
    ℹ️ **Leve:** Recomendação
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 12px; padding: 20px;">
    Burocrata de Bolso v4.0 | Sistema de Análise Jurídica © 2024
</div>
""", unsafe_allow_html=True)
