import os
import json
import openai
import requests
from github import Github

# OpenAI init
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load GitHub event
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
with open(GITHUB_EVENT_PATH) as f:
    event = json.load(f)

comment = event.get("comment", {}).get("body", "").lower()
supported_commands = {
    "/review": "You're a code review bot. Review this code patch for quality, bugs, and improvements.",
    "/optimize": "You're a performance expert. Suggest optimizations or efficiency improvements for this patch.",
    "/security": "You're a security auditor. Analyze this patch and report any security risks or hardening suggestions.",
    "/test": "You're a test strategist. Suggest test cases or identify missing test coverage for this patch."
}

# Determine which command is present
matched_command = next((cmd for cmd in supported_commands if cmd in comment), None)
if not matched_command:
    print("🛑 No supported command found.")
    exit(0)

# Extract info
pr_number = event["issue"]["number"]
repo_name = event["repository"]["full_name"]
gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
commit_id = pr.head.sha

# Go through each file
comments = []
for file in pr.get_files():
    if not file.patch:
        continue

    filename = file.filename
    patch = file.patch
    print(f"🔍 {matched_command} - Analyzing {filename}")

    # Set the prompt based on command
    prompt = supported_commands[matched_command]
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"File: {filename}\nPatch:\n{patch}"}
    ]

    # OpenAI call
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
        print(f"❌ Error: {str(e)}")
        continue

    # Approx inline position (1st added line)
    for i, line in enumerate(patch.split("\n")):
        if line.startswith("+") and not line.startswith("+++"):
            comments.append({
                "path": filename,
                "position": i + 1,
                "body": ai_comment
            })
            break

# Post comments
if comments:
    print("📤 Posting inline comments...")
    pr.create_review(
        body=f"🤖 AI Review triggered by `{matched_command}`",
        event="COMMENT",
        commit_id=commit_id,
        comments=comments
    )
    print("✅ Inline review posted.")
else:
    print("⚠️ No actionable comments generated.")
