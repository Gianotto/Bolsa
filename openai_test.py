import os
import openai

#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = ''
openai.Model.list()

openai.Completion.create(
  model = 'gpt-3.5-turbo',
  #engine = 'davinci-002',
  prompt = 'Make a list of astronomical observatories:'
)



response = openai.Image.create(
  prompt="a white siamese cat",
  n=1,
  size="1024x1024"
)
image_url = response['data'][0]['url']
print(image_url)