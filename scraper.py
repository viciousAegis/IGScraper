from instagrapi import Client
import pandas as pd
import requests
import os
import time
import datetime

ACCOUNT_USERNAME = "foodenjoyer2" # create multiple accounts to avoid rate limit
ACCOUNT_PASSWORD = "jBTYiC9ze7wuVZZ"

# ACCOUNT_USERNAME = "dont_care_10101" # create multiple accounts to avoid rate limit
# ACCOUNT_PASSWORD = "akshit"

class InstaScraper():
    def __init__(self, last_date):
        self.api = Client()
        self.hashtags = []
        self.amount = 100
        self.curr_hashtag = None
        self.curr_date = None
        self.last_date = last_date
    
    def login(self):
        self.api.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
    
    def set_hashtags(self, hashtags):
        self.hashtags = hashtags
    
    def set_amount(self, amount):
        self.amount = amount
    
    def __get_posts(self, hashtag):
        print('Getting posts for hashtag: ', hashtag)
        return self.api.hashtag_medias_recent(hashtag, amount=self.amount)


    def __convert_to_df(self, posts):
        postsToAnalyze = []
        for post in posts:
            postDict = {}
            for item in post:
                postDict[item[0]] = item[1]
            postsToAnalyze.append(postDict)
        return pd.DataFrame.from_records(postsToAnalyze)

    def __save_image(self, url, file_name):
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_name, 'wb+') as f:
                f.write(response.content)
        else:
            print('Error: ', response.status_code)
    
    def __save_images(self, df, dir_path):
        # create an images folder
        if not os.path.exists(dir_path + '/images'):
            os.makedirs(dir_path + '/images')
            
        for row in df[['pk','thumbnail_url','resources']].itertuples(index=False):
            url = row[1]
            pk = str(row[0])
            resources = row[2]
            if(url != None):
                self.__save_image(url, dir_path + '/images/post_' + pk + '.jpg')
            else:
                for resource in resources:
                    pk = str(resource).split("'")[1]
                    url = str(resource).split("'")[3]
                    self.__save_image(url, dir_path + '/images/post_' + pk + '.jpg')
    
    def __save_to_csv(self, df, dir_path):
        with open(dir_path + '/posts_data.csv', 'w+') as f:
            df.to_csv(f, index=False)
    
    def __check_for_duplicates(self, df, prev_csv_path):
        if os.path.exists(prev_csv_path):
            prev_df = pd.read_csv(prev_csv_path)
            prev_pks = prev_df['pk'].tolist()
            df = df[~df['pk'].isin(prev_pks)]
        return df

    def __save_data(self, df):
        self.curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if not os.path.exists('posts/'+self.curr_hashtag+'/'+self.curr_date):
            os.makedirs('posts/'+self.curr_hashtag+'/'+self.curr_date)
        
        dir_path = 'posts/'+self.curr_hashtag+'/'+self.curr_date
        
        self.__save_to_csv(df, dir_path)
        self.__save_images(df, dir_path)
    
    def scrape_hashtag(self, hashtag):
        self.curr_hashtag = hashtag
        print('Scraping hashtag: ' + hashtag)
        stime = time.time()
        posts = self.__get_posts(hashtag)
        print('Time taken to get posts: ', time.time() - stime)
        df = self.__convert_to_df(posts)
        df = self.__check_for_duplicates(df, 'posts/'+self.curr_hashtag+'/'+self.last_date+'/posts_data.csv')
        stime = time.time()
        self.__save_data(df)
        print('Time taken to save images: ', time.time() - stime)
    
    def scrape_hashtags(self):
        for hashtag in self.hashtags:
            stime = time.time()
            self.scrape_hashtag(hashtag)
            print('Time taken to scrape hashtag: ', time.time() - stime)
            time.sleep(60)

if __name__ == '__main__':
    # get today's date in the format YYYY-MM-DD
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    scraper = InstaScraper(today)
    scraper.login()
    scraper.set_hashtags(['foodsubstitutes', 'eatthisnotthat', 'foodswaps', 'healthysubstitutes'])
    scraper.scrape_hashtags()
