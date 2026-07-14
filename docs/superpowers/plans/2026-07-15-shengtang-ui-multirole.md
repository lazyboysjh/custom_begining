# Sanctum Multi-role UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将圣堂初遇升级为支持同场多角色独立状态的 MVU 角色卡，并统一重做封面与状态栏的高质感响应式 UI。

**Architecture:** `世界.出场角色` 保存当前场景有序姓名数组，`角色` record 保存永久角色档案；Schema 负责旧结构迁移、去重和数值约束。状态栏只读 `stat_data` 并维护本地选中角色，封面与状态栏在各自 HTML 中使用同名设计 token 保持视觉一致。

**Tech Stack:** HTML/CSS/JavaScript、MVU/Zod 4、YAML、Python unittest、Playwright、现有 Python 卡片构建器。

## Global Constraints

- 正式 UI 不显示构建版本、CDN、MVU/API、初始化成功、变量路径、事务状态或开发说明。
- 桌面封面 `16:9`，手机封面 `9:16`；酒馆 iframe 内禁止用 `vh` 强撑高度。
- 页面不得产生横向滚动；动态文字必须换行、省略或自适应。
- 主容器圆角不超过 `8px`，小控件使用 `6px`；按钮优先图标并提供 tooltip。
- 动效分为 `180ms` 交互、`320..480ms` 进入、`600ms` 数值变化，并支持 `prefers-reduced-motion`。
- MVU UI 必须等待 `waitGlobalInitialized('Mvu')`、使用 `getAllVariables()`、读取 `stat_data.*` 并监听 `VARIABLE_UPDATE_ENDED`。

---

### Task 1: 多角色变量结构与回归测试

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Modify: `plot/schema.mvu.js`
- Modify: `plot/initvar.yaml`

**Interfaces:**
- Produces: `stat_data.世界.出场角色: string[]`
- Produces: `stat_data.角色: Record<string, RoleState>`

- [ ] **Step 1: 写失败测试**

在 `scripts/test_shengtang_regressions.py` 增加断言：

```python
class MultiRoleSchemaTests(unittest.TestCase):
    def test_schema_has_present_role_array_and_role_record(self) -> None:
        schema = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
        initvar = yaml.safe_load((ROOT / "plot/initvar.yaml").read_text(encoding="utf-8"))
        self.assertIn("出场角色: z.array(z.string())", schema)
        self.assertIn("角色: z.record(z.string()", schema)
        self.assertEqual(initvar["世界"]["出场角色"], [])
        self.assertEqual(initvar["角色"], {})

    def test_schema_migrates_legacy_opening_state(self) -> None:
        schema = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
        for marker in ("同场角色", "初遇", "new Set", "delete data.初遇"):
            self.assertIn(marker, schema)
```

- [ ] **Step 2: 运行并确认 RED**

Run: `python -m unittest scripts.test_shengtang_regressions.MultiRoleSchemaTests -v`

Expected: FAIL，缺少 `出场角色` 与 `角色` 新结构。

- [ ] **Step 3: 实现 Schema 与初始变量**

在 `plot/schema.mvu.js` 定义可复用角色状态，并在根 transform 中迁移旧字段：

```javascript
const RoleState = z.object({
  作品: z.string().prefault(''),
  是否自定义: z.boolean().prefault(false),
  污秽类型: z.string().prefault(''),
  污秽度: z.coerce.number().prefault(40),
  信任: z.coerce.number().prefault(15),
  好感度: z.coerce.number().prefault(10),
  堕落值: z.coerce.number().prefault(5),
  依存度: z.coerce.number().prefault(0),
  仪式阶段: z.string().prefault('初见'),
  与user关系: z.string().prefault('陌路'),
  当前心态: z.string().prefault(''),
  当前目标: z.string().prefault('确认污秽来源并保全自身'),
  对user判断: z.string().prefault('能力与动机待验证'),
  当前边界: z.string().prefault('不接受未经说明或同意的私密接触'),
}).transform(clampRoleState);
```

`plot/initvar.yaml` 使用 `出场角色: []` 和 `角色: {}`，保留旧字段只在 Schema 兼容输入中使用。

- [ ] **Step 4: 运行并确认 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions.MultiRoleSchemaTests -v`

Expected: PASS。

### Task 2: 多角色更新规则与开局/抽卡数据写入

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Modify: `plot/mvu_update.yaml`
- Modify: `src/shengtang/ui/cover/index.html`
- Modify: `src/shengtang/ui/status/index.html`

**Interfaces:**
- Consumes: `世界.出场角色` 与 `角色.[姓名]`
- Produces: 开局完整 initvar 与抽卡 `insert` JSON Patch

- [ ] **Step 1: 写失败测试**

```python
def test_multirole_rules_are_independent(self) -> None:
    rules = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
    for marker in ("出场角色", "角色.[姓名]", "实际感知", "未出场角色", "/世界/出场角色/-"):
        self.assertIn(marker, rules)

def test_opening_and_draw_prompts_write_multirole_paths(self) -> None:
    self.assertIn('/世界/出场角色', COVER)
    self.assertIn('/角色/', COVER)
    self.assertNotIn('/世界/同场角色', STATUS)
```

- [ ] **Step 2: 运行并确认 RED**

Run: `python -m unittest scripts.test_shengtang_regressions.MultiRoleSchemaTests -v`

Expected: FAIL，旧提示词仍写 `同场角色` 和单个 `初遇`。

- [ ] **Step 3: 实现更新规则**

抽卡新人首次进入输出：

```json
[
  { "op": "insert", "path": "/角色/新人姓名", "value": { "作品": "作品名", "信任": 10, "好感度": 5 } },
  { "op": "insert", "path": "/世界/出场角色/-", "value": "新人姓名" }
]
```

开局增量 patch 同时建立 `角色.[姓名]` 并把姓名写入 `世界.出场角色`。规则明确同场角色按实际感知分别更新，离场只移除数组项。

- [ ] **Step 4: 运行并确认 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions.MultiRoleSchemaTests -v`

Expected: PASS。

### Task 3: 状态栏多角色产品布局

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Modify: `src/shengtang/ui/status/index.html`
- Modify: `scripts/ui_audit.py`

**Interfaces:**
- Consumes: `getAllVariables().stat_data.世界.出场角色`
- Consumes: `getAllVariables().stat_data.角色[name]`
- Produces: `renderRoleSwitcher(names, activeName)` 与 `renderRoleState(role)`

- [ ] **Step 1: 写失败测试**

```python
def test_status_renders_multirole_state(self) -> None:
    for marker in (
        "stat_data.世界.出场角色", "stat_data.角色", "activeRoleName",
        "renderRoleSwitcher", "role-picker", "aria-label=\"全部角色\"",
    ):
        self.assertIn(marker, STATUS)

def test_status_hides_internal_copy(self) -> None:
    for forbidden in ("MVU", "CDN", "初始化成功", "UI ·", "变量路径"):
        self.assertNotIn(forbidden, STATUS)
```

- [ ] **Step 2: 运行并确认 RED**

Run: `python -m unittest scripts.test_shengtang_regressions.StatusLifecycleTests -v`

Expected: FAIL，状态栏仍按单角色渲染并含内部提示。

- [ ] **Step 3: 实现多角色状态栏**

使用单一磨砂主容器、角色快捷栏、可搜索选择器和响应式详情区域。初始化逻辑必须保持：

```javascript
async function init() {
  await waitGlobalInitialized('Mvu');
  populateCharacterData();
  subscriptions.push(eventOn(Mvu.events.VARIABLE_UPDATE_ENDED, populateCharacterData));
}
$(errorCatched(init));
```

`populateCharacterData()` 从 `stat_data` 读取数组与 record；当前角色离场时自动切换到第一名。

- [ ] **Step 4: 运行并确认 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions.StatusLifecycleTests -v`

Expected: PASS。

### Task 4: 封面与状态栏统一视觉重构

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Modify: `src/shengtang/ui/cover/index.html`
- Modify: `src/shengtang/ui/status/index.html`

**Interfaces:**
- Produces: 两个 HTML 内一致的 `--st-bg`、`--st-surface`、`--st-line`、`--st-gold`、`--st-radius`、`--st-ease`

- [ ] **Step 1: 写失败测试**

```python
def test_cover_and_status_share_product_tokens(self) -> None:
    for token in ("--st-bg", "--st-surface", "--st-line", "--st-gold", "--st-radius", "--st-ease"):
        self.assertIn(token, COVER)
        self.assertIn(token, STATUS)
    self.assertNotIn("UI ·", COVER)
    self.assertNotIn("Ambient orbs", STATUS)
```

- [ ] **Step 2: 运行并确认 RED**

Run: `python -m unittest scripts.test_shengtang_regressions -v`

Expected: FAIL，旧 token 与装饰性文案仍存在。

- [ ] **Step 3: 实现统一 UI**

主容器遵循：

```css
.st-shell {
  border: 1px solid var(--st-line);
  border-radius: var(--st-radius);
  background: var(--st-surface);
  box-shadow: inset 0 1px rgba(255,255,255,.055), 0 24px 64px rgba(0,0,0,.34);
  backdrop-filter: blur(24px) saturate(1.22);
}
```

移除装饰球、粗边框、外发光、开发文案和重复说明；控件统一图标、tooltip、按压反馈和稳定尺寸。

- [ ] **Step 4: 运行并确认 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions -v`

Expected: PASS。

### Task 5: 多端浏览器审查与卡片构建

**Files:**
- Modify: `scripts/ui_audit.py`
- Generated: `圣堂初遇.json`
- Generated: `dist/shengtang/ui/cover/index.html`
- Generated: `dist/shengtang/ui/status/index.html`

**Interfaces:**
- Consumes: 新 UI 与新 MVU fixture
- Produces: `tmp/ui-audit/*.png` 与发布候选角色卡

- [ ] **Step 1: 更新浏览器 fixture**

```javascript
世界: { 场景: "圣言堂·告解室", 出场角色: ["芙莉莲", "牧濑红莉栖", "雪之下雪乃"] },
角色: {
  芙莉莲: { 信任: 46, 好感度: 32, 当前心态: "保持观察" },
  牧濑红莉栖: { 信任: 28, 好感度: 18, 当前心态: "分析异常" },
  雪之下雪乃: { 信任: 20, 好感度: 12, 当前心态: "警惕环境" }
}
```

- [ ] **Step 2: 构建并运行完整测试**

Run: `python build_shengtang_card.py`

Run: `python -m unittest scripts.test_shengtang_regressions -v`

Run: `pnpm.cmd build`

Expected: 全部 exit `0`。

- [ ] **Step 3: 运行浏览器多端审查**

Run: `python scripts/ui_audit.py`

Expected: mobile/tablet/desktop 均生成封面与状态栏截图，报告中所有 `overflowX=False`。

- [ ] **Step 4: 运行发布审查**

Run: `python scripts/superpower_shengtang_review.py`

Expected: `ERR=0`。

### Task 6: 提交、推送与固定 CDN

**Files:**
- Modify: `圣堂初遇.json`

**Interfaces:**
- Produces: 固定到 UI commit 的 jsDelivr URL

- [ ] **Step 1: 提交并推送 UI**

```powershell
git add -- plot src scripts build_shengtang_card.py dist/shengtang/ui
git commit -m "Redesign Sanctum multi-role UI"
git pull --rebase origin main
git push origin main
```

- [ ] **Step 2: 用 UI commit 重新生成卡**

```powershell
$ref = git rev-parse HEAD
$env:ST_CDN_REF = $ref
$env:ST_CDN_V = '11'
python build_shengtang_card.py
git add -- '圣堂初遇.json'
git commit -m "Pin Sanctum card CDN to multi-role UI"
git pull --rebase origin main
git push origin main
```

- [ ] **Step 3: 验证远端和 CDN**

Run: `git ls-remote origin refs/heads/main`

Run: 对固定 commit 的 cover/status URL 执行 `Invoke-WebRequest`。

Expected: 远端 HEAD 与本地一致；两个 URL 都返回 `200`，封面包含 `--st-surface`，状态栏包含 `renderRoleSwitcher`。
