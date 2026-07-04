"""
update_dashboard.py
每日收盘后自动刷新 dashboard/data.json 的脚本

执行流程:
1. 尝试拉取最新数据(akshare / 公开源)
2. 与现有 CSV 历史数据合并
3. 写入 data.json

失败策略:
- 任意数据源拉取失败,继续用已有 CSV,不中断
- 整体失败,data.json 保持旧值(用 try/except 整体包)

依赖:
- pip install akshare (主用)
- pip install requests (备选)

执行方式:
- 手动: py update_dashboard.py
- 计划任务: 每日 16:30 自动跑(详见 README.md)
"""

import sys
import json
import time
import csv
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(r"C:\Users\zhouz\.openclaw\workspace")
DASH = WORKSPACE / "dashboard"
DATA_OUT = DASH / "data" / "data.json"


# ============================================================
# 综合情绪指标计算
# ============================================================
def normalize_vix(v):
    """VIX 标准化到 0-100 (原始 0-50 → 0-100)"""
    if v is None: return None
    return max(0, min(100, round(v * 2, 1)))

def normalize_pcr(p):
    """PCR 标准化到 0-100 (原始 0-2 → 0-100)"""
    if p is None: return None
    return max(0, min(100, round(p * 50, 1)))

def normalize_margin(b):
    """两融余额 标准化到 0-100 (历史范围 7000-30000 亿)"""
    if b is None: return None
    return max(0, min(100, round((b - 7000) / 23000 * 100, 1)))

def normalize_cnn(c):
    """CNN 恐惧贪婪已经是 0-100,直接返回"""
    if c is None: return None
    return max(0, min(100, round(c, 1)))

def compute_composite_sentiment(dates, vix_data, pcr_data, margin_data, cnn_data):
    """
    综合情绪指标 = VIX×25% + PCR×25% + 两融×25% + CNN×25%
    所有指标先标准化到 0-100,再加权平均

    区域解释:
    - 0-20 极度冰点 (资产荒,可能机会)
    - 20-40 恐慌 (情绪谨慎)
    - 40-60 中性 (正常状态)
    - 60-80 贪婪 (情绪浓厚)
    - 80-100 极度贪婪 (泡沫化,警惕)
    """
    n = len(dates)
    composite  = []
    components = {
        "vix_norm":    [],
        "pcr_norm":    [],
        "margin_norm": [],
        "cnn_norm":    [],
    }

    for i in range(n):
        v = vix_data[i]    if i < len(vix_data)    else None
        p = pcr_data[i]    if i < len(pcr_data)    else None
        m = margin_data[i] if i < len(margin_data) else None
        c = cnn_data[i]    if i < len(cnn_data)    else None

        v_n = normalize_vix(v)
        p_n = normalize_pcr(p)
        m_n = normalize_margin(m)
        c_n = normalize_cnn(c)

        components["vix_norm"].append(v_n)
        components["pcr_norm"].append(p_n)
        components["margin_norm"].append(m_n)
        components["cnn_norm"].append(c_n)

        # 加权平均 (都要有数据才算)
        if None in (v_n, p_n, m_n, c_n):
            composite.append(None)
        else:
            avg = (v_n + p_n + m_n + c_n) / 4
            composite.append(round(avg, 1))

    return composite, components


# ============================================================
# CSV 读取
# ============================================================
def read_csv(path):
    out = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = [c.strip().lstrip("\ufeff") for c in (reader.fieldnames or [])]
        for c in cols: out[c] = []
        for row in reader:
            for k in row:
                k_clean = k.strip().lstrip("\ufeff")
                v = row[k]
                if v is None or v == "":
                    out[k_clean].append(None)
                else:
                    try: out[k_clean].append(float(v))
                    except (ValueError, TypeError): out[k_clean].append(v.strip() if isinstance(v, str) else v)
    return out


# ============================================================
# 选源数据拉取(全部 optional,失败用 CSV)
# ============================================================
def fetch_vix_pcr_fallback():
    """拉 VIX + CNN F&G (失败返回 None)"""
    try:
        import requests
        # CNN 恐惧贪婪
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                         timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok:
            d = r.json()
            cur = d.get("fear_and_greed", {})
            score = cur.get("score")
            rating = cur.get("rating", "")
            rating_map = {0:"extreme fear", 1:"fear", 2:"neutral", 3:"greed", 4:"extreme greed"}
            return {
                "fetched_at": datetime.now().isoformat()[:16],
                "cnn_fg": score,
                "cnn_rating": rating_map.get(cur.get("rating", ""), str(cur.get("rating", ""))),
            }
    except Exception as e:
        print(f"  [WARN] CNN F&G fail: {e}", file=sys.stderr)
    return None


def fetch_vix_fallback():
    """拉 VIX (CBOE 公开 CSV)"""
    try:
        import requests
        # 兜底: Yahoo Finance VIX 历史 API
        # 这里用 CBOE 的直接 CSV
        end = int(time.time())
        start = end - 90*86400  # 90 天
        url = f"https://query1.finance.yahoo.com/v7/finance/download/%5EVIX?period1={start}&period2={end}&interval=1d&events=history"
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok and r.text.startswith("Date"):
            lines = r.text.splitlines()
            last = lines[-1].split(",")
            return {"fetched_at": datetime.now().isoformat()[:16], "vix": float(last[4])}
    except Exception as e:
        print(f"  [WARN] VIX fail: {e}", file=sys.stderr)
    return None


# ============================================================
# 主逻辑
# ============================================================
def build_data():
    out = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "schema_version": 1,
    }

    # ---------- 1. 情绪四指标 (主用现有 CSV) ----------
    sentiment_csv = read_csv(WORKSPACE / "sentiment_4panel_data.csv")
    if sentiment_csv:
        # 截取最近 1500 行
        n = min(1500, max(len(v) for v in sentiment_csv.values()))
        if n > 0:
            keys = list(sentiment_csv.keys())
            for k in keys: sentiment_csv[k] = sentiment_csv[k][-n:]

        # 原始 4 个指标
        vix_data    = sentiment_csv.get("VIX", [])
        pcr_data    = sentiment_csv.get("PCR", [])
        cnn_data    = sentiment_csv.get("CNN_FG", [])
        margin_data = sentiment_csv.get("两融余额_亿", [])
        dates       = sentiment_csv.get("date", [])

        # 综合情绪指标
        composite, components = compute_composite_sentiment(
            dates, vix_data, pcr_data, margin_data, cnn_data
        )

        out["sentiment"] = {
            "dates":      dates,
            "composite":  composite,                                    # 主线:合成值 0-100
            "components": components,                                    # 4 个标准化后的成分(各占 25%)
            "raw": {                                                   # 原始数据(给 tooltip)
                "VIX":      vix_data,
                "PCR":      pcr_data,
                "两融余额": margin_data,
                "CNN_FG":   cnn_data,
            },
            "rating":     sentiment_csv.get("CNN评级", []),
            "weight":     {"VIX": 25, "PCR": 25, "两融余额": 25, "CNN_FG": 25},  # 权重说明
            "zones": [                                                 # 区域定义
                {"min": 0,   "max": 20,  "label": "极度冰点", "color": "#374151"},
                {"min": 20,  "max": 40,  "label": "恐慌",     "color": "#ef4444"},
                {"min": 40,  "max": 60,  "label": "中性",     "color": "#22c55e"},
                {"min": 60,  "max": 80,  "label": "贪婪",     "color": "#f59e0b"},
                {"min": 80,  "max": 100, "label": "极度贪婪", "color": "#ef4444"},
            ],
        }
        print(f"  sentiment rows: {n}, composite last: {composite[-1] if composite else 'N/A'}")

    # ---------- 2. 抱团率 ----------
    baotuan_csv = read_csv(WORKSPACE / "周总投资思路之成交额抱团_2016-2026_v3.csv")
    if baotuan_csv:
        n = max(len(v) for v in baotuan_csv.values())
        out["baotuan"] = {
            "dates": baotuan_csv.get("date", []),
            "series": [
                {"name": "抱团率(%)",          "data": baotuan_csv.get("ratio_pct", [])},
                {"name": "5日均线(%)",         "data": baotuan_csv.get("ratio_pct_5d_ma", [])},
                {"name": "全市场总成交额(亿)",  "data": baotuan_csv.get("total_amount_yi", [])},
                {"name": "参与股票数",          "data": baotuan_csv.get("n_stock", [])},
            ],
        }
        print(f"  baotuan rows: {n}")

    # ---------- 3. 长周期 ----------
    longterm_csv = read_csv(WORKSPACE / "data" / "sentiment_longterm_v3.csv")
    if longterm_csv:
        n = min(1500, max(len(v) for v in longterm_csv.values()))
        keys = list(longterm_csv.keys())
        for k in keys: longterm_csv[k] = longterm_csv[k][-n:]

        cyb  = longterm_csv.get("收盘", [])
        margin = longterm_csv.get("两融_余额", [])
        # 两融余额 / 1e12 转 万亿
        margin_yi = [round(v/1e12, 2) if v is not None else None for v in margin]

        out["longterm"] = {
            "dates": longterm_csv.get("日期", []),
            "series": [
                {"name": "创业板指",       "data": cyb},
                {"name": "沪深300",        "data": longterm_csv.get("沪深300", [])},
                {"name": "上证指数",       "data": longterm_csv.get("上证指数", [])},
                {"name": "PE TTM",         "data": longterm_csv.get("上证PE_滚动", [])},
                {"name": "两融余额(万亿)",  "data": margin_yi},
                {"name": "20日波动率(%)",   "data": longterm_csv.get("20日波动率", [])},
            ],
            "phase": longterm_csv.get("情绪阶段", []),
        }
        print(f"  longterm rows: {n}")

    # ---------- 4. 尝试拉取最新 VIX + CNN(给页面显示,但不参与 series) ----------
    meta = {"vix_latest": None, "cnn_fg_latest": None}
    v = fetch_vix_fallback()
    if v: meta["vix_latest"] = v["vix"]
    c = fetch_vix_pcr_fallback()
    if c: meta["cnn_fg_latest"] = c.get("cnn_fg")
    out["_latest_meta"] = meta

    # ---------- 5. judgment 当下情绪周期判定 ----------
    # 简单规则(可在 update 时人工修正)
    # 默认读取上次的 judgment,这样不会因为没跑 judgment 而丢失手改的状态
    last_judgment = load_last_judgment()
    out["judgment"] = last_judgment or default_judgment()

    return out


def load_last_judgment():
    """读上次脚本保存的 judgment.json"""
    p = DASH / "data" / "judgment.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return None


def default_judgment():
    return {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
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
        "next_check": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
    }


def save_judgment(j):
    """保存人工 judgment"""
    p = DASH / "data" / "judgment.json"
    p.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  judgment saved: {p}")


# ============================================================
# CLI: 手动修改 judgment
# ============================================================
def cmd_set_judgment(args):
    """py update_dashboard.py set --phase "高潮期" --pos 70 --signal "..." """
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--phase",   default=None)
    p.add_argument("--pos",     type=int, default=None)
    p.add_argument("--signal",  action="append", default=[])
    p.add_argument("--advice",  default=None)
    p.add_argument("--next",    default=None)
    a = p.parse_args(args)
    j = load_last_judgment() or default_judgment()
    if a.phase:  j["cycle_phase"] = a.phase
    if a.pos is not None: j["position_pct"] = a.pos
    if a.signal:
        # 替换或追加
        if a.signal == ["__clear__"]:
            j["key_signals"] = []
        else:
            existing = j.get("key_signals", [])
            j["key_signals"] = existing + [s for s in a.signal if s not in existing]
    if a.advice: j["advice"] = a.advice
    if a.next:   j["next_check"] = a.next
    j["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_judgment(j)
    print(f"updated: phase={j['cycle_phase']}, pos={j['position_pct']}%, signals={len(j['key_signals'])}")


# ============================================================
# 主入口
# ============================================================
def main(argv):
    if len(argv) > 1 and argv[1] == "set":
        cmd_set_judgment(argv[2:])
        return 0

    print(f"[{datetime.now():%Y-%m-%d %H:%M}] update_dashboard 开始")
    try:
        data = build_data()

        # 如果 judgment.json 不存在,写入默认 (首次运行)
        judgment_path = DASH / "data" / "judgment.json"
        if not judgment_path.exists():
            save_judgment(data["judgment"])

        DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
        DATA_OUT.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8"
        )
        size = DATA_OUT.stat().st_size
        print(f"[OK] {DATA_OUT}  ({size:,} bytes)")
        return 0
    except Exception as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
