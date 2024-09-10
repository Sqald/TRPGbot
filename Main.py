# 外部プログラムのインポート
import discord
from discord import app_commands
import asyncio
import mysql.connector
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

DBHost_name = [s for s in env if re.match('.*DBHost.*', s)]
DBHost = re.search('\'.*.\'',DBHost_name[0]).group().replace('\'', '')

DBPort_name = [s for s in env if re.match('.*DBPort.*', s)]
DBPort = re.search('\'.*.\'',DBPort_name[0]).group().replace('\'', '')

DBUser_name = [s for s in env if re.match('.*DBUser.*', s)]
DBUser = re.search('\'.*.\'',DBUser_name[0]).group().replace('\'', '')

DBPassword_name = [s for s in env if re.match('.*DBPassword.*', s)]
DBPassword = re.search('\'.*.\'',DBPassword_name[0]).group().replace('\'', '')

DBName_name = [s for s in env if re.match('.*DBName.*', s)]
DBName = re.search('\'.*.\'',DBName_name[0]).group().replace('\'', '')

print(DBHost,DBName,DBPassword,DBUser)
try:
    conn = mysql.connector.connect(host=DBHost ,port=int(DBPort) ,user=DBUser, password=DBPassword)
    curs = conn.cursor()

    print("Connect")
except:
    print("Database connection failed. Please check connection settings and server status and restart.")

conn.ping(reconnect=True)

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
    dice = await guild.create_category_channel(name="ダイス")
    dices = await dice.create_text_channel(name="ダイス")
    # カテゴリ内にテキストチャンネルを作成
    
    #権限の変更
    everyone_role = guild.default_role
    write = discord.PermissionOverwrite(send_messages=False)
    await trpg.set_permissions(everyone_role, overwrite=write)

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
        kp_id = interaction.user.id
        guild_id = guild.id
        
        result = await find_channel_link(guild, channel_name, exclude_categories)
        if result == None:
            result = ""
        contents = f"""# {name} \n\n{result}"""
        message = await channel.send(f"{contents}\n\n",embed=embed)
        message_id = message.id
        guild_id = guild.id
        if message.channel.category:
            category_id = message.channel.category.id
        channel_id = message.channel.id
        random_color = discord.Color(generate_random_color())

        try:
            role = await guild.create_role(name=embed.title, color=random_color)

            role_id = role.id
            bot = discord.utils.get(guild.roles, name=env_name.group().replace('\'', ''))
            overwrite = discord.PermissionOverwrite(view_channel=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await channel.set_permissions(bot, overwrite=overwrite)

            list_id= [guild_id,category_id,channel_id,message_id,role_id,name,kp_id,member]

            curs.execute(f"USE {DBName}")
            curs.execute('insert into messageDB (guild_id,category_id,channel_id,message_id,role_id,Name,KP_id,Count) values (%s, %s, %s, %s, %s, %s, %s, %s)', list_id)
            conn.commit()
        except:
            await interaction.followup.send("データベースの編集に失敗しました。",ephemeral=True)
        for i in range(1,member+1):
            embed.add_field(name=f"HO{i}",value="未設定", inline=False)
            embed.add_field(name=f"HO{i} PC",value="未設定", inline=False)
            await message.edit(embed=embed)
            print(i)
            if menu:
                ho = await category2.create_text_channel(f"{name}-HO{i}")
                try:
                    list_id= [guild_id,category_id,channel_id,message_id,ho.id]
                    curs.execute(f"USE {DBName}")
                    curs.execute('insert into secretDB (guild_id,category_id,channel_id,message_id,secret_channel_id) values (%s, %s, %s, %s, %s)', list_id)
                    conn.commit()
                except:
                    await interaction.followup.send("秘匿データベースの作成に失敗しました。",ephemeral=True)
                everyone_role = guild.default_role
                kp = discord.PermissionOverwrite(view_channel=True)
                overwrite = discord.PermissionOverwrite(view_channel=False)
                await ho.set_permissions(everyone_role, overwrite=overwrite)
                await ho.set_permissions(interaction.user, overwrite=kp)

        #HO用リアクション作成
        message = await channel.fetch_message(message.id)
        embed = message.embeds[0]
        embed.add_field(name="ID",value=message.id)
        await message.edit(embed=embed)
        for field in embed.fields:
                if field.name == "HO1":
                    await message.add_reaction('1️⃣')
                if field.name == "HO2":
                    await message.add_reaction('2️⃣')
                if field.name == "HO3":
                    await message.add_reaction('3️⃣')
                if field.name == "HO4":
                    await message.add_reaction('4️⃣')
                if field.name == "HO5":
                    await message.add_reaction('5️⃣')
                if field.name == "HO6":
                    await message.add_reaction('6️⃣')
                if field.name == "HO7":
                    await message.add_reaction('7️⃣')
                if field.name == "HO8":
                    await message.add_reaction('8️⃣')
                if field.name == "HO9":
                    await message.add_reaction('9️⃣')
                if field.name == "HO10":
                    await message.add_reaction('🔟')

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
    delhitoku="True:秘匿を削除 Fales:秘匿を削除しない"
)
async def close_command(interaction: discord.Interaction, delhitoku:bool):
    try:
        guild = interaction.guild
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT role_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id}")
        role_id = curs.fetchone()
        role = guild.get_role(role_id[0])
        everyone_role = guild.default_role
        overwrite = discord.PermissionOverwrite(view_channel=True)
        channel = interaction.channel
        category = discord.utils.get(guild.categories, name="終了済")
        if delhitoku:
            try:
                curs.execute(f"USE {DBName}")
                curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE channel_id = {interaction.channel.id} AND guild_id = {guild.id}")
                hitoku_id = curs.fetchall()
                for i in hitoku_id:
                    hitoku_channel = guild.get_channel(i[0])
                    await hitoku_channel.delete()
                curs.execute(f"DELETE FROM secretDB WHERE channel_id = {interaction.channel.id}")
            except:
                await interaction.response.send_message(content="秘匿の削除に失敗しました。",ephemeral=True)
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
async def delete_command(interaction: discord.Interaction):
    try:
        message = interaction.message
        guild = interaction.guild
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT role_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id}")
        role_id = curs.fetchone()
        role = guild.get_role(role_id[0])
        channel = interaction.channel
        try:
            curs.execute(f"USE {DBName}")
            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE channel_id = {interaction.channel.id} AND guild_id = {guild.id}")
            hitoku_id = curs.fetchall()
            for i in hitoku_id:
                hitoku_channel = guild.get_channel(i[0])
                await hitoku_channel.delete()
            curs.execute(f"DELETE FROM secretDB WHERE channel_id = {interaction.channel.id}")
        except:
            await interaction.response.send_message(content="秘匿の削除に失敗しました。",ephemeral=True)
        try:
            await channel.delete()
            if role != None:
                await role.delete()
        except:
            pass
        curs.execute(f"DELETE FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id}")
    except:
        try:
            await interaction.response.send_message(content="削除に失敗しました。",ephemeral=True)
        except:
            return

@tree.command(name="debug",description="開発時以外使用しないでください。復元できない致命的な操作を行う可能性があります。")
@app_commands.describe(
    select="メニューを選択してください。",
)
async def debug_command(interaction: discord.Interaction, select:str):
    await interaction.response.defer(ephemeral=True) 
    guild = interaction.guild
    channel = interaction.channel
    category = channel.category
    if select == "role":
        for role in guild.roles :
            print(role.name)
            if role.is_default():
                continue  # デフォルトロールは削除できない
            elif role.name == env_name.group().replace('\'', ''):
                continue
            await role.delete()
        await interaction.followup.send(f"削除しました。",ephemeral=True)
    elif select == "channel":
        for i in category.channels:
            await i.delete()
        await interaction.followup.send(f"削除しました。",ephemeral=True)

@tree.command(name="roll",description="ダイスを振ります。")
@app_commands.describe(
    dices="振るダイスの数",
    num="振るダイスの出目数",
    count="ダイスを振る回数",
    vision="自分以外に見せない場合はTrueを選択してください",
)
async def roll_command(interaction: discord.Interaction, dices:int, num:int, count:int=1, vision:bool=False):
    try:
        dice_text=""
        for i in range(1, count+1):
            counter=[]
            for a in range(dices):
                counter.append(random.randrange(1,num))
            dice_text = dice_text + f"#{i} {counter} = {sum(counter)} \n\n" 
        await interaction.response.send_message(content=f"{dice_text}",ephemeral=vision)
    except:
        try:
            await interaction.response.send_message(content="ロールに失敗しました。",ephemeral=True)
        except:
            return


@client.event
async def on_message(message):
    # 説明関連
    if message.reference:
        if message.author != client.user:
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

@client.event
async def on_raw_reaction_add(reaction):
    guild = client.get_guild(reaction.guild_id)
    channel = await guild.fetch_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    user = reaction.member
    user_name = user.display_name
    if user.name == env_name.group().replace('\'', ''):
        pass
    else :
        if message.embeds[0]:
            embed = message.embeds[0]
            if reaction.emoji.name == '1️⃣':
                for field in embed.fields:
                    if field.name == "HO1":
                        embed.set_field_at(1, name="HO1", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '2️⃣':
                for field in embed.fields:
                    if field.name == "HO2":
                        embed.set_field_at(3, name="HO2", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '3️⃣':
                for field in embed.fields:
                    if field.name == "HO3":
                        embed.set_field_at(5, name="HO3", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '4️⃣':
                for field in embed.fields:
                    if field.name == "HO4":
                        embed.set_field_at(7, name="HO4", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '5️⃣':
                for field in embed.fields:
                    if field.name == "HO5":
                        embed.set_field_at(9, name="HO5", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '6️⃣':
                for field in embed.fields:
                    if field.name == "HO6":
                        embed.set_field_at(11, name="HO6", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '7️⃣':
                for field in embed.fields:
                    if field.name == "HO7":
                        embed.set_field_at(13, name="HO7", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '8️⃣':
                for field in embed.fields:
                    if field.name == "HO8":
                        embed.set_field_at(15, name="HO8", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '9️⃣':
                for field in embed.fields:
                    if field.name == "HO9":
                        embed.set_field_at(17, name="HO9", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue
            elif reaction.emoji.name == '🔟':
                for field in embed.fields:
                    if field.name == "HO10":
                        embed.set_field_at(19, name="HO10", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0])
                            if role is None:
                                continue
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_channel_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = guild.get_channel(hitoku_id[0])
                            if hitoku_channel != None:
                                await channel.set_permissions(user, read_messages=True)
                        except:
                            continue

        if all(x.value != "未設定" for x in embed.fields[1::2]):
            # 他のロールは閲覧できないようにする
            everyone_role = guild.default_role
            overwrite = discord.PermissionOverwrite(view_channel=False)
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