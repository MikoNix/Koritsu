import openai
import re


# ── Тарифы ───────────────────────────────────────────────────────────────
# Обновить согласно актуальным тарифам Yandex Cloud Foundation Models:
# https://yandex.cloud/ru/docs/foundation-models/pricing
PRICE_PER_1K_TOKENS = 0.82  # ₽ за 1000 токенов (вход + выход)
CHARS_PER_TOKEN     = 4    # ~4 символа на токен для кода


# ── Доступные модели ──────────────────────────────────────────────────────
# Ключ   — отображаемое название
# id     — идентификатор промпта в YandexGPT
# desc   — описание для UI
MODELS = {
    "Bauman 19.701": {
        "id":   "fvt60bpn6f51khbi7jjt",
        "desc": "Подходит для большинства университетов",
    },
    # Добавить другие модели:
    # "YandexGPT 5 Lite": {
    #     "id":   "PROMPT_ID_HERE",
    #     "desc": "Быстрее и дешевле, для простого кода",
    # },
}


def request(code_path, model_id=None):
    """
    Читает код из файла, отправляет в YandexGPT и возвращает JSON-текст.
    model_id — id промпта; если None, берётся первая модель из MODELS.
    """
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()

    prompt_id = model_id or next(iter(MODELS.values()))["id"]

    client = openai.OpenAI(
        api_key="",
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=""
    )

    response = client.responses.create(
        prompt={"id": prompt_id},
        input=code,
    )

    text = (response.output_text or "").strip()

    # Убираем markdown-обёртку ```json ... ``` если нейронка её добавила
    text = re.sub(r'^```[a-zA-Z]*\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    if not text:
        raise ValueError("AI вернул пустой ответ")
    if not text.startswith('['):
        raise ValueError(f"AI вернул не JSON-массив. Начало ответа: {text[:300]!r}")

    return text
