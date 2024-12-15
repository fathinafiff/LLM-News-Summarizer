from typing import List, Dict, Tuple
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from collections import Counter
import networkx as nx
import re

class CustomSummarizer:
    def __init__(self):
        self.indo_stopwords = set([
            "yang", "dan", "di", "ke", "dari", "pada", "dalam", "untuk", "dengan",
            "ini", "itu", "juga", "sudah", "saya", "anda", "akan", "bisa",
            "ada", "tidak", "saat", "oleh", "setelah", "seperti", "ketika",
            "bagi", "sampai", "karena", "sebuah", "tersebut", "dapat"
        ])
        
        # Common news-specific words to filter
        self.news_specific_words = set([
            "kata", "ujar", "menurut", "dijelaskan", "diberitakan",
            "dilaporkan", "disampaikan", "wartawan", "reporter"
        ])
        
    def clean_text(self, text: str) -> str:
        """Clean the text from unwanted patterns"""
        # Remove special characters and extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\n\r\t]', ' ', text)
        
        # Remove specific patterns
        patterns = [
            r'\(.*?\)',  # Text in parentheses
            r'["\'].*?["\']',  # Quoted text
            r'https?://\S+',  # URLs
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text)
            
        return text.strip()
    
    def get_sentence_vectors(self, sentences: List[str]) -> List[np.ndarray]:
        """Convert sentences to TF-IDF weighted vectors"""
        # Create word frequency dict across all sentences
        word_freq = Counter()
        sentence_words = []
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [w for w in words if w.isalnum() and 
                    w not in self.indo_stopwords and 
                    w not in self.news_specific_words]
            sentence_words.append(words)
            word_freq.update(words)
            
        # Create vocabulary
        vocab = list(word_freq.keys())
        
        # Calculate IDF
        num_docs = len(sentences)
        idf = {}
        for word in vocab:
            doc_count = sum(1 for words in sentence_words if word in words)
            idf[word] = np.log(num_docs / (1 + doc_count))
            
        # Create sentence vectors
        vectors = []
        for words in sentence_words:
            vector = np.zeros(len(vocab))
            word_counts = Counter(words)
            for word, count in word_counts.items():
                if word in vocab:
                    index = vocab.index(word)
                    tf = count / len(words)
                    vector[index] = tf * idf[word]
            vectors.append(vector)
            
        return vectors
    
    def sentence_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """Create similarity matrix between sentences"""
        vectors = self.get_sentence_vectors(sentences)
        num_sentences = len(sentences)
        similarity_matrix = np.zeros((num_sentences, num_sentences))
        
        for i in range(num_sentences):
            for j in range(num_sentences):
                if i != j:
                    similarity = 1 - cosine_distance(vectors[i], vectors[j])
                    similarity_matrix[i][j] = similarity
                    
        return similarity_matrix
    
    def rank_sentences(self, similarity_matrix: np.ndarray) -> np.ndarray:
        """Rank sentences using PageRank algorithm"""
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        return np.array(list(scores.values()))
    
    def position_score(self, index: int, total: int) -> float:
        """Calculate position-based importance score"""
        if index == 0:  # First sentence
            return 1.0
        elif index == total - 1:  # Last sentence
            return 0.5
        else:
            return 1.0 - (index / total)
    
    def get_key_phrases(self, text: str, num_phrases: int = 5) -> List[str]:
        """Extract key phrases using frequency and position"""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and 
                w not in self.indo_stopwords and 
                w not in self.news_specific_words]
        
        # Get word frequencies
        word_freq = Counter(words)
        
        # Get bigrams (pairs of consecutive words)
        bigrams = list(zip(words[:-1], words[1:]))
        bigram_freq = Counter(bigrams)
        
        # Score phrases based on frequency and word importance
        phrases = []
        for bigram, freq in bigram_freq.most_common(num_phrases * 2):
            phrase = ' '.join(bigram)
            # Score based on frequency and individual word importance
            score = freq * (word_freq[bigram[0]] + word_freq[bigram[1]])
            phrases.append((phrase, score))
            
        return [phrase for phrase, _ in sorted(phrases, key=lambda x: x[1], reverse=True)[:num_phrases]]
    
    def summarize(self, articles: List[str], num_sentences: int = 5) -> Tuple[List[str], str]:
        """Generate summary from multiple articles"""
        # Combine and clean articles
        combined_text = ' '.join(articles)
        cleaned_text = self.clean_text(combined_text)
        
        # Split into sentences
        sentences = sent_tokenize(cleaned_text)
        if len(sentences) <= num_sentences:
            return sentences, ' '.join(sentences)
            
        # Calculate similarity matrix
        similarity_matrix = self.sentence_similarity_matrix(sentences)
        
        # Get PageRank scores
        pagerank_scores = self.rank_sentences(similarity_matrix)
        
        # Calculate position scores
        position_scores = np.array([self.position_score(i, len(sentences)) 
                                  for i in range(len(sentences))])
        
        # Combine scores
        final_scores = 0.7 * pagerank_scores + 0.3 * position_scores
        
        # Select top sentences while maintaining order
        top_indices = np.argsort(final_scores)[-num_sentences:]
        top_indices = sorted(top_indices)
        
        selected_sentences = [sentences[i] for i in top_indices]
        
        # Extract key phrases
        key_phrases = self.get_key_phrases(cleaned_text)
        
        # Create formatted summary
        summary_parts = []
        for i, sent in enumerate(selected_sentences):
            # Highlight key phrases in the sentence
            highlighted_sent = sent
            for phrase in key_phrases:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                highlighted_sent = pattern.sub(f'*{phrase}*', highlighted_sent)
            summary_parts.append(highlighted_sent)
        
        final_summary = ' '.join(summary_parts)
        
        return selected_sentences, final_summary