import discord
from discord.ext import commands
from discord import Option # Importação correta
from db_manager import encontrar_processo_por_id
from admin_modals import AlterarNivelForm, RevogarPorteForm

# --- VIEW COM OS BOTÕES DE ADMINISTRAÇÃO ---
class VerificacaoAdminView(discord.ui.View):
    def __init__(self, numero_processo: str, dados_processo: dict):
        super().__init__(timeout=None) # Botões Permanentes para uma mensagem pública
        self.numero_processo = numero_processo
        self.dados_processo = dados_processo

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        NOME_CARGO_POLICIA = "Policial Civil"
        tem_cargo = discord.utils.get(interaction.user.roles, name=NOME_CARGO_POLICIA)
        if not tem_cargo:
            await interaction.response.send_message("🚫 Apenas a Polícia Civil pode usar estas opções.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Alterar Porte", style=discord.ButtonStyle.secondary, emoji="✏️", custom_id="admin_alterar_porte_v2")
    async def alterar_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Esta versão passa a mensagem original para ser editada
        await interaction.response.send_modal(
            AlterarNivelForm(self.numero_processo, self.dados_processo, interaction.message)
        )
        
    @discord.ui.button(label="Revogar Porte", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="admin_revogar_porte_v2")
    async def revogar_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Esta versão passa a mensagem original para ser editada
        await interaction.response.send_modal(
            RevogarPorteForm(self.numero_processo, self.dados_processo, interaction.message)
        )

# --- O COMANDO DE BARRA /verificar_porte ---
class ConsultaCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="verificar_porte",
        description="Verifica o status de um porte de arma pela identidade."
    )
    async def verificar_porte(self, ctx: discord.ApplicationContext, 
        identidade: Option(str, "A identidade (ID) do cidadão a ser verificado.")
    ):
        numero_processo, dados = encontrar_processo_por_id(identidade)

        if dados is None or dados.get("status") not in ["Porte Emitido", "Revogado"]:
            await ctx.respond(f"ℹ️ Nenhum porte de arma (emitido ou revogado) encontrado para a ID `{identidade}`.", ephemeral=True)
            return

        cor_embed = discord.Color.dark_grey()
        if dados['status'] == 'Revogado':
            cor_embed = discord.Color.dark_red()
        elif dados['status'] == 'Porte Emitido':
            cor_embed = discord.Color.green()

        embed = discord.Embed(
            title=f"Consulta de Porte - {dados['nome']}",
            color=cor_embed
        )
        embed.add_field(name="Nível", value=f"**Nível {dados['nivel_porte']}**", inline=False)
        embed.add_field(name="Nome", value=dados['nome'], inline=False)
        embed.add_field(name="Identidade (ID)", value=dados['identidade'], inline=False)
        embed.add_field(name="Status", value=f"`{dados['status']}`", inline=False)

        if 'log_alteracao' in dados:
            log = dados['log_alteracao']
            texto_log = (f"De `Nível {log['de_nivel']}` para `Nível {log['para_nivel']}` em {log['data']}\n"
                         f"**Admin:** {log['admin']}\n"
                         f"**Motivo:** {log['motivo']}")
            embed.add_field(name="Última Alteração de Nível", value=texto_log, inline=False)
        
        if 'log_revogacao' in dados:
            log = dados['log_revogacao']
            texto_log = (f"Revogado em {log['data']} por {log['admin']}\n"
                         f"**Motivo:** {log['motivo']}")
            embed.add_field(name="Informações da Revogação", value=texto_log, inline=False)
        
        view_para_enviar = discord.ui.View(timeout=None)
        if dados['status'] == 'Porte Emitido':
            view_para_enviar = VerificacaoAdminView(numero_processo, dados)
            embed.set_footer(text="Ações administrativas disponíveis abaixo (apenas Polícia Civil).")

        # A ALTERAÇÃO ESTÁ AQUI: removemos ephemeral=True para a resposta ser PÚBLICA
        await ctx.respond(embed=embed, view=view_para_enviar)

def setup(bot):
    bot.add_cog(ConsultaCommands(bot))