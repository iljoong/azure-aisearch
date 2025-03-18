## Prepare Test Sample

- Create a BASIC sku Azure SQL Database.
    - Add an `AdventureWorksLT` sample as a test sample.
- Create a view for data source.

```sql
CREATE VIEW vNcArticles AS
SELECT 
    p.ProductID as article_id,
    p.ProductCategoryID as board_id,
    p.ProductNumber as game_code,
    p.ModifiedDate as updated_at,
    p.Name as title,
    pd.Description as content
FROM 
    SalesLT.Product p
JOIN 
    SalesLT.ProductModel pm ON p.ProductModelID = pm.ProductModelID
JOIN 
    SalesLT.ProductModelProductDescription pdm ON pm.ProductModelID = pdm.ProductModelID
JOIN 
    SalesLT.ProductDescription pd ON pdm.ProductDescriptionID = pd.ProductDescriptionID
WHERE 
    pdm.Culture = 'en'; -- Adjust culture code as needed
```

## Reference

SqlDB datasource:
https://learn.microsoft.com/en-us/azure/search/search-how-to-index-sql-database?tabs=portal-check-indexer

skillset:
- **concept**:https://learn.microsoft.com/en-us/azure/search/cognitive-search-working-with-skillsets
- https://learn.microsoft.com/en-us/azure/search/cognitive-search-defining-skillset
- skills:
    - AzureOpenAIEmbedding: https://learn.microsoft.com/en-us/azure/search/cognitive-search-skill-azure-openai-embedding
    - Translation: https://learn.microsoft.com/en-us/azure/search/cognitive-search-skill-text-translation
        - billable: https://learn.microsoft.com/en-us/azure/search/cognitive-search-attach-cognitive-services
        - free account supports upto 20 translations only
    - Custom API: https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api

Index projection:
- https://learn.microsoft.com/en-us/azure/search/search-how-to-define-index-projections?tabs=rest-create-index

python SDK:
- translation: https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.indexes.models.texttranslationskill?view=azure-python
- filedmapping: https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.indexes.models.fieldmapping?view=azure-python