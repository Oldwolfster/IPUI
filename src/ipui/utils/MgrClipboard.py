# MgrClipboard.py  Update: copy() now trims floats; deep_copy() is raw byte-exact
import subprocess
import platform
import pygame

class MgrClipboard:

    # MgrClipboard.py method: copy  Update: trims long float decimals on the way out
    @staticmethod
    def copy(text, places=5):
        MgrClipboard.deep_copy(MgrClipboard.trim_floats(text, places))

    # MgrClipboard.py method: deep_copy  NEW: former copy() body, raw byte-exact
    @staticmethod
    def deep_copy(text):
        if platform.system() == "Windows":
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        else:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))

    # MgrClipboard.py method: trim_floats  NEW: round float cells in TSV text
    @staticmethod
    def trim_floats(text, places=5):
        return "\n".join(MgrClipboard.trim_row(row, places) for row in text.split("\n"))

    # MgrClipboard.py method: trim_row  NEW: round float cells in one TSV row
    @staticmethod
    def trim_row(row, places):
        return "\t".join(MgrClipboard.trim_cell(cell, places) for cell in row.split("\t"))

    # MgrClipboard.py method: trim_cell  NEW: round one cell if it parses as float
    @staticmethod
    def trim_cell(cell, places):
        if "." not in cell:  return cell
        try:                 value = float(cell)
        except ValueError:   return cell
        return str(round(value, places))

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