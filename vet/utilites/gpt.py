from g4f.client import Client

client = Client()
mess = []
def gpt(promt):
    mess.append({"role": "user", "content": promt})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mess,
        web_search=False
    )
    mess.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content
