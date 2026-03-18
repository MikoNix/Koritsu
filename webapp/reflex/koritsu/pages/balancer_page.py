"""
Balancer Admin — Task Queue Dashboard
Endfield-inspired sci-fi UI
"""

import reflex as rx
from koritsu.state.balancer_state import BalancerState
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
ACCENT_GLOW_STRONG = "rgba(240, 192, 64, 0.25)"
TEXT = "rgba(255, 255, 255, 0.92)"
TEXT_DIM = "rgba(255, 255, 255, 0.45)"
TEXT_MID = "rgba(255, 255, 255, 0.65)"
DANGER = "#f87171"
SUCCESS = "#34d399"
CYAN = "#22d3ee"
MONO = "'SF Mono','Fira Code','Cascadia Code','Consolas',monospace"
SANS = "'Rajdhani','Exo 2','Segoe UI',system-ui,sans-serif"


# ── Reusable Components ──────────────────────────────────────────────────────

def corner_brackets(child: rx.Component, **props) -> rx.Component:
    """Wrap content in Endfield-style corner brackets."""
    return rx.box(
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
        child,
        position="relative",
        **props,
    )


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


def stat_box(label: str, value, color: str = ACCENT) -> rx.Component:
    return rx.box(
        rx.text(
            label,
            font_size="9px", letter_spacing="1.5px", text_transform="uppercase",
            color=TEXT_DIM, font_family=SANS, font_weight="600",
        ),
        rx.text(
            value,
            font_size="28px", font_weight="700", color=color,
            font_family=MONO, line_height="1.1",
            text_shadow=f"0 0 20px {ACCENT_GLOW}",
        ),
        padding="12px 16px",
        background=PANEL_LIGHT,
        border=f"1px solid {BORDER}",
        border_radius="2px",
        min_width="120px",
    )


def status_badge(status: rx.Var) -> rx.Component:
    return rx.match(
        status,
        ("pending", rx.badge("PENDING", color_scheme="yellow", variant="outline", size="1")),
        ("running", rx.badge("RUNNING", color_scheme="cyan", variant="outline", size="1")),
        ("completed", rx.badge("DONE", color_scheme="green", variant="outline", size="1")),
        ("failed", rx.badge("FAIL", color_scheme="red", variant="outline", size="1")),
        ("expired", rx.badge("EXPIRED", color_scheme="purple", variant="outline", size="1")),
        ("cancelled", rx.badge("CANCEL", color_scheme="gray", variant="outline", size="1")),
        rx.badge(status, variant="outline", size="1"),
    )


def priority_display(priority: rx.Var) -> rx.Component:
    return rx.match(
        priority,
        (0, rx.text("0", color=TEXT_DIM, font_family=MONO, font_size="13px", font_weight="700")),
        (1, rx.text("1", color="#60a5fa", font_family=MONO, font_size="13px", font_weight="700")),
        (2, rx.text("2", color=ACCENT, font_family=MONO, font_size="13px", font_weight="700")),
        (3, rx.text("3", color=DANGER, font_family=MONO, font_size="13px", font_weight="700",
                     text_shadow="0 0 8px rgba(248,113,113,0.4)")),
        rx.text("?", color=TEXT_DIM, font_family=MONO),
    )


# ── Animated Background ─────────────────────────────────────────────────────

def animated_bg() -> rx.Component:
    """Floating grid + moving particles effect via CSS."""
    return rx.fragment(
        # Grid pattern
        rx.box(
            position="fixed", top="0", left="0", right="0", bottom="0",
            background=(
                "linear-gradient(rgba(240,192,64,0.03) 1px, transparent 1px),"
                "linear-gradient(90deg, rgba(240,192,64,0.03) 1px, transparent 1px)"
            ),
            background_size="60px 60px",
            pointer_events="none",
            z_index="0",
        ),
        # Floating orb 1
        rx.box(
            position="fixed",
            width="300px", height="300px",
            border_radius="50%",
            background="radial-gradient(circle, rgba(240,192,64,0.06) 0%, transparent 70%)",
            top="10%", left="5%",
            animation="floatOrb1 20s ease-in-out infinite",
            pointer_events="none",
            z_index="0",
        ),
        # Floating orb 2
        rx.box(
            position="fixed",
            width="400px", height="400px",
            border_radius="50%",
            background="radial-gradient(circle, rgba(34,211,238,0.04) 0%, transparent 70%)",
            bottom="15%", right="10%",
            animation="floatOrb2 25s ease-in-out infinite",
            pointer_events="none",
            z_index="0",
        ),
        # Floating orb 3
        rx.box(
            position="fixed",
            width="200px", height="200px",
            border_radius="50%",
            background="radial-gradient(circle, rgba(232,121,249,0.04) 0%, transparent 70%)",
            top="60%", left="50%",
            animation="floatOrb3 18s ease-in-out infinite",
            pointer_events="none",
            z_index="0",
        ),
        # Diagonal scan line
        rx.box(
            position="fixed",
            top="0", left="-100%",
            width="50%", height="100%",
            background="linear-gradient(90deg, transparent, rgba(240,192,64,0.03), transparent)",
            transform="skewX(-15deg)",
            animation="scanDiag 8s linear infinite",
            pointer_events="none",
            z_index="0",
        ),
        # Scanline overlay
        rx.box(
            position="fixed", top="0", left="0", right="0", bottom="0",
            background="repeating-linear-gradient(transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
            pointer_events="none",
            z_index="1",
        ),
        # CSS keyframes
        rx.el.style("""
            @keyframes floatOrb1 {
                0%, 100% { transform: translate(0, 0) scale(1); }
                25% { transform: translate(80px, 40px) scale(1.1); }
                50% { transform: translate(30px, -60px) scale(0.95); }
                75% { transform: translate(-50px, 20px) scale(1.05); }
            }
            @keyframes floatOrb2 {
                0%, 100% { transform: translate(0, 0) scale(1); }
                33% { transform: translate(-60px, -40px) scale(1.15); }
                66% { transform: translate(40px, 50px) scale(0.9); }
            }
            @keyframes floatOrb3 {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(-80px, -60px); }
            }
            @keyframes scanDiag {
                0% { left: -50%; }
                100% { left: 150%; }
            }
            @keyframes pulseGlow {
                0%, 100% { opacity: 0.4; }
                50% { opacity: 1; }
            }
        """),
    )


# ── Header ───────────────────────────────────────────────────────────────────

def page_header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            # CMYK bars
            rx.hstack(
                rx.box(width="3px", height="28px", background="#22d3ee"),
                rx.box(width="3px", height="28px", background="#e879f9"),
                rx.box(width="3px", height="28px", background=ACCENT),
                rx.box(width="3px", height="28px", background="rgba(255,255,255,0.3)"),
                gap="2px",
            ),
            rx.vstack(
                rx.text(
                    "TASK BALANCER",
                    font_size="20px", font_weight="700", letter_spacing="3px",
                    color=TEXT, font_family=SANS,
                ),
                rx.text(
                    "QUEUE MANAGEMENT SYSTEM v0.1",
                    font_size="9px", letter_spacing="2px",
                    color=TEXT_DIM, font_family=MONO,
                ),
                gap="0",
            ),
            align_items="center", gap="14px",
        ),
        rx.spacer(),
        rx.box(
            rx.hstack(
                rx.icon("refresh-cw", size=14, color=ACCENT),
                rx.text(
                    "REFRESH", font_size="10px", letter_spacing="1.5px",
                    color=ACCENT, font_family=SANS, font_weight="600",
                ),
                gap="6px", align_items="center",
            ),
            padding="8px 16px",
            border=f"1px solid {BORDER_BRIGHT}",
            background="transparent",
            cursor="pointer",
            transition="all 0.2s",
            _hover={
                "background": ACCENT_GLOW,
                "border_color": ACCENT,
                "box_shadow": f"0 0 16px {ACCENT_GLOW}",
            },
            on_click=BalancerState.load_tasks,
        ),
        width="100%",
        padding="20px 28px",
        background="rgba(8, 8, 15, 0.92)",
        border_bottom=f"1px solid {BORDER}",
        align_items="center",
        position="relative",
        z_index="10",
    )


# ── Stats Bar ────────────────────────────────────────────────────────────────

def stats_bar() -> rx.Component:
    return rx.hstack(
        stat_box("Total", BalancerState.total_count),
        stat_box("Pending", BalancerState.pending_count, color="#f0c040"),
        stat_box("Running", BalancerState.running_count, color=CYAN),
        stat_box("Done", BalancerState.done_count, color=SUCCESS),
        stat_box("Failed", BalancerState.failed_count, color=DANGER),
        gap="12px",
        padding="16px 28px",
        width="100%",
        overflow_x="auto",
        flex_wrap="wrap",
        position="relative",
        z_index="10",
    )


# ── Status Filter Tabs ──────────────────────────────────────────────────────

def filter_tab(label: str, value: str, color: str = TEXT_MID) -> rx.Component:
    """Single filter tab button."""
    is_active = BalancerState.status_filter == value
    return rx.box(
        rx.text(
            label,
            font_size="10px",
            letter_spacing="1.5px",
            font_weight="600",
            font_family=SANS,
            color=rx.cond(is_active, ACCENT, TEXT_DIM),
        ),
        padding="6px 14px",
        cursor="pointer",
        border_bottom=rx.cond(
            is_active,
            f"2px solid {ACCENT}",
            "2px solid transparent",
        ),
        transition="all 0.2s",
        _hover={"background": ACCENT_GLOW},
        on_click=BalancerState.set_filter(value),
    )


def search_and_filters() -> rx.Component:
    return rx.vstack(
        # Search bar
        rx.hstack(
            rx.icon("search", size=16, color=TEXT_DIM),
            rx.input(
                value=BalancerState.search_query,
                on_change=BalancerState.set_search,
                placeholder="Search by UUID, username, destination...",
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
            rx.cond(
                BalancerState.search_query != "",
                rx.box(
                    rx.icon("x", size=12, color=TEXT_DIM),
                    cursor="pointer",
                    padding="4px",
                    _hover={"background": ACCENT_GLOW},
                    on_click=BalancerState.set_search(""),
                ),
            ),
            width="100%",
            padding="10px 16px",
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
        # Filter tabs
        rx.hstack(
            filter_tab("ALL", "all"),
            rx.box(width="1px", height="20px", background=BORDER),
            filter_tab("PENDING", "pending"),
            filter_tab("RUNNING", "running"),
            filter_tab("DONE", "completed"),
            filter_tab("FAILED", "failed"),
            filter_tab("EXPIRED", "expired"),
            filter_tab("CANCELLED", "cancelled"),
            gap="4px",
            align_items="center",
            overflow_x="auto",
            width="100%",
        ),
        gap="12px",
        width="100%",
        padding="0 28px",
        position="relative",
        z_index="10",
    )


# ── Task Row ─────────────────────────────────────────────────────────────────

def task_row(task: rx.Var) -> rx.Component:
    return rx.hstack(
        # Priority
        rx.box(
            priority_display(task["priority"]),
            min_width="30px", text_align="center",
        ),
        # UUID (short)
        rx.text(
            task["task_uuid"].to(str)[:8],
            font_family=MONO, font_size="12px", color=TEXT_MID, min_width="80px",
        ),
        # Status
        rx.box(status_badge(task["status"]), min_width="80px"),
        # Destination
        rx.text(
            task["task_dest"],
            font_family=MONO, font_size="12px", color=CYAN, min_width="80px",
        ),
        # Username
        rx.text(
            task["username"],
            font_size="12px", color=TEXT_MID, font_family=SANS, min_width="100px",
        ),
        rx.spacer(),
        # Cancel button (pending/running only)
        rx.cond(
            (task["status"] == "pending") | (task["status"] == "running"),
            rx.box(
                rx.icon("x", size=12, color=DANGER),
                padding="4px", cursor="pointer",
                border=f"1px solid rgba(248,113,113,0.2)",
                _hover={"background": "rgba(248,113,113,0.1)", "border_color": DANGER},
                on_click=BalancerState.cancel_task(task["task_uuid"]),
            ),
        ),
        # View detail
        rx.box(
            rx.icon("chevron-right", size=14, color=TEXT_DIM),
            padding="4px", cursor="pointer",
            _hover={"background": ACCENT_GLOW},
            on_click=BalancerState.select_task(task),
        ),
        width="100%",
        padding="10px 16px",
        align_items="center",
        gap="12px",
        background=PANEL_LIGHT,
        border_bottom="1px solid rgba(255,255,255,0.04)",
        transition="all 0.15s",
        _hover={"background": "rgba(240, 192, 64, 0.04)"},
    )


def task_table_header() -> rx.Component:
    labels = [("PRI", "30px"), ("UUID", "80px"), ("STATUS", "80px"),
              ("DEST", "80px"), ("USER", "100px")]
    return rx.hstack(
        *[
            rx.text(
                label,
                font_size="9px", letter_spacing="1.5px", color=TEXT_DIM,
                font_family=SANS, font_weight="600", min_width=w,
            )
            for label, w in labels
        ],
        width="100%", padding="8px 16px", gap="12px",
        border_bottom=f"1px solid {BORDER}",
    )


# ── Task List Panel ──────────────────────────────────────────────────────────

def task_list_panel() -> rx.Component:
    return rx.box(
        section_label("TASK QUEUE"),
        rx.box(
            corner_brackets(
                rx.vstack(
                    task_table_header(),
                    rx.cond(
                        BalancerState.filtered_tasks.length() > 0,
                        rx.vstack(
                            rx.foreach(BalancerState.filtered_tasks, task_row),
                            width="100%", gap="0",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("inbox", size=32, color=TEXT_DIM),
                                rx.text(
                                    "NO TASKS FOUND",
                                    font_size="11px", letter_spacing="2px",
                                    color=TEXT_DIM, font_family=SANS,
                                ),
                                align_items="center", gap="8px",
                            ),
                            padding="48px",
                        ),
                    ),
                    width="100%", gap="0",
                    max_height="600px", overflow_y="auto",
                ),
                padding="4px",
                background=PANEL,
                border=f"1px solid {BORDER}",
            ),
            margin_top="12px",
        ),
        width="100%",
    )


# ── Detail Modal ─────────────────────────────────────────────────────────────

def detail_modal() -> rx.Component:
    row_style = {
        "font_size": "12px", "font_family": MONO, "color": TEXT,
    }
    label_style = {
        "font_size": "9px", "letter_spacing": "1.5px", "text_transform": "uppercase",
        "color": TEXT_DIM, "font_family": SANS, "font_weight": "600", "min_width": "80px",
    }

    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.hstack(
                        rx.box(width="3px", height="16px", background=ACCENT),
                        rx.text(
                            "TASK DETAIL",
                            font_size="13px", letter_spacing="2px", font_weight="700",
                            color=ACCENT, font_family=SANS,
                        ),
                        gap="8px", align_items="center",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon("x", size=16, color=TEXT_DIM, cursor="pointer"),
                    ),
                    width="100%", align_items="center",
                ),
            ),
            rx.separator(color=BORDER),
            rx.vstack(
                rx.hstack(
                    rx.text("UUID", **label_style),
                    rx.text(BalancerState.selected_task["task_uuid"].to(str), **row_style),
                    align_items="baseline",
                ),
                rx.hstack(
                    rx.text("STATUS", **label_style),
                    status_badge(BalancerState.selected_task["status"].to(str)),
                    align_items="center",
                ),
                rx.hstack(
                    rx.text("PRIORITY", **label_style),
                    priority_display(BalancerState.selected_task["priority"].to(int)),
                    align_items="center",
                ),
                rx.hstack(
                    rx.text("DEST", **label_style),
                    rx.text(
                        BalancerState.selected_task["task_dest"].to(str),
                        color=CYAN, font_size="12px", font_family=MONO,
                    ),
                    align_items="baseline",
                ),
                rx.hstack(
                    rx.text("USER", **label_style),
                    rx.text(BalancerState.selected_task["username"].to(str), **row_style),
                    align_items="baseline",
                ),
                rx.hstack(
                    rx.text("ANSW TO", **label_style),
                    rx.text(BalancerState.selected_task["answ_to"].to(str), **row_style),
                    align_items="baseline",
                ),
                rx.cond(
                    BalancerState.selected_task.get("error", None),
                    rx.hstack(
                        rx.text("ERROR", **label_style),
                        rx.text(
                            BalancerState.selected_task["error"].to(str),
                            color=DANGER, font_size="12px", font_family=MONO,
                        ),
                        align_items="baseline",
                    ),
                ),
                rx.cond(
                    BalancerState.selected_task.get("result", None),
                    rx.vstack(
                        rx.text("RESULT", **label_style),
                        rx.box(
                            rx.text(
                                BalancerState.selected_task["result"].to(str),
                                font_size="11px", font_family=MONO, color=SUCCESS,
                                white_space="pre-wrap", word_break="break-all",
                            ),
                            padding="8px",
                            background="rgba(255,255,255,0.02)",
                            border=f"1px solid {BORDER}",
                            width="100%", max_height="200px", overflow_y="auto",
                        ),
                        gap="4px", width="100%",
                    ),
                ),
                gap="10px", padding="12px 0", width="100%",
            ),
            background="#0d1020",
            border=f"1px solid {BORDER_BRIGHT}",
            box_shadow=f"0 0 40px rgba(0,0,0,0.8), 0 0 80px {ACCENT_GLOW}",
            max_width="520px",
        ),
        open=BalancerState.show_detail,
        on_open_change=lambda v: BalancerState.set_show_detail(v),
    )


# ── Main Page ────────────────────────────────────────────────────────────────

def balancer_page() -> rx.Component:
    return rx.box(
        animated_bg(),
        header(show_nav_links=True),
        rx.vstack(
            # Balancer sub-header with title + refresh
            rx.hstack(
                rx.hstack(
                    rx.hstack(
                        rx.box(width="3px", height="28px", background="#22d3ee"),
                        rx.box(width="3px", height="28px", background="#e879f9"),
                        rx.box(width="3px", height="28px", background=ACCENT),
                        rx.box(width="3px", height="28px", background="rgba(255,255,255,0.3)"),
                        gap="2px",
                    ),
                    rx.vstack(
                        rx.text(
                            "TASK BALANCER",
                            font_size="20px", font_weight="700", letter_spacing="3px",
                            color=TEXT, font_family=SANS,
                        ),
                        rx.text(
                            "QUEUE MANAGEMENT SYSTEM v0.1",
                            font_size="9px", letter_spacing="2px",
                            color=TEXT_DIM, font_family=MONO,
                        ),
                        gap="0",
                    ),
                    align_items="center", gap="14px",
                ),
                rx.spacer(),
                rx.box(
                    rx.hstack(
                        rx.icon("refresh-cw", size=14, color=ACCENT),
                        rx.text(
                            "REFRESH", font_size="10px", letter_spacing="1.5px",
                            color=ACCENT, font_family=SANS, font_weight="600",
                        ),
                        gap="6px", align_items="center",
                    ),
                    padding="8px 16px",
                    border=f"1px solid {BORDER_BRIGHT}",
                    background="transparent",
                    cursor="pointer",
                    transition="all 0.2s",
                    _hover={
                        "background": ACCENT_GLOW,
                        "border_color": ACCENT,
                        "box_shadow": f"0 0 16px {ACCENT_GLOW}",
                    },
                    on_click=BalancerState.load_tasks,
                ),
                width="100%",
                padding="20px 28px",
                align_items="center",
                position="relative",
                z_index="10",
            ),
            # Decorative accent line
            rx.box(
                width="100%", height="1px",
                background=f"linear-gradient(90deg, transparent, {ACCENT_DIM}, transparent)",
                position="relative", z_index="10",
            ),
            stats_bar(),
            search_and_filters(),
            # Task table
            rx.box(
                task_list_panel(),
                padding="0 28px 28px 28px",
                width="100%",
                position="relative",
                z_index="10",
            ),
            width="100%",
            min_height="100vh",
            gap="0",
            padding_top="56px",  # space for fixed header
        ),
        detail_modal(),
        background=BG,
        min_height="100vh",
        position="relative",
        overflow="hidden",
    )
