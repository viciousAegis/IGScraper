import subprocess

if __name__ == '__main__':
    # run the scraper
    subprocess.run(['python', 'scraper.py'])
    
    # run the ocr
    subprocess.run(['python', 'ocr.py'])
    
    # run the stats
    subprocess.run(['python', 'stats.py'])