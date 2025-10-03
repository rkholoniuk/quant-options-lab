# app/main.py
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from i18n import t, language_selector

COLOR_MAP = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]
# --------------------------- Data Model ---------------------------------------
@dataclass
class OptionLeg:
    type: str     # "CALL" | "PUT"
    pos: str      # "LONG_CALL" | "SHORT_CALL" | "LONG_PUT" | "SHORT_PUT"
    quantity: int
    premium: float
    strike: float


# --------------------------- Computation --------------------------------------
def payoff(stock_price: float, leg: OptionLeg) -> float:
    """Single-leg P/L at expiry."""
    if leg.type == "CALL":
        intrinsic = max(stock_price - leg.strike, 0.0)
        is_long = (leg.pos == "LONG_CALL")
    else:  # PUT
        intrinsic = max(leg.strike - stock_price, 0.0)
        is_long = (leg.pos == "LONG_PUT")
    return (intrinsic - leg.premium) if is_long else (-intrinsic + leg.premium)


def compute_curve(
    underlying_price: float,
    std_dev_pct: float,
    legs: List[OptionLeg],
) -> Dict:
    """Build x-grid and aggregate portfolio P/L curve + stats."""
    upper = underlying_price * (1 + std_dev_pct / 100.0)
    lower = underlying_price * (1 - std_dev_pct / 100.0)
    x = np.linspace(lower, upper, 400)

    y = []
    for price in x:
        total = 0.0
        for leg in legs:
            total += payoff(price, leg) * leg.quantity
        y.append(total)

    y_arr = np.asarray(y, dtype=float)
    max_gain = float(np.max(y_arr))
    min_gain = float(np.min(y_arr))
    i_max = int(np.argmax(y_arr))
    i_min = int(np.argmin(y_arr))

    long_total = sum(l.premium * l.quantity for l in legs if l.pos.startswith("LONG"))
    short_total = sum(l.premium * l.quantity for l in legs if l.pos.startswith("SHORT"))
    total_cost = long_total - short_total

    return {
        "x": x,
        "y": y_arr,
        "max_gain": max_gain,
        "min_gain": min_gain,
        "i_max": i_max,
        "i_min": i_min,
        "total_cost": total_cost,
    }


# --------------------------- UI Builders --------------------------------------
def build_sidebar() -> Tuple[float, float, Dict[str, bool], List[OptionLeg]]:
    """All sidebar inputs in one place. Returns (underlying, std_dev, toggles, legs)."""
    with st.sidebar:
        language_selector()
        st.header(t("inputs"))

        underlying_price = st.number_input(
            t("underlying_price"), min_value=1.0, max_value=1000.0, value=100.0, step=0.1
        )
        std_dev = st.number_input(
            t("std_dev_pct"), min_value=0.0, max_value=100.0, value=10.0, step=0.1
        )

        # Toggles for reference lines
        toggles = {
            "show_zero": st.checkbox(t("show_zero_line"), value=True, key="tgl_zero"),
            "show_strikes": st.checkbox(t("show_strike_lines"), value=True, key="tgl_strikes"),
            "show_underlying": st.checkbox(t("show_underlying_line"), value=True, key="tgl_under"),
        }

        # Position legs
        option_data: List[OptionLeg] = []
        option_count = st.number_input(t("num_combos"), min_value=1, max_value=10, value=1, step=1)

        OPTION_TYPES = ["CALL", "PUT"]
        POS_CALL = ["LONG_CALL", "SHORT_CALL"]
        POS_PUT = ["LONG_PUT", "SHORT_PUT"]

        def format_option_type(code: str) -> str:
            return t("call") if code == "CALL" else t("put")

        def format_position(code: str) -> str:
            return {
                "LONG_CALL": t("long_call"),
                "SHORT_CALL": t("short_call"),
                "LONG_PUT": t("long_put"),
                "SHORT_PUT": t("short_put"),
            }[code]

        for i in range(option_count):
            st.subheader(t("option_n", n=i + 1))
            opt_type_code = st.selectbox(
                t("option_type"),
                options=OPTION_TYPES,
                format_func=format_option_type,
                key=f"type_{i}",
            )
            pos_options = POS_CALL if opt_type_code == "CALL" else POS_PUT
            pos_code = st.selectbox(
                t("position"),
                options=pos_options,
                format_func=format_position,
                key=f"pos_{i}",
            )
            quantity = st.number_input(t("quantity"), value=1, key=f"qty_{i}")
            premium = st.number_input(t("premium"), min_value=0.0, value=5.0, step=0.1, key=f"prem_{i}")
            strike_price = st.number_input(t("strike_price"), min_value=0.0, value=100.0, step=0.1, key=f"strike_{i}")

            option_data.append(
                OptionLeg(
                    type=opt_type_code,
                    pos=pos_code,
                    quantity=int(quantity),
                    premium=float(premium),
                    strike=float(strike_price),
                )
            )

    return float(underlying_price), float(std_dev), toggles, option_data


def draw_chart(
    x: np.ndarray,
    y: np.ndarray,
    underlying_price: float,
    std_dev_pct: float,
    max_gain: float,
    min_gain: float,
    i_max: int,
    i_min: int,
    legs: List[OptionLeg],
    toggles: Dict[str, bool],
):
    """Render the payoff chart with per-leg colored profiles and a bold net curve."""
    fig = go.Figure()

    # --- σ-band around underlying ------------------------------------------------
    band = underlying_price * (std_dev_pct / 100.0)
    fig.add_shape(
        type="rect",
        x0=underlying_price - band,
        x1=underlying_price + band,
        y0=min_gain,
        y1=max_gain,
        fillcolor="LightSkyBlue",
        opacity=0.35,
        layer="below",
        line_width=0,
    )

    # --- Individual legs (colored, dotted) --------------------------------------
    for idx, leg in enumerate(legs[:10]):  # cap to first 10 legs for the palette
        leg_y = [payoff(px, leg) * leg.quantity for px in x]
        fig.add_trace(go.Scatter(
            x=x,
            y=leg_y,
            mode="lines",
            name=f"{leg.pos} {leg.type} K={leg.strike:g}",
            line=dict(color=COLOR_MAP[idx % len(COLOR_MAP)], dash="dot", width=1.5),
            legendgroup="legs",
            hovertemplate="S=%{x:.2f}<br>P/L=%{y:.2f}<extra>%{fullData.name}</extra>",
        ))

    # --- Net payoff (bold, black) -----------------------------------------------
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines",
        name=t("yaxis_title"),
        line=dict(color="black", width=2.5),
        legendgroup="net",
        hovertemplate="S=%{x:.2f}<br>Net P/L=%{y:.2f}<extra></extra>",
    ))

    # --- Max/Min markers ---------------------------------------------------------
    fig.add_annotation(
        x=x[i_max], y=max_gain, text=t("max_gain"),
        showarrow=True, arrowhead=4, ax=0, ay=-40
    )
    fig.add_annotation(
        x=x[i_min], y=min_gain, text=t("min_gain"),
        showarrow=True, arrowhead=4, ax=0, ay=40
    )

    # --- Reference lines ---------------------------------------------------------
    if toggles.get("show_zero"):
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")

    if toggles.get("show_underlying"):
        fig.add_vline(x=underlying_price, line_width=1.5, line_dash="solid", line_color="black")

    if toggles.get("show_strikes") and legs:
        for s in sorted({leg.strike for leg in legs}):
            fig.add_vline(x=s, line_width=1, line_dash="dot", line_color="darkgreen")

    # --- Layout ------------------------------------------------------------------
    fig.update_layout(
        title=t("payoff_diagram"),
        xaxis_title=t("xaxis_title"),
        yaxis_title=t("yaxis_title"),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------- App Entry ----------------------------------------
def main():
    st.title(t("app_title"))

    underlying_price, std_dev, toggles, legs = build_sidebar()
    results = compute_curve(underlying_price, std_dev, legs)

    draw_chart(
        x=results["x"],
        y=results["y"],
        underlying_price=underlying_price,
        std_dev_pct=std_dev,
        max_gain=results["max_gain"],
        min_gain=results["min_gain"],
        i_max=results["i_max"],
        i_min=results["i_min"],
        legs=legs,
        toggles=toggles,
    )

    # Metrics
    st.write(f"{t('total_cost')}: ${results['total_cost']:.0f}")
    st.write(f"{t('max_gain_label')}: ${results['max_gain']:.0f}")
    st.write(f"{t('min_gain_label')}: ${results['min_gain']:.0f}")

    # Simple inference
    threshold = 0.05 * underlying_price
    max_gain_stock_price = results["x"][results["i_max"]]
    skew = (
        t("bullish") if max_gain_stock_price > underlying_price + threshold
        else t("bearish") if max_gain_stock_price < underlying_price - threshold
        else t("neutral")
    )
    decision = t("invest") if results["max_gain"] > 0 else t("dont_invest")
    st.write(skew)
    st.write(decision)

    # Footer
    st.markdown(
        f"""
        <style>.footer {{ position: fixed; bottom: 5px; right: 10px; }}</style>
        <div class="footer">{t('footer')}</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
