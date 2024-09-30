# Advance-File-Search---AI-Agent

This repository contains the implementation of an Advanced File Search System that utilizes an agent-based approach for intelligent and efficient file retrieval. The system is designed to handle complex user queries and retrieve files based on metadata, file insights, and various constraints like file type, size, time range, and more.

# Features:
Vectorized Search with Chroma DB: Utilizes vector embeddings to represent generated insights, enabling similarity-based search across stored files.
Dynamic Insight Generation: File descriptions are generated using static templates or a generative model, and converted into embeddings for more accurate matching.
Customizable Query Constraints: Supports multiple constraints, including file type (PDF, DOCX, etc.), file size limits, date of creation/modification, source (e.g., Google Drive), and file location in the cloud.
Efficient Filtering: Allows filtering based on complex criteria such as file size, upload date, file format, and specific folders.
Similarity-Based Retrieval: Matches user queries with the most relevant file descriptions and metadata using vector embeddings and returns file metadata (name, size, date, URL).
File Metadata Storage: Stores file metadata and embeddings in a vector database (Chroma DB) for quick and efficient retrieval.

# Potential Advancements:
Advanced Vectorization: Leverage stronger models like BERT or Sentence Transformers for better embedding representations.
Additional Filters: Add support for more constraints like access permissions, content-based search, geolocation, and multi-cloud sources.
Enhanced Ranking: Implement ranking algorithms to prioritize search results based on relevance, recency, or user preferences.

# Use Cases:
Team Meeting File Retrieval: Easily locate the most recent team meeting file or specific meetings by date or type.
Product/Feature-Based Search: Retrieve files related to specific products or features, including those uploaded within a particular time frame.
Cloud Source-Specific Search: Filter results based on file source (e.g., Google Drive) and format (e.g., PDFs).
Efficient Document Management: Manage large collections of files across cloud platforms with intelligent, fast search capabilities.

# Technologies Used:
Python: Core language for system implementation.
Chroma DB: Vector database for storing embeddings and metadata.
Vectorization Models: For generating embeddings of file insights and user queries.
