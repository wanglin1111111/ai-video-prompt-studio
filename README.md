# ai-video-prompt-studio

模型无关的 AI 视频提示词工程工作室。对标 YouMind Skills Awards 冠军作品（即梦 Seedance2.0 Prompt Gen & Opt，3871 安装）的超越重构版。

## 相对冠军作品的四个超越

| 维度 | 冠军作品 | 本 Skill |
|---|---|---|
| 模型 | 锁定 Seedance 2.0（平台已出 2.5，单模型技能随版本贬值） | 语法层与模型解耦；6 系模型方言卡，新模型只加一卡 |
| 工作流 | 止步单镜头提示词 | 剧本→分镜表→圣经系统→逐镜提示词→修订环，解决跨镜一致性 |
| 验证 | 无 | `scripts/validate.py` 六维机器校验 + 双样例断言（good 必过 / bad 必挂） |
| 规范 | — | 对齐 agentskills.io：frontmatter 触发词+反例、progressive disclosure、body<500 行 |

保留冠军优点：中文原生优化、六要素结构、场景化参数建议、模板库（以决策表+样例形式存在）。

## 安装

复制本目录到 `~/.agents/skills/`（或你的 Skill 加载路径）即可。

## 自检

```bash
python scripts/validate.py tests/sample_good.json   # 必须 exit 0
python scripts/validate.py tests/sample_bad.json    # 必须 exit 1
```

## 结构

```
SKILL.md                          工作流入口（四层架构 + 标准流程 + 硬规则）
references/grammar.md             六要素决策表（景别/运镜/光影/风格），模型无关
references/model-cards.md         Seedance/Sora/Veo/Kling/Runway/PixVerse 方言卡
references/storyboard-continuity.md  圣经系统、分镜表 schema、修订环
references/gotchas.md             跨模型真实坑位（负面词邀请函、运镜语义税…）
scripts/validate.py               分镜表六维校验器（exit 0/1/2）
tests/sample_good.json            通过基准
tests/sample_bad.json             拦截基准（8 类缺陷）
```
