import os
from io import BytesIO

import aiohttp
from PIL import Image

from NintbotForDiscord.Plugin import BasePlugin


class IFunnyRemover(BasePlugin):

    def __init__(self, manifest, bot_instance):
        super().__init__(manifest, bot_instance)

        self.register_command("removewatermark",
                              "Removes the iFunny watermark from an image",
                              self.command_removewatermark)

        self.allowed_extensions = [
            ".jpg",
            ".png"
        ]

    def enable(self):
        super(IFunnyRemover, self).enable()
        self.logger.info(f"Enabling iFunny Remover v{self.manifest['version']}")

    def disable(self):
        super(IFunnyRemover, self).disable()
        self.logger.info(f"Disabling iFunny Remover v{self.manifest['version']}")

    @staticmethod
    def remove_watermark(img: Image.Image) -> Image.Image:
        width, height = img.size
        cropped = img.crop((0, 0, width, height - 20))
        return cropped

    async def command_removewatermark(self, args: dict):
        image_message = None
        async for message in self.bot.logs_from(args["channel"], limit=10):
            if len(message.attachments) != 1:
                continue
            if any(message.attachments[0]["filename"].lower().endswith(i) for i in self.allowed_extensions):
                image_message = message
                break

        if image_message is None:
            await self.bot.send_message(args["channel"], "No images have been posted within the last 10 messages.")
            return

        self.logger.debug("Retrieving image...")

        async with aiohttp.ClientSession(loop=self.bot.EventManager.loop) as session:
            async with session.get(image_message.attachments[0]["url"]) as response:
                image = response.content
                content = await image.read()
                file = BytesIO(content)

        self.logger.debug("Got image, removing watermark...")
        removed_watermark = self.remove_watermark(Image.open(file))
        removed_watermark.save(os.path.join(self.manifest["path"], "watermark_removed.png"))
        await self.bot.send_file(args["channel"], os.path.join(self.manifest["path"], "watermark_removed.png"))
