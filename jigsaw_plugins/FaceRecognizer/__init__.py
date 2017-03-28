import os
from io import BytesIO

import aiohttp
import discord
import face_recognition
import numpy

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin


class FaceRecognizer(BasePlugin):

    def __init__(self, manifest, bot_instance):
        super().__init__(manifest, bot_instance)

        self.register_handler(EventTypes.MESSAGE_SENT, self.on_message)

        self.enabled_servers = [
            "106515301121703936",
            "219853764037836800",
            "129388853571223552"
        ]

        self.allowed_extensions = [
            ".jpg",
            ".png"
        ]

        self._known_encodings = []
        self._image_path = os.path.abspath(os.path.join(self.manifest["path"], "images"))
        self._encoding_path = os.path.abspath(os.path.join(self.manifest["path"], "encodings"))

    def get_missing_encodings(self):
        for file in os.listdir(self._image_path):
            if file + ".npy" not in os.listdir(self._encoding_path) and any(file.lower().endswith(i) for i in self.allowed_extensions):
                yield file

    def generate_encoding(self, filename):
        self.logger.info(f"Generating encoding for {filename}, this may take a while.")
        image = face_recognition.load_image_file(os.path.join(self._image_path, filename))
        encodings = face_recognition.face_encodings(image, num_jitters=25)
        if len(encodings) != 1:
            self.logger.warning(f"{filename} contains an invalid number of faces ({len(encodings)}). It is suggested you delete this file.")
            return
        else:
            self.logger.info("Encoding generated, saving now.")
            savepath = os.path.join(self._encoding_path, filename)
            numpy.save(savepath, encodings[0])
            self.logger.info(f"Encoding saved to {savepath}.npy.")

    def generate_missing_encodings(self):
        self.logger.debug("Generating missing encodings...")
        for file in self.get_missing_encodings():
            self.generate_encoding(file)
        self.logger.debug("Missing encodings generated.")

    def load_encodings(self):
        self.generate_missing_encodings()
        for file in os.listdir(self._encoding_path):
            self.logger.debug(f"Loading encoding from {file}.")
            self._known_encodings.append({
                "name": file.split("-")[0],
                "file": file,
                "encoding": numpy.load(os.path.join(self._encoding_path, file))
            })
            self.logger.debug(f"Encoding loaded.")

    def enable(self):
        super(FaceRecognizer, self).enable()
        self.logger.info(f"Enabling Face Recognizer v{self.manifest['version']}")
        self.load_encodings()

    def disable(self):
        super(FaceRecognizer, self).disable()
        self.logger.info(f"Disabling Face Recognizer v{self.manifest['version']}")
        self.logger.debug("Clearing encodings...")
        self._known_encodings = []
        self.logger.debug("Encodings cleared.")

    async def on_message(self, args: dict):
        message = args["message"]  # type: discord.Message
        if len(message.attachments) != 1:
            return

        if not any(message.attachments[0]["filename"].lower().endswith(i) for i in self.allowed_extensions):
            return

        if message.server.id not in self.enabled_servers:
            return

        async with aiohttp.ClientSession(loop=self.bot.EventManager.loop) as session:
            async with session.get(message.attachments[0]["url"]) as response:
                image = response.content
                content = await image.read()
                file = BytesIO(content)

        image = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(image, num_jitters=10)
        seen = []

        for known_encoding in self._known_encodings:
            for unknown in encodings:
                results = face_recognition.compare_faces([known_encoding["encoding"]], unknown, tolerance=0.5)
                if results[0] and known_encoding["name"] not in seen:
                    seen.append(f"{known_encoding['name']} (based on {known_encoding['file']})")

        if len(seen) != 0:
            await self.bot.send_message(args["channel"], f"I think I see: {', '.join(seen)}")
