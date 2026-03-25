# 李宏毅 AI Agent 课程完整笔记

> **视频来源**: [B站 BV1D2wVzLELU](https://www.bilibili.com/video/BV1D2wVzLELU/)
> **讲者**: 李宏毅教授（台湾大学）
> **总时长**: 约 2.5 小时（4集）
> **转录方式**: yt-dlp 下载音频 → whisper-cli (large-v3-turbo) 本地转录 → Qwen3-235B-A22B 总结
> **幻灯片提取**: yt-dlp 下载视频(720p) → ffmpeg 关键帧提取 → dhash 去重 → tesseract OCR + 多模态 AI 识别
> **转录日期**: 2026-03-25

---

## 合集目录

| 集数 | 标题 | 时长 | 逐字稿文件 |
|------|------|------|-----------|
| P1 | AI Agent 的核心技术：Context Engineering 基本概念解说 | 53:06 | `p1_context_engineering.txt` |
| P2 | AI Agent 之间可以有什么样的互动 | 22:29 | `p2_agent_interaction.txt` |
| P3 | AI Agent 对于工作带来的冲击 - 以学术研究为例 | 23:56 | `p3_work_impact.txt` |
| P4 | AI Agent 背后的关键技术，上下文工程 (Context Engineering) | 1:50:08 | `p4_context_engineering_deep.txt` |

> 完整逐字稿合并文件: `BV1D2wVzLELU_full_transcript.txt`（187KB, 6613行）

---

## 第1集: Context Engineering 基本概念解说（53分钟）

### 课程大纲
1. AI Agent 核心技术：Context Engineering（重点）
2. AI Agent 间互动
3. AI Agent 对未来工作的冲击

### 一、为什么需要 Context Engineering

- **语言模型的本质**：文字接龙，给输入（Prompt），接一段话出来
- **核心矛盾**：语言模型"活在当下"，只管现在的输入，不管之前给过什么
- **Agent 工作流程**：
  - 人类给输入 → 模型回应（可能是工具调用指令）→ 工具执行 → 输出传回模型
  - 每次都必须把**完整历史**传回模型（之前的命令 + 工具指令 + 工具输出）
- **Context = 模型的输入**：包含所有历史信息的完整上下文

> "语言模型是活在当下的，它只管现在的输入"
> "AI Agent 就像经纪人，决定模型该看什么"

### 二、Context Engineering 算法框架

**形式化定义**：
```
C_{t+1} = F(I_t, O_t, C_t)
```
- `C_t`：第 t 步的上下文（Context）
- `I_t`：第 t 步的外部输入（用户指令、工具输出等）
- `O_t`：第 t 步的模型输出
- `F`：上下文更新函数 ← **这就是 Context Engineering 要设计的核心**

**上下文分层**：
- **P (Prompt)**：实际输入模型的活跃上下文
- **N (Non-prompt)**：存储在硬盘的非活跃记忆

### 三、压缩技术 (Compression)

#### 3.1 为什么需要压缩
- 模型输入长度有限（如 GPT-4 为 32k token）
- 随着对话推进，上下文越来越长，终将超出限制
- **84% 的 context 由外部输入（工具输出）占据**

#### 3.2 压缩方法

| 方法 | 原理 | 优缺点 |
|------|------|--------|
| **Observation Masking** | 将工具输出替换为 "此处有工具输出" | 成本低，但可能引发轨迹延长 |
| **LLM Summary** | 用语言模型压缩历史记录 | 效果好但成本高 |
| **混合策略** | 前期用 Masking，后期用 Summary | 综合效果最佳 |

#### 3.3 论文验证
- **SWE Bench 实验**（2023）：Observation Masking 与 LLM Summary 表现相当，但前者更省成本
- **ACON 论文**（2023）：提出反馈机制提升摘要质量，解决信息丢失问题

### 四、记忆管理 (Memory Management)

#### 4.1 双层存储架构
```
C_t = (P_t, N_t)
P_t: 输入模型的 Prompt 部分
N_t: 硬盘存储的非活跃记忆
```

#### 4.2 操作机制
- **SaveMemory**：将 P_t 部分转移到 N_t
- **LoadMemory**：从 N_t 检索信息到 P_t
- **MemorySearch**：按关键词搜索记忆
- **MemoryGet**：按行号范围获取特定记忆片段

#### 4.3 类比
- **Rick & Morty 记忆管**：地下室存储非活跃记忆

### 五、过滤与按需加载

#### 5.1 Observation Filtering
- **智能读取工具**：带语义理解的文件读取（如只定位 bug 相关代码）
- **内存分块访问**：OpenClaw 的 MemoryGet 工具（指定行号范围）

#### 5.2 On-Demand Loading（按需加载）
- **传统方法**：将所有工具说明写入 System Prompt（易超限）
- **NCP0 方案**（2023）：
  - 语言模型自主生成工具需求
  - 动态检索工具库（类似 OpenClaw 的 Skill 机制）

### 六、Agentic Context Engineering (ACE)

#### 6.1 核心思想
- 让 LLM **自主管理**上下文，而非人类设计规则
```
C_{t+1} = F_{LLM}(C_t, I_t, O_t)
```

#### 6.2 代表性工作
| 方法 | 机制 | 特点 |
|------|------|------|
| **Dynamic Cheat Sheet** | Prompt 引导 LLM 优化 context | 简单有效 |
| **Recursive LM**（2023） | 通过元数据索引实现无限长 context | 突破长度限制 |
| **Agent4**（2023） | 微调模型使用 fold 压缩工具 | 模型学会自主压缩 |

#### 6.3 挑战：模型抗拒压缩
- LLM 倾向于保留记忆（如拒绝执行 erase 指令）
- 解决方案：通过 RL 训练，用 context 长度惩罚引导模型分裂 subagent

---

## 第2集: AI Agent 之间的互动（22分钟）

### 一、协作拓扑结构

#### 1.1 四种协作模式
| 结构 | 说明 | 效果 |
|------|------|------|
| **链式 (Chain)** | 线性传递 | 效果最差 |
| **树状 (Tree)** | 先主干发想再分给分支 | 反直觉地有效 |
| **全连接 (Mesh)** | 所有 Agent 互相连接 | 效果最佳 |
| **随机 (Random)** | Mesh 剪枝后的随机连接 | 接近 Mesh |

#### 1.2 关键发现
- **协作扩展定律 (Scaling Law)**：Agent 数量增加 → 质量提升 → 最终饱和
- 不同任务需定制化拓扑结构，没有通用最优解

### 二、对抗性互动：狼人杀

#### 2.1 实验设计
- 通过"内心独白 + 公开发言"双模式验证 AI 策略能力
- 典型案例：狼人 Mona 发现暴露后，投票给队友 Grace 制造"金水"假象

#### 2.2 剧本杀强化学习论文（2024年1月）
- RL 训练使凶手角色隐藏能力显著提升
- **重要发现**：数学任务 (Math500/AIM/GSM8K) 和指令遵循 (IF eval) 出现跨任务能力迁移
- **类比人类进化**：社交能力可能促进推理能力发展

### 三、AI 社交行为

#### 3.1 Mobook 平台观察
- AI 自发成立"甲壳教"（五大教义 + 入教指令）
- 70% 以上帖子对话深度为 0（仅单次回复）

#### 3.2 自主性边界
- 小金实验：指令"自主收集素材 → 制作视频"，2小时自主调试
- **结论**：当前 AI 本质仍是高级文字接龙工具，真正自主性需突破指令依赖

---

## 第3集: AI Agent 对工作的冲击 - 以学术研究为例（24分钟）

### 一、AI 在学术研究各环节的应用

#### 1.1 论文撰写
| 指标 | AI 完成 | 人类完成 |
|------|---------|---------|
| 成本 | $10 | $1,000 |
| 时间 | 1 小时 | 16 小时 |
| 错误率 | 仅 1 处数据错误 | - |

- **Andrew Hall 实验**：用 Claude Code 1小时生成论文，对比博士生16小时

#### 1.2 实验设计
- **Auto Research 系统**：LLM 自主训练模型，5分钟/次实验迭代

#### 1.3 创意生成

**2024年 LLM 创意研究**：
- AI 创意 Novelty（新颖性）胜出
- 人类创意 Feasibility（可行性）胜出

**2025年续作研究**：
- 实操验证发现 AI 创意实操性下降
- 人类创意最终评分反超
- **典型问题**：AI 倾向堆砌术语但难以落地

#### 1.4 论文审稿
- **Triple AI 2026 会议实践**：3 人类 + 1 AI 审稿人，AI 仅提供建议不打分

### 二、AI for Science 会议数据
- 投稿量：247 篇
- 接受率：19.4%（48 篇）
- 接受论文特征：**人类在创意和实验设计阶段介入度高**

### 三、未来趋势判断
1. 研究机构将转型为"资深学者 + AI 军团"模式
2. 形成"AI 写稿 - AI 审稿"闭环系统
3. H-Index 体系的适用性存疑
4. 研究本质的再定义：**问题发现 vs 论文产出**

---

## 第4集: Context Engineering 深度版（1小时50分钟）

> 这是第1集内容的综合深入版本，包含更多技术细节和例子。

### 一、Context Engineering vs Prompt Engineering

| 维度 | Prompt Engineering | Context Engineering |
|------|-------------------|-------------------|
| 关注重点 | 输入格式（JSON 结构、特殊符号） | 自动化管理输入内容 |
| "神奇咒语"依赖 | 高（如 "Waves Waves" 触发长文本） | 低（现代模型依赖度降低） |
| 输入管理方式 | 人工设计规则 | 模型自主管理 |

> 类似 Neural Network → Deep Learning 的命名迭代

### 二、In Context Learning (ICL)

- **机制**：通过输入示例（而非参数调整）影响模型输出
- **经典案例**：GEMINI 1.5 通过输入卡拉蒙语教科书实现零样本翻译
  - 不需要语法规则，只需例句
  - 评分从 <1 提升至 4.0（满分 6 分）

### 三、工具调用框架

```
执行流程：
1. 模型生成工具调用指令（如 [TOR]Temperature(高雄, 2025-01-11)[/TOR]）
2. 解析指令并执行工具
3. 将工具输出注入上下文继续生成
```

### 四、Computer Use 技术
- 通过坐标定位实现浏览器操作
- 需 GPT-5 级模型才能准确执行

### 五、深度思考机制 (Reasoning)
- **脑内小剧场**：模型自主生成多路径解题过程
- 代表模型：ChatGPT O 系列、DeepSeek R 系列、Gemini Deep Think

### 六、长上下文处理挑战

#### 6.1 Context Rot 现象
- DataBrick 实验：搜索 token 超过临界点后正确率骤降
- **Lost in the Middle 效应**：模型更关注上下文首尾信息

#### 6.2 上下文窗口现状
- Llama 4: 10M tokens（但实际有效使用率不足 5%）
- Gemini 1.5: 200 万 token 时开始注意力分散
- 哈利波特全集处理准确率仅达 72%

### 七、压缩技术详解

| 技术方案 | Context 利用率 | 任务完成率 | 典型场景 |
|---------|---------------|-----------|---------|
| 原始 RAG | 30% | 65% | 简单问答 |
| 递归压缩 | 68% | 82% | 长期任务规划 |
| Multi Agent | 85% | 91% | 复杂系统操作 |
| 混合式记忆管理 | 76% | 88% | 持续学习场景 |

### 八、Multi Agent 系统

#### 8.1 架构价值
- 分工降低单 Agent Context 负载
- **旅游规划场景**：领导 Agent 仅保留订餐/订房结果，执行 Agent 处理具体操作细节
- LangChain 实验数据：复杂任务中 Multi Agent 表现优于单 Agent 35%

#### 8.2 典型应用
- **ChatDev 系统**：CEO / CTO / 程序员 / 测试员多角色协作
- 论文写作分工：分布式摘要生成 + 汇总写作

### 九、记忆筛选机制
- **斯坦福小镇实验**验证的三维度排序：
  1. 重要性评分（0-9分）
  2. 时间衰减
  3. 相关性排序

---

## 完整技术术语表

| 英文术语 | 中文 | 说明 |
|---------|------|------|
| Context Engineering | 上下文工程 | 自动化管理 LLM 输入上下文的技术 |
| Prompt Engineering | 提示词工程 | 手动设计 LLM 输入格式 |
| In Context Learning (ICL) | 上下文学习 | 通过输入示例影响模型输出 |
| Observation Masking | 观察掩码 | 将工具输出替换为占位符 |
| Memory Compaction | 记忆压缩 | 压缩历史记录减少 token 占用 |
| Agentic CE (ACE) | 自主上下文工程 | 让 LLM 自主管理上下文 |
| Context Rot | 上下文腐化 | 上下文过长导致信息丢失 |
| Lost in the Middle | 中间丢失效应 | 模型更关注首尾忽略中间 |
| RAG | 检索增强生成 | 从外部知识库检索信息注入上下文 |
| Subagent | 子代理 | 自主执行子任务的 Agent 模块 |
| OpenClaw | 小龙虾框架 | 李宏毅团队的 AI Agent 框架 |
| Computer Use | 计算机操作 | AI 通过坐标定位操作 GUI |
| Scaling Law | 扩展定律 | Agent 数量与任务质量的关系 |

---

## 引用论文完整清单（从幻灯片 OCR 提取 + arXiv API 查证）

> 共 33 篇 arXiv 论文 + 多个博客/网站链接，以下为从视频幻灯片中提取的完整列表。

### ArXiv 论文（按 ID 排序）

| # | arXiv ID | 论文标题 | 课程相关主题 |
|---|----------|---------|------------|
| 1 | [2205.11916](https://arxiv.org/abs/2205.11916) | Large Language Models are Zero-Shot Reasoners | Prompt Engineering / Chain-of-Thought |
| 2 | [2206.03931](https://arxiv.org/abs/2206.03931) | Learning to Generate Prompts for Dialogue Generation through Reinforcement Learning | Prompt 自动生成 |
| 3 | [2304.03442](https://arxiv.org/abs/2304.03442) | **Generative Agents: Interactive Simulacra of Human Behavior** | 斯坦福小镇实验 / 记忆三维度排序 |
| 4 | [2307.03172](https://arxiv.org/abs/2307.03172) | **Lost in the Middle: How Language Models Use Long Contexts** | Lost in the Middle 效应 / Context Rot |
| 5 | [2308.15022](https://arxiv.org/abs/2308.15022) | Recursively Summarizing Enables Long-Term Dialogue Memory in Large Language Models | 递归摘要 / 长期记忆 |
| 6 | [2309.03409](https://arxiv.org/abs/2309.03409) | Large Language Models as Optimizers | LLM 作为优化器 |
| 7 | [2310.03128](https://arxiv.org/abs/2310.03128) | MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use | Tool RAG / 工具挑选 |
| 8 | [2312.16171](https://arxiv.org/abs/2312.16171) | Principled Instructions Are All You Need for Questioning LLaMA-1/2, GPT-3.5/4 | Prompt Engineering 技巧 |
| 9 | [2406.07155](https://arxiv.org/abs/2406.07155) | Scaling Large Language Model-based Multi-Agent Collaboration | Multi-Agent 协作扩展定律 |
| 10 | [2406.08747](https://arxiv.org/abs/2406.08747) | **StreamBench: Towards Benchmarking Continuous Improvement of Language Agents** | Streaming ICL / Appier 研究 |
| 11 | [2409.04109](https://arxiv.org/abs/2409.04109) | **Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers** | AI 写论文 / 创意研究 |
| 12 | [2501.01652](https://arxiv.org/abs/2501.01652) | MIRAGE: Exploring How Large Language Models Perform in Complex Social Interactive Environments | 狼人杀 AI 实验 |
| 13 | [2501.16214](https://arxiv.org/abs/2501.16214) | Provence: efficient and robust context pruning for retrieval-augmented generation | Context 剪枝 / RAG 优化 |
| 14 | [2502.11271](https://arxiv.org/abs/2502.11271) | OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning | Tool RAG / 工具框架 |
| 15 | [2502.12110](https://arxiv.org/abs/2502.12110) | A-MEM: Agentic Memory for LLM Agents | 自主记忆管理 |
| 16 | [2504.19413](https://arxiv.org/abs/2504.19413) | Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | 长期记忆系统 |
| 17 | [2505.03275](https://arxiv.org/abs/2505.03275) | RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation | Tool RAG + MCP |
| 18 | [2505.06120](https://arxiv.org/abs/2505.06120) | LLMs Get Lost In Multi-Turn Conversation | 多轮对话信息丢失 |
| 19 | [2506.01056](https://arxiv.org/abs/2506.01056) | **MCP-Zero: Active Tool Discovery for Autonomous LLM Agents** | 过滤：按需加载工具 |
| 20 | [2506.06326](https://arxiv.org/abs/2506.06326) | Memory OS of AI Agent | Agent 记忆操作系统 |
| 21 | [2508.21433](https://arxiv.org/abs/2508.21433) | **The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management** | Observation Masking vs LLM Summary |
| 22 | [2509.23586](https://arxiv.org/abs/2509.23586) | Reducing Cost of LLM Agents with Trajectory Reduction | Agent 轨迹压缩 |
| 23 | [2510.00615](https://arxiv.org/abs/2510.00615) | **ACON: Optimizing Context Compression for Long-horizon LLM Agents** | 反馈机制提升压缩质量 |
| 24 | [2510.04618](https://arxiv.org/abs/2510.04618) | **Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models** | ACE 核心论文 / Generator-Reflector-Curator |
| 25 | [2510.06727](https://arxiv.org/abs/2510.06727) | Scaling LLM Multi-turn RL with End-to-end Summarization-based Context Management | RL 训练 Agent 自主压缩 |
| 26 | [2510.11967](https://arxiv.org/abs/2510.11967) | Scaling Long-Horizon LLM Agent via Context-Folding | Context Folding 技术 |
| 27 | [2510.24699](https://arxiv.org/abs/2510.24699) | **AgentFold: Long-Horizon Web Agents with Proactive Context Management** | 压缩时机 / 何时 Fold |
| 28 | [2512.24601](https://arxiv.org/abs/2512.24601) | **Recursive Language Models** | RLM / 无限长 Context 突破 |
| 29 | [2601.12323](https://arxiv.org/abs/2601.12323) | MARO: Learning Stronger Reasoning from Social Interaction | 社交 RL → 推理能力迁移 |
| 30 | [2601.16746](https://arxiv.org/abs/2601.16746) | SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents | 代码 Agent 上下文剪枝 |
| 31 | [2602.07432](https://arxiv.org/abs/2602.07432) | The Moltbook Illusion: Separating Human Influence from Emergent Behavior in AI Agent Societies | AI 社交行为 / Moltbook 平台 |
| 32 | [2602.13284](https://arxiv.org/abs/2602.13284) | Agents in the Wild: Safety, Society, and the Illusion of Sociality on Moltbook | AI 社交自主性 |
| 33 | [2602.17221](https://arxiv.org/abs/2602.17221) | From Labor to Collaboration: A Methodological Experiment Using AI Agents to Augment Research Perspectives in Taiwan's Humanities and Social Sciences | AI 辅助人文社科研究 |

### 其他技术报告

| 资源 | 链接 | 说明 |
|------|------|------|
| Gemini 1.5 技术报告 | [PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf) | 卡拉蒙语零样本翻译实验 |

### 博客文章 & 网站

| 标题/来源 | 链接 | 课程相关 |
|----------|------|---------|
| Manus: Context Engineering for AI Agents | [manus.im](https://manus.im/blog/Context-Engineering-for-Al-Agents-Lessons-from-Building-Manus) | Context Engineering 定义来源 |
| Context Rot: How Increasing Input Tokens Impacts LLM Performance | [research.trychroma.com](https://research.trychroma.com/context-rot) | Context Rot 现象 |
| The 100x Research Institution | [freesystems.substack.com](https://freesystems.substack.com/p/the-100x-research-institution) | AI 对学术研究的影响 |
| Benchmarking Multi-Agent Architectures | [blog.langchain.com](https://blog.langchain.com/benchmarking-multi-agent-architectures/) | Multi-Agent 性能对比 |
| Summarization for Monitoring | [alignment.anthropic.com](https://alignment.anthropic.com/2025/summarization-for-monitoring/) | LLM 摘要的信息损失 |
| Long Context LLMs | [artfish.ai](https://www.artfish.ai/p/long-context-llms) | 长上下文模型对比 |
| Long Context Blog | [databricks.com](https://www.databricks.com/blog/long-context-) | DataBricks 长上下文实验 |
| Introducing ChatGPT Agent | [openai.com](https://openai.com/zh-Hant/index/introducing-chatgpt-agent/) | ChatGPT Agent 介绍 |
| Claude 3.5 Models & Computer Use | [anthropic.com](https://www.anthropic.com/news/3-5-models-and-computer-use) | Claude Computer Use 技术 |
| Claude System Prompt | [docs.anthropic.com](https://docs.anthropic.com/en/release-notes/system-prompts#august-5-2025) | Claude Opus 4.1 System Prompt 展示 |
| ChatGPT Tips Analysis | [minimaxir.com](https://minimaxir.com/2024/02/chatgpt-tips-analysis/) | Prompt 技巧分析 |

### GitHub 仓库

| 项目 | 链接 | 说明 |
|------|------|------|
| ChatDev | [github.com/OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev) | Multi-Agent 协作开发系统 |
| AutoResearch | [github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch) | Karpathy 的自动化研究工具 |
| vbm-replication | [github.com/andybhall/vbm-replication-](https://github.com/andybhall/vbm-replication-) | Andrew Hall 论文复现代码 |
| StreamBench | [stream-bench.github.io](https://stream-bench.github.io/) | Appier 的 Streaming ICL 基准 |

### 视频/平台链接

| 资源 | 链接 | 说明 |
|------|------|------|
| 一堂课搞懂 AI Agent 的原理（前置课程） | [youtu.be/M2Yg1kwPpts](https://youtu.be/M2Yg1kwPpts?si=Dw3UvnKQTITxNdci) | P4 开头推荐的先修课 |
| 下次上课前预习视频 | [youtu.be/8iFvVM7WUUs8](https://youtu.be/8iFvVM7WUUs8) | P3 末尾提到的预习 |
| 蝦說 AI (小金老師) | [youtube.com/@SpeechLab-m7o](https://www.youtube.com/@SpeechLab-m7o) | AI 自主制作影片实验 |
| Agents4Science 2025 | [agents4science.stanford.edu](https://agents4science.stanford.edu/) | AI 写论文 + AI 审论文的会议 |
| Werewolf AI 平台 | [werewolf.foaster.ai](https://werewolf.foaster.ai/) | AI 狼人杀实验平台 |
| Moltbook 平台 | [moltbook.com](https://www.moltbook.com/) | AI 社交行为观察平台 |
| TAICA 台灣人工智慧課程協會 | [taicatw.net](https://taicatw.net/fall-114/) | 课程信息 |

---

## 转录技术说明

本文档使用以下技术栈完成视频 → 文字 → 总结的全流程：

```bash
# 1. 安装工具
brew install yt-dlp ffmpeg

# 2. 下载音频（B站视频合集）
yt-dlp --no-playlist -f "bestaudio[ext=m4a]/bestaudio" \
  -o "/tmp/bilibili_audio/p1.m4a" \
  "https://www.bilibili.com/video/BV1D2wVzLELU?p=1"

# 3. 转换为 WAV (16kHz mono)
ffmpeg -i p1.m4a -ar 16000 -ac 1 -f wav p1.wav -y

# 4. 本地 Whisper 转录（whisper.cpp large-v3-turbo）
whisper-cli -m ggml-large-v3-turbo.bin -l zh -otxt -of p1_transcript -f p1.wav
# 53分钟音频 → 3分钟转录（M3 Pro Metal 加速）

# 5. AI 总结（Summarize CLI + Qwen3-235B）
cat p1_transcript.txt | summarize - --model qwen --plain --length long \
  --prompt "详细笔记式总结..."
```

### 性能数据

| 步骤 | P1 (53min) | P2 (22min) | P3 (24min) | P4 (110min) |
|------|-----------|-----------|-----------|------------|
| 音频下载 | 4s | 3s | 5s | 12s |
| WAV 转换 | 2s | 0.8s | 0.9s | 3.7s |
| Whisper 转录 | 183s | 79s | 82s | 379s |
| Qwen 总结 | 26s | 18s | 24s | 28s×2 |

> whisper 模型: large-v3-turbo (1.5GB)
> 总结模型: Qwen3-235B-A22B (via HAI 平台)
