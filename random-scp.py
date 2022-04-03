import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import itertools
import pydoc

art_html = None

def main():
    # Get dummy "random" page
    try:
        randhtml = requests.get('https://scp-wiki.wikidot.com/random:random-scp').text
    except:
        print("\nFailed to get webpage. Exiting...")
        exit()
    infoDict = find_link(randhtml)
    url = display_article_info(infoDict['artID'], infoDict['art_title'])
    # Ask to read article
    while True:
        rNow = input('\nRead article now? (y/n): ')
        if rNow.lower() == 'y':
            read_article(url)
            break
        elif rNow.lower() == 'n':
            break
        else:
            print("\nInvalid input.")
    # Ask to save
    while True: 
        d_choice = input('\nWould you like to save this article? (y/n): ')
        if d_choice.lower() == 'y':
            download_article(url, infoDict['art_title'])
            break
        elif d_choice.lower() == 'n':
            # Todo - too verbose, condense using similar code from later
            art_choice = input('\nNot saved. Would you like another SCP? (y/n): ')
            if art_choice == 'y':
                main()
            elif(art_choice == 'n'):
                print('\nQuitting...')
                exit()
            else:
                print('\nInvalid input.')
        else:
            print('\nInvalid input.')

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
    print('\n\n\nRandom Article:', art_title)
    art_url = 'https://scp-wiki.wikidot.com/{}'.format(artID)
    print('URL:', art_url)
    return art_url

# Displays article with pydoc pager
def read_article(url):
    try:
        art_html = requests.get(url).text
        soup = BeautifulSoup(art_html, 'html.parser').get_text('\n')
    except:
        print('An error occurred while fetching the document.')
    art_start = soup.find('rating:')
    # Make temp file for pager
    with open('scp.tmp', 'a+', encoding='UTF-8') as tmp:
        for lines in itertools.islice(soup, art_start, None):
            tmp.write(lines)
        tmp.seek(0)
        pydoc.pager(tmp.read())
    # Could probably just use this as the txt in the download function, then remove it if they say no
    os.remove('scp.tmp')
    return soup

# Downloads article in HTML and plaintext
def download_article(url, art_title):
    # If user didn't read article, fetch it now
    global art_html
    if art_html is None:
        art_html = requests.get(url).text
    # Make scp directory if not present
    if not os.path.isdir('scp'):
        os.makedirs('scp')
    os.chdir('scp')
    # Write files
    with open('{}.html'.format(art_title.lower()), 'w', encoding='UTF-8') as file:
        try:
            file.write(art_html)
            print('Downloaded as scp/{}.html'.format(art_title.lower()))
        except:
            print("HTML download failed.")
    with open('{}.txt'.format(art_title.lower()), 'w', encoding='UTF-8') as file:
        soup = BeautifulSoup(art_html, 'html.parser').get_text('\n')
        art_start = soup.find('rating:')
        try:
            for lines in itertools.islice(soup, art_start, None):
                file.write(lines)
            print('Downloaded as scp/{}.txt'.format(art_title.lower()))
        except:
            print("Plaintext download failed.")
    # Loop if wanted
    repeat = input("Want another article? (y/n): ")
    if repeat.lower() == 'y':
        os.chdir('..')
        main()
    elif repeat.lower() == 'n':
        print("\nDone.")
    else:
        print('\nInvalid input.')

main()
