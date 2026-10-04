import os
from typing import List

import discord


DISCORD_MESSAGE_LIMIT = 2000


async def send_newsletter(text: str):
	client = discord.Client(intents=discord.Intents.default())
	async with client:
		await client.login(os.environ["DISCORD_TOKEN"])
		channel = await client.fetch_channel(int(os.environ["DISCORD_CHANNEL_ID"]))
		for chunk in split_message(text):
			await channel.send(chunk)


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> List[str]:
	chunks = []
	current = ""
	for line in text.splitlines(keepends=True):
		while len(line) > limit:
			if current:
				chunks.append(current)
				current = ""
			chunks.append(line[:limit])
			line = line[limit:]
		if len(current) + len(line) > limit:
			chunks.append(current)
			current = ""
		current += line
	if current.strip():
		chunks.append(current)
	return chunks
