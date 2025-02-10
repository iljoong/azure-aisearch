"""
app.py: A simple Gradio app for searching Azure AI Search
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

def _search(query, method, page, category):
    # For demonstration, we just return the query wrapped in HTML tags
    skip = (page-1)*10

    if method == "keyword":
        results = azsch_keyword_query(query, skip, category)
        html_result, count = generate_html(results)
    elif method == "vector":
        results = azsch_vector_query(query, skip, category)
        html_result, count = generate_html(results)
    elif method == "hybrid":
        results = azsch_hybrid_query(query, skip, category)
        html_result, count = generate_html(results)
    elif method == "rerank":
        results = azsch_rerank_query(query, skip, category)
        html_result, count = generate_html_rerank(results)
    else:
        html_result = "No method selected"
        count = 0

    facets = results.get_facets()
    pages = (count-1) // 10 + 2

    html = f"""
<h1>Search Results for: {query}</h1>
<h3>Count: {count}</h3>
<h3>{_facet_html(facets)}</h3>

{html_result}
"""
    html += "<div style=\"display: flex; justify-content: center; align-items: center;\">Pages:"
    for i in range(1, pages):
        if i == page:
            html += f"{i} "
        else:
            html += f"<a href=\"#\" onclick=\"window.location.href = window.location.href + '&skip={i*10}';\">{i}</a> "
    html += "</div>" 
    return html, list(range(1, pages)), facets

# search + page dropdown update
def search(query, method, page, category):
    html, pages, facets = _search(query, method, page, category)
    categorys = ["전체"]
    for facet in facets:
        for value in facets[facet]:
            categorys.append(value['value'])

    return gr.update(elem_id="page_id", choices=pages), gr.update(elem_id="category_id", choices=categorys), html

def update_method(page):
    return [gr.update(elem_id="id_page", choices=[1]), 
            gr.update(elem_id="id_category", choices=["전체"])]

with gr.Blocks() as demo:
    label = gr.Label("AI Search Demo - Search Features")

    with gr.Row():
        with gr.Column():
            method_dd = gr.Dropdown(label="Search Method", choices=["keyword", "vector", "hybrid", "rerank"], value="keyword")
        with gr.Column():
            page_dd = gr.Dropdown(elem_id="id_page", label="Page", choices=[1], value=1)
        with gr.Column():
            category_dd = gr.Dropdown(elem_id="id_category", label="Category Filter", choices=["전체"], value="전체")

    search_input = gr.Textbox(
        show_label=False,
        placeholder = "Enter text and press enter. 해외 플레이")
    #submit_button = gr.Button("Submit")
    html_output = gr.HTML()

    #submit_button.click(fn=search, inputs=search_input, outputs=html_output)
    search_input.submit(fn=search, inputs=[search_input, method_dd, page_dd, category_dd], outputs=[page_dd, category_dd, html_output])
    method_dd.change(fn=update_method, inputs=[page_dd], outputs=[page_dd, category_dd])
    page_dd.change(fn=search, inputs=[search_input, method_dd, page_dd, category_dd], outputs=[page_dd, category_dd, html_output])
    category_dd.change(fn=search, inputs=[search_input, method_dd, page_dd, category_dd], outputs=[page_dd, category_dd, html_output])

demo.launch()