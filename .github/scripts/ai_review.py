import os
from openai import OpenAI
from github import Github

def get_diff_content():
    with open('pr.diff', 'r') as f:
        return f.read().strip()

def analyze_with_gpt4(diff):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """You are an expert code reviewer. Analyze the diff and provide:
1. Code quality assessment
2. Potential bugs/edge cases
3. Security concerns
4. Optimization suggestions
5. Specific actionable recommendations"""
            },
            {
                "role": "user",
                "content": f"Review this code diff:\n{diff}"
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )
    return response.choices[0].message.content

def post_github_comment(review):
    gh_token = os.getenv("GH_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not (gh_token and repo_name and pr_number):
        print("Skipping GitHub comment - missing GH_TOKEN, REPO, or PR_NUMBER")
        return

    g = Github(gh_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    pr.create_issue_comment(f"## 🤖 GPT-4 Code Review\n\n{review}")

def main():
    try:
        print("🔍 Starting GPT-4 code review...")

        diff = get_diff_content()
        if not diff:
            raise ValueError("Empty diff - no changes to review")

        review = analyze_with_gpt4(diff)
        print("\n✅ Review completed:")
        print(review)

        post_github_comment(review)

    except Exception as e:
        print(f"❌ Review failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
