# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder

import openai
import os

load_dotenv(verbose=True, override=True)

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')
api_key = os.getenv('OPENAI_API_KEY')

# Example docs (replace with anything)
docs = [
    Document(content="My name is Jean and I live in Paris."), 
    Document(content="My name is Mark and I live in Berlin."), 
    Document(content="My name is Giorgio and I live in Rome.")
]

document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

prompt_template = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}}
Answer:
"""

retriever = InMemoryBM25Retriever(document_store=document_store)
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(api_key=Secret.from_token(api_key))

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']

    results = rag_pipeline.run(
        {
            "retriever": {"query": user_message},
            "prompt_builder": {"question": user_message},
        }
    )
    reply = results["llm"]["replies"]
    print(reply)

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
