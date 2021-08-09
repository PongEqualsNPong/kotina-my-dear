import discord
import yaml 
from discord.ext import commands
from services.logging.loggingService import LoggingService 
from services.general.greeting import Greetings


config = yaml.safe_load(open("config.yml"))
TOKEN = config['authentication']['token']

intents = discord.Intents.all()
loggingService = LoggingService()
bot = commands.Bot(command_prefix="kot ", intents = intents)
intents.members = True


@bot.command()
async def test(ctx, *args):
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
    
bot.add_cog(Greetings(bot))

bot.run(TOKEN)


