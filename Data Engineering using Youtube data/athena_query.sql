SELECT a.title,
        a.category_id,
        b.snippet_title
        FROM "AwsDataCatalog"."glue-demo"."raw_statistics" a
INNER JOIN "AwsDataCatalog"."glue-demo-cleaned"."cleaned_statistics_reference_data" b
    ON a.category_id = b.id