from typing import List, Tuple, Dict
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import numpy as np
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class TextProcessor:
    def __init__(self, api_key: str = None):
        self.indo_stopwords = set([
            "yang", "dan", "di", "ke", "dari", "pada", "dalam", "untuk", "dengan",
            "ini", "itu", "juga", "sudah", "saya", "anda", "akan", "bisa",
            "ada", "tidak", "saat", "oleh", "setelah", "seperti", "ketika",
            "bagi", "sampai", "karena", "sebuah", "tersebut", "dapat"
        ])

        self.groq_client = None
        if api_key:
            self.groq_client = Groq(api_key=api_key)
    
    def clean_text(self, text: str) -> str:
        """
        Membersihkan teks dari karakter yang tidak diinginkan
        """
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\n\r\t]', ' ', text)
        
        patterns = ["ADVERTISEMENT", "SCROLL TO CONTINUE WITH CONTENT"]
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
        return text.strip()
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Memisahkan teks menjadi kalimat-kalimat
        """
        sentences = sent_tokenize(text)
        cleaned_sentences = [self.clean_text(sent) for sent in sentences]
        
        valid_sentences = [sent for sent in cleaned_sentences 
                         if len(sent.split()) >= 5]
        
        return valid_sentences
    
    def calculate_sentence_scores(self, sentences: List[str]) -> Dict[str, float]:
        """
        Menghitung skor setiap kalimat berdasarkan beberapa metrik
        """
        all_text = " ".join(sentences).lower()
        
        words = word_tokenize(all_text)
        words = [w for w in words if w.isalnum() and w not in self.indo_stopwords]
        word_freq = Counter(words)
        
        scores = {}
        for sentence in sentences:
            length_score = 1.0
            words_count = len(sentence.split())
            if words_count < 8 or words_count > 25:
                length_score = 0.8
                
            position_score = 1.0
            if sentences.index(sentence) == 0:  
                position_score = 1.2
                
            word_importance_score = 0
            sent_words = word_tokenize(sentence.lower())
            sent_words = [w for w in sent_words if w.isalnum()]
            for word in sent_words:
                if word not in self.indo_stopwords:
                    word_importance_score += word_freq[word]
            word_importance_score = word_importance_score / len(sent_words)
            
            final_score = (length_score * 0.3 + 
                         position_score * 0.3 + 
                         word_importance_score * 0.4)
            
            scores[sentence] = final_score
            
        return scores
    
    def extract_key_sentences(self, text: str, num_sentences: int = 5) -> List[str]:
        """
        Mengekstrak kalimat-kalimat penting dari teks
        """
        cleaned_text = self.clean_text(text)
        sentences = self.extract_sentences(cleaned_text)
        
        sentence_scores = self.calculate_sentence_scores(sentences)
        
        sorted_sentences = sorted(sentence_scores.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        top_sentences = [sent for sent, score in sorted_sentences[:num_sentences]]
        ordered_sentences = [sent for sent in sentences if sent in top_sentences]
        
        return ordered_sentences
    
    def prepare_llm_prompt(self, key_sentences: List[str]) -> str:
        """
        Menyiapkan prompt untuk LLM berdasarkan kalimat-kalimat penting
        """
        context = "\n".join([f"- {sent}" for sent in key_sentences])
        
        prompt = f"""Berikut adalah poin-poin penting dari beberapa artikel berita:

{context}

Tolong buatkan ringkasan yang koheren dalam Bahasa Indonesia dengan memperhatikan:
1. Hubungan antar kejadian/informasi
2. Urutan kronologis (jika relevan)
3. Fokus pada informasi penting
4. Hindari pengulangan

Ringkasan:"""
        
        return prompt

    def process_articles(self, articles: List[str]) -> Tuple[List[str], str]:
        """
        Process articles and generate summary
        """
        if not self.groq_client:
            raise ValueError("Groq client not initialized. Please provide API key during initialization.")
            
        # Combine all articles
        combined_text = " ".join(articles)
        
        # Extract key sentences
        key_sentences = self.extract_key_sentences(combined_text)
        
        # Prepare prompt for LLM
        prompt = self.prepare_llm_prompt(key_sentences)
        
        try:
            # Get summary from LLM
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=1000
            )
            summary = chat_completion.choices[0].message.content
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"
            
        return key_sentences, summary