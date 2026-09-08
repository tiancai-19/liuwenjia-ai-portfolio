# 项目 3 · 电商运营自动化工具集

> 状态：🟡 开发中（子工具① 商品图文 AIGC 工作台已可演示）｜ 对应方向：AI 自动化提效 / AIGC 电商运营

含 3 个子工具，分别打不同 JD 关键词。当前已完成子工具①，②③ 为规划。

---

## 子工具 ① 商品图文 AIGC 工作台（✅ 已可演示）

### 1. 问题（Problem）
电商运营上新时，商品标题、卖点文案、主图重复制作、耗时长、质量不稳；同一商品常需多版文案做 A/B。

### 2. 方案（Action）
纯前端单页工具：输入商品名 + 类目 + 卖点 → 大模型生成 3 版标题 / 3 条卖点 / 详情 + 主图提示词 → 文生图出主图 → 满意的组合收藏进模板库复用。

### 3. 架构（Architecture）
- 前端：纯 HTML / CSS / JavaScript（单文件，无构建）
- 文案模型：智谱 GLM-4.7-Flash（open.bigmodel.cn，免费、200K、OpenAI 兼容）
- 图像模型：智谱 CogView-3-Flash（免费文生图，¥0/张，同账号同 Key）
- 调用：浏览器 `fetch` 直连智谱开放平台，无后端
- Key 安全：仅存浏览器 `localStorage`（密码掩码），不进仓库/服务器
- 模板库：收藏的组合存 `localStorage`（演示用；生产可换 MySQL）

### 4. 效果（Result）
- 文案：一次输入出 3 标题 + 3 卖点 + 详情 + 主图提示词，可直接复制用
- 主图：CogView-3-Flash 生成，默认带 AI 水印（生产环境签去水印声明可关）
- 在线演示：https://tiancai-19.github.io/liuwenjia-ai-portfolio/project-3-ecommerce-rpa/

### 5. 踩坑（Lesson）
- **图生成较慢**：CogView-3-Flash 免费档可能排队，前端设 120 秒超时 + 重试提示，避免白等
- **免费档限速**：GLM 约 1 次/秒、图像也可能 429，代码对 429 做了友好提示
- **图像 URL 有效期**：智谱返回图链 30 天有效，长期留存需转存（本 Demo 未做）
- **原型≠作品**：本工具接的是真实双模型 API + 本地模板库，不是 easy-vibe 的假数据原型

### 6. 运行（Run）
```bash
cd project-3-ecommerce-rpa
python -m http.server 8000
# 浏览器访问 http://localhost:8000
```
- 在线演示：https://tiancai-19.github.io/liuwenjia-ai-portfolio/project-3-ecommerce-rpa/
- 使用：填 Key 并保存 → 点「一键填充示例」→「生成文案」→「生成主图」→「收藏」

### 进阶方向（面试可展开，本 Demo 未实现）
- 模板落 MySQL / 后端，实现团队共享模板库
- Excel 批量导入商品，循环批量生成图文草稿
- 影刀 RPA 把生成结果回写商品后台，完成上新闭环

---

## 子工具 ② 订单对账自动化（⚪ 规划，升级旧 P1 跨平台对账）
- 旧 P1 已用 Python + pandas + MySQL 跑通，覆盖多平台订单格式
- 升级点：加 AI 异常识别 / 差异原因自动分类 / 生成对账报告
- 保留原因：真实跑通的数据处理项目，证明 Python/SQL 基础，对应 AI 产品经理/数据类岗位对 SQL/数据处理的要求

## 子工具 ③ 客服常见问答 bot（⚪ 规划）
- Coze / Dify 搭建，接知识库
- 覆盖常见客诉自动应答，降低人工重复劳动

---

> 公开 README 写通用方向即可，不写具体投递公司名；面试话术仅放私有笔记，不写在此处。
