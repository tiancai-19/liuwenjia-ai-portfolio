"""
rag_core.py — 企业知识库问答核心（RAG）
作者：刘文佳（GitHub: tiancai-19）
技术栈：智谱 Embedding-3（向量化） + Chroma（本地向量库） + GLM-4.7-Flash（生成）

设计要点：
1. 文档切分 → 向量化（Embedding-3）→ 存入本地 Chroma，构建向量索引
2. 用户提问同样向量化，Chroma 做相似度检索，召回 top-k 段落
3. 把召回段落作为上下文拼进 Prompt，让 GLM-4.7-Flash 生成带 [1][2] 引用的答案
4. 纯后端调用，无浏览器跨域（CORS）问题；API Key 仅用于调智谱，不落库、不暴露
"""

import os
import re

# 关闭 Chroma 遥测，避免无意义的联网上报
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from openai import OpenAI
import chromadb

EMBED_MODEL = "embedding-3"          # 智谱中文向量化模型（新用户送额度，demo 几乎零成本）
GEN_MODEL = "glm-4.7-flash"          # 智谱免费生成模型
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"  # 智谱 OpenAI 兼容端点
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")  # 向量库持久化目录（本地磁盘）
COLLECTION = "company_kb"            # 集合名（Chroma 要求 3-512 字符）


def get_client(api_key: str) -> OpenAI:
    """构造智谱 OpenAI 兼容客户端。"""
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def chunk_text(text: str, max_len: int = 280):
    """按段落切分；超长段落再按句末标点断句，保证单块不太长、语义完整。"""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    for p in paras:
        if len(p) <= max_len:
            chunks.append(p)
            continue
        sentences = re.split(r"(?<=[。！？；])", p)
        buf = ""
        for s in sentences:
            if len(buf) + len(s) <= max_len:
                buf += s
            else:
                if buf:
                    chunks.append(buf.strip())
                buf = s
        if buf:
            chunks.append(buf.strip())
    return chunks


def build_index(api_key: str, doc_path: str) -> int:
    """读取文档 → 分块 → 向量化 → 写入 Chroma。返回块数量。"""
    client = get_client(api_key)
    with open(doc_path, encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_text(text)

    # 批量向量化（一次请求多段，省调用次数）
    resp = client.embeddings.create(model=EMBED_MODEL, input=chunks)
    embeddings = [d.embedding for d in resp.data]

    # 写入本地向量库（先清旧库再建，保证可重复构建）
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    if COLLECTION in [c.name for c in chroma.list_collections()]:
        chroma.delete_collection(COLLECTION)
    col = chroma.get_or_create_collection(name=COLLECTION)
    ids = [f"c{i}" for i in range(len(chunks))]
    col.add(ids=ids, documents=chunks, embeddings=embeddings)
    return len(chunks)


def query(api_key: str, question: str, top_k: int = 3):
    """检索 + 生成。返回 (answer, refs)。refs 为召回的原文段落列表。"""
    client = get_client(api_key)
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    col = chroma.get_or_create_collection(name=COLLECTION)

    # 1) 问题向量化
    q_emb = client.embeddings.create(model=EMBED_MODEL, input=[question]).data[0].embedding
    # 2) 向量检索 top-k
    res = col.query(query_embeddings=[q_emb], n_results=top_k)
    contexts = res["documents"][0]

    # 3) 拼 Prompt，让模型只基于检索到的资料回答并标引用
    sys_prompt = (
        "你是企业知识库问答助手。只根据下面【参考资料】回答用户问题，"
        "在相关句末用 [1]、[2] 标注引用了哪条资料。"
        "如果资料里没有答案，明确说“资料中未提及”，不要编造。"
    )
    ctx_block = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
    user_prompt = f"【参考资料】\n{ctx_block}\n\n【问题】{question}"

    # 4) 大模型生成
    resp = client.chat.completions.create(
        model=GEN_MODEL,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    answer = resp.choices[0].message.content
    return answer, contexts
