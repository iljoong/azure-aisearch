"""
app_diff.py: A simple Gradio app for searching Azure AI Search
"""
import gradio as gr
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.models import (
    VectorizableTextQuery,
    VectorQuery,
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType)

import os

from dotenv import load_dotenv

load_dotenv("../.env")

service_endpoint = os.getenv("AZSCH_ENDPOINT")  
credential = AzureKeyCredential(os.environ["AZSCH_KEY"])

index_name = "ncfaqs-kor-index"
search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)


def azsch_keyword_query(query, skip=0, category="전체"):
    results = search_client.search(  
        search_text=query,  
        select=["title", "chunk", "category", "type", "parent_id"],
        facets=["category"],
        filter=f"category eq '{category}'" if category != "전체" else None,
        highlight_fields="chunk",
        highlight_pre_tag="<b style='color: yellow;'>",
        highlight_post_tag="</b>",
        query_language="ko-kr",
        include_total_count=True,
        skip=skip,
        top=10
    ) 

    return results

def azsch_vector_query(query, skip=0, category="전체"):
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="vector", exhaustive=True)

    # hightlight is not supported for pure vector search
    results = search_client.search(  
        search_text=None,  
        vector_queries=[vector_query],
        select=["title", "chunk", "category", "type", "parent_id"],
        facets=["category"],
        filter=f"category eq '{category}'" if category != "전체" else None,
        #highlight_fields="chunk",
        #highlight_pre_tag="<b style='color: yellow;'>",
        #highlight_post_tag="</b>",
        query_language="ko-kr",
        include_total_count=True,
        skip=skip,
        top=10
    ) 

    return results
        
def azsch_hybrid_query(query, skip=0, category="전체"):
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="vector", exhaustive=True)

    results = search_client.search(  
        search_text=query,  
        vector_queries=[vector_query],
        select=["title", "chunk", "category", "type", "parent_id"],
        facets=["category"],
        filter=f"category eq '{category}'" if category != "전체" else None,
        highlight_fields="chunk",
        highlight_pre_tag="<b style='color: yellow;'>",
        highlight_post_tag="</b>",
        query_language="ko-kr",
        include_total_count=True,
        skip=skip,
        top=10
    ) 

    return results 

def azsch_rerank_query(query, skip=0, category="전체"):
    #vector_query = VectorizedQuery(vector=generate_embeddings(query), k_nearest_neighbors=3, fields="vector")
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="vector", exhaustive=True)

    results = search_client.search(  
        search_text=query,  
        vector_queries=[vector_query],
        select=["title", "chunk", "category", "type", "parent_id"],
        facets=["category"],
        filter=f"category eq '{category}'" if category != "전체" else None,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='semantic-config',
        query_caption=QueryCaptionType.EXTRACTIVE,
        #query_answer=QueryAnswerType.EXTRACTIVE,
        highlight_pre_tag="<b style='color: yellow;'>",
        highlight_post_tag="</b>",
        query_language="ko-kr",
        include_total_count=True,
        skip=skip,
        top=10 # for limiting text search
    )

    return results

def generate_html(results):

    html = ""
    for result in results:
        if (result["@search.highlights"]):
            html += f"""<div>
{result['@search.score']:.5f}:[{result['category']}] <a href=\"https://www.nightcrows.co.kr/help/faq/{result['parent_id']}?wmsso_sign=check\">{result['title']}</a>"""
            for highlight in result['@search.highlights']['chunk']:
                html += f"<p>{highlight}</p>"
            html += "</div><hr>"
        else:
            html += f"""<div>
{result['@search.score']:.5f}:[{result['category']}] <a href=\"https://www.nightcrows.co.kr/help/faq/{result['parent_id']}?wmsso_sign=check\">{result['title']}</a>
</div><hr>"""

    return html, results.get_count()

def generate_html_rerank(results):

    try:
        html = ""
        for result in results:  
            # rerank score for only 50 results
            if result['@search.reranker_score']:
                score = result['@search.reranker_score']
            else:
                score = result['@search.score']

            if result["@search.captions"]:
                caption = result["@search.captions"][0]
                html += f"""<div>
    {score:.5f}:[{result['category']}] <a href=\"https://www.nightcrows.co.kr/help/faq/{result['parent_id']}?wmsso_sign=check\">{result['title']}</a>
    <p>{caption.highlights}</p>
    </div><hr>"""
            else:
                html += f"""<div>
    {score:.5f}:[{result['category']}] <a href=\"https://www.nightcrows.co.kr/help/faq/{result['parent_id']}?wmsso_sign=check\">{result['title']}</a>
    </div><hr>"""

        return html, results.get_count()
    except Exception as e:
        print(html)
        print(e)
        return "", 0
 
def _facet_html(facets):
    html = ""
    for facet in facets:
        for value in facets[facet]:
            html += f"{value['value']}({value['count']}) "
    return html

# search + page dropdown update
def search(query):

    keyword_results = azsch_keyword_query(query)
    _keyword_html, count = generate_html(keyword_results)
    keyword_html = f"""
    <h1>Keyword Search Result for: {query}</h1>
    <h3>Count: {count}</h3>

    {_keyword_html}"""

    rerank_results = azsch_rerank_query(query)
    _rerank_html, count = generate_html_rerank(rerank_results)
    rerank_html = f"""
    <h1>Rerank Search Results for: {query}</h1>
    <h3>Count: {count}</h3>

    {_rerank_html}"""

    return keyword_html, rerank_html


with gr.Blocks() as demo:
    label = gr.Label("AI Search Demo- Search Methods Comparison")

    search_input = gr.Textbox(
        show_label=False,
        placeholder = "Enter text and press enter. 해외 플레이")
    with gr.Row():
        with gr.Column():
            keyword_output = gr.HTML()
        with gr.Column():
            rerank_output = gr.HTML()

    #submit_button.click(fn=search, inputs=search_input, outputs=html_output)
    search_input.submit(fn=search, inputs=[search_input], outputs=[keyword_output, rerank_output])

demo.launch()