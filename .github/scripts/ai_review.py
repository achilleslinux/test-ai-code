import os
import requests
from github import Github  # Requires PyGithub

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_diff_content():
    """Read the PR diff file."""
    with open('pr.diff', 'r') as f:
        diff = f.read().strip()
        if not diff:
            raise ValueError("❌ No changes detected in the diff.")
        return diff

def get_deepseek_review(diff: str) -> str:
    """Get AI review from DeepSeek."""
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # Or "deepseek-coder" for code-specific reviews
        "messages": [
            {
                "role": "system",
                "content": "You are an expert code reviewer. Provide concise feedback on:\n"
                           "1. Code quality\n2. Security risks\n3. Optimization opportunities\n"
                           "4. Specific actionable suggestions."
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
    response.raise_for_status()  # Raise HTTP errors
    return response.json()["choices"][0]["message"]["content"]

def post_github_comment(review: str):
    """Post the review as a comment on the PR."""
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️ Skipping GitHub comment (GITHUB_TOKEN not set)")
        return

    github = Github(os.getenv("GITHUB_TOKEN"))
    repo = github.get_repo(os.getenv("GITHUB_REPOSITORY"))
    pr = repo.get_pull(int(os.getenv("PR_NUMBER")))
    pr.create_issue_comment(f"## 🔍 DeepSeek Code Review\n\n{review}")

def main():
    try:
        print("🚀 Starting DeepSeek Code Review...")
        diff = get_diff_content()
        review = get_deepseek_review(diff)
        print("\n✅ Review Generated Successfully!")
        post_github_comment(review
