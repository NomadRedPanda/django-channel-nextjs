from django.shortcuts import render
from chat.llm_config import get_client,get_completion


def test_llm(request):
    LLM_MODEL = "gemini-2.0-flash-exp"
    client = get_client(llm_model=LLM_MODEL)
    completion = client.chat.completions.create(
      model=LLM_MODEL,
      messages=[
        {
          "role": "user",
          "content": "tell me a joke"
        }
      ]
    )
    response = completion.choices[0].message.content
    context={
        "user_prompt":"A joke",
        "response": response
    }

    return render(request, "chat/llm_test.html", context)