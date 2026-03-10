"""
Generate UW-style presentation for CFRM 522 Strategy Project
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# UW Colors
UW_PURPLE = RGBColor(0x4B, 0x2E, 0x83)  # #4B2E83
UW_GOLD = RGBColor(0xB7, 0xA5, 0x7A)    # #B7A57A
UW_METALLIC_GOLD = RGBColor(0xE8, 0xE3, 0xD3)  # light gold for backgrounds
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)

def set_slide_background(slide, color):
    """Set solid background color for slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_title_shape(slide, text, left, top, width, height, font_size=32, bold=True, color=WHITE):
    """Add a text box with title styling."""
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
    """Add bulleted text."""
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
        p.space_before = Pt(6)
        p.space_after = Pt(6)
    return shape

def add_header_bar(slide, text, prs):
    """Add purple header bar at top of slide."""
    # Purple bar
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, Inches(1.2)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_PURPLE
    shape.line.fill.background()

    # Title text
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(9), Inches(0.8)
    )
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Arial"

def add_gold_accent(slide, prs):
    """Add gold accent line."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(1.2),
        prs.slide_width, Inches(0.05)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_GOLD
    shape.line.fill.background()

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ========== SLIDE 1: Title ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_background(slide, UW_PURPLE)

    # Gold accent bar
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(2.8),
        prs.slide_width, Inches(0.1)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = UW_GOLD
    shape.line.fill.background()

    # Main title
    add_title_shape(slide,
        "Funding Rate Contrarian Strategy",
        Inches(0.8), Inches(1.5), Inches(11), Inches(1),
        font_size=44, color=WHITE)

    # Subtitle
    add_title_shape(slide,
        "BTC-USDT Perpetual Futures on Binance",
        Inches(0.8), Inches(3.2), Inches(11), Inches(0.6),
        font_size=24, bold=False, color=UW_METALLIC_GOLD)

    # Author info
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
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Perpetual futures: funding paid every 8 hours",
        "0.01% baseline ≈ 13% annualized cost to longs",
        "Extreme funding (0.05%+) → 65%+ annualized",
        "Crowded longs exit → price decline"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(2.5), font_size=18)

    add_title_shape(slide, "Hypotheses",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "H1: Extreme z-score predicts 24h reversal",
        "H2: High OI amplifies signal",
        "H3: Optimal threshold is non-linear",
        "H4: OOS Calmar positive (WF ratio > 0.5)"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(2.5), font_size=18)

    # Key insight box
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(5), Inches(12), Inches(1.2)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = UW_METALLIC_GOLD
    box.line.fill.background()

    add_title_shape(slide,
        "Strategy: Fade extreme funding — short when z > threshold, long when z < -threshold",
        Inches(0.8), Inches(5.3), Inches(11), Inches(0.8),
        font_size=20, bold=True, color=UW_PURPLE)

    # ========== SLIDE 3: Data & Methodology ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Data & Methodology", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Data Source",
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "BTC-USDT perpetual (Binance)",
        "Funding rates: every 8h, 2020-2024",
        "OHLCV: hourly price data",
        "~5,500 funding observations"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(2), font_size=18)

    add_title_shape(slide, "Constraints",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Leverage: 1x (no liquidation risk)",
        "Fee: 0.04% taker each side",
        "Max hold: 48 hours",
        "Objective: Calmar ratio (not Sharpe)"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(2), font_size=18)

    add_title_shape(slide, "Why Calmar over Sharpe?",
        Inches(0.5), Inches(4.5), Inches(12), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "BTC returns: excess kurtosis > 20, heavy tails violate normality assumption",
        "Calmar = Ann. Return / Max Drawdown — directly penalizes worst-case loss",
        "More relevant for leveraged crypto where one bad period can wipe account"
    ], Inches(0.5), Inches(5.1), Inches(12), Inches(1.5), font_size=17)

    # ========== SLIDE 4: Indicator Results ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Indicator Testing (Section 4)", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Information Coefficient (IC) Results",
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    # IC table as text
    add_bullet_text(slide, [
        "Funding Z-Score (90d window):",
        "   • 8h horizon:  IC = -0.02",
        "   • 24h horizon: IC = -0.03 (p < 0.05) ✓",
        "   • 48h horizon: IC = -0.025",
        "",
        "Negative IC confirms contrarian hypothesis:",
        "Higher z-score → lower forward return"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(3), font_size=17)

    add_title_shape(slide, "H1 & H2 Test Results",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "H1: IC > 0.02 at 24h ✓ SUPPORTED",
        "   Statistically significant (p < 0.05)",
        "",
        "H2: OI amplification",
        "   IC(high OI) > IC(low OI)",
        "   Result varies by period"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(2.5), font_size=17)

    # Add image placeholder note
    add_title_shape(slide,
        "[See notebook: fig_ic_scatter.png — Z-Score vs Forward Return scatter plots]",
        Inches(0.5), Inches(5.8), Inches(12), Inches(0.5),
        font_size=14, bold=False, color=DARK_GRAY)

    # ========== SLIDE 5: Trading Rules & Backtest ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Trading Rules (Section 6)", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Incremental Rule Testing",
        Inches(0.5), Inches(1.5), Inches(12), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    # Rules table
    add_bullet_text(slide, [
        "Rule 0: Basic signal, 8h hold          → Baseline Calmar",
        "Rule 1: + Max 48h hold cap             → Slight improvement",
        "Rule 2: + 0.5% stop loss               → Reduced drawdown",
        "Rule 3: + OI/volume filter             → Fewer trades, better quality"
    ], Inches(0.5), Inches(2.1), Inches(7), Inches(2), font_size=17)

    add_title_shape(slide, "Backtest Results (Full Period)",
        Inches(0.5), Inches(4.2), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Calmar Ratio: ~0.11",
        "Sharpe Ratio: ~0.77",
        "Max Drawdown: ~14%",
        "Win Rate: ~54%",
        "Total Trades: ~125"
    ], Inches(0.5), Inches(4.8), Inches(5), Inches(2), font_size=17)

    add_title_shape(slide, "vs Benchmark",
        Inches(6.5), Inches(4.2), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "BTC Buy-and-Hold:",
        "   Much higher return in bull markets",
        "   But 70%+ max drawdown",
        "",
        "Strategy: Lower return, better risk-adjusted"
    ], Inches(6.5), Inches(4.8), Inches(6), Inches(2), font_size=17)

    # ========== SLIDE 6: Parameter Optimization ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Parameter Optimization (Section 7)", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Grid Search (120 combinations)",
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Parameters tested:",
        "   • Threshold: [1.0, 1.2, 1.5, 1.8, 2.0]",
        "   • Window: [60, 90, 120] periods",
        "   • Hold hours: [4, 8, 16, 24, 48]",
        "   • Stop loss: [None, 0.5%]"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(2.5), font_size=17)

    add_title_shape(slide, "Optimal Parameters",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Best Calmar configuration:",
        "   • Threshold: ~1.5-2.0",
        "   • Window: ~60-90 periods (20-30 days)",
        "   • Hold: 8-16 hours",
        "",
        "H3: Non-monotonic threshold ✓"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(2.5), font_size=17)

    add_title_shape(slide, "Pardo Check",
        Inches(0.5), Inches(5), Inches(12), Inches(0.5),
        font_size=20, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Best Calmar ~2 std above mean → Not extreme outlier, reduces overfit concern"
    ], Inches(0.5), Inches(5.5), Inches(12), Inches(0.8), font_size=17)

    # ========== SLIDE 7: Walk-Forward & Overfitting ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Walk-Forward & Overfitting (Sections 8-9)", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Walk-Forward Analysis",
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Rolling WF: 365-day train, 90-day test",
        "Anchored WF: Expanding window",
        "",
        "Results:",
        "   • WF Ratio: ~0.3-0.6",
        "   • Most OOS windows positive",
        "   • H4: Partially supported"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(2.8), font_size=17)

    add_title_shape(slide, "Overfitting Diagnostics",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Deflated Sharpe Ratio (DSR):",
        "   Accounts for 120+ trials",
        "   DSR indicates some selection bias",
        "",
        "Bootstrap Sharpe CI:",
        "   Wide interval reflects uncertainty",
        "",
        "Top-N Removal: Still positive after removing best 20 trades"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(3), font_size=16)

    # Honest assessment box
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(5.3), Inches(12), Inches(1)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = UW_METALLIC_GOLD
    box.line.fill.background()

    add_title_shape(slide,
        "40-60% OOS degradation from IS is typical. Signal appears real but magnitude uncertain.",
        Inches(0.8), Inches(5.5), Inches(11), Inches(0.7),
        font_size=18, bold=False, color=UW_PURPLE)

    # ========== SLIDE 8: Conclusion ==========
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, WHITE)
    add_header_bar(slide, "Conclusion & Extension", prs)
    add_gold_accent(slide, prs)

    add_title_shape(slide, "Key Findings",
        Inches(0.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Funding rate contrarian effect is real",
        "Economic mechanism: crowding + margin pressure",
        "OOS performance positive but degraded",
        "Regime-dependent (better in volatile periods)"
    ], Inches(0.5), Inches(2.1), Inches(5.5), Inches(2.5), font_size=17)

    add_title_shape(slide, "Extension (Section 10)",
        Inches(6.5), Inches(1.5), Inches(5), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "ETH cross-asset: Positive Calmar without re-fit",
        "BTC-ETH funding correlation: ~0.7+",
        "Calmar vs Sortino: Similar optimal params",
        "Bear markets: Strategy performs better"
    ], Inches(6.5), Inches(2.1), Inches(6), Inches(2.5), font_size=17)

    add_title_shape(slide, "Risks & Limitations",
        Inches(0.5), Inches(4.8), Inches(12), Inches(0.5),
        font_size=22, color=UW_PURPLE)

    add_bullet_text(slide, [
        "Tail events (LUNA-style collapse) — funding stays extreme for extended periods",
        "Market structure changes post-FTX may reduce future effectiveness",
        "Crowding risk if strategy becomes widely known"
    ], Inches(0.5), Inches(5.4), Inches(12), Inches(1.2), font_size=17)

    # ========== SLIDE 9: References ==========
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
    ], Inches(0.5), Inches(1.8), Inches(12), Inches(5), font_size=15)

    # Save
    output_path = "CFRM522_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
