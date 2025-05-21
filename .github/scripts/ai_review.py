import os
import openai
import requests
import json

# ✅ Init OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ GitHub environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# ✅ Load event JSON
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo = event["repository"]["full_name"]

# ✅ Fetch PR diff
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
}
print(f"🔍 Fetching PR diff from {diff_url}")
diff_response = requests.get(diff_url, headers=headers)
diff = diff_response.text[:12000]  # Limit input size

# ✅ Prepare OpenAI message
messages = [
    {
        "role": "system",
        "content": "You are an experienced software engineer reviewing a GitHub pull request. Provide a concise, constructive code review."
    },
    {
        "role": "user",
        "content": f"Please review this GitHub PR diff:\n\n{diff}"
    }
]

# ✅ Call OpenAI API
print("🧠 Calling OpenAI API...")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use gpt-4 if you regain quota/access
        messages=messages,
        temperature=0.5,
    )
    review = response.choices[0].message.content
    print("✅ Received review:\n", review)
except Exception as e:
    print("❌ OpenAI API call failed:", str(e))
    review = "⚠️ Failed to generate AI review due to API error."

# ✅ Post comment to GitHub PR
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_data = {"body": review}
comment_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
print("📤 Posting comment to PR...")

resp = requests.post(comment_url, headers=comment_headers, json=comment_data)

if resp.status_code != 201:
    print(f"❌ Failed to post comment: {resp.status_code}")
    print(resp.text)
else:
    print("✅ Comment posted successfully.")
