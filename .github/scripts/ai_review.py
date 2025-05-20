import os
import requests
from github import Github

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_diff_content():
    """Read the PR diff file."""
    with open('pr.diff', 'r') as f:
        diff = f.read().strip()
        if not diff:
            raise ValueError("No changes detected in the diff.")
        return diff

def get_deepseek_review(diff: str) -> str:
    """Get AI review from DeepSeek."""
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert code reviewer. Analyze the PR diff and provide:\n"
                           "1. Code quality issues\n"
                           "2. Security risks\n"
                           "3. Optimization suggestions\n"
                           "4. Specific actionable feedback."
            },
            {
                "role": "user",
                "content": f"Review this code diff:\n{diff}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def post_github_comment(review: str):
    """Post the review as a comment on the PR."""
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("PR_NUMBER"))
    
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(f"## 🔍 DeepSeek Code Review\n\n{review}")

def main():
    try:
        print("🚀 Starting DeepSeek Code Review...")
        diff = get_diff_content()
        review = get_deepseek_review(diff)
        print("\n📝 Review Generated Successfully!")
        post_github_comment(review)
        print("✅ Posted review on GitHub PR!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
