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
    def _draw_box(msg, color, title):
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
        return out

    @staticmethod
    def err(*args, exc_type: type[Exception] = ValueError) -> None:
        # Check if user passed a custom exception type as the last arg
        if args and isinstance(args[-1], type) and issubclass(args[-1], Exception):
            exc_type = args[-1]
            args     = args[:-1]

        formatted = EZ.format_message(*args)
        box       = EZ._draw_box(formatted, EZ.RED, EZ.PREFIX_ERR)
        raise exc_type(box)

    @staticmethod
    def warn(*args) -> None:
        formatted = EZ.format_message(*args)
        print(EZ._draw_box(formatted, EZ.YELLOW, EZ.PREFIX_WARN))