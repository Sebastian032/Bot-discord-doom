import asyncio
import os
import gc
import discord
from discord.ext import commands
from aiohttp import web

# Intents mínimos para ahorrar memoria
intents = discord.Intents.none()
intents.guilds = True
intents.voice_states = True

# Servidor web en segundo plano para el health check de Render
async def handle_health_check(request):
    return web.Response(text="Doom Slayer is online!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render asigna automáticamente el puerto en la variable PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f" LOG LOCAL: Servidor Web activo en el puerto {port}", flush=True)

class DoomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, max_messages=None)

    async def setup_hook(self):
        await self.tree.sync()
        await start_web_server()

bot = DoomBot()

@bot.event
async def on_ready():
    print(f" LOG LOCAL: ¡El Slayer ha despertado! Conectado como {bot.user}", flush=True)

@bot.tree.command(name="doom", description="Reproduce el primer testamento del Doom Slayer")
async def doom(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ ¡Debes estar en un canal de voz!", ephemeral=True)
        return

    canal_voz = interaction.user.voice.channel
    await interaction.response.send_message("🔥 *'En la primera era, en la primera batalla...'*")

    vc = interaction.guild.voice_client
    if not vc:
        vc = await canal_voz.connect(timeout=10.0, reconnect=True)
    elif vc.channel != canal_voz:
        await vc.move_to(canal_voz)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    archivo_audio = os.path.join(BASE_DIR, "doom.mp3")

    if not os.path.exists(archivo_audio):
        print(f"❌ ERROR: No se encontró el archivo en {archivo_audio}", flush=True)
        return

    def despues_de_reproducir(error):
        if error:
            print(f"❌ Error durante la reproducción de FFmpeg: {error}", flush=True)
        else:
            print(" LOG LOCAL: FFmpeg terminó de reproducir normalmente.", flush=True)
        gc.collect()

    # Opciones de bajo consumo de RAM para FFmpeg
    ffmpeg_options = {
        'before_options': '-re',
        'options': '-vn -sn -dn -bufsize 64k'
    }

    audio_source = discord.FFmpegPCMAudio(archivo_audio, **ffmpeg_options)
    vc.play(audio_source, after=despues_de_reproducir)

    while vc.is_playing():
        await asyncio.sleep(1)

    await asyncio.sleep(1)
    await vc.disconnect()
    gc.collect()

bot.run(os.getenv("DISCORD_TOKEN"))