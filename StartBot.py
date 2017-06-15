import sys
import os

from NintbotForDiscord.Launcher import FileBotLauncher

if len(sys.argv) == 2:
    launcher = FileBotLauncher(sys.argv[1])
else:
    launcher = FileBotLauncher(os.path.join("config.json"))
