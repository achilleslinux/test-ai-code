import os
import openai
import requests
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Load GitHub event info
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo = event["repository"]["full_name"]

# Get the PR diff
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
}
diff_response = requests.get(diff_url, headers=headers)
diff = diff_response.text[:12000]  # Truncate for token safety

# Prepare OpenAI message
messages = [
    {"role": "system", "content": "You are an experienced software engineer reviewing a GitHub pull request. Give clear, constructive feedback."},
    {"role": "user", "content": f"Please review the following GitHub pull request diff:\n\n{diff}"}
]

# Get review from ChatGPT
response = openai.ChatCompletion.create(
    model="gpt-4",  # Uses GPT-4-turbo
    messages=messages,
    temperature=0.5,
)

review = response.choices[0].message.content

# Post review comment
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_data = {"body": review}
comment_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
requests.post(comment_url, headers=comment_headers, json=comment_data)
