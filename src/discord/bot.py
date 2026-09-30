import os
import discord
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	await post_new_articles()


async def post_new_articles():
	channel = bot.get_channel(1522995413995622400)
	if channel:
		# Send articles
		await channel.send("wassup")
	else:
		print("Error: Could not find channel. Check the ID and bot permissions.")

	await bot.close()
	


if __name__ == "__main__":
	bot.run(os.getenv("DISCORD_TOKEN"))
	