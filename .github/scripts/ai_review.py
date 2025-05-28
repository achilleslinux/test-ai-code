import os
import json
import openai
import requests
from github import Github

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load GitHub event payload
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

comment_body = event.get("comment", {}).get("body", "").lower()

# Supported commands and their prompts
supported_commands = {
    "/review": "You're a senior code reviewer. Review the code patch and suggest improvements, flag issues, and explain why.",
    "/optimize": "You're a performance expert. Suggest performance optimizations and efficiency improvements.",
    "/security": "You're a security auditor. Identify vulnerabilities and suggest secure coding practices.",
    "/test": "You're a test engineer. Identify missing test cases and suggest unit or integration tests."
}

# Find the command in the comment
matched_command = next((cmd for cmd in supported_commands if cmd in comment_body), None)
if not matched_command:
    print("🛑 No valid command found in comment.")
    exit(0)

# GitHub context
pr_number = event["issue"]["number"]
repo_name = event["repository"]["full_name"]

# Initialize GitHub client
gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Get full commit object (NOT just SHA)
commit = repo.get_commit(pr.head.sha)

# Prepare inline review comments
comments = []

for file in pr.get_files():
    if not file.patch:
        continue

    filename = file.filename
    patch = file.patch
    print(f"🔍 {matched_command} - Analyzing {filename}")

    messages = [
        {"role": "system", "content": supported_commands[matched_command]},
        {"role": "user", "content": f"File: {filename}\nPatch:\n{patch}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
        ai_comment = response.choices[0].message.content.strip()
        print(f"✅ AI response for {filename}")
    except Exception as e:
        print(f"❌ OpenAI error for {filename}: {str(e)}")
        continue

    # Post comment at first added line
    for i, line in enumerate(patch.split("\n")):
        if line.startswith("+") and not line.startswith("+++"):
            comments.append({
                "path": filename,
                "position": i + 1,
                "body": ai_comment
            })
            break

# Submit the GitHub PR review with inline comments
if comments:
    print("📤 Posting inline comments...")
    pr.create_review(
        body=f"🤖 AI Review triggered by `{matched_command}`",
        event="COMMENT",
        commit=commit,  # ✅ Must be a Commit object
        comments=comments
    )
    print("✅ Inline review posted.")
else:
    print("⚠️ No actionable comments generated.")
