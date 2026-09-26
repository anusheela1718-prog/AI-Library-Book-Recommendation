# S3 bucket layout

```
YOUR-BUCKET-NAME/
├── index.html, recommendations.html, history.html, book-details.html   (website, public)
├── css/  js/  assets/                                                  (website, public)
├── images/    book covers B001.svg ...                                 (public, shown on the website)
├── dataset/   books.csv                                                (PRIVATE - only Lambda reads it)
└── model/     tfidf_model.json                                         (PRIVATE - only Lambda uses it)
```

Only website files and images are public (see `bucket-policy.json`). `dataset/` and `model/` stay private.
Website hosting is HTTP only. (HTTPS would need CloudFront - not required for this project.)
