# -*- coding: utf-8 -*-
"""RAG_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SjCgJRW_PXwsoxvJ3Nrlqh4RIj82SjcD
"""

! pip install langchain

! pip install -qU langchain-openai

import getpass
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()

import getpass
import os

os.environ["OPENAI_API_KEY"] = getpass.getpass()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

!pip install pdfplumber

from langchain.schema import Document
import pdfplumber
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Custom loader for PDF files
class PDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        try:
            full_text = []
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    full_text.append(page.extract_text())
            return "\n".join(full_text)
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

# 1. Load, chunk, and index the contents of the PDF file to create a retriever.
file_path = "Venelopee.pdf"

# Load the PDF file
text_content = PDFLoader(file_path=file_path).load()


# Wrap text content in Document objects
documents = [Document(page_content=text_content)]

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
splits = text_splitter.split_documents(documents)

# Create vector store and retriever
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 2. Incorporate the retriever into a question-answering chain.
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use five sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Create question-answering chain
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

response = rag_chain.invoke({"input": "Who is Venelope?"})
response["answer"]

response = rag_chain.invoke({"input": "Who is Caesar?"})
response["answer"]

response = rag_chain.invoke({"input": "Did Venelope die?"})
response["answer"]

response = rag_chain.invoke({"input": "Who helped Lila in finding the mirror?"})
response["answer"]

response = rag_chain.invoke({"input": "What is the theme of the poem in this story?"})
response["answer"]

response = rag_chain.invoke({"input": "Who is Mufasa?"})
response["answer"]

response = rag_chain.invoke({"input": "Who is Simba?"})
response["answer"]

response = rag_chain.invoke({"input": "Who likes to eat croissant?"})
response["answer"]

response = rag_chain.invoke({"input": "Name the various characters in this story?"})
response["answer"]

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

from langchain_core.messages import AIMessage, HumanMessage

chat_history = []

question = "Who is Venelope?"
ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=ai_msg_1["answer"]),
    ]
)

second_question = "Is she the queen of Animapolis?"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})

print(ai_msg_2["answer"])

chat_history = []

question = "Who is Lila?"
ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=ai_msg_1["answer"]),
    ]
)

second_question = "Who helps her in finding the mirror?"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})

print(ai_msg_2["answer"])

chat_history = []

question = "Who is Caesar?"
ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=ai_msg_1["answer"]),
    ]
)

second_question = "Which language did he know?"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})

print(ai_msg_2["answer"])

chat_history = []

question = "Who is the Queen?"
ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=ai_msg_1["answer"]),
    ]
)

second_question = "What did she like to eat?"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})

print(ai_msg_2["answer"])
