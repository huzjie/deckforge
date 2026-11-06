# deckforge — 幻灯片生成智能体零依赖参考实现

> 拆解 IBM Palette 的幻灯片生成范式：**设计/编码两阶段分离 + 合成训练数据 + 可校验修复闭环（repair harness）**，用一个纯 Python、零依赖、可验证的小系统把整套思路跑通。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Zero deps](https://img.shields.io/badge/deps-zero-brightgreen)
![Tests](https://img.shields.io/badge/tests-47%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**一句话**：与其让一个 LLM「直接写一页 PPT」黑盒输出，不如把「大纲 → 设计规格 → 布局渲染 → 程序校验 → 自动修复」拆成五个可证伪的工程步骤，每一步都能被程序检查、被奖励信号驱动。这就是 Palette 报告里「repair harness 在 PresentBench 上平均 +3.5 分」背后的机制，本仓库用几十行确定性代码把它复现出来。

---

## 这个热点背后的技术原理（拆解）

Palette 之所以有效，不是「模型更大」，而是三件事：

1. **设计阶段与编码阶段分离（separate design and coding stages）**。设计阶段只回答「这页要放什么」（元素类型 + 语义目标），编码阶段才回答「放在哪个框里」（bbox）。两者分离后，设计规格可以独立评分、独立修复，还能作为合成训练的监督信号——错误被隔离到单一阶段，而不是糊在一个黑盒输出里。

2. **合成训练数据（synthetic training data）**。真实 deck 的 `(大纲 → 设计规格 → 渲染结果)` 三元组由确定性程序生成，标签零人工成本、无限可扩。本仓库的 `world/corpus.py` 就是这么干的：5 个模板 × 变体 → 20 个大纲，全部可复现。

3. **可校验修复（checked repairs）**。deck 好不好不靠人看，靠程序查：**有没有元素重叠、有没有元素越出它该在的版式带、有没有空页/缺失**。查出来 → 定位到具体元素 → 确定性补丁 → 再校验。因为每一环都是闭式规则，所以「修复增益」是个精确、可重复的数字，不是模糊评分。

本仓库把这三点落成一套**可验证奖励（verifiable reward）**闭环：模型每生成一个元素，程序立刻判「类型对 + 目标对 + 落点对」三条件，全对才给 1 分，幻觉元素（大纲没要的元素）直接 0 分。

---

## 可复用的干货块

### ① 提示词模板：两阶段契约（prompts/system_prompt.md 的浓缩）

```
你是演示工程智能体，分两阶段产出，别合并：
1. 设计阶段：输出设计规格 = 有序 (元素类型, 目标元素) 列表 —— 回答「放什么」
2. 编码阶段：输出布局 = 每元素归一化 bbox —— 回答「放哪」
元素词表（封闭集）：title subtitle bullet image chart table code footer caption
硬规则：一个大纲要点对应一个元素；不许发明元素；元素框不得重叠；每个元素必须在自己的版式带内。
```

### ② 让四项指标「必然单调」的技巧：阈值翻转

这是本仓库最值得抄的工程手法（`core/engine.py`）：

```
对每个 (大纲, 要点) 固定两个阈值 t_design、t_layout ∈ (0,1)；
skill >= 阈值 → 用 oracle 真值；否则 → 独立抛硬币基线。
```

skill 从 0 升到 1 时，越来越多的要点从「随机猜」翻成「oracle 正解」，阶跃函数聚合后必然单调——**单调性是被构造出来的，不是靠训练碰运气**。两个配套铁律：

- 基线必须是**独立抛硬币**，不能是「翻转 oracle」（翻转会恒错，skill=0 起点就错位到 0 而非 ~概率值）；
- 阈值下界用 `1e-6` 而非 `0`，否则 skill=0 时 `0>=0` 提前翻转，破坏「纯基线」语义。

### ③ 修复闭环（repair harness）的确定性补丁

修复只改**垂直位置**、保留元素身份和水平宽度（`training/repair.py`）：越界元素 snap 回它的版式带，重叠的内容元素按 spec 顺序重新堆叠。因为 patch 是确定性的，同一坏 deck 永远得到同一修复结果，「修复增益」可精确复现。

### ④ 确定性渲染 = 可验证的前提

`core/deck.py` 把幻灯片画成**文本网格**（每个元素按类型用不同字符填充其 bbox），种子来自 `md5("<template>:<seed>")`。两次运行同一大纲看到同一真值，才谈得上「可验证奖励」。

---

## 演示

```bash
git clone https://github.com/huzjie/deckforge.git
cd deckforge
python -m deckforge.cli doctor
python -m deckforge.cli bench
```

`doctor` 在 skill=1.0 复现 oracle；`bench` 输出四项单调指标曲线 + 修复增益（实测）：

```
[bench] skill  layout_acc  design_acc  deck_success  score
[bench] 0.00   0.0900       0.0400       0.0000         0.0100
[bench] 0.25   0.2900       0.1400       0.0000         0.0800
[bench] 0.50   0.5400       0.3200       0.0000         0.2400
[bench] 0.75   0.7800       0.5600       0.0000         0.5200
[bench] 1.00   1.0000       1.0000       1.0000         1.0000
[bench] monotone: layout_acc_inc=True, design_acc_inc=True, deck_success_inc=True, score_inc=True
[bench] repair_gain: broken=8 fixed=8 after=0 gain=1.0000
```

## 安装与使用

```bash
python -m deckforge.cli doctor          # 自检：oracle 在 skill=1.0 全部命中
python -m deckforge.cli bench           # 四项单调基准 + 修复增益
python -m deckforge.cli run --deck d00 --skill 1.0   # 单 deck 闭环生成
python -m deckforge.cli repair --n 8    # 修复闭环演示
python -m deckforge.cli serve --port 8431           # 零依赖 HTTP API
make test                                # 47 个单测
```

纯标准库，`pip install` 都省了；`python >= 3.9` 即可。

## 项目结构

```
deckforge/
  core/        deck 渲染 / elements 词表 / embed 语义对齐 / layout / designer / engine
  world/       设计 oracle（闭式真值）+ 确定性语料（合成数据）
  training/    可验证奖励 verifier + 修复闭环 repair + skill 单调训练 trainer
  serving/     零依赖 HTTP API
  tasks/       五项能力声明式注册表
  utils/       确定性 rng / 极简 yaml / 线性代数
tests/         47 单测
prompts/       6 份可直接套用的提示词模板
recipes/       5 份 yaml 配置回退（benchmark/full/minimal/layout/design）
examples/      6 个可运行示例
docs/          9 篇文档（架构 / 渲染 / oracle / 奖励 / 基准 / API / 任务 / 贡献）
deploy/        Docker + docker-compose + Kubernetes + Helm
```

## 五项能力

| 能力 | 指标 | skill 0→1（实测） |
|---|---|---|
| 布局落位（编码阶段） | `layout_acc` | 0.09 → 1.00 |
| 设计规格（设计阶段） | `design_acc` | 0.04 → 1.00 |
| 闭环完成 | `deck_success` | 0.00 → 1.00 |
| 可验证奖励 | `score` | 0.01 → 1.00 |
| 可校验修复 | `repair_gain` | 1.00（坏 deck 全部修好） |

## License

MIT
