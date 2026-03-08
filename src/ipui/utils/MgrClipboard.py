# Clipboard.py  NEW: Platform clipboard utility
import subprocess


class Clipboard:

    @staticmethod
    def copy(text):
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-16le'))