# OGG 音轨号写入测试方案

**创建时间**：2026-01-30  
**版本**：v1.0  
**状态**：📋 待确认  
**类型**：测试方案（中文）

---

## 🎯 测试目标

### 主要目标

1. ✅ **验证 OGG 文件音轨号写入**：确认 `TRACKNUMBER` 标签正确写入
2. ✅ **验证 FLAC 文件音轨号写入**：确认 `TRACKNUMBER` 标签正确写入（补充阶段）
3. ✅ **验证音轨号检查逻辑**：确认已经有音轨号的文件不会被覆盖
4. ✅ **验证文件名解析**：确认所有格式的文件名都能正确解析

---

## 🧪 测试计划

### 测试 1：音轨号提取验证

**目的**：验证 `extract_track_number_from_filename()` 函数能正确提取所有格式的音轨号

**测试文件**：
- ✅ `01 B_O_K.ogg` → 预期：`1`
- ✅ `02 无言无语.ogg` → 预期：`2`
- ✅ `03 好人 (Radio Edit).ogg` → 预期：`3`
- ✅ `04 Erica.ogg` → 预期：`4`
- ✅ `05 情歌.flac` → 预期：`5`
- ✅ `06 男人 KTV.ogg` → 预期：`6`
- ✅ `07 一句.ogg` → 预期：`7`
- ✅ `08 Volar.ogg` → 预期：`8`
- ✅ `09 未输.ogg` → 预期：`9`
- ✅ `10 头条新闻.ogg` → 预期：`10`
- ✅ `11 情永落.ogg` → 预期：`11`
- ✅ `12 我不是好人.ogg` → 预期：`12`
- ✅ `13 贝壳.ogg` → 预期：`13`
- ✅ `14 运.ogg` → 预期：`14`
- ✅ `歌名.flac` → 预期：`None`（未找到）
- ✅ `15. 另一首歌.flac` → 预期：`15`

**测试方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
python -c "
from metadata_utils import extract_track_number_from_filename

test_files = [
    '01 B_O_K.ogg',
    '02 无言无语.ogg',
    '03 好人 (Radio Edit).ogg',
    '04 Erica.ogg',
    '05 情歌.flac',
    '06 男人 KTV.ogg',
    '07 一句.ogg',
    '08 Volar.ogg',
    '09 未输.ogg',
    '10 头条新闻.ogg',
    '11 情永落.ogg',
    '12 我不是好人.ogg',
    '13 贝壳.ogg',
    '14 运.ogg',
    '歌名.flac',
    '15. 另一首歌.flac'
]

print('音轨号提取验证:')
print('='*60)
for file in test_files:
    track_num = extract_track_number_from_filename(file)
    result = 'OK' if track_num is not None else 'SKIP'
    print(f'{file:50s} -> {track_num:5}  [{result}]')
print('='*60)
" 2>&1
```

**预期结果**：
- ✅ 所有带数字的文件名都能正确提取音轨号
- ✅ 不带数字的文件名返回 `None`
- ✅ 带前导零的文件名能正确提取（如 `01` → `1`）

---

### 测试 2：OGG 文件音轨号写入验证

**目的**：验证 OGG 文件的 `TRACKNUMBER` 标签能正确写入

**测试目录**：`G:\QQMusic\Decrypted\VipSongsDownload\侧田\From Justin (Collection Of His First 3 Years)`

**测试文件**：
- ✅ `01 B_O_K.ogg` → 预期：写入 `TRACKNUMBER=1`
- ✅ `02 无言无语.ogg` → 预期：写入 `TRACKNUMBER=2`
- ✅ `03 好人 (Radio Edit).ogg` → 预期：写入 `TRACKNUMBER=3`
- ✅ `04 Erica.ogg` → 预期：写入 `TRACKNUMBER=4`
- ✅ `06 男人 KTV.ogg` → 预期：写入 `TRACKNUMBER=6`
- ✅ `07 一句.ogg` → 预期：写入 `TRACKNUMBER=7`
- ✅ `08 Volar.ogg` → 预期：写入 `TRACKNUMBER=8`
- ✅ `09 未输.ogg` → 预期：写入 `TRACKNUMBER=9`
- ✅ `10 头条新闻.ogg` → 预期：写入 `TRACKNUMBER=10`
- ✅ `11 情永落.ogg` → 预期：写入 `TRACKNUMBER=11`
- ✅ `12 我不是好人.ogg` → 预期：写入 `TRACKNUMBER=12`
- ✅ `13 贝壳.ogg` → 预期：写入 `TRACKNUMBER=13`
- ✅ `14 运.ogg` → 预期：写入 `TRACKNUMBER=14`

**测试方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)" 2>&1 | grep -E "音轨号|TRACKNUMBER|处理文件"
```

**预期结果**：
```
2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 1/15: 01 B_O_K.ogg
2026-01-30 XX:XX:XX - INFO - 添加年份 (OGG): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (OGG): 1  ← 关键验证点
2026-01-30 XX:XX:XX - INFO - 保存元数据 (OGG): 01 B_O_K.ogg
2026-01-30 XX:XX:XX - INFO - [OK] 01 B_O_K.ogg

2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 2/15: 02 无言无语.ogg
2026-01-30 XX:XX:XX - INFO - 添加年份 (OGG): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (OGG): 2  ← 关键验证点
2026-01-30 XX:XX:XX - INFO - 保存元数据 (OGG): 02 无言无语.ogg
2026-01-30 XX:XX:XX - INFO - [OK] 02 无言无语.ogg

...
```

**验证要点**：
- [ ] 日志显示 `添加音轨号 (OGG): X`
- [ ] 所有 OGG 文件都有音轨号写入日志
- [ ] 没有显示 `未找到音轨号，跳过音轨号写入`

---

### 测试 3：FLAC 文件音轨号写入验证（补充阶段）

**目的**：验证 FLAC 文件的 `TRACKNUMBER` 标签能正确写入（补充阶段）

**测试目录**：`G:\QQMusic\Decrypted\VipSongsDownload\侧田\From Justin (Collection Of His First 3 Years)`

**测试文件**：
- ✅ `05 情歌.flac` → 预期：写入 `TRACKNUMBER=5`

**测试方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)" 2>&1 | grep -E "音轨号|TRACKNUMBER|处理文件.*情歌"
```

**预期结果**：
```
2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 5/15: 05 情歌.flac
2026-01-30 XX:XX:XX - INFO - 添加年份 (FLAC): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (FLAC): 5  ← 关键验证点
2026-01-30 XX:XX:XX - INFO - 嵌入封面 (FLAC)
2026-01-30 XX:XX:XX - INFO - 保存元数据 (FLAC): 05 情歌.flac
2026-01-30 XX:XX:XX - INFO - [OK] 05 情歌.flac
```

**验证要点**：
- [ ] 日志显示 `添加音轨号 (FLAC): X`
- [ ] FLAC 文件有音轨号写入日志
- [ ] 没有显示 `FLAC 文件已经有音轨号: X，跳过写入`（第一次运行）

---

### 测试 4：音轨号检查验证（避免重复写入）

**目的**：验证已经有音轨号的文件不会被覆盖

**测试方法 1**：重复运行（第二次运行）

```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)" 2>&1 | grep -E "音轨号|跳过|已有音轨号"
```

**预期结果**：
```
2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 1/15: 01 B_O_K.ogg
2026-01-30 XX:XX:XX - INFO - 添加年份 (OGG): 2006
2026-01-30 XX:XX:XX - INFO - OGG 文件已经有音轨号: 1，跳过写入  ← 关键验证点
2026-01-30 XX:XX:XX - INFO - 保存元数据 (OGG): 01 B_O_K.ogg
```

**验证要点**：
- [ ] 第二次运行显示 `OGG 文件已经有音轨号: X，跳过写入`
- [ ] 第三次运行也显示 `OGG 文件已经有音轨号: X，跳过写入`
- [ ] 没有显示 `添加音轨号 (OGG): X`（重复写入）

**测试方法 2**：手动验证

```bash
cd /d/WorkDev/qqmusic_decryptor
python -c "
from mutagen.oggvorbis import OggVorbis

# 检查 OGG 文件的 TRACKNUMBER 标签
ogg_file = 'G:/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)/01 B_O_K.ogg'
audio = OggVorbis(ogg_file)

# 检查 TRACKNUMBER 标签
track_number = audio.get('TRACKNUMBER')
print(f'OGG 文件: {ogg_file}')
print(f'TRACKNUMBER 标签: {track_number}')
print(f'TRACKNUMBER 类型: {type(track_number)}')
" 2>&1
```

**预期结果**：
```
OGG 文件: G:/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)/01 B_O_K.ogg
TRACKNUMBER 标签: 1
TRACKNUMBER 类型: <class 'str'>
```

**验证要点**：
- [ ] `TRACKNUMBER` 标签存在
- [ ] `TRACKNUMBER` 标签的值是字符串（`"1"`, `"2"` 等）
- [ ] `TRACKNUMBER` 标签的值正确（与文件名匹配）

---

### 测试 5：批量处理验证

**目的**：验证所有文件都能正确处理

**测试命令**：
```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)" 2>&1 | grep -E "音轨号|总文件数|成功"
```

**预期结果**：
```
==================================================
处理完成
==================================================

总文件数: 15
成功: 15
失败: 0
跳过: 0
==================================================
```

**验证要点**：
- [ ] 总文件数：15（1 FLAC + 14 OGG）
- [ ] 成功数：15（所有文件都正确处理）
- [ ] 失败数：0
- [ ] 跳过数：0（除非文件名没有数字）

---

## 📋 验证清单

### 功能验证

- [ ] **音轨号提取功能**：所有格式的文件名都能正确解析
- [ ] **OGG 音轨号写入**：所有 OGG 文件都正确写入 `TRACKNUMBER` 标签
- [ ] **FLAC 音轨号写入**：所有 FLAC 文件都正确写入 `TRACKNUMBER` 标签（补充阶段）
- [ ] **音轨号检查功能**：已经有音轨号的文件不会被覆盖

### 日志验证

- [ ] **日志显示**：所有操作都有详细日志输出
- [ ] **日志级别**：INFO 级别日志正确显示
- [ ] **日志格式**：日志格式清晰易懂

### 数据验证

- [ ] **元数据写入**：所有文件的元数据都正确写入
- [ ] **数据完整性**：元数据没有丢失或损坏
- [ ] **数据一致性**：元数据与文件名一致

---

## 🚀 测试执行计划

### 阶段 1：音轨号提取验证（计划 1）

**任务**：
- [ ] 运行音轨号提取测试
- [ ] 验证所有格式的文件名都能正确解析
- [ ] 验证返回值类型正确（整数或 None）
- [ ] 记录测试结果

**预期结果**：
- ✅ 所有测试文件都能正确提取音轨号
- ✅ 不带数字的文件名返回 `None`
- ✅ 带前导零的文件名能正确提取（如 `01` → `1`）

---

### 阶段 2：OGG 文件音轨号写入验证（计划 2）

**任务**：
- [ ] 运行 OGG 文件音轨号写入测试
- [ ] 验证所有 OGG 文件都正确写入 `TRACKNUMBER` 标签
- [ ] 验证日志显示 `添加音轨号 (OGG): X`
- [ ] 记录测试结果

**预期结果**：
- ✅ 所有 14 个 OGG 文件都正确写入 `TRACKNUMBER` 标签
- ✅ 日志显示所有文件的音轨号写入过程

---

### 阶段 3：FLAC 文件音轨号写入验证（计划 3）

**任务**：
- [ ] 运行 FLAC 文件音轨号写入测试（补充阶段）
- [ ] 验证 FLAC 文件正确写入 `TRACKNUMBER` 标签
- [ ] 验证日志显示 `添加音轨号 (FLAC): X`
- [ ] 记录测试结果

**预期结果**：
- ✅ 1 个 FLAC 文件正确写入 `TRACKNUMBER` 标签（补充阶段）
- ✅ 日志显示音轨号写入过程

---

### 阶段 4：音轨号检查验证（计划 4）

**任务**：
- [ ] 第二次运行脚本
- [ ] 验证已经有音轨号的文件不会被覆盖
- [ ] 验证日志显示 `OGG 文件已经有音轨号: X，跳过写入`
- [ ] 验证没有重复写入日志

**预期结果**：
- ✅ 第二次运行显示 `OGG 文件已经有音轨号: X，跳过写入`
- ✅ 第三次运行也显示 `OGG 文件已经有音轨号: X，跳过写入`
- ✅ 没有显示 `添加音轨号 (OGG): X`（重复写入）

---

### 阶段 5：批量处理验证（计划 5）

**任务**：
- [ ] 运行批量处理测试
- [ ] 验证所有文件都能正确处理
- [ ] 验证统计信息正确（总文件数、成功数、失败数、跳过数）
- [ ] 记录测试结果

**预期结果**：
- ✅ 总文件数：15（1 FLAC + 14 OGG）
- ✅ 成功数：15（所有文件都正确处理）
- ✅ 失败数：0
- ✅ 跳过数：0

---

## 📊 测试结果记录

### 测试 1：音轨号提取验证

| 文件名 | 预期值 | 实际值 | 状态 |
|--------|--------|--------|------|
| `01 B_O_K.ogg` | `1` | - | ⏸️ 待测试 |
| `02 无言无语.ogg` | `2` | - | ⏸️ 待测试 |
| `03 好人 (Radio Edit).ogg` | `3` | - | ⏸️ 待测试 |
| `04 Erica.ogg` | `4` | - | ⏸️ 待测试 |
| `05 情歌.flac` | `5` | - | ⏸️ 待测试 |
| `06 男人 KTV.ogg` | `6` | - | ⏸️ 待测试 |
| `07 一句.ogg` | `7` | - | ⏸️ 待测试 |
| `08 Volar.ogg` | `8` | - | ⏸️ 待测试 |
| `09 未输.ogg` | `9` | - | ⏸️ 待测试 |
| `10 头条新闻.ogg` | `10` | - | ⏸️ 待测试 |
| `11 情永落.ogg` | `11` | - | ⏸️ 待测试 |
| `12 我不是好人.ogg` | `12` | - | ⏸️ 待测试 |
| `13 贝壳.ogg` | `13` | - | ⏸️ 待测试 |
| `14 运.ogg` | `14` | - | ⏸️ 待测试 |
| `歌名.flac` | `None` | - | ⏸️ 待测试 |
| `15. 另一首歌.flac` | `15` | - | ⏸️ 待测试 |

### 测试 2：OGG 文件音轨号写入验证

| 文件名 | 预期 | 实际 | 状态 |
|--------|------|------|------|
| `01 B_O_K.ogg` | `1` | - | ⏸️ 待测试 |
| `02 无言无语.ogg` | `2` | - | ⏸️ 待测试 |
| `03 好人 (Radio Edit).ogg` | `3` | - | ⏸️ 待测试 |
| `04 Erica.ogg` | `4` | - | ⏸️ 待测试 |
| `06 男人 KTV.ogg` | `6` | - | ⏸️ 待测试 |
| `07 一句.ogg` | `7` | - | ⏸️ 待测试 |
| `08 Volar.ogg` | `8` | - | ⏸️ 待测试 |
| `09 未输.ogg` | `9` | - | ⏸️ 待测试 |
| `10 头条新闻.ogg` | `10` | - | ⏸️ 待测试 |
| `11 情永落.ogg` | `11` | - | ⏸️ 待测试 |
| `12 我不是好人.ogg` | `12` | - | ⏸️ 待测试 |
| `13 贝壳.ogg` | `13` | - | ⏸️ 待测试 |
| `14 运.ogg` | `14` | - | ⏸️ 待测试 |

### 测试 3：FLAC 文件音轨号写入验证

| 文件名 | 预期 | 实际 | 状态 |
|--------|------|------|------|
| `05 情歌.flac` | `5` | - | ⏸️ 待测试 |

### 测试 4：音轨号检查验证

| 运行次数 | 预期日志 | 实际日志 | 状态 |
|---------|----------|----------|------|
| 第一次运行 | `添加音轨号 (OGG): 1` | - | ⏸️ 待测试 |
| 第二次运行 | `OGG 文件已经有音轨号: 1，跳过写入` | - | ⏸️ 待测试 |
| 第三次运行 | `OGG 文件已经有音轨号: 1，跳过写入` | - | ⏸️ 待测试 |

### 测试 5：批量处理验证

| 指标 | 预期值 | 实际值 | 状态 |
|------|--------|--------|------|
| 总文件数 | `15` | - | ⏸️ 待测试 |
| 成功数 | `15` | - | ⏸️ 待测试 |
| 失败数 | `0` | - | ⏸️ 待测试 |
| 跳过数 | `0` | - | ⏸️ 待测试 |

---

## 🎯 成功标准

### 必须满足的条件

1. ✅ **音轨号提取功能**：所有格式的文件名都能正确解析
2. ✅ **OGG 音轨号写入**：所有 OGG 文件都正确写入 `TRACKNUMBER` 标签
3. ✅ **FLAC 音轨号写入**：所有 FLAC 文件都正确写入 `TRACKNUMBER` 标签（补充阶段）
4. ✅ **音轨号检查功能**：已经有音轨号的文件不会被覆盖
5. ✅ **详细日志输出**：所有操作都有详细的 INFO 级别日志
6. ✅ **统计信息正确**：总文件数、成功数、失败数、跳过数都正确

### 预期的日志输出

```
2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 1/15: 01 B_O_K.ogg
2026-01-30 XX:XX:XX - INFO - 提取标签 - 01 B_O_K.ogg: Artist=侧田, Album=From Justin...
2026-01-30 XX:XX:XX - INFO - 添加年份 (OGG): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (OGG): 1
2026-01-30 XX:XX:XX - INFO - 保存元数据 (OGG): 01 B_O_K.ogg
2026-01-30 XX:XX:XX - INFO - [OK] 01 B_O_K.ogg

2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 2/15: 02 无言无语.ogg
2026-01-30 XX:XX:XX - INFO - 添加年份 (OGG): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (OGG): 2
2026-01-30 XX:XX:XX - INFO - 保存元数据 (OGG): 02 无言无语.ogg
2026-01-30 XX:XX:XX - INFO - [OK] 02 无言无语.ogg

...

2026-01-30 XX:XX:XX - INFO - [INFO] 处理文件 5/15: 05 情歌.flac
2026-01-30 XX:XX:XX - INFO - 添加年份 (FLAC): 2006
2026-01-30 XX:XX:XX - INFO - 添加音轨号 (FLAC): 5
2026-01-30 XX:XX:XX - INFO - 嵌入封面 (FLAC)
2026-01-30 XX:XX:XX - INFO - 保存元数据 (FLAC): 05 情歌.flac
2026-01-30 XX:XX:XX - INFO - [OK] 05 情歌.flac
```

---

## 📋 测试记录

### 测试 1：音轨号提取验证（⏸️ 待执行）

**执行时间**：-  
**执行人**：-  
**测试结果**：⏸️ 待测试

---

### 测试 2：OGG 文件音轨号写入验证（⏸️ 待执行）

**执行时间**：-  
**执行人**：-  
**测试结果**：⏸️ 待测试

---

### 测试 3：FLAC 文件音轨号写入验证（⏸️ 待执行）

**执行时间**：-  
**执行人**：-  
**测试结果**：⏸️ 待测试

---

### 测试 4：音轨号检查验证（⏸️ 待执行）

**执行时间**：-  
**执行人**：-  
**测试结果**：⏸️ 待测试

---

### 测试 5：批量处理验证（⏸️ 待执行）

**执行时间**：-  
**执行人**：-  
**测试结果**：⏸️ 待测试

---

## 🚀 下一步行动

### 等待实施方案确认

**待确认**：
1. ❓ **方案确认**：是否按照实施方案进行代码修改？
2. ❓ **测试确认**：是否按照测试方案进行功能测试？

### 如果确认实施

**我会执行**：
1. ✅ 修改 `supplement_album_metadata.py` 中的 `embed_metadata_to_audio()` 函数签名
2. ✅ 在 FLAC 处理部分添加音轨号写入逻辑（检查 + 写入）
3. ✅ 在 OGG 处理部分添加音轨号写入逻辑（检查 + 写入）
4. ✅ 修改处理循环传递音轨号给函数
5. ✅ 创建最终报告文档

### 如果需要调整

**请告诉我**：
1. ❓ 需要调整实施方案吗？
2. ❓ 需要调整测试方案吗？
3. ❓ 需要添加其他功能吗？

---

## 📚 相关文档

- **实施方案**：`docs/OGG音轨号写入实施方案.md`（本文件）
- **OGG 支持文档**：`docs/OGG_METADATA_IMPLEMENTATION_RESULT.md`（已完成的功能）
- **参考文档**：`docs/FLAC_METADATA_RESEARCH.md`（音轨号规则）

---

**文档创建时间**：2026-01-30  
**最后更新**：2026-01-30  
**维护者**：AI 助手
