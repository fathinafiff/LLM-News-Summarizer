def summarize_with_groq(api_key, text):
    """Send text and popular words to Groq API for summarization."""
    from groq import Groq

    client = Groq(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Prettier this Indonesia Summaries Article from News, based on this text: {text}, this come from more than 1 different news article in same topic, write output also in Bahasa Indonesia",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    return chat_completion.choices[0].message.content