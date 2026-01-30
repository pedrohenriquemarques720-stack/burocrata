import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime
import pandas as pd
import io

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Análise Jurídica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ESTILOS
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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE AUDITORIA MELHORADO
# --------------------------------------------------

def normalizar_texto(t):
    """Normaliza texto removendo acentos e padronizando"""
    if t:
        # Remove acentos
        t = unicodedata.normalize('NFKD', t)
        t = ''.join([c for c in t if not unicodedata.combining(c)])
        # Converte para minúsculas e remove espaços extras
        t = t.lower()
        t = re.sub(r'\s+', ' ', t)
        return t.strip()
    return ""

class AuditoriaContratoLocacao:
    """Sistema de auditoria inteligente para contratos de locação"""
    
    def __init__(self):
        self.padroes_detectados = []
        
    def buscar_padroes(self, texto):
        """Busca múltiplos padrões para cada tipo de problema"""
        
        texto_normalizado = normalizar_texto(texto)
        problemas = []
        
        # 1. REAJUSTE ILEGAL - Múltiplos padrões
        padroes_reajuste = [
            r'reajuste.*?trimestral',
            r'reajuste.*?mensal',
            r'reajuste.*?semestral',
            r'reajuste.*?3.*?meses',
            r'reajuste.*?6.*?meses',
            r'reajuste.*?4.*?meses',
            r'reajuste.*?bimestral',
            r'reajuste.*?bianual',
            r'reajuste a cada.*?(3|4|6)',
            r'reajuste.*?cada.*?(3|4|6).*?meses'
        ]
        
        for padrao in padroes_reajuste:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "readjust",
                    "nome": "Reajuste Ilegal",
                    "gravidade": "critico",
                    "exp": "O reajuste de aluguel deve ser ANUAL (12 meses). Períodos menores são ilegais.",
                    "lei": "Lei 10.192/01",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break  # Encontrou um padrão, para de buscar
        
        # 2. GARANTIA DUPLA - Múltiplos padrões
        padroes_garantia = [
            r'fiador.*?caucao',
            r'caucao.*?fiador',
            r'fiador.*?deposito',
            r'deposito.*?fiador',
            r'fiador.*?e.*?caucao',
            r'caucao.*?e.*?fiador',
            r'fiador.*?seguro.*?fianca',
            r'fiador.*?mais.*?caucao',
            r'exige.*?fiador.*?caucao',
            r'fiador.*?alem.*?caucao'
        ]
        
        for padrao in padroes_garantia:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "guarantee_dupla",
                    "nome": "Garantia Dupla Ilegal",
                    "gravidade": "critico",
                    "exp": "É proibido exigir mais de uma garantia no mesmo contrato (ex: fiador E caução).",
                    "lei": "Art. 37, Lei 8.245/91",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        # 3. BENFEITORIAS - Múltiplos padrões
        padroes_benfeitorias = [
            r'renuncia.*?benfeitoria',
            r'nao indeniza.*?benfeitoria',
            r'sem direito.*?benfeitoria',
            r'nao tem direito.*?benfeitoria',
            r'abre mao.*?benfeitoria',
            r'renuncia.*?reforma',
            r'nao recebera.*?reforma',
            r'sem direito.*?reforma',
            r'renuncia.*?obra',
            r'nao indeniza.*?obra'
        ]
        
        for padrao in padroes_benfeitorias:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "improvements",
                    "nome": "Cláusula de Benfeitorias",
                    "gravidade": "critico",
                    "exp": "O inquilino tem direito a indenização por reformas necessárias. Cláusula de renúncia é nula.",
                    "lei": "Art. 35, Lei 8.245/91",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        # 4. VIOLAÇÃO DE PRIVACIDADE - Múltiplos padrões
        padroes_privacidade = [
            r'qualquer.*?visita',
            r'sem aviso.*?visita',
            r'a qualquer.*?visita',
            r'livre.*?visita',
            r'qualquer.*?vistoria',
            r'sem aviso.*?vistoria',
            r'qualquer.*?entrar',
            r'sem aviso.*?entrar',
            r'visita.*?sem.*?aviso',
            r'vistoria.*?sem.*?aviso'
        ]
        
        for padrao in padroes_privacidade:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "privacy",
                    "nome": "Violação de Privacidade",
                    "gravidade": "medio",
                    "exp": "O locador não pode entrar no imóvel sem aviso prévio e hora combinada.",
                    "lei": "Art. 23, IX, Lei 8.245/91",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        # 5. MULTA DESPROPORCIONAL - Múltiplos padrões
        padroes_multa = [
            r'multa.*?12.*?meses',
            r'multa.*?doze.*?meses',
            r'12.*?meses.*?multa',
            r'doze.*?meses.*?multa',
            r'multa.*?integral',
            r'multa.*?total',
            r'multa.*?cheia',
            r'multa.*?completa',
            r'pagar.*?12.*?meses.*?multa',
            r'multa.*?correspondente.*?12.*?meses'
        ]
        
        for padrao in padroes_multa:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "proportion",
                    "nome": "Multa s/ Proporcionalidade",
                    "gravidade": "critico",
                    "exp": "A multa deve ser proporcional ao tempo que resta de contrato. Multa integral de 12 meses é abusiva.",
                    "lei": "Art. 4º, Lei 8.245/91 e Art. 51, CDC",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        # 6. VENDA DESPEJA - Múltiplos padrões
        padroes_venda = [
            r'venda.*?rescindido',
            r'venda.*?rescisao',
            r'venda.*?terminar',
            r'venda.*?desocupar',
            r'alienacao.*?rescindir',
            r'venda.*?automaticamente',
            r'venda.*?automatico'
        ]
        
        for padrao in padroes_venda:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "sale_eviction",
                    "nome": "Cláusula 'Venda Despeja'",
                    "gravidade": "medio",
                    "exp": "A venda do imóvel não rescinde automaticamente o contrato. Inquilino tem preferência.",
                    "lei": "Art. 27, Lei 8.245/91",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        # 7. ANIMAIS - Múltiplos padrões
        padroes_animais = [
            r'proibido.*?animais',
            r'vedado.*?animais',
            r'nao permitido.*?animais',
            r'proibicao.*?animais',
            r'nao.*?animais',
            r'proibido.*?pet',
            r'vedado.*?pet',
            r'proibido.*?animal'
        ]
        
        for padrao in padroes_animais:
            if re.search(padrao, texto_normalizado, re.IGNORECASE):
                problemas.append({
                    "id": "no_pets",
                    "nome": "Proibição Total de Animais",
                    "gravidade": "leve",
                    "exp": "Cláusula que proíbe qualquer animal pode ser considerada abusiva, exceto por justa causa.",
                    "lei": "Art. 51, CDC e Súmula 482 STJ",
                    "contexto": self._extrair_contexto(texto_normalizado, padrao),
                    "pagina": 1
                })
                break
        
        return problemas
    
    def _extrair_contexto(self, texto, padrao, tamanho=100):
        """Extrai contexto ao redor do padrão encontrado"""
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            inicio = max(0, match.start() - tamanho)
            fim = min(len(texto), match.end() + tamanho)
            return f"...{texto[inicio:fim]}..."
        return ""

def realizar_auditoria_contrato_locacao(arquivo_pdf):
    """Função principal de auditoria"""
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            texto_completo = ""
            
            for pagina in pdf.pages:
                try:
                    texto_pag = pagina.extract_text() or ""
                    texto_completo += texto_pag + "\n"
                except:
                    continue
            
            if not texto_completo.strip():
                st.warning("Não foi possível extrair texto do PDF.")
                return []
            
            # DEBUG: Mostrar texto normalizado
            with st.expander("🔍 Ver texto extraído (para debug)"):
                texto_normalizado = normalizar_texto(texto_completo)
                st.text_area("Texto normalizado (primeiros 2000 caracteres):", 
                           texto_normalizado[:2000], height=200)
                
                # Mostrar estatísticas do texto
                st.metric("Caracteres no texto", len(texto_normalizado))
                st.metric("Palavras no texto", len(texto_normalizado.split()))
            
            # Usar o sistema de auditoria melhorado
            auditoria = AuditoriaContratoLocacao()
            problemas = auditoria.buscar_padroes(texto_completo)
            
            # Remover duplicatas
            problemas_unicos = []
            ids_vistos = set()
            for problema in problemas:
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
# FUNÇÃO PRINCIPAL
# --------------------------------------------------

def processar_documento(arquivo_pdf):
    """Processa o documento e retorna problemas detectados"""
    try:
        arquivo_bytes = arquivo_pdf.read()
        
        # Verificar se é contrato de locação (simples)
        with pdfplumber.open(io.BytesIO(arquivo_bytes)) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                try:
                    texto = pagina.extract_text() or ""
                    texto_completo += texto + "\n"
                except:
                    continue
        
        texto_lower = texto_completo.lower()
        indicadores_locacao = ['locação', 'locador', 'locatário', 'aluguel', 'fiador', 'caução']
        
        if any(ind in texto_lower for ind in indicadores_locacao):
            problemas = realizar_auditoria_contrato_locacao(io.BytesIO(arquivo_bytes))
            return problemas, 'contrato_locacao'
        
        return [], 'desconhecido'
        
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return [], 'desconhecido'

# --------------------------------------------------
# INTERFACE
# --------------------------------------------------

st.markdown('<h1 class="header-title">Burocrata de Bolso v5.0</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Sistema Inteligente de Análise Jurídica</p>', unsafe_allow_html=True)

# Estado da sessão
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'analisado' not in st.session_state:
    st.session_state.analisado = False

# Upload e análise
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.subheader("📄 Upload do Documento")
    
    arquivo = st.file_uploader(
        "Selecione um contrato de locação em PDF",
        type=["pdf"],
        help="O sistema analisa contratos de locação residencial"
    )
    
    if arquivo:
        if st.button("🔍 Analisar Documento", type="primary", use_container_width=True):
            with st.spinner("Analisando cláusulas..."):
                problemas, tipo_doc = processar_documento(arquivo)
                st.session_state.resultados = {
                    'problemas': problemas,
                    'tipo_doc': tipo_doc,
                    'nome_arquivo': arquivo.name
                }
                st.session_state.analisado = True
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    if st.session_state.analisado and st.session_state.resultados:
        problemas = st.session_state.resultados['problemas']
        
        # Calcular score
        critico_count = sum(1 for p in problemas if p.get('gravidade') == 'critico')
        medio_count = sum(1 for p in problemas if p.get('gravidade') == 'medio')
        leve_count = sum(1 for p in problemas if p.get('gravidade') == 'leve')
        
        penalidade = min(critico_count * 30 + medio_count * 15 + leve_count * 5, 100)
        score = max(100 - penalidade, 0)
        
        st.markdown("**Índice de Conformidade**")
        
        if score >= 80:
            st.markdown(f'<h2 style="color: #276749;">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**✅ Conforme**")
        elif score >= 60:
            st.markdown(f'<h2 style="color: #d69e2e;">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**⚠️ Atenção**")
        else:
            st.markdown(f'<h2 style="color: #c53030;">{score}/100</h2>', unsafe_allow_html=True)
            st.markdown("**🚨 Crítico**")
        
        st.progress(score / 100)
        st.markdown(f"**Problemas:** {len(problemas)}")
    else:
        st.markdown("**Índice de Conformidade**")
        st.markdown('<h2>--/100</h2>', unsafe_allow_html=True)
        st.markdown("**Aguardando análise**")
        st.progress(0)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Resultados
if st.session_state.analisado and st.session_state.resultados:
    problemas = st.session_state.resultados['problemas']
    
    if problemas:
        st.markdown("---")
        st.subheader("📊 Resultados da Análise")
        
        # Estatísticas
        critico_count = sum(1 for p in problemas if p.get('gravidade') == 'critico')
        medio_count = sum(1 for p in problemas if p.get('gravidade') == 'medio')
        leve_count = sum(1 for p in problemas if p.get('gravidade') == 'leve')
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric("🚨 Críticos", critico_count, delta=None)
        with col_stats2:
            st.metric("⚠️ Médios", medio_count, delta=None)
        with col_stats3:
            st.metric("ℹ️ Leves", leve_count, delta=None)
        
        # Lista de problemas
        for problema in problemas:
            gravidade = problema.get('gravidade', '')
            
            if gravidade == 'critico':
                emoji = "🚨"
                cor = "#c53030"
            elif gravidade == 'medio':
                emoji = "⚠️"
                cor = "#d69e2e"
            else:
                emoji = "ℹ️"
                cor = "#38a169"
            
            with st.expander(f"{emoji} {problema['nome']}"):
                st.markdown(f"**Descrição:** {problema['exp']}")
                st.markdown(f"**Fundamento Legal:** {problema['lei']}")
                
                if problema.get('contexto'):
                    st.markdown("**Trecho encontrado:**")
                    st.markdown(f'<div style="background-color: #f7fafc; padding: 10px; border-radius: 4px; border-left: 3px solid {cor}; font-size: 14px;">{problema["contexto"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.success("✅ Nenhuma irregularidade detectada nas cláusulas analisadas!")

# Texto de teste
st.markdown("---")
st.subheader("📝 Texto de Teste para Copiar")

texto_teste = """CONTRATO DE LOCAÇÃO RESIDENCIAL

CLÁUSULA 1 - DO OBJETO
A LOCADORA dá em locação ao LOCATÁRIO o imóvel residencial situado à Avenida Paulista, 1000, apartamento 101, São Paulo-SP.

CLÁUSULA 2 - DO PRAZO
Contrato com vigência de 30 meses.

CLÁUSULA 3 - DO VALOR DO ALUGUEL
O aluguel mensal será de R$ 3.000,00. O reajuste será trimestral.

CLÁUSULA 4 - DAS GARANTIAS
Para garantia do fiel cumprimento, o LOCATÁRIO deverá apresentar fiadores com renda comprovada e depósito caução de três meses de aluguel.

CLÁUSULA 5 - DAS BENFEITORIAS
O LOCATÁRIO renuncia a qualquer indenização por benfeitorias necessárias realizadas no imóvel.

CLÁUSULA 6 - DAS VISITAS
A LOCADORA poderá realizar visitas ao imóvel a qualquer tempo, sem aviso prévio.

CLÁUSULA 7 - DA MULTA
Em caso de rescisão antecipada, será devida multa correspondente a 12 meses de aluguel.

CLÁUSULA 8 - DOS ANIMAIS
É vedada a permanência de animais de estimação.

CLÁUSULA 9 - DA VENDA
Em caso de venda do imóvel, o contrato estará automaticamente rescindido.

CLÁUSULA 10 - DO FORO
Fica eleito o foro da Comarca de São Paulo.
"""

st.code(texto_teste, language="text")

st.info("""
**🎯 Este contrato de teste contém 5 armadilhas:**

1. **🚨 Reajuste trimestral** (deve ser anual)
2. **🚨 Garantia dupla** (fiador E caução)
3. **🚨 Renúncia a benfeitorias** (cláusula nula)
4. **⚠️ Violação de privacidade** (visitas sem aviso)
5. **🚨 Multa desproporcional** (12 meses)

**Total esperado: 5 problemas detectados**
""")

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Sobre o Sistema")
    st.markdown("""
    **Funcionalidades:**
    - Análise de 7 cláusulas problemáticas
    - Detecção inteligente de padrões
    - Classificação por gravidade
    - Contexto dos trechos encontrados
    
    **Cláusulas analisadas:**
    - 🚨 Reajuste ilegal
    - 🚨 Garantia dupla
    - 🚨 Benfeitorias
    - ⚠️ Privacidade
    - 🚨 Multa
    - ⚠️ Venda despeja
    - ℹ️ Animais
    """)
    
    st.markdown("---")
    
    if st.session_state.analisado:
        st.markdown("### 📊 Estatísticas da Análise")
        if st.session_state.resultados:
            problemas = st.session_state.resultados['problemas']
            if problemas:
                st.markdown(f"**Total de problemas:** {len(problemas)}")
                
                tipos = {}
                for p in problemas:
                    tipo = p['nome']
                    tipos[tipo] = tipos.get(tipo, 0) + 1
                
                for tipo, count in tipos.items():
                    st.markdown(f"- {tipo}: {count}")
            else:
                st.markdown("✅ Nenhum problema encontrado")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 12px;">
    Burocrata de Bolso v5.0 | Sistema Inteligente de Análise Jurídica © 2024
</div>
""", unsafe_allow_html=True)
