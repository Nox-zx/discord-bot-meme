import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S"
)

try:
    from config import DISCORD_TOKEN, GEMINI_API_KEY, MAX_CONTEXT_MESSAGES
    from core.ai_engine import AIEngine
    from core.action_router import ActionRouter
    from services.media_service import MediaService
    import discord
except ModuleNotFoundError as e:
    logging.critical(f"Erro ao importar módulos: {e}")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

media_service = MediaService()
ai_engine = AIEngine(api_key=GEMINI_API_KEY)
action_router = ActionRouter(media_service=media_service)

@client.event
async def on_ready():
    logging.info(f"Bot conectado com sucesso como: {client.user} (ID: {client.user.id})")

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if client.user in message.mentions:
        logging.info(f"Mensagem de {message.author.display_name}: {message.content}")
        
        async with message.channel.typing():
            try:
                history = []
                async for msg in message.channel.history(limit=MAX_CONTEXT_MESSAGES):
                    history.append({
                        "author": msg.author.display_name,
                        "content": msg.content,
                        "is_bot": msg.author == client.user
                    })
                history.reverse()

                decision = await ai_engine.decide_action(history)
                logging.info(f"Decisão da IA: {decision}")

                await action_router.execute(decision, message)

            except Exception as e:
                logging.error(f"Erro ao processar mensagem: {e}")
                await message.channel.send("Ocorreu um erro ao tentar responder.")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logging.critical("DISCORD_TOKEN não configurado nas variáveis de ambiente.")
    elif not GEMINI_API_KEY:
        logging.critical("GEMINI_API_KEY não configurada nas variáveis de ambiente.")
    else:
        client.run(DISCORD_TOKEN)

