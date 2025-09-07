from pipeline.extract import extract_pages
from pipeline.split import split_into_sections, split_into_chapters, split_into_articles
from pipeline.chunking import process_data
from pipeline.embed import process_data_with_embeddings 

pdf_path = "constitution of India.pdf"
pages = extract_pages(pdf_path)
sections = split_into_sections(pages)
chapters = split_into_chapters(sections)
articles = split_into_articles(chapters)
final_data = process_data(articles)
embedded_data = process_data_with_embeddings(final_data)
