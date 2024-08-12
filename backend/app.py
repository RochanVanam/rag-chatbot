# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from newsapi import NewsApiClient

import openai
import os

load_dotenv(verbose=True, override=True)

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

# News API
news_api_key = os.getenv('NEWS_API_KEY')
newsapi = NewsApiClient(api_key=news_api_key)

# get all articles
TOPIC = 'crypto' # change this to anything
all_articles = newsapi.get_everything(q=TOPIC,
                                      language='en',
                                      sort_by='publishedAt',)

articles = all_articles['articles']

docs = []
for i, article in enumerate(articles):
    if i >= 50:
        break
    content = article['content']
    document = Document(content=content)
    docs.append(document)
    i += 1

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
llm = OpenAIGenerator(api_key=Secret.from_token(openai_api_key))

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
