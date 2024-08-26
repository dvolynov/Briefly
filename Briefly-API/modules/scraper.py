import requests
from bs4 import BeautifulSoup


class Scraper:

    def __call__(self, topics):
        result = []

        for topic, url in topics.items():
            response = requests.get(url)
            k = 0

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                a_list = soup.select(f'div#container-{topic.lower()} ul li div div a')
                articles = ["https://www.theguardian.com" + a.get('href') for a in a_list]
                for link in articles:
                    if link:
                        result.append({
                            'topic': topic,
                            'link': link

                        })
                        k += 1
            print(topic, k)
        return result