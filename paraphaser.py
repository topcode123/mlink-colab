import openai
import requests
import json

from Settings import OPENAI_TOKEN

openai.api_key = OPENAI_TOKEN


def paraphase_vi(paragraph):
    url = "https://api.momd.vn/paraphaser/paraphase-vi"

    payload = json.dumps({
        "paragraph": paragraph
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


def rewrite_article_gpt3(raw_data):
    # results = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt="viết lại đoạn văn sau bằng tiếng việt\n" + raw_data + "",
    #     temperature=0,
    #     max_tokens=len(raw_data) + 1,
    #     top_p=1,
    #     frequency_penalty=0.2,
    #     presence_penalty=0
    # )
    results = openai.Completion.create(
        model="text-davinci-003",
        prompt="in a suspensful and mysterious style rewrite text below\n" + raw_data + "",
        temperature=0,
        max_tokens=len(raw_data) + 1,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0
    )
    response = dict(results)

    openai_response = response['choices']
    print(openai_response[-1]['text'])
    return openai_response[-1]['text']
