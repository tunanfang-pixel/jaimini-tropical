# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Jaimini Tropical Astrology Engine — 纯 Jaimini 回归黄道占星计算引擎，基于 Iranganti Rangacharya 的《Jaimini Sutramritam》和《Muhurtha Sindhu》(Jyotish-Prasana)。

**GitHub**: https://github.com/tunanfang-pixel/jaimini-tropical

## 核心设计原则

1. **回归黄道（Tropical）** — 不设 Ayanamsa
2. **整宫制（Whole Sign）** — Rasi = Bhava
3. **纯 Jaimini** — 零 Parashara 污染：无 Vimshottari、无 Shadbala、无行星相位、无不等宫制
4. **数据表格式** — 高精度数值表格，不画星盘
5. **7 星 Karaka 系统** — Rangacharya 体系，不含 Rahu

## 架构

```
jaimini/
├── engine/    → 天文层：ephemeris(Skyfield JPL DE421), houses, time_utils
├── core/      → Jaimini 层：karakas, dashas, padas, lagnas, divisions, argala
├── chart/     → 整合层：chart.py (Chart 对象)
├── cli/       → 命令行入口：main.py
├── tests/     → 测试：test_engine, test_jaimini
└── docs/      → THEORY.md (数据哲学文档)
```

## 运行 / 测试

```bash
# 计算星盘
python run_jaimini.py "1949-10-01" "15:00:00" "+8" "39.907" "116.397" --name "Chart"

# 运行测试
C:/Users/20442/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest jaimini/tests/ -v
```

## Python 环境

- 路径: `C:\Users\20442\AppData\Local\Python\pythoncore-3.14-64\python.exe`（非 Windows Store 版）
- Shell: bash (Git Bash) 或 PowerShell
- 系统编码: GBK（Windows 中文版），注意 Unicode 兼容

## 技术栈

- Python 3.14，不依赖第三方库（除 Skyfield + JPL DE421 星历）
- 星历文件: `de421.bsp` (约 16MB)
