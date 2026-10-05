import os
from datetime import datetime, timezone
from typing import List

import discord

from contract_objects.newsletter import Newsletter


EMBED_TITLE_LIMIT = 256
EMBED_DESCRIPTION_LIMIT = 4096
EMBEDS_PER_MESSAGE = 10
EMBED_TOTAL_LIMIT = 6000

HEADER_COLOR = 0xC9A227
SECTION_COLORS = [0x2B6CB0, 0x2F855A, 0xC05621, 0x6B46C1, 0xB83280, 0x2C7A7B]


async def send_newsletter(newsletter: Newsletter):
	client = discord.Client(intents=discord.Intents.default())
	async with client:
		await client.login(os.environ["DISCORD_TOKEN"])
		channel = await client.fetch_channel(int(os.environ["DISCORD_CHANNEL_ID"]))
		embeds = build_embeds(newsletter, client.user)
		for group in group_embeds(embeds):
			await channel.send(embeds=group)


def build_embeds(newsletter: Newsletter, bot_user: discord.ClientUser) -> List[discord.Embed]:
	header = discord.Embed(
		title=newsletter.title[:EMBED_TITLE_LIMIT],
		description=newsletter.intro,
		color=HEADER_COLOR,
		timestamp=datetime.now(timezone.utc),
	)
	header.set_author(name=bot_user.name, icon_url=bot_user.display_avatar.url)
	embeds = [header]

	for index, section in enumerate(newsletter.sections):
		color = SECTION_COLORS[index % len(SECTION_COLORS)]
		for part, chunk in enumerate(split_message(section.content, EMBED_DESCRIPTION_LIMIT)):
			embeds.append(discord.Embed(title=section.title[:EMBED_TITLE_LIMIT] if part == 0 else None, description=chunk, color=color))

	if newsletter.outro:
		footer = discord.Embed(description=newsletter.outro, color=HEADER_COLOR)
		footer.set_footer(text=bot_user.name, icon_url=bot_user.display_avatar.url)
		embeds.append(footer)
	return embeds


def group_embeds(embeds: List[discord.Embed]) -> List[List[discord.Embed]]:
	groups = []
	current = []
	current_size = 0
	for embed in embeds:
		size = len(embed)
		if current and (len(current) == EMBEDS_PER_MESSAGE or current_size + size > EMBED_TOTAL_LIMIT):
			groups.append(current)
			current = []
			current_size = 0
		current.append(embed)
		current_size += size
	if current:
		groups.append(current)
	return groups


def split_message(text: str, limit: int) -> List[str]:
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
