import discord
from discord.ext import commands
from discord.commands import Option
from db_manager import encontrar_processo_por_id, limpar_processo_por_id

# --- VIEW (BOTÕES) PARA CONFIRMAÇÃO DA LIMPEZA ---
class LimparConfirmView(discord.ui.View):
    def __init__(self, numero_processo: str, dados_processo: dict, interaction_original: discord.Interaction):
        super().__init__(timeout=60) # Botões expiram em 1 minuto
        self.numero_processo = numero_processo
        self.dados_processo = dados_processo
        self.interaction_original = interaction_original

    async def on_timeout(self):
        # Edita a mensagem original para mostrar que o tempo esgotou
        for item in self.children:
            item.disabled = True
        try:
            await self.interaction_original.edit_original_response(
                content="⌛ **Tempo Esgotado.**\nA ação de limpeza foi cancelada.",
                view=self
            )
        except discord.errors.NotFound:
            # A mensagem pode já ter sido respondida ou apagada, ignora o erro
            pass

    @discord.ui.button(label="Confirmar Limpeza", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        processo_removido = limpar_processo_por_id(self.numero_processo)
        
        for item in self.children:
            item.disabled = True
        
        if processo_removido:
            await interaction.response.edit_message(
                content=f"✅ **Histórico Removido!**\nO processo de **{processo_removido['nome']}** (ID: {processo_removido['identidade']}) foi permanentemente apagado da base de dados.",
                view=self
            )
        else:
             await interaction.response.edit_message(
                content="❌ **Erro!** O processo não pôde ser encontrado para limpeza. Talvez já tenha sido removido.",
                view=self
            )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(
            content="🚫 **Ação Cancelada.**\nNenhuma alteração foi feita.",
            view=self
        )

# --- O COMANDO DE BARRA /limpar_id ---
class LimpezaCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="limpar_id",
        description="Apaga PERMANENTEMENTE todo o histórico de um cidadão da base de dados."
    )
    @commands.has_role("Policial Civil") # Apenas Polícia Civil pode usar
    async def limpar_id(self, ctx: discord.ApplicationContext, 
        identidade: Option(str, "A identidade (ID) do cidadão a ser limpo.")
    ):
        numero_processo, dados = encontrar_processo_por_id(identidade)

        if dados is None:
            await ctx.respond(f"❌ Nenhum processo encontrado para a ID `{identidade}`.", ephemeral=True)
            return

        confirm_text = (
            f"🚨 **ATENÇÃO: AÇÃO IRREVERSÍVEL** 🚨\n\n"
            f"Você está prestes a apagar **TODO** o histórico do cidadão abaixo:\n\n"
            f"👤 **Nome:** {dados.get('nome', 'N/A')}\n"
            f"💳 **ID:** {dados.get('identidade', 'N/A')}\n"
            f"⚖️ **Processo Nº:** {numero_processo}\n"
            f"📈 **Status Atual:** `{dados.get('status', 'N/A')}`\n\n"
            f"Esta ação **NÃO PODE SER DESFEITA**. Deseja continuar?"
        )

        await ctx.respond(
            confirm_text,
            view=LimparConfirmView(numero_processo, dados, ctx.interaction),
            ephemeral=True # A mensagem de confirmação é privada para o admin
        )

    # --- NOVA FUNÇÃO DE TRATAMENTO DE ERRO ---
    @limpar_id.error
    async def limpar_id_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        # Verifica se o erro é especificamente sobre um cargo em falta
        if isinstance(error, commands.MissingRole):
            await ctx.respond("🚫 **Acesso Negado.**\nVocê não possui permissão para utilizar este comando.", ephemeral=True)
        else:
            # Para outros tipos de erro, podemos enviar uma mensagem genérica e imprimir o erro no terminal
            print(f"Ocorreu um erro inesperado no comando /limpar_id: {error}")
            await ctx.respond("❌ Ocorreu um erro inesperado ao executar este comando.", ephemeral=True)


def setup(bot):
    bot.add_cog(LimpezaCommands(bot))