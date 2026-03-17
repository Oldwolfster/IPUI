# MgrClipboard.py  Update: Windows subprocess, fallback to scrap
import subprocess
import platform
import pygame

class Clipboard:

    @staticmethod
    def copy(text):
        if platform.system() == "Windows":
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        else:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))

    @staticmethod
    def paste():
        if platform.system() == "Windows":
            result = subprocess.run(['powershell', '-command', 'Get-Clipboard'],
                                    capture_output=True, text=True)
            return result.stdout.rstrip('\r\n')
        else:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            data = pygame.scrap.get(pygame.SCRAP_TEXT)
            if data:
                return data.decode('utf-8').rstrip('\x00')
            return ""