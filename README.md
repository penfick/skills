# Agent Skills by penfick

A collection of agent skills for Claude Code, Codex, Pi Agent, and any tool that supports the [Agent Skills](https://agentskills.io) standard.

## Skills

| Skill | Description |
|-------|-------------|
| [vision-support](./vision-support/) | 为非多模态模型提供图片识别能力，支持多图识别、19+ 平台、主备回退 |

## 安装

### 方式一：`npx skills`（推荐）

```bash
# 安装指定 skill
npx skills add https://github.com/penfick/skills --skill vision-support -g -y

# 查看 repo 中所有可用 skill
npx skills add https://github.com/penfick/skills --list
```

### 方式二：npm

```bash
npm install -g vision-support
```

### 方式三：git clone

```bash
# 克隆整个 repo 到 skills 目录（所有 skill 都可用）
git clone https://github.com/penfick/skills.git ~/.agents/skills

# 或只安装单个 skill
git clone https://github.com/penfick/skills.git /tmp/skills
cp -r /tmp/skills/vision-support ~/.agents/skills/vision-support
rm -rf /tmp/skills
```

### 方式四：一行脚本

```bash
# Mac / Linux
bash -c "$(curl -fsSL https://raw.githubusercontent.com/penfick/skills/main/vision-support/install.sh)"
```

## 目录结构

```
skills/
├── README.md                    ← 你在这里
└── vision-support/              ← 单个 skill 目录
    ├── SKILL.md                 ← skill 入口
    ├── scripts/vision.mjs       ← 核心脚本
    └── ...
```

每个子目录是一个独立的 skill，包含自己的 `SKILL.md`，符合 [Agent Skills 规范](https://agentskills.io/specification)。

## License

MIT
