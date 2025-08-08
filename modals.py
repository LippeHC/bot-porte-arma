import discord
import datetime
from db_manager import salvar_processo, encontrar_e_atualizar_laudo, encontrar_e_emitir_porte

# --- Formulário do Policial (Completo e com Edição de Mensagem) ---
class EmissaoPorteForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Emissão de Porte de Arma")
        self.add_item(discord.ui.InputText(
            label="💳 Identidade (ID) do Cidadão a Emitir",
            placeholder="Digite a ID para confirmar a emissão do porte."
        ))

    async def callback(self, interaction: discord.Interaction):
        identidade_cidadao = self.children[0].value.strip()
        dados_processo, numero_porte = encontrar_e_emitir_porte(identidade_cidadao)
        
        if dados_processo is None:
            await interaction.response.send_message(
                f"❌ **Processo Inválido!** Verifique se a ID `{identidade_cidadao}` está correta e se o processo já foi aprovado no teste psicológico.",
                ephemeral=True
            )
            return

        # --- LÓGICA DE EDIÇÃO DA MENSAGEM ORIGINAL ---
        try:
            canal_original = interaction.guild.get_channel(dados_processo['channel_id'])
            if canal_original:
                mensagem_original = await canal_original.fetch_message(dados_processo['message_id'])
                embed_original = mensagem_original.embeds[0]
                
                embed_original.description = "Este processo foi finalizado com sucesso.\n**Status:** `Porte Emitido`"
                embed_original.color = discord.Color.green()
                await mensagem_original.edit(embed=embed_original)
        except Exception as e:
            print(f"Erro ao editar a mensagem do processo (Emissão): {e}")

        # --- Lógica para enviar o certificado final do porte ---
        canal_destino = discord.utils.get(interaction.guild.text_channels, name="🔫┋registro-de-porte")
        if not canal_destino:
            await interaction.response.send_message("❌ Erro: Canal `🔫┋registro-de-porte` não encontrado.", ephemeral=True)
            return

        nivel = dados_processo.get("nivel_porte")
        texto_artigo_3 = ""
        if nivel == '1':
            texto_artigo_3 = "Art. 3º - O porte de arma abrange o espaço territorial citado acima; o cidadão que possui o porte está autorizado a andar com 1 (uma) Glock pente cheio + 50 Munições que devem ser adquiridas com a Polícia Civil da Cidade onde foi lavrado o documento acima."
        elif nivel == '2':
            texto_artigo_3 = "Art. 3º - O porte de arma abrange o espaço territorial citado acima; o cidadão que possui o porte está autorizado a andar com 1 (um) Tazer, que devem ser adquiridas com o Departamento Jurídico da Cidade onde foi lavrado o documento acima."
        elif nivel == '3':
            texto_artigo_3 = "Art. 3º - O porte de arma abrange o espaço territorial citado acima; o cidadão que possui o porte está autorizado a andar com 1 (um) Fuzil com pente cheio + 50 Munições, seguindo as regras de uso da cidade."

        texto_legal = (
            "Conforme a lei de Nº 10826, Art. 6º, § XI, de 22.12.2023 da Resolução conjunta CNJ/CNMP Nº 4, de 28.02.2014 e da Resolução CSJT Nº 203, de 25.08.2017\n"
            "RESOLUÇÃO CSJT Nº 203/2017\n\n"
            f"{texto_artigo_3}"
        )

        embed_final = discord.Embed(
            title=f"✅ Porte de Arma Emitido - Nº {numero_porte}",
            description=texto_legal,
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed_final.set_author(name="Governo de Alexandria - Departamento de Polícia")
        embed_final.add_field(name="Órgão de Controle", value="Policia Cívil de Alexandria", inline=True)
        embed_final.add_field(name="Nome do Cidadão", value=dados_processo.get('nome'), inline=False)
        embed_final.add_field(name="Identidade (ID)", value=dados_processo.get('identidade'), inline=True)
        embed_final.add_field(name="Abrangência Territorial", value="Cidade de Alexandria", inline=True)
        embed_final.add_field(name="Emissor do Porte", value=interaction.user.mention, inline=False)
        
        await canal_destino.send(embed=embed_final)
        await interaction.response.send_message("✅ Porte de arma emitido e registado com sucesso!", ephemeral=True)


# --- Formulário do Médico (Completo e com Edição de Mensagem) ---
class LaudoForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Laudo Psicológico")
        self.add_item(discord.ui.InputText(label="💳 Identidade (ID) do Paciente Apto", placeholder="Digite a ID do cidadão que foi aprovado."))

    async def callback(self, interaction: discord.Interaction):
        identidade_paciente = self.children[0].value.strip()
        processo_encontrado = encontrar_e_atualizar_laudo(identidade_paciente)
        
        if processo_encontrado is None:
            await interaction.response.send_message(f"❌ **Processo não encontrado!**", ephemeral=True)
            return

        # --- LÓGICA DE EDIÇÃO DA MENSAGEM ORIGINAL ---
        try:
            canal_original = interaction.guild.get_channel(processo_encontrado['channel_id'])
            if canal_original:
                mensagem_original = await canal_original.fetch_message(processo_encontrado['message_id'])
                embed_original = mensagem_original.embeds[0]
                
                embed_original.description = "O laudo psicológico foi aprovado. O processo aguarda emissão pela Polícia.\n**Status:** `Aguardando Emissão`"
                embed_original.color = discord.Color.blue()
                await mensagem_original.edit(embed=embed_original)
        except Exception as e:
            print(f"Erro ao editar a mensagem do processo (Laudo): {e}")

        # --- Lógica para enviar o laudo no canal de testes ---
        canal_laudos = discord.utils.get(interaction.guild.text_channels, name="🧠┋teste-psicológico")
        if not canal_laudos:
            await interaction.response.send_message("❌ Erro: Canal `🧠┋teste-psicológico` não encontrado.", ephemeral=True)
            return
            
        embed_laudo = discord.Embed(
            title="🧠 Laudo Psicológico Emitido",
            description=f"O cidadão foi considerado apto para o porte de arma.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed_laudo.add_field(name="👤 Nome", value=processo_encontrado['nome'], inline=False)
        embed_laudo.add_field(name="💳 Identidade (ID)", value=processo_encontrado['identidade'], inline=False)
        embed_laudo.add_field(name="📞 Telefone", value=processo_encontrado['telefone'], inline=False)
        embed_laudo.add_field(name="✅ Laudo", value="**Apto**", inline=False)
        embed_laudo.set_footer(text=f"Laudo emitido por: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await canal_laudos.send(embed=embed_laudo)
        await interaction.response.send_message("✅ Laudo de aptidão registado com sucesso!", ephemeral=True)


# --- Formulário do Advogado (Completo e guarda a ID da mensagem) ---
class PorteForm(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Solicitação de Porte de Arma")
        self.add_item(discord.ui.InputText(label="🔫 Nível do Porte (1, 2 ou 3)",placeholder="Digite apenas o número 1, 2 ou 3",max_length=1))
        self.add_item(discord.ui.InputText(label="👤 Nome Completo do Cidadão",placeholder="Ex: Sérgio Serrote"))
        self.add_item(discord.ui.InputText(label="💳 Identidade (ID no jogo)",placeholder="Ex: 654"))
        self.add_item(discord.ui.InputText(label="📞 Telefone de Contato",placeholder="Ex: (555) 123-456"))
        self.add_item(discord.ui.InputText(label="💼 Profissão e Renda",placeholder="Ex: Advogado - Renda 120k",style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction):
        nivel = self.children[0].value.strip()
        if nivel not in ['1', '2', '3']:
            await interaction.response.send_message("❌ **Nível Inválido.** Por favor, insira apenas 1, 2 ou 3.", ephemeral=True)
            return

        dados_processo = {
            "nivel_porte": nivel,
            "nome": self.children[1].value.strip(),
            "identidade": self.children[2].value.strip(),
            "telefone": self.children[3].value.strip(),
            "profissao_renda": self.children[4].value.strip(),
            "advogado_id": interaction.user.id,
            "advogado_nome": interaction.user.display_name
        }
        
        canal_destino = discord.utils.get(interaction.guild.text_channels, name="🔫lançar-registro-de-porte")
        if not canal_destino:
            await interaction.response.send_message("❌ Erro: Canal de registos não encontrado.", ephemeral=True)
            return

        embed_inicial = discord.Embed(
            title=f"⚖️ Processo de Porte #... Iniciado", # Título temporário
            description="Um novo processo foi aberto e aguarda os próximos passos.\n**Status:** `Aguardando Avaliação`",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed_inicial.add_field(name="🔫 Nível do Porte Solicitado", value=f"**Nível {dados_processo['nivel_porte']}**", inline=False)
        embed_inicial.add_field(name="👤 Nome", value=dados_processo['nome'], inline=True)
        embed_inicial.add_field(name="💳 Identidade", value=dados_processo['identidade'], inline=True)
        embed_inicial.add_field(name="📞 Telefone", value=dados_processo['telefone'], inline=True)
        embed_inicial.add_field(name="💼 Profissão e Renda", value=dados_processo['profissao_renda'], inline=False)
        embed_inicial.add_field(name="✍️ Processo Aberto Por", value=interaction.user.mention, inline=False)
        embed_inicial.set_footer(text=f"ID do Advogado: {interaction.user.id}")

        try:
            mensagem_enviada = await canal_destino.send(embed=embed_inicial)
            
            numero_processo = salvar_processo(
                dados_processo,
                message_id=mensagem_enviada.id,
                channel_id=canal_destino.id
            )
            
            embed_inicial.title = f"⚖️ Processo de Porte #{numero_processo} Iniciado"
            await mensagem_enviada.edit(embed=embed_inicial)
            
            await interaction.response.send_message("✅ Solicitação registada com sucesso!", ephemeral=True)
        except Exception as e:
            print(f"Ocorreu um erro inesperado no callback do PorteForm: {e}")
            await interaction.response.send_message("❌ Ocorreu um erro inesperado.", ephemeral=True)