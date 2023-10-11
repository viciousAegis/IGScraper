# get the stats of all the files in the post directory
# and print them out in a table

import os
import tabulate
import pandas as pd

def get_stats():
    # get all directories in the post directory
    dirs = os.listdir('posts')
    # for each directory, get the stats
    
    stats = []
    
    for dir in dirs:
        post_count = 0
        image_count = 0
        # get the directories in the directory, which are the posts scraped on that day
        inner_dirs = os.listdir('posts/' + dir)
        # there is posts_data.csv in each directory, count the number of posts in that file for each directory
        for inner_dir in inner_dirs:
            # get the number of posts in the file
            with open('posts/' + dir + '/' + inner_dir + '/posts_data.csv', 'r') as f:
                df = pd.read_csv(f)
                num_posts = len(df)
            
            post_count += num_posts
            
            # get the number of files in the images directory under this directory
            num_images = len(os.listdir('posts/' + dir + '/' + inner_dir + '/images'))
            image_count += num_images
        
        stats.append({
            'hashtag': dir,
            'post_count': post_count,
            'image_count': image_count
        })
    
    return stats

def print_stats(stats):
    # print the stats in a table
    table = []
    for stat in stats:
        table.append([stat['hashtag'], stat['post_count'], stat['image_count']])
    table.append(['total', sum([stat['post_count'] for stat in stats]), sum([stat['image_count'] for stat in stats])])
    print(tabulate.tabulate(table, headers=['hashtag', 'post_count', 'image_count']))

if __name__ == '__main__':
    print_stats(get_stats())