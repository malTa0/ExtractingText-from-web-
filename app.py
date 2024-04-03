from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display
import os
import uuid

app = Flask(__name__)

def get_important_words(url):
    stop_words = set(open("stopwords.txt", 'r', encoding="utf-8").read().split())
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = ""
                     
    for content in soup.find_all(['a','h1','h2','h3','span']):
        text += content.text.strip() + " "
    words = [word.lower() for word in text.split() if word not in stop_words and len(word) > 3]
    return words 

def generate_wordcloud(url):
    try:
        important_words = get_important_words(url)
        words_text = " ".join(important_words)
        reshaped_text = arabic_reshaper.reshape(words_text)
        text = get_display(reshaped_text)
        font_path = "Amiri-Bold.ttf"
        # Generate a word cloud
        wordcloud = WordCloud(width=800, height=800, 
                              background_color='white', 
                              stopwords=None, 
                              min_font_size=10,
                              font_path=font_path).generate(text)

        # Save the word cloud image with a unique name
        image_filename = str(uuid.uuid4()) + '.png'
        image_path = os.path.join('static', image_filename)
        wordcloud.to_file(image_path)
        return image_filename
    except Exception as e:
        print(e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    images = []
    if request.method == 'POST':
        urls = request.form.getlist('url')
        if urls:
            for url in urls:
                image_filename = generate_wordcloud(url)
                if image_filename:
                    images.append(image_filename)
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
