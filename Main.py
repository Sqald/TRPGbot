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
print(env_num_token[0])
env_token = re.search('\'.*.\'',env_num_token[0])
print(env_token.group().replace('\'', ''))

env_num_kill = [s for s in env if re.match('.*killPass.*', s)]
print(env_num_kill[0])
env_kill = re.search('\'.*.\'',env_num_kill[0])
print(env_kill.group().replace('\'', ''))

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

@tree.command(name="new",description="新しいイベントを作成します。")
@app_commands.describe(
    name="設定名を選択してください",
    menu="使うシナリオを選択してください 1:ソープスクール 2:その他",
    style="TRPG仕様を選択してください 1:CoC6版 2:その他",
    member="HOの数を入力してください (10まで対応)",
    desc= "説明を入力してください"
)
async def new_command(interaction: discord.Interaction, name:str, style:int ,menu:int, member:int, desc:str):
    if style == 1:
        style = "CoC6版"
    elif style == 2:
        style = "その他"
    else :
        style = "指定失敗"
    HO1 = "未設定"
    embed = discord.Embed(title=f"{name}",color=0x7fffd4, description=f"""# {name} \n## {style} \n### {desc} """)
    for i in range(1,member+1):
        embed.add_field(name=f"HO{i}",value="未設定")
    await interaction.response.send_message(embed=embed,ephemeral=False)

@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    user_name = user.display_name
    if message.embeds[0]:
        embed = message.embeds[0]
        if reaction.emoji == '1️⃣':
            for field in embed.fields:
                if field.name == "HO1":
                    embed.set_field_at(0, name="HO1", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '2️⃣':
            for field in embed.fields:
                if field.name == "HO2":
                    embed.set_field_at(1, name="HO2", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '3️⃣':
            for field in embed.fields:
                if field.name == "HO3":
                    embed.set_field_at(2, name="HO3", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '4️⃣':
            for field in embed.fields:
                if field.name == "HO4":
                    embed.set_field_at(3, name="HO4", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '5️⃣':
            for field in embed.fields:
                if field.name == "HO5":
                    embed.set_field_at(4, name="HO5", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '6️⃣':
            for field in embed.fields:
                if field.name == "HO6":
                    embed.set_field_at(5, name="HO6", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '7️⃣':
            for field in embed.fields:
                if field.name == "HO7":
                    embed.set_field_at(6, name="HO7", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '8️⃣':
            for field in embed.fields:
                if field.name == "HO8":
                    embed.set_field_at(7, name="HO8", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '9️⃣':
            for field in embed.fields:
                if field.name == "HO9":
                    embed.set_field_at(8, name="HO9", value=user_name)
            await message.edit(embed=embed)
        elif reaction.emoji == '🔟':
            for field in embed.fields:
                if field.name == "HO10":
                    embed.set_field_at(9, name="HO10", value=user_name)
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