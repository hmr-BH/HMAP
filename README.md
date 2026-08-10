# HMAP — Human Maintainability Assessment of Programming Projects

> 评估一个编程项目**是否适合人类程序员维护**的 Claude Code skill。输出 0-100 分与九档定性，并对 vibe coding / AI 生成的「屎山」代码做专项取证。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

现在越来越多代码由 AI 生成，其中大量是 vibe coding 产物——专业程序员看了都头大。HMAP 用一套可复现的评分体系给项目的人类可维护性打分：**满分 100，覆盖五个维度，每一条评分判断都必须附带 `文件:行号` 证据**，不靠印象流。

## 功能特性

- **五维加权评分**：可读性 25 / 注释文档 20 / 架构 25 / AI 屎山 15 / 工程规范 15
- **九档定性**：从 90+「洁癖舒适区」到 0-20「只能 AI agent 维护」
- **AI 屎山专项取证**：12 类信号 + 正反例清单，单独成维度、单独出报告段落
- **证据纪律**：每条判断强制 `文件:行号`，杜绝无据断言
- **只评估不修改**：绝不顺手重构、修 bug，问题只进报告

## 评分模型

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| 代码可读性 | 25 | 命名语义化、函数短小单一职责、控制流清晰、心智路径顺畅 |
| 注释与文档质量 | 20 | 注释讲「为什么」而非复述操作、无废话、README 与代码一致、无幻觉引用 |
| 架构设计 | 25 | 分层与模块边界清晰、职责单一、依赖方向合理、便于维护拓展 |
| AI 屎山痕迹（反向计分） | 15 | 死代码、过度工程、无效抽象、幻觉注释、拼凑感——痕迹越多分越低 |
| 工程规范与一致性 | 15 | 命名/风格一致、错误处理一致、DRY、测试有意义 |

## 九档评分标准

| 分数段 | 档位定性 |
|--------|---------|
| 90-100 | 可读性和人类可维护性极高，注释清晰无废话，架构便于维护拓展；最代码洁癖的专业程序员也感到舒适 |
| 80-90 | 可读性和可维护性较高，逻辑/架构/注释有少量问题但整体通畅；大部分高质量开源项目在此档 |
| 70-80 | 正常项目水平，日常维护有少量心智负担；编码、注释基本规范 |
| 60-70 | 有小部分明显的 AI 屎山痕迹，注释略微混乱，逻辑较复杂 |
| 50-60 | 有一定规模 AI 屎山，部分架构意图不明，注释只描述操作不讲述原因，有拼凑痕迹 |
| 40-50 | AI 屎山较多，注释垃圾，可维护性低、可读性差，略微不适宜人类维护 |
| 30-40 | 较为不适宜人类程序员维护 |
| 20-30 | 极为不适合人类程序员维护 |
| 0-20 | 完全是一坨 AI 屎山，无药可救，不建议人类阅读（会遭心智创伤），只能 AI agent 维护 |

## 安装

需要 [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)。把本仓库的 `SKILL.md` 与 `references/` 复制到 Claude Code 的 skills 目录即可。

### 全局安装（所有项目可用）

macOS / Linux：

```bash
mkdir -p ~/.claude/skills/human-maintainability
cp SKILL.md ~/.claude/skills/human-maintainability/
cp -r references ~/.claude/skills/human-maintainability/
```

Windows（PowerShell）：

```powershell
$dst = "$HOME\.claude\skills\human-maintainability"
New-Item -ItemType Directory -Force "$dst\references" | Out-Null
Copy-Item SKILL.md $dst -Force
Copy-Item references\*.md "$dst\references\" -Force
```

### 项目级安装（仅某个项目可用）

把 `SKILL.md` 与 `references/` 复制到 `<你的项目>/.claude/skills/human-maintainability/`。

## 使用

对任意项目目录发起评估，命中以下关键词即触发：

- 「评估这个项目的可维护性」
- 「给这个项目打打分」
- 「这个项目是不是 AI 屎山」
- 「代码质量评估 / 可读性评分」
- 「HMAP / human maintainability」

支持参数：

| 参数 | 说明 |
|------|------|
| `--depth=轻\|中\|深` | 采样强度：≤50 文件全读，大项目分层采样 |
| `--output=路径` | 把完整报告写入指定 md 文件 |
| `--focus=维度名` | 只评估单个维度（可读性/注释文档/架构/AI屎山/工程规范） |

## 评估流程

1. **清点项目**：文件树、语言分布、行数（排除 `node_modules`、`dist` 等产物目录）
2. **采样**：按规模取样并声明置信度，未读文件不当读过打分
3. **逐维度取证**：每条判断落到 `文件:行号`
4. **加权打分** → 九档映射
5. **输出报告**：总分 / 分维度得分 / 优点 / 问题 / AI 屎山专项 / 结论

## 项目结构

```
HMAP/
├── SKILL.md                   # 主文件：触发、工作流、九档映射、报告模板
├── references/
│   ├── scoring-rubric.md      # 分维度 0-100 打分细则
│   └── ai-slop-signals.md     # 12 类 AI 屎山信号 + 正反例
├── .gitignore
├── LICENSE                    # MIT
└── README.md
```

## 协议

[MIT](./LICENSE)

## 贡献

欢迎提交 issue 与 PR：新增/修正屎山信号、调整打分细则、改进报告模板等。改动请保持现有结构（`SKILL.md` 主文件 + `references/` 细则）。
