import os
import cv2
import requests
import json


def generate_text(api_key, prompt):
    url = "https://api.openai.com/v1/engines/text-davinci-002/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 50
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        if response.status_code == 401:
            raise ValueError("API key tidak valid. Harap periksa kembali API key Anda.")
        elif response.status_code == 429:
            raise ValueError(f"{response.json()}")
        else:
            raise ValueError(f"Terjadi kesalahan saat mengakses API: {response.json()}")

    try:
        return response.json()['choices'][0]['text'].strip()
    except KeyError:
        raise ValueError("API key tidak valid. Segera cek API key Anda.")

def translate_text(api_key, text, target_language="en"):
    prompt = f"Translate the following text to {target_language}: {text}"
    translated_text = generate_text(api_key, prompt)
    return translated_text

def generate_image(api_key, prompt, output_file):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "image-alpha-001",
        "prompt": prompt,
        "num_images": 1,
        "size": "256x256",
        "response_format": "url"
    }
    response = requests.post(url, headers=headers, json=data)
    image_url = response.json()['data'][0]['url']
    image_data = requests.get(image_url).content
    with open(output_file, 'wb') as f:
        f.write(image_data)

def create_video_from_images(image_folder, video_name, fps=30):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    images.sort()

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()
    print("Video created successfully")

chatgpt_api_key = "input_your_api_key_here"
dalle_api_key = "input_your_api_key_here"

prompt = input("Masukkan cerita atau deskripsi: ")

try:
    translated_prompt = translate_text(chatgpt_api_key, prompt)

    generated_text = generate_text(chatgpt_api_key, translated_prompt)
except ValueError as e:
    print(f"{e}")
    exit()

image_descriptions = generated_text.split(". ")
for i, description in enumerate(image_descriptions):
    if not description:
        continue
    print(f"Generating image for: {description}")
    output_file = f"images/image_{i+1}.png"
    generate_image(dalle_api_key, description, output_file)

create_video_from_images("images", "output_video.mp4", fps=5)
