const loading = document.getElementById('loading');
const result = document.getElementById('result');
const storyText = document.getElementById('storyText');
const temaBadge = document.getElementById('temaBadge');
const storyContainer = document.getElementById('storyContainer');
const btnGerar = document.getElementById('btnGerar');
const continuarMensagem = document.getElementById('continuarMensagem');

/**
 * Função principal para gerar história
 */
async function gerarHistoria() {
    // Ocultar resultado anterior
    result.classList.remove('show');
    continuarMensagem.style.display = 'none';
    
    // Mostrar loading
    loading.classList.add('show');
    btnGerar.disabled = true;
    
    try {
        // Fazer requisição para o backend
        const response = await fetch('/gerar-historia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        // Ocultar loading
        loading.classList.remove('show');
        
        // Mostrar resultado
        result.classList.add('show');
        
        if (data.success) {
            // História gerada com sucesso
            mostrarHistoria(data);
        } else {
            // Erro ao gerar história
            mostrarErro(data);
        }
        
    } catch (error) {
        // Erro de conexão
        loading.classList.remove('show');
        result.classList.add('show');
        mostrarErroConexao(error);
    } finally {
        // Reativar botão
        btnGerar.disabled = false;
    }
}

/**
 * Exibe a história gerada com sucesso
 */
function mostrarHistoria(data) {
    storyContainer.classList.remove('error');
    temaBadge.innerHTML = `<span class="emoji">📚</span>Tema: ${data.tema}`;
    storyText.textContent = data.historia;
    storyText.classList.remove('error-text');
    
    // Mostrar mensagem "Continue na sua imaginação" se tiver 7 ou mais parágrafos
    if (data.mostrar_continuar) {
        continuarMensagem.style.display = 'block';
    }
    
    // Log de sucesso no console (opcional)
    console.log(`✅ História gerada: ${data.paragrafos} parágrafos`);
    if (data.modelo_usado) {
        console.log(`🤖 Modelo usado: ${data.modelo_usado}`);
    }
}

/**
 * Exibe erro retornado pela API
 */
function mostrarErro(data) {
    storyContainer.classList.add('error');
    temaBadge.innerHTML = '<span class="emoji">❌</span>Erro ao gerar história';
    storyText.innerHTML = `<strong>Detalhes do erro:</strong><br><br>${data.error}<br><br>${data.details || ''}`;
    storyText.classList.add('error-text');
    
    // Log de erro no console
    console.error('❌ Erro na API:', data.error);
}

/**
 * Exibe erro de conexão
 */
function mostrarErroConexao(error) {
    storyContainer.classList.add('error');
    temaBadge.innerHTML = '<span class="emoji">❌</span>Erro de conexão';
    storyText.innerHTML = `<strong>Não foi possível conectar ao servidor:</strong><br><br>${error.message}`;
    storyText.classList.add('error-text');
    
    // Log de erro no console
    console.error('❌ Erro de conexão:', error);
}

/**
 * Permitir gerar história ao pressionar Enter
 */
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !btnGerar.disabled) {
        gerarHistoria();
    }
});

/**
 * Log de inicialização (opcional)
 */
console.log('✨ Gerador de Histórias inicializado!');
console.log('🎯 Pressione o botão ou Enter para gerar uma história');
