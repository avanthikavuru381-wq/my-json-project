import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # loads GROQ_API_KEY from .env

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

def chat(user_message, system_prompt='You are a professor.'):
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',  # free & fast
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user',   'content': user_message}
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# ── Test it ──────────────────────────────────────────────
if __name__ == '__main__':
    # Basic test
    print('=== Basic Chat ===')
    reply = chat('What is Agentic AI in 2 sentences?')
    print(reply)

    # Custom persona test
    print('\n=== Pirate Bot ===')
    reply = chat(
        'Tell me about machine learning',
        system_prompt='You are a pirate who explains tech concepts.'
    )
    print(reply)

    # Token info
    print('\n=== Token Usage ===')
    r = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role':'user','content':'Hello!'}]
    )
    print(f'Prompt tokens:     {r.usage.prompt_tokens}')
    print(f'Completion tokens: {r.usage.completion_tokens}')
    print(f'Total tokens:      {r.usage.total_tokens}')
