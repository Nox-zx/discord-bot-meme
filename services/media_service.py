import aiohttp
import logging
import random

class MediaService:
    def __init__(self):
        self.headers = {
            "User-Agent": "DiscordBot:MemeFetcher:v1.0 (by /u/discord_bot)"
        }
        self.default_subreddits = ["memes", "dankmemes", "shitposting", "wholesomememes"]

    async def fetch_meme_url(self, query: str = None) -> str | None:
        if query:
            url = f"https://www.reddit.com/r/memes/search.json?q={query}&restrict_sr=1&limit=15&sort=relevance"
        else:
            sub = random.choice(self.default_subreddits)
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        children = data.get("data", {}).get("children", [])
                        
                        valid_posts = []
                        for post in children:
                            post_data = post.get("data", {})
                            post_url = post_data.get("url", "")
                            
                            if not post_data.get("over_18", False) and any(post_url.endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".gif"]):
                                valid_posts.append(post_url)

                        if valid_posts:
                            return random.choice(valid_posts)

                    logging.warning(f"Nenhum meme encontrado no Reddit para: {query}")
                    
                    if query:
                        return await self.fetch_meme_url(query=None)

                    return None
        except Exception as e:
            logging.error(f"Erro ao buscar mídia no Reddit: {e}")
            return None

