import os
import re
from typing import List, Dict

from langchain.document_loaders import (
    PyPDFLoader,#.pdf
    Docx2txtLoader,#.docx
    UnstructuredFileLoader,
    DirectoryLoader,
    UnstructuredWordDocumentLoader,  # 处理.doc
    UnstructuredExcelLoader,  # 处理.xlsx
)

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
import argparse


class MultiFormatLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
       try:
            if self.file_path.endswith('.pdf'):
                return PyPDFLoader(self.file_path).load()
            elif self.file_path.endswith('.docx'):
                return Docx2txtLoader(self.file_path).load()
            elif self.file_path.endswith('.doc'):
                return UnstructuredWordDocumentLoader(self.file_path).load()
            elif self.file_path.endswith('xlsx'):
                return UnstructuredExcelLoader(self.file_path).load()
            else:
                return UnstructuredFileLoader(self.file_path).load()
       except Exception as e:
           raise ValueError(f"Failed to load {self.file_path}: {str(e)}")
class NWUKnowledgeTrainer:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="deepseek-r1:14b")
        self.exclude_files = ['.DS_Store', 'Thumbs.db']  # 排除系统文件

        #定义各目录的处理配置
        self.category_config = {
            "培养方案相关": {
                "chunk_size": 1500,
                "chunk_overlap": 400,
                "loader": MultiFormatLoader,
                "file_types": [".pdf"]
            },
            "日常生活相关": {
                "chunk_size": 800,
                "chunk_overlap": 150,
                "loader": MultiFormatLoader,
                "file_types": [".docx", ".pdf"]
            },
            "竞赛相关": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "loader": MultiFormatLoader,
                "file_types": [".pdf"]
            },
            "课程、考试资源相关": {
                "chunk_size": 1200,
                "chunk_overlap": 300,
                "loader": MultiFormatLoader,
                "file_types": [".pdf", ".docx",".doc"]
            },
            "选课考试相关": {
                "chunk_size": 1000,
                "chunk_overlap": 250,
                "loader": MultiFormatLoader,
                "file_types": [".docx",".pdf",".doc",".xlsx"]
            },


        }

    def clean_text(self, text: str) -> str:
        """清理文档文本"""
        # 去除特殊字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        # 合并多余空格和换行
        text = re.sub(r'\s+', ' ', text)
        # 移除文档头尾的无关信息
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return ' '.join(lines[:1000])  # 限制最大长度

    def load_category_documents(self, base_dir: str) -> List[Document]:
        """修复后的文档加载方法"""
        all_documents = []

        for category, config in self.category_config.items():
            category_dir = os.path.join(base_dir, category)
            if not os.path.exists(category_dir):
                print(f"⚠️ 目录不存在: {category_dir}")
                continue

            print(f"\n📂 正在处理类别: {category}")

            for root, _, files in os.walk(category_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    # 过滤文件
                    if any(exclude in file for exclude in self.exclude_files):
                        continue
                    if file_ext not in config["file_types"]:
                        continue

                    # 动态选择加载器
                    try:
                        if file_ext == '.pdf':
                            docs = PyPDFLoader(file_path).load()
                        elif file_ext == '.docx':
                            docs = Docx2txtLoader(file_path).load()
                        elif file_ext == '.doc':
                            docs = UnstructuredWordDocumentLoader(file_path).load()
                        elif file_ext == '.xlsx':
                            docs = UnstructuredExcelLoader(file_path).load()
                        else:
                            docs = UnstructuredFileLoader(file_path).load()

                        # 清洗和增强元数据
                        for doc in docs:
                            doc.metadata.update({
                                "category": category,
                                "source_path": file_path
                            })
                            doc.page_content = self.clean_text(doc.page_content)
                            all_documents.append(doc)
                            print(f"✅ 已加载: {file}")
                    except Exception as e:
                        print(f"❌ 加载失败 {file}: {str(e)}")

        return all_documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """根据类别使用不同策略分割文档"""
        split_docs = []

        for doc in documents:
            category = doc.metadata["category"]
            config = self.category_config.get(category, {})

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.get("chunk_size", 1000),
                chunk_overlap=config.get("chunk_overlap", 200),
                length_function=len
            )

            try:
                splits = splitter.split_documents([doc])
                for split in splits:
                    split.metadata.update(doc.metadata)  # 保留原始元数据
                split_docs.extend(splits)
            except Exception as e:
                print(f"分割文档出错: {str(e)}")
                continue

        return split_docs

    def train(self, docs_dir: str, db_dir: str):
        """训练知识库"""
        print("🔍 开始扫描文档目录...")
        documents = self.load_category_documents(docs_dir)

        if not documents:
            print("❌ 未找到任何有效文档，请检查目录结构")
            return False

        print(f"\n📑 共加载 {len(documents)} 个文档，开始分割...")
        splits = self.split_documents(documents)
        print(f"✂️ 分割为 {len(splits)} 个文本块")

        print("\n🧠 正在创建向量数据库...")
        try:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=db_dir,
                collection_metadata={
                    "hnsw:space": "cosine",
                    "institution": "西北大学"
                }
            )
            vectorstore.persist()

            print(f"\n🎉 知识库训练完成！")
            print(f"- 文档类别: {len(self.category_config)} 类")
            print(f"- 向量存储位置: {db_dir}")
            return True

        except Exception as e:
            print(f"❌ 创建向量数据库失败: {str(e)}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="西北大学知识库训练系统")
    parser.add_argument("--docs_dir", default="./数据集", help="文档根目录路径")
    parser.add_argument("--db_dir", default="./nwu_knowledge_v1", help="向量数据库存储路径")

    args = parser.parse_args()

    if not os.path.exists(args.docs_dir):
        print(f"⚠️ 文档目录不存在，正在创建标准目录结构...")
        os.makedirs(args.docs_dir)
        for category in ["培养方案相关", "日常生活相关", "竞赛相关",
                         "课程、考试资源相关", "选课考试相关", "学校概况"]:
            os.makedirs(os.path.join(args.docs_dir, category))
        print(f"✅ 已创建目录结构，请按类别放入文档后重新运行")
        print(f"目录结构:\n{args.docs_dir}")
        for root, dirs, _ in os.walk(args.docs_dir):
            level = root.replace(args.docs_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for d in dirs:
                print(f"{subindent}{d}/")
    else:
        trainer = NWUKnowledgeTrainer()
        success = trainer.train(args.docs_dir, args.db_dir)
        exit(0 if success else 1)