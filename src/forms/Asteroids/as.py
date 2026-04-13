from ipui import *
import pygame

class Asteroids(_BaseForm):
    STATES = {
        "READY"     : {"next": "PLAYING", "message": "Click to Start!"},
        "PLAYING"   : {"next": "GAME_OVER"},
        "GAME_OVER" : {"next": "READY", "duration": 2.5, "message": "GAME OVER"},
    }

    def build(self):
        self.lbl_score = Title(self, "Score: 0")

    def ip_setup_pane(self, ip):
        #print(1/0)
        self.ship_x  = 0.5
        self.ship_y  = 0.5
        self.speed   = 0.4
        self.bullets = []
        ip.state.add("READY", None, "PLAYING")
        ip.state.add("PLAYING", None)
        ip.state.add("GAME_OVER", None, "READY", duration=2.5)
        ip.state.go("READY")

    def ip_think(self, ip):
        if ip.state.is_("PLAYING"):
            self.ship_x += self.speed * ip.dt
            self.lbl_score.set_text(f"Score: {len(self.bullets)}")

    def ip_draw(self, ip):
        pos = ip.to_screen(self.ship_x, self.ship_y)
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, ip.scale_y(0.02))

    def ip_draw_hud(self, ip):
        font = Style.FONT_DETAIL
        surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (10, 10))

if __name__ == "__main__":
    show(Asteroids)