<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacidade - Ícones Interativos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .privacy-container {
            width: 100%;
            max-width: 400px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .privacy-header {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .privacy-header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        .privacy-widget {
            padding: 30px;
        }
        
        .privacy-details {
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .privacy-details:hover {
            border-color: #6a11cb;
            box-shadow: 0 5px 15px rgba(106, 17, 203, 0.1);
        }
        
        .privacy-details[open] {
            border-color: #6a11cb;
        }
        
        .privacy-summary {
            list-style: none;
            cursor: pointer;
            padding: 20px;
            background: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s ease;
        }
        
        .privacy-summary:hover {
            background: #f8f9ff;
        }
        
        .privacy-summary::-webkit-details-marker {
            display: none;
        }
        
        .privacy-icons {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .icon-wrapper {
            position: relative;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .privacy-icon {
            font-size: 24px;
            transition: transform 0.3s ease;
        }
        
        .privacy-icon.shield {
            color: #4CAF50;
        }
        
        .privacy-icon.level {
            color: #FF9800;
        }
        
        .arrow {
            font-size: 20px;
            color: #6a11cb;
            transition: transform 0.3s ease;
            margin-left: 10px;
        }
        
        .privacy-details[open] .arrow {
            transform: rotate(180deg);
        }
        
        .privacy-explanation {
            padding: 0 20px 20px 20px;
            background: linear-gradient(to bottom, #f8f9ff, #ffffff);
            animation: fadeIn 0.5s ease;
        }
        
        .privacy-explanation h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }
        
        .privacy-level {
            display: inline-block;
            background: linear-gradient(135deg, #FF9800, #FFB74D);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            box-shadow: 0 3px 10px rgba(255, 152, 0, 0.3);
        }
        
        .privacy-explanation p {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
            font-size: 0.95rem;
        }
        
        .privacy-features {
            background: #e8f4ff;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            border-left: 4px solid #2575fc;
        }
        
        .privacy-features h4 {
            color: #2575fc;
            margin-bottom: 10px;
        }
        
        .privacy-features ul {
            list-style: none;
            padding-left: 10px;
        }
        
        .privacy-features li {
            color: #444;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        
        .privacy-features li:before {
            content: "✓";
            color: #4CAF50;
            font-weight: bold;
            margin-right: 10px;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .toggle-hint {
            text-align: center;
            margin-top: 15px;
            color: #777;
            font-size: 0.85rem;
            font-style: italic;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="privacy-container">
        <div class="privacy-header">
            <h1><i class="fas fa-user-shield"></i> CONFIGURAÇÕES DE PRIVACIDADE</h1>
        </div>
        
        <div class="privacy-widget">
            <details class="privacy-details" id="privacyDetails">
                <summary class="privacy-summary">
                    <div class="privacy-icons">
                        <div class="icon-wrapper">
                            <i class="fas fa-shield-alt privacy-icon shield"></i>
                        </div>
                        <div class="icon-wrapper">
                            <i class="fas fa-chart-bar privacy-icon level"></i>
                        </div>
                        <span class="arrow">
                            <i class="fas fa-chevron-down"></i>
                        </span>
                    </div>
                </summary>
                <div class="privacy-explanation">
                    <h3>Nível de Privacidade</h3>
                    <div class="privacy-level">MÉDIO</div>
                    <p>Este nível de privacidade oferece um equilíbrio entre proteção e funcionalidade. Alguns dados são coletados para melhorar sua experiência, mas com limitações importantes.</p>
                    
                    <div class="privacy-features">
                        <h4><i class="fas fa-check-circle"></i> O que isso inclui:</h4>
                        <ul>
                            <li>Proteção básica contra rastreamento</li>
                            <li>Cookies essenciais permitidos</li>
                            <li>Dados anonimizados para analytics</li>
                            <li>Compartilhamento limitado com terceiros</li>
                            <li>Notificações sobre mudanças na política</li>
                        </ul>
                    </div>
                    
                    <p><strong>Recomendado</strong> para a maioria dos usuários que desejam uma experiência personalizada sem expor muitos dados pessoais.</p>
                </div>
            </details>
            
            <div class="toggle-hint">
                <i class="fas fa-mouse-pointer"></i> Clique nos ícones para expandir/recolher
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const privacyDetails = document.getElementById('privacyDetails');
            const icons = document.querySelectorAll('.privacy-icon');
            
            // Adiciona efeito de clique nos ícones
            icons.forEach(icon => {
                icon.addEventListener('click', function(e) {
                    e.stopPropagation();
                    privacyDetails.open = !privacyDetails.open;
                });
            });
            
            // Adiciona efeito sutil aos ícones ao passar o mouse
            icons.forEach(icon => {
                icon.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.1)';
                });
                
                icon.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                });
            });
        });
    </script>
</body>
</html>
