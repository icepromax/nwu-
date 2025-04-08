from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
from langchain.chains import ConversationChain, RetrievalQA
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from typing import Optional, List, Dict, Any
import uuid
from collections import defaultdict
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os
import logging

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置参数
CHROMA_DB_DIR = "./nwu_knowledge_v2"  # 修改为您的知识库目录

# 西北大学专属prompt模板
NWU_PROMPT_TEMPLATE = """你是西小北，是一个专业的西北大学校园助手，请根据以下上下文信息回答问题。
上下文：
{context}

问题：{question}

回答要求：
1. 如果是培养方案、课程相关问题，请注明来源文件
2. 如果是规章制度问题，请说明最新修订时间（如有）
3. 保持回答简洁准确，使用中文回答
4. 如果不知道答案，请回答"根据现有资料，我暂时无法回答这个问题"
5. 用中文回答问题
最终答案："""

# 自定义Ollama的LLM包装器
class OllamaLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "ollama-llama3"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> str:
        try:
            response = ollama.generate(
                model="llama3:8b",
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "num_ctx": 4096  # 增大上下文窗口
                }
            )
            return response["response"]
        except Exception as e:
            logger.error(f"Ollama生成错误: {str(e)}")
            return "抱歉，处理您的请求时出现问题"


# 初始化LLM和Embeddings
llm = OllamaLLM()
embeddings = OllamaEmbeddings(model="llama3:8b")

# 存储不同会话的对话链
conversation_chains = defaultdict(lambda: ConversationChain(
    llm=llm,
    memory=ConversationBufferWindowMemory(k=5),
    verbose=True
))

# 知识库问答链
knowledge_qa_chain = None


def create_nwu_prompt():
    """创建西北大学专属prompt"""
    return PromptTemplate(
        template=NWU_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )


def load_knowledge_base():
    global knowledge_qa_chain

    if not os.path.exists(CHROMA_DB_DIR):
        logger.warning(f"知识库目录 {CHROMA_DB_DIR} 不存在")
        return

    try:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )

        knowledge_qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 3, "score_threshold": 0.65}
            ),
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                input_key="query",
                output_key="result"
            ),
            return_source_documents=True,
            output_key="result",  # 关键修复
            chain_type_kwargs={
                "prompt": create_nwu_prompt(),
                "verbose": True
            }
        )
        logger.info("西北大学知识库加载成功")
    except Exception as e:
        logger.error(f"知识库加载失败: {str(e)}")


# 初始化时加载知识库
load_knowledge_base()


@app.route('/chat/generate', methods=['POST'])
def generate():
    data = request.json
    logger.info(f"收到请求: {data}")

    question = data.get('prompt', '').strip()
    session_id = data.get('session_id')
    use_knowledge = data.get('use_knowledge', False)

    if not question:
        return jsonify({'code': 400, 'error': '问题不能为空'}), 400

    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"为新用户创建session: {session_id}")

    try:
        if use_knowledge:
            if not knowledge_qa_chain:
                return jsonify({
                    'code': 503,
                    'error': '知识库未加载',
                    'session_id': session_id
                }), 503

            result = knowledge_qa_chain({"query": question})
            answer = result["result"]

            response = {
                'code': 100,
                'data': answer,
                'session_id': session_id,
                'is_knowledge_based': True
            }
        else:
            conversation = conversation_chains[session_id]
            answer = conversation.predict(input=question)

            response = {
                'code': 100,
                'data': answer,
                'session_id': session_id,
                'is_knowledge_based': False
            }

    except Exception as e:
        logger.error(f"处理请求出错: {str(e)}")
        return jsonify({
            'code': 500,
            'error': '服务器内部错误',
            'session_id': session_id
        }), 500

    logger.info(f"返回响应: {response}")
    return jsonify(response)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
