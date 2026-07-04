"""
build_initial_data.py
将现有历史 CSV 数据整合成 dashboard/data.json
"""

import json
import csv
from pathlib import Path

WORKSPACE = Path(r"C:\Users\zhouz\.openclaw\workspace")
DATA = WORKSPACE / "dashboard" / "data"
DATA.mkdir(parents=True, exist_ok=True)


def read_csv_as_dict(path):
    """读 CSV 返回 {column: [values]} 字典,自动处理空值"""
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            for k, v in row.items():
                if k is None:
                    continue
                # 去掉 BOM 等不可见字符
                k_clean = k.strip().lstrip("\ufeff").strip()
                if v is None or v == "":
                    row[k_clean] = None
                else:
                    try:
                        row[k_clean] = float(v)
                    except (ValueError, TypeError):
                        row[k_clean] = v.strip() if isinstance(v, str) else v
                if k != k_clean and k in row:
                    row.pop(k, None)
            rows.append(row)
    if not rows:
        return {}
    cols = list(rows[0].keys())
    out = {c: [] for c in cols}
    for r in rows:
        for c in cols:
            out[c].append(r.get(c))
    return out


def to_easymode(data_dict, x_col=None):
    """转 ECharts 系列: {x:[], series:[{name, data}]}"""
    if not data_dict:
        return {"dates": [], "series": []}

    cols = list(data_dict.keys())
    if x_col is None:
        x_col = cols[0]
    x = data_dict[x_col]
    series = []
    for c in cols:
        if c == x_col:
            continue
        # 跳过空字符串列
        if all(v is None for v in data_dict[c]):
            continue
        series.append({
            "name": c,
            "type": "line",
            "data": data_dict[c],
            "smooth": False,
            "symbol": "none",
        })
    return {
        "dates": x,
        "series": series,
    }


def main():
    out = {
        "update_time": "2026-07-04 22:00",
        "schema_version": 1,
    }

    # ========== 1. 情绪四指标 ==========
    sentiment = read_csv_as_dict(WORKSPACE / "sentiment_4panel_data.csv")
    if sentiment:
        dates = sentiment.get("date", [])
        # 截取最近 N 天
        for k in sentiment:
            sentiment[k] = sentiment[k][-1500:]  # 全部

        out["sentiment"] = {
            "dates": sentiment.get("date", []),
            "series": [
                {"name": "VIX",  "data": sentiment.get("VIX", [])},
                {"name": "PCR",  "data": sentiment.get("PCR", [])},
                {"name": "CNN恐惧贪婪", "data": sentiment.get("CNN_FG", [])},
                {"name": "两融余额(亿)", "data": sentiment.get("两融余额_亿", [])},
            ],
            "rating": sentiment.get("CNN评级", []),
        }

    # ========== 2. 抱团率 ==========
    baotuan = read_csv_as_dict(WORKSPACE / "周总投资思路之成交额抱团_2016-2026_v3.csv")
    if baotuan:
        out["baotuan"] = {
            "dates": baotuan.get("date", []),
            "series": [
                {"name": "抱团率(%)",            "data": baotuan.get("ratio_pct", [])},
                {"name": "5日均线(%)",            "data": baotuan.get("ratio_pct_5d_ma", [])},
                {"name": "全市场总成交额(亿)",   "data": baotuan.get("total_amount_yi", [])},
                {"name": "参与股票数",            "data": baotuan.get("n_stock", [])},
            ],
        }

    # ========== 3. 长周期(创业板+资金面+估值面)==========
    longterm = read_csv_as_dict(WORKSPACE / "data" / "sentiment_longterm_v3.csv")
    if longterm:
        # 截取最新 1500 行
        for k in longterm:
            longterm[k] = longterm[k][-1500:]

        cyb = longterm.get("收盘", [])  # 创业板指收盘
        hs300 = longterm.get("沪深300", [])
        sh = longterm.get("上证指数", [])

        out["longterm"] = {
            "dates": longterm.get("日期", []),
            "series": [
                {"name": "创业板指",     "data": cyb},
                {"name": "沪深300",      "data": hs300},
                {"name": "上证指数",     "data": sh},
                {"name": "PE TTM",       "data": longterm.get("上证PE_滚动", [])},
                {"name": "两融余额(万亿)", "data": [_normalize(v, 1e12) for v in longterm.get("两融_余额", [])]},
                {"name": "20日波动率(%)", "data": longterm.get("20日波动率", [])},
            ],
            "phase": longterm.get("情绪阶段", []),
        }

    # ========== 4. 当下情绪周期判定 (硬编码) ==========
    # 基于 2026-07-03 数据手算
    out["judgment"] = {
        "update_time": "2026-07-04 22:00",
        "cycle_phase": "冰点后修复期",
        "cycle_phase_short": "修复期",
        "position_pct": 30,
        "key_signals": [
            "上周五大冰点(创业板-5.71% / 科创50-7.70%)",
            "7-3 微涨修复(上证+0.37% / 创业板+0.07%)",
            "机器人主线领涨(双环+9.99% 涨停/埃斯顿+10%)",
            "海外创新药全线上扬(+1.8%~+3.4%)",
            "AI算力链海外负面,7-6 谨慎",
            "北向 -40 亿持续净流出,场外观望",
        ],
        "advice": "可建 25-30% 仓位,主线机器人+商业航天+券商+创新药龙头",
        "next_check": "2026-07-06",
    }

    # 写到文件
    out_path = DATA / "data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    size = out_path.stat().st_size
    print(f"WROTE: {out_path}")
    print(f"Size:  {size:,} bytes ({size/1024:.1f} KB)")
    print(f"Sentiment rows:  {len(out.get('sentiment', {}).get('dates', []))}")
    print(f"Baotuan rows:    {len(out.get('baotuan', {}).get('dates', []))}")
    print(f"Longterm rows:   {len(out.get('longterm', {}).get('dates', []))}")


def _normalize(v, divisor):
    """原始单位 → 显示单位"""
    if v is None:
        return None
    try:
        return round(float(v) / divisor, 2)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    main()
