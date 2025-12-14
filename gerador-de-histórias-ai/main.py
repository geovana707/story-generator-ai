from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import random
import logging

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gerador de Histórias Aleatórias")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Chave da API do Google Gemini
GOOGLE_API_KEY = "AIzaSyBfLZmDqbNHo6LaO2-Eu6JvVe__5I9NAA0"

# MODELO CORRETO: Gemini 2.5 Flash
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Lista de temas aleatórios para gerar histórias
TEMAS = [
    "um astronauta perdido em um planeta desconhecido",
    "uma bruxa que perdeu seus poderes mágicos",
    "um robô que aprende a sentir emoções",
    "um dragão vegetariano em um mundo de carnívoros",
    "uma cidade flutuante nas nuvens",
    "um detetive que pode ver fantasmas",
    "uma biblioteca onde os livros ganham vida à noite",
    "um gato que se transforma em humano durante a lua cheia",
    "uma floresta encantada que muda de lugar",
    "um cientista que descobre uma dimensão paralela",
    "um pirata que tem medo do oceano",
    "uma bailarina de circo com poderes telecinéticos",
    "um chef de cozinha que pode falar com os alimentos",
    "uma nave espacial abandonada cheia de mistérios",
    "um pintor cujas obras se tornam realidade",
    "uma escola para super-heróis aposentados",
    "um relojoeiro que pode voltar no tempo",
    "uma sereia que sonha em explorar o deserto",
    "um vampiro que trabalha como dentista",
    "uma máquina do tempo quebrada em uma feira de antiguidades"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/gerar-historia")
async def gerar_historia():
    """Endpoint para gerar história aleatória usando Google Gemini"""
    try:
        # Escolher um tema aleatório
        tema = random.choice(TEMAS)
        
        # Escolher aleatoriamente entre 3 e 7 parágrafos
        num_paragrafos = random.randint(3, 7)
        
        logger.info(f"Gerando história com {num_paragrafos} parágrafos sobre: {tema}")
        
        # Preparar o prompt
        prompt_completo = f"""Você é um excelente escritor de histórias criativas e envolventes. 

Crie uma história COMPLETA E FINALIZADA sobre: {tema}

REGRAS OBRIGATÓRIAS:
1. A história DEVE ter EXATAMENTE {num_paragrafos} parágrafos
2. O ÚLTIMO parágrafo DEVE ser a conclusão e finalização da história
3. A história DEVE estar completa do início ao fim
4. NÃO deixe a história em aberto ou sem conclusão

Estrutura:
- Parágrafo 1: Apresentação do personagem e contexto inicial
- Parágrafos intermediários: Desenvolvimento do conflito/aventura
- Parágrafo {num_paragrafos} (FINAL): Resolução COMPLETA do conflito e conclusão satisfatória

Cada parágrafo deve ter 4-6 frases. Separe os parágrafos com linha em branco.

IMPORTANTE: Termine a história de forma definitiva no último parágrafo. O leitor deve sentir que a história teve um encerramento claro."""

        # Fazer requisição para a API do Google Gemini
        async with httpx.AsyncClient(timeout=45.0) as client:  # Aumentado timeout
            response = await client.post(
                f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt_completo
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.8,  # Reduzido para mais consistência
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 3000,  # AUMENTADO para histórias mais longas
                        "stopSequences": []
                    },
                    "safetySettings": [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                }
            )
            
            logger.info(f"Status da API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se há filtro de segurança
                if "candidates" not in data or len(data["candidates"]) == 0:
                    logger.error("Resposta sem candidatos - possível bloqueio de segurança")
                    return {
                        "success": False,
                        "error": "Conteúdo bloqueado por filtros de segurança",
                        "details": "Tente gerar novamente com outro tema."
                    }
                
                candidate = data["candidates"][0]
                
                # Verificar finish_reason
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                logger.info(f"Finish reason: {finish_reason}")
                
                if finish_reason == "SAFETY":
                    return {
                        "success": False,
                        "error": "História bloqueada por filtros de segurança",
                        "details": "O conteúdo gerado foi considerado inadequado. Tente outro tema."
                    }
                
                if finish_reason == "MAX_TOKENS":
                    logger.warning("História atingiu limite de tokens - pode estar incompleta")
                
                historia = candidate["content"]["parts"][0]["text"]
                
                # Contar parágrafos
                paragrafos = [p.strip() for p in historia.split('\n\n') if p.strip()]
                total_paragrafos = len(paragrafos)
                
                logger.info(f"História gerada com {total_paragrafos} parágrafos (esperados: {num_paragrafos})")
                logger.info(f"Tamanho da história: {len(historia)} caracteres")
                
                # Avisar se história parece incompleta
                historia_incompleta = finish_reason == "MAX_TOKENS" or total_paragrafos < num_paragrafos
                
                return {
                    "success": True,
                    "historia": historia,
                    "tema": tema,
                    "paragrafos": total_paragrafos,
                    "mostrar_continuar": total_paragrafos >= 7,
                    "aviso_incompleta": historia_incompleta
                }
            else:
                logger.error(f"Erro na API: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erro na API: {response.status_code}",
                    "details": response.text
                }
                
    except httpx.TimeoutException:
        logger.error("Timeout na requisição para API")
        return {
            "success": False,
            "error": "Timeout na conexão",
            "details": "A API demorou muito para responder. Tente novamente."
        }
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": "Erro inesperado no servidor"
        }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    return {"status": "ok", "message": "Servidor funcionando!"}

@app.get("/temas-disponiveis")
async def listar_temas():
    """Retorna a lista de temas disponíveis"""
    return {"temas": TEMAS, "total": len(TEMAS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
