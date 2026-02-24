import streamlit as st
from pathlib import Path


def util_sidebar():
    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />',
        unsafe_allow_html=True
    )
    css_path = Path(__file__).parent / "static" / "css" / "sidebar.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.write("Menu")
        if st.button("HOME", icon=":material/home:"):
            st.switch_page("home.py")
        if st.button("Генератор отчётов", icon=":material/edit_document:"):
            st.switch_page("pages/Template.py")
        if st.button("Генератор блоксхем", icon=":material/schema:"):
            st.switch_page("pages/SchemeAI.py")
        if st.button("ТЕСТ", icon=":material/psychology:"):
            st.switch_page("pages/page3.py")


PAGES = [
    {"title": "Генератор отчётов",  "icon": "edit_document", "desc": "Создавайте Jinja-шаблоны и генерируйте готовые документы автоматически.", "color": "#58a6ff", "page": "pages/Template.py"},
    {"title": "Генератор блоксхем", "icon": "schema",        "desc": "Постройте блок-схему любого процесса с помощью AI за несколько секунд.",  "color": "#a371f7", "page": "pages/SchemeAI.py"},
    {"title": "ТЕСТ",               "icon": "psychology",    "desc": "Экспериментальный модуль для тестирования новых возможностей.",             "color": "#ff7b72", "page": "pages/page3.py"},
]

PLANS = [
    {
        "name": "Free",
        "price": "0 ₽",
        "period": "навсегда",
        "accent": "#8b949e",
        "features": ["5 отчётов / месяц", "3 блок-схемы", "Базовые шаблоны"],
        "cta": "Текущий план",
        "disabled": True,
    },
    {
        "name": "Pro",
        "price": "790 ₽",
        "period": "в месяц",
        "accent": "#58a6ff",
        "features": ["Безлимитные отчёты", "Безлимитные схемы", "Приоритетный AI", "Экспорт PDF/DOCX"],
        "cta": "Выбрать Pro",
        "disabled": False,
        "badge": "Популярный",
    },
    {
        "name": "Team",
        "price": "2 490 ₽",
        "period": "в месяц",
        "accent": "#a371f7",
        "features": ["Всё из Pro", "До 10 пользователей", "Командные шаблоны", "Аналитика и логи"],
        "cta": "Выбрать Team",
        "disabled": False,
    },
]


def load_css():
    css_path = Path(__file__).parent / "static" / "css" / "home.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page_cards():
    """HTML-карточки страниц — работают нормально."""
    cards_html = '<div class="cards-grid">'
    for p in PAGES:
        cards_html += f"""
        <a class="page-card" href="?nav={p['page']}" style="--card-accent:{p['color']}">
            <div class="spin-border"></div>
            <div class="card-inner">
                <div class="page-card__icon">
                    <div class="mat-icon">{p['icon']}</div>
                </div>
                <div class="page-card__title">{p['title']}</div>
                <div class="page-card__desc">{p['desc']}</div>
                <div class="page-card__arrow">→</div>
            </div>
        </a>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def render_plan_cards():
    """Карточки подписок через нативный st.columns + st.container."""
    cols = st.columns(3, gap="medium")

    for col, plan in zip(cols, PLANS):
        with col:
            # Обёртка с CSS-классом для спин-бордера
            st.markdown(
                f'<div class="plan-card" style="--plan-accent:{plan["accent"]}">'
                f'<div class="spin-border"></div></div>',
                unsafe_allow_html=True,
            )

            # Нативный контейнер поверх — весь контент через st.*
            with st.container():
                st.markdown(
                    f'<div class="plan-container" style="--plan-accent:{plan["accent"]}">',
                    unsafe_allow_html=True,
                )

                # Бейдж
                if plan.get("badge"):
                    st.markdown(
                        f'<div class="plan-badge">{plan["badge"]}</div>',
                        unsafe_allow_html=True,
                    )

                # Название + цена
                st.markdown(
                    f'<div class="plan-name">{plan["name"]}</div>'
                    f'<div class="plan-price">'
                    f'<div class="plan-amount">{plan["price"]}</div>'
                    f'<div class="plan-period">/{plan["period"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Фичи
                for feature in plan["features"]:
                    st.markdown(
                        f'<div class="plan-feature">'
                        f'<div class="check-dot" style="background:{plan["accent"]}"></div>'
                        f'{feature}</div>',
                        unsafe_allow_html=True,
                    )

                # Кнопка
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                if not plan["disabled"]:
                    if st.button(plan["cta"], key=f"plan_{plan['name']}", use_container_width=True):
                        pass  # логика оплаты
                else:
                    st.button(plan["cta"], key=f"plan_{plan['name']}", disabled=True, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Главная", layout="wide", initial_sidebar_state="expanded")
    util_sidebar()
    load_css()

    params = st.query_params
    if "nav" in params:
        st.switch_page(params["nav"])

    # Hero
    st.markdown("""
    <div class="hero">
        <h1>Добро пожаловать 👋</h1>
        <p>Выберите инструмент ниже или перейдите через боковое меню.</p>
        <div class="hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Инструменты</p>', unsafe_allow_html=True)
    render_page_cards()

    st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Подписки</p>', unsafe_allow_html=True)
    render_plan_cards()


if __name__ == "__main__":
    main()