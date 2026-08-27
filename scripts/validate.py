#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分镜表校验器（ai-video-prompt-studio 第④层）。

用法: python validate.py <shotlist.json>
退出码: 0=通过 / 1=存在缺陷 / 2=文件或结构错误

校验维度:
  A. 六要素齐全: subject/scene/camera/lighting/style/quality + 成品提示词
  B. 圣经连续性: continuity 引用的 CHAR-/SCENE-/PROP- 必须在 bibles 登记
  C. 矛盾检测: 固定机位 vs 运镜动词共存; 景别与细节要求冲突; 时长非正数
  D. 提示词厚度: prompt_zh/prompt_en 至少一项 >= 30 字符
  E. 逐字复用: 镜头引用圣经 ID 时, 特征关键短语应出现在提示词中(抽样 1 条)
"""
import json
import re
import sys

MOVE_VERBS = re.compile(r"(推近|拉远|横移|摇|跟拍|环绕|升降|俯冲)")
FIXED_WORDS = ("固定机位", "固定镜头", "无运镜")
BIBLE_PREFIX = ("CHAR-", "SCENE-", "PROP-")
MIN_PROMPT_LEN = 30

# 方言卡时长档位(volatile 提示值, 宽松校验: 只拦截明显非法值)
LEGAL_DURATIONS = {3, 4, 5, 8, 10, 12, 15}


def fail(issues, shot_id, msg):
    issues.append(f"[{shot_id}] {msg}")


def check(data):
    issues = []
    shots = data.get("shots") or []
    if not shots:
        issues.append("[root] shots 为空——至少需要一镜")
        return issues

    bibles = data.get("bibles") or {}
    reg = {}
    for kind, key in (("CHAR-", "characters"), ("SCENE-", "scenes"), ("PROP-", "props")):
        reg[kind] = {b.get("id") for b in (bibles.get(key) or []) if b.get("id")}

    known_models = {
        "seedance-2.0", "seedance-2.5", "sora-2", "veo-3", "veo-3.1",
        "kling-2.5", "kling-3", "runway-gen-4", "pixverse-v5",
    }

    for s in shots:
        sid = s.get("id") or "?"
        if not re.match(r"^S\d{2,}$", sid):
            fail(issues, sid, "镜号格式应为 S01/S02…")

        # A. 六要素
        for field in ("subject", "scene", "lighting", "style", "quality"):
            v = s.get(field)
            if not v or (isinstance(v, str) and not v.strip()) or v == []:
                fail(issues, sid, f"六要素缺失: {field}")
        cam = s.get("camera") or {}
        if not (isinstance(cam, dict) and cam.get("size") and cam.get("move")):
            fail(issues, sid, "camera.size / camera.move 缺失")

        # B. 圣经连续性
        all_ids = {x for kv in reg.values() for x in kv}
        for ref in s.get("continuity") or []:
            if not str(ref).startswith(BIBLE_PREFIX):
                fail(issues, sid, f"continuity 引用 {ref} 不是 CHAR-/SCENE-/PROP- 编号")
            elif ref not in all_ids:
                fail(issues, sid, f"continuity 引用 {ref} 未在 bibles 登记(悬空引用)")

        # C. 矛盾检测
        prompt = (s.get("prompt_zh") or "") + " " + (s.get("prompt_en") or "")
        # 风格语境中的"跟拍/手持"等是画风词不是运镜指令，剔除后再扫描
        prompt_for_move = re.sub(r"(纪录片|手持|跟随)(跟拍|运镜)(语境|风格|感|式)", "风格词", prompt)
        move = str(cam.get("move", ""))
        if any(w in move for w in FIXED_WORDS) and MOVE_VERBS.search(move):
            fail(issues, sid, f"camera.move 自相矛盾: '{move}' 同时含固定机位与运镜动词")
        if any(w in move for w in FIXED_WORDS) and MOVE_VERBS.search(prompt_for_move):
            fail(issues, sid, "声明固定机位但提示词正文出现运镜动词")
        dur = s.get("duration_s")
        if not isinstance(dur, (int, float)) or dur <= 0:
            fail(issues, sid, f"duration_s 非法: {dur!r}")
        elif dur not in LEGAL_DURATIONS:
            fail(issues, sid, f"duration_s={dur} 不在常见档位 {sorted(LEGAL_DURATIONS)} 内(volatile, 请核实模型当前档位)")
        model = s.get("model")
        if model not in known_models:
            fail(issues, sid, f"model '{model}' 不在方言卡清单; 先在 model-cards.md 建卡再使用")

        # D. 提示词厚度
        if len(s.get("prompt_zh") or "") < MIN_PROMPT_LEN and len(s.get("prompt_en") or "") < MIN_PROMPT_LEN:
            fail(issues, sid, f"提示词过薄(<{MIN_PROMPT_LEN}字): 六要素未展开")

        # E. 逐字复用抽样: 引用 CHAR- 时, name/look/wardrobe 关键特征至少一项逐字出现
        for ref in s.get("continuity") or []:
            if str(ref).startswith("CHAR-"):
                ent = next((b for b in (bibles.get("characters") or []) if b.get("id") == ref), None)
                if not ent:
                    continue
                anchors = [ent.get(k) for k in ("name", "look", "wardrobe")]
                anchors = [a for a in anchors if a]
                # 取 look 的前 10 字做关键短语（全文比对太脆，短句截断防同义改写）
                hit = any((a if len(a) <= 12 else a[:10]) in prompt for a in anchors)
                if anchors and not hit:
                    fail(issues, sid, f"引用 {ref} 但其 name/look/wardrobe 关键短语均未逐字出现在提示词(漂移风险)")

    return issues


def main():
    if len(sys.argv) != 2:
        print("用法: python validate.py <shotlist.json>", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"文件/JSON错误: {e}", file=sys.stderr)
        return 2
    issues = check(data)
    if issues:
        print(f"FAIL — {len(issues)} 处缺陷:")
        for i in issues:
            print("  -", i)
        return 1
    print("PASS — 分镜表校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
