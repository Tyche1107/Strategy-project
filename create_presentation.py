"""
Generate UW-style presentation for CFRM 522 Strategy Project
With all figures included
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

# UW Colors
UW_PURPLE = RGBColor(0x4B, 0x2E, 0x83)
UW_GOLD = RGBColor(0xB7, 0xA5, 0x7A)
UW_METALLIC_GOLD = RGBColor(0xE8, 0xE3, 0xD3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_title_shape(slide, text, left, top, width, height, font_size=32, bold=True, color=WHITE):
    shape = slide.shapes.add_textbox(left, top, width, height)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.LEFT
    return shape

def add_bullet_text(slide, bullets, left, top, width, height, font_size=18, color=DARK_GRAY):
    shape = slide.shapes.add_textbox(left, top, width, height)
    tf = shape.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = "Arial"
        p.level = 0
        p.space_before = Pt(4)
        p.space_after = Pt(4)
    return shape

def add_header_bar(slide, text, prs):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, Inches(1.0)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_PURPLE
    shape.line.fill.background()

    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.25),
        Inches(12), Inches(0.6)
    )
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Arial"

def add_gold_accent(slide, prs):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(1.0),
        prs.slide_width, Inches(0.04)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_GOLD
    shape.line.fill.background()

def add_image(slide, img_path, left, top, width=None, height=None):
    """Add image to slide."""
    if os.path.exists(img_path):
        if width and height:
            slide.shapes.add_picture(img_path, left, top, width, height)
        elif width:
            slide.shapes.add_picture(img_path, left, top, width=width)
        elif height:
            slide.shapes.add_picture(img_path, left, top, height=height)
        else:
            slide.shapes.add_picture(img_path, left, top)
        return True
    return False

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ========== SLIDE 1: Title ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, UW_PURPLE)

    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(2.8),
        prs.slide_width, Inches(0.1)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_GOLD
    shape.line.fill.background()

    add_title_shape(slide,
        "Funding Rate Contrarian Strategy",
        Inches(0.8), Inches(1.5), Inches(11), Inches(1),
        font_size=44, color=WHITE)

    add_title_shape(slide,
        "BTC-USDT Perpetual Futures on Binance",
        Inches(0.8), Inches(3.2), Inches(11), Inches(0.6),
        font_size=24, bold=False, color=UW_METALLIC_GOLD)

    add_title_shape(slide,
        "Adeline Wen\nCFRM 522 — Winter 2026",
        Inches(0.8), Inches(5.5), Inches(5), Inches(1),
        font_size=20, bold=False, color=WHITE)

    # ========== SLIDE 2: Problem & Hypothesis ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Problem & Hypothesis", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Economic Mechanism",
        Inches(0.5), Inches(1.3), Inches(5), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Perpetual futures: funding paid every 8h",
        "0.01% baseline ≈ 13% annualized",
        "Extreme funding (0.05%+) → 65%+ annualized",
        "Crowded longs exit → price decline",
        "Brunnermeier & Pedersen (2009): funding liquidity spiral"
    ], Inches(0.5), Inches(1.8), Inches(5.5), Inches(2.5), font_size=16)

    add_title_shape(slide, "Pre-committed Hypotheses",
        Inches(6.5), Inches(1.3), Inches(6), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "H1: Extreme z-score → 24h reversal (IC > 0.02)",
        "H2: High OI amplifies signal",
        "H3: Optimal threshold is non-linear",
        "H4: OOS Calmar positive (WF ratio > 0.5)"
    ], Inches(6.5), Inches(1.8), Inches(6), Inches(2), font_size=16)

    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(4.5), Inches(12), Inches(1)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = UW_METALLIC_GOLD
    box.line.fill.background()

    add_title_shape(slide,
        "Strategy: Short when z > threshold, Long when z < -threshold",
        Inches(0.8), Inches(4.7), Inches(11), Inches(0.7),
        font_size=20, bold=True, color=UW_PURPLE)

    add_title_shape(slide, "Objective: Calmar Ratio (not Sharpe)",
        Inches(0.5), Inches(5.8), Inches(12), Inches(0.5),
        font_size=18, color=UW_PURPLE)
    add_bullet_text(slide, [
        "BTC returns: excess kurtosis > 20 → Sharpe assumes normality, inappropriate here"
    ], Inches(0.5), Inches(6.3), Inches(12), Inches(0.5), font_size=15)

    # ========== SLIDE 3: Funding Rate Distribution ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Data: Funding Rate Distribution", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_funding_dist.png",
              Inches(0.3), Inches(1.3), width=Inches(12.7))

    add_bullet_text(slide, [
        "Heavy tails (kurtosis > 10) • Slight positive skew (longs dominate) • NOT normally distributed"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 4: ACF & Seasonality ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Data: Autocorrelation & Seasonality", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_funding_acf.png",
              Inches(0.2), Inches(1.2), width=Inches(6.4))
    add_image(slide, "data/fig_funding_seasonal.png",
              Inches(6.7), Inches(1.2), width=Inches(6.4))

    add_bullet_text(slide, [
        "Left: ACF significant at lags 1-3 → short-term persistence, then decay (mean reversion)",
        "Right: No strong weekday effect — funding driven by market sentiment, not calendar"
    ], Inches(0.5), Inches(5.5), Inches(12), Inches(1), font_size=15)

    # ========== SLIDE 5: Price & Events ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Data: BTC Price & Funding Rate (2020-2024)", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_events.png",
              Inches(0.2), Inches(1.15), width=Inches(12.9))

    add_bullet_text(slide, [
        "Major events: March 2020 crash • May 2021 selloff • LUNA collapse (May 2022) • FTX collapse (Nov 2022)"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 6: IC Scatter ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Indicator Testing: Information Coefficient", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_ic_scatter.png",
              Inches(0.2), Inches(1.15), width=Inches(12.9))

    add_bullet_text(slide, [
        "Negative slope: higher z-score → lower forward return • H1 SUPPORTED: IC statistically significant at 24h"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 7: Signal Timeline ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Signal Processing: Timeline (2021-2023)", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_signal_timeline.png",
              Inches(0.2), Inches(1.1), width=Inches(12.9))

    add_bullet_text(slide, [
        "Green: Long signals (z < -1.5) • Red: Short signals (z > 1.5) • Signals cluster around extreme funding events"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 8: Equity Curves ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Trading Rules: Incremental Equity Curves", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_equity_curves.png",
              Inches(0.3), Inches(1.1), width=Inches(12.7))

    add_bullet_text(slide, [
        "Rule 0: Basic • Rule 1: +Max hold • Rule 2: +Stop loss • Rule 3: +OI filter • Gray: BTC buy-and-hold"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 9: Grid Search Heatmap ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Parameter Optimization: Grid Search", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_gridsearch_heatmap.png",
              Inches(0.3), Inches(1.15), width=Inches(12.7))

    add_bullet_text(slide, [
        "Left: Threshold vs Window heatmap • Right: Pardo check — best not extreme outlier • H3 SUPPORTED: peaked, not corner"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 10: Sensitivity ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Parameter Optimization: Sensitivity Analysis", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_sensitivity.png",
              Inches(0.2), Inches(1.15), width=Inches(12.9))

    add_bullet_text(slide, [
        "Flat curve = robust to parameter choice • Sharp peak = potential overfit • Threshold most sensitive parameter"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 11: Walk-Forward ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Walk-Forward Analysis (Out-of-Sample)", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_walkforward.png",
              Inches(0.3), Inches(1.1), width=Inches(12.7))

    add_bullet_text(slide, [
        "Most OOS windows positive • WF ratio ~0.3-0.6 • Parameter drift suggests regime dependence • H4 PARTIALLY SUPPORTED"
    ], Inches(0.5), Inches(6.8), Inches(12), Inches(0.5), font_size=14)

    # ========== SLIDE 12: Bootstrap Sharpe ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Overfitting: Bootstrap Sharpe Distribution", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_bootstrap_sharpe.png",
              Inches(2), Inches(1.2), width=Inches(9))

    add_title_shape(slide, "Deflated Sharpe Ratio (DSR)",
        Inches(0.5), Inches(5.5), Inches(5), Inches(0.4),
        font_size=18, color=UW_PURPLE)
    add_bullet_text(slide, [
        "Accounts for 120+ parameter trials",
        "DSR adjusts for selection bias",
        "Wide CI reflects sample uncertainty"
    ], Inches(0.5), Inches(5.9), Inches(5), Inches(1.2), font_size=15)

    add_title_shape(slide, "Top-N Removal Test",
        Inches(7), Inches(5.5), Inches(5), Inches(0.4),
        font_size=18, color=UW_PURPLE)
    add_bullet_text(slide, [
        "Remove best 20 trades",
        "Still profitable → distributed edge",
        "Not outlier-driven"
    ], Inches(7), Inches(5.9), Inches(5.5), Inches(1.2), font_size=15)

    # ========== SLIDE 13: Extension ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Extension: Cross-Asset & ETH", prs)
    add_gold_accent(slide, prs)

    add_image(slide, "data/fig_cross_asset_corr.png",
              Inches(0.3), Inches(1.15), width=Inches(6))
    add_image(slide, "data/fig_extension_equity.png",
              Inches(6.5), Inches(1.15), width=Inches(6.5))

    add_bullet_text(slide, [
        "Left: BTC-ETH funding correlation ~0.7+ (macro-driven, limited diversification)",
        "Right: ETH positive Calmar with BTC-optimized params (no re-fitting) → genuine microstructure effect"
    ], Inches(0.5), Inches(5.8), Inches(12), Inches(0.8), font_size=15)

    # ========== SLIDE 14: Conclusion ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Conclusion", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Key Findings",
        Inches(0.5), Inches(1.3), Inches(5), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Funding rate contrarian effect is real",
        "Economic basis: crowding + margin pressure",
        "IC statistically significant at 24h",
        "OOS performance positive (40-60% degradation typical)",
        "Cross-asset validation on ETH"
    ], Inches(0.5), Inches(1.8), Inches(5.5), Inches(2.5), font_size=16)

    add_title_shape(slide, "Backtest Results",
        Inches(6.5), Inches(1.3), Inches(5), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Calmar Ratio: ~0.11",
        "Sharpe Ratio: ~0.77",
        "Max Drawdown: ~14%",
        "Win Rate: ~54%",
        "Total Trades: ~125 (2020-2024)"
    ], Inches(6.5), Inches(1.8), Inches(6), Inches(2.5), font_size=16)

    add_title_shape(slide, "Risks & Limitations",
        Inches(0.5), Inches(4.5), Inches(12), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Tail events: LUNA-style collapse where funding stays extreme",
        "Regime dependence: better in high-volatility periods",
        "Market structure change post-FTX may reduce future effectiveness",
        "Crowding risk if strategy becomes widely known"
    ], Inches(0.5), Inches(5), Inches(12), Inches(1.5), font_size=16)

    # ========== SLIDE 15: References ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "References", prs)
    add_gold_accent(slide, prs)

    add_bullet_text(slide, [
        "Bailey, D. H., & Lopez de Prado, M. (2014). The Deflated Sharpe Ratio.",
        "       Journal of Portfolio Management, 40(5), 94-107.",
        "",
        "Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity.",
        "       Review of Financial Studies, 22(6), 2201-2238.",
        "",
        "Pardo, R. (2008). The Evaluation and Optimization of Trading Strategies.",
        "       John Wiley & Sons.",
        "",
        "Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage.",
        "       Journal of Finance, 52(1), 35-55.",
        "",
        "Liu, Y., Tsyvinski, A., & Wu, X. (2022). Common Risk Factors in Cryptocurrency.",
        "       Journal of Finance, 77(2), 1133-1177."
    ], Inches(0.5), Inches(1.5), Inches(12), Inches(5.5), font_size=15)

    # Save
    output_path = "CFRM522_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved: {output_path}")
    print(f"Total slides: {len(prs.slides)}")
    return output_path

if __name__ == "__main__":
    create_presentation()
