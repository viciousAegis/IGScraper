from instagrapi import Client

ACCOUNT_USERNAME = "foodenjoyer2"
ACCOUNT_PASSWORD = "jBTYiC9ze7wuVZZ"

print("Starting login")
cl = Client()
cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
print("Login success: %s" % cl.user_id)

HASHTAG = "foodsubstitutes"

hashtag = cl.hashtag_info(HASHTAG)
print("Hashtag: %s" % hashtag)

try:
    print({"Relevant related hashtags": cl.hashtag_related_hashtags(HASHTAG)})
except Exception as e:
    print(e)

top_posts = cl.hashtag_medias_top(HASHTAG)

'''
post structure:
{
    "pk": 1234567890123456789,
    "media_type": 1,
    "comment_count": 0,
    "like_count": 0,
    "thumbnail_url": "https://instagram.fybz2-2.fna.fbcdn.net/v/t51.2885-15/e35/s150x150/123456789_123456789012345_1234567890123456789_n.jpg?_nc_ht=instagram.fybz2-2.fna.fbcdn.net&_nc_cat=1&_nc_ohc=1234567890123456789&tp=1&oh=12345678901234567890123456789012&oe=5FFB1234",
    "caption_text": "This is a caption",
    "resources": [ ... ],
'''

postsToAnalyze = []

for post in top_posts:
    for item in post:
        print(item)
    break
