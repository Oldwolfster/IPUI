import pygame
from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style


class ChartWidget(_BaseWidget):
    """
    desc:        Live-updating line chart powered by matplotlib. Dirty-flag rendering keeps it fast.
    when_to_use: Loss curves, training progress, any time-series data.
    best_for:    Watching neural networks learn in real time.
    example:     chart = ChartWidget(parent, name="loss", height_flex=True)
    api:         set_data(lines, x_label, y_label)
    """
    def build(self):
        self.my_name       = "ChartWidget"
        self.height_flex   = self.height_flex or 1
        self.my_surface    = None
        self.pad           = 0
        self.border        = 0
        self.chart_lines   = []
        self.chart_x_label = "X"
        self.chart_y_label = "Y"
        self.chart_dirty   = False

    def set_data(self, lines, x_label="X", y_label="Y"):
        self.chart_lines   = lines
        self.chart_x_label = x_label
        self.chart_y_label = y_label
        self.chart_dirty   = True
        if self.rect and self.rect.width > 50 and self.rect.height > 50:
            self.my_surface = self.render_chart()


    def draw(self, surface):
        if self.chart_dirty and self.rect and self.rect.width > 50 and self.rect.height > 50:  # Add below this line
            self.my_surface = self.render_chart()
            self.chart_dirty = False
        super().draw(surface)

    def render_chart(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        dpi   = 100
        fig_w = self.rect.width / dpi
        fig_h = self.rect.height / dpi

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        fig.patch.set_facecolor("#191920")
        ax.set_facecolor("#232330")

        for line in self.chart_lines:
            ax.plot(line["x"], line["y"], linewidth=1.5, label=line.get("label", ""))

        ax.set_xlabel(self.chart_x_label, color="#E08C1E", fontsize=8)
        ax.set_ylabel(self.chart_y_label, color="#E08C1E", fontsize=8)
        ax.tick_params(colors="#9090A0", labelsize=7)
        ax.spines["bottom"].set_color("#505060")
        ax.spines["left"].set_color("#505060")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if any(line.get("label") for line in self.chart_lines):
            ax.legend(fontsize=6, facecolor="#232330", edgecolor="#505060",
                      labelcolor="#C8C8D0", loc="upper right")

        fig.tight_layout(pad=0)

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf  = bytes(canvas.get_renderer().buffer_rgba())
        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(buf, size, "RGBA")

        plt.close(fig)
        return surf