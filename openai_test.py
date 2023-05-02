import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()

openai.Completion.create(
  engine="davinci",
  prompt="Make a list of astronomical observatories:"
)