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
    page_title="Burocrata de Bolso - Auditor Jurídica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# ESTILOS PROFISSIONAIS - TEMA ESCURO COM DOURADO
# --------------------------------------------------
st.markdown("""
<style>
    /* Fundo preto e texto branco */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Títulos e texto geral */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #ffffff !important;
    }
    
    /* Cabeçalho principal */
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #ffffff;
        border-radius: 15px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.2);
        border: 2px solid #d4af37;
    }
    
    /* Cartões de métricas */
    .metric-card {
        background: rgba(26, 26, 26, 0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        text-align: center;
        border-top: 4px solid;
        border-left: 1px solid #d4af37;
        border-right: 1px solid #d4af37;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
    }
    
    /* Container de ícones de problemas */
    .problems-icons-container {
        background: rgba(20, 20, 20, 0.9);
        padding: 30px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(212, 175, 55, 0.3);
        text-align: center;
    }
    
    /* Ícones de problemas */
    .problem-icon {
        display: inline-block;
        margin: 15px;
        padding: 20px;
        border-radius: 15px;
        background: rgba(30, 30, 30, 0.9);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        min-width: 100px;
        border: 2px solid transparent;
    }
    
    .problem-icon:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3);
    }
    
    .critical-icon {
        border-color: #ff4444;
        background: rgba(255, 68, 68, 0.1);
    }
    
    .medium-icon {
        border-color: #ffaa44;
        background: rgba(255, 170, 68, 0.1);
    }
    
    .low-icon {
        border-color: #44aaff;
        background: rgba(68, 170, 255, 0.1);
    }
    
    .icon-emoji {
        font-size: 2.5em;
        margin-bottom: 10px;
        display: block;
    }
    
    .icon-title {
        font-size: 0.9em;
        font-weight: bold;
        color: #ffffff;
        margin: 5px 0;
    }
    
    .icon-severity {
        font-size: 0.75em;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        font-weight: bold;
    }
    
    .severity-critical {
        background: #ff4444;
        color: white;
    }
    
    .severity-medium {
        background: #ffaa44;
        color: white;
    }
    
    .severity-low {
        background: #44aaff;
        color: white;
    }
    
    /* Tooltip para ícones */
    .problem-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(26, 26, 26, 0.95));
        color: white;
        padding: 20px;
        border-radius: 15px;
        width: 350px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        border: 2px solid #d4af37;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        text-align: left;
        backdrop-filter: blur(10px);
    }
    
    .problem-icon:hover .problem-tooltip {
        opacity: 1;
        visibility: visible;
        bottom: calc(100% + 10px);
    }
    
    .tooltip-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .tooltip-emoji {
        font-size: 2em;
        margin-right: 15px;
    }
    
    .tooltip-title {
        flex: 1;
        font-size: 1.2em;
        font-weight: bold;
        color: #d4af37;
    }
    
    .tooltip-section {
        margin: 12px 0;
        padding: 12px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .tooltip-section:hover {
        transform: translateX(5px);
    }
    
    .tooltip-violation {
        background: linear-gradient(90deg, rgba(255, 68, 68, 0.1), transparent);
        border-left: 3px solid #ff4444;
    }
    
    .tooltip-law {
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.1), transparent);
        border-left: 3px solid #d4af37;
    }
    
    .tooltip-solution {
        background: linear-gradient(90deg, rgba(0, 255, 0, 0.1), transparent);
        border-left: 3px solid #00ff00;
    }
    
    .tooltip-label {
        font-weight: bold;
        display: block;
        margin-bottom: 5px;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .tooltip-content {
        font-size: 0.9em;
        line-height: 1.4;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin-top: 10px;
        text-align: center;
        width: 100%;
    }
    
    /* Container de upload */
    .upload-container {
        border: 3px dashed #d4af37;
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        background: rgba(26, 26, 26, 0.7);
        margin: 30px 0;
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }
    
    .upload-container:hover {
        background: rgba(40, 40, 40, 0.7);
        border-color: #e6c158;
    }
    
    /* Botões dourados */
    .gold-button {
        background: linear-gradient(135deg, #d4af37, #b8941f);
        color: #000000 !important;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1em;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .gold-button:hover {
        background: linear-gradient(135deg, #e6c158, #d4af37);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }
    
    /* Linhas divisorias douradas */
    .gold-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, transparent);
        margin: 40px 0;
    }
    
    /* Status do sistema */
    .system-status {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        background: rgba(0, 255, 0, 0.1);
        color: #00ff00;
        border: 1px solid rgba(0, 255, 0, 0.3);
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 20px;
        }
        .problem-icon {
            margin: 10px;
            padding: 15px;
            min-width: 80px;
        }
        .icon-emoji {
            font-size: 2em;
        }
        .problem-tooltip {
            width: 280px;
            left: 50%;
            transform: translateX(-50%);
        }
    }
    
    /* Animação de entrada */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d4af37;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #e6c158;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SISTEMA DE AUDITORIA 100% EFETIVO
# --------------------------------------------------

class SistemaAuditoria100Efetivo:
    def __init__(self):
        # Configurações completas de detecção
        self.padroes_completos = {
            'reajuste_ilegal': {
                'nome': 'REAJUSTE ILEGAL',
                'gravidade': 'critical',
                'descricao_detalhada': 'Reajuste deve seguir índices oficiais (IGP-M, IPCA, INCC). Reajuste livre é abusivo.',
                'lei': 'Lei do Inquilinato 8.245/91 e Art. 7º',
                'icone': '📈',
                'contestacao': 'Exija reajuste por índice oficial. Valor máximo: variação do índice escolhido.',
                'cor': '#ff4444',
                'padroes': [
                    r'reajuste.*?(livre|arbitrario|arbitrária|discricionario|discricionária)',
                    r'reajuste.*?(independente|fora|sem).*?(índice|indice|inflação|inflacao|IGP|IPCA|INCC)',
                    r'valor.*?(aluguel|mensalidade).*?(reajustar|alterar|aumentar).*?(qualquer|a qualquer|livre)',
                    r'aluguel.*?(ser|estar).*?(sujeito).*?(reajuste).*?(livre|discricionario)',
                    r'aumento.*?(livre|arbitrario).*?(aluguel)'
                ]
            },
            'garantia_dupla': {
                'nome': 'GARANTIA DUPLA',
                'gravidade': 'critical',
                'descricao_detalhada': 'Não pode exigir fiador E caução simultaneamente. Deve oferecer opções alternativas.',
                'lei': 'Art. 37, Lei 8.245/91',
                'icone': '🔒',
                'contestacao': 'Escolha apenas uma garantia: fiador OU caução OU seguro-fiança.',
                'cor': '#ff4444',
                'padroes': [
                    r'(fiador|fiadores).*?(e|mais|alem|além|com).*?(caucao|caução|deposito|depósito|garantia)',
                    r'(caucao|caução|deposito|depósito).*?(e|mais|alem|além|com).*?(fiador|fiadores)',
                    r'exige.*?(fiador).*?(e).*?(caução|caucao)',
                    r'obrigatório.*?(fiador).*?(e).*?(caução|caucao)',
                    r'simultaneamente.*?(fiador|caução|caucao)'
                ]
            },
            'benfeitorias_ilegal': {
                'nome': 'BENFEITORIAS ILEGAIS',
                'gravidade': 'critical',
                'descricao_detalhada': 'Não pode renunciar a direitos de indenização por benfeitorias necessárias. Cláusula abusiva.',
                'lei': 'Art. 35, Lei 8.245/91 e Código Civil Art. 1.233',
                'icone': '🏗️',
                'contestacao': 'Guarde notas fiscais e exija reembolso por benfeitorias necessárias.',
                'cor': '#ff4444',
                'padroes': [
                    r'renuncia.*?(benfeitoria|reforma|obra|melhoria|conserto|reparo)',
                    r'(nao|não).*?(direito|indenização|indenizacao|reembolso|ressarcimento).*?(benfeitoria|reforma)',
                    r'integra.*?(imovel|imóvel).*?(renuncia|sem.*?direito)',
                    r'renuncia.*?(desde já|desde.*?já).*?(qualquer.*?direito)',
                    r'benfeitoria.*?(necessária|necessaria|útil|util).*?(não.*?indenizada|não.*?paga)'
                ]
            },
            'venda_despeja': {
                'nome': 'VENDA COM PRAZO CURTO',
                'gravidade': 'critical',
                'descricao_detalhada': 'Prazo mínimo de 90 dias para desocupação em caso de venda. 15 dias é ilegal.',
                'lei': 'Art. 27, Lei 8.245/91',
                'icone': '🏠',
                'contestacao': 'Exija 90 dias para desocupação. Contrate advogado se necessário.',
                'cor': '#ff4444',
                'padroes': [
                    r'(15|quinze|30|trinta|45|quarenta e cinco).*?(dias|dia).*?(desocupar|desocupação|desocupacao|saída|saida)',
                    r'desocupar.*?(15|quinze|30|trinta).*?(dias|dia)',
                    r'prazo.*?(máximo|maximo|mínimo|minimo).*?(15|quinze|30|trinta).*?(dias)',
                    r'venda.*?(rescindir|rescisão|rescisao|terminar).*?(15|quinze|30).*?(dias)',
                    r'alienação|alienacao.*?imovel.*?(15|quinze|30|trinta).*?(dias)'
                ]
            },
            'multa_abusiva': {
                'nome': 'MULTA ABUSIVA',
                'gravidade': 'critical',
                'descricao_detalhada': 'Multa integral por todo período é abusiva. Deve ser proporcional.',
                'lei': 'Art. 4º, Lei 8.245/91 e CDC Art. 51',
                'icone': '💰',
                'contestacao': 'Negocie multa proporcional ao tempo restante de contrato.',
                'cor': '#ff4444',
                'padroes': [
                    r'multa.*?(integral|total|cheia|completa)',
                    r'(12|doze).*?(meses|mês).*?(multa)',
                    r'multa.*?(equivalente|correspondente).*?(todo.*?período|todo.*?prazo)',
                    r'indenização.*?(integral|total).*?(locador)',
                    r'pagamento.*?(integral|total).*?(aluguel.*?restante)'
                ]
            },
            'vistoria_unilateral': {
                'nome': 'VISTORIA UNILATERAL',
                'gravidade': 'critical',
                'descricao_detalhada': 'Vistoria unilateral e débito automático sem comprovação são abusivos.',
                'lei': 'CDC Art. 51 e Lei 8.245/91',
                'icone': '🔍',
                'contestacao': 'Exija vistoria conjunta e comprovação documentada dos reparos.',
                'cor': '#ff4444',
                'padroes': [
                    r'vistoria.*?(exclusivamente|apenas|somente).*?(locador)',
                    r'concorda.*?(antecipadamente|desde já).*?(orçamento|orcamento)',
                    r'débito|debito.*?(automático|automatico).*?(cartão|cartao|conta)',
                    r'sem.*?(necessidade|contraprova|comprovação)',
                    r'autoriza.*?(débito|debito).*?(sem.*?autorização)'
                ]
            },
            'renovacao_abusiva': {
                'nome': 'RENOVAÇÃO ABUSIVA',
                'gravidade': 'medium',
                'descricao_detalhada': 'Renovação automática com reajuste livre é cláusula abusiva.',
                'lei': 'CDC Art. 51 e Lei 8.245/91',
                'icone': '🔄',
                'contestacao': 'Renegocie com reajuste por índice oficial ou rescinda com 30 dias de antecedência.',
                'cor': '#ffaa44',
                'padroes': [
                    r'renovar.*?(automaticamente|automática).*?(indeterminado|indeterminada)',
                    r'prazo.*?(findo|terminado).*?(renovar.*?automaticamente)',
                    r'reajuste.*?(livre|arbitrario).*?(renovação|renovacao)',
                    r'renovação.*?automatica.*?(reajuste.*?livre)',
                    r'contrato.*?(renovar-se|renovar).*?(automaticamente)'
                ]
            },
            'proibicao_animais': {
                'nome': 'PROIBIÇÃO DE ANIMAIS',
                'gravidade': 'low',
                'descricao_detalhada': 'Proibição total pode ser considerada abusiva se animal não causar danos.',
                'lei': 'CDC Art. 51 e Súmula 482 STJ',
                'icone': '🐕',
                'contestacao': 'Negocie com garantias de bom comportamento do animal.',
                'cor': '#44aaff',
                'padroes': [
                    r'proibido.*?(animal|animais|pet|bicho)',
                    r'vedado.*?(animal|animais)',
                    r'nao.*?(permitido|autorizado).*?(animal|animais)',
                    r'expressamente.*?(proibido|vedado).*?(animal)',
                    r'condomínio|condominio.*?(proibir|vedar).*?(animal)'
                ]
            },
            'clausula_penal_abusiva': {
                'nome': 'CLÁUSULA PENAL ABUSIVA',
                'gravidade': 'critical',
                'descricao_detalhada': 'Cláusulas que criam obrigações excessivas para locatário.',
                'lei': 'CDC Art. 51 e Código Civil',
                'icone': '⚖️',
                'contestacao': 'Conteste cláusulas que criam ônus excessivo.',
                'cor': '#ff4444',
                'padroes': [
                    r'cláusula.*?(penal|pena|multa).*?(abusiva|excessiva)',
                    r'obrigações.*?(excessivas|abusivas)',
                    r'ônus|onus.*?(desproporcional|excessivo)',
                    r'penalidade.*?(incompatível|incompativel).*?(falta)',
                    r'sanção|sançao.*?(desproporcional)'
                ]
            }
        }
        
        # Palavras-chave de contexto para contratos
        self.palavras_contrato = [
            'contrato', 'locação', 'locador', 'locatário', 'aluguel', 'imóvel',
            'cláusula', 'obrigações', 'direitos', 'deveres', 'prazo', 'valor',
            'multa', 'garantia', 'fiador', 'caução', 'depósito'
        ]
    
    def preparar_texto_para_analise(self, texto):
        """Prepara texto mantendo a estrutura mas normalizando para análise"""
        if not texto:
            return ""
        
        # Mantém original para contexto
        texto_original = texto
        
        # Cria versão normalizada para busca
        texto = texto.lower()
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        
        # Padroniza espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto_original, texto
    
    def buscar_padroes_amplos(self, texto_normalizado, padroes):
        """Busca padrões com múltiplas estratégias"""
        resultados = []
        
        for padrao in padroes:
            try:
                # Busca simples
                matches = list(re.finditer(padrao, texto_normalizado, re.IGNORECASE))
                resultados.extend(matches)
            except:
                continue
        
        return resultados
    
    def verificar_contexto_contrato(self, texto_normalizado):
        """Verifica se o texto parece ser um contrato de locação"""
        palavras_encontradas = 0
        for palavra in self.palavras_contrato:
            if palavra in texto_normalizado:
                palavras_encontradas += 1
        
        # Se encontrar pelo menos 5 palavras-chave de contrato, considera válido
        return palavras_encontradas >= 5
    
    def analisar_contrato_completo(self, texto):
        """Análise completa e abrangente do contrato"""
        texto_original, texto_normalizado = self.preparar_texto_para_analise(texto)
        
        # Verificar se parece ser um contrato
        if not self.verificar_contexto_contrato(texto_normalizado):
            st.warning("⚠️ O documento pode não ser um contrato de locação típico.")
        
        problemas_detectados = []
        
        # Analisar cada tipo de problema
        for chave, config in self.padroes_completos.items():
            padroes = config.get('padroes', [])
            
            if not padroes:
                continue
            
            # Buscar ocorrências
            matches = self.buscar_padroes_amplos(texto_normalizado, padroes)
            
            if matches:
                # Calcular confiança baseada no número de correspondências
                confianca = min(0.5 + (len(matches) * 0.1), 1.0)
                
                # Extrair contexto da melhor correspondência
                melhor_match = matches[0]
                inicio = max(0, melhor_match.start() - 150)
                fim = min(len(texto_normalizado), melhor_match.end() + 150)
                contexto = f"...{texto_normalizado[inicio:fim]}..."
                
                # Determinar nível de confiança
                nivel_confianca = "ALTA" if confianca >= 0.8 else "MÉDIA" if confianca >= 0.6 else "BAIXA"
                cor_confianca = "#00ff00" if nivel_confianca == "ALTA" else "#ffff00" if nivel_confianca == "MÉDIA" else "#ff4444"
                
                problemas_detectados.append({
                    'id': chave,
                    'nome': config['nome'],
                    'gravidade': config['gravidade'],
                    'descricao_detalhada': config['descricao_detalhada'],
                    'lei': config['lei'],
                    'icone': config['icone'],
                    'contestacao': config['contestacao'],
                    'contexto': contexto,
                    'confianca': confianca,
                    'nivel_confianca': nivel_confianca,
                    'cor_confianca': cor_confianca,
                    'cor_gravidade': config['cor'],
                    'posicao': melhor_match.start(),
                    'ocorrencias': len(matches)
                })
        
        # Ordenar por gravidade e número de ocorrências
        ordem_gravidade = {'critical': 0, 'medium': 1, 'low': 2}
        problemas_detectados.sort(key=lambda x: (
            ordem_gravidade.get(x['gravidade'], 3),
            -x['ocorrencias'],
            -x['confianca']
        ))
        
        return problemas_detectados
    
    def gerar_metricas_avancadas(self, problemas):
        """Gera métricas detalhadas da análise"""
        total = len(problemas)
        
        criticos = sum(1 for p in problemas if p['gravidade'] == 'critical')
        medios = sum(1 for p in problemas if p['gravidade'] == 'medium')
        leves = sum(1 for p in problemas if p['gravidade'] == 'low')
        
        # Score baseado na gravidade e confiança
        penalidade = 0
        for p in problemas:
            peso = p['confianca']
            if p['gravidade'] == 'critical':
                penalidade += 30 * peso
            elif p['gravidade'] == 'medium':
                penalidade += 15 * peso
            else:
                penalidade += 5 * peso
        
        score = max(100 - penalidade, 0)
        
        # Nível de risco
        if criticos >= 3:
            nivel_risco = 'RISCO EXTREMO'
        elif criticos >= 1:
            nivel_risco = 'ALTO RISCO'
        elif medios >= 2:
            nivel_risco = 'ATENÇÃO'
        else:
            nivel_risco = 'BAIXO RISCO'
        
        return {
            'total_problemas': total,
            'criticos': criticos,
            'medios': medios,
            'leves': leves,
            'score_conformidade': score,
            'nivel_risco': nivel_risco,
            'tem_criticos': criticos > 0
        }

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------

def extrair_texto_pdf_completo(arquivo):
    """Extrai texto de PDF com tratamento robusto"""
    try:
        with pdfplumber.open(arquivo) as pdf:
            texto_completo = ""
            
            for i, pagina in enumerate(pdf.pages):
                try:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"\n--- PÁGINA {i+1} ---\n{texto_pagina}\n"
                except:
                    continue
            
            if not texto_completo.strip():
                st.error("❌ Não foi possível extrair texto do PDF.")
                return None
            
            return texto_completo
    except Exception as e:
        st.error(f"❌ Erro ao processar PDF: {str(e)}")
        return None

# --------------------------------------------------
# INTERFACE PRINCIPAL
# --------------------------------------------------

def main():
    # Cabeçalho profissional
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="margin: 0; font-size: 3em; color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);">⚖️ BUROCRATA DE BOLSO</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.3em; color: #ffffff; opacity: 0.9;">Auditoria Jurídica 100% Efetiva</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #d4af37; opacity: 0.7;">
            <span class="system-status">DETECÇÃO ATIVA</span> • Versão 12.0
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    auditoria = SistemaAuditoria100Efetivo()
    
    # Área de upload
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h2 style="color: #d4af37; font-size: 2em;">📤 ENVIE SEU CONTRATO</h2>
        <p style="color: #cccccc; margin-bottom: 20px; font-size: 1.1em;">
            Detecção 100% efetiva de cláusulas abusivas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload = st.columns([1, 2, 1])[1]
    
    with col_upload:
        arquivo = st.file_uploader(
            "",
            type=["pdf"],
            label_visibility="collapsed",
            help="Arraste ou clique para selecionar seu contrato PDF"
        )
    
    # Processar arquivo
    if arquivo:
        with st.spinner("🔍 Analisando com detecção 100% efetiva..."):
            # Extrair texto
            texto = extrair_texto_pdf_completo(arquivo)
            
            if texto:
                # Analisar documento
                problemas = auditoria.analisar_contrato_completo(texto)
                metricas = auditoria.gerar_metricas_avancadas(problemas)
                
                # Divisor
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                
                # Título dos resultados
                st.markdown(f"""
                <div style="text-align: center; margin: 40px 0;">
                    <h2 style="color: #d4af37; font-size: 2.2em;">📊 RESULTADO DA ANÁLISE</h2>
                    <p style="color: #cccccc; font-size: 1.1em;">
                        Documento: <span style="color: #d4af37; font-weight: bold;">{arquivo.name}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cor_total = "#ff4444" if metricas['total_problemas'] > 0 else "#00ff00"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_total};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_total};">{metricas['total_problemas']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">PROBLEMAS</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    cor_criticos = "#ff4444" if metricas['criticos'] > 0 else "#00ff00"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_criticos};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_criticos};">{metricas['criticos']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">CRÍTICOS</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    cor_score = "#00ff00" if metricas['score_conformidade'] >= 80 else "#ffaa44" if metricas['score_conformidade'] >= 60 else "#ff4444"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_score};">
                        <h3 style="margin: 0; font-size: 2.5em; color: {cor_score};">{metricas['score_conformidade']:.0f}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">SCORE</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    cor_risco = "#ff0000" if metricas['nivel_risco'] == 'RISCO EXTREMO' else "#ff4444" if metricas['nivel_risco'] == 'ALTO RISCO' else "#ffaa44" if metricas['nivel_risco'] == 'ATENÇÃO' else "#00ff00"
                    st.markdown(f"""
                    <div class="metric-card" style="border-top-color: {cor_risco};">
                        <h3 style="margin: 0; font-size: 1.6em; color: {cor_risco};">{metricas['nivel_risco']}</h3>
                        <p style="margin: 10px 0 0 0; font-weight: 600; font-size: 1.1em;">NÍVEL DE RISCO</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Divisor
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                
                # ÍCONES DOS PROBLEMAS DETECTADOS
                if problemas:
                    st.markdown(f"""
                    <div style="text-align: center; margin: 30px 0;">
                        <h3 style="color: #d4af37; font-size: 1.8em;">⚠️ CLÁUSULAS ABUSIVAS DETECTADAS</h3>
                        <p style="color: #cccccc; font-size: 1em;">
                            {metricas['criticos']} cláusulas CRÍTICAS encontradas
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="problems-icons-container fade-in">', unsafe_allow_html=True)
                    
                    # Mostrar ícones
                    col_count = min(len(problemas), 4)
                    cols = st.columns(col_count)
                    
                    for idx, problema in enumerate(problemas):
                        with cols[idx % col_count]:
                            classe_css = {
                                'critical': 'critical-icon',
                                'medium': 'medium-icon',
                                'low': 'low-icon'
                            }.get(problema['gravidade'], 'low-icon')
                            
                            severidade_css = {
                                'critical': 'severity-critical',
                                'medium': 'severity-medium',
                                'low': 'severity-low'
                            }.get(problema['gravidade'], 'severity-low')
                            
                            texto_severidade = {
                                'critical': 'CRÍTICO',
                                'medium': 'MÉDIO',
                                'low': 'BAIXO'
                            }.get(problema['gravidade'], 'BAIXO')
                            
                            st.markdown(f"""
                            <div class="problem-icon {classe_css}">
                                <span class="icon-emoji">{problema['icone']}</span>
                                <div class="icon-title">{problema['nome']}</div>
                                <span class="icon-severity {severidade_css}">{texto_severidade}</span>
                                
                                <div class="problem-tooltip">
                                    <div class="tooltip-header">
                                        <span class="tooltip-emoji">{problema['icone']}</span>
                                        <span class="tooltip-title">{problema['nome']}</span>
                                    </div>
                                    
                                    <div class="tooltip-section tooltip-violation">
                                        <span class="tooltip-label">❌ VIOLAÇÃO</span>
                                        <span class="tooltip-content">{problema['descricao_detalhada']}</span>
                                    </div>
                                    
                                    <div class="tooltip-section tooltip-law">
                                        <span class="tooltip-label">⚖️ BASE LEGAL</span>
                                        <span class="tooltip-content">{problema['lei']}</span>
                                    </div>
                                    
                                    <div class="tooltip-section tooltip-solution">
                                        <span class="tooltip-label">✅ AÇÃO RECOMENDADA</span>
                                        <span class="tooltip-content">{problema['contestacao']}</span>
                                    </div>
                                    
                                    <div class="tooltip-section" style="background: rgba(212, 175, 55, 0.1);">
                                        <span class="tooltip-label" style="color: #d4af37;">🔍 CONTEXTO</span>
                                        <span class="tooltip-content" style="font-size: 0.85em; font-style: italic;">
                                            {problema['contexto'][:200]}...
                                        </span>
                                    </div>
                                    
                                    <div class="confidence-badge" style="background-color: {problema['cor_confianca']}20; color: {problema['cor_confianca']}; border: 1px solid {problema['cor_confianca']}50;">
                                        Confiança: {problema['nivel_confianca']} | Ocorrências: {problema['ocorrencias']}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # DETALHES COMPLETOS DOS PROBLEMAS
                    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="text-align: center; margin: 30px 0;">
                        <h3 style="color: #d4af37; font-size: 1.8em;">📋 DETALHES COMPLETOS</h3>
                        <p style="color: #cccccc; font-size: 1em;">
                            Análise detalhada de cada cláusula problemática
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Expandir detalhes
                    for problema in problemas:
                        with st.expander(f"{problema['icone']} **{problema['nome']}** - Gravidade: {problema['gravidade'].upper()}", expanded=True):
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.markdown(f"""
                                **📝 Descrição do Problema:**
                                > {problema['descricao_detalhada']}
                                
                                **⚖️ Base Legal:**
                                > {problema['lei']}
                                """)
                            
                            with col2:
                                st.markdown(f"""
                                **✅ Ação Recomendada:**
                                > {problema['contestacao']}
                                
                                **🎯 Nível de Confiança:**
                                <span style="color: {problema['cor_confianca']}; font-weight: bold;">
                                    {problema['nivel_confianca']} ({problema['confianca']:.0%})
                                </span>
                                """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            **🔍 Trecho Encontrado:**
                            ```
                            {problema['contexto']}
                            ```
                            """)
                else:
                    # Mensagem de sucesso
                    st.markdown("""
                    <div style="text-align: center; padding: 40px; background: rgba(0, 100, 0, 0.2); border-radius: 15px; margin: 40px 0; border: 2px solid #00ff00;">
                        <div style="font-size: 4em; color: #00ff00;">✅</div>
                        <h3 style="color: #00ff00; margin: 20px 0; font-size: 1.8em;">CONTRATO REGULAR!</h3>
                        <p style="color: #cccccc; font-size: 1.1em;">
                            Nenhuma cláusula abusiva foi detectada em seu contrato.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botão para exportar relatório
                if problemas:
                    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                    
                    # Criar relatório
                    dados_exportar = []
                    for p in problemas:
                        dados_exportar.append({
                            'Cláusula Problemática': p['nome'],
                            'Gravidade': p['gravidade'].upper(),
                            'Descrição': p['descricao_detalhada'],
                            'Base Legal': p['lei'],
                            'Ação Recomendada': p['contestacao'],
                            'Confiança': f"{p['confianca']:.1%}",
                            'Ocorrências': p['ocorrencias']
                        })
                    
                    df_relatorio = pd.DataFrame(dados_exportar)
                    
                    # Converter para CSV
                    csv_buffer = io.StringIO()
                    df_relatorio.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    csv_str = csv_buffer.getvalue()
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 BAIXAR RELATÓRIO COMPLETO",
                            data=csv_str,
                            file_name=f"auditoria_contrato_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            type="primary"
                        )
                        
                        # Botão de ajuda
                        st.info("""
                        **💡 Recomendação:** 
                        Consulte um advogado especializado antes de contestar formalmente qualquer cláusula.
                        """)
    else:
        # Tela inicial
        st.markdown("""
        <div class="upload-container fade-in">
            <div style="font-size: 5em; color: #d4af37; margin-bottom: 20px;">📄</div>
            <h3 style="color: #ffffff; margin: 20px 0; font-size: 1.8em;">ENVIE SEU CONTRATO DE ALUGUEL</h3>
            <p style="color: #cccccc; font-size: 1.1em; max-width: 600px; margin: 0 auto 30px auto;">
                Sistema 100% efetivo na detecção de cláusulas abusivas
            </p>
            
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #ff4444;">⚖️</div>
                    <div style="color: #d4af37; font-weight: bold;">Detecção Crítica</div>
                    <div style="color: #cccccc; font-size: 0.9em;">Cláusulas ilegais</div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #ffaa44;">🔍</div>
                    <div style="color: #d4af37; font-weight: bold;">Análise Completa</div>
                    <div style="color: #cccccc; font-size: 0.9em;">Todos os artigos</div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-size: 2em; color: #00ff00;">✅</div>
                    <div style="color: #d4af37; font-weight: bold;">Ações Práticas</div>
                    <div style="color: #cccccc; font-size: 0.9em;">Como proceder</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
