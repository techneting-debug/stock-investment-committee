# 股票投委会 · Stock Investment Committee

一个面向 Codex 的持仓决策 Skill。它不只总结公司资料，而是让八种投资框架独立立论，由机构评分官统一证据口径，经过三轮多空辩论后，由主席给出具体到价格、股数和基本面触发条件的行动方案。

> 本项目用于研究与决策辅助，不保证收益，也不构成针对任何人的持牌投资顾问服务。席位仅模拟相关投资者公开方法论，不代表本人观点、持仓、建议或背书。

## 它解决什么问题

- 用户只说“分析某股票”时，先收集股票、股数、成本和仓位比例四项信息。
- 新闻官只使用法定披露、监管机构、公司公告、主流媒体和可追溯行业资料。
- 八个风格席位独立给出多空证据，避免所有角色机械赞同。
- 强制展示公司质量、盈利质量、估值与操作三轮辩论。
- 统一采用 100 分标准，由评分官给出中位数、分歧和综合分。
- 对已有持仓给出分档买点、卖点、交易股数、交易后持股和基本面否决条件。
- 用户需要时生成自包含、响应式 HTML，桌面端右栏显示辩论过程。

## 投委会席位

正式投票席位包括：段永平席、巴菲特席、芒格席、林园席、张磊席、但斌席、葛卫东席、杨怀定席、机构评分官和投委会主席。新闻官为非投票支持角色，拥有重大风险警报和投资论文重审职责。

角色名称用于标记公开方法论视角，不虚构人物原话、实时观点或私人持仓。

## 安装

在 Codex 中直接要求：

```text
请从 GitHub 仓库 OWNER/stock-investment-committee 的
skills/stock-investment-committee 路径安装这个技能。
```

也可使用 Codex 自带的安装脚本：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo OWNER/stock-investment-committee \
  --path skills/stock-investment-committee
```

将 `OWNER` 替换为实际 GitHub 用户名或组织名。安装完成后，在下一轮对话中使用。

## 使用

显式调用：

```text
$stock-investment-committee 分析新洁能
```

一次提供完整信息：

```text
使用股票投委会分析新洁能（605111.SH）：
持有 1700 股，成本 59 元，占家庭可投资资产 4.73%。
请给出当前动作、分档买卖方案和 HTML 阅读版。
```

如果信息不完整，技能会优先询问：

```text
股票名称/代码：
持股数量：
持股成本：
持仓比例：
```

## 输出内容

1. 主席结论
2. 持仓测算
3. 新闻官简报
4. 核心经营与财务数据
5. 十席评分
6. 三轮多空辩论
7. 悲观、基准、乐观估值
8. 具体买卖行动表
9. 持有条件与基本面否决条件
10. 主席最终决议

价格区间是基于估值和经营条件的决策区间，不是对短期股价的保证或预测。

## 数据与隐私

- 优先使用交易所、法定披露、公司投资者关系页面和监管信息。
- 财务关键值原则上至少交叉验证两个独立来源。
- 微博、头条、论坛、股吧和聊天截图只作为待核查线索，不能直接进入评分。
- Skill 不需要账户密钥，也不会主动连接券商或执行交易。
- 不要在问题、报告或仓库 issue 中提交账户号码、身份信息或 API 密钥。

## 仓库结构

```text
skills/stock-investment-committee/
├── SKILL.md
├── agents/openai.yaml
├── scripts/financial_rigor.py
└── evals/evals.json
```

`financial_rigor.py` 只依赖 Python 标准库，用于市值、盈亏、估值、交叉验证和三情景计算。

## 本地验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/stock-investment-committee

python3 skills/stock-investment-committee/scripts/financial_rigor.py \
  position --shares 1700 --cost 59 --price 55.15
```

结构检查器需要本地 Python 环境提供 PyYAML；缺少时可在装有该依赖的 Codex 开发环境中执行，不影响技能日常调用。

## 版本策略

- `0.1.x`：规则、提示词和兼容性修订
- `0.x.0`：新增行业框架、报告形态或席位能力
- `1.0.0`：经过跨行业、跨市场的稳定评测后发布

## 许可证

[MIT License](LICENSE)
