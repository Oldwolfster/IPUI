# Key.py  Keyboard constants for IPUI.
# Use with ip.key_down(Key.LEFT), ip.key_pressed(Key.SPACE), etc.
# No strings. IDE autocomplete. Typo-proof.

import pygame


class Key:
    """Keyboard constants — thin wrapper over pygame.K_* for autocomplete."""

    # ── Letters ───────────────────────────────────────────
    A               = pygame.K_a
    B               = pygame.K_b
    C               = pygame.K_c
    D               = pygame.K_d
    E               = pygame.K_e
    F               = pygame.K_f
    G               = pygame.K_g
    H               = pygame.K_h
    I               = pygame.K_i
    J               = pygame.K_j
    K               = pygame.K_k
    L               = pygame.K_l
    M               = pygame.K_m
    N               = pygame.K_n
    O               = pygame.K_o
    P               = pygame.K_p
    Q               = pygame.K_q
    R               = pygame.K_r
    S               = pygame.K_s
    T               = pygame.K_t
    U               = pygame.K_u
    V               = pygame.K_v
    W               = pygame.K_w
    X               = pygame.K_x
    Y               = pygame.K_y
    Z               = pygame.K_z

    # ── Numbers ───────────────────────────────────────────
    NUM_0           = pygame.K_0
    NUM_1           = pygame.K_1
    NUM_2           = pygame.K_2
    NUM_3           = pygame.K_3
    NUM_4           = pygame.K_4
    NUM_5           = pygame.K_5
    NUM_6           = pygame.K_6
    NUM_7           = pygame.K_7
    NUM_8           = pygame.K_8
    NUM_9           = pygame.K_9

    # ── Arrows ────────────────────────────────────────────
    LEFT            = pygame.K_LEFT
    RIGHT           = pygame.K_RIGHT
    UP              = pygame.K_UP
    DOWN            = pygame.K_DOWN

    # ── Navigation ────────────────────────────────────────
    HOME            = pygame.K_HOME
    END             = pygame.K_END
    PAGEUP          = pygame.K_PAGEUP
    PAGEDOWN        = pygame.K_PAGEDOWN

    # ── Editing ───────────────────────────────────────────
    BACKSPACE       = pygame.K_BACKSPACE
    DELETE          = pygame.K_DELETE
    RETURN          = pygame.K_RETURN
    TAB             = pygame.K_TAB
    ESCAPE          = pygame.K_ESCAPE
    SPACE           = pygame.K_SPACE

    # ── Function keys ─────────────────────────────────────
    F1              = pygame.K_F1
    F2              = pygame.K_F2
    F3              = pygame.K_F3
    F4              = pygame.K_F4
    F5              = pygame.K_F5
    F6              = pygame.K_F6
    F7              = pygame.K_F7
    F8              = pygame.K_F8
    F9              = pygame.K_F9
    F10             = pygame.K_F10
    F11             = pygame.K_F11
    F12             = pygame.K_F12
