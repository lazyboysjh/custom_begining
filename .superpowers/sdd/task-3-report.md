# Task 3 实施报告

## 修改文件

- `src/shengtang/ui/cover/index.html`
- `src/shengtang/ui/status/index.html`

只修改用户可见字符串、title、aria-label 与错误提示，不修改按钮 id、事件绑定、MVU 路径或生成 API 参数。

## 测试

命令：`python -m unittest scripts.test_shengtang_regressions.CharacterCatalogTests.test_revised_ui_copy_is_present_and_obsolete_copy_is_removed`

结果：`Ran 1 test ... OK`。

`git diff --check` 通过。

## 自审

- 旧词 `枢纽抽卡 / 相聚一刻 / 一键随机开始 / 生成开局` 已清除。
- 新词 `召来新客 / 推进当前幕 / 随机启程 / 揭晓初遇 / 正在编织初遇` 已覆盖静态与动态状态。
- 生成错误不再把原始内部错误直接展示给用户，详细信息仅写控制台。

## Task 3 复审修复

### 修改

- `src/shengtang/ui/cover/index.html`：将“生成时从能力池中随机选择，结果会与本局一起锁定。”改为自然叙事提示“命运会在诸般可能中替你挑选一项能力，让它成为这次相遇的一部分。”，移除内部机制与游戏术语。
- `src/shengtang/ui/status/index.html`：将“当前为界面预览”改为“请先打开消息发送功能，再续写当前幕。”，明确用户下一步操作。

### 测试

- `python -m unittest scripts.test_shengtang_regressions.CharacterCatalogTests.test_revised_ui_copy_is_present_and_obsolete_copy_is_removed`：通过。
- `git diff --check`：通过。

### 自审

- 两处旧文案均已移除，新增文案均为用户可见、自然且与当前动作一致的提示。
- 仅修改指定的两个 HTML 文件和本报告；未改动按钮标识、事件绑定、MVU 路径或发送参数。
