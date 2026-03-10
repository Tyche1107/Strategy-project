# CFRM 522 Presentation Speaking Notes
# 双语发言稿 (Bilingual Script)

**Duration: 10-12 minutes | 时长：10-12分钟**

---

## Slide 1: Title (30 seconds)

**English:**
Good morning/afternoon everyone. My name is Adeline Wen, and today I'll be presenting my CFRM 522 strategy project: a Funding Rate Contrarian Strategy on Bitcoin perpetual futures traded on Binance.

**中文:**
大家好，我是Adeline Wen。今天我将展示我的CFRM 522策略项目：一个基于Binance比特币永续合约的资金费率反向策略。

---

## Slide 2: Problem & Hypothesis (1.5 minutes)

**English:**
Let me start with the economic intuition. Perpetual futures on Binance charge a funding rate every 8 hours. At the baseline of 0.01%, this costs longs about 13% annually. But when markets get crowded and funding spikes to 0.05% or higher, that's 65% annualized — unsustainable for leveraged traders.

This creates predictable price pressure. Crowded longs are forced to exit, either to stop paying fees or because their margin gets eroded. This is the funding liquidity spiral described by Brunnermeier and Pedersen.

My strategy is simple: go short when the funding rate z-score exceeds my threshold, and go long when it's deeply negative. I'm fading the crowd.

I pre-committed to four hypotheses before looking at results — this is critical to avoid data mining.

**中文:**
让我从经济直觉开始。Binance的永续合约每8小时收取一次资金费率。基准0.01%意味着多头每年支付约13%。但当市场拥挤、资金费率飙升到0.05%以上时，这就是65%的年化成本——对于杠杆交易者来说无法承受。

这会产生可预测的价格压力。拥挤的多头被迫平仓，要么是为了停止支付费用，要么是因为保证金被侵蚀。这就是Brunnermeier和Pedersen描述的资金流动性螺旋。

我的策略很简单：当资金费率z-score超过阈值时做空，当深度为负时做多。我在反向操作人群。

我在查看结果之前预先提交了四个假设——这对于避免数据挖掘至关重要。

---

## Slide 3: Funding Rate Distribution (45 seconds)

**English:**
This slide shows the funding rate distribution from 2020 to 2024. Notice three things:

First, heavy tails — the kurtosis is over 10, meaning extreme events are much more common than a normal distribution would predict.

Second, positive skew — longs tend to dominate in crypto, so they're usually the ones paying.

Third, this is clearly NOT normal. This is why I chose Calmar ratio over Sharpe — Sharpe assumes normality, which doesn't hold here.

**中文:**
这张幻灯片展示了2020年到2024年的资金费率分布。注意三点：

第一，重尾分布——峰度超过10，意味着极端事件比正态分布预测的更常见。

第二，正偏态——加密市场中多头通常占主导，所以他们通常是付费方。

第三，这明显不是正态分布。这就是为什么我选择Calmar比率而不是Sharpe——Sharpe假设正态性，这里不成立。

---

## Slide 4: ACF & Seasonality (45 seconds)

**English:**
On the left, you can see the autocorrelation function. Funding rates are persistent in the short term — significant at lags 1 through 3. But the ACF decays, which supports our mean reversion hypothesis.

On the right, there's no strong weekday effect. Funding is driven by market sentiment, not calendar effects. This means we don't need to add day-of-week filters.

**中文:**
左边是自相关函数。资金费率在短期内具有持续性——在滞后1到3期显著。但ACF衰减，这支持我们的均值回归假设。

右边没有明显的星期效应。资金费率是由市场情绪驱动的，而不是日历效应。这意味着我们不需要添加星期过滤器。

---

## Slide 5: Price & Events (30 seconds)

**English:**
This shows BTC price and funding rate over the full sample period. You can see the major events marked: March 2020 crash, May 2021 selloff, LUNA collapse in May 2022, and FTX collapse in November 2022. Each of these events produced extreme funding rate readings.

**中文:**
这显示了整个样本期间的BTC价格和资金费率。你可以看到标记的主要事件：2020年3月崩盘、2021年5月抛售、2022年5月LUNA崩盘，以及2022年11月FTX崩盘。每个事件都产生了极端的资金费率读数。

---

## Slide 6: IC Scatter (45 seconds)

**English:**
This is the key slide for indicator validation. I computed the Information Coefficient — Spearman correlation between the z-score and forward returns at 8, 24, and 48 hours.

The negative slope confirms our contrarian hypothesis: higher z-scores predict lower forward returns. At the 24-hour horizon, the IC is statistically significant with p less than 0.05.

This supports Hypothesis 1 — extreme funding z-scores DO predict mean reversion.

**中文:**
这是指标验证的关键幻灯片。我计算了信息系数——z-score与8、24、48小时前向收益之间的Spearman相关性。

负斜率证实了我们的反向假设：更高的z-score预测更低的前向收益。在24小时视野下，IC在p<0.05时统计显著。

这支持假设1——极端资金费率z-score确实能预测均值回归。

---

## Slide 7: Signal Timeline (30 seconds)

**English:**
Here you can see how the signals fire over time. Green lines are long signals when z-score is below negative 1.5, red lines are short signals when z-score exceeds positive 1.5. The signals cluster around extreme funding events, which is exactly what we want.

**中文:**
这里你可以看到信号如何随时间触发。绿线是z-score低于-1.5时的多头信号，红线是z-score超过+1.5时的空头信号。信号聚集在极端资金费率事件周围，这正是我们想要的。

---

## Slide 8: Equity Curves (45 seconds)

**English:**
I tested trading rules incrementally, following Pardo's methodology. Rule 0 is the basic signal with an 8-hour hold. Rule 1 adds a 48-hour maximum hold. Rule 2 adds a 0.5% stop loss. Rule 3 adds an OI filter.

The gray dashed line is BTC buy-and-hold — much higher total return, but also 70%+ maximum drawdown. The strategy trades off some return for significantly better risk-adjusted performance.

**中文:**
我按照Pardo的方法增量测试了交易规则。规则0是基本信号，持有8小时。规则1添加48小时最大持有期。规则2添加0.5%止损。规则3添加OI过滤器。

灰色虚线是BTC买入持有——总回报高得多，但最大回撤也超过70%。策略以牺牲一些回报换取显著更好的风险调整表现。

---

## Slide 9: Grid Search (45 seconds)

**English:**
I ran a grid search over 120 parameter combinations: threshold, window length, and hold hours.

The left heatmap shows mean Calmar across threshold and window combinations. You can see it's not a corner solution — the best performance is in the middle ranges, supporting Hypothesis 3.

The right histogram is the Pardo check. The best Calmar is about 2 standard deviations above the mean — high, but not an extreme outlier that would suggest overfitting.

**中文:**
我对120个参数组合进行了网格搜索：阈值、窗口长度和持有小时数。

左边的热力图显示阈值和窗口组合的平均Calmar。你可以看到这不是角解——最佳表现在中间范围，支持假设3。

右边的直方图是Pardo检验。最佳Calmar大约高于均值2个标准差——很高，但不是表明过拟合的极端异常值。

---

## Slide 10: Sensitivity (30 seconds)

**English:**
These sensitivity plots show how robust the strategy is to each parameter. A flat curve means the strategy is robust to that choice. A sharp peak suggests potential overfitting. Threshold is the most sensitive parameter, which makes sense — it directly controls when we trade.

**中文:**
这些敏感性图显示策略对每个参数的稳健性。平坦的曲线意味着策略对该选择稳健。尖峰表明潜在的过拟合。阈值是最敏感的参数，这是合理的——它直接控制我们何时交易。

---

## Slide 11: Walk-Forward (1 minute)

**English:**
Walk-forward analysis is critical for testing out-of-sample performance. I used a rolling 365-day training window with 90-day test periods.

The good news: most OOS windows show positive Calmar. The WF ratio — mean OOS Calmar divided by mean IS Calmar — is between 0.3 and 0.6.

Is that good? For a systematic strategy, 40-60% degradation from in-sample to out-of-sample is actually typical. What would be alarming is consistent negative OOS performance, which we don't see here.

I do observe parameter drift across windows, which suggests the strategy is regime-dependent — it works better in high-volatility periods.

**中文:**
前向分析对于测试样本外表现至关重要。我使用了滚动365天训练窗口和90天测试期。

好消息是：大多数OOS窗口显示正Calmar。WF比率——平均OOS Calmar除以平均IS Calmar——在0.3到0.6之间。

这好吗？对于系统化策略，从样本内到样本外40-60%的衰减实际上是典型的。令人担忧的是持续的负OOS表现，我们这里没有看到。

我确实观察到跨窗口的参数漂移，这表明策略是依赖市场状态的——它在高波动期表现更好。

---

## Slide 12: Overfitting Diagnostics (1 minute)

**English:**
I ran three overfitting diagnostics.

First, the Deflated Sharpe Ratio from Bailey and Lopez de Prado. This adjusts for the fact that I tested 120 parameter combinations. Some selection bias is present.

Second, the bootstrap Sharpe distribution shows a wide confidence interval — which honestly reflects uncertainty about future performance.

Third, the top-N removal test. After removing the best 20 trades, the strategy is still profitable. This means the edge is distributed across many trades, not concentrated in a few lucky outliers.

**中文:**
我进行了三项过拟合诊断。

首先，Bailey和Lopez de Prado的膨胀Sharpe比率。这调整了我测试120个参数组合的事实。存在一些选择偏差。

第二，bootstrap Sharpe分布显示宽置信区间——这诚实地反映了对未来表现的不确定性。

第三，Top-N移除测试。移除最佳20笔交易后，策略仍然盈利。这意味着优势分布在许多交易中，而不是集中在少数幸运的异常值上。

---

## Slide 13: Extension (45 seconds)

**English:**
For the extension, I applied the BTC-optimized parameters to ETH — with NO refitting.

ETH shows positive Calmar using the exact same parameters. This is strong evidence that the funding rate contrarian effect is a genuine market microstructure phenomenon, not just BTC-specific noise.

The left chart shows BTC-ETH funding correlation is above 0.7 — they're driven by macro sentiment, so there's limited diversification benefit from combining them.

**中文:**
作为扩展，我将BTC优化的参数应用于ETH——没有重新拟合。

ETH使用完全相同的参数显示正Calmar。这是强有力的证据，表明资金费率反向效应是真正的市场微观结构现象，而不仅仅是BTC特定的噪音。

左图显示BTC-ETH资金费率相关性高于0.7——它们受宏观情绪驱动，所以组合它们的分散化收益有限。

---

## Slide 14: Conclusion (1 minute)

**English:**
Let me summarize.

The funding rate contrarian effect is real. It has a solid economic basis in crowding and margin pressure. The IC is statistically significant, and cross-asset validation on ETH confirms this isn't data mining.

Backtest results: Calmar around 0.11, Sharpe around 0.77, max drawdown about 14%, win rate 54%, with 125 trades over 4 years.

For hypotheses: H1 and H3 are supported. H2 is mixed — OI helps in some periods but not consistently. H4 is partially supported — OOS is positive but degraded from IS.

The main risks are tail events where funding stays extreme for extended periods, like the LUNA collapse. The strategy is also regime-dependent, and if it becomes widely known, the edge may disappear.

Thank you. I'm happy to take questions.

**中文:**
让我总结一下。

资金费率反向效应是真实的。它在拥挤和保证金压力方面有坚实的经济基础。IC统计显著，ETH的跨资产验证证实这不是数据挖掘。

回测结果：Calmar约0.11，Sharpe约0.77，最大回撤约14%，胜率54%，4年125笔交易。

假设方面：H1和H3得到支持。H2结果混合——OI在某些时期有帮助但不一致。H4部分支持——OOS为正但低于IS。

主要风险是资金费率长期保持极端的尾部事件，如LUNA崩盘。策略也依赖市场状态，如果它被广泛知晓，优势可能会消失。

谢谢。我很乐意回答问题。

---

## Slide 15: References

**English:**
These are my main references. I'm happy to discuss any of them in detail.

**中文:**
这些是我的主要参考文献。我很乐意详细讨论其中任何一篇。

---

# Q&A Preparation / 问答准备

**Q: Why Calmar instead of Sharpe?**
A: BTC returns have excess kurtosis over 20, violating normality. Calmar penalizes the worst drawdown directly, which matters more for leveraged trading.

**Q: 为什么选Calmar而不是Sharpe?**
A: BTC收益的超额峰度超过20，违反正态性。Calmar直接惩罚最大回撤，这对杠杆交易更重要。

**Q: What's your biggest concern about this strategy?**
A: Tail risk. In events like LUNA, funding can stay extreme for days while price keeps moving against you. The stop loss helps but doesn't fully protect against gap risk.

**Q: 你对这个策略最大的担忧是什么?**
A: 尾部风险。在像LUNA这样的事件中，资金费率可能连续几天保持极端，而价格继续朝不利方向移动。止损有帮助但不能完全防止跳空风险。

**Q: Would you actually trade this?**
A: With modifications, yes. I'd use smaller position sizing (Kelly fraction), add a volatility filter, and probably only trade during high-funding-volatility regimes.

**Q: 你会真正交易这个策略吗?**
A: 经过修改，会的。我会使用更小的仓位规模（Kelly分数），添加波动率过滤器，并可能只在高资金费率波动期交易。
