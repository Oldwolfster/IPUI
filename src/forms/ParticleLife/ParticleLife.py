import math
import random
import pygame
from ipui import *


class ParticleLife(_basePane):
    IP_LIFECYCLE = "pause"

    def initialize(self):
        self.particles             = []
        self.type_specs            = []
        self.g_lookup              = {}
        self.last_type_signature   = None
        self.last_matrix_signature = None
        self.status_frame_mod      = 0
        self.world_rect            = pygame.Rect(320, 120, 800, 560)
        self.lbl_status            = None
        self.lbl_types             = None


        self.grid_cell_size        = 50
        self.grid_cols             = 1
        self.grid_rows             = 1
        self.force_lut             = []
        self.force_lut_resolution  = 2
        self.force_lut_signature   = None


        self._refresh_sim_config(respawn=True)
        self.private_needs_respawn = True

    # ==========================================================
    # Build
    # ==========================================================
    def particle_life(self, parent):
        root = Card(parent)

        header = CardRow(root, width_flex=True, justify_spread=True)
        Heading(header, "Particle Life", glow=True)

        buttons = CardRow(header)
        Button(buttons, "Pause / Resume", on_click=self._toggle_pause)
        Button(buttons, "Respawn",        color_bg=Style.COLOR_PAL_GREEN_DARK, on_click=self._respawn_from_config)
        Button(buttons, "Shuffle Vel",    on_click=self._randomize_velocities)
        Button(buttons, "Center Burst",   on_click=self._center_burst)

        Body(root, "Simulation uses the Particles tab as its live config source.")
        Body(root, "Edit particle types or matrix values, then come back here — the sim auto-syncs.")
        Body(root, "World draws behind the UI. The left card is control/status; the right side is the playground.")

        self.lbl_status = Body(root, "")
        self.lbl_types  = Body(root, "")

    # ==========================================================
    # Lifecycle hooks
    # ==========================================================
    def ip_think(self, ctx):

        self.world_rect = self._compute_world_rect(ctx)
        if self.private_needs_respawn:
            self.private_needs_respawn = False
            self._respawn_from_config()
        self._ensure_force_lut()
        self._update_grid_geometry()

        if self._refresh_sim_config(respawn=False):
            # if counts/colors/types changed, particle set may have been rebuilt
            pass

        if self._read_bool("pl.sim.paused", False):
            self._publish_runtime_metrics(ctx)
            return

        if not self.particles:
            self._respawn_from_config()
            self._publish_runtime_metrics(ctx)
            return

        dt = max(0.0, min(float(ctx.dt), 0.05))

        r_min               = self._read_float("pl.sim.r_min", 10.0)
        r_mid               = self._read_float("pl.sim.r_mid", 40.0)
        r_max               = self._read_float("pl.sim.r_max", 90.0)
        force_scale         = self._read_float("pl.sim.force_scale", 120.0)
        collision_strength  = self._read_float("pl.sim.collision_strength", 2.0)
        damping             = self._read_float("pl.sim.damping", 0.05)
        v_max               = self._read_float("pl.sim.v_max", 180.0)

        n  = len(self.particles)
        ax = [0.0] * n
        ay = [0.0] * n

        world_w  = float(self.world_rect.width)
        world_h  = float(self.world_rect.height)
        r_max_sq = r_max * r_max

        grid = self._build_spatial_grid()

        # check current cell and adjacent cells only
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                bucket = grid[row][col]
                if not bucket:
                    continue

                for d_row in (-1, 0, 1):
                    n_row = (row + d_row) % self.grid_rows
                    for d_col in (-1, 0, 1):
                        n_col = (col + d_col) % self.grid_cols

                        if (n_row < row) or (n_row == row and n_col < col):
                            continue

                        other_bucket = grid[n_row][n_col]
                        if not other_bucket:
                            continue

                        if row == n_row and col == n_col:
                            for pos_i in range(len(bucket) - 1):
                                i   = bucket[pos_i]
                                p_i = self.particles[i]

                                for pos_j in range(pos_i + 1, len(bucket)):
                                    j   = bucket[pos_j]
                                    p_j = self.particles[j]

                                    dx, dy = self._wrapped_delta(p_i["x"], p_i["y"], p_j["x"], p_j["y"], world_w, world_h)
                                    dist_sq = (dx * dx) + (dy * dy)

                                    if dist_sq > r_max_sq:
                                        continue

                                    if dist_sq < 0.0001:
                                        angle = random.uniform(0.0, math.tau)
                                        dx    = math.cos(angle)
                                        dy    = math.sin(angle)
                                        dist  = 1.0
                                    else:
                                        dist = math.sqrt(dist_sq)

                                    ux = dx / dist
                                    uy = dy / dist

                                    g_ij = self.g_lookup.get((p_i["type"], p_j["type"]), 0.0)
                                    g_ji = self.g_lookup.get((p_j["type"], p_i["type"]), 0.0)

                                    f_ij = self._distance_force_fast(dist, r_min, r_mid, r_max, g_ij, collision_strength) * force_scale
                                    f_ji = self._distance_force_fast(dist, r_min, r_mid, r_max, g_ji, collision_strength) * force_scale

                                    ax[i] += ux * f_ij
                                    ay[i] += uy * f_ij

                                    ax[j] -= ux * f_ji
                                    ay[j] -= uy * f_ji
                        else:
                            for i in bucket:
                                p_i = self.particles[i]

                                for j in other_bucket:
                                    p_j = self.particles[j]

                                    dx, dy = self._wrapped_delta(p_i["x"], p_i["y"], p_j["x"], p_j["y"], world_w, world_h)
                                    dist_sq = (dx * dx) + (dy * dy)

                                    if dist_sq > r_max_sq:
                                        continue

                                    if dist_sq < 0.0001:
                                        angle = random.uniform(0.0, math.tau)
                                        dx    = math.cos(angle)
                                        dy    = math.sin(angle)
                                        dist  = 1.0
                                    else:
                                        dist = math.sqrt(dist_sq)

                                    ux = dx / dist
                                    uy = dy / dist

                                    g_ij = self.g_lookup.get((p_i["type"], p_j["type"]), 0.0)
                                    g_ji = self.g_lookup.get((p_j["type"], p_i["type"]), 0.0)

                                    f_ij = self._distance_force_fast(dist, r_min, r_mid, r_max, g_ij, collision_strength) * force_scale
                                    f_ji = self._distance_force_fast(dist, r_min, r_mid, r_max, g_ji, collision_strength) * force_scale

                                    ax[i] += ux * f_ij
                                    ay[i] += uy * f_ij

                                    ax[j] -= ux * f_ji
                                    ay[j] -= uy * f_ji

        damping_mult = max(0.0, 1.0 - (damping * dt * 60.0))

        for i, p in enumerate(self.particles):
            p["vx"] += ax[i] * dt
            p["vy"] += ay[i] * dt

            p["vx"] *= damping_mult
            p["vy"] *= damping_mult

            speed_sq = (p["vx"] * p["vx"]) + (p["vy"] * p["vy"])
            if speed_sq > (v_max * v_max):
                speed = math.sqrt(speed_sq)
                if speed > 0.0:
                    scale   = v_max / speed
                    p["vx"] *= scale
                    p["vy"] *= scale

            p["x"] = (p["x"] + (p["vx"] * dt)) % world_w
            p["y"] = (p["y"] + (p["vy"] * dt)) % world_h

        self._publish_runtime_metrics(ctx)

    def ip_renderpre(self, ctx):
        self.world_rect = self._compute_world_rect(ctx)

        trail_alpha = self._read_int("pl.sim.trail_alpha", 36)
        trail_alpha = max(0, min(255, trail_alpha))

        world = pygame.Surface((self.world_rect.width, self.world_rect.height), pygame.SRCALPHA)
        world.fill((9, 11, 18, trail_alpha))
        ctx.surface.blit(world, self.world_rect.topleft)

        pygame.draw.rect(ctx.surface, (36, 42, 58), self.world_rect, width=1, border_radius=10)

        for p in self.particles:
            px = self.world_rect.left + int(p["x"])
            py = self.world_rect.top  + int(p["y"])
            pygame.draw.circle(ctx.surface, p["color"], (px, py), p["radius"])

    def ip_renderpost(self, ctx):
        font = Style.FONT_DETAIL
        surf = font.render(f"FPS: {ctx.fps}", True, Style.COLOR_TEXT_ACCENT)
        x    = self.world_rect.left + 10
        y    = self.world_rect.top + 10
        ctx.surface.blit(surf, (x, y))

    # ==========================================================
    # User actions
    # ==========================================================
    def _toggle_pause(self):
        paused = self._read_bool("pl.sim.paused", False)
        self.form.pipeline_set("pl.sim.paused", not paused)

    def _respawn_from_config(self):
        self._refresh_sim_config(respawn=True)

    def _randomize_velocities(self):
        v_max = self._read_float("pl.sim.v_max", 180.0)
        for p in self.particles:
            p["vx"] = random.uniform(-v_max * 0.35, v_max * 0.35)
            p["vy"] = random.uniform(-v_max * 0.35, v_max * 0.35)

    def _center_burst(self):
        cx = self.world_rect.width  * 0.5
        cy = self.world_rect.height * 0.5
        v_max = self._read_float("pl.sim.v_max", 180.0)

        for p in self.particles:
            p["x"] = cx + random.uniform(-40.0, 40.0)
            p["y"] = cy + random.uniform(-40.0, 40.0)
            p["vx"] = random.uniform(-v_max * 0.45, v_max * 0.45)
            p["vy"] = random.uniform(-v_max * 0.45, v_max * 0.45)

    # ==========================================================
    # Config / cache
    # ==========================================================
    def seed_particle_types(self):
        ids = self.form.pipeline_read("pl.particle_ids")
        if ids:
            return
        types = [
            ("A", "A", 255, 80,  40,  50),
            ("B", "B", 40,  170, 255, 50),
            ("C", "C", 50,  220, 80,  50),
            ("D", "D", 220, 60,  220, 50),
        ]
        ids = [t[0] for t in types]
        self.form.pipeline_set("pl.particle_ids", ids)
        for pid, name, r, g, b, count in types:
            self.form.pipeline_set(f"pl.p.{pid}.name",  name)
            self.form.pipeline_set(f"pl.p.{pid}.r",     r)
            self.form.pipeline_set(f"pl.p.{pid}.g",     g)
            self.form.pipeline_set(f"pl.p.{pid}.b",     b)
            self.form.pipeline_set(f"pl.p.{pid}.count", count)
        for a in ids:
            for b in ids:
                self.form.pipeline_set(f"pl.G.{a}.{b}", round(random.uniform(-1.0, 1.0), 2))

    def _refresh_sim_config(self, respawn=False):
        changed = False

        type_signature = self._build_type_signature()
        if type_signature != self.last_type_signature:
            self.type_specs = self._read_type_specs()
            self.last_type_signature = type_signature
            changed = True
            respawn = True

        matrix_signature = self._build_matrix_signature()
        if matrix_signature != self.last_matrix_signature:
            self.g_lookup = self._read_matrix_lookup()
            self.last_matrix_signature = matrix_signature
            changed = True

        if respawn:
            self._spawn_particles()

        return changed

    def _build_type_signature(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        sig = []

        for pid in ids:
            sig.append((
                pid,
                self.form.pipeline_read(f"pl.p.{pid}.name"),
                self.form.pipeline_read(f"pl.p.{pid}.r"),
                self.form.pipeline_read(f"pl.p.{pid}.g"),
                self.form.pipeline_read(f"pl.p.{pid}.b"),
                self.form.pipeline_read(f"pl.p.{pid}.count"),
            ))

        return tuple(sig)

    def _build_matrix_signature(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        sig = []

        for a in ids:
            for b in ids:
                sig.append((a, b, self.form.pipeline_read(f"pl.G.{a}.{b}")))

        return tuple(sig)

    def _read_type_specs(self):
        ids    = self.form.pipeline_read("pl.particle_ids") or []
        specs  = []

        for pid in ids:
            name  = str(self.form.pipeline_read(f"pl.p.{pid}.name") or pid)
            r     = self._read_int(f"pl.p.{pid}.r", 180)
            g     = self._read_int(f"pl.p.{pid}.g", 180)
            b     = self._read_int(f"pl.p.{pid}.b", 180)
            count = max(0, self._read_int(f"pl.p.{pid}.count", 200))

            specs.append({
                "id":    pid,
                "name":  name,
                "color": (max(0, min(255, r)),
                          max(0, min(255, g)),
                          max(0, min(255, b))),
                "count": count,
            })

        return specs

    def _read_matrix_lookup(self):
        lookup = {}
        ids = self.form.pipeline_read("pl.particle_ids") or []

        for a in ids:
            for b in ids:
                lookup[(a, b)] = self._read_float(f"pl.G.{a}.{b}", 0.0)

        return lookup

    def _spawn_particles(self):
        self.particles = []

        if not self.type_specs:
            return

        world_w = float(self.world_rect.width)
        world_h = float(self.world_rect.height)
        v_max   = self._read_float("pl.sim.v_max", 180.0)

        for spec in self.type_specs:
            for _ in range(spec["count"]):
                self.particles.append({
                    "type":   spec["id"],
                    "color":  spec["color"],
                    "radius": 3,
                    "x":      random.uniform(0.0, world_w),
                    "y":      random.uniform(0.0, world_h),
                    "vx":     random.uniform(-v_max * 0.15, v_max * 0.15),
                    "vy":     random.uniform(-v_max * 0.15, v_max * 0.15),
                })

    # ==========================================================
    # Helpers
    # ==========================================================
    def _publish_runtime_metrics(self, ctx):
        self.form.pipeline_set("pl.sim.count", len(self.particles))
        self.form.pipeline_set("pl.sim.fps", ctx.fps)

        if self.status_frame_mod % 10 == 0:
            paused_text = "Paused" if self._read_bool("pl.sim.paused", False) else "Running"
            status = (
                f"{paused_text} | Particles: {len(self.particles)} | "
                f"World: {self.world_rect.width}x{self.world_rect.height} | FPS: {ctx.fps}"
            )

            type_summary = ", ".join(
                f"{spec['name']} ({spec['count']})"
                for spec in self.type_specs
            ) or "No particle types configured."

            if self.lbl_status is not None:
                self.lbl_status.set_text(status)

            if self.lbl_types is not None:
                self.lbl_types.set_text(type_summary)

        self.status_frame_mod += 1

    def _compute_world_rect(self, ctx):
        if ctx.rect_pane:
            return ctx.rect_pane
        return pygame.Rect(320, 120, 800, 560)

    def _wrapped_delta(self, ax, ay, bx, by, world_w, world_h):
        dx = bx - ax
        dy = by - ay

        half_w = world_w * 0.5
        half_h = world_h * 0.5

        if dx > half_w:
            dx -= world_w
        elif dx < -half_w:
            dx += world_w

        if dy > half_h:
            dy -= world_h
        elif dy < -half_h:
            dy += world_h

        return dx, dy

    def _distance_force(self, dist, r_min, r_mid, r_max, g_value, collision_strength):
        if dist <= 0.0001:
            return -collision_strength

        if dist < r_min:
            return -collision_strength * (1.0 - (dist / max(r_min, 0.0001)))

        if dist > r_max:
            return 0.0

        if dist <= r_mid:
            span = max(r_mid - r_min, 0.0001)
            t = (dist - r_min) / span
            return g_value * t

        span = max(r_max - r_mid, 0.0001)
        t = 1.0 - ((dist - r_mid) / span)
        return g_value * max(0.0, t)

    def _distance_force_fast(self, dist, r_min, r_mid, r_max, g_value, collision_strength):
        if dist <= 0.0001:
            return -collision_strength

        if not self.force_lut:
            return self._distance_force(dist, r_min, r_mid, r_max, g_value, collision_strength)

        lut_index = int(dist * self.force_lut_resolution)
        if lut_index < 0:
            lut_index = 0
        elif lut_index >= len(self.force_lut):
            lut_index = len(self.force_lut) - 1

        return self.force_lut[lut_index] * g_value

    def _ensure_force_lut(self):
        r_min              = self._read_float("pl.sim.r_min", 10.0)
        r_mid              = self._read_float("pl.sim.r_mid", 40.0)
        r_max              = self._read_float("pl.sim.r_max", 90.0)
        collision_strength = self._read_float("pl.sim.collision_strength", 2.0)

        signature = (r_min, r_mid, r_max, collision_strength, self.force_lut_resolution)
        if signature == self.force_lut_signature:
            return

        max_index = max(1, int(math.ceil(r_max * self.force_lut_resolution)) + 2)
        self.force_lut = [0.0] * max_index

        for i in range(max_index):
            dist = i / self.force_lut_resolution

            if dist <= 0.0001:
                self.force_lut[i] = -collision_strength
                continue

            if dist < r_min:
                self.force_lut[i] = -collision_strength * (1.0 - (dist / max(r_min, 0.0001)))
                continue

            if dist > r_max:
                self.force_lut[i] = 0.0
                continue

            if dist <= r_mid:
                span = max(r_mid - r_min, 0.0001)
                self.force_lut[i] = (dist - r_min) / span
                continue

            span = max(r_max - r_mid, 0.0001)
            self.force_lut[i] = max(0.0, 1.0 - ((dist - r_mid) / span))

        self.force_lut_signature = signature

    def _update_grid_geometry(self):
        self.grid_cols = max(1, int(math.ceil(self.world_rect.width  / self.grid_cell_size)))
        self.grid_rows = max(1, int(math.ceil(self.world_rect.height / self.grid_cell_size)))

    def _build_spatial_grid(self):
        grid = [
            [[] for _ in range(self.grid_cols)]
            for _ in range(self.grid_rows)
        ]

        inv_cell = 1.0 / self.grid_cell_size

        for index, p in enumerate(self.particles):
            col = int(p["x"] * inv_cell) % self.grid_cols
            row = int(p["y"] * inv_cell) % self.grid_rows
            grid[row][col].append(index)

        return grid

    def _set_default(self, key, value):
        if self.form.pipeline_read(key) is None:
            self.form.pipeline_set(key, value)

    def _read_float(self, key, default):
        value = self.form.pipeline_read(key)
        if value in (None, ""):
            return float(default)

        try:
            return float(value)
        except Exception:
            return float(default)

    def _read_int(self, key, default):
        value = self.form.pipeline_read(key)
        if value in (None, ""):
            return int(default)

        try:
            return int(float(value))
        except Exception:
            return int(default)

    def _read_bool(self, key, default):
        value = self.form.pipeline_read(key)
        if value is None:
            return bool(default)

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ("1", "true", "yes", "y", "on"):
                return True
            if normalized in ("0", "false", "no", "n", "off"):
                return False

        return bool(value)
