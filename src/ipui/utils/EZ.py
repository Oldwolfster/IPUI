import inspect
import os
import time

import pygame


class EZ:
    # ANSI Color Codes
    RED          = "\033[91m"
    YELLOW       = "\033[93m"
    BOLD         = "\033[1m"
    RESET        = "\033[0m"

    PREFIX_ERR   = " HOUSTON!!! WE HAVE A PROBLEM!!! "
    PREFIX_WARN  = " HOUSTON!!! WE HAVE A WARNING!!! "

    @staticmethod
    def format_message(*args):
        # Filter and flatten args while maintaining your specific indent logic
        parts = []
        for a in args:
            if a is None: continue
            if isinstance(a, (list, tuple)):
                parts.extend([str(x) for x in a if x is not None])
            elif not (isinstance(a, type) and issubclass(a, Exception)):
                parts.append(str(a))

        message = " ".join(parts)
        lines   = message.split("\n")
        # Align all lines after the first for better visual scanning
        return lines[0] + "".join(f"\n    {l}" for l in lines[1:])

    @staticmethod
    def _draw_box(msg, color, title, origin):
        lines   = msg.split("\n")
        width   = max(len(l) for l in lines)
        width   = max(width, len(title)) + 4

        # The "Structural Frame" - Impossible to miss while scrolling
        out  = f"\n{color}{EZ.BOLD}╔" + "═" * (width) + "╗\n"
        out += f"║{title.center(width)}║\n"
        out += f"╠" + "═" * (width) + "╣\n"
        for l in lines:
            out += f"║  {l:<{width-2}}║\n"
        out += f"╚" + "═" * (width) + f"╝{EZ.RESET}\n"
        out +=f"\n{origin}"
        return out

    @staticmethod
    def _get_origin_info():
        """
        Scans the stack to find the first caller NOT in the framework core.
        """
        stack = inspect.stack()
        # Define what we consider "Framework Plumbing"
        plumbing_files = ("EZ.py", "_BaseWidget.py", "engine.py")

        for frame_info in stack:
            filename = frame_info.filename
            base_name = os.path.basename(filename)

            # Skip this helper, EZ.err, and the internal framework logic
            if base_name in plumbing_files or "inspect" in filename:
                continue

            # This is the first 'External' file (e.g., Paradigm.py)
            return f'File "{filename}", line {frame_info.lineno}"'

        return "Unknown Location"

    @staticmethod
    def err(*args, exc_type: type[Exception] = ValueError) -> None:
        if args and isinstance(args[-1], type) and issubclass(args[-1], Exception):
            exc_type = args[-1]
            args = args[:-1]

        origin = EZ._get_origin_info()
        formatted = EZ.format_message(*args)

        # Inject the origin into the box so the developer knows exactly where to look
        #title = f"{EZ.PREFIX_ERR}\n    LOCATED AT: {origin}"

        box = EZ._draw_box(formatted, EZ.RED, EZ.PREFIX_ERR, origin)
        raise exc_type(box)

    @staticmethod
    def warn(*args) -> None:
        formatted = EZ.format_message(*args)
        print(EZ._draw_box(formatted, EZ.YELLOW, EZ.PREFIX_WARN))


    @staticmethod
    def _halt_and_flare(screen):
        """ The 0.5s 'Pre-Submit Review' flare. """
        if not pygame.display.get_init():
            return

        # 1. Capture the current screen and dim it
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((20, 0, 0)) # Deep 'Emergency' Red

        screen.blit(overlay, (0, 0))

        # 2. Draw a simple high-impact warning
        # (Using your internal font/draw logic)
        EZ.draw_emergency_text(screen, "HOUSTON: CRITICAL FAILURE IMMINENT")

        pygame.display.flip()

        # 3. The 'Brace' period
        time.sleep(0.5)