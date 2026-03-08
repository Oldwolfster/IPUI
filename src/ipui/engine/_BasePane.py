# _basePane.py  Update: add initialize lifecycle hook
from ipui.utils.EZ import EZ


class _basePane:
    """Base class for pane builders.
    Gives self.form to all methods.
    Override initialize() for one-time setup."""

    # _basePane.py method: __init_subclass__  NEW: guard against __init__ override
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__:
            raise TypeError(f"{cls.__name__}: Don't override __init__, use initialize() instead")

    def __init__(self, form):
        self.form = form
        self.register_derives()
        self.initialize()


# _basePane.py method: register_derives  Update: use EZ.err

    def register_derives(self):
        derives = getattr(self.__class__, 'DECLARATION_UPDATES', None)
        if not derives:
            return
        for control_name, entry in derives.items():
            method_name = entry["compute"]
            method      = getattr(self, method_name, None)
            if method is None:
                EZ.err(
                    f"{self.__class__.__name__}.DECLARATION_UPDATES references '{method_name}'. "
                    f"Create {method_name}() on {self.__class__.__name__} "
                    f"to calculate the value for {control_name}."
                )
            self.form.register_derive(
                control_name = control_name,
                property     = entry["property"],
                compute      = method,
                triggers     = entry["triggers"],
            )
        #self.form.pipeline.fire_all_derives()

    def initialize(self): #If writing documentation DOCUMENT THIS IOC HOOK
        pass

    def swap_pane(self, index, builder, *args, **kwargs):
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap