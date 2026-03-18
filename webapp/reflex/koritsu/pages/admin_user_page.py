"""
Admin User Settings — manage any user by UUID.
Endfield-inspired sci-fi UI, same style as balancer page.
"""

import reflex as rx
from koritsu.state.admin_state import AdminState
from koritsu.components.header import header

# ── Endfield Palette ─────────────────────────────────────────────────────────
BG = "linear-gradient(135deg, #08080f 0%, #0b0f1a 50%, #07101e 100%)"
PANEL = "rgba(15, 18, 30, 0.85)"
PANEL_LIGHT = "rgba(255, 255, 255, 0.03)"
BORDER = "rgba(240, 192, 64, 0.15)"
BORDER_BRIGHT = "rgba(240, 192, 64, 0.35)"
ACCENT = "#f0c040"
ACCENT_DIM = "rgba(240, 192, 64, 0.6)"
ACCENT_GLOW = "rgba(240, 192, 64, 0.15)"
TEXT = "rgba(255, 255, 255, 0.92)"
TEXT_DIM = "rgba(255, 255, 255, 0.45)"
TEXT_MID = "rgba(255, 255, 255, 0.65)"
DANGER = "#f87171"
SUCCESS = "#34d399"
CYAN = "#22d3ee"
MONO = "'SF Mono','Fira Code','Cascadia Code','Consolas',monospace"
SANS = "'Rajdhani','Exo 2','Segoe UI',system-ui,sans-serif"


# ── Helpers ──────────────────────────────────────────────────────────────────

def section_label(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(width="3px", height="14px", background=ACCENT),
        rx.text(
            text,
            font_size="11px", font_weight="700", letter_spacing="2.5px",
            text_transform="uppercase", color=ACCENT, font_family=SANS,
        ),
        rx.box(flex="1", height="1px", background=BORDER),
        align_items="center", gap="10px", width="100%",
    )


LABEL_STYLE = {
    "font_size": "9px",
    "letter_spacing": "1.5px",
    "text_transform": "uppercase",
    "color": TEXT_DIM,
    "font_family": SANS,
    "font_weight": "600",
}

INPUT_STYLE = {
    "background": "rgba(255, 255, 255, 0.03)",
    "border": f"1px solid {BORDER}",
    "color": TEXT,
    "font_family": MONO,
    "font_size": "12px",
    "border_radius": "2px",
    "width": "100%",
    "_focus": {
        "border_color": ACCENT,
        "box_shadow": f"0 0 0 2px {ACCENT_GLOW}",
        "outline": "none",
    },
}


def field_row(label: str, value_input: rx.Component, action_btn: rx.Component = None) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(label, **LABEL_STYLE),
            value_input,
            gap="4px",
            flex="1",
        ),
        action_btn if action_btn else rx.fragment(),
        align_items="flex-end",
        gap="10px",
        width="100%",
    )


def save_button(label: str, on_click) -> rx.Component:
    return rx.box(
        rx.text(
            label,
            font_size="10px", letter_spacing="1.5px", font_weight="700",
            color="#0b0f1a", font_family=SANS,
        ),
        padding="8px 16px",
        background=ACCENT,
        cursor="pointer",
        transition="all 0.2s",
        _hover={"background": "#ffd966", "box_shadow": f"0 0 16px {ACCENT_GLOW}"},
        on_click=on_click,
        display="flex",
        align_items="center",
        justify_content="center",
        min_width="80px",
    )


# ── Search Panel ─────────────────────────────────────────────────────────────

def search_panel() -> rx.Component:
    return rx.box(
        section_label("FIND USER"),
        rx.box(
            rx.hstack(
                rx.icon("search", size=16, color=TEXT_DIM),
                rx.input(
                    value=AdminState.search_uuid,
                    on_change=AdminState.set_search_uuid,
                    placeholder="Enter user UUID...",
                    background="transparent",
                    border="none",
                    color=TEXT,
                    font_family=MONO,
                    font_size="12px",
                    width="100%",
                    outline="none",
                    _focus={"outline": "none", "box_shadow": "none"},
                    _placeholder={"color": TEXT_DIM},
                ),
                rx.box(
                    rx.text(
                        "SEARCH", font_size="10px", letter_spacing="1.5px",
                        font_weight="700", color="#0b0f1a", font_family=SANS,
                    ),
                    padding="6px 14px",
                    background=ACCENT,
                    cursor="pointer",
                    transition="all 0.2s",
                    _hover={"background": "#ffd966"},
                    on_click=AdminState.search_user,
                ),
                width="100%",
                padding="8px 14px",
                background=PANEL,
                border=f"1px solid {BORDER}",
                align_items="center",
                gap="10px",
                transition="all 0.2s",
                _focus_within={
                    "border_color": ACCENT,
                    "box_shadow": f"0 0 0 2px {ACCENT_GLOW}",
                },
            ),
            margin_top="12px",
        ),
        rx.cond(
            AdminState.search_error != "",
            rx.text(
                AdminState.search_error,
                font_size="11px", color=DANGER, font_family=MONO,
                margin_top="8px",
            ),
        ),
        width="100%",
    )


# ── User Info Card ───────────────────────────────────────────────────────────

def info_row(label: str, value) -> rx.Component:
    return rx.hstack(
        rx.text(label, min_width="100px", **LABEL_STYLE),
        rx.text(value, font_size="12px", font_family=MONO, color=TEXT),
        align_items="baseline",
    )


def user_info_card() -> rx.Component:
    return rx.box(
        section_label("USER INFO"),
        rx.box(
            # Corner brackets
            rx.box(
                position="absolute", top="0", left="0",
                width="14px", height="14px",
                border_top=f"1px solid {ACCENT}", border_left=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", top="0", right="0",
                width="14px", height="14px",
                border_top=f"1px solid {ACCENT}", border_right=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", bottom="0", left="0",
                width="14px", height="14px",
                border_bottom=f"1px solid {ACCENT}", border_left=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", bottom="0", right="0",
                width="14px", height="14px",
                border_bottom=f"1px solid {ACCENT}", border_right=f"1px solid {ACCENT}",
            ),
            rx.vstack(
                info_row("UUID", AdminState.user_uuid),
                info_row("USERNAME", AdminState.username),
                info_row("DISPLAY", AdminState.display_name),
                info_row("SUB LEVEL", AdminState.sub_level),
                info_row("EXPIRES", AdminState.sub_expire_date),
                info_row("TOKENS", AdminState.tokens_left),
                gap="8px",
                width="100%",
            ),
            position="relative",
            padding="20px",
            background=PANEL,
            border=f"1px solid {BORDER}",
            margin_top="12px",
        ),
        width="100%",
    )


# ── Edit Panel ───────────────────────────────────────────────────────────────

def edit_panel() -> rx.Component:
    return rx.box(
        section_label("EDIT USER"),
        rx.box(
            rx.box(
                position="absolute", top="0", left="0",
                width="14px", height="14px",
                border_top=f"1px solid {ACCENT}", border_left=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", top="0", right="0",
                width="14px", height="14px",
                border_top=f"1px solid {ACCENT}", border_right=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", bottom="0", left="0",
                width="14px", height="14px",
                border_bottom=f"1px solid {ACCENT}", border_left=f"1px solid {ACCENT}",
            ),
            rx.box(
                position="absolute", bottom="0", right="0",
                width="14px", height="14px",
                border_bottom=f"1px solid {ACCENT}", border_right=f"1px solid {ACCENT}",
            ),
            rx.vstack(
                # Username
                field_row(
                    "USERNAME",
                    rx.input(
                        value=AdminState.edit_username,
                        on_change=AdminState.set_edit_username,
                        **INPUT_STYLE,
                    ),
                    save_button("SAVE", AdminState.save_username),
                ),
                # Display name
                field_row(
                    "DISPLAY NAME",
                    rx.input(
                        value=AdminState.edit_display_name,
                        on_change=AdminState.set_edit_display_name,
                        **INPUT_STYLE,
                    ),
                    save_button("SAVE", AdminState.save_display_name),
                ),
                # Tokens
                field_row(
                    "TOKENS",
                    rx.input(
                        value=AdminState.edit_tokens,
                        on_change=AdminState.set_edit_tokens,
                        **INPUT_STYLE,
                    ),
                    save_button("SET", AdminState.save_tokens),
                ),
                # Feedback
                rx.cond(
                    AdminState.save_success != "",
                    rx.text(AdminState.save_success, font_size="11px", color=SUCCESS, font_family=MONO),
                ),
                rx.cond(
                    AdminState.save_error != "",
                    rx.text(AdminState.save_error, font_size="11px", color=DANGER, font_family=MONO),
                ),
                gap="16px",
                padding="20px",
                width="100%",
            ),
            position="relative",
            background=PANEL,
            border=f"1px solid {BORDER}",
            margin_top="12px",
        ),
        width="100%",
    )


# ── Warning Banner ───────────────────────────────────────────────────────────

def warning_banner() -> rx.Component:
    return rx.hstack(
        rx.icon("triangle-alert", size=16, color=ACCENT),
        rx.text(
            "ADMIN ACCESS — NO AUTH PROTECTION. DO NOT EXPOSE IN PRODUCTION.",
            font_size="10px", letter_spacing="1px", color=ACCENT,
            font_family=MONO, font_weight="600",
        ),
        padding="10px 20px",
        background="rgba(240,192,64,0.06)",
        border=f"1px solid {BORDER_BRIGHT}",
        align_items="center",
        gap="10px",
        width="100%",
    )


# ── Background (reuse from balancer) ────────────────────────────────────────

def animated_bg() -> rx.Component:
    return rx.fragment(
        rx.box(
            position="fixed", top="0", left="0", right="0", bottom="0",
            background=(
                "linear-gradient(rgba(240,192,64,0.03) 1px, transparent 1px),"
                "linear-gradient(90deg, rgba(240,192,64,0.03) 1px, transparent 1px)"
            ),
            background_size="60px 60px",
            pointer_events="none", z_index="0",
        ),
        rx.box(
            position="fixed",
            width="300px", height="300px",
            border_radius="50%",
            background="radial-gradient(circle, rgba(240,192,64,0.06) 0%, transparent 70%)",
            top="20%", right="10%",
            animation="floatOrb1 20s ease-in-out infinite",
            pointer_events="none", z_index="0",
        ),
        rx.box(
            position="fixed", top="0", left="0", right="0", bottom="0",
            background="repeating-linear-gradient(transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
            pointer_events="none", z_index="1",
        ),
        rx.el.style("""
            @keyframes floatOrb1 {
                0%, 100% { transform: translate(0, 0) scale(1); }
                25% { transform: translate(80px, 40px) scale(1.1); }
                50% { transform: translate(30px, -60px) scale(0.95); }
                75% { transform: translate(-50px, 20px) scale(1.05); }
            }
        """),
    )


# ── Main Page ────────────────────────────────────────────────────────────────

def admin_user_page() -> rx.Component:
    return rx.box(
        animated_bg(),
        header(show_nav_links=True),
        rx.vstack(
            # Sub-header
            rx.hstack(
                rx.hstack(
                    rx.hstack(
                        rx.box(width="3px", height="28px", background=DANGER),
                        rx.box(width="3px", height="28px", background=ACCENT),
                        gap="2px",
                    ),
                    rx.vstack(
                        rx.text(
                            "USER MANAGEMENT",
                            font_size="20px", font_weight="700", letter_spacing="3px",
                            color=TEXT, font_family=SANS,
                        ),
                        rx.text(
                            "ADMIN PANEL // NO AUTH",
                            font_size="9px", letter_spacing="2px",
                            color=DANGER, font_family=MONO,
                        ),
                        gap="0",
                    ),
                    align_items="center", gap="14px",
                ),
                rx.spacer(),
                rx.link(
                    rx.box(
                        rx.hstack(
                            rx.icon("arrow-left", size=14, color=ACCENT),
                            rx.text(
                                "BALANCER", font_size="10px", letter_spacing="1.5px",
                                color=ACCENT, font_family=SANS, font_weight="600",
                            ),
                            gap="6px", align_items="center",
                        ),
                        padding="8px 16px",
                        border=f"1px solid {BORDER_BRIGHT}",
                        cursor="pointer",
                        transition="all 0.2s",
                        _hover={"background": ACCENT_GLOW, "border_color": ACCENT},
                    ),
                    href="/balancer",
                    text_decoration="none",
                ),
                width="100%",
                padding="20px 28px",
                align_items="center",
                position="relative",
                z_index="10",
            ),
            # Warning
            rx.box(
                warning_banner(),
                padding="0 28px",
                width="100%",
                position="relative",
                z_index="10",
            ),
            # Content
            rx.box(
                rx.vstack(
                    search_panel(),
                    rx.cond(
                        AdminState.user_loaded,
                        rx.vstack(
                            user_info_card(),
                            edit_panel(),
                            gap="20px",
                            width="100%",
                        ),
                    ),
                    gap="20px",
                    width="100%",
                    max_width="700px",
                ),
                padding="20px 28px",
                width="100%",
                position="relative",
                z_index="10",
            ),
            width="100%",
            min_height="100vh",
            gap="0",
            padding_top="56px",
        ),
        background=BG,
        min_height="100vh",
        position="relative",
        overflow="hidden",
    )
