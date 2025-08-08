import discord
from discord.ext import commands
from views import PainelView # Precisamos de importar a nossa View do outro ficheiro

class PanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # O comando de barra agora fica dentro desta classe
    @commands.slash_command(
        name="criar_painel",
        description="Envia o painel de controle de porte de arma no canal atual.",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    async def criar_painel(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Painel de Porte de Arma",
            description="Selecione uma das opções abaixo para iniciar o seu processo.",
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="Bot Jurídico")

        # Envia a mensagem com os botões (a View)
        await ctx.send(embed=embed, view=PainelView())
        await ctx.respond("Painel criado com sucesso!", ephemeral=True)

# Função especial que o main.py vai usar para registar este Cog
def setup(bot):
    bot.add_cog(PanelCog(bot))