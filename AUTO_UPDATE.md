# 🤖 自动每日刷新设置(可选)

让网站**每天自动更新一次**,不需要你手动上传数据。

---

## 🎯 实现原理

GitHub 提供一个免费功能叫 **GitHub Actions** 🅴 — 可以在**指定时间自动跑脚本**。

我已经写好了这个工作流文件:`.github/workflows/daily_refresh.yml`

它会做这些事:
```
每天 16:30 北京时间 (= 08:30 UTC) 自动跑:
  ↓
拉取你的仓库代码
  ↓
运行 scripts/update_dashboard.py
  ↓
如果 data/data.json 有变化
  ↓
自动 commit + push
  ↓
GitHub Pages 自动重新部署
  ↓
你的网站就是最新数据了 ✅
```

---

## ✅ 启用步骤(2 分钟)

### 第 1 步:上传整个项目(包 .github 文件夹)

由于 GitHub 网页不显示隐藏文件夹,你需要用稍微不同的方式上传 `.github` 文件夹:

#### 方式 A · 浏览器(浏览器可读出 .github 目录但默认隐藏)🅴

1. 仓库页面 → **`⬆ Add file` 🅴** → **`Upload files` 🅴**
2. **把整个解压后的 `dashboard-deploy/` 文件夹直接拖进去**(包括 `.github` 文件夹)
3. 浏览器会保留所有文件包括隐藏的 `.github/`
4. 底部 → **Commit changes** 🅴

#### 方式 B · GitHub 网页(分开传 .github)

1. **手动创建文件夹**:
   - 仓库页面 → **Create new file** 🅴
   - 路径输入框输入:`.github/workflows/daily_refresh.yml`
   - 把 `daily_refresh.yml` 文件内容粘贴进去
   - 点 **Commit new file** 🅴
2. 回到仓库页面验证一下,看 `daily_refresh.yml` 是否出现在根目录下

### 第 2 步:启用 GitHub Actions 🅴

1. 仓库顶部 → 点击 **Actions** 🅴 标签
2. 如果看到提示:`I understand my workflows, go ahead and enable them` 🅴 — 点击它
3. 你会看到 **`Daily Refresh`** 🅴 这个 workflow,绿色勾表示启用

### 第 3 步(可选):测试一次

1. 进 **Actions** 🅴 标签
2. 点 **Daily Refresh** 🅴
3. 右侧 **Run workflow** 🅴 → **Run workflow** 🅴(绿色按钮)
4. 等 30 秒 - 2 分钟,刷新页面看是否有绿色 ✅
5. 跑完后去仓库看 **Code** 🅴 标签,会看到一个新的 commit 信息:
   ```
   Auto-refresh 2026-07-05 08:30 UTC
   ```

### 第 4 步:完事 ✅

之后每天收盘后(北京时间 16:30),它会自动跑、自动更新。你需要做的:
- **啥都不用做** 🤖

---

## 📅 跑的时间

按 cron 表达式 `30 8 * * 1-5` 配置:
- ⏰ 每天 **08:30 UTC**(格林威治时间)
- ⏰ 等于北京时间 **16:30**(UTC+8)
- 📅 周一到周五(`1-5`),周末不跑(A 股不开市)

如果想改成收盘后**半小时**(17:00 北京时间):
- 把 `cron: "30 8 * * 1-5"` 改成 `cron: "0 9 * * 1-5"`

如果想周末也跑(节假日没用,但保险):
- 改成 `cron: "30 8 * * *`(去掉 `1-5`)

修改 `.github/workflows/daily_refresh.yml` 后 commit 即可生效。

---

## ❓ 故障排查

### Q1:Actions 标签页找不到
**A**: 看仓库代码里有没有 `.github/workflows/daily_refresh.yml` 这个文件路径。如果路径不对(比如变成了 `.github-workflows-daily.yml` 这种带横线的),GitHub 不会识别为 workflow。

### Q2:workflow 跑成功了,但 data.json 没更新
**A**: 检查权限设置:
1. 仓库 → **Settings** 🅴 → **Actions** 🅴 → **General** 🅴
2. 滚动到 **Workflow permissions** 🅴
3. 选 **`Read and write permissions` 🅴**
4. 勾上 **`Allow GitHub Actions to create and approve pull requests` 🅴**

### Q3:跑失败,看红色 ❌
**A**: 进 Actions → Daily Refresh → 失败的 run → 看日志
- 最常见的失败原因:
  - Python 找不到 `update_dashboard.py` → 检查脚本路径
  - akshare 安装失败 → 网络问题,可改为只用 requests
  - 权限不够 → 参考 Q2 设置

### Q4:可以随时手动跑吗?
**A**: 可以!Actions 标签 → Daily Refresh → 右侧 **`Run workflow` 🅴** 按钮。

---

## 🎁 进阶:每日 AI 自动写复盘

如果以后想让 AI 根据当日数据**自动生成复盘文本**加到 judgment.json,告诉子安,我可以扩展 workflow,集成 AI 自动生成内容。

那才是终极形态:
```
每天 16:30 触发:
  ↓
GitHub Actions 自动跑 update_dashboard.py
  ↓
拉取最新数据(指数 / 板块 / 涨停 / 北向)
  ↓
调用 AI 模型写一段复盘
  ↓
更新 judgment.json(自动)
  ↓
你打开网站 → 直接看到今天的市场判断 ✅
```

---

_最后更新:2026-07-04_
