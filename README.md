# HMAP — Human Maintainability Assessment of Programming Projects

> 评估一个编程项目**是否适合人类程序员维护**的 Claude Code skill。输出 0-100 分与九档定性，并以 **60 分为及格线**（≥60 人类可维护，<60 不适合人类直接维护），对 vibe coding / AI 生成的「屎山」代码做专项取证。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

越来越多代码由 AI 生成，其中大量是 vibe coding 产物——表面规范、实则让人类难以维护。HMAP 用一套可复现的评分体系给项目的人类可维护性打分：**满分 100，覆盖四个维度，每一条评分判断都必须附带 `文件:行号` 证据**，不靠印象流。

**黑猫白猫，一视同仁**：不管项目是 vibe coding、AI 代写还是纯手工，同一把尺子。AI 来源、项目体量、维护者人数**永不作为判据**，只评"产物是否妨碍人类维护"。

## 功能特性

- **四维加权评分**：设计合理性与技术诚实性 25 / 可追踪性与心智负担 30 / 人类可读性与自我解释性 15 / AI 屎山与许愿痕迹（反向）30
- **九档定性 + 60 分及格线**：≥60 = 人类可维护，<60 = 不适合人类直接维护（符合百分制考试直觉）
- **测量驱动，反 vibe-check**：13 项客观测量表（M1-M13）先于任何打分，凭印象的数值不算证据，同一项目两次评估总分差控制在 ≤3 分
- **结构性硬闸门**：存在使人类无法/极难维护的结构性事实时总分硬性封顶（god-file 混杂 → 60；源码内联 AI 过程标记成规模 → 45；热路径调试残留 → 45；前两者并存 → 40）
- **职责混杂 RM 协议**：区分"大但组织清晰"（HMCL/grok-build 式，不降档）与"大且混杂"（PCL/N.E.K.O 式，触发闸门）的唯一仲裁器
- **AI 屎山专项取证**：14 类信号 + 许愿检测协议 + 正反例清单
- **只评估不修改**：绝不顺手重构、修 bug，问题只进报告

## 评分模型

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| 设计合理性与技术诚实性 | 25 | 架构匹配问题复杂度吗？承诺成立吗？有技术思维还是纯许愿？ |
| 可追踪性与心智负担 | 30 | 人类能追踪请求→代码吗？职责清晰还是啥都写一块？改动一处需知几处？ |
| 人类可读性与自我解释性 | 15 | 代码能自我解释吗？命名/注释是帮人懂「为什么」还是写给 AI/清单看？ |
| AI 屎山与许愿痕迹（反向计分） | 30 | 承诺背离、过度工程、源码内联 AI 过程标记、结构性 god、系统性复制粘贴、调试残留、幻觉注释——痕迹越多分越低 |

## 九档评分标准（60 分流）

| 分数段 | 档位定性 |
|--------|---------|
| 90-100 | 适合，体验极佳：职责边界清晰、可追踪，注释讲"为什么"，承诺全兑现 |
| 80-90 | 适合，顺畅：整体通畅，仅个别可接受债务；无结构性混杂、无成规模 AI 过程指纹 |
| 70-80 | 适合，有负担：有跨文件追踪成本、个别庞杂点或小部分 AI 痕迹 |
| 60-70 | 及格线边缘：勉强能维护，有明显 AI 屎山痕迹或结构庞杂苗头，接手吃力但人类仍可维护 |
| 50-60 | 不及格：不适宜人类直接维护，职责混杂严重、可读性差，接手成本不成比例 |
| 40-50 | 不适宜：核心庞杂、结构不可追踪，需靠外置文档/AI 才能理解 |
| 30-40 | 不适宜（更重）：结构性 god 泛滥，人类无法安全改动 |
| 20-30 | 极不适宜：结构性 god + AI 过程指纹遍布 |
| 0-20 | 只能 AI agent 维护：完全屎山，无药可救 |

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
| `--focus=维度名` | 只评估单个维度（设计合理性/可追踪性/可读性/AI屎山） |

## 评估流程

1. **清点项目**：文件树、语言分布、行数（排除 `node_modules`、`dist`、`bin/Release` 等产物目录）
2. **测量（先于打分）**：跑客观测量表 M1-M13，数值填测量单
3. **承诺-实现核对**：README/文档承诺逐条代码验证（许愿检测）
4. **RM 职责混杂协议**：对 ≥400 行函数 / ≥1800 行文件判定"单一职责 vs 混杂"
5. **加权打分 → 硬闸门 → 60 分流校验** → 九档映射
6. **输出报告**：总分 / 分维度得分 / 优点 / 问题 / AI 屎山专项 / 结论

## 项目结构

```
HMAP/
├── SKILL.md                   # 主文件：触发、工作流、九档映射、报告模板
├── references/
│   ├── scoring-rubric.md      # 测量表 M1-M13、档位映射、RM 协议、硬闸门、平局规则
│   └── ai-slop-signals.md     # 14 类 AI 屎山信号 + 许愿检测协议
├── .gitignore
├── LICENSE                    # MIT
└── README.md
```

## 协议

[MIT](./LICENSE)

## 贡献

欢迎提交 issue 与 PR：新增/修正屎山信号、调整打分细则、改进报告模板等。改动请保持现有结构（`SKILL.md` 主文件 + `references/` 细则）。
