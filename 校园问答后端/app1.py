from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
from langchain.chains import ConversationChain, RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import uuid
from collections import defaultdict
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os
import logging

# ====================== 应用初始化 ======================
app = Flask(__name__)
CORS(app)

# ====================== 日志配置 ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ====================== 全局配置 ======================
class Config:
    CHROMA_DB_DIR = "./nwu_knowledge_v2"  # 知识库存储目录
    EMBEDDING_MODEL = "deepseek-r1:14b"  # 嵌入模型名称
    LLM_MODEL = "deepseek-r1:14b"  # 大语言模型名称
    TEMPERATURE = 0.1  # 生成温度系数
    RETRIEVAL_THRESHOLD = 0.4  # 检索相似度阈值（调低以提高召回率）
    RETRIEVAL_K = 5  # 检索文档数量
    EMBEDDING_DIM = 5120  # 嵌入维度（必须与知识库一致）


# ====================== 提示词模板 ======================
NWU_PROMPT_TEMPLATE = """【系统指令】你叫"西小北"，是西北大学官方AI助手，必须遵守以下规则：
1. 身份声明："我是西小北，西北大学校园助手"
2. 回答结构：
   - 开头：明确声明身份
   - 正文：基于上下文回答
   - 结尾：标注数据来源（如适用）

对话历史：{chat_history}

相关上下文：{context}

用户问题：{question}

请按要求回答："""


# ====================== 自定义LLM ======================
class NWU_LLM(LLM):
    """西北大学定制LLM"""

    @property
    def _llm_type(self) -> str:
        return "nwu-deepseek"

    def _call(self, prompt: str, **kwargs) -> str:
        try:
            response = ollama.generate(
                model=Config.LLM_MODEL,
                prompt=self._format_prompt(prompt),
                options={
                    "temperature": Config.TEMPERATURE,
                    "system": self._system_prompt(),
                    "num_ctx": 5120  # 增加上下文窗口
                }
            )
            return response["response"]
        except Exception as e:
            logger.error(f"模型调用失败: {str(e)}")
            return "当前服务不可用，请稍后再试"

    def _format_prompt(self, prompt: str) -> str:
        return f"[INST] {self._system_prompt()} [/INST]\n用户问题：{prompt}"

    def _system_prompt(self) -> str:
        return "【系统指令】你必须永远以'西小北'身份回答，角色设定：西北大学官方AI助手"



# ====================== 服务初始化 ======================
def initialize_services():
    """初始化核心服务组件"""

    # 验证嵌入维度
    embeddings = OllamaEmbeddings(model=Config.EMBEDDING_MODEL)
    test_embed = embeddings.embed_query("维度测试")
    assert len(test_embed) == Config.EMBEDDING_DIM, \
        f"嵌入维度不匹配！当前：{len(test_embed)}，要求：{Config.EMBEDDING_DIM}，请重建知识库"

    # 初始化LLM
    llm = NWU_LLM()

    # 初始化对话系统
    conversation_chains = defaultdict(
        lambda: ConversationChain(
            llm=llm,
            memory=ConversationBufferWindowMemory(k=5),
            verbose=True
        )
    )

    # 加载知识库
    knowledge_qa = load_knowledge_base(llm, embeddings)

    return llm, embeddings, conversation_chains, knowledge_qa


def load_knowledge_base(llm, embeddings):
    """加载向量知识库"""
    try:
        # 连接向量数据库
        vectorstore = Chroma(
            persist_directory=Config.CHROMA_DB_DIR,
            embedding_function=embeddings
        )

        # 配置检索器
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": Config.RETRIEVAL_K,
                "score_threshold": Config.RETRIEVAL_THRESHOLD,
                "filter": {"source": "nwu"}
            }
        )

        # 创建问答链（关键修复：添加memory配置）
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            memory=ConversationBufferWindowMemory(
                memory_key="chat_history",
                input_key="query",
                k=5  # 保留5轮历史对话
            ),
            chain_type_kwargs={
                "prompt": PromptTemplate(
                    template=NWU_PROMPT_TEMPLATE,
                    input_variables=["context", "question", "chat_history"]
                ),
                "verbose": True
            },
            return_source_documents=True
        )

    except Exception as e:
        logger.error(f"知识库加载失败: {str(e)}")
        raise


# ====================== 全局服务实例 ======================
llm, embeddings, conversation_chains, knowledge_qa = initialize_services()


# ====================== API接口 ======================
@app.route('/chat/generate', methods=['POST'])
def handle_query():
    """处理用户查询请求"""
    data = request.json
    question = data.get('prompt', '').strip()
    session_id = data.get('session_id') or str(uuid.uuid4())
    use_knowledge = data.get('use_knowledge', False)

    # 输入验证
    if not question:
        return error_response(400, "问题不能为空", session_id)

    try:
        # 选择处理模式
        if use_knowledge:
            return process_knowledge_query(question, session_id)
        return process_conversation(question, session_id)

    except Exception as e:
        logger.error(f"请求处理异常: {str(e)}")
        return error_response(500, "服务器内部错误", session_id)


def process_knowledge_query(question: str, session_id: str) -> Dict:
    """处理知识库查询（包含降级逻辑）"""
    if not knowledge_qa:
        return error_response(503, "知识库未就绪", session_id)

    try:
        # 关键修复：显式传递对话历史
        result = knowledge_qa({
            "query": question,
            "chat_history": conversation_chains[session_id].memory.buffer_as_str
        })

        # 处理空结果
        if not result.get("source_documents"):
            logger.warning(f"知识库未找到'{question}'的匹配内容")
            return process_conversation(question, session_id)

        # 提取来源信息
        sources = list({os.path.basename(doc.metadata["source"])
                        for doc in result["source_documents"]})

        return success_response(
            answer=result["result"],
            session_id=session_id,
            sources=sources,
            is_knowledge_based=True
        )

    except Exception as e:
        logger.error(f"知识库查询失败: {str(e)}")
        return process_conversation(question, session_id)  # 降级到普通对话


def process_conversation(question: str, session_id: str) -> Dict:
    """处理普通对话"""
    try:
        answer = conversation_chains[session_id].predict(input=question)
        return success_response(
            answer=answer,
            session_id=session_id,
            is_knowledge_based=False
        )
    except Exception as e:
        logger.error(f"对话处理失败: {str(e)}")
        return error_response(500, "对话服务暂时不可用", session_id)


# ====================== 响应工具 ======================
def success_response(answer: str, session_id: str, **extras) -> Dict:
    return jsonify({
        "code": 100,
        "data": answer,
        "session_id": session_id,
        **extras
    })


def error_response(code: int, error: str, session_id: str) -> Dict:
    return jsonify({
        "code": code,
        "error": error,
        "session_id": session_id
    }), code


# ====================== 主程序 ======================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)