# Human Maintainability Assessment of Programming Projects

[English](README.md) | [中文](README.zh-CN.md)

`HMAP`是一个评估编程项目的**人类可维护性**的skill，专门针对 Vibe Coding 与 AI 生成代码。输出 0–100 分量化评分与九档定性结论，**分数大于 60 分可人类参与维护，小于 60 分建议重构或使用AI维护。**

---

## 为什么需要这个Skill

AI 生成代码的速度远超人类理解速度。一个人类手写项目可能今天能被完全理解，但让AI迭代两周后连原作者都难以看懂。

HMAP 会从多个角度对项目代码进行深入评估：
- 职责混杂的超大代码文件让单点改动牵一发而动全身
- 过度封装与业务实际需求脱节
- 复制粘贴的相似逻辑导致维护时举步维艰
- README文档承诺与实现行为不一致
- AI 生成过程中的临时标记、调试代码直接残留在生产环境

评估基于 15 项客观指标（含 M14 语义一致性审计：名实、契约、概念、词汇四个不变量）与硬性结构闸门，不接受"总体还行"的模糊判断。如果项目低于 60 分，说明人类程序员来维护该项目会感受到困惑与艰难。

## 评分说明

| 分数段 | 档位定性 |
|--------|---------|
| 90-100 | **适合，体验极佳**：职责边界清晰、请求→代码可追踪，注释讲"为什么"，承诺全部兑现 |
| 80-90 | **适合，顺畅**：整体通畅，仅个别可接受债务；**无结构性混杂、无成规模 AI 过程指纹** |
| 70-80 | **适合，有负担**：已有跨文件追踪成本、个别庞杂点或小部分 AI 痕迹 |
| 60-70 | **及格线边缘：勉强能维护**：有明显 AI 屎山痕迹或结构庞杂苗头（god-file/庞杂函数），接手吃力但人类仍可维护 |
| 50-60 | **不及格：不适宜人类直接维护**：职责混杂严重、可读性差，人类接手成本不成比例 |
| 40-50 | **不适宜**：核心庞杂、结构不可追踪，必须靠外置文档/AI 才能理解 |
| 30-40 | **不适宜（更重）**：结构性 god 泛滥，人类无法安全改动 |
| 20-30 | **极不适宜**：结构性 god + AI 过程指纹遍布 |
| 0-20 | **只能 AI agent 维护**：完全屎山，无药可救 |

---

## 安装

本 skill 遵循 **Agent Skills 标准**（`SKILL.md` + `references/`），**任何支持 skills 的 code agent 都能使用**——不限于 Claude Code（Cursor、Windsurf、Zed、Trae 等支持该标准的 agent 均可）。

安装方法统一为：把本仓库的 `SKILL.md` 与 `references/` 复制到你所用 agent 的 skills 目录下，命名为 `human-maintainability/` 子目录。

以 **Claude Code** 为例（全局安装，所有项目可用）：

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

**其他 agent**：按各自文档指定的 skills 目录放置即可——例如 Cursor 的项目级 `.cursor/skills/`、Windsurf 的 `.windsurf/skills/`、或通用的用户级 `~/.skills/`。目录名必须是 `human-maintainability/`，且 `SKILL.md` 与 `references/` 保持同目录。

项目级安装（仅某项目可用）：把两个文件放到 `<你的项目>/.claude/skills/human-maintainability/`（或对应 agent 的项目级 skills 目录）。

---

## 使用

在项目目录触发评估：

- `/human-maintainability 对这个项目进行打分`
- `评估这个项目的人类可维护性`
- `执行 HMAP 评分`

可选参数：
- `--depth=轻|中|深（控制文件采样强度，越深结果越全面，越浅token消耗越少。默认为"中"）`
- `--output=报告文件输出路径（默认不输出）`
- `--focus=关注维度（设计合理性|可追踪性|可读性|AI屎山|其他）可指定，但不会出总分`

---

## 项目结构

```
HMAP/
├── SKILL.md                 # 工作流与报告模板
├── references/
│   ├── scoring-rubric.md    # M1-M15 测量表、SCA 语义一致性协议与硬闸门
│   ├── ai-slop-signals.md   # 17 类 AI 低质 / 语义债务信号
│   ├── golden-example.md    # 完整打分示例
│   ├── cp-detect.py         # 复制粘贴分组检测器（M5）
│   └── semantic-surface.py  # SCA 协议语义表面提取器（M14）
├── LICENSE
└── README.md
```

## 许可证

[MIT License](./LICENSE)
