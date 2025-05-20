import openai
import os

def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")

    with open('pr.diff', 'r') as f:
        diff = f.read()

    prompt = f"""Review the following code changes and suggest improvements:
{diff}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    print("### AI Code Review Suggestion ###")
    print(response['choices'][0]['message']['content'])

if __name__ == "__main__":
    main()
