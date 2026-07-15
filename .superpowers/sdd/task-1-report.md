# Task 1 实施报告

## 修改文件

- `scripts/test_shengtang_regressions.py`
  - 将角色目录精确数量及 ID、名称唯一性断言从 150 人改为 200 人。
  - 新增 `plot/character_batches/recent_anime.yaml` 的 50 人批次及来源 ID 一致性断言。
  - 新增 UI 文案回归测试：移除“枢纽抽卡”“相聚一刻”“一键随机开始”“生成开局”，并要求“召来新客”“推进当前幕”“随机启程”“揭晓初遇”“正在编织初遇”。
- `.superpowers/sdd/task-1-report.md`
  - 本报告。

未修改生产代码，也未暂存工作区中其他协作者的未跟踪文件。

## 测试命令

```powershell
python -m unittest scripts.test_shengtang_regressions
```

## 关键失败输出

```text
FAIL: test_revised_ui_copy_is_present_and_obsolete_copy_is_removed
AssertionError: '枢纽抽卡' unexpectedly found in ...

FAIL: test_roster_has_exactly_200_unique_characters
AssertionError: 150 != 200

Ran 67 tests in 0.544s
FAILED (failures=2)
```

补充检查确认：`plot/character_batches/recent_anime.yaml` 当前不存在；五个期望新文案在 `COVER + STATUS` 中均不存在。完整测试首先在 200 人数量断言失败，因此本次运行未继续执行 `recent_anime.yaml` 的读取断言。

## 自审

- [x] 仅修改测试断言，没有生产代码改动。
- [x] 角色总数、ID 唯一性、名称唯一性均要求 200。
- [x] 新增 50 人批次和来源集合一致性验收。
- [x] 新增旧文案清除和新文案存在验收。
- [x] `git diff --check` 通过。
- [x] 测试文件 UTF-8 字节检查通过。
- [x] 测试按要求失败，失败原因与当前 150 人目录、缺少批次文件和缺少新文案一致。
