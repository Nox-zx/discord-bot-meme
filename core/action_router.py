import discord
from services.media_service import MediaService

class ActionRouter:
    def __init__(self, media_service: MediaService):
        self.media_service = media_service

    async def execute(self, decision: dict, message: discord.Message):
        action_type = decision.get("action_type")
        payload = decision.get("payload", {})

        if action_type == "TEXT":
            text = payload.get("text_content")
            if text:
                await message.channel.send(text)

        elif action_type == "EMOJI_REACTION":
            emoji = payload.get("emoji_symbol")
            if emoji:
                try:
                    await message.add_reaction(emoji)
                except Exception:
                    await message.channel.send(emoji)

        elif action_type == "MEME_SEARCH":
            query = payload.get("search_query")
            text_caption = payload.get("text_content", "")
            
            meme_url = await self.media_service.fetch_meme_url(query)

            if meme_url:
                embed = discord.Embed()
                embed.set_image(url=meme_url)
                await message.channel.send(content=text_caption if text_caption else None, embed=embed)
            else:
                fallback_text = text_caption if text_caption else "Queria te mandar um meme sobre isso, mas não encontrei um bom no momento!"
                await message.channel.send(fallback_text)

