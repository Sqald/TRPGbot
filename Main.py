# 外部プログラムのインポート
import discord
from discord import app_commands
import asyncio
import re
import sys
import random
import datetime
import calendar

# 必要なデータの外部読み出し
f = open('.env', 'r')
env = f.readlines()
f.close()

# データの代入
env_num_token = [s for s in env if re.match('.*Token.*', s)]
env_token = re.search('\'.*.\'',env_num_token[0])

env_num_kill = [s for s in env if re.match('.*killPass.*', s)]
env_kill = re.search('\'.*.\'',env_num_kill[0])

env_num_name = [s for s in env if re.match('.*Botname.*', s)]
env_name = re.search('\'.*.\'',env_num_name[0])

TOKEN = env_token.group().replace('\'', '')

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

# 起動時に動作する処理
tree = app_commands.CommandTree(client)
@client.event
async def on_ready():
    print("GetReady")
    await tree.sync()#スラッシュコマンドを同期

def generate_random_color():
  r = hex(random.randint(0, 255))[2:]
  g = hex(random.randint(0, 255))[2:]
  b = hex(random.randint(0, 255))[2:]
  return int(f"0x{r}{g}{b}", 16)  # 整数に変換

def lowercase_english_words(text):
  return re.sub(r'\b[a-zA-Z]+\b', lambda m: m.group(0).lower(), text)

async def find_channel_link(guild, name, exclude_categories):
    for category in guild.categories:
        if category.name not in exclude_categories:
            for channel in category.channels:
                if channel.name == name:
                    return channel.mention
    return None

async def find_channel_in_category(guild, category_name, channel_name):
    for category in guild.categories:
        if category.name == category_name:
            for channel in category.channels:
                if channel.name == channel_name:
                    return channel
    return None

async def delete_channels_containing(guild, name_id, exclude_categories):
    try:
        for category in guild.categories:
            if category.name not in exclude_categories:
                for channel in category.channels:
                    if name_id in channel.name:
                        await channel.delete()
    except:
        return


#サーバー追加時に秘匿用チャンネルとボット処理用チャンネル、
@client.event
async def on_guild_join(guild):
    # Bot用カテゴリの作成
    botting = await guild.create_category_channel(name="TRPGbot処理用")
    trpg = await guild.create_category_channel(name="TRPGシナリオ")
    trpg_text = await trpg.create_text_channel(name="シナリオ一覧")
    trpg_text = await trpg.create_text_channel(name="タイマン")
    trpg_text = await trpg.create_text_channel(name="2PL")
    trpg_text = await trpg.create_text_channel(name="複数")
    trpg_text = await trpg.create_text_channel(name="秘匿")
    voice = await guild.create_category_channel(name="セッション")
    session1 = await voice.create_voice_channel(name="Room1")
    session2 = await voice.create_voice_channel(name="Room2")
    session3 = await voice.create_voice_channel(name="Room3")
    wait = await voice.create_voice_channel(name="待機")
    talk1 = await voice.create_voice_channel(name="雑談1")
    talk2 = await voice.create_voice_channel(name="雑談2")
    hitoku = await guild.create_category_channel(name="秘匿")
    use_bot = await guild.create_category_channel(name="連絡")
    closed = await guild.create_category_channel(name="終了済")
    # カテゴリ内にテキストチャンネルを作成
    text_channel = await botting.create_text_channel(name="botinfo")
    channel = guild.get_channel(text_channel.id)
    categoryid = guild.get_channel(botting.id)
    #権限の変更
    everyone_role = guild.default_role
    overwrite = discord.PermissionOverwrite(read_messages=False)
    write = discord.PermissionOverwrite(send_messages=False)
    await channel.set_permissions(everyone_role, overwrite=overwrite)
    await trpg.set_permissions(everyone_role, overwrite=write)
    await categoryid.set_permissions(everyone_role, overwrite=overwrite)
    await channel.send(f"[Info]\n\n{guild.name}")

# スラッシュコマンドに関する動作
@tree.command(name="info",description="情報を表示します。")
async def test_command(interaction: discord.Interaction):
    guild = interaction.guild
    content=f"{client.user.name}-{client.user.id}-{len(client.guilds)}\n{guild.name}-{guild.id}-{guild.owner}-{guild.created_at}-{len(guild.members)}"
    await interaction.response.send_message(f"""{content}""",ephemeral=True)

@tree.command(name="new",description="新しいイベントを作成します。シナリオ説明はこのテキストに返信して追加することができます。")
@app_commands.describe(
    name="タイトルを指定してください",
    menu="秘匿の有無を選択してください 有:True 無:False",
    style="TRPG仕様を選択してください 1:CoC6版 2:その他",
    member="HOの数を入力してください (10まで対応)",
    densuke="伝助などのURLを入力してください。",
    url="BoothなどのURLを入力してください。"
)
async def new_command(interaction: discord.Interaction, name:str, style:int ,menu:bool, member:int, url:str=None, densuke:str=None, ccfolia:str=None):
    await interaction.response.defer(ephemeral=True) 
    ccfolia_set = ""
    if style == 1:
        style = "CoC6版"
    elif style == 2:
        style = "その他"
    else :
        style = "指定失敗"
    if ccfolia != None:
        ccfolia_set = f"[CCFOLIA]({ccfolia})"
    try:
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="連絡")
        category2 = discord.utils.get(guild.categories, name="秘匿")
        channel = await category.create_text_channel(name)
        embed = discord.Embed(title=f"{name}",color=0x7fffd4, description=f"""# {name} \n## {style} \n\n{ccfolia_set}""", url=url)
        embed.add_field(name="KP",value=interaction.user.display_name, inline=False)
        embed.set_author(name="伝助", url=densuke)
        exclude_categories = ["連絡", "終了済", "秘匿"]
        channel_name = name
        result = await find_channel_link(guild, channel_name, exclude_categories)
        if result == None:
            result = ""
        contents = f"""# {name} \n\n{result}"""
        for i in range(1,member+1):
            embed.add_field(name=f"HO{i}",value="未設定", inline=False)
            embed.add_field(name=f"HO{i} PC",value="未設定", inline=False)
            if menu:
                ho = await category2.create_text_channel(f"{name}-HO{i}")
                everyone_role = guild.default_role
                overwrite = discord.PermissionOverwrite(view_channel=False)
                await ho.set_permissions(everyone_role, overwrite=overwrite)
        await channel.send(f"{contents}\n\n",embed=embed)
        await interaction.followup.send(f"{name}を作成しました。",ephemeral=True)
    except:
       await interaction.followup.send("失敗しました。",ephemeral=True)


@tree.command(name="densuke",description="イベント情報に伝助を追加することができます。。")
@app_commands.describe(
    ids="最終行のIDを入力してください",
    densuke="伝助のURLを入力してください。"
)
async def densuke_command(interaction: discord.Interaction, ids:str, densuke:str):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        embed = message.embeds[0]
        embed.set_author(name="伝助", url=densuke)
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="booth",description="イベント情報にシナリオの情報を追加することができます。")
@app_commands.describe(
    ids="最終行のIDを入力してください",
    url="BoothのURLを入力してください。"
)
async def booth_command(interaction: discord.Interaction, ids:str, url:str):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        embed = message.embeds[0]
        embed.url = url
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="ccfolia",description="イベント情報にCCFOLIAを追加することができます。")
@app_commands.describe(
    ids="最終行のIDを入力してください",
    ccfolia="CCFOLIAのURLを入力してください。"
)
async def ccfolia_command(interaction: discord.Interaction, ids:str, ccfolia:str):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        embed = message.embeds[0]
        embed.description = embed.description + f"\n\n[CCFOLIA]({ccfolia})"
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="close",description="イベント用に作成した関連品を削除することができます。実行は当該チャンネルのみで行うことができます。")
@app_commands.describe(
    ids="最終行のIDを入力してください",
    delhitoku="True:秘匿を削除 Fales:秘匿を削除しない"
)
async def close_command(interaction: discord.Interaction, ids:str, delhitoku:bool):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        guild = message.guild
        embed = message.embeds[0]
        role = discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
        everyone_role = guild.default_role
        overwrite = discord.PermissionOverwrite(view_channel=True)
        channel = discord.utils.get(guild.channels, name=lowercase_english_words(embed.title + "-" + str(message.id)))
        category = discord.utils.get(guild.categories, name="終了済")
        exclude_categories=["連絡","終了済","TRPGシナリオ"]
        if delhitoku:
            await delete_channels_containing(guild, str(ids), exclude_categories)
        await channel.set_permissions(everyone_role, overwrite=overwrite)
        await channel.edit(category=category)
        await role.delete()
        await interaction.response.send_message(content="終了済に設定しました。",ephemeral=True)
    except:
        try:
            await interaction.response.send_message(content="削除に失敗しました。",ephemeral=True)
        except:
            return

@tree.command(name="delete",description="イベントを削除することができます。実行は当該チャンネルのみで行うことができます。")
@app_commands.describe(
    ids="最終行のIDを入力してください",
)
async def delete_command(interaction: discord.Interaction, ids:str):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        guild = message.guild
        embed = message.embeds[0]
        role = discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
        channel = discord.utils.get(guild.channels, name=lowercase_english_words(embed.title) + "-" + str(message.id))
        exclude_categories=["連絡","終了済","TRPGシナリオ"]
        await delete_channels_containing(guild, str(ids), exclude_categories)
        if role != None:
            await role.delete()
        await channel.delete()
    except:
        try:
            await interaction.response.send_message(content="削除に失敗しました。",ephemeral=True)
        except:
            return

@client.event
async def on_message(message):
    # 説明関連
    if message.reference:
        original_message = await message.channel.fetch_message(message.reference.message_id)
        if original_message.embeds:
            if original_message.embeds[0].fields[0].value == message.author.display_name:
                new_content = original_message.content + "\n \n" + f"""### {message.content}"""
                await original_message.edit(content=new_content)
                await message.delete()
            # 指定された名前のフィールドを探す
            embed = original_message.embeds[0]
            if original_message.embeds[0].fields[0].value == message.author.display_name:
                return
            else:
                for index, field in enumerate(embed.fields):
                    if field.value == message.author.display_name:
                        # 次のフィールドが存在する場合
                        if index + 1 < len(embed.fields):
                            # 次のフィールドの値に返信内容を追加
                            embed.set_field_at(index + 1, name=embed.fields[index + 1].name, value=message.content+"\n \n", inline=False)
                            await original_message.edit(embed=embed)
            await message.delete()
                
    # HO用リアクション関連
    if message.author == client.user:
        if message.embeds:
            embed = message.embeds[0]
            embed.add_field(name="ID",value=message.id)
            guild = message.guild
            random_color = discord.Color(generate_random_color())

            await guild.create_role(name=embed.title + "-" + str(message.id),color=random_color)
            channel = await find_channel_in_category(guild, "連絡", lowercase_english_words(embed.title))
            await channel.edit(name=embed.title + "-" + str(message.id))
            await message.edit(embed=embed)

            role = discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
            bot = discord.utils.get(guild.roles, name=env_name.group().replace('\'', ''))
            overwrite = discord.PermissionOverwrite(view_channel=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await channel.set_permissions(bot, overwrite=overwrite)

            for field in embed.fields:
                if field.name == "HO1":
                    await message.add_reaction('1️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho1"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO2":
                    await message.add_reaction('2️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho2"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO3":
                    await message.add_reaction('3️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho3"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO4":
                    await message.add_reaction('4️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho4"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO5":
                    await message.add_reaction('5️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho5"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO6":
                    await message.add_reaction('6️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho6"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO7":
                    await message.add_reaction('7️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho7"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO8":
                    await message.add_reaction('8️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho8"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO9":
                    await message.add_reaction('9️⃣')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho9"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
                if field.name == "HO10":
                    await message.add_reaction('🔟')
                    channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho10"))
                    if channel != None:
                        await channel.edit(name=f"{embed.title}-{field.name}-{message.id}")
            

@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    user_name = user.display_name
    if user.name == env_name.group().replace('\'', ''):
        return
    else :
        if message.embeds[0]:
            embed = message.embeds[0]
            if reaction.emoji == '1️⃣':
                for field in embed.fields:
                    if field.name == "HO1":
                        embed.set_field_at(1, name="HO1", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho1-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '2️⃣':
                for field in embed.fields:
                    if field.name == "HO2":
                        embed.set_field_at(3, name="HO2", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho2-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '3️⃣':
                for field in embed.fields:
                    if field.name == "HO3":
                        embed.set_field_at(5, name="HO3", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho3-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '4️⃣':
                for field in embed.fields:
                    if field.name == "HO4":
                        embed.set_field_at(7, name="HO4", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho4-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '5️⃣':
                for field in embed.fields:
                    if field.name == "HO5":
                        embed.set_field_at(9, name="HO5", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho5-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '6️⃣':
                for field in embed.fields:
                    if field.name == "HO6":
                        embed.set_field_at(11, name="HO6", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho6-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '7️⃣':
                for field in embed.fields:
                    if field.name == "HO7":
                        embed.set_field_at(13, name="HO7", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho7-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '8️⃣':
                for field in embed.fields:
                    if field.name == "HO8":
                        embed.set_field_at(15, name="HO8", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho8-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '9️⃣':
                for field in embed.fields:
                    if field.name == "HO9":
                        embed.set_field_at(17, name="HO9", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho9-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)
            elif reaction.emoji == '🔟':
                for field in embed.fields:
                    if field.name == "HO10":
                        embed.set_field_at(19, name="HO10", value=user_name)
                        guild = message.guild
                        role =discord.utils.get(guild.roles, name=embed.title + "-" + str(message.id))
                        if role is None:
                            return
                        await user.add_roles(role)
                        channel = await find_channel_in_category(guild, "秘匿", lowercase_english_words(f"{embed.title}-ho10-{message.id}"))
                        if channel != None:
                            await channel.set_permissions(user, read_messages=True)
                await message.edit(embed=embed)

        if all(x.value != "未設定" for x in embed.fields[1::2]):
            # 他のロールは閲覧できないようにする
            everyone_role = guild.default_role
            overwrite = discord.PermissionOverwrite(view_channel=False)
            channel = discord.utils.get(guild.channels, name=lowercase_english_words(embed.title + "-" + str(message.id)))
            await channel.set_permissions(everyone_role, overwrite=overwrite)
        else:
            return

            
            

# botの停止に関する動作
@tree.command(name="kill",description="Botを停止します")
@app_commands.default_permissions(administrator=True)
async def kill_command(interaction: discord.Interaction,text:str):
    if text ==  env_kill.group().replace('\'', ''):
        await interaction.response.send_message("終了中。。。",ephemeral=False)
        sys.exit()
    else :
        await interaction.response.send_message("失敗しました。",ephemeral=False)

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)