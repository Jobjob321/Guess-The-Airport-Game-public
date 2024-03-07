import discord, requests, asyncio
from get_airport_emoji import get_country_flag
from timer import Timer
from discord import app_commands
from discord.ext import commands, tasks

BOT_TOKEN = ""
AIRPORT_TOKEN = ""


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description="description", intents=intents)


game_states = {}

role = None
guild = None

TIMER_DURATION = 10 * 60
timer_instance = Timer(TIMER_DURATION)



@bot.event
async def on_ready():
    global guild
    global airport_set
    global role
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    guild = bot.guilds[0]
    timer_instance.expired = True
    airport_set = False

    role_name_to_find = "Current GTA picker"  
    role = discord.utils.get(guild.roles, name=role_name_to_find)

    for member in guild.members:
        if role in member.roles:
            await member.remove_roles(role)

    print('------')
    if timer_instance.has_expired():
        print("timer has expired")
        

response_json = {}

def get_channel_by_name(guild, channel_name):
    """Function to get a channel object by name."""
    for channel in guild.channels:
        if channel.name == channel_name:
            return channel
    return None  # Return None if the channel is not found


def send_timer_expired_message():
    """Function to send a message when the timer expires."""
    # Get the channel where you want to send the message
    channel = get_channel_by_name(guild, "guess-the-airport")  # Replace None with the channel object where you want to send the message
    if channel is not None:
        # Send the message
        asyncio.ensure_future(channel.send("Timer has expired! Anyone can now choose."))


airport_set = False
@bot.tree.command(name="set_airport")
@app_commands.describe(airport = "Enter airport")
async def set_airport(interaction: discord.Interaction, airport: str):
    global airport_set
    global response_json

    guild_id = interaction.guild_id
    if guild_id not in game_states:
        game_states[guild_id] = {"airport_set": False, "response_json": None}

    if game_states[guild_id]["airport_set"]:
        await interaction.response.send_message("Airport already set", ephemeral=True)
        return

    guild = bot.get_guild(guild_id)
    role_name_to_find = "Current GTA picker"  
    role = discord.utils.get(guild.roles, name=role_name_to_find)

    if role is None:
        print(f"Role '{role_name_to_find}' not found in guild.")
        await interaction.response.send_message(f"Role '{role_name_to_find}' not found in guild.", ephemeral=True)
        return



    if game_states[guild_id]["airport_set"] == True:
        await interaction.response.send_message("Airport already set", ephemeral=True)
        return
    
    if timer_instance.expired == True:
        pass
    else:
        if discord.utils.get(interaction.user.roles, name="Current GTA picker") is None:
            await interaction.response.send_message("You aren't the current picker.", ephemeral=True)
            return

    if len(airport) == 3 and game_states[guild_id]["airport_set"] == False:
        try:
            response = requests.get('https://api.api-ninjas.com/v1/airports?iata={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
            game_states[guild_id]["response_json"] = response.json()[0]
            response_name = game_states[guild_id]["response_json"]["name"]
            await interaction.response.send_message("Succesfully set airport to {}".format(response_name), ephemeral=True)
            channel = get_channel_by_name(guild, "guess-the-airport")
    
            try:
                await channel.send("A new round has been started, good luck!")
            except:
                print("error")
            game_states[guild_id]["airport_set"] = True
            for member in guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
            
            await interaction.user.add_roles(role)
            timer_instance.stop()
        except:
            try:
                response = requests.get('https://api.api-ninjas.com/v1/airports?name={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
                game_states[guild_id]["response_json"] = response.json()[0]
                response_name = game_states[guild_id]["response_json"]["name"]
                await interaction.response.send_message("Succesfully set airport to {}".format(response_name), ephemeral=True)
                channel = get_channel_by_name(guild, "guess-the-airport")
                try:
                    await channel.send("A new round has been started, good luck!")
                except:
                    print("error")

                game_states[guild_id]["airport_set"] = True
                for member in guild.members:
                    if role in member.roles:
                        await member.remove_roles(role)
                await interaction.user.add_roles(role)
                timer_instance.stop()
            except:
                await interaction.response.send_message("Airport not recognised, try again", ephemeral=True)
                game_states[guild_id]["airport_set"] = False


    if len(airport) == 4 and game_states[guild_id]["airport_set"] == False:
        try:
            response = requests.get('https://api.api-ninjas.com/v1/airports?icao={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
            game_states[guild_id]["response_json"] = response.json()[0]
            response_name = game_states[guild_id]["response_json"]["name"]
            game_states[guild_id]["airport_set"] = True
            timer_instance.stop()
            for member in guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Succesfully set airport to {}".format(response_name), ephemeral=True)
            channel = get_channel_by_name(guild, "guess-the-airport")
    
            try:
                await channel.send("A new round has been started, good luck!")
            except:
                print("error")
            
        except:
            try:
                response = requests.get('https://api.api-ninjas.com/v1/airports?name={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
                game_states[guild_id]["response_json"] = response.json()[0]
                response_name = game_states[guild_id]["response_json"]["name"]
                await interaction.response.send_message("Succesfully set airport to {}".format(response_name), ephemeral=True)
                channel = get_channel_by_name(guild, "guess-the-airport")
    
                try:
                    await channel.send("A new round has been started, good luck!")
                except:
                    print("error")
                game_states[guild_id]["airport_set"] = True
                for member in guild.members:
                    if role in member.roles:
                        await member.remove_roles(role)
                await interaction.user.add_roles(role)
                timer_instance.stop()
                
            except:
                await interaction.response.send_message("Airport not recognised, try again", ephemeral=True)
                game_states[guild_id]["airport_set"] = False

    if len(airport) != 3 and len(airport) != 4 and game_states[guild_id]["airport_set"] == False:
        try:
            response = requests.get('https://api.api-ninjas.com/v1/airports?name={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
            game_states[guild_id]["response_json"] = response.json()[0]
            response_name = game_states[guild_id]["response_json"]["name"]
            await interaction.response.send_message("Succesfully set airport to {}".format(response_name), ephemeral=True)
            channel = get_channel_by_name(guild, "guess-the-airport")
    
            try:
                await channel.send("A new round has been started, good luck!")
            except:
                print("error")
            timer_instance.stop()
            for member in guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
            await interaction.user.add_roles(role)
            game_states[guild_id]["airport_set"] = True
            
        except:
            await interaction.response.send_message("Airport not recognised, try again", ephemeral=True)
            game_states[guild_id]["airport_set"] = False

guess_name = ""
@bot.tree.command(name="guess_airport")
@app_commands.describe(airport="Enter airport")
async def guess_airport(interaction: discord.Interaction, airport: str):
    global airport_set
    global response_json
    global guess_name

    guild_id = interaction.guild_id
    if guild_id not in game_states:
        await interaction.response.send_message("No game has been started in this server.", ephemeral=True)
        return

    guild = bot.get_guild(guild_id)
    role_name_to_find = "Current GTA picker"  
    role = discord.utils.get(guild.roles, name=role_name_to_find)

    if role is None:
        print(f"Role '{role_name_to_find}' not found in guild.")
        await interaction.response.send_message(f"Role '{role_name_to_find}' not found in guild.", ephemeral=True)
        return

    
    if discord.utils.get(interaction.user.roles, name="Current GTA picker") is not None:
        await interaction.response.send_message("You cannot use this command while you are the person that chose.", ephemeral=True)
        return

    try:
        if len(airport) == 3:
            guess = requests.get('https://api.api-ninjas.com/v1/airports?iata={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
        elif len(airport) == 4:
            guess = requests.get('https://api.api-ninjas.com/v1/airports?icao={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})
        else:
            guess = requests.get('https://api.api-ninjas.com/v1/airports?name={}'.format(airport), headers={'X-Api-Key': AIRPORT_TOKEN})

        guessing_json = guess.json()[0]
        guess_name = guessing_json["name"]
    except Exception as e:
        print(e)
        await interaction.response.send_message("Airport not recognized, try again", ephemeral=True)
        return
	
    if game_states[guild_id]["response_json"] == guessing_json:
        try:
            for member in guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove roles.", ephemeral=True)
            return
        
        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to add roles.", ephemeral=True)
        else:
            guess_city = guessing_json["city"]
            guess_region = guessing_json["region"]
            guess_country = guessing_json["country"]
            await interaction.response.send_message(f"✅ It was {guess_name}, {guess_city}, {guess_region}, {guess_country}. Your turn to choose.")
            timer_instance.restart()
            game_states[guild_id]["airport_set"] = False

    else:
        guess_country = guessing_json["country"]
        guess_city = guessing_json["city"]
        guess_region = guessing_json["region"]
        if guess_country == game_states[guild_id]["response_json"]["country"]:
            await interaction.response.send_message(f"❌ {get_country_flag(guess_country)} {guess_name}, {guess_city}, {guess_region}, {guess_country}")
        else:
            await interaction.response.send_message(f"❌ {guess_name}, {guess_city}, {guess_region}, {guess_country}")


    print(guess_name)


bot.run(BOT_TOKEN)


