from openai import OpenAI
import os

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open('pr.diff', 'r') as f:
        diff = f.read()

    prompt = f"""Please review these code changes and provide constructive feedback:
1. Identify potential bugs
2. Suggest improvements
3. Note any security concerns
4. Keep comments concise

Code changes:
{diff}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        print("\n### AI Code Review ###")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error during AI review: {str(e)}")

if __name__ == "__main__":
    main()
EOF
          python3 .github/scripts/ai_review.py
