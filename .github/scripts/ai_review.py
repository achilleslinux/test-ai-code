import os
import openai
import requests
import json

# Init OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GitHub environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Load GitHub event payload
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

# Only proceed if the comment includes /review
comment_body = event.get("comment", {}).get("body", "")
if "/review" not in comment_body.lower():
    print("🛑 No /review command found in comment. Exiting.")
    exit(0)

# Determine PR number and repo
pr_number = event["issue"]["number"]
repo = event["repository"]["full_name"]

# Fetch PR diff
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
}
print(f"🔍 Fetching PR diff from {diff_url}")
diff_response = requests.get(diff_url, headers=headers)
diff = diff_response.text[:12000]  # Limit to prevent token overload

# Create prompt for OpenAI
messages = [
    {
        "role": "system",
        "content": (
            "You are a senior software engineer reviewing a GitHub pull request. "
            "Analyze the code changes and provide:\n"
            "- Code quality issues\n"
            "- Security concerns\n"
            "- Optimization suggestions\n"
            "- Specific, actionable feedback\n\n"
            "Be concise but cover all important points."
        )
    },
    {
        "role": "user",
        "content": f"Here is the diff of the PR:\n\n{diff}"
    }
]

# Call OpenAI API
print("🧠 Calling OpenAI API...")
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4,
    )
    review = response.choices[0].message.content
    print("✅ Review generated successfully.")
except Exception as e:
    review = f"⚠️ AI review generation failed: {str(e)}"
    print("❌ Error during API call:", str(e))

# Post review as a comment to the PR
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_data = {"body": f"## 🤖 AI Review\n\n{review}"}
comment_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

print("📤 Posting review comment to GitHub...")
response = requests.post(comment_url, headers=comment_headers, json=comment_data)

if response.status_code == 201:
    print("✅ Review posted to PR.")
else:
    print(f"❌ Failed to post comment: {response.status_code}")
    print(response.text)
