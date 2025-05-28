import os
import json
import openai
import requests
from github import Github

# Initialize OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load GitHub event payload
with open(os.getenv("GITHUB_EVENT_PATH")) as f:
    event = json.load(f)

comment_body = event.get("comment", {}).get("body", "").lower()

# Supported commands and their prompts
supported_commands = {
    "/review": "You're a senior code reviewer. Review the code patch and suggest improvements, flag issues, and explain why.",
    "/optimize": "You're a performance expert. Suggest performance optimizations and efficiency improvements.",
    "/security": "You're a security auditor. Identify vulnerabilities and suggest secure coding practices.",
    "/test": "You're a test engineer. Identify missing test cases and suggest unit or integration tests."
}

# Match the command
matched_command = next((cmd for cmd in supported_commands if cmd in comment_body), None)
if not matched_command:
    print("🛑 No valid command found.")
    exit(0)

# GitHub context
pr_number = event["issue"]["number"]
repo_name = event["repository"]["full_name"]

gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
commit = repo.get_commit(pr.head.sha)

comments = []
score_summary_blocks = []

for file in pr.get_files():
    if not file.patch:
        continue

    filename = file.filename
    patch = file.patch
    print(f"🔍 {matched_command} - Analyzing {filename}")

    # ---- INLINE FEEDBACK PROMPT ----
    feedback_messages = [
        {"role": "system", "content": supported_commands[matched_command]},
        {"role": "user", "content": f"File: {filename}\nPatch:\n{patch}"}
    ]

    # ---- SCORING PROMPT ----
    scoring_messages = [
        {
            "role": "system",
            "content": (
                "You're an AI code reviewer. Score this patch from 1 to 10 for:\n"
                "- Code Quality\n- Security\n- Performance\n- Test Coverage\n\n"
                "Provide a short summary.\nRespond in strict JSON:\n"
                "{\n"
                "  \"code_quality\": <1-10>,\n"
                "  \"security\": <1-10>,\n"
                "  \"performance\": <1-10>,\n"
                "  \"test_coverage\": <1-10>,\n"
                "  \"summary\": \"...\"\n}"
            )
        },
        {"role": "user", "content": f"File: {filename}\nPatch:\n{patch}"}
    ]

    # AI Feedback
    try:
        feedback = client.chat.completions.create(
            model="gpt-4",
            messages=feedback_messages,
            temperature=0.3,
            max_tokens=800
        ).choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI feedback error: {e}")
        feedback = None

    # AI Score
    try:
        raw_score = client.chat.completions.create(
            model="gpt-4",
            messages=scoring_messages,
            temperature=0.2,
            max_tokens=500
        ).choices[0].message.content.strip()

        print("🧠 Score JSON:", raw_score)
        score = json.loads(raw_score)

        # Build markdown block for summary
        score_summary_blocks.append(
            f"### 📊 `{filename}` Score\n"
            f"- Code Quality: **{score['code_quality']}**/10\n"
            f"- Security: **{score['security']}**/10\n"
            f"- Performance: **{score['performance']}**/10\n"
            f"- Test Coverage: **{score['test_coverage']}**/10\n"
            f"**Summary:** {score['summary']}\n"
        )
    except Exception as e:
        print(f"❌ Score JSON error: {e}")

    # Add inline comment on the first added line
    if feedback:
        for i, line in enumerate(patch.split("\n")):
            if line.startswith("+") and not line.startswith("+++"):
                comments.append({
                    "path": filename,
                    "position": i + 1,
                    "body": feedback
                })
                break

# ✅ Post inline review
if comments:
    print("📤 Posting inline review...")
    pr.create_review(
        body=f"🤖 AI Review triggered by `{matched_command}`",
        event="COMMENT",
        commit=commit,
        comments=comments
    )
    print("✅ Inline comments posted.")

# ✅ Post score summary as issue comment
if score_summary_blocks:
    summary_comment = "## 🧠 AI Review Scoring Summary\n" + "\n".join(score_summary_blocks)
    pr.create_issue_comment(summary_comment)
    print("✅ Score summary posted.")
else:
    print("⚠️ No score summary generated.")
