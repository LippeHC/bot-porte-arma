import discord
# Importa TODAS as classes de formulário que vamos usar do modals.py
from modals import PorteForm, LaudoForm, EmissaoPorteForm

# A View principal que contém os 3 botões do painel de controle
class PainelView(discord.ui.View):
    def __init__(self):
        # timeout=None garante que os botões nunca expirem
        super().__init__(timeout=None)

    # --- Botão do Advogado ---
    @discord.ui.button(label="Advogado", style=discord.ButtonStyle.green, custom_id="botao_advogado")
    async def advogado_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Coloque aqui o nome exato do cargo no seu Discord
        NOME_CARGO_ADVOGADO = "Advogado"
        cargo_encontrado = discord.utils.get(interaction.user.roles, name=NOME_CARGO_ADVOGADO)

        if cargo_encontrado is None:
            await interaction.response.send_message(
                f"🚫 **Área Restrita!** Apenas membros com o cargo `{NOME_CARGO_ADVOGADO}` podem aceder.",
                ephemeral=True
            )
            return

        # Se o cargo for encontrado, abre o formulário do advogado
        await interaction.response.send_modal(PorteForm())

    # --- Botão do Médico ---
    @discord.ui.button(label="Médico", style=discord.ButtonStyle.blurple, custom_id="botao_medico")
    async def medico_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Coloque aqui o nome exato do cargo no seu Discord
        NOME_CARGO_MEDICO = "Médico" # ou "Psicólogo"
        cargo_encontrado = discord.utils.get(interaction.user.roles, name=NOME_CARGO_MEDICO)

        if cargo_encontrado is None:
            await interaction.response.send_message(
                f"🚫 **Área Restrita!** Apenas membros com o cargo `{NOME_CARGO_MEDICO}` podem aceder.",
                ephemeral=True
            )
            return

        # Se o cargo for encontrado, abre o formulário do médico
        await interaction.response.send_modal(LaudoForm())

    # --- Botão do Policial Civil ---
    @discord.ui.button(label="Policial Civil", style=discord.ButtonStyle.red, custom_id="botao_policial")
    async def policial_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Coloque aqui o nome exato do cargo no seu Discord
        NOME_CARGO_POLICIA = "Policial Civil"
        cargo_encontrado = discord.utils.get(interaction.user.roles, name=NOME_CARGO_POLICIA)

        if cargo_encontrado is None:
            await interaction.response.send_message(
                f"🚫 **Área Restrita!** Apenas membros com o cargo `{NOME_CARGO_POLICIA}` podem aceder.",
                ephemeral=True
            )
            return
        
        # Se o cargo for encontrado, abre o formulário do policial
        await interaction.response.send_modal(EmissaoPorteForm())