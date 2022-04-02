import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import itertools

def main():
    # Get dummy "random" page
    try:
        randhtml = requests.get('https://scp-wiki.wikidot.com/random:random-scp').text
    except:
        print("Failed to get article. Exiting...")
        exit()
    infoDict = find_link(randhtml)
    url = display_article_info(infoDict['artID'], infoDict['art_title'])
    download_article(url, infoDict['art_title'])

# Find line with randomly-generated article
def find_link(randhtml):
    for line in randhtml.split("\n"):
        if '<p>Random SCP: <a href="/' in line:
            scp_str = line
            break
    #Find href'd url
    id_fpos = scp_str.index('/')
    id_lpos = scp_str.index('"', id_fpos)
    artID = scp_str[id_fpos+1:id_lpos]

    # Article title to be returned to info function

    title_fpos = scp_str.index('>',id_lpos)
    title_lpos = scp_str.index('<', title_fpos)
    art_title = scp_str[title_fpos+1: title_lpos]
    # So main function can process both variables
    info_dict = dict();
    info_dict['artID'] = artID
    info_dict['art_title'] = art_title
    return info_dict

# Uses previous artID to fill in URL
def display_article_info(artID, art_title):
    print('Random Article:', art_title)
    art_url = 'https://scp-wiki.wikidot.com/{}'.format(artID)
    print('URL:', art_url)
    return art_url

# Downloads article in HTML and plaintext
def download_article(art_url, art_title):
    # Make scp directory if not present
    art_content = requests.get(art_url).text
    if not os.path.isdir('scp'):
        os.makedirs('scp')
    os.chdir('scp')
    # Write files
    with open('{}.html'.format(art_title.lower()), 'w', encoding='UTF-8') as file:
        try:
            file.write(art_content)
        except:
            print("HTML download failed.")
    with open('{}.txt'.format(art_title.lower()), 'w', encoding='UTF-8') as file:
        soup = BeautifulSoup(art_content, 'html.parser').get_text('\n')
        art_start = soup.find('rating:')
        try:
            for lines in itertools.islice(soup, art_start, None):
                file.write(lines)
        except:
            print("Plaintext download failed.")
    try:
        repeat = input("Want another article? (y/n): ")
        if repeat.lower() == 'y':
            main()
        elif repeat.lower() == 'n':
            print("Done.")
            return 0
        else:
            print('Invalid input.')
    except:
        print("Invalid input.")





main()
