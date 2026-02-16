import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import discord
from discord import app_commands
from discord.ui import View, button, Button

from gacha import roll
from storage import save_pull, get_pull, update_pull, delete_pull, load_pulls, IMAGES_DIR

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
PLACEHOLDER_IMAGE = Path(__file__).parent / "assets" / "placeholder.png"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="pull", description="Get a new character prompt")
async def pull_command(interaction: discord.Interaction):
    result = roll()
    save_pull(result)

    embed = discord.Embed(
        title=f"Prompt Get!",
        description=f"""
Rarity: {result['rarity']} 
Prompt {result['prompt']}
Recommended time: {result['time']}
""",
    )
    embed.set_footer(text=f"ID: {result['id']}")

    await interaction.response.send_message(embed=embed)


@tree.command(name="complete", description="Upload art for a pull")
@app_commands.describe(pull_id="The pull ID to complete", image="Your character art")
async def complete_command(
    interaction: discord.Interaction,
    pull_id: str,
    image: discord.Attachment,
):
    pull = get_pull(pull_id)
    if not pull:
        await interaction.response.send_message(f"No pull found with ID {pull_id}", ephemeral=True)
        return

    if pull["image_path"]:
        await interaction.response.send_message("This pull already has art!", ephemeral=True)
        return

    ext = image.filename.split(".")[-1] if "." in image.filename else "png"
    filename = f"{pull_id}.{ext}"
    filepath = IMAGES_DIR / filename

    await image.save(filepath)

    update_pull(pull_id, {"image_path": str(filepath)})

    embed = discord.Embed(title=f"Completed: [{pull['rarity']}] {pull['prompt']}")
    embed.set_image(url=f"attachment://{filename}")

    await interaction.response.send_message(
        embed=embed,
        file=discord.File(filepath, filename=filename),
    )


class GalleryView(View):
    def __init__(self, pulls: list[dict]):
        super().__init__(timeout=300)
        self.pulls = pulls
        self.index = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= len(self.pulls) - 1

    def get_embed(self) -> discord.Embed:
        pull = self.pulls[self.index]
        status = "done" if pull["image_path"] else "pending"
        embed = discord.Embed(
            title=f"[{pull['rarity']}] {pull['prompt']}",
            description=f"Status: {status}\nID: {pull['id']}",
        )
        embed.set_footer(text=f"{self.index + 1} / {len(self.pulls)}")
        return embed

    def get_file(self) -> discord.File:
        pull = self.pulls[self.index]
        if pull["image_path"] and Path(pull["image_path"]).exists():
            return discord.File(pull["image_path"], filename="image.png")
        return discord.File(PLACEHOLDER_IMAGE, filename="image.png")

    @button(label="Prev", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, btn: Button):
        self.index = max(0, self.index - 1)
        self._update_buttons()
        embed = self.get_embed()
        file = self.get_file()
        embed.set_image(url="attachment://image.png")
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

    @button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, btn: Button):
        self.index = min(len(self.pulls) - 1, self.index + 1)
        self._update_buttons()
        embed = self.get_embed()
        file = self.get_file()
        embed.set_image(url="attachment://image.png")
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

    @button(label="Upload Art", style=discord.ButtonStyle.success)
    async def upload_btn(self, interaction: discord.Interaction, btn: Button):
        pull = self.pulls[self.index]
        if pull["image_path"]:
            await interaction.response.send_message("This pull already has art!", ephemeral=True)
            return

        await interaction.response.send_message(
            f"Upload your art for **[{pull['rarity']}] {pull['prompt']}** — "
            "send an image in this channel within 60 seconds.",
            ephemeral=True,
        )

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
                and m.attachments
            )

        try:
            msg = await client.wait_for("message", check=check, timeout=60)
        except TimeoutError:
            await interaction.followup.send("Timed out waiting for an image.", ephemeral=True)
            return

        attachment = msg.attachments[0]
        ext = attachment.filename.split(".")[-1] if "." in attachment.filename else "png"
        filename = f"{pull['id']}.{ext}"
        filepath = IMAGES_DIR / filename

        await attachment.save(filepath)
        update_pull(pull["id"], {"image_path": str(filepath)})
        pull["image_path"] = str(filepath)

        embed = self.get_embed()
        file = self.get_file()
        embed.set_image(url="attachment://image.png")
        await self.message.edit(embed=embed, attachments=[file], view=self)

        await interaction.followup.send(
            f"Art saved for **[{pull['rarity']}] {pull['prompt']}**!", ephemeral=True
        )

    @button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_btn(self, interaction: discord.Interaction, btn: Button):
        pull = self.pulls[self.index]
        delete_pull(pull["id"])
        self.pulls.pop(self.index)

        if not self.pulls:
            await interaction.response.edit_message(
                content="All pulls deleted!", embed=None, attachments=[], view=None
            )
            return

        self.index = min(self.index, len(self.pulls) - 1)
        self._update_buttons()
        embed = self.get_embed()
        file = self.get_file()
        embed.set_image(url="attachment://image.png")
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)


@tree.command(name="updateart", description="Replace the art for a pull")
@app_commands.describe(pull_id="The pull ID to update", image="Your new character art")
async def updateart_command(
    interaction: discord.Interaction,
    pull_id: str,
    image: discord.Attachment,
):
    pull = get_pull(pull_id)
    if not pull:
        await interaction.response.send_message(f"No pull found with ID {pull_id}", ephemeral=True)
        return

    if not pull["image_path"]:
        await interaction.response.send_message(
            "This pull has no art yet! Use /complete instead.", ephemeral=True
        )
        return

    # Delete the old image file
    old_path = Path(pull["image_path"])
    if old_path.exists():
        old_path.unlink()

    ext = image.filename.split(".")[-1] if "." in image.filename else "png"
    filename = f"{pull_id}.{ext}"
    filepath = IMAGES_DIR / filename

    await image.save(filepath)

    update_pull(pull_id, {"image_path": str(filepath)})

    embed = discord.Embed(title=f"Updated: [{pull['rarity']}] {pull['prompt']}")
    embed.set_image(url=f"attachment://{filename}")

    await interaction.response.send_message(
        embed=embed,
        file=discord.File(filepath, filename=filename),
    )


@tree.command(name="delete", description="Delete a pull")
@app_commands.describe(pull_id="The pull ID to delete")
async def delete_command(interaction: discord.Interaction, pull_id: str):
    pull = delete_pull(pull_id)
    if not pull:
        await interaction.response.send_message(f"No pull found with ID {pull_id}", ephemeral=True)
        return

    await interaction.response.send_message(
        f"Deleted [{pull['rarity']}] {pull['prompt']} (ID: {pull['id']})", ephemeral=True
    )


@tree.command(name="pulls", description="View all your pulls")
async def pulls_command(interaction: discord.Interaction):
    pulls = load_pulls()

    if not pulls:
        await interaction.response.send_message("No pulls yet! Use /pull to get started.", ephemeral=True)
        return

    view = GalleryView(pulls)
    embed = view.get_embed()
    file = view.get_file()
    embed.set_image(url="attachment://image.png")
    await interaction.response.send_message(embed=embed, file=file, view=view)

    view.message = await interaction.original_response()


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


def main():
    if not DISCORD_TOKEN:
        print("Set DISCORD_TOKEN environment variable")
        return
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
