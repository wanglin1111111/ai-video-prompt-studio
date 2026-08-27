---
name: ai-video-prompt-studio
description: 模型无关的AI视频提示词工程工作室：把脚本或想法变成机器可校验的分镜表(shot list)——逐镜六要素提示词、角色/场景圣经系统保证跨镜一致性、各模型方言卡(Seedance/Sora2/Veo3/Kling可灵/Runway Gen-4/PixVerse)适配时长画幅参数。Use whenever the user wants 文生视频/图生视频 prompts, 分镜提示词, 角色一致性 across shots, choosing duration/aspect/motion params, adapting prompts between video models, or QA-ing an existing shot list. Not for: 纯图片生成提示词、已有 footage 的剪辑、字幕翻译。触发词:视频提示词、分镜、文生视频、图生视频、首尾帧、角色一致性、镜头语言、Seedance、Sora、可灵、Veo。
license: MIT
metadata:
  version: "1.0.0"
  author: wanglin1111111
  provenance: "对标 YouMind Skills Awards 冠军作品(即梦Seedance2.0 Prompt Gen & Opt)的超越重构：单模型→多模型方言卡、单镜头→全流程分镜、零验证→validate.py+双样例"
---

# AI 视频提示词工程工作室

把"一个想法/一版脚本"变成"一组可直接投喂视频模型、镜头间相互连贯、且经过机器校验的提示词"。与单模型提示词生成器的根本区别：**语法层、方言层、工作流层、验证层四层分离**——换模型不改语法，加模型只加一张方言卡。

## 四层架构（先读懂再动手）

```
脚本/想法
  │
  ▼
① 语法层 references/grammar.md     六要素决策表：主体/场景/镜头/光影/风格/质量
  │                                  （与模型无关，一次学会处处使用）
  ▼
② 方言层 references/model-cards.md 每模型一张卡：参数集、语言偏好、首尾帧、已知怪癖
  │                                  （换模型=换卡；卡上标 volatile 的字段必须现场核实）
  ▼
③ 工作流层 references/storyboard-continuity.md
  │     剧本→分镜表→圣经系统(角色/场景/道具)→逐镜提示词→修订环
  ▼
④ 验证层 scripts/validate.py       机器校验分镜表：六要素齐全、圣经ID可解析、矛盾检测
```

## 标准工作流

1. **明确四输入**：故事梗概（1-3 句也行）、目标模型（决定方言卡）、时长与画幅约束、横竖屏用途。缺哪个就问哪个，不要猜。
2. **建圣经**：从梗概提取角色/场景/道具，登记为 `CHAR-1`/`SCENE-1`/`PROP-1` 编号（模板见工作流层）。跳过这一步是跨镜不一致的头号原因。
3. **拆分镜表**：按"一镜一动作一信息"原则切分；每镜填六要素 + 时长 + 画幅 + 模型。参考 `references/grammar.md` 的决策表选景别/运镜。
4. **写逐镜提示词**：先中文母版，按方言卡需要再出英文版；首尾帧需求在分镜表标注 `i2v_start`/`i2v_end` 字段。
5. **机器校验**（不可跳过）：
   ```bash
   python scripts/validate.py shotlist.json          # exit 0=通过 / 1=有缺陷 / 2=文件错误
   python scripts/validate.py tests/sample_good.json # 自检基准，应恒为 0
   ```
6. **交付**：给用户分镜表 JSON + 一张可读版表格（镜号/景别/运镜/画面/台词/时长），并注明哪些参数属于 volatile 字段、投喂前要在平台 UI 上复核。

## 硬规则

- **圣经先行**：第二镜起必须引用已登记的 CHAR/SCENE/PROP 编号，validate.py 会拦截悬空引用。
- **volatile 字段不进成品**：时长档位、分辨率、价格随平台版本漂移。方言卡中标 `volatile` 的值只用于初稿建议，交付前必须让用户在当前 UI 核实——把"参数过期"当作常态来设计。
- **矛盾即失败**：同一镜提示词里"固定机位"与推拉摇移共存、景别与运镜物理冲突（大远景+特写细节要求）、时长超出模型档位，都按缺陷处理，不靠模型自觉。
- **负面提示词按卡而定**：有的模型支持 negative prompt 字段，有的只会把它画进画面。写之前查方言卡，不要通用。
- **双样例纪律**：改 validate.py 或语法规则时，`tests/sample_good.json` 必须保持 exit 0、`tests/sample_bad.json` 必须保持 exit 1，缺一不可——"通过"必须由"失败样例被拦截"来证明。

## 深入阅读（按需加载，勿一次全读）

| 文件 | 何时读 |
|---|---|
| `references/grammar.md` | 每次拆分镜前；六要素决策表与镜头语言速查 |
| `references/model-cards.md` | 确定目标模型后；方言适配与参数档位 |
| `references/storyboard-continuity.md` | 多镜头项目；圣经系统与修订环模板 |
| `references/gotchas.md` | 出片质量异常时；跨模型真实坑位速查 |
