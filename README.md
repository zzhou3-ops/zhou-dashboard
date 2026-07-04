# 周总投资思路 · 情绪 + 抱团率看板

一个自动更新的本地网站,展示市场情绪周期 / 资金抱团率 / 长周期估值。

---

## 🚀 30 秒上手

1. **打开仪表盘**(两种方式任选):
   - **方式 A - 双击打开**:直接双击 `dashboard.html`,浏览器即可看(无需任何服务器)
   - **方式 B - 本地服务**(支持自动定时刷新):
     ```powershell
     cd C:\Users\zhouz\.openclaw\workspace\dashboard
     py -m http.server 8080
     # 浏览器打开 http://localhost:8080/dashboard.html
     ```

2. **每日刷新一次**(收盘后跑):
   ```powershell
   cd C:\Users\zhouz\.openclaw\workspace\dashboard
   py update_dashboard.py
   ```
   这条命令会把现有 CSV 数据整合成最新的 `data/data.json`,然后浏览器下次刷新就自动显示新数据。

---

## 📅 设置每日自动刷新(可选,强烈推荐)

### Windows 任务计划程序

1. 打开 **任务计划程序**(`Win + R` → `taskschd.msc`)
2. 右键 → **创建任务**:
   - **常规** Tab:
     - 名称: `dashboard_daily_refresh`
     - 勾选"不管用户是否登录都要运行"
   - **触发器** Tab → 新建:
     - 每天,起始时间 **16:30**(收盘后)
   - **操作** Tab → 新建:
     - 程序: `py`
     - 参数: `C:\Users\zhouz\.openclaw\workspace\dashboard\update_dashboard.py`
     - 起始于: `C:\Users\zhouz\.openclaw\workspace\dashboard`
   - **设置** Tab:
     - 勾选"如果任务失败,按以下频率重新启动"(每 30 分钟)
   - 确定

3. 测试一下:右键 → 运行,看看是否生成新 `data.json`

---

## 🛠️ 修改情绪判定(子安帮周总手工调整)

当市场情绪发生变化时,用 CLI 命令更新 dashboard 顶部的判定面板:

```powershell
cd C:\Users\zhouz\.openclaw\workspace\dashboard

# 设置情绪周期为"高潮期"
py update_dashboard.py set --phase "高潮期" --pos 70

# 添加信号
py update_dashboard.py set --signal "上证突破 4100" --signal "北向资金大幅净流入"

# 设置操作建议
py update_dashboard.py set --advice "可加仓至 50-60%,优先券商+机器人龙头"

# 清空所有信号
py update_dashboard.py set --signal __clear__
```

修改后**立即生效**(浏览器下次刷新即见新值)。

---

## 🌐 部署到公网(可选,需要的话子安可以帮)

### 方案 1:GitHub Pages(免费,适合长期访问)

1. 在 GitHub 新建一个仓库(比如 `zhou-dashboard`),设为 **Public**
2. 把 `dashboard/` 文件夹里的所有文件 push 到 main 分支根目录
3. 进入仓库 Settings → Pages → Source 选 `main` 分支根目录
4. 等 1-2 分钟,访问 `https://<你的用户名>.github.io/zhou-dashboard/dashboard.html` 即可

### 方案 2:Vercel / Netlify(更快)

一行命令行即可部署,免费,大陆访问可能慢些。

---

## 📁 文件结构

```
dashboard/
├── dashboard.html         # 主页面,单文件
├── data/
│   ├── data.json          # 当前显示用数据(脚本生成)
│   └── judgment.json      # 手工设置的情绪判定(可选)
├── update_dashboard.py    # 数据刷新脚本
├── build_initial_data.py  # 初次构建数据(一次性)
├── README.md              # 本文件
└── (以下是子安维护用的脚本,需要时给数据源)
    └── sentiment_*.csv    # 源 CSV(在 ../ 父目录)
```

---

## ❓ 常见问题

**Q: 浏览器打开 dashboard.html 后,数据还是旧的?**
A: 浏览器有缓存。建议每次跑完 `update_dashboard.py` 后,按 `Ctrl+F5` 强刷。

**Q: 我想加新指标(比如北向资金)怎么办?**
A: 让子安改 `update_dashboard.py` 增加 series 字段,以及 `dashboard.html` 加新的 chart 容器。

**Q: 任务计划程序没自动跑?**
A: 检查:
1. "起始于" 路径是否正确填入
2. 系统中是否禁用计划任务(`Win + R` → `gpedit.msc` 看组策略)
3. 看任务计划程序历史记录

**Q: 想要手机也能看?**
A: 部署到 GitHub Pages 后手机直接访问那个 URL 即可。

---

## 🎯 当前面板

| 面板 | 含义 | 数据源 |
|---|---|---|
| 顶部 Chicks | 当前情绪周期 / 仓位建议 / 下次更新 | judgment.json |
| 情绪周期 (QUAD) | VIX / PCR / 两融 / CNN F&G | sentiment_chart.py |
| 资金抱团率 (2016-) | TOP 50 成交占比 / 总成交额 | 抱团率采集脚本 |
| 长周期三大指数 | 创业板 / 沪深 300 / 上证指数 | 长周期 CSV |
| 估值 + 资金面 | PE TTM / 两融余额(万亿) / 20日波动率 | 长周期 CSV |
| 关键信号面板 | 当前 6 条核心信号 + 操作建议 | judgment.json + 子安手工维护 |

---

最后更新: 2026-07-04
主理人: 子安 (周总数字幕僚 🌙)
