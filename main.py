import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

room_owners = {}
room_counter = 1  # 部屋番号管理用

class RoomView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 部屋を作成", style=discord.ButtonStyle.primary, custom_id="create_vc")
    async def create_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        global room_counter
        guild = interaction.guild
        
        # 1. 部屋番号を付与
        room_name = f"#{room_counter:03} 部屋"
        room_counter += 1
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            interaction.user: discord.PermissionOverwrite(connect=True, manage_channels=True)
        }
        
        vc = await guild.create_voice_channel(room_name, overwrites=overwrites, user_limit=2) # 定員2名
        room_owners[vc.id] = interaction.user.id
        await interaction.response.send_message(f"{room_name} を作成しました。", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    # 満員チェック・VC名更新
    for vc_id, owner_id in room_owners.items():
        vc = member.guild.get_channel(vc_id)
        if not vc: continue
        
        # 人数に応じて名前を変更
        current_count = len(vc.members)
        new_name = vc.name.split("] ")[-1] # 番号部分を抽出
        
        if current_count >= vc.user_limit:
            await vc.edit(name=f"[満員] {new_name}")
        elif current_count == 0:
            # 誰もいなくなったら削除
            await vc.delete()
            del room_owners[vc_id]
            break
        else:
            await vc.edit(name=f"[空室] {new_name}")

    # 入室時のノック処理（以前のコードと同じ）
    if after.channel is not None and after.channel.id in room_owners:
        # (入室拒否とDM通知のロジックをここに配置...)
        pass

# ... (KnockViewやその他の処理は以前のものと同じ) ...
