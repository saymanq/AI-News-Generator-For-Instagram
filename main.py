from newsapi import NewsApiClient
import ollama
from imaginairy.api import imagine
from imaginairy.schema import ImaginePrompt
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

def get_headlines():
    print(f"Starting to get headlines....")
    newsapi = NewsApiClient(api_key='e0afaca371df4a1aa7fdda7e5c45fd85')
    top_headlines = newsapi.get_top_headlines(category='technology', country='us')

    status = top_headlines['status']

    if status != 'ok':
        raise Exception("There was an error fetching news headlines")

    news_stories = {}
    for i in range(20):
        news_stories[top_headlines['articles'][i]['title']] = top_headlines['articles'][i]['description']
    
    print(f"Successfully received headlines....")
    return news_stories

def ask_llama3(prompt):
    response = ollama.chat(model = 'llama3', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    return response['message']['content']

def sort_for_usefullness(headlines):
    print(f"Started sorting headlines....")
    sorted_headlines = {}
    for headline, description in headlines.items():
        prompt = f"Classify the given headline as significant or not significant enough to be posted as important breaking news. News about important leaks about iphones and samsung phones are also significant. You can use the description of the headline for more context. (Respond with only 'yes' or 'no' and nothing else) Headline: {headline} | Description: {description}"
        response = ask_llama3(prompt).strip().lower()
        #print(headline)
        #print(response, end='\n')
        if response == 'yes':
            sorted_headlines[headline] = description

    print(f"Successfully sorted headlines....")
    return sorted_headlines

def create_text(headlines):
    print(f"Started Creating Text....")
    text_to_display = []
    for headline, description in headlines.items():
        prompt = f"Make the following headline into a single sentence or phrase with atmost 15 words and it should look like a headline. You can use the description of the headline also for more context.(Respond with only the sentence or phrase created and nothing else) Headline: {headline}. Description: {description}."
        response = ask_llama3(prompt).strip()
        text_to_display.append(response)
    
    print(f"Successfully Created Text....")
    return text_to_display

def create_images(headlines):
    print(f"Started Creating Images....")
    initial_prompts = []
    for headline, description in headlines.items():
        prompt = f"Analyze the headline and the description and pick an appropriate item that can be used as the best representation of the headline and description. Create a short description about that item that can be passed to Stable Diffusion to create an image. You can use the description of the headline also for more context. (Respond with only the description (for example: 'A futuristic-looking high-tech monitor with a sleek design, featuring a large 4K resolution screen and a unique 1000 Hz refresh rate, showcasing vibrant colors and crystal-clear images.') asked and nothing else) Headline: {headline}. Description: {description}."
        response = ask_llama3(prompt).strip()
        initial_prompts.append(f"{response}. Make it such that it is suitable to be used as a background for an instagram post with text on top.")
    
    prompts = []
    for prompt in initial_prompts:
        prompts.append(ImaginePrompt(f"{prompt}"))

    images_created = 0
    for number, result in enumerate(imagine(prompts)):
        result.save(f'/Users/syedaymanquadri/Documents/Programming/GitHub_Repos/Python/Projects/instagram-news-post-generator/outputs/generated/pic{number+1}.jpg')
        images_created += 1
    
    print(f"Successfully Created Images....")
    return images_created

def split_text(text):
    print(f"Started Splitting Text....")
    string = []
    words = text.split(' ')
    phrase = ''
    for word in words:
        if len(word) + len(phrase) > 42:
            string.append(phrase.strip())
            phrase = ''
        else:
            phrase += f"{word} "
    else:
        string.append(phrase.strip())

    print(f"Successfully Splitted Text....")
    return string

def fuse_image_and_text(no_of_images_created, texts_to_display):
    print(f"Started fusing image and text....")
    for num in range(no_of_images_created):
        img = Image.open(f'/Users/syedaymanquadri/Documents/Programming/GitHub_Repos/Python/Projects/instagram-news-post-generator/outputs/generated/pic{num + 1}.jpg')
        width, height = img.size

        enhancer = ImageEnhance.Brightness(img)
        img_brightness_reduced = enhancer.enhance(0.3)

        text = texts_to_display[num]
        lines = split_text(text)

        font = ImageFont.truetype('/Users/syedaymanquadri/Documents/Programming/GitHub_Repos/Python/Projects/instagram-news-post-generator/fonts/Roboto-Medium.ttf', 26) 
        text_width = font.getlength(lines[0])

        x = (width - text_width) / 2
        y = (height / 5) * 2

        draw = ImageDraw.Draw(img_brightness_reduced)
        for number in range(len(lines)):
            draw.text((x, y+(number*40)), f'{lines[number]}', font=font, fill=(255, 255, 255))

        img_brightness_reduced.save(f'/Users/syedaymanquadri/Documents/Programming/GitHub_Repos/Python/Projects/instagram-news-post-generator/imgs/post{num + 1}.jpg')
        print(f"Successfully fused and saved images....")

def main():
    print(f"Started Creating Instagram Posts....\n")
    headlines = get_headlines()
    final_headlines = sort_for_usefullness(headlines)
    texts_to_display = create_text(final_headlines)
    no_of_images_created = create_images(final_headlines)
    fuse_image_and_text(no_of_images_created, texts_to_display)
    print(f"\nSuccessfully Created Instagram Posts....")


if __name__ == '__main__':
    main()
