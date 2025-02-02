# Azure AI Search

## SDK doc

- SearchIndexClient Class: https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.indexes.searchindexclient?view=azure-python
- SearchClient Class: https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.searchclient?view=azure-python

## Indexing

- schema: https://learn.microsoft.com/en-us/azure/search/search-what-is-an-index#schema-of-a-search-index
    - field type: https://learn.microsoft.com/en-us/rest/api/searchservice/supported-data-types
    - field attributes: https://learn.microsoft.com/en-us/azure/search/search-what-is-an-index#field-attributes
- Sample: https://learn.microsoft.com/en-us/azure/search/search-get-started-text?tabs=python

## Full text search

https://learn.microsoft.com/en-us/azure/search/search-lucene-query-architecture

## Additional features

- Hightlighting: https://learn.microsoft.com/en-us/azure/search/search-pagination-page-layout#hit-highlighting
- Synonyms: https://learn.microsoft.com/en-us/azure/search/search-synonyms?tabs=rest%2Crest-assign

## Ranking

AI Search score:

https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking#scores-in-a-hybrid-search-results

BM25 ranking:

https://learn.microsoft.com/en-us/azure/search/index-similarity-and-scoring#how-bm25-ranking-works

## Limits

https://learn.microsoft.com/en-us/azure/search/search-limits-quotas-capacity#index-limits

- maximum depth of complex fields: 10

## Download koream sample (pkl)

https://iktempstorage.blob.core.windows.net/aisearch/kor_proverbs_idioms.pkl?sp=r&st=2025-01-26T00:44:30Z&se=2025-03-01T08:44:30Z&spr=https&sv=2022-11-02&sr=b&sig=gyoWDrw9owkuwr9vw2AsbA3HRRIwtlgcO98ewHdTOT0%3D