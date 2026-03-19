---
name: focusavatar
description: 数字人生成 CLI 工具，凭 accessKeyId/accessKeySecret 调用后端 API，支持提交任务（MP3/MP4/文字→视频）与查询任务结果（orderNo）；不存储用户数据，凭证仅通过请求头发送。
category: media
author: community
keywords: focusavatar, 数字人, 数字人生成, AI数字人, 视频生成, ai视频, 语音合成, 唇形同步
---

# 数字人生成技能 (focusavatar)

命令行数字人生成工具，通过 **accessKeyId** 与 **accessKeySecret** 调用后端 API，完成「MP3 + MP4 模板 + 文字」到数字人视频的生成与结果查询。**安装或首次使用前请先前往控制台获取 accessKeyId 和 accessKeySecret**。

---

## 目的与能力

- **目的**：在命令行或技能环境中快速调用数字人视频生成服务，无需在本地保存用户媒体文件。
- **能力**：
  - **提交任务**：输入 MP3 地址、MP4 地址（本地路径或 URL）及合成文字，提交到后端；支持轮询直至完成并输出视频链接。
  - **查询结果**：凭任务单号 `orderNo` 查询任务状态与视频链接。
  - **不落盘**：仅将地址与文本传给后端，不在本工具内存储。
  - **交互引导**：分步输入、确认与重填，错误可追溯。

---

## 凭证（accessKeyId / accessKeySecret）

**使用前必读**：所有 API 调用均需认证，请先获取凭证：

1. **注册账号**：前往控制台（如 https://login.joycoreai.com/ 或部署方提供的地址）注册。
2. **购买/开通**：完成购买或开通流程。
3. **创建密钥**：在控制台创建密钥，复制 **accessKeyId** 和 **accessKeySecret**。

**使用方式**：

- 运行脚本时按提示输入，或
- 设置环境变量免输入（将 `你的accessKeyId`、`你的accessKeySecret` 替换为控制台复制的真实值）：

  **Windows（PowerShell，当前窗口有效）**：
  ```powershell
  $env:FOCUSAVATAR_ACCESS_KEY_ID = "你的accessKeyId"
  $env:FOCUSAVATAR_ACCESS_KEY_SECRET = "你的accessKeySecret"
  ```

  **Windows（CMD，当前窗口有效）**：
  ```cmd
  set FOCUSAVATAR_ACCESS_KEY_ID=你的accessKeyId
  set FOCUSAVATAR_ACCESS_KEY_SECRET=你的accessKeySecret
  ```

  **Windows（永久）**：  
  设置 → 系统 → 关于 → 高级系统设置 → 环境变量 → 用户变量 → 新建 `FOCUSAVATAR_ACCESS_KEY_ID`、`FOCUSAVATAR_ACCESS_KEY_SECRET` 并填入对应值。

  **Linux / macOS（当前终端有效）**：
  ```bash
  export FOCUSAVATAR_ACCESS_KEY_ID="你的accessKeyId"
  export FOCUSAVATAR_ACCESS_KEY_SECRET="你的accessKeySecret"
  ```

  **Linux / macOS（永久）**：  
  将上述两行写入 `~/.bashrc` 或 `~/.zshrc`，再执行 `source ~/.bashrc` 或 `source ~/.zshrc`。

认证通过请求头 `X-Access-Key-Id`、`X-Access-Key-Secret` 传递；本技能不保存、不上传凭证到除后端以外的任何地方。

---

## 指令范围（When to use）

- 需要**生成数字人视频**（提供 MP3、MP4 地址与文字）。
- 需要**查询数字人任务结果**（已知 orderNo）。
- 需要调用 **focusavatar / 焦点数字人 / yunji 数字人** 相关 API。
- 在命令行或 OpenClaw 技能环境中操作数字人生成与查询。

---

## 功能

- ✅ 使用前引导至指定地址获取 accessKeyId / accessKeySecret
- ✅ **两种模式**：**提交任务**（生成视频）/ **查询任务结果**（凭 orderNo）
- ✅ 分步引导：MP3 → MP4 → 文字 → 确认/重填
- ✅ 不下载文件：直接传地址给后端
- ✅ 进度与轮询：异步任务自动轮询，完成即输出视频链接
- ✅ 支持仅查询任务结果（输入 orderNo）

---

## 后端接口

- **提交**：`POST {BASE_URL}/skill/api/submit`  
  - Body：`mp3`, `mp4`, `text`  
  - 返回：`videoUrl` 或 `orderNo`（需轮询）
- **查询**：`POST {BASE_URL}/skill/api/api/result`  
  - Body：`orderNo`  
  - 返回：`status`、`progress`、`videoUrl`、`message` 等  

BASE_URL 由环境变量 `FOCUSAVATAR_API` 指定（未设置时默认示例：`https://yunji.focus-jd.cn`）。

---

## 安装

```bash
npx skills add https://github.com/lintqiu/focusavatar -s focusavatar -g -y
```

安装后通过 OpenClaw 或技能入口启动本技能即可；启动后会先提示获取 accessKeyId / accessKeySecret，再选择操作模式。

---

## 安装机制

**1. 通过 OpenClaw Skills 安装到本地**

- **前置条件**：本机已安装 **Node.js**（含 npm），以便使用 `npx`。未安装可前往 [https://nodejs.org/](https://nodejs.org/) 下载安装。
- 在终端执行（将 `https://github.com/lintqiu/focusavatar` 替换为实际技能仓库地址，例如 `https://github.com/lintqiu/focusavatar`）：
  ```bash
  npx skills add https://github.com/lintqiu/focusavatar -s focusavatar -g -y
  ```
- **参数说明**：`-s focusavatar` 为技能名称，`-g` 表示按全局/规范安装，`-y` 表示默认确认、非交互。
- 安装完成后，技能会出现在 OpenClaw 的本地技能目录（如用户目录下的 `.openclaw/workspace/skills/focusavatar`，以 OpenClaw 实际约定为准）。

**2. 运行环境与依赖**

- **Python**：需要 **Python 3.6 及以上**。  
  - 检查版本：`python3 --version` 或 `python --version`。  
  - 未安装请从 [https://www.python.org/downloads/](https://www.python.org/downloads/) 安装；Windows 安装时建议勾选「Add Python to PATH」。
- **requests**：必须安装，否则无法发起 HTTP 请求。  
  - Linux / macOS：`pip3 install requests` 或 `python3 -m pip install requests`  
  - Windows：`pip install requests` 或 `py -m pip install requests`  
  - 使用虚拟环境时，请在对应环境中执行上述命令。

**3. 权限与网络**

- **无需系统级或 root/管理员权限**：以当前用户安装和运行即可。
- **需要网络访问**：会访问环境变量 `FOCUSAVATAR_API` 指定的后端（未设置时使用默认地址），请确保本机可访问该地址（防火墙、代理允许出站）。

---

## 使用流程

1. **获取凭证**：按提示前往控制台完成注册 → 购买/开通 → 创建密钥，复制 accessKeyId、accessKeySecret，并输入或设置环境变量。
2. **选择模式**：
   - **提交任务**（选 `1`）：输入 MP3、MP4、文字 → 确认 → 提交 → 等待/轮询 → 输出视频链接。
   - **查询任务结果**（选 `2`）：输入 orderNo，查询状态与视频链接。
3. 仅查询时选择「查询任务结果」并输入 orderNo 即可。

---

## 隐私说明

- 本工具仅作**客户端调用**，**不存储、不收集**用户的 MP3/MP4 地址、文字内容或生成视频。
- 所有请求**直接发往后端**（由 `FOCUSAVATAR_API` 指定），数据处理与存储由该后端及所属方负责。
- **凭证**：accessKeyId、accessKeySecret 仅用于构造请求头，不写入磁盘、不上传到本仓库或第三方。
- 用户需确保所提交内容符合法律法规，不侵犯第三方权益。

---

## 坚持与特权

- **坚持（Persistence）**：不持久化用户业务数据；凭证可通过环境变量在会话间复用，由用户自行管理。
- **特权（Privileges）**：无需 root 或系统特权；需要网络权限；若由 OpenClaw/助手执行「提交任务」，建议设置较长超时（如 600 秒），因后端生成可能需数分钟。

---

## When to use（摘要）

- 需要生成数字人视频
- 需要查询数字人任务结果（orderNo）
- 需要调用 focusavatar / 焦点数字人 相关 API
- 命令行环境下快速生成或查询
