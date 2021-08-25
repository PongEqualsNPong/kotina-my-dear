from logging import log
import discord
from typing import List, Tuple
from discord.errors import Forbidden
from discord.ext.commands import bot
from data.enum.roles import Roles
from data.enum.channels import Channels
import random as random

commands = discord.ext.commands

# self.bot
class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def kill(self, ctx):
        if ctx.channel.id == Channels.TEST.value:
            await self.bot.logout()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        roleMember = discord.utils.get(member.guild.roles, id=Roles.ROLE_VISITOR.value)
        await member.add_roles(roleMember)

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        channel = message.channel
        isMod = False
        staffRole = discord.utils.find(lambda r: r.id == 777975184035807302, message.author.roles)
        if staffRole != None:
            isMod = True

        # or channel.name == "bot-test" and message.author.bot == False and isMod == False
        # line is for debugging purpose
        if  channel.name == "general" and message.author.bot == False     or   channel.name == "🔖membership-request" and message.author.bot == False and isMod == False :
            emojiAccepted = "✅"
            emojiRejected = "❌"
            content = message.content
            try:
                #tokenize content
                tokens = self.tokenize(content, message.author)
                # roles
                roles = []
    
                moreRoles = self.matchRole(tokens[2], message)
                allRoles = roles + moreRoles
                # name and tag
                targetName = tokens[0] + " " + tokens[1]
                await message.author.edit(nick=targetName)
                # clear roles first hotfix
                toRemove = []
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R5.value))
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R4.value))
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R3.value))
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R2.value))
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R1.value))
                toRemove.append(discord.utils.get(message.author.guild.roles, id=Roles.ROLE_VISITOR.value))

                for role in toRemove:
                    await message.author.remove_roles(role)

                for role in allRoles:
                    await message.author.add_roles(role)

                await message.add_reaction(emojiAccepted)

            except ValueError or TypeError:
                await message.add_reaction(emojiRejected)
                await channel.send("Hey Stepbro I'm stuck! Kindly follow the request template rigorously, otherwise I cannot update your server identity and I will be stuck AGAIN.")

            except Forbidden or AttributeError:
                await message.add_reaction(emojiRejected)
                await channel.send("Onii-Chan you are so powerful! I wanna be like you, teach me Senpai.")
                    
            
            except TokenizeException:
                await message.add_reaction(emojiRejected)
                await channel.send(
                    "Hey Stepbro! I think this one is too big for me. Kindly follow the request template otherwise I cannot update your server identity."
                ) if random.randrange(0, 99) > 49 else await channel.send(
                    "Hey Stepbro I'm stuck! Kindly follow the request template rigorously, otherwise I cannot update your server identity and I will be stuck AGAIN."
                )

    def matchRole(self, token: str, message):
        result = []
        rank = token[-1]
        if rank == "5":
            result.append(
                discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R5.value)
            )
        elif rank == "4":
            result.append(
                discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R4.value)
            )
        elif rank == "3":
            result.append(
                discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R3.value)
            )
        elif rank == "2":
            result.append(
                discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R2.value)
            )
        else:
            result.append(
                discord.utils.get(message.author.guild.roles, id=Roles.ROLE_R1.value)
            )
        return result

    def tokenize(self, messageContent, messageAuthor) -> List[str]: 
        splitList = [word for word in messageContent.split()]
        if len(splitList) > 5:
            raise TokenizeException(messageContent)
        elif len(splitList) >= 1 and len(splitList) <= 5:
            tag = self.parseTag(splitList)
            rank = self.parseRank(splitList)
            filtered = [token for token in splitList if token != tag and token != rank]
            name = self.parseName(filtered, messageAuthor)
            # finish tag we hope that input wasnt complete garbage
            if len(tag) == 3:
                tag = '[' + tag + ']'
            else:
                asList = list(tag)
                asList[0] = '['
                asList[-1] = ']'
                tag = ''.join(asList)
            return [tag, name, rank]
        else:
            raise ValueError

    def parseName(self, tokenList: List[str], messageAuthor) -> str:
        if len(tokenList) > 0:
            result = ''
            for token in tokenList:
                result += token + ' '
            return result.rstrip()
        else:
            return messageAuthor.name
        
    def parseTag(self, tokenList: List[str]) -> str:
        #search for len token 3 or 5
        goodCandidates = [token for token in tokenList if len(token) == 3 and token.isupper()]
        decentCandidates = [token for token in tokenList if len(token) == 5]
        betterCandidates = []
        for candidate in decentCandidates:
            if candidate[0] == '(' or candidate[0] == '[' or candidate[0] == '{' or candidate[0] == '<':
                betterCandidates.append(candidate)
        bestCandidates = goodCandidates + betterCandidates
        if len(bestCandidates) > 0:
            return bestCandidates[0]
        else: 
            raise TokenizeException('Cannot resolve Tag.')

    def parseRank(self, tokenList: List[str]) -> str:
        candidates = [token for token in tokenList if len(token) == 2]
        # need to check for 1-5
        betterCandidates = [token for token in candidates if token[0].upper() == 'R' and token[1].isnumeric()]
        if len(betterCandidates) > 0:
            return betterCandidates[0]
        else: 
            raise TokenizeException('Cannot resolve Rank.')




    @commands.command()
    async def member(self, ctx):
        if ctx.channel.id == Channels.TEST.value:
            role = discord.utils.get(ctx.guild.roles, id=Roles.ROLE_VISITOR.value)  
            members = self.bot.get_all_members()
            for member in members:
                if len(member.roles) < 2: 
                    await member.add_roles(role)

    @commands.command()
    async def roles(self, ctx):
        if ctx.channel.id == Channels.TEST.value:
            roles = ctx.guild.roles
            print(roles)
        

                





class TokenizeException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "{} is invalid input, can only accept shorter ".format(self.value)
