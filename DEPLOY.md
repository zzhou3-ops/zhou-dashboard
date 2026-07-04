# 🌐 GitHub Pages 部署指南 — 周总投资思路看板

5 分钟把 `dashboard.html` 部署到公网,任何设备(电脑/手机/平板)浏览器直接访问。

> 📖 **使用贴士**:GitHub 网页是英文界面,本指南在中英文对照用 🅴 标记英文关键词,方便定位。

---

## 📦 你需要准备的东西

1. **GitHub 账号**(免费注册 https://github.com,2 分钟)
   - 没账号的话点 **Sign up** 🅴 → 邮箱 + 用户名 + 密码
2. **浏览器**就行(Edge / Chrome / Safari 都可以)
3. 不需要装 Git、不需要懂命令行

> ⚠️ 整个 `dashboard-deploy/` 目录就是你需要上传的全部内容(已包含数据 + 脚本)

---

## 🚀 方案 A — 浏览器直接上传(最简单,推荐)

### 🅴 Step 1 — Create a new repository(2 分钟)

1. 浏览器打开 https://github.com/new
2. **填仓库信息**(页面从顶到底):
   - **Owner** 🅴 → 选你的 GitHub 账号
   - **Repository name** 🅴 → 输入 `zhou-dashboard`
     - ⚠️ 必须小写 + 用 `-` 不能用空格,比如:`zhou-dashboard`
   - **Description** 🅴(可选) → `周总投资思路 · 情绪 + 抱团率看板`
   - **Public / Private** 🅴 → 选 **Public** ✅(GitHub Pages 免费版要求 Public)
3. 勾上 ✅ **Add a README file** 🅴
4. 点击绿色按钮 **Create repository** 🅴

✅ 仓库创建成功,你会被带到仓库页面(类似 `https://github.com/<你的用户名>/zhou-dashboard`)。

---

### 🅴 Step 2 — Upload files(3 分钟)

1. 在仓库页面,点击 **⬆ Add file** 🅴 → **Upload files** 🅴
   - (或者直接访问 `https://github.com/<你的用户名>/zhou-dashboard/upload/main`)
2. **拖拽整个 `dashboard-deploy/` 文件夹**到上传框
   - ⚠️ 浏览器接受文件夹拖拽;如果不行,展开文件夹把里面的所有文件全部选中拖上去
3. 等文件列表显示出来,确认包含:
   - `dashboard.html`
   - `data/data.json`
   - `data/judgment.json`
   - `README.md`
   - `DEPLOY.md`(本文件)
   - `scripts/build_initial_data.py`
   - `scripts/update_dashboard.py`
   - `data/.gitkeep`
4. 页面底部 **Commit changes** 🅴 框,填提交说明比如:
   ```
   初始部署:周总投资思路 · 情绪 + 抱团率看板
   ```
5. 点击绿色按钮 **Commit changes** 🅴

GitHub 会花 1-2 秒上传,完成后跳回仓库文件列表页面。

---

### 🅴 Step 3 — Enable GitHub Pages(1 分钟)

1. 仓库页面顶部 → 点击 **⚙ Settings** 🅴(齿轮图标)
2. 左侧菜单 → 找 **Pages** 🅴 并点击
3. 页面滚动到 **GitHub Pages** 🅴 区域:
   - **Source** 🅴: 选 **Deploy from a branch** 🅴
   - **Branch** 🅴: 选 **`main`** 🅴,目录选 **`/ (root)`** 🅴
4. 等待 1-2 分钟,刷新该 Settings → Pages 页面
5. 顶部会出现一条绿色横幅:
   > ✅ **Your site is live at** 🅴 `https://<你的用户名>.github.io/zhou-dashboard/`

> ⚠️ 横幅的 URL 是 `https://<你的用户名>.github.io/zhou-dashboard/`(根目录),  
> 但你要访问的页面是 `https://<你的用户名>.github.io/zhou-dashboard/dashboard.html`(具体文件)

---

### 🅴 Step 4 — Visit your dashboard ✅

浏览器打开:

```
https://<你的用户名>.github.io/zhou-dashboard/dashboard.html
```

看到的就是上面截图里的深色 NAVY 主题看板!

> 💡 **Add to bookmarks** 🅴:把上面那个 URL 加到浏览器收藏夹。下次直接点收藏就能看。

---

## 🪛 后续:每日刷新数据

GitHub Pages 的数据是**静态的**,上传后数据不会自动更新。

### 🅴 Daily data refresh

**每天收盘后想看到最新数据?** 用脚本刷新 + 提交:

#### 方式 1 - 在本地更新后重新上传(简单)

1. 打开 PowerShell:
   ```powershell
   cd C:\Users\zhouz\.openclaw\workspace\dashboard\data
   py ..\scripts\update_dashboard.py
   py ..\scripts\update_dashboard.py set --phase "高潮期" --pos 70  # 可选,手工改判定
   ```

2. 浏览器打开 GitHub 仓库 → 进 `data/` 目录
3. 点击 `data.json` → 点 ✏️ **Edit this file** 🅴
4. 把本地新的 `data.json` 内容粘贴进去
5. 底部点 **Commit changes** 🅴

#### 方式 2 - 装 Git 用命令(更省事,需 GitHub Desktop 或 git for Windows)

如果你想体验更顺滑的更新流程,可以告诉我,子安可以再写一份自动 push 的脚本。

---

## ❓ 常见问题(Troubleshooting)🅴

### Q1:网站打开是 404 Not Found
**A**: 等待 1-2 分钟,GitHub Pages 部署是异步的。也可以在 **Settings → Pages** 🅴 里看 **build status** 🅴。

### Q2:`data/` 目录点进去看不到 `data.json`
**A**: 上传时必须确保 `data/data.json` 这个相对路径。GitHub 上是按目录树显示的。
如果只有 `data.json` 没有 `data/` 目录,说明上传时把文件夹结构丢了。需要重新上传并保留文件夹层级。

### Q3:页面打开后是空白(只看到标题,没有图表)
**A**:
- 大概率是浏览器缓存。**Ctrl + F5** 🅴 强刷一下 (Mac: **Cmd + Shift + R** 🅴)
- 如果还不行,打开浏览器开发者工具(**F12** 🅴) → **Console** 🅴 标签 → 看红色错误
- 最常见错误:`Failed to fetch data/data.json` — 说明 `data.json` 路径错了

### Q4:上传时文件夹拖不上去
**A**: Chrome/Edge 大部分支持,如果不支持:
1. 打开 `dashboard-deploy/data/` 文件夹,把 `data.json` 和 `judgment.json` 两个文件一起拖上去
2. 然后单独打开 `dashboard-deploy/scripts/` 文件夹,把脚本拖上去
3. 最后单独把 `dashboard.html` 和 `README.md` 拖上去

### Q5:仓库设为 Private 后找不到 Pages
**A**: 免费版 GitHub Pages 必须 **Public** 🅴 仓库。Private 仓库的 Pages 是付费功能。

### Q6:第一次访问 GitHub 需要登录吗?
**A**: 不需要登录就可以访问 Public 仓库的 GitHub Pages 网站。但上传文件时必须登录。

---

## 🎁 进阶(可选,以后想要时找我做)

- **自定义域名** 🅴 Custom domain:`zhou.dashboard.com` 这种,可以绑定到自己域名
- **HTTPS** 🅴:GitHub Pages 默认 HTTPS,无需配置
- **手机访问** 🅴 Mobile:GitHub Pages 自动适配移动端
- **每日自动更新** 🅴 Auto-refresh:装 **GitHub Actions** 🅴,每天 16:30 自动跑脚本 + 提交

---

## 📖 中英对照速查表 🅴

| 中文 | English 🅴 | 说明 |
|---|---|---|
| 仓库 | Repository / Repo | GitHub 上的项目文件夹 |
| 创建仓库 | Create repository / New repo | 新建项目按钮 |
| 主分支 | `main` 🅴 / `master` 🅴 | 默认代码分支 |
| 上传文件 | Upload files 🅴 | 添加代码的入口 |
| 提交 | Commit 🅴 / Commit changes 🅴 | 保存一版变更 |
| 设置 | Settings 🅴 | 仓库配置页 |
| Pages | Pages 🅴 | 静态网站托管设置 |
| 源 | Source 🅴 | Pages 部署来源 |
| 部署分支 | Branch 🅴 | 选哪个分支的代码上线 |
| 根目录 | `/ (root)` 🅴 | 分支根目录 |
| 文件夹拖拽 | Drag & drop 🅴 | 浏览器拖文件进 GitHub |
| 公开仓库 | Public repository 🅴 | 任何人都能看 |
| 私有仓库 | Private repository 🅴 | 仅自己可见 |
| 个人主页 | Profile 🅴 | github.com/<用户名> |
| 收藏 / 书签 | Bookmark / Add to favorites 🅴 | 浏览器收藏功能 |
| 命令行 | Command line 🅴 | Git Bash / PowerShell |
| 开发者工具 | Developer tools 🅴 | F12 / 浏览器调试 |

---

部署完成后,告诉子安你的 URL,我帮你加进 v1 看板页脚 — 这样从你访问的页面就能看到自己的主页链接。

---

_主理人:子安(周总数字幕僚 🌙)_  
_最后更新:2026-07-04_
