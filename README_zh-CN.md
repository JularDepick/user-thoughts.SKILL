<div align="center">

# UserThoughts.SKILL

[![Version](https://img.shields.io/badge/Version-0.1.1-blue)](https://github.com/JularDepick/UserThoughts.SKILL/releases)
[![Copyright](https://img.shields.io/badge/Copyright-JularDepick-0066AA)](./COPYRIGHT)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)
[![Standard](https://img.shields.io/badge/Standard-Agent--SKILL-red)](https://agentskills.io/)

[[English]](./README.md) [[简体中文]](./README_zh-CN.md)

一个遵循 [Agent Skills](https://agentskills.io/) 规范的技能，让 AI Agent 自动组织用户发言，维护**持久化、绑定项目的想法文档库 (mdbase)**——让决策、偏好和约束跨越会话、穿越 Agent 传递。

</div>

---

## 为什么需要这个技能？

与 Agent 协作开发项目时，用户会在对话中不断表达设计决策、需求偏好、规则约束。这些细节不仅容易散落在聊天记录中，更关键的是——**跨会话和接手 Agent 时，这些积累会彻底丢失**。

### 核心痛点

每个新会话、新 Agent 都从零开始。用户原本的意图、积累的决策、踩过的坑，在上下文切换的瞬间全部蒸发。结果：

- **跨会话漂移** — 新会话从头推导需求，遗漏用户已说过的细节
- **接手断裂** — 切换 Agent 或交接协作者时，接手方完全不了解用户的积累，只能猜、只能重新问、只能偏离
- **重复摩擦** — 用户不得不跨会话反复解释同样的决策和偏好，消磨信任和节奏

UserThoughts.SKILL 通过维护一个**持久化、绑定项目的想法文档库**来解决这个问题——它跨越会话边界，在 Agent 之间干净地传递：

- **捕获**：对话中自动识别并记录用户想法
- **组织**：按维度整理为结构化文档库 (mdbase)
- **保留**：保持用户原始表述，不简化、不改写
- **绑定**：想法文档库与项目生命周期同步——不属于任何单次会话或单个 Agent

任何接手项目的 Agent 只需读取 `mdbase/`，就能立刻理解用户要什么、决定了什么、有什么约束——无需重新推导。

### 示例：有无 UserThoughts 的对比

**场景** — 用户花 3 个会话定义了一个 Web 应用的认证方案、UI 风格和技术栈。然后开新会话（或交给另一个 Agent）来实现登录页。

**没有 UserThoughts：**

```
会话 1:  用户: "用 OAuth2，别用 JWT。上个项目吃过 token 过期的亏。"
会话 2:  用户: "暗色主题优先，亮色后面做。圆角，8px 半径。"
会话 3:  用户: "Next.js + Prisma。不要 MongoDB——我们需要关系完整性。"
...
会话 4:  [新会话 / 不同 Agent]
         Agent: "我来搭一个 JWT 认证、直角、MongoDB 的登录页。"
         用户: "你到底有没有听我说话？！" 😤
```

新会话从零开始，之前所有决策全部丢失。

**有 UserThoughts：**

```
会话 1-3: UserThoughts 静默记录到 .ustht/mdbase/
          ├── details/rules.md     → "不用 JWT，用 OAuth2。上个项目有 token 过期问题。"
          ├── details/ui/details.md → "暗色主题优先。圆角 8px。"
          └── details/dev-stack.md  → "Next.js + Prisma。不要 MongoDB。"

会话 4:   [新会话 / 不同 Agent]
          Agent 读取 mdbase/ → 已知所有约束 → 正确实现。
          用户: "完美。" ✅
```

想法文档库弥合了断裂。新 Agent 继承了用户的完整决策历史。

### 语言策略

- **SKILL 本体**（SKILL.md、references/、assets/）语言固定为中文，不随用户语言变化
- **Agent 输出适配用户语言**：命令反馈、sortin 摘要、mdbase 展示、提示信息等面向用户的输出，必须使用用户当前对话所用的语言
- **想法原文保留**：raw 记录和 mdbase 中的想法内容保持用户原始语言，不翻译、不转换

---

## 安装

### 前置依赖

| 依赖 | 必需 | 用途 |
|------|------|------|
| `read` / `write` | 是 | 读写 `#ustht/` 下文件 |
| `bash` | 是 | 文件复制、目录创建 |
| SubAgent | 否 | 并行维护 mdbase 维度文件 |

### 安装方式

将 `UserThoughts/` 目录放入 Agent 的技能文件夹。具体路径取决于你的 Agent：

| Agent | 技能目录 |
|-------|---------|
| VS Code / Copilot | `.agents/skills/UserThoughts/` |
| Claude Code | `.claude/skills/UserThoughts/` |
| OpenCode | `.opencode/skills/UserThoughts/` |
| 其他 | 参考对应 Agent 文档 |

安装后，Agent 通过 `SKILL.md` 的 YAML frontmatter 自动发现技能。

---

## 快速开始

1. **安装**技能（见上方）
2. **开始对话**——当用户表达项目想法时，技能自动激活
3. **使用命令**：
   - `/ustht status` — 查看当前状态
   - `/ustht sortin` — 整理想法到 mdbase
   - `/ustht mdbase show` — 查看想法库

---

## 工作原理

技能采用**三阶段渐进式披露**（progressive disclosure）来最小化上下文开销：

1. **发现** — Agent 读取 YAML frontmatter 的 `name` 和 `description`（约 100 词，始终在上下文中）。这是触发机制——Agent 根据 description 决定是否调用技能。
2. **激活** — Agent 加载 `SKILL.md` 正文（核心指令，约 300 行）。包含工作流、命令、工作模式和关键规则。
3. **执行** — Agent 按需加载 `references/` 下的详细规范。仅在需要具体行为规范时才读取（如 `sortin.md` 维护算法、`commands.md` 正则匹配）。

这意味着技能在需要深度之前保持轻量——简单的 `/ustht status` 只需阶段 2，而复杂的 `resort` 可能加载阶段 3。

### 工作流

```
用户发言 → Agent 识别项目想法 → 写入 raw/（即时计划）
         ↓
用户执行 /ustht sortin → Agent 处理 raw/ → 按维度追加到 mdbase/
         ↓
用户执行 /ustht mdbase show → Agent 展示组织好的想法库
```

### 工作模式

| 模式 | 条件 | 行为 |
|------|------|------|
| **即时计划** | `SKILL_STATUS=on` + `INSTANT_STATUS=on` | 自动捕获用户想法写入 raw/ |
| **被动模式** | `SKILL_STATUS=on` + `INSTANT_STATUS=off` | 仅响应命令 |
| **暂停模式** | `SKILL_STATUS=off` | 写入命令返回错误；只读命令仍可用 |
| **只读模式** | 必需工具缺失 | 仅只读命令可用 |

---

## 技能结构

```
UserThoughts/
├── SKILL.md                    # 入口（frontmatter + 核心指令）
├── references/                 # 详细规范（按需加载）
│   ├── commands.md             # 命令正则与自然语言映射
│   ├── sortin.md               # 维护算法与维度管理
│   ├── edge-cases.md           # 边界场景与交互示例
│   └── safety.md               # 安全边界与数据完整性
├── scripts/                    # Python 脚本（供 Agent 调用，均支持 --help）
│   ├── common.py               # 共享工具函数（供其他脚本导入）
│   ├── status.py               # 显示当前状态
│   ├── init.py                 # 初始化 .ustht/ 目录
│   ├── show_raw.py             # 查看未处理 raw 文件
│   ├── show_mdbase.py          # 查看 mdbase 索引/维度
│   ├── sortin.py               # 执行软维护
│   ├── write_raw.py            # 写入 raw 条目
│   ├── toggle.py               # 切换 SKILL/INSTANT 状态
│   └── ignore_ops.py           # 忽略操作
└── assets/
    └── Runtime-Template/       # 首次使用时复制到工作目录的模板
        ├── define.ini
        └── mdbase/
            ├── README.ai.md
            ├── backlog.md
            └── details/...
```

---

## 命令

```bash
# 状态与开关
/ustht init                                # 初始化工作目录（创建 .ustht/ 及模板）
/ustht status                              # 全部状态概览
/ustht skill [on|off]                      # 查看/切换技能状态
/ustht instant [on|off]                    # 查看/切换即时计划

# 维护流程
/ustht sortin [--dry]                      # 软维护（追加新想法），--dry 预览不写入
/ustht resort [--dry]                      # 硬维护（重整全部 mdbase），--dry 预览不写入

# 忽略管理
/ustht ignore start|end                    # 开始/结束忽略区间（仅上下文有效）
/ustht ignore [--last]                     # 忽略上一条已记录的想法
/ustht ignore show                         # 查看被忽略的记录
... /ustht ignore                          # 后缀模式，忽略本条消息

# 内容查看与导出
/ustht raw                                 # 查看未处理的 raw 记录
/ustht mdbase show [--all|--维度名]        # 查看索引或指定维度
/ustht mdbase export [--all|--维度名]      # 导出到 #export/
/ustht import <路径>                       # 扫描路径下 .md 文件，并入 mdbase
```

命令也可通过自然语言触发——当用户的表述明确指向某一命令时（如"看看规则" → `/ustht mdbase show rules`、"整理一下想法" → `/ustht sortin`），Agent 直接执行等效命令。详细映射规则见 [references/commands.md](references/commands.md)。

---

## 运行时结构

首次使用后，技能在工作目录下创建 `.ustht/`：

```
<工作目录>/
└── .ustht/
    ├── define.ini             # 状态与宏常量
    ├── raw/                   # 用户原始发言（按日期分片）
    │   └── yyyy-mm-dd.md
    ├── ignored/               # 被忽略的发言
    │   └── yyyy-mm-dd.md
    ├── export/                # 导出的 mdbase 内容
    └── mdbase/                # 整理后的用户想法库
        ├── README.ai.md       # 索引与概览
        ├── backlog.md         # 待办事项
        └── details/           # 按维度组织的想法文件
            ├── rules.md       # 项目规则
            ├── plans.md       # 项目规划
            ├── dev-stack.md   # 技术栈
            ├── general.md     # 通用（兜底维度）
            ├── ui/
            │   ├── outline.md # UI 整体设计
            │   └── details.md # UI 细节设计
            └── ...            # 按需扩展
```

---

## 开发

本仓库包含技能本体（`UserThoughts/`）及其文档。

```
UserThoughts.SKILL/
├── UserThoughts/           # 技能本体（安装到 Agent 的技能目录）
│   ├── SKILL.md            # 入口文件（YAML frontmatter + 核心指令）
│   ├── references/         # 按需加载的详细规范
│   ├── scripts/            # Python 脚本（供 Agent 调用）
│   └── assets/             # 首次使用时复制到工作目录的运行时模板
├── README.md               # 英文文档
├── README_zh-CN.md         # 中文文档
├── LICENSE                 # MIT 许可证
└── COPYRIGHT               # 版权声明
```

**SKILL 本体语言**：技能本体（`SKILL.md`、`references/`、`assets/`）使用中文编写。Agent 输出自动适配用户语言。

**贡献**：欢迎提交 Issue 和 Pull Request。请确保更改兼容 [Agent Skills](https://agentskills.io/) 规范。

---

## 更新日志

版本历史请参阅 [GitHub Releases](https://github.com/JularDepick/UserThoughts.SKILL/releases)。

---

## 许可证

[MIT](./LICENSE) — Copyright (c) 2026 JularDepick
