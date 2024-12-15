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
        
        self.news_specific_words = set([
            "kata", "ujar", "menurut", "dijelaskan", "diberitakan",
            "dilaporkan", "disampaikan", "wartawan", "reporter"
        ])

    def clean_text(self, text: str) -> str:
        """Clean the text from unwanted patterns"""
        # Remove special characters and extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\n\r\t]', ' ', text)
        text = re.sub(r'[\(\)\[\]\{\}"]', '', text)
        return text.strip()

    def calculate_sentence_scores(self, sentences: List[str]) -> np.ndarray:
        """Calculate sentence scores using multiple metrics"""
        num_sentences = len(sentences)
        scores = np.zeros(num_sentences)
        
        # 1. Position score
        for i in range(num_sentences):
            if i == 0:  # First sentence
                scores[i] += 3
            elif i == num_sentences - 1:  # Last sentence
                scores[i] += 1
            elif i < num_sentences // 3:  # First third
                scores[i] += 2
        
        # 2. Length score
        lengths = [len(sent.split()) for sent in sentences]
        avg_length = np.mean(lengths)
        for i, length in enumerate(lengths):
            if 0.6 * avg_length <= length <= 1.4 * avg_length:
                scores[i] += 1
        
        # 3. Word frequency score
        word_freq = Counter()
        for sent in sentences:
            words = word_tokenize(sent.lower())
            words = [w for w in words if w.isalnum() and 
                    w not in self.indo_stopwords and 
                    w not in self.news_specific_words]
            word_freq.update(words)
        
        for i, sent in enumerate(sentences):
            words = word_tokenize(sent.lower())
            words = [w for w in words if w.isalnum()]
            score = sum(word_freq[w] for w in words) / len(words) if words else 0
            scores[i] += score
        
        return scores / scores.max()  # Normalize scores

    def similarity_score(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between two sentences"""
        words1 = set(word_tokenize(sent1.lower()))
        words2 = set(word_tokenize(sent2.lower()))
        
        # Filter stopwords
        words1 = {w for w in words1 if w.isalnum() and w not in self.indo_stopwords}
        words2 = {w for w in words2 if w.isalnum() and w not in self.indo_stopwords}
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0

    def remove_redundant_sentences(self, sentences: List[str], scores: np.ndarray, 
                                 threshold: float = 0.4) -> List[int]:
        """Remove sentences that are too similar to higher-scored sentences"""
        num_sentences = len(sentences)
        selected_indices = []
        
        # Sort sentence indices by score
        sorted_indices = np.argsort(scores)[::-1]
        
        for idx in sorted_indices:
            # Check if this sentence is too similar to any already selected sentence
            is_redundant = False
            for selected_idx in selected_indices:
                similarity = self.similarity_score(sentences[idx], sentences[selected_idx])
                if similarity > threshold:
                    is_redundant = True
                    break
            
            if not is_redundant:
                selected_indices.append(idx)
        
        return selected_indices

    def summarize(self, articles: List[str], num_sentences: int = 5) -> Dict:
        """Generate summary with detailed processing steps"""
        process_details = {
            'original_articles': [],
            'cleaned_articles': [],
            'sentence_details': [],
            'selected_sentences': [],
            'final_summary': ''
        }

        # Step 1: Original articles and cleaning
        for idx, article in enumerate(articles, 1):
            process_details['original_articles'].append({
                'index': idx,
                'length': len(article),
                'text': article[:300] + '...' if len(article) > 300 else article
            })

        # Step 2: Clean and combine articles
        combined_text = ' '.join(articles)
        cleaned_text = self.clean_text(combined_text)
        
        # Step 3: Split into sentences
        sentences = sent_tokenize(cleaned_text)
        
        # Step 4: Calculate scores
        scores = self.calculate_sentence_scores(sentences)
        
        # Store sentence details
        for idx, (sentence, score) in enumerate(zip(sentences, scores)):
            words = word_tokenize(sentence.lower())
            important_words = [w for w in words if w.isalnum() and 
                             w not in self.indo_stopwords and 
                             w not in self.news_specific_words]
            
            process_details['sentence_details'].append({
                'index': idx + 1,
                'text': sentence,
                'length': len(words),
                'score': float(score),
                'position_score': 3 if idx == 0 else (1 if idx == len(sentences)-1 else 2 if idx < len(sentences)//3 else 0),
                'important_words': important_words
            })
        
        # Step 5: Remove redundant sentences
        selected_indices = self.remove_redundant_sentences(sentences, scores)
        selected_indices = sorted(selected_indices[:num_sentences])
        
        # Get final selected sentences
        selected_sentences = [sentences[i] for i in selected_indices]
        process_details['selected_sentences'] = [
            process_details['sentence_details'][i] for i in selected_indices
        ]
        
        # Create final summary
        process_details['final_summary'] = ' '.join(selected_sentences)
        
        return process_details