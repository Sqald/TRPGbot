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

async def delete_channels_containing(guild, name_id, exclude_categories):
    try:
        for category in guild.categories:
            if category.name not in exclude_categories:
                for channel in category.channels:
                    if name_id in channel.name:
                        await channel.delete()
    except:
        return


@tree.command(name="new",description="新しいイベントを作成します。シナリオ説明はこのテキストに返信して追加することができます。")
@app_commands.describe(
    name="チャンネル名を指定してください。",
    menu="秘匿の有無を選択してください 有:True 無:False",
    member="HOの数を入力してください (10まで対応)",
    densuke="伝助などのURLを入力してください。",
    url="BoothなどのURLを入力してください。"
)
async def new_command(interaction: discord.Interaction, name:str, menu:bool, member:int, url:str=None, densuke:str=None, ccfolia:str=None):
    await interaction.response.defer(ephemeral=True) 
    ccfolia_set = ""
    if ccfolia != None:
        ccfolia_set = f"[CCFOLIA]({ccfolia})"
    try:
        guild = interaction.guild
        category = interaction.channel.category
        channel = await category.create_text_channel(name)
        everyone_role = guild.default_role
        overwrite = discord.PermissionOverwrite(view_channel=False)
        await channel.set_permissions(everyone_role, overwrite=overwrite)
        embed = discord.Embed(title=f"{name}",color=0x7fffd4, description=f"""# {name}\n\n{ccfolia_set}""", url=url)
        embed.add_field(name="KP",value=interaction.user.display_name, inline=False)
        embed.set_author(name="伝助", url=densuke)
        channel_name = name
        kp_id = interaction.user.id
        guild_id = guild.id
        contents = f"""# {name} \n\n{interaction.channel.mention}"""
        message = await channel.send(f"{contents}\n\n",embed=embed)
        message_id = message.id
        guild_id = guild.id
        if message.channel.category:
            category_id = message.channel.category.id
        channel_id = message.channel.id
        random_color = discord.Color(generate_random_color())

        try:
            role = await guild.create_role(name=embed.title, color=random_color)
            new_content = message.content + f"\n{role.mention}"
            await message.edit(content=new_content)
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
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {interaction.channel.category.id} AND guild_id = {guild.id} ORDER BY HO_num")
        hitoku_ch = curs.fetchall()
        for i in range(1,member+1):
            embed.add_field(name=f"HO{i}",value="未設定", inline=False)
            embed.add_field(name=f"HO{i} PC",value="未設定", inline=False)
            await message.edit(embed=embed)
            if menu:
                try:
                    ho = guild.get_channel(hitoku_ch[i-1][0])
                    thread = await ho.create_thread(name=f"HO{i}相談")
                    list_id= [guild_id,category_id,channel_id,message_id,thread.id]
                    curs.execute(f"USE {DBName}")
                    curs.execute('insert into secretDB (guild_id,category_id,channel_id,message_id,secret_thread_id) values (%s, %s, %s, %s, %s)', list_id)
                    conn.commit()
                    everyone_role = guild.default_role
                    kp = discord.PermissionOverwrite(view_channel=True)
                    overwrite = discord.PermissionOverwrite(view_channel=False)
                    await ho.set_permissions(everyone_role, overwrite=overwrite)
                    await ho.set_permissions(interaction.user, overwrite=kp)
                except:
                    await interaction.followup.send("秘匿データベースの作成に失敗しました。",ephemeral=True)
                

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
    densuke="伝助のURLを入力してください。"
)
async def densuke_command(interaction: discord.Interaction, densuke:str):
    try:
        guild = interaction.guild
        channel = interaction.channel
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT message_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id} ORDER BY id")
        message = channel.fetch_message(curs.fetchone()[0])
        embed = message.embeds[0]
        embed.set_author(name="伝助", url=densuke)
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="booth",description="イベント情報にシナリオの情報を追加することができます。")
@app_commands.describe(
    url="BoothのURLを入力してください。"
)
async def booth_command(interaction: discord.Interaction, url:str):
    try:
        guild = interaction.guild
        channel = interaction.channel
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT message_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id} ORDER BY id")
        message = await channel.fetch_message(curs.fetchone()[0])
        embed = message.embeds[0]
        embed.url = url
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="ccfolia",description="イベント情報にCCFOLIAを追加することができます。")
@app_commands.describe(
    ccfolia="CCFOLIAのURLを入力してください。"
)
async def ccfolia_command(interaction: discord.Interaction, ccfolia:str):
    try:
        guild = interaction.guild
        channel = interaction.channel
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT message_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id} ORDER BY id")
        message_id = curs.fetchone()
        message = await channel.fetch_message(message_id[0])
        embed = message.embeds[0]
        embed.description = embed.description + f"\n\n[CCFOLIA]({ccfolia})"
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="close",description="イベント用に作成した関連品を削除することができます。実行は当該チャンネルのみで行うことができます。")
@app_commands.describe(
    delhitoku="True:秘匿を削除 False:秘匿を削除しない"
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
                curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE channel_id = {interaction.channel.id} AND guild_id = {guild.id} ORDER BY id")
                hitoku_id = curs.fetchall()
                curs.execute(f"USE {DBName}")
                curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {interaction.channel.category.id} AND guild_id = {guild.id} ORDER BY id")
                hitoku_ch = curs.fetchall()
                try:
                    a = 0
                    for i in hitoku_id:
                        ho_channel = guild.get_channel(hitoku_ch[a][0])
                        hitoku_channel = ho_channel.get_thread(i[0])
                        await hitoku_channel.delete()
                        a = a + 1
                    curs.execute(f"DELETE FROM secretDB WHERE channel_id = {interaction.channel.id}")
                except:
                    pass
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
        guild = interaction.guild
        curs.execute(f"USE {DBName}")
        curs.execute(f"SELECT role_id FROM messageDB WHERE channel_id = {interaction.channel.id} AND KP_id = {interaction.user.id} AND guild_id = {guild.id} ORDER BY id")
        role_id = curs.fetchone()
        role = guild.get_role(role_id[0])
        channel = interaction.channel
        try:
            curs.execute(f"USE {DBName}")
            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE channel_id = {interaction.channel.id} AND guild_id = {guild.id} ORDER BY id")
            hitoku_id = curs.fetchall()
            curs.execute(f"USE {DBName}")
            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {interaction.channel.category.id} AND guild_id = {guild.id} ORDER BY id")
            hitoku_ch = curs.fetchall()
            try:
                a = 0
                for i in hitoku_id:
                    ho_channel = guild.get_channel(hitoku_ch[a][0])
                    hitoku_channel = ho_channel.get_thread(i[0])
                    await hitoku_channel.delete()
                    a = a + 1
                curs.execute(f"DELETE FROM secretDB WHERE channel_id = {interaction.channel.id}")
            except:
                pass
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
    if interaction.user.guild_permissions.administrator:
        await interaction.response.defer(ephemeral=True) 
        guild = interaction.guild
        channel = interaction.channel
        category = channel.category
        if select == "role":
            for role in guild.roles :
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

@tree.command(name="sql",description="基本的には使用しないでください。復元できない致命的な操作を行う可能性があります。")
@app_commands.describe(
    sql="メニューを選択してください。",
)

async def debug_command(interaction: discord.Interaction, sql:str):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.defer(ephemeral=True) 
        curs.execute(f"USE {DBName}")
        curs.execute(f"{sql}")
        await interaction.followup.send(curs.fetchall(), ephemeral=True)

@tree.command(name="set",description="複数回使用しないでください。復元できない致命的な操作を行う可能性があります。")
@app_commands.describe(
    ho_num="HO番号を指定してください。",
)

async def debug_command(interaction: discord.Interaction, ho_num:int):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.defer(ephemeral=True) 
        guild = interaction.guild
        category = interaction.channel.category
        ho_channel = interaction.channel
        try:
            list_id = [ho_num,guild.id,category.id,ho_channel.id]
            curs.execute(f"USE {DBName}")
            curs.execute('insert into secretchannelDB (HO_num,guild_id,category_id,ho_channel_id) values (%s, %s, %s, %s)', list_id)
            conn.commit()
            await interaction.followup.send("セットしました。", ephemeral=True)
        except:
            await interaction.followup.send("データベース操作に失敗しました。", ephemeral=True)


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
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 1")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[0][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '2️⃣':
                for field in embed.fields:
                    if field.name == "HO2":
                        embed.set_field_at(3, name="HO2", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 2")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[1][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '3️⃣':
                for field in embed.fields:
                    if field.name == "HO3":
                        embed.set_field_at(5, name="HO3", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 3")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[2][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '4️⃣':
                for field in embed.fields:
                    if field.name == "HO4":
                        embed.set_field_at(7, name="HO4", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 4")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[3][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '5️⃣':
                for field in embed.fields:
                    if field.name == "HO5":
                        embed.set_field_at(9, name="HO5", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 5")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[4][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '6️⃣':
                for field in embed.fields:
                    if field.name == "HO6":
                        embed.set_field_at(11, name="HO6", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 6")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[5][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '7️⃣':
                for field in embed.fields:
                    if field.name == "HO7":
                        embed.set_field_at(13, name="HO7", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 7")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[6][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '8️⃣':
                for field in embed.fields:
                    if field.name == "HO8":
                        embed.set_field_at(15, name="HO8", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 8")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[7][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '9️⃣':
                for field in embed.fields:
                    if field.name == "HO9":
                        embed.set_field_at(17, name="HO9", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 9")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[8][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass
            elif reaction.emoji.name == '🔟':
                for field in embed.fields:
                    if field.name == "HO10":
                        embed.set_field_at(19, name="HO10", value=user_name)
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 10")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=True)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT role_id FROM messageDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            role_id = curs.fetchall()
                            role = guild.get_role(role_id[0][0])
                            if role is None:
                                pass
                            else:
                                await user.add_roles(role)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[9][0])
                            if hitoku_channel != None:
                                await hitoku_channel.send(f"<@{user.id}>")
                                await hitoku_channel.edit(name=hitoku_channel.name + f"-{user_name}さん")
                        except:
                            pass

@client.event
async def on_raw_reaction_remove(reaction):
    guild = client.get_guild(reaction.guild_id)
    channel = await guild.fetch_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    user = await guild.fetch_member(reaction.user_id)
    user_name = user.display_name
    if user.name == env_name.group().replace('\'', ''):
        pass
    else :
        if message.embeds[0]:
            embed = message.embeds[0]
            if reaction.emoji.name == '1️⃣':
                for field in embed.fields:
                    if field.name == "HO1":
                        embed.set_field_at(1, name="HO1", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 1")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[0][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO1相談")
                        except:
                            pass
            elif reaction.emoji.name == '2️⃣':
                for field in embed.fields:
                    if field.name == "HO2":
                        embed.set_field_at(3, name="HO2", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 2")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[1][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO2相談")
                        except:
                            pass
            elif reaction.emoji.name == '3️⃣':
                for field in embed.fields:
                    if field.name == "HO3":
                        embed.set_field_at(5, name="HO3", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 3")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[2][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO3相談")
                        except:
                            pass
            elif reaction.emoji.name == '4️⃣':
                for field in embed.fields:
                    if field.name == "HO4":
                        embed.set_field_at(7, name="HO4", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 4")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[3][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO4相談")
                        except:
                            pass
            elif reaction.emoji.name == '5️⃣':
                for field in embed.fields:
                    if field.name == "HO5":
                        embed.set_field_at(9, name="HO5", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 5")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[4][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO5相談")
                        except:
                            pass
            elif reaction.emoji.name == '6️⃣':
                for field in embed.fields:
                    if field.name == "HO6":
                        embed.set_field_at(11, name="HO6", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 6")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[5][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO6相談")
                        except:
                            pass
            elif reaction.emoji.name == '7️⃣':
                for field in embed.fields:
                    if field.name == "HO7":
                        embed.set_field_at(13, name="HO7", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 7")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[6][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO7相談")
                        except:
                            pass
            elif reaction.emoji.name == '8️⃣':
                for field in embed.fields:
                    if field.name == "HO8":
                        embed.set_field_at(15, name="HO8", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 8")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[7][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO8相談")
                        except:
                            pass
            elif reaction.emoji.name == '9️⃣':
                for field in embed.fields:
                    if field.name == "HO9":
                        embed.set_field_at(17, name="HO9", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 9")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[8][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO9相談")
                        except:
                            pass
            elif reaction.emoji.name == '🔟':
                for field in embed.fields:
                    if field.name == "HO10":
                        embed.set_field_at(19, name="HO10", value="未設定")
                        await message.edit(embed=embed)
                        try:
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT ho_channel_id FROM secretchannelDB WHERE category_id = {message.channel.category.id} AND guild_id = {guild.id} AND HO_num = 10")
                            ho_channel_id = curs.fetchone()
                            ho_channel = guild.get_channel(ho_channel_id[0])
                            if ho_channel != None:
                                await ho_channel.set_permissions(user, read_messages=False)
                            
                            curs.execute(f"USE {DBName}")
                            curs.execute(f"SELECT secret_thread_id FROM secretDB WHERE message_id = {message.id} AND guild_id = {guild.id}")
                            hitoku_id = curs.fetchall()
                            hitoku_channel = client.get_channel(hitoku_id[9][0])
                            if hitoku_channel != None:
                                await hitoku_channel.remove_user(user)
                                await hitoku_channel.edit(name="HO10相談")
                        except:
                            pass


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