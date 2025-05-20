import os
from openai import OpenAI
from github import Github

def get_diff_content():
    """Read and return the diff content"""
    with open('pr.diff', 'r') as f:
        content = f.read().strip()
        if not content:
            raise ValueError("No changes detected in the diff file")
        return content

def get_ai_review(diff_content):
    """Get code review from OpenAI"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4",  # Correct model name for GPT-4
        messages=[
            {
                "role": "system",
                "content": """You are an expert code reviewer. Provide:
1. Code quality analysis
2. Potential bugs
3. Security concerns
4. Optimization suggestions
5. Specific actionable items"""
            },
            {
                "role": "user",
                "content": f"Review this code diff:\n{diff_content}"
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )
    return response.choices[0].message.content

def post_review_comment(review_text):
    """Post review as GitHub comment"""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Skipping GitHub comment - no GITHUB_TOKEN")
        return
        
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    pr = repo.get_pull(int(os.getenv("PR_NUMBER")))
    pr.create_issue_comment(f"## AI Code Review\n\n{review_text}")

def main():
    try:
        print("Starting code review process...")
        
        diff = get_diff_content()
        review = get_ai_review(diff)
        
        print("\n=== Review Results ===")
        print(review)
        
        post_review_comment(review)
        print("\nReview posted successfully!")
        
    except Exception as e:
        print(f"\nError during review process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
