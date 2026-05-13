# Agent Skills by penfick

一个 Agent Skills 集合，适用于 Claude Code / Codex / Pi Agent / 任何支持 [Agent Skills](https://agentskills.io) 标准的工具。

## Skills

| Skill | 说明 |
|-------|------|
| [vision-support](./vision-support/) | 为非多模态模型提供图片识别能力，支持多图识别、19+ 平台、主备回退 |

## 安装

### `npx skills`（推荐）

```bash
# 安装指定 skill
npx skills add https://github.com/penfick/skills --skill vision-support -g -y

# 查看所有可用 skill
npx skills add https://github.com/penfick/skills --list
```

### Git Clone

```bash
git clone https://github.com/penfick/skills.git ~/.agents/skills
```

## 目录结构

```
skills/
├── README.md
├── LICENSE
└── vision-support/
    ├── SKILL.md
    └── ...
```

每个子目录是一个独立 skill，包含 `SKILL.md`，符合 [Agent Skills 规范](https://agentskills.io/specification)。

## 友情链接

https://linux.do/

## License

MIT
