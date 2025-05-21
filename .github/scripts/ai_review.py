import os
import openai
import requests
import json

# Set API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Load GitHub event info
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo = event["repository"]["full_name"]

# Get PR diff
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
}
diff_response = requests.get(diff_url, headers=headers)
diff = diff_response.text[:12000]  # Trim for token safety

# Prepare messages
messages = [
    {"role": "system", "content": "You are an experienced software engineer reviewing a GitHub pull request. Give clear, constructive feedback."},
    {"role": "user", "content": f"Please review the following GitHub pull request diff:\n\n{diff}"}
]

# Call GPT-4
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    temperature=0.5,
)

review = response.choices[0].message.content

# Post comment to PR
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_data = {"body": review}
comment_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
requests.post(comment_url, headers=comment_headers, json=comment_data)
