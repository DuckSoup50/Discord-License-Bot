from discord import Intents
import discord
import json
import random
import string
import os
import time
import asyncio
import datetime

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if not message.content.startswith('%'):
        return
    
    if "Admin" in [role.name for role in message.author.roles]:
        args = message.content.split(' ')

        match (args[0]):
            case "%gen":
                if len(args) != 3:
                    await message.channel.send("Invalid usage.")
                    return
                amount = range(int(args[1]))
                keyType = args[2]
                await GenerateKeys(amount, keyType)
                return
            case "%check":
                await message.channel.send("Checking Licenses 24/7.")
                while True:
                    await ExpireCheck(message)
                    await asyncio.sleep(3600)
 

    if "NoSub" in [role.name for role in message.author.roles]:
        args = message.content.split(' ')

        match (args[0]):
            case "%redeem":
                if len(args) != 2:
                    await message.channel.send("Invalid usage.")
                    return
                key = args[1]
                await RedeemKey(message, key)
                return

async def RedeemKey(message, key):
    if not os.path.exists('Redeemed.json'):
       with open('Redeemed.json', 'w') as f:
        json.dump({}, f)
    
    with open('Keys.json', 'r') as f:
        keys = json.load(f)

        if key in keys:
            currentTime = time.time()

            keyType = keys[key]
            match (keyType):
                case "Weekly":
                    futureTime = currentTime + (60 * 60 * 24 * 7)
                    epochTs = int(futureTime)
                case "Monthly":
                    futureTime = currentTime + (60 * 60 * 24 * 31)
                    epochTs = int(futureTime)
                case "Lifetime":
                    futureTime = currentTime + (60 * 60 * 24 * 365 * 10)
                    epochTs = int(futureTime)

            role = discord.utils.get(message.guild.roles, name=keyType)
            NoSubrole = discord.utils.get(message.guild.roles, name="NoSub")

            if not role:
                await message.author.send("Could not redeem your key. Please Contact Sat!")
                return
            
            await message.author.add_roles(role)
            await message.author.remove_roles(NoSubrole)

            del keys[key]
            with open('Keys.json', 'w') as f:
                json.dump(keys, f, indent=2)

            with open('Redeemed.json', 'r') as f:
                redeemed = json.load(f)

            dt_obj = datetime.datetime.fromtimestamp(epochTs)
            dt_str = dt_obj.strftime("%Y-%m-%d %H:%M")

            redeemed[key] = {
                'Id': message.author.id,
                'Expire': epochTs,
                'Plan': keyType,
                'Time': dt_str
            }

            with open('Redeemed.json', 'w') as f:
                json.dump(redeemed, f, indent=2)

            logging = client.get_channel(1082026368763691160)
            await message.channel.send("Redeemed! Check your DM for more information!")
            await logging.send(f"{message.author} has redeemed: **{role}** and expires on **{dt_str}**. <@1024706645315551253>")
            await message.author.send(f"You have successfully redeemed your key.\nIt will expire on: {dt_str}")
        
        else: 
            await message.delete()
            await message.channel.send("Invalid key!")

async def ExpireCheck(message):
    with open('Redeemed.json', 'r') as f:
        AllKeys = json.load(f)  

    for key in list(AllKeys):
        expire_time = AllKeys[key]['Expire']
        current_time = int(time.time())

        
        if expire_time <= current_time:
            # Subscribtion has ended!
            user_id = AllKeys[key]['Id']
            role_name = AllKeys[key]['Plan']
            role = discord.utils.get(message.guild.roles, name=role_name)

            if not role:
                continue

            member = await message.guild.fetch_member(user_id)
            await member.remove_roles(role)
            # Add NoSub Role back! (Maybe Epxired if you like that)
            # Send a pm... saying blah blah buy new sub

            role = discord.utils.get(message.guild.roles, name="NoSub")
            await message.author.add_roles(role)
            logging = client.get_channel(1082026368763691160)
            await logging.send(f"{user_id} -> Subscribtion has ended. Plan was: {role_name}")
            await message.author.send(f"Hello,\nYour {role_name} subscribtion has ended!\nWant to renew? Go to: https://shoppy.gg/@AtomicCloud")
            del AllKeys[key]

            with open('Redeemed.json', 'w') as f:
                json.dump(AllKeys, f, indent=2)
        
        


async def GenerateKeys(amount, type):
   if not os.path.exists('Keys.json'):
       with open('Keys.json', 'w') as f:
        json.dump({}, f)

   for i in amount:
       key = 'Atomic-' + ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16)) + '-Cloud'
       keys = {}
       with open('Keys.json', 'r') as f:
           keys = json.load(f)
       keys[key] = type
       with open('Keys.json', 'w') as f:
           json.dump(keys, f, indent=2)
        


client.run('MTA4MTE5MTY3OTc5ODgxNjgwMg.GtwUP6.IKOFyfY30Ol4FP6b0-bqinyzwW_mElCJBMiY00')