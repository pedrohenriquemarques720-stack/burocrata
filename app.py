import streamlit as st
import pdfplumber
import re
import unicodedata
from datetime import datetime

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------
st.set_page_config(
    page_title="Burocrata de Bolso - Auditor Jurídico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# ESTILOS MINIMALISTAS
# --------------------------------------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    .detected-issue {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 5px solid;
    }
    
    .critical { 
        background-color: #fff5f5; 
        border-left-color: #fc8181;
    }
    
    .medium { 
        background-color: #fffaf0; 
        border-left-color: #f6ad55;
    }
    
    .low { 
        background-color: #f0fff4; 
        border-left-color: #68d391;
    }
    
    .upload-area {
        border: 2px dashed #4a5568;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }
    
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE DETECÇÃO ROBUSTO
# --------------------------------------------------

class SistemaAuditoria:
    def __init__(self):
        self.padroes = {
            'reajuste_ilegal': {
                'regex': [
                    r'reajuste.*?(trimestral|mensal|semestral|bianual|bimestral)',
                    r'reajuste.*?(a cada|cada).*?(3|4|6).*?(mes|mês)',
                    r'reajuste.*?3.*?meses',
                    r'reajuste.*?6.*?meses',
                    r'trimestralmente.*?reajuste'
                ],
                'nome': 'Reajuste Ilegal',
                'gravidade': 'critical',
                'descricao': 'Reajuste deve ser ANUAL (12 meses). Períodos menores são ilegais.',
                'lei': 'Lei 10.192/01'
            },
            'garantia_dupla': {
                'regex': [
                    r'fiador.*?(e|mais|alem).*?(caucao|deposito|seguro)',
                    r'(caucao|deposito|seguro).*?(e|mais|alem).*?fiador',
                    r'exige.*?fiador.*?(caucao|deposito)',
                    r'exige.*?(caucao|deposito).*?fiador',
                    r'fiador.*?caucao',
                    r'caucao.*?fiador'
                ],
                'nome': 'Garantia Dupla Ilegal',
                'gravidade': 'critical',
                'descricao': 'É proibido exigir fiador E caução simultaneamente.',
                'lei': 'Art. 37, Lei 8.245/91'
            },
            'benfeitorias_ilegal': {
                'regex': [
                    r'renuncia.*?(benfeitoria|reforma|obra)',
                    r'nao.*?(indeniza|recebe|tem direito).*?(benfeitoria|reforma|obra)',
                    r'sem.*?direito.*?(benfeitoria|reforma|obra)',
                    r'abre.*?mao.*?(benfeitoria|reforma|obra)'
                ],
                'nome': 'Renúncia Ilegal a Benfeitorias',
                'gravidade': 'critical',
                'descricao': 'Inquilino tem direito a indenização por benfeitorias necessárias.',
                'lei': 'Art. 35, Lei 8.245/91'
            },
            'privacidade_violada': {
                'regex': [
                    r'(qualquer|a qualquer|livre).*?(visita|vistoria|ingresso)',
                    r'sem.*?aviso.*?(visita|vistoria|entrar)',
                    r'visita.*?sem.*?aviso',
                    r'vistoria.*?sem.*?aviso'
                ],
                'nome': 'Violação de Privacidade',
                'gravidade': 'medium',
                'descricao': 'Locador não pode entrar sem aviso prévio e hora combinada.',
                'lei': 'Art. 23, IX, Lei 8.245/91'
            },
            'multa_abusiva': {
                'regex': [
                    r'multa.*?(12|doze).*?meses',
                    r'(12|doze).*?meses.*?multa',
                    r'multa.*?integral.*?aluguel',
                    r'multa.*?total.*?aluguel',
                    r'pagar.*?(12|doze).*?meses.*?multa'
                ],
                'nome': 'Multa Abusiva',
                'gravidade': 'critical',
                'descricao': 'Multa deve ser proporcional. 12 meses é considerada abusiva.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC'
            }
        }
    
    def preparar_texto(self, texto):
        """Prepara texto para análise"""
        if not texto:
            return ""
        
        # Remove acentos e normaliza
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        
        # Converte para minúscula e remove espaços extras
        texto = texto.lower()
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto
    
    def analisar_contrato(self, texto):
        """Analisa contrato e retorna problemas encontrados"""
        texto_preparado = self.preparar_texto(texto)
        problemas = []
        
        for chave, config in self.padroes.items():
            encontrado = False
            contexto = ""
            
            for padrao in config['regex']:
                try:
                    match = re.search(padrao, texto_preparado, re.IGNORECASE)
                    if match:
                        encontrado = True
                        # Extrair contexto
                        inicio = max(0, match.start() - 100)
                        fim = min(len(texto_preparado), match.end() + 100)
                        contexto = texto_preparado[inicio:fim]
                        break
                except:
                    continue
            
            if encontrado:
                problemas.append({
                    'id': chave,
                    'nome': config['nome'],
                    'gravidade': config['gravidade'],
                    'descricao': config['descricao'],
                    'lei': config['lei'],
                    'contexto': f"...{contexto}..." if contexto else ""
                })
        
        return problemas
    
    def calcular_score(self, problemas):
        """Calcula score de conformidade"""
        if not problemas:
            return 100
        
        penalidade = 0
        for problema in problemas:
            if problema['gravidade'] == 'critical':
                penalidade += 20
            elif problema['gravidade'] == 'medium':
                penalidade += 10
            else:
                penalidade += 5
        
        return max(100 - penalidade, 0)

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def extrair_texto_pdf(arquivo):
    """Extrai texto de arquivo PDF"""
    try:
        with pdfplumber.open(arquivo) as pdf:
            texto = ""
            for pagina in pdf.pages:
                conteudo = pagina.extract_text() or ""
                texto += conteudo + "\n"
            return texto
    except Exception as e:
        st.error(f"Erro ao extrair texto: {str(e)}")
        return ""

def obter_cor_score(score):
    """Retorna cor baseada no score"""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    else:
        return "red"

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

def main():
    # Cabeçalho
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ BUROCRATA DE BOLSO</h1>
        <p>Sistema Inteligente de Auditoria de Contratos</p>
        <p style="font-size: 0.9em; opacity: 0.9;">Versão 7.0 - Foco em Resultados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    auditoria = SistemaAuditoria()
    
    # Área de upload
    st.markdown("### 📄 CARREGUE SEU CONTRATO")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        arquivo = st.file_uploader(
            "Selecione o contrato em PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )
    
    if arquivo:
        # Processar arquivo
        with st.spinner("🔍 Analisando contrato..."):
            # Extrair texto
            texto_contrato = extrair_texto_pdf(arquivo)
            
            if texto_contrato:
                # Analisar contrato
                problemas = auditoria.analisar_contrato(texto_contrato)
                score = auditoria.calcular_score(problemas)
                
                # Resultados
                st.markdown("---")
                
                # Score Card
                col_score, col_problems = st.columns([1, 2])
                
                with col_score:
                    st.markdown("### 📊 ÍNDICE DE CONFORMIDADE")
                    cor = obter_cor_score(score)
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border-radius: 10px;">
                        <h1 style="color: {cor}; margin: 0;">{score}/100</h1>
                        <p style="margin: 5px 0 0 0; font-weight: bold;">
                            {'✅ EXCELENTE' if score >= 80 else '⚠️ ATENÇÃO' if score >= 60 else '🚨 CRÍTICO'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(score/100)
                    
                    # Estatísticas
                    crit = sum(1 for p in problemas if p['gravidade'] == 'critical')
                    med = sum(1 for p in problemas if p['gravidade'] == 'medium')
                    low = sum(1 for p in problemas if p['gravidade'] == 'low')
                    
                    st.metric("🚨 Críticos", crit)
                    st.metric("⚠️ Médios", med)
                    st.metric("ℹ️ Leves", low)
                
                with col_problems:
                    if problemas:
                        st.markdown("### 🚨 PROBLEMAS DETECTADOS")
                        
                        # Agrupar por gravidade
                        problemas_criticos = [p for p in problemas if p['gravidade'] == 'critical']
                        problemas_medios = [p for p in problemas if p['gravidade'] == 'medium']
                        problemas_leves = [p for p in problemas if p['gravidade'] == 'low']
                        
                        # Mostrar problemas críticos primeiro
                        for problema in problemas_criticos + problemas_medios + problemas_leves:
                            gravidade_class = {
                                'critical': 'critical',
                                'medium': 'medium', 
                                'low': 'low'
                            }[problema['gravidade']]
                            
                            emoji = {
                                'critical': '🚨',
                                'medium': '⚠️',
                                'low': 'ℹ️'
                            }[problema['gravidade']]
                            
                            st.markdown(f"""
                            <div class="detected-issue {gravidade_class}">
                                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                    <span style="font-size: 1.5em; margin-right: 10px;">{emoji}</span>
                                    <h4 style="margin: 0;">{problema['nome']}</h4>
                                </div>
                                <p><strong>Descrição:</strong> {problema['descricao']}</p>
                                <p><strong>Base Legal:</strong> {problema['lei']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if problema.get('contexto'):
                                with st.expander("📝 Ver trecho do contrato"):
                                    st.text(problema['contexto'])
                        
                        # Resumo
                        st.markdown(f"### 📋 RESUMO DA AUDITORIA")
                        st.markdown(f"""
                        - **Total de problemas:** {len(problemas)}
                        - **Críticos:** {len(problemas_criticos)}
                        - **Médios:** {len(problemas_medios)}
                        - **Leves:** {len(problemas_leves)}
                        """)
                        
                        # Recomendações
                        if problemas_criticos:
                            st.markdown("""
                            ### ⚠️ RECOMENDAÇÕES URGENTES
                            1. **NEGOCIAR** as cláusulas críticas antes de assinar
                            2. **BUSCAR ASSESSORIA JURÍDICA** especializada
                            3. **NÃO ASSINAR** sem corrigir as irregularidades críticas
                            """)
                    else:
                        st.markdown("""
                        <div style="text-align: center; padding: 40px; background-color: #f0fff4; border-radius: 10px;">
                            <h2 style="color: #276749;">✅ CONTRATO REGULAR</h2>
                            <p style="font-size: 1.1em;">Nenhuma irregularidade grave detectada nas cláusulas analisadas.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Informações adicionais
                st.markdown("---")
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.markdown("### 📈 ESTATÍSTICAS")
                    st.markdown(f"""
                    - Texto analisado: {len(texto_contrato):,} caracteres
                    - Padrões verificados: {len(auditoria.padroes)}
                    - Tempo de análise: Instantâneo
                    """)
                
                with col_info2:
                    st.markdown("### ⚖️ LEGISLAÇÃO APLICÁVEL")
                    st.markdown("""
                    - Lei 8.245/91 (Lei do Inquilinato)
                    - Lei 10.192/01 (Reajustes)
                    - Código de Defesa do Consumidor
                    - Jurisprudência do STJ
                    """)
                
                with col_info3:
                    st.markdown("### 🔒 SEGURANÇA")
                    st.markdown("""
                    - Processamento local
                    - Nenhum dado armazenado
                    - Análise em tempo real
                    - Sem registro de informações
                    """)
            
            else:
                st.error("❌ Não foi possível extrair texto do PDF. Verifique se o arquivo não está protegido ou corrompido.")
    
    else:
        # Tela inicial
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h2>🎯 COMO FUNCIONA</h2>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 30px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>1. 📤 UPLOAD</h3>
                    <p>Carregue seu contrato em PDF</p>
                </div>
                <div style="flex: 1; min-width: 200px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>2. 🔍 ANÁLISE</h3>
                    <p>Sistema analisa automaticamente</p>
                </div>
                <div style="flex: 1; min-width: 200px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>3. 📊 RESULTADO</h3>
                    <p>Relatório completo com problemas</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Áreas de atuação
        st.markdown("---")
        st.markdown("### ⚖️ ÁREAS DE ATUAÇÃO")
        
        col_area1, col_area2, col_area3, col_area4 = st.columns(4)
        
        with col_area1:
            st.markdown("""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; border-radius: 8px;">
                <h4>🏠 LOCAÇÃO</h4>
                <p>Contratos residenciais</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_area2:
            st.markdown("""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); color: white; border-radius: 8px;">
                <h4>⚖️ SERVIÇOS</h4>
                <p>Prestação de serviços</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_area3:
            st.markdown("""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #38a169 0%, #2f855a 100%); color: white; border-radius: 8px;">
                <h4>💰 COMPRA/VENDA</h4>
                <p>Imóveis e bens</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_area4:
            st.markdown("""
            <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%); color: white; border-radius: 8px;">
                <h4>🧾 FISCAL</h4>
                <p>Notas fiscais</p>
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------
st.markdown("""
<footer style="text-align: center; padding: 20px; margin-top: 40px; color: #718096; font-size: 0.9em;">
    <hr style="border: none; height: 1px; background: #e2e8f0; margin: 20px 0;">
    <p>BUROCRATA DE BOLSO | Sistema de Auditoria Jurídica © 2024</p>
    <p><small>Este sistema fornece análise automática baseada em padrões. Não substitui consulta jurídica profissional.</small></p>
</footer>
""", unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
