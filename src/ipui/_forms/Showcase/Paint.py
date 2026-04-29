from ipui import *
import pygame

class Paint(_BaseTab):
    def tools(self, parent):
        Title(parent, "Paint")
        Body(parent, "Hold left mouse to draw")

        Heading(parent, "Colors")
        Row_colors = Row(parent)
        Button(Row_colors, "Black", on_click=lambda: self.set_color((  0,   0,   0)), color_bg=( 50,  50,  50))
        Button(Row_colors, "Red",   on_click=lambda: self.set_color((220,  60,  60)), color_bg=(120,  40,  40))
        Button(Row_colors, "Green", on_click=lambda: self.set_color(( 60, 180,  90)), color_bg=( 40, 100,  60))
        Button(Row_colors, "Blue",  on_click=lambda: self.set_color(( 70, 120, 220)), color_bg=( 40,  60, 120))

        Heading(parent, "Brush Size")
        Row_sizes = Row(parent)
        Button(Row_sizes, "Small",  on_click=lambda: self.set_brush_size(2))
        Button(Row_sizes, "Medium", on_click=lambda: self.set_brush_size(5))
        Button(Row_sizes, "Large",  on_click=lambda: self.set_brush_size(10))

        Heading(parent, "Tools")
        Row_tools = Row(parent)
        Button(Row_tools, "Brush",  on_click=self.use_brush,  color_bg=Style.COLOR_BUTTON_CTA)
        Button(Row_tools, "Eraser", on_click=self.use_eraser)

        Heading(parent, "Actions")
        Row_actions = Row(parent)
        Button(Row_actions, "Undo",  on_click=self.undo_last_stroke)
        Button(Row_actions, "Clear", on_click=self.clear_canvas)

        self.lbl_status = Detail(parent, "Brush | Black | 5px")

    def ip_setup(self, ip):
        self.strokes      = []
        self.current_line = []
        self.color        = (0, 0, 0)
        self.brush_size   = 5
        self.eraser_mode  = False
        self.was_drawing  = False
        self.bg_color     = Style.COLOR_BACKGROUND

    def set_color(self, color):
        self.color = color
        self.eraser_mode = False
        self.refresh_status()

    def set_brush_size(self, size):
        self.brush_size = size
        self.refresh_status()

    def use_brush(self):
        self.eraser_mode = False
        self.refresh_status()

    def use_eraser(self):
        self.eraser_mode = True
        self.refresh_status()

    def undo_last_stroke(self):
        if self.strokes:
            self.strokes.pop()

    def clear_canvas(self):
        self.strokes.clear()
        self.current_line.clear()
        self.was_drawing = False

    def refresh_status(self):
        mode = "Eraser" if self.eraser_mode else "Brush"

        if self.eraser_mode:
            color_name = "Background"
        else:
            color_name = self.private_color_name(self.color)

        self.lbl_status.set_text(f"{mode} | {color_name} | {self.brush_size}px")

    def ip_think(self, ip):
        drawing_now = ip.mouse_down(Mouse.LEFT) and ip.mouse_inside_pane()
        just_started = drawing_now and not self.was_drawing
        just_stopped = not drawing_now and self.was_drawing

        if just_started:
            self.current_line = []
            self.private_add_point(ip)

        elif drawing_now:
            self.private_add_point(ip)

        elif just_stopped:
            if self.current_line:
                draw_color = self.bg_color if self.eraser_mode else self.color
                self.strokes.append({
                    "points": self.current_line[:],
                    "color" : draw_color,
                    "width" : self.brush_size,
                })
            self.current_line = []

        self.was_drawing = drawing_now

    def private_add_point(self, ip):
        x, y = ip.mouse_local_pos()

        if not self.current_line:
            self.current_line.append((x, y))
            return

        last_x, last_y = self.current_line[-1]
        if abs(x - last_x) >= 1 or abs(y - last_y) >= 1:
            self.current_line.append((x, y))

    def ip_draw(self, ip):
        self.private_draw_strokes(ip)
        self.private_draw_current_line(ip)

    def private_draw_strokes(self, ip):
        for stroke in self.strokes:
            self.private_draw_line(
                surface = ip.surface,
                points  = stroke["points"],
                color   = stroke["color"],
                width   = stroke["width"],
                rect    = ip.rect_pane,
            )

    def private_draw_current_line(self, ip):
        if not self.current_line:
            return

        draw_color = self.bg_color if self.eraser_mode else self.color

        self.private_draw_line(
            surface = ip.surface,
            points  = self.current_line,
            color   = draw_color,
            width   = self.brush_size,
            rect    = ip.rect_pane,
        )

    def private_draw_line(self, surface, points, color, width, rect):
        if len(points) == 1:
            x = rect.left + points[0][0]
            y = rect.top  + points[0][1]
            pygame.draw.circle(surface, color, (int(x), int(y)), max(1, width // 2))
            return

        translated_points = []
        for x, y in points:
            translated_points.append((rect.left + x, rect.top + y))

        pygame.draw.lines(surface, color, False, translated_points, width)

    def private_color_name(self, color):
        names = {
            (0, 0, 0): "Black",
            (220, 60, 60): "Red",
            (60, 180, 90): "Green",
            (70, 120, 220): "Blue",
        }
        return names.get(color, str(color))