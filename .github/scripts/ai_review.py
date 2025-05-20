from openai import OpenAI
import os

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open('pr.diff', 'r') as f:
        diff = f.read()

    prompt = f"""Review the following code changes and suggest improvements:
{diff}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    print("### AI Code Review Suggestion ###")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
