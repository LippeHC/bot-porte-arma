import discord
import os
from dotenv import load_dotenv
from views import PainelView
from cogs.consulta_commands import VerificacaoAdminView
from keep_alive import keep_alive # Importa a função para manter o bot acordado

# Carrega as variáveis do ficheiro .env
load_dotenv()
# Lê o token de forma segura, sem o expor no código
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(intents=intents)

# Loop corrigido que carrega os ficheiros de comando e ignora o __init__.py
for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    # Regista as views permanentes para que os botões funcionem sempre
    bot.add_view(PainelView())
    bot.add_view(VerificacaoAdminView(numero_processo=None, dados_processo=None))
    
    print(f'Sucesso! O bot {bot.user} está online!')
    await bot.sync_commands()
    print("Comandos sincronizados com o Discord.")

# Inicia o servidor web para manter o bot acordado no Replit
keep_alive()

# Inicia o bot
print("A ligar o bot...")
bot.run(TOKEN)