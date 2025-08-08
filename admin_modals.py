import discord
from db_manager import alterar_nivel_por_id, revogar_porte_por_id

class AlterarNivelForm(discord.ui.Modal):
    def __init__(self, numero_processo: str, dados_processo: dict, mensagem_original: discord.Message):
        super().__init__(title=f"Alterar Porte de {dados_processo['nome']}")
        self.numero_processo = numero_processo
        self.dados_processo = dados_processo
        self.mensagem_original = mensagem_original
        
        self.add_item(discord.ui.InputText(
            label="Novo Nível do Porte (1, 2 ou 3)",
            placeholder=f"O nível atual é {dados_processo['nivel_porte']}. Insira o novo nível.",
            max_length=1,
            required=True
        ))
        self.add_item(discord.ui.InputText(
            label="Justificativa da Alteração",
            placeholder="Explique o motivo para a alteração do nível do porte.",
            style=discord.InputTextStyle.paragraph,
            required=True
        ))

    async def callback(self, interaction: discord.Interaction):
        novo_nivel = self.children[0].value.strip()
        motivo = self.children[1].value
        
        if novo_nivel not in ['1', '2', '3']:
            await interaction.response.send_message("❌ Nível inválido. Use apenas 1, 2 ou 3.", ephemeral=True)
            return

        processo_alterado = alterar_nivel_por_id(self.numero_processo, novo_nivel, motivo, interaction.user.mention)
        if processo_alterado:
            # Edita a mensagem de verificação original para refletir a mudança
            embed_original = self.mensagem_original.embeds[0]
            embed_original.clear_fields() # Limpa os campos antigos
            embed_original.add_field(name="Nível", value=f"**Nível {processo_alterado['nivel_porte']}** (Alterado)", inline=False)
            embed_original.add_field(name="Nome", value=processo_alterado['nome'], inline=False)
            embed_original.add_field(name="Identidade (ID)", value=processo_alterado['identidade'], inline=False)
            embed_original.add_field(name="Status", value=f"`{processo_alterado['status']}`", inline=False)
            
            # Adiciona o registo da alteração
            log = processo_alterado['log_alteracao']
            texto_log = f"**Admin:** {log['admin']} em {log['data']}\n**Motivo:** {log['motivo']}"
            embed_original.add_field(name="Registo de Alteração", value=texto_log, inline=False)
            
            embed_original.color = discord.Color.orange()
            embed_original.set_footer(text=f"Última alteração por {interaction.user.display_name}")

            await self.mensagem_original.edit(embed=embed_original)
            await interaction.response.send_message(f"✅ O nível do porte foi alterado com sucesso.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro ao alterar o nível do porte.", ephemeral=True)

class RevogarPorteForm(discord.ui.Modal):
    def __init__(self, numero_processo: str, dados_processo: dict, mensagem_original: discord.Message):
        super().__init__(title=f"Revogar Porte de {dados_processo['nome']}")
        self.numero_processo = numero_processo
        self.dados_processo = dados_processo
        self.mensagem_original = mensagem_original
        
        self.add_item(discord.ui.InputText(
            label="Justificativa da Revogação",
            placeholder="Explique o motivo pelo qual o porte está a ser revogado.",
            style=discord.InputTextStyle.paragraph,
            required=True
        ))
        self.add_item(discord.ui.InputText(
            label="Confirme a ação escrevendo 'REVOGAR'",
            placeholder="Esta ação é irreversível.",
            max_length=8
        ))

    async def callback(self, interaction: discord.Interaction):
        motivo = self.children[0].value
        confirmacao = self.children[1].value.strip()
        if confirmacao.upper() != 'REVOGAR':
            await interaction.response.send_message("❌ Confirmação inválida. A ação foi cancelada.", ephemeral=True)
            return

        processo_revogado = revogar_porte_por_id(self.numero_processo, motivo, interaction.user.mention)
        if processo_revogado:
            # Edita a mensagem de verificação original
            embed_original = self.mensagem_original.embeds[0]
            embed_original.title = f"⚠️ Porte Revogado - {processo_revogado['nome']}"
            embed_original.color = discord.Color.dark_red()
            
            # Adiciona o registo da revogação
            log = processo_revogado['log_revogacao']
            texto_log = f"**Admin:** {log['admin']} em {log['data']}\n**Motivo:** {log['motivo']}"
            # Limpa campos antigos e adiciona o novo status e o log
            embed_original.clear_fields()
            embed_original.add_field(name="Status Final", value="`REVOGADO`", inline=False)
            embed_original.add_field(name="Informações da Revogação", value=texto_log, inline=False)
            embed_original.set_footer(text=f"Porte revogado por {interaction.user.display_name}")
            
            # Edita a mensagem e remove os botões, pois a ação é final
            await self.mensagem_original.edit(embed=embed_original, view=None)
            await interaction.response.send_message("✅ O porte foi revogado com sucesso.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro ao revogar o porte.", ephemeral=True)