# 🎮 技能系统完整索引

## 📂 文件结构

```
data/skills/
├── base/                    # 基础模板（9个）
│   ├── _base.yaml          # 根模板
│   ├── fire.yaml           # 火系模板
│   ├── water.yaml          # 水系模板
│   ├── lightning.yaml      # 雷系模板
│   ├── poison.yaml         # 毒系模板
│   ├── blood.yaml          # 血系模板
│   ├── spirit.yaml         # 精神系模板
│   ├── physical.yaml       # 物理战技模板
│   └── support.yaml        # 辅助技能模板
│
├── combat/                  # 物理战技（4个）
│   ├── basic_attack.yaml   # 普通攻击 ✅
│   ├── armor_shatter.yaml  # 破甲斩
│   ├── lacerate.yaml       # 撕裂
│   └── power_strike.yaml   # 重击
│
├── fire/                    # 火系法术（2个）
│   ├── flame_strike.yaml   # 火焰冲击
│   └── fireball.yaml       # 火球术
│
├── water/                   # 水系法术（2个）
│   ├── frost_arrow.yaml    # 寒冰箭
│   └── ice_shield.yaml     # 冰盾术
│
├── lightning/               # 雷系法术（2个）
│   ├── thunder_strike.yaml # 雷霆一击
│   └── chain_lightning.yaml # 连锁闪电
│
├── poison/                  # 毒系法术（3个）
│   ├── poison_dart.yaml    # 剧毒飞镖
│   ├── poison_mist.yaml    # 毒雾术
│   └── venom_fang.yaml     # 毒牙
│
├── blood/                   # 血系法术（2个）
│   ├── blood_claw.yaml     # 血爪
│   └── blood_sacrifice.yaml # 血祭术
│
├── spirit/                  # 精神系法术（5个）
│   ├── curse_weakness.yaml # 虚弱诅咒
│   ├── silence.yaml        # 沉默术
│   ├── immobilize.yaml     # 定身术
│   ├── blind.yaml          # 致盲术
│   └── curse_of_pain.yaml  # 痛苦诅咒
│
└── support/                 # 辅助技能（6个）
    ├── sword_aura.yaml     # 剑气护体
    ├── berserk.yaml        # 狂暴
    ├── swift_step.yaml     # 疾风步
    ├── meditation.yaml     # 灵气吐纳
    ├── rejuvenation.yaml   # 回春术
    └── battle_cry.yaml     # 战吼
```

**总计：9个模板 + 26个技能 = 35个文件**

---

## 📊 技能列表（按效果分类）

### 💥 纯伤害技能（3个）
1. **basic_attack** - 普通攻击（无消耗）
2. **fireball** - 火球术（火伤害）
3. **power_strike** - 重击（高伤害+眩晕）

### 🔥 伤害+DoT技能（7个）
4. **flame_strike** - 火焰冲击（火伤害+灼烧）
5. **frost_arrow** - 寒冰箭（水伤害+冰封减速）
6. **thunder_strike** - 雷霆一击（雷伤害+麻痹）
7. **chain_lightning** - 连锁闪电（范围雷伤害+麻痹）
8. **poison_dart** - 剧毒飞镖（毒伤害+中毒DoT）
9. **lacerate** - 撕裂（物理伤害+流血DoT）
10. **venom_fang** - 毒牙（毒伤害+中毒+流血）

### 🛡️ 伤害+Debuff技能（2个）
11. **armor_shatter** - 破甲斩（伤害+破防）
12. **blood_claw** - 血爪（伤害+吸血）

### ☠️ 纯DoT技能（1个）
13. **poison_mist** - 毒雾术（腐蚀DoT+破防）

### 😵 控制技能（3个）
14. **silence** - 沉默术（无法使用技能）
15. **immobilize** - 定身术（眩晕1回合）
16. **blind** - 致盲术（降低命中率）

### 😖 Debuff技能（2个）
17. **curse_weakness** - 虚弱诅咒（降低攻击力）
18. **curse_of_pain** - 痛苦诅咒（受伤增加）

### 🛡️ 防御型Buff（2个）
19. **sword_aura** - 剑气护体（护盾+防御）
20. **ice_shield** - 冰盾术（护盾+防御）

### ⚔️ 攻击型Buff（3个）
21. **berserk** - 狂暴（攻击+吸血）
22. **battle_cry** - 战吼（攻击+暴击）
23. **swift_step** - 疾风步（速度提升）

### 💚 恢复型Buff（2个）
24. **meditation** - 灵气吐纳（灵力回复）
25. **rejuvenation** - 回春术（生命回复）

### 💀 代价型技能（1个）
26. **blood_sacrifice** - 血祭术（超高伤害+消耗生命+虚弱反噬）

---

## 🎯 26个效果全部覆盖

| 效果类型 | 使用技能 | 文件位置 |
|---------|---------|---------|
| `damage` | 所有伤害技能 | - |
| `apply_burn` | flame_strike, fireball | fire/ |
| `apply_frozen` | frost_arrow | water/ |
| `apply_shock` | thunder_strike, chain_lightning | lightning/ |
| `apply_poison` | poison_dart, venom_fang | poison/ |
| `apply_corrosion` | poison_mist | poison/ |
| `apply_bleed` | lacerate, venom_fang | combat/, poison/ |
| `apply_weakness` | curse_weakness, blood_sacrifice | spirit/, blood/ |
| `apply_armor_break` | armor_shatter | combat/ |
| `apply_slow` | (在frozen中) | - |
| `apply_silence` | silence | spirit/ |
| `apply_stun` | immobilize, power_strike | spirit/, combat/ |
| `apply_blind` | blind | spirit/ |
| `apply_curse` | curse_of_pain | spirit/ |
| `apply_qi_drain` | (可自行添加) | - |
| `apply_shield` | sword_aura, ice_shield | support/, water/ |
| `apply_attack_boost` | berserk, battle_cry | support/ |
| `apply_defense_boost` | sword_aura, ice_shield | support/, water/ |
| `apply_speed_boost` | swift_step | support/ |
| `apply_lifesteal` | berserk, blood_claw | support/, blood/ |
| `apply_combo` | (可自行添加) | - |
| `apply_crit_boost` | battle_cry | support/ |
| `apply_evasion` | (可自行添加) | - |
| `apply_reflect` | (可自行添加) | - |
| `apply_qi_regen` | meditation | support/ |
| `apply_hp_regen` | rejuvenation | support/ |
| `apply_immortal_body` | (可自行添加) | - |

---

## 🔄 继承关系图

```
_base (根模板)
├─ physical_combat (物理战技)
│  ├─ basic_attack
│  ├─ armor_shatter
│  ├─ lacerate
│  └─ power_strike
│
├─ fire_magic (火系法术)
│  ├─ flame_strike
│  └─ fireball
│
├─ water_magic (水系法术)
│  ├─ frost_arrow
│  └─ ice_shield
│
├─ lightning_magic (雷系法术)
│  ├─ thunder_strike
│  └─ chain_lightning
│
├─ poison_magic (毒系法术)
│  ├─ poison_dart
│  ├─ poison_mist
│  └─ venom_fang
│
├─ blood_magic (血系法术)
│  ├─ blood_claw
│  └─ blood_sacrifice
│
├─ spirit_magic (精神系法术)
│  ├─ curse_weakness
│  ├─ silence
│  ├─ immobilize
│  ├─ blind
│  └─ curse_of_pain
│
└─ support_skill (辅助技能)
   ├─ sword_aura
   ├─ berserk
   ├─ swift_step
   ├─ meditation
   ├─ rejuvenation
   └─ battle_cry
```

---

## 📝 使用说明

### 1. 创建新技能的步骤

```yaml
# 1. 选择合适的模板
# 2. 创建新文件 data/skills/类型/技能名.yaml
# 3. 使用模板

skills:
  your_skill:
    inherit: "fire_magic"      # 继承火系模板
    
    name: "你的技能"
    desc: "技能描述"
    
    # 覆盖需要修改的参数
    level_formula:
      damage:
        base: 60
        grow: 0.04
    
    # 定义效果
    effects:
      - type: damage
        value: "{level_damage}"
        element: fire
      
      - type: apply_burn
        tick_damage: 15
        duration: 3
    
    # 自定义战斗文本
    battle_text:
      cast:
        - text: "{caster}施展你的技能！"
          delay_percent: 0
```

### 2. 学习条件说明

| 境界 | 等级范围 | 可学技能 |
|------|---------|---------|
| 练气期 | 1-10 | basic_attack, fireball, poison_dart, swift_step, meditation, blind |
| 筑基期 | 11-25 | flame_strike, frost_arrow, ice_shield, armor_shatter, lacerate, poison_mist, venom_fang, blood_claw, curse_weakness, silence, sword_aura, berserk, rejuvenation, battle_cry |
| 金丹期 | 26-40 | thunder_strike, chain_lightning, immobilize, curse_of_pain, blood_sacrifice |

### 3. 效果组合建议

#### 适合PVE（刷怪）
- **高DoT组合**：poison_dart + poison_mist + lacerate
- **爆发组合**：berserk + blood_sacrifice
- **持续输出**：flame_strike + thunder_strike + meditation

#### 适合PVP（对战）
- **控制组合**：silence + immobilize + blind
- **Debuff组合**：curse_weakness + curse_of_pain + armor_shatter
- **生存组合**：sword_aura + ice_shield + rejuvenation

#### 适合BOSS战
- **团队辅助**：battle_cry + berserk + rejuvenation
- **高伤害**：blood_sacrifice + curse_of_pain + armor_shatter
- **安全输出**：frost_arrow + poison_mist + sword_aura

---

## 🎨 扩展建议

### 还缺的效果（可自行添加）

1. **apply_qi_drain** - 灵力流失
   ```yaml
   mana_burn:
     effects:
       - type: apply_qi_drain
         tick_drain: 15
         duration: 4
   ```

2. **apply_combo** - 连击
   ```yaml
   combo_strike:
     effects:
       - type: apply_combo
         chance: 0.3
         duration: 3
   ```

3. **apply_evasion** - 免伤
   ```yaml
   shadow_dance:
     effects:
       - type: apply_evasion
         chance: 0.25
         duration: 3
   ```

4. **apply_reflect** - 反伤
   ```yaml
   thorn_armor:
     effects:
       - type: apply_reflect
         ratio: 0.3
         duration: 4
   ```

5. **apply_immortal_body** - 不灭真身
   ```yaml
   immortal_form:
     effects:
       - type: apply_immortal_body
         duration: 5
   ```

---

## ✅ 完成清单

- [x] 9个基础模板
- [x] 26个具体技能
- [x] 覆盖21/26个效果
- [x] 详细中文注释
- [x] 继承关系清晰
- [ ] 5个特殊效果（需要时添加）

---

**技能系统已完成！** 🎉

所有文件都可以直接使用，复制到对应目录即可。
