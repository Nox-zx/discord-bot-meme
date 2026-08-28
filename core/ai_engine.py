import json
import logging
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.system_instruction = """
Você é um membro ativo de um grupo do Discord. Sua função é responder aos usuários de forma natural, dinâmica e adaptativa.

Em vez de responder sempre apenas em texto, você DEVE decidir o melhor formato para a sua resposta com base no contexto:
1. "TEXT": Para conversas normais, explicações ou opiniões diretas.
2. "MEME_SEARCH": Quando a situação pedir uma reação visual, piada, meme ou GIF viral.
3. "EMOJI_REACTION": Quando a mensagem do usuário pedir apenas uma reação rápida.

Você DEVE responder EXCLUSIVAMENTE em formato JSON rigoroso, seguindo esta estrutura:
{
  "action_type": "TEXT" | "MEME_SEARCH" | "EMOJI_REACTION",
  "payload": {
    "text_content": "Texto da resposta (obrigatório se action_type for TEXT; opcional se for MEME_SEARCH)",
    "search_query": "Termo de busca em inglês focado no meme/GIF ideal (usar apenas se action_type for MEME_SEARCH)",
    "emoji_symbol": "Único emoji unicode para reagir (usar apenas se action_type for EMOJI_REACTION)"
  }
}
"""

    async def decide_action(self, context_history: list[dict]) -> dict:
        prompt = f"Histórico recente da conversa:\n{json.dumps(context_history, ensure_ascii=False)}\n\nDecida a sua próxima ação."

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            return json.loads(response.text)
        except Exception as e:
            logging.error(f"Erro ao processar decisão da IA: {e}")
            return {
                "action_type": "TEXT",
                "payload": {"text_content": "Deu um pequeno bug no meu processamento aqui, mas estou acompanhando!"}
            }

