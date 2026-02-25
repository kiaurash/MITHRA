# GSBsys (Genetic System Builder) - Complete Analysis

## Overview

GSBsys is a **production-deployed, commercially-validated pure-GA trading system** for futures and stock markets. This documentation provides a complete technical analysis based on the official website (trademaid.info/gsbhelp) and application screenshots.

**Key Characteristics:**
- Pure genetic algorithm (no RL component)
- 37 built-in technical indicators
- Multiplicative signal combination architecture
- 20 million combinations tested per development cycle
- Multi-year commercial deployment across multiple markets
- Pricing: $200-$799 (NDA required)

## Documentation Structure

### Core Technical Documents
- **[GA-Architecture.md](GA-Architecture.md)** - Complete genetic algorithm components, parameters, and operators
- **[Indicator-System.md](Indicator-System.md)** - 37 indicators, signal combination, and entry/exit logic
- **[Methodology.md](Methodology.md)** - 5-part development process and validation framework
- **[Technical-Specifications.md](Technical-Specifications.md)** - All parameters, thresholds, and configuration settings

### Analysis Documents
- **[Comparison-to-Research.md](Comparison-to-Research.md)** - How GSBsys compares to GA+RL academic research
- **[Key-Insights.md](Key-Insights.md)** - Novel findings and practitioner innovations

### Reproduction Guides
- **[Reproduction-Guide.md](Reproduction-Guide.md)** - What can/cannot be reproduced from available documentation
- **[Website-Documentation-Index.md](Website-Documentation-Index.md)** - Complete catalog of all accessible website pages and their content

### Supporting Materials
- **[Indicators/](Indicators/)** - Screenshots of the GSBsys application showing indicator rankings and GA settings

## Quick Facts

| Parameter | Value |
|-----------|-------|
| Population Size | 200 |
| Generations | 1,000 |
| Restarts | 10 (new random seed each) |
| Total Combinations | 20 million |
| Crossover Rate | 95% |
| Mutation Rate | 5% |
| Mutation Strength | 25% |
| Train/Test Split | 40% / 60% (conservative) |
| Primary Fitness | Net Profit × Average Trade |
| Min Pearson (train/test) | 0.95 |
| Min Profit Factor | 1.2 (train/test), 1.8 (validation) |

## Target Markets

- E-mini S&P 500 (ES)
- NASDAQ E-mini (NQ)
- Dow E-mini (YM)
- Natural Gas (NG)
- DAX
- Gold (GC)
- Crude Oil (CL)

## Platform Integration

Systems export to:
- TradeStation (EasyLanguage)
- MultiCharts
- NinjaTrader

## Commercial Validation

Unlike academic GA+RL systems (which typically have <6 months live validation), GSBsys has:
- Multi-year commercial sales history
- NDA-protected deployment (suggesting actual live use)
- Pricing model indicating sustained practitioner confidence
- Regular version updates (v1.0.68.92 as of May 2025)

## Comparison to Academic Research

GSBsys provides the **practitioner baseline** that the GA+RL academic research (documented in `Bootcamp25\ai_agent_framework\research\Research-Results\FinanceRL-Q126\GA+RL-Result3-FINAL.md`) lacks:

- **MaxAI** (best academic system): 4 months live, Profit Factor 1.07
- **GSBsys**: Multi-year deployment, requires PF ≥ 1.8 for validation

See [Comparison-to-Research.md](Comparison-to-Research.md) for detailed analysis.

## Source Materials

**Website:** https://trademaid.info/gsbhelp/

**Key Pages Analyzed:**
- GeneticAlgorithm.html
- Optimization.html
- GAGenerationsGAPopulation.html
- Methodology.html
- GSBArchitecture1.html
- BuildingNasdaqSP500orDowsystems.html
- Provingthemethodology.html

**Screenshots:** See [Indicators/](Indicators/) folder

## Analysis Date

February 19, 2026
