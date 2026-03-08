class EZ:
    PREFIX = "HEY PILGRIM! EZ-FIX ----> "

    @staticmethod
    def err(*args, exc_type: type[Exception] = ValueError) -> None:
        # Backwards compat:
        #   EZ.err("msg", ValueError)
        # Also supports:
        #   EZ.err("a", "b")
        #   EZ.err("a", "b", ValueError)
        if args and isinstance(args[-1], type) and issubclass(args[-1], Exception):
            exc_type = args[-1]
            args     = args[:-1]

        parts = []
        for a in args:
            if a is None:
                continue
            if isinstance(a, (list, tuple)):
                for x in a:
                    if x is None:
                        continue
                    parts.append(str(x))
            else:
                parts.append(str(a))

        message = "".join(parts) if parts else ""
        raise exc_type(f"{EZ.PREFIX}{message}")