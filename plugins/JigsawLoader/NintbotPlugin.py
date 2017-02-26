from jigsaw import JigsawPlugin


class NintbotPlugin(JigsawPlugin):

    def __init__(self, manifest, bot_instance):
        super(NintbotPlugin, self).__init__(manifest)

        self.bot = bot_instance
        self.plugin_info = {
            "plugin_name": self.manifest.get("name", "Unnamed Plugin"),
            "plugin_developer": self.manifest.get("developer", "Unspecified Developer"),
            "plugin_version": self.manifest.get("version", "0.0.0"),
            "module_name": self.manifest.get("module_name", self.manifest.get("name", "Unnamed Plugin")),
            "main_file": self.manifest.get("main_path", "__init__.py")
        }
