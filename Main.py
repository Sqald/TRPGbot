# 外部プログラムのインポート
import discord
from discord import app_commands
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

# 自分のBotのアクセストークンに置き換えてください
TOKEN = env_token.group().replace('\'', '')

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

# 起動時に動作する処理
tree = app_commands.CommandTree(client)
@client.event
async def on_ready():
    print("起動完了")
    await tree.sync()#スラッシュコマンドを同期

# スラッシュコマンドに関する動作
@tree.command(name="test",description="テストコマンドです。")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("てすと！",ephemeral=False)
    print(interaction.guild)

@tree.command(name="new",description="新しいイベントを作成します。シナリオ説明はこのテキストに返信して追加することができます。")
@app_commands.describe(
    name="タイトルを指定してください",
    menu="使うシナリオを選択してください 1:ソープスクール 2:その他",
    style="TRPG仕様を選択してください 1:CoC6版 2:その他",
    member="HOの数を入力してください (10まで対応)",
    densuke="伝助などのURLを入力してください。",
    url="BoothなどのURLを入力してください。"
)
async def new_command(interaction: discord.Interaction, name:str, style:int ,menu:int, member:int, url:str=None, densuke:str=None):
    if style == 1:
        style = "CoC6版"
    elif style == 2:
        style = "その他"
    else :
        style = "指定失敗"
    embed = discord.Embed(title=f"{name}",color=0x7fffd4, description=f"""# {name} \n## {style} """, url=url)
    embed.add_field(name="KP",value=interaction.user.display_name, inline=False)
    embed.set_author(name="伝助", url=densuke)
    contents = f"""# {name}"""
    for i in range(1,member+1):
        embed.add_field(name=f"HO{i}",value="未設定", inline=False)
        embed.add_field(name=f"HO{i} PC",value="未設定", inline=False)
    await interaction.response.send_message(content=contents,embed=embed,ephemeral=False)

@tree.command(name="densuke",description="新しいイベントを作成します。シナリオ説明はこのテキストに返信して追加することができます。")
@app_commands.describe(
    densuke="伝助のURLを入力してください。"
)
async def densuke_command(interaction: discord.Interaction, ids:str, densuke:str=None):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        embed = message.embeds[0]
        embed.set_author(name="伝助", url=densuke)
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

@tree.command(name="booth",description="新しいイベントを作成します。シナリオ説明はこのテキストに返信して追加することができます。")
@app_commands.describe(
    url="BoothのURLを入力してください。"
)
async def booth_command(interaction: discord.Interaction, ids:str, url:str=None):
    try:
        message = await interaction.channel.fetch_message(int(ids))
        embed = message.embeds[0]
        embed.url = url
        await message.edit(embed=embed)
        await interaction.response.send_message(content="設定しました。",ephemeral=True)
    except:
        await interaction.response.send_message(content="設定に失敗しました。",ephemeral=True)

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
                await message.edit(embed=embed)
            elif reaction.emoji == '2️⃣':
                for field in embed.fields:
                    if field.name == "HO2":
                        embed.set_field_at(3, name="HO2", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '3️⃣':
                for field in embed.fields:
                    if field.name == "HO3":
                        embed.set_field_at(5, name="HO3", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '4️⃣':
                for field in embed.fields:
                    if field.name == "HO4":
                        embed.set_field_at(7, name="HO4", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '5️⃣':
                for field in embed.fields:
                    if field.name == "HO5":
                        embed.set_field_at(9, name="HO5", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '6️⃣':
                for field in embed.fields:
                    if field.name == "HO6":
                        embed.set_field_at(11, name="HO6", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '7️⃣':
                for field in embed.fields:
                    if field.name == "HO7":
                        embed.set_field_at(13, name="HO7", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '8️⃣':
                for field in embed.fields:
                    if field.name == "HO8":
                        embed.set_field_at(15, name="HO8", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '9️⃣':
                for field in embed.fields:
                    if field.name == "HO9":
                        embed.set_field_at(17, name="HO9", value=user_name)
                await message.edit(embed=embed)
            elif reaction.emoji == '🔟':
                for field in embed.fields:
                    if field.name == "HO10":
                        embed.set_field_at(19, name="HO10", value=user_name)
                await message.edit(embed=embed)
            
            

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