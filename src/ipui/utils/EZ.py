# EZ.py  Update: add origin_file/origin_line params, format internally; legacy origin= string still accepted

import inspect
import os
import time

import pygame


class EZ:
    # ANSI Color Codes
    RED             = "\033[91m"
    YELLOW          = "\033[93m"
    BOLD            = "\033[1m"
    RESET           = "\033[0m"
    PREFIX_ERR      = " HOUSTON!!! WE HAVE A PROBLEM!!! "
    PREFIX_WARN     = " HOUSTON!!! WE HAVE A WARNING!!! "
    WRAP_WIDTH = 120

    # IPUI_ROOT = the absolute path of the ipui package, derived from EZ.py's location.
    # EZ.py lives at <IPUI_ROOT>/utils/EZ.py, so two dirname() calls walk us up to ipui/.
    # Works for any install layout: editable (src/ipui), PyPI (site-packages/ipui), vendored, frozen.
    # If EZ.py ever moves, update the dirname count below to match its new depth.
    IPUI_ROOT       = os.path.normcase(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Folders whose frames are noise — skip them and keep walking up to find the actual bug site.
    SKIP_FOLDERS    = (
        os.path.join(IPUI_ROOT, 'engine')  + os.sep,
        os.path.join(IPUI_ROOT, 'widgets') + os.sep,
        os.path.join(IPUI_ROOT, 'utils')   + os.sep,
    )

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
    def draw_boxOLD(msg, color, title, origin):
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
        out += f"\n{origin}"
        return out

    @staticmethod
    def draw_box(msg, color, title, origin):
        import textwrap
        raw_lines = msg.split("\n")
        lines     = []
        for raw in raw_lines:
            if len(raw) <= EZ.WRAP_WIDTH:
                lines.append(raw)
            else:
                lines.extend(textwrap.wrap(raw, EZ.WRAP_WIDTH, break_long_words=True, break_on_hyphens=False))
        width = max(len(l) for l in lines)
        width = max(width, len(title)) + 4

        # The "Structural Frame" - Impossible to miss while scrolling
        out  = f"\n{color}{EZ.BOLD}╔" + "═" * (width) + "╗\n"
        out += f"║{title.center(width)}║\n"
        out += f"╠" + "═" * (width) + "╣\n"
        for l in lines:
            out += f"║  {l:<{width-2}}║\n"
        out += f"╚" + "═" * (width) + f"╝{EZ.RESET}\n"
        out += f"\n{origin}"
        return out

    @staticmethod
    def format_origin(file_path, line):
        """The single source of truth for the clickable-link format.
        PyCharm matches: File "<path>", line N — exact spelling matters."""
        return f'File "{file_path}", line {line}'

    @staticmethod
    def get_origin_info():
        """Walk the stack and return the first frame outside our noise folders.
        Premise: framework bugs are rare, user mistakes are constant.
        We skip ipui/engine/, ipui/widgets/, and ipui/utils/ (where EZ lives)
        and keep walking up until we land on the actual bug site."""
        for frame_info in inspect.stack()[1:]:                          # [1:] skips this method
            normalized = os.path.normcase(os.path.abspath(frame_info.filename))
            if any(normalized.startswith(skip) for skip in EZ.SKIP_FOLDERS): continue
            return EZ.format_origin(frame_info.filename, frame_info.lineno)
        return EZ.format_origin('<unknown>', 0)

    @staticmethod
    def resolve_origin(origin, origin_file, origin_line):
        """Origin precedence: explicit string > explicit file/line > stack walk."""
        if origin is not None:                          return origin
        if origin_file is not None:                     return EZ.format_origin(origin_file, origin_line)
        return EZ.get_origin_info()

    @staticmethod
    def err(*args, exc_type: type[Exception] = ValueError,
            origin=None, origin_file=None, origin_line=1) -> None:
        if args and isinstance(args[-1], type) and issubclass(args[-1], Exception):
            exc_type    = args[-1]
            args        = args[:-1]

        origin          = EZ.resolve_origin(origin, origin_file, origin_line)
        formatted       = EZ.format_message(*args)

        box = EZ.draw_box(formatted, EZ.RED, EZ.PREFIX_ERR, origin)
        raise exc_type(box)

    @staticmethod
    def warn(*args, origin=None, origin_file=None, origin_line=1) -> None:
        formatted = EZ.format_message(*args)
        origin    = EZ.resolve_origin(origin, origin_file, origin_line)
        print(EZ.draw_box(formatted, EZ.YELLOW, EZ.PREFIX_WARN, origin))

    @staticmethod
    def warn_scroll(widget):
        if widget.scroll_v:
            name = type(widget).__name__
            EZ.err(
                f"{name} doesn't support scroll_v=True directly.\n"
                f"Wrap it in a scroll_v Card instead:\n"
                f"  card = Card(parent, scroll_v=True)\n"
                f"  {name}(card, ...)"
            )