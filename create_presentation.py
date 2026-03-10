"""
Generate UW-style presentation for CFRM 522 Strategy Project
Optimized layout with all figures
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
UW_LIGHT_GOLD = RGBColor(0xE8, 0xE3, 0xD3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY = RGBColor(0x2D, 0x2D, 0x2D)
LIGHT_GRAY = RGBColor(0x66, 0x66, 0x66)

def set_background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def add_text(slide, text, left, top, width, height, size=18, bold=False, color=DARK_GRAY, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = "Arial"
    p.alignment = align
    return box

def add_bullets(slide, items, left, top, width, height, size=16, color=DARK_GRAY, spacing=8):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = "Arial"
        p.space_before = Pt(spacing)
        p.space_after = Pt(spacing)
    return box

def add_header(slide, title, prs):
    # Purple header bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.9))
    bar.fill.solid()
    bar.fill.fore_color.rgb = UW_PURPLE
    bar.line.fill.background()

    # Gold accent
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.9), prs.slide_width, Inches(0.035))
    accent.fill.solid()
    accent.fill.fore_color.rgb = UW_GOLD
    accent.line.fill.background()

    # Title text
    add_text(slide, title, Inches(0.5), Inches(0.22), Inches(12), Inches(0.55), size=28, bold=True, color=WHITE)

def add_image(slide, path, left, top, width=None, height=None):
    if os.path.exists(path):
        if width:
            slide.shapes.add_picture(path, left, top, width=width)
        elif height:
            slide.shapes.add_picture(path, left, top, height=height)
        else:
            slide.shapes.add_picture(path, left, top)

def add_caption(slide, text, top=Inches(6.9)):
    add_text(slide, text, Inches(0.5), top, Inches(12.3), Inches(0.4), size=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

def add_section_title(slide, text, left, top):
    add_text(slide, text, left, top, Inches(5), Inches(0.4), size=18, bold=True, color=UW_PURPLE)

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 1: Title
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, UW_PURPLE)

    # Gold line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.0), Inches(11.7), Inches(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = UW_GOLD
    line.line.fill.background()

    add_text(slide, "Funding Rate Contrarian Strategy", Inches(0.8), Inches(1.8), Inches(11), Inches(1), size=48, bold=True, color=WHITE)
    add_text(slide, "BTC-USDT Perpetual Futures | Binance", Inches(0.8), Inches(3.4), Inches(11), Inches(0.6), size=24, color=UW_LIGHT_GOLD)
    add_text(slide, "Adeline Wen", Inches(0.8), Inches(5.5), Inches(5), Inches(0.5), size=22, color=WHITE)
    add_text(slide, "CFRM 522 · Winter 2026", Inches(0.8), Inches(6.0), Inches(5), Inches(0.5), size=18, color=UW_LIGHT_GOLD)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 2: Problem & Hypothesis
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Problem & Hypothesis", prs)

    # Left column
    add_section_title(slide, "Economic Mechanism", Inches(0.5), Inches(1.2))
    add_bullets(slide, [
        "Perpetual futures: funding paid every 8 hours",
        "Baseline 0.01% ≈ 13% annualized cost",
        "Extreme 0.05%+ → 65%+ annualized",
        "Crowded longs forced to exit → price drops",
        "Brunnermeier & Pedersen (2009): liquidity spiral"
    ], Inches(0.5), Inches(1.65), Inches(5.8), Inches(2.8), size=15)

    # Right column
    add_section_title(slide, "Pre-committed Hypotheses", Inches(6.8), Inches(1.2))
    add_bullets(slide, [
        "H1: |z-score| > 1.5 predicts 24h reversal",
        "H2: High OI change amplifies signal",
        "H3: Threshold-Calmar is non-monotonic",
        "H4: WF ratio > 0.5 (OOS positive)"
    ], Inches(6.8), Inches(1.65), Inches(6), Inches(2.2), size=15)

    # Strategy box
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(4.6), Inches(12.3), Inches(0.9))
    box.fill.solid()
    box.fill.fore_color.rgb = UW_LIGHT_GOLD
    box.line.fill.background()
    add_text(slide, "Strategy: Short when z > threshold  |  Long when z < -threshold",
             Inches(0.8), Inches(4.8), Inches(11.5), Inches(0.5), size=20, bold=True, color=UW_PURPLE, align=PP_ALIGN.CENTER)

    # Objective note
    add_section_title(slide, "Objective: Calmar Ratio", Inches(0.5), Inches(5.8))
    add_text(slide, "BTC has excess kurtosis > 20 — Sharpe assumes normality, Calmar penalizes max drawdown directly",
             Inches(0.5), Inches(6.2), Inches(12), Inches(0.5), size=14, color=LIGHT_GRAY)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 3: Funding Distribution
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Data: Funding Rate Distribution", prs)
    add_image(slide, "data/fig_funding_dist.png", Inches(0.4), Inches(1.15), width=Inches(12.5))
    add_caption(slide, "Heavy tails (kurtosis > 10)  •  Positive skew (longs dominate)  •  Non-normal → justifies Calmar over Sharpe")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 4: ACF & Seasonality
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Data: Autocorrelation & Seasonality", prs)
    add_image(slide, "data/fig_funding_acf.png", Inches(0.3), Inches(1.1), width=Inches(6.3))
    add_image(slide, "data/fig_funding_seasonal.png", Inches(6.7), Inches(1.1), width=Inches(6.3))
    add_caption(slide, "ACF decays after lag 3 → supports mean reversion  •  No weekday effect → sentiment-driven, not calendar", Inches(5.6))

    # ══════════════════════════════════════════════════════════════
    # SLIDE 5: Price & Events
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Data: BTC Price & Funding Rate (2020-2024)", prs)
    add_image(slide, "data/fig_events.png", Inches(0.3), Inches(1.05), width=Inches(12.7))
    add_caption(slide, "Key events: March 2020 crash  •  May 2021 selloff  •  LUNA (May 2022)  •  FTX (Nov 2022)")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 6: IC Scatter
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Indicator Testing: Information Coefficient (IC)", prs)
    add_image(slide, "data/fig_ic_scatter.png", Inches(0.3), Inches(1.05), width=Inches(12.7))
    add_caption(slide, "Negative slope confirms contrarian hypothesis  •  H1 SUPPORTED: IC significant at 24h horizon (p < 0.05)")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 7: Signal Timeline
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Signal Processing: Timeline (2021-2023)", prs)
    add_image(slide, "data/fig_signal_timeline.png", Inches(0.3), Inches(1.0), width=Inches(12.7))
    add_caption(slide, "Green = Long (z < -1.5)  •  Red = Short (z > 1.5)  •  Signals cluster around extreme funding events")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 8: Equity Curves
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Trading Rules: Incremental Equity Curves", prs)
    add_image(slide, "data/fig_equity_curves.png", Inches(0.4), Inches(1.0), width=Inches(12.5))
    add_caption(slide, "Rule 0: Basic  →  Rule 1: +Max hold  →  Rule 2: +Stop loss  →  Rule 3: +OI filter  •  Gray: BTC buy-and-hold")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 9: Grid Search
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Parameter Optimization: Grid Search (120 combinations)", prs)
    add_image(slide, "data/fig_gridsearch_heatmap.png", Inches(0.4), Inches(1.05), width=Inches(12.5))
    add_caption(slide, "Left: Threshold × Window heatmap  •  Right: Pardo check (best not extreme outlier)  •  H3 SUPPORTED")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 10: Sensitivity
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Parameter Optimization: Sensitivity Analysis", prs)
    add_image(slide, "data/fig_sensitivity.png", Inches(0.3), Inches(1.05), width=Inches(12.7))
    add_caption(slide, "Flat = robust to choice  •  Sharp peak = overfit risk  •  Threshold is most sensitive parameter")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 11: Walk-Forward
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Walk-Forward Analysis (Out-of-Sample)", prs)
    add_image(slide, "data/fig_walkforward.png", Inches(0.4), Inches(1.0), width=Inches(12.5))
    add_caption(slide, "Most OOS windows positive  •  WF ratio 0.3-0.6  •  Parameter drift → regime dependence  •  H4 PARTIALLY SUPPORTED")

    # ══════════════════════════════════════════════════════════════
    # SLIDE 12: Bootstrap & Overfitting
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Overfitting Diagnostics", prs)
    add_image(slide, "data/fig_bootstrap_sharpe.png", Inches(0.4), Inches(1.1), width=Inches(7.5))

    # Right side text
    add_section_title(slide, "Deflated Sharpe Ratio", Inches(8.2), Inches(1.2))
    add_bullets(slide, [
        "Accounts for 120+ trials",
        "Adjusts for selection bias",
        "Wide CI reflects uncertainty"
    ], Inches(8.2), Inches(1.65), Inches(4.5), Inches(1.8), size=15)

    add_section_title(slide, "Top-N Removal Test", Inches(8.2), Inches(3.6))
    add_bullets(slide, [
        "Remove best 20 trades",
        "Still profitable",
        "Edge is distributed, not outlier-driven"
    ], Inches(8.2), Inches(4.05), Inches(4.5), Inches(1.8), size=15)

    add_section_title(slide, "PBO Cross-Test", Inches(8.2), Inches(5.8))
    add_text(slide, "Half-sample optimization shows moderate parameter stability across time",
             Inches(8.2), Inches(6.2), Inches(4.5), Inches(0.6), size=14, color=LIGHT_GRAY)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 13: Extension
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Extension: Cross-Asset Validation", prs)
    add_image(slide, "data/fig_cross_asset_corr.png", Inches(0.3), Inches(1.1), width=Inches(5.8))
    add_image(slide, "data/fig_extension_equity.png", Inches(6.3), Inches(1.1), width=Inches(6.7))

    add_text(slide, "BTC-ETH correlation ~0.7+ (macro-driven)", Inches(0.5), Inches(5.5), Inches(5.5), Inches(0.4), size=14, color=LIGHT_GRAY)
    add_text(slide, "ETH positive Calmar with BTC params (no re-fit) → genuine effect", Inches(6.5), Inches(5.5), Inches(6.3), Inches(0.4), size=14, color=LIGHT_GRAY)

    # Key insight
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.7))
    box.fill.solid()
    box.fill.fore_color.rgb = UW_LIGHT_GOLD
    box.line.fill.background()
    add_text(slide, "Cross-asset validation confirms: funding rate contrarian is a market microstructure effect, not BTC-specific noise",
             Inches(0.7), Inches(6.35), Inches(12), Inches(0.5), size=15, bold=True, color=UW_PURPLE, align=PP_ALIGN.CENTER)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 14: Conclusion
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "Conclusion", prs)

    # Three columns
    add_section_title(slide, "Key Findings", Inches(0.5), Inches(1.2))
    add_bullets(slide, [
        "Funding contrarian effect is real",
        "Economic basis: crowding + margin",
        "IC significant at 24h",
        "OOS positive (40-60% degradation)",
        "Cross-asset validated"
    ], Inches(0.5), Inches(1.65), Inches(4), Inches(2.8), size=14)

    add_section_title(slide, "Backtest Results", Inches(4.8), Inches(1.2))
    add_bullets(slide, [
        "Calmar: ~0.11",
        "Sharpe: ~0.77",
        "Max DD: ~14%",
        "Win Rate: ~54%",
        "Trades: ~125"
    ], Inches(4.8), Inches(1.65), Inches(3.5), Inches(2.8), size=14)

    add_section_title(slide, "Hypothesis Results", Inches(8.8), Inches(1.2))
    add_bullets(slide, [
        "H1: ✓ Supported",
        "H2: ~ Mixed",
        "H3: ✓ Supported",
        "H4: ~ Partial"
    ], Inches(8.8), Inches(1.65), Inches(4), Inches(2.2), size=14)

    # Risks
    add_section_title(slide, "Risks & Limitations", Inches(0.5), Inches(4.6))
    add_bullets(slide, [
        "Tail events: LUNA-style collapse where funding stays extreme for extended periods",
        "Regime dependence: strategy performs better in high-volatility periods",
        "Market structure shift: post-FTX changes may reduce future effectiveness",
        "Crowding risk: if strategy becomes widely known, edge may disappear"
    ], Inches(0.5), Inches(5.05), Inches(12), Inches(1.8), size=14)

    # ══════════════════════════════════════════════════════════════
    # SLIDE 15: References
    # ══════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, WHITE)
    add_header(slide, "References", prs)

    refs = [
        "Bailey, D. H., & Lopez de Prado, M. (2014). The Deflated Sharpe Ratio.",
        "    Journal of Portfolio Management, 40(5), 94-107.",
        "",
        "Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity.",
        "    Review of Financial Studies, 22(6), 2201-2238.",
        "",
        "Liu, Y., Tsyvinski, A., & Wu, X. (2022). Common Risk Factors in Cryptocurrency.",
        "    Journal of Finance, 77(2), 1133-1177.",
        "",
        "Pardo, R. (2008). The Evaluation and Optimization of Trading Strategies. Wiley.",
        "",
        "Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage.",
        "    Journal of Finance, 52(1), 35-55."
    ]

    box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(12), Inches(5.5))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(refs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.font.name = "Arial"

    # Save
    prs.save("CFRM522_Presentation.pptx")
    print(f"Saved: CFRM522_Presentation.pptx ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_presentation()
