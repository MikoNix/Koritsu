import reflex as rx
from koritsu.state.auth_state import AuthState
from koritsu.pages.home import _nav, _auth_modal

BG   = "linear-gradient(135deg, #08080f 0%, #0b0f1a 50%, #07101e 100%)"
PANEL = "rgba(255,255,255,0.05)"
BORDER = "rgba(255,255,255,0.10)"
ACCENT = "#3b82f6"
TEXT = "rgba(255,255,255,0.92)"
MUTED = "rgba(255,255,255,0.40)"
SANS = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',system-ui,sans-serif"


class RefPageState(rx.State):
    referral_code: str = ""
    is_loading: bool = True

    @rx.event
    async def on_load(self):
        """Читаем ref_code из URL и предзаполняем поле регистрации."""
        self.referral_code = self.router.page.params.get("ref_code", "")
        if self.referral_code:
            auth_state = await self.get_state(AuthState)
            auth_state.register_ref_code = self.referral_code
            auth_state.auth_tab = "register"
            auth_state.show_auth_modal = True
        self.is_loading = False


def ref_page() -> rx.Component:
    return rx.box(
        _nav(),
        _auth_modal(),
        rx.box(
            rx.vstack(
                rx.box(
                    rx.icon("users", size=40, color="white"),
                    width="80px",
                    height="80px",
                    background="linear-gradient(135deg, #3b82f6, #8b5cf6)",
                    border_radius="50%",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    margin_bottom="24px",
                ),
                rx.text(
                    "Вас пригласили в Koritsu!",
                    color=TEXT,
                    font_size="28px",
                    font_weight="700",
                    font_family=SANS,
                    margin_bottom="12px",
                    text_align="center",
                ),
                rx.text(
                    "Зарегистрируйтесь по реферальной ссылке",
                    color=MUTED,
                    font_size="16px",
                    font_family=SANS,
                    text_align="center",
                    margin_bottom="8px",
                ),
                rx.text(
                    "Реферальный код будет автоматически применён при регистрации",
                    color="rgba(255,255,255,0.30)",
                    font_size="14px",
                    font_family=SANS,
                    text_align="center",
                    margin_bottom="32px",
                ),
                rx.el.button(
                    "Зарегистрироваться",
                    on_click=AuthState.open_register,
                    color="white",
                    font_size="15px",
                    font_family=SANS,
                    font_weight="600",
                    background=f"linear-gradient(135deg,{ACCENT},#2563eb)",
                    border="none",
                    border_radius="12px",
                    padding="14px 32px",
                    cursor="pointer",
                    margin_bottom="16px",
                    width="100%",
                ),
                rx.el.button(
                    "Уже есть аккаунт? Войти",
                    on_click=AuthState.open_login,
                    color=MUTED,
                    font_size="14px",
                    font_family=SANS,
                    background="transparent",
                    border="none",
                    cursor="pointer",
                    width="100%",
                ),
                align="center",
                spacing="0",
            ),
            background=PANEL,
            border=f"1px solid {BORDER}",
            border_radius="24px",
            padding="48px",
            backdrop_filter="blur(20px)",
            max_width="440px",
            width="100%",
        ),
        background=BG,
        min_height="100vh",
        display="flex",
        align_items="center",
        justify_content="center",
        padding_top="76px",
        padding_x="20px",
        padding_bottom="20px",
    )
