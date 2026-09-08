> 状态：🟢 本地已跑通（待部署 Streamlit Community Cloud 拿公开链接） ｜ 对应方向：AI 应用开发 / 智能体 / RAG 知识库

# ② 企业知识库问答系统（RAG）

面向企业的「上传文档 → 自然语言问答」知识库。员工用大白话提问，系统从私有文档里检索相关段落，由大模型生成**带原文引用**的答案，避免胡编。

## 1. 问题（Problem）
企业制度 / 产品 FAQ / 客服话术散落在 Word、PDF、内部 wiki 里，新人找答案靠问老人或翻文档，慢且易遗漏。
通用大模型答不准企业私有信息（幻觉）。需要一个**只基于本公司资料、可追溯出处**的问答工具。

## 2. 方案（Solution）
经典 RAG 四步：
1. **文档切分**：按段落 + 句末断句，切成语义完整的块（≤280 字）
2. **向量化建库**：用智谱 `Embedding-3` 把每块转成向量，存入本地 Chroma 向量库
3. **检索**：用户问题同样向量化，Chroma 做相似度召回 top-3 段落
4. **生成**：把召回段落拼进 Prompt，让智谱 `GLM-4.7-Flash` 生成带 `[1][2]` 引用的答案；资料没有就说「未提及」，不编造

## 3. 架构（Architecture）
```
data/company_faq.txt  ──►  切分  ──►  Embedding-3  ──►  Chroma(本地持久化)
                                                        │
用户问题 ──► Embedding-3 ──► Chroma 检索 top-3 ──► 拼 Prompt ──► GLM-4.7-Flash ──► 带引用答案
                                                        │
                              app.py(Streamlit 界面) 展示答案 + 参考资料
```
- `rag_core.py`：检索 + 生成核心（与界面解耦，以后换 FastAPI 外壳也行）
- `app.py`：Streamlit 网页界面
- 纯后端调用智谱，**无浏览器跨域（CORS）问题**；Key 仅用于调接口，不落库

## 4. 效果（Result）
- 示例库内置 7 类公司制度（年假 / 报销 / 试用期 / 退换货 / 客服时效 / 考勤 / 信息安全）
- 检索召回准、回答带引用、资料缺失会拒答
- 成本：生成免费（GLM-4.7-Flash），向量化 Embedding-3 新用户送额度，demo 量几乎零成本
- 截图：（待补：本地 `streamlit run app.py` 跑通后截图贴此处）
- 公开链接：https://liuwenjia-rag.streamlit.app

## 5. 踩坑（Pitfalls）
- Chroma 集合名必须 3-512 字符且只能字母/数字/下划线，初版命名 `"kb"` 报错 `Got: kb`，改成 `"company_kb"` 解决
- 本地依赖 chromadb 体积大，首次 `pip install` 较慢（sandbox 曾卡 25 分钟，换清华镜像源解决）；云端用官方源一般数分钟
- 关键认知：RAG 质量 = 切分策略 × 检索召回 × Prompt 约束，检索不准模型再强也答错

## 6. 运行（Run）
```bash
pip install -r requirements.txt
# 本地可选：复制 .streamlit/secrets.toml.example 为 secrets.toml 填 Key
# 或直接在界面左侧输入智谱 Key（open.bigmodel.cn 获取）
streamlit run app.py
# 浏览器打开 http://localhost:8501 → 左侧填 Key → 首次自动建索引 → 提问
```
- 部署 Streamlit Community Cloud：登录 share.streamlit.io → New app → 选仓库 `liuwenjia-ai-portfolio` / 分支 `main` / 入口 `project-2-rag-kb/app.py` → Advanced → Secrets 填 `ZHIPU_API_KEY=你的key` → Deploy（Public app 免费，无需信用卡）

## 面试可讲
「我从文档解析、分块、Embedding、向量检索到大模型生成全链路自己实现。最难的是切分和检索召回质量——块太大语义杂、太小丢上下文；我用句号断句控制在 280 字内。还有幻觉问题，我用 Prompt 强制模型只基于检索段落作答并标引用，资料没有就拒答。」
