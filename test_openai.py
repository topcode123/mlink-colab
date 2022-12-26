import openai


def gpt_processing(raw_data):
    openai.api_key = ""
    print("raw data len: ", len(raw_data) + 1)
    gpt_data_convert_dictionary = openai.Completion.create(
        model="text-davinci-002",
        prompt=raw_data,
        max_tokens=len(raw_data) + 1,
    )
    return gpt_data_convert_dictionary["choices"][0]["text"].strip()


def GPT_Completion(texts):
    ## Call the API key under your account (in a secure way)
    response = openai.Completion.create(
        engine="",
        prompt=texts,
        temperature=0.6,
        top_p=1,
        max_tokens=64,
        frequency_penalty=0,
        presence_penalty=0
    )
    return print(response.choices[0].text)


GPT_Completion("hello world")
