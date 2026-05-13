# Vision Support

> **铁律：本技能配置的模型仅用于图片内容识别，绝不参与主逻辑推理。**

为 Claude Code、Codex、Pi Agent 等开发工具中的**非多模态模型**（如 deepseek-v4-pro、GLM-5.1、mimo-v2.5-pro）提供图片识别能力。

当主模型无法"看"图片时，自动调用配置好的视觉模型来识别图片内容，把结果返回给主模型继续工作。

## 特性

- 🖼️ **多图识别** — 支持同时传入多张图片进行对比分析
- 🔄 **自动回退** — 主模型失败后依次尝试 fallback 模型
- 🌍 **19+ 平台** — 覆盖国内外主流 API（OpenAI / Gemini / 通义千问 / GLM / Ollama 等）
- 🎯 **零依赖** — 仅需 Node.js 18+，无需 npm install
- 🛠️ **交互式配置** — `init` 命令引导选平台、填密钥、选模型
- 🔌 **跨工具** — 适用于任何支持 Agent Skills 的工具

## 安装

### `npx skills`（推荐）

```bash
npx skills add https://github.com/penfick/skills --skill vision-support -g -y
```

### npm

```bash
npm install -g vision-support
```

安装后自动注册全局命令 `vision-support`，同时自动将 skill 文件复制到 `~/.agents/skills/`。

### Mac / Linux 一行命令

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/penfick/skills/main/vision-support/install.sh)"
```

### Windows (PowerShell)

```powershell
git clone https://github.com/penfick/skills.git $env:TEMP\skills
node $env:TEMP\skills\vision-support\install.mjs
```

### 手动安装

```bash
git clone https://github.com/penfick/skills.git ~/.agents/skills
```

### 卸载

```bash
# npx skills
npx skills remove vision-support

# npm
npm uninstall -g vision-support

# 其他方式
node install.mjs --uninstall
```

## 快速开始

```bash
# 1. 初始化（交互式选平台 → 填密钥 → 选模型）
vision-support init
# 或
node ~/.agents/skills/vision-support/scripts/vision.mjs init

# 2. 验证
vision-support config test

# 3. 识图
vision-support ./screenshot.png
```

## 使用方法

### 识别图片

```bash
# 单张
vision-support ./image.png

# 多张对比
vision-support img1.png img2.png "对比这两张图"

# URL 图片
vision-support https://example.com/img.png "描述图片"

# 自定义提问
vision-support ./ui.png "这个界面有什么布局问题？"
```

### 配置管理

```bash
vision-support init                    # 交互式初始化
vision-support config add              # 添加 fallback 模型
vision-support config edit [name]      # 编辑模型
vision-support config list             # 列出模型
vision-support config primary [name]   # 设置主模型
vision-support config remove <name>    # 删除模型
vision-support config set-key <n> <k>  # 设置密钥
vision-support config set-url <n> <u>  # 设置 API 地址
vision-support config test [name]      # 测试连通性
```

### 在 Agent 中触发

- **自动**：发送图片 + 说"看看这个截图"/"分析这个界面" → 自动触发
- **手动**：`/skill:vision-support` 或 `/vision`

## 支持的平台

| 分类 | 平台 |
|------|------|
| 国际 | OpenAI、Google Gemini、Anthropic Claude、DeepSeek、Groq、Mistral、xAI (Grok)、OpenRouter、Fireworks AI |
| 国内 | 通义千问 (Qwen VL)、智谱 GLM (GLM-4V)、Moonshot (Kimi)、阶跃星辰 (Step)、MiniMax、SiliconFlow (硅基流动)、小米 MiMo |
| 本地 | Ollama、LM Studio |
| 自定义 | 任何 OpenAI 兼容平台（自填 baseUrl） |

## 工作原理

```
用户发图片 + 问题
       ↓
 Agent 读取 SKILL.md，调用 vision.mjs
       ↓
 主视觉模型 (GPT-4o) ──成功──→ 返回识别结果
       ↓ 失败
 Fallback 1 (Gemini) ──成功──→ 返回识别结果
       ↓ 失败
 Fallback 2 (Qwen-VL) ──成功──→ 返回识别结果
       ↓
 stdout 输出文本描述 → 主模型继续工作
```

## 目录结构

```
vision-support/
├── SKILL.md                  # 技能说明（Agent 自动读取）
├── package.json              # npm 包配置
├── bin/
│   ├── cli.mjs               # npm 全局命令入口
│   └── postinstall.mjs       # npm 安装后自动部署 skill
├── install.mjs               # 跨平台安装脚本
├── install.sh                # Mac/Linux 一键安装
├── config.example.json       # 配置模板
├── scripts/
│   └── vision.mjs            # 核心脚本（零依赖）
└── references/
    └── supported-models.md   # 模型配置参考
```

## License

MIT
