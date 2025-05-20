name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install GitHub CLI
        run: sudo apt-get install -y gh

      - name: Get PR Diff
        id: get_diff
        run: |
          echo "Fetching PR diff..."
          gh pr diff ${{ github.event.pull_request.number }} > pr.diff
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Install OpenAI
        run: pip install openai

      - name: Run AI Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          mkdir -p .github/scripts
          cat << 'EOF' > .github/scripts/ai_review.py
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
