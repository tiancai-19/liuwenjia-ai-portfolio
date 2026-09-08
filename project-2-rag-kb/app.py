"""
app.py — 企业知识库问答 RAG（Streamlit 界面）
运行：streamlit run app.py
API Key 来源优先级：① HuggingFace/Streamlit Secrets ② 环境变量 ZHIPU_API_KEY ③ 界面输入
"""

import os
import streamlit as st

# rag_core 顶部会关闭 Chroma 遥测，需在其 import 前设置页面
st.set_page_config(page_title="企业知识库问答系统", layout="wide")

from rag_core import build_index, query, CHROMA_PATH, GEN_MODEL, EMBED_MODEL

st.markdown(
    """<style>
    .stApp a{color:#0F6E56;}
    .stButton>button{background-color:#0F6E56;border-color:#0F6E56;color:#fff;}
    .stButton>button:hover{background-color:#0c5a45;border-color:#0c5a45;}
    </style>""",
    unsafe_allow_html=True,
)
st.markdown("[← 返回作品集主页](https://tiancai-19.github.io/liuwenjia-ai-portfolio/)", unsafe_allow_html=True)

st.title("企业知识库问答系统")
st.caption(
    f"向量化：智谱 {EMBED_MODEL} ｜ 生成：智谱 {GEN_MODEL} ｜ 向量库：Chroma（本地）\n"
    "API Key 仅用于调用智谱，不落库、不对外暴露。"
)

# ---------- API Key 获取 ----------
api_key = None
try:
    api_key = st.secrets["ZHIPU_API_KEY"]
except Exception:
    api_key = None
if not api_key:
    api_key = os.environ.get("ZHIPU_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input(
        "智谱 API Key", type="password",
        help="在 open.bigmodel.cn 获取；本地填一次即可，不会保存或上传",
    )

if not api_key:
    st.warning("请先在左侧填入智谱 API Key（或配置 Secrets / 环境变量 ZHIPU_API_KEY）")
    st.stop()

# ---------- 建索引 ----------
DOC = os.path.join(os.path.dirname(__file__), "data", "company_faq.txt")
rebuild = st.sidebar.button("🔄 重建索引")
need_build = rebuild or not os.path.exists(CHROMA_PATH)
if need_build:
    with st.sidebar.status("正在向量化文档…"):
        try:
            n = build_index(api_key, DOC)
            st.sidebar.success(f"索引已建，共 {n} 段")
        except Exception as e:
            st.sidebar.error(f"建索引失败：{e}")
            st.stop()
else:
    st.sidebar.info("✅ 索引已存在（需更新文档时点“重建索引”）")

# ---------- 问答 ----------
st.markdown("### 提问")
q = st.text_input(
    "输入你的问题：",
    placeholder="例如：年假怎么算？ / 报销流程是什么？ / 试用期多久？",
    label_visibility="collapsed",
)

if q:
    with st.spinner("检索 + 生成中…"):
        try:
            ans, refs = query(api_key, q)
            st.markdown("### 回答")
            st.write(ans)
            with st.expander("📎 检索到的参考资料（模型据此作答）"):
                for i, r in enumerate(refs, 1):
                    st.markdown(f"**[{i}]** {r}")
        except Exception as e:
            st.error(f"调用出错：{e}")

st.markdown(
    "<div style='margin-top:32px;padding-top:16px;border-top:1px solid #e3e2dd;"
    "text-align:center;color:#6b6a65;font-size:13px;'>"
    "<a href='https://tiancai-19.github.io/liuwenjia-ai-portfolio/' style='color:#0F6E56;"
    "text-decoration:none;'>← 返回作品集主页</a></div>",
    unsafe_allow_html=True,
)
