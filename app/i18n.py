import streamlit as st

# --- Translations -------------------------------------------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "Option Tool",
        "inputs": "Inputs",
        "underlying_price": "Underlying Stock Price",
        "std_dev_pct": "Price range (%)",
        "num_combos": "Number of Option Combinations",
        "option_n": "Option {n}",
        "option_type": "Option Type",
        "position": "Position",
        "quantity": "Quantity",
        "premium": "Premium",
        "strike_price": "Strike Price",
        "call": "Call",
        "put": "Put",
        "long_call": "Long Call",
        "short_call": "Short Call",
        "long_put": "Long Put",
        "short_put": "Short Put",
        "payoff_diagram": "Payoff Diagram",
        "xaxis_title": "Stock Price at Expiry",
        "yaxis_title": "Net Payoff",
        "max_gain": "Max Gain",
        "min_gain": "Min Gain",
        "total_cost": "Total cost to enter the position",
        "max_gain_label": "Maximum Gain",
        "min_gain_label": "Minimum Gain (Max Loss)",
        "bullish": "Bullish",
        "bearish": "Bearish",
        "neutral": "Neutral",
        "invest": "Invest",
        "dont_invest": "Don't Invest",
        "footer": "Powered by ToxicVolt",
        "language": "Language",
        "lang_en": "English",
        "lang_ru": "Russian",
        "lang_uk": "Ukrainian",
        "show_zero_line": "Show P/L = 0 line",
        "show_strike_lines": "Show strike lines",
        "show_underlying_line": "Show underlying price line",

    },
    "uk": {
        "app_title": "Інструмент опціонів",
        "inputs": "Параметри",
        "underlying_price": "Ціна базового активу",
        "std_dev_pct": "Диапазон цен (±%)",
        "num_combos": "Кількість комбінацій опціонів",
        "option_n": "Опціон {n}",
        "option_type": "Тип опціону",
        "position": "Позиція",
        "quantity": "Кількість",
        "premium": "Премія",
        "strike_price": "Страйк",
        "call": "Колл",
        "put": "Пут",
        "long_call": "Покупка колла",
        "short_call": "Продаж колла",
        "long_put": "Покупка пута",
        "short_put": "Продаж пута",
        "payoff_diagram": "Діаграма прибутку/збитку",
        "xaxis_title": "Ціна активу на експірації",
        "yaxis_title": "Сумарний результат",
        "max_gain": "Макс. прибуток",
        "min_gain": "Мін. результат",
        "total_cost": "Вартість входу в позицію",
        "max_gain_label": "Максимальний прибуток",
        "min_gain_label": "Мінімальний результат (макс. збиток)",
        "bullish": "Бичачий",
        "bearish": "Ведмежий",
        "neutral": "Нейтральний",
        "invest": "Інвестувати",
        "dont_invest": "Не інвестувати",
        "footer": "Powered by ToxicVolt",
        "language": "Мова",
        "lang_en": "Англійська",
        "lang_ru": "Російська",
        "lang_uk": "Українська",
        "show_zero_line": "Показати лінію P/L = 0",
        "show_strike_lines": "Показати лінії страйків",
        "show_underlying_line": "Показати лінію поточної ціни",

    },
}

def get_lang() -> str:
    """Read ?lang=xx from URL or session; default 'en'."""
    qp = st.query_params
    if "lang" in qp and qp["lang"] in TRANSLATIONS:
        st.session_state["lang"] = qp["lang"]
    return st.session_state.get("lang", "en")

def t(key: str, **fmt) -> str:
    """Translate a key using current lang; fallback to English."""
    lang = st.session_state.get("lang", "en")
    d = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    s = d.get(key, TRANSLATIONS["en"].get(key, key))
    return s.format(**fmt) if fmt else s

def language_selector():
    """Render language switcher in sidebar and keep URL in sync."""
    lang_code = get_lang()
    # Show names in the currently selected language
    lang_names = {
        "en": TRANSLATIONS[lang_code]["lang_en"],
        "uk": TRANSLATIONS[lang_code]["lang_uk"],
    }
    chosen = st.selectbox(
        t("language"),
        options=["en", "uk"],
        index=["en", "uk"].index(lang_code),
        format_func=lambda code: lang_names[code],
        key="lang_select",
    )
    if chosen != st.session_state.get("lang", "en"):
        st.session_state["lang"] = chosen
        st.query_params["lang"] = chosen
        st.rerun()
# -----------------------------------------------------------------------------