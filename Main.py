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
    menu="使うシナリオを選択してください 1:ソープスクール 2:その他",
)
async def new_command(interaction: discord.Interaction, name:str, menu:int):
    embed = discord.Embed(title=f"{name}",color=0x7fffd4, description=f"")
    await interaction.response.send_message(embed=embed,ephemeral=False)

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