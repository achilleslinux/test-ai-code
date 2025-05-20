from openai import OpenAI
import os

def main():
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open('pr.diff', 'r') as f:
            diff = f.read()

        prompt = """Please review these code changes and provide:
1. Brief feedback on code quality
2. Potential improvements
3. Any obvious issues

Diff:
{}
""".format(diff)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        print("\n### AI Code Review ###")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"\n⚠️ Error in AI review: {str(e)}")
        print("Note: GPT-3.5 requires OpenAI API credits (free tier may be limited)")

if __name__ == "__main__":
    main()
EOF
          python3 .github/scripts/ai_review.py
