# Module Detailed Design Spec

## Why
为了实现 LangGraph RPG-Agent 系统的架构蓝图，我们需要在实际编码前对每个模块进行详细的技术方案设计。通过先设计整体职责和接口，再基于依赖关系（从依赖最少的模块开始）逐步设计各个子模块的细节，并加入“设计反思”机制（将每个模块的设计反思结果向后续依赖的模块传递），可以保证系统的高内聚低耦合，确保各模块的设计不偏离整体架构。

## What Changes
- 增加 `docs/design/overall-architecture.md` 文档，用于整体模块的职责规划与接口设计，并梳理模块依赖关系。
- 按照 `core -> io/memory -> agent/box -> graph` 的依赖顺序，依次增加以下模块详细设计文档，并在每个文档末尾记录“设计反思”：
  - `docs/design/core-module.md`：全局配置与基础数据模型模块。
  - `docs/design/io-module.md`：I/O 插件适配器模块。
  - `docs/design/memory-module.md`：三级记忆模块（Sensory, STM, LTM）。
  - `docs/design/agent-module.md`：认知节点逻辑与 Prompt 模板模块。
  - `docs/design/box-module.md`：系统容器模块（状态守卫、感官合成、隐私屏蔽）。
  - `docs/design/graph-module.md`：LangGraph 状态定义与工作流组装模块。

## Impact
- Affected specs: 完善系统架构设计，提供落地指导，并确保依赖合理性。
- Affected code: 后续所有 `src/` 目录下的代码实现都将基于这些经过反思和迭代的设计文档。

## ADDED Requirements
### Requirement: 整体架构与依赖分析
系统应当提供一份整体规划文档，明确定义各模块的核心职责、模块间的交互接口以及详细的依赖关系。

#### Scenario: Success case
- **WHEN** 开发者阅读整体规划文档时
- **THEN** 能够清晰理解系统的工作流、核心抽象接口以及正确的开发/设计顺序。

### Requirement: 基于依赖关系的递进式设计与反思机制
每个核心模块都需要单独的详细设计文档。设计时必须遵循前置模块的设计结论，并在设计完成后进行反思。反思内容需明确记录，以便后续模块参考。如果在设计中发现与整体规划有冲突，必须在文档中详细描述。

#### Scenario: Success case
- **WHEN** 开发者进行后续模块设计时
- **THEN** 能够参考前置模块的设计细节和反思总结，及时调整当前模块的设计，避免架构腐化。
