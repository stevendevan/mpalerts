import os
import time
import re
from typing import List

import requests
from bs4 import BeautifulSoup

import notification_tools

# constants
FORUM_URL: str = 'https://www.mountainproject.com/forum/103989416/for-sale-for-free-want-to-buy'
EMAIL_ADDR: str = 'stevendevan12@gmail.com'
POST_KEYWORDS: List[str] = ['cam', '45', '45.5', '46', 'offset']
MOST_RECENT_THREAD_ID_FILENAME = 'mpalerts_most_recent_thread_id.txt'

# global vars
most_recent_thread_id = 0
most_recent_thread_id_filepath = ''


def get_forum_html_from_url(url: str):
    return requests.get(url).text


def any_keywords_in_text(keyword_list: List[str], text_to_search: str):
    for keyword in keyword_list:
        # re.search only finds the first occurrence, which is all we need.
        regex_result = re.search(keyword, text_to_search, re.IGNORECASE)
        if (regex_result is not None) and (len(regex_result.regs) > 0):
            return True
    # else
    return False


def find_sale_posts_containing_keywords(thread_links, keywords):
    def thread_title_or_body_contain_keywords(link, keywords):
        thread_html = requests.get(link).text
        thread_soup = BeautifulSoup(thread_html, 'html.parser')
        thread_title = thread_soup.find('h1').text
        original_post_body = thread_soup.find(attrs={'fr-view'})

        # Could be condensed to a list comprehension but this may be easier to read and debug.
        # we cannot simply find all 'p' (paragraph) elements because there are other
        # possible elements like 'li' (list items) and who knows what else.
        # If we loop through all children of the post body and grab everything with
        # a 'text' attribute, I'm hoping that will cover all cases.
        text_to_search = thread_title
        for child_element in original_post_body:
            if hasattr(child_element, 'text'):
                text_to_search = text_to_search + ' ' + child_element.text

        if any_keywords_in_text(keywords, text_to_search):
            return True
        else:
            return False

    valid_links = []
    for thread_link in thread_links:
        time.sleep(1)  # arbitrary value. avoid spamming requests.
        if thread_title_or_body_contain_keywords(thread_link, keywords):
            valid_links.append(thread_link)

    return valid_links


def find_new_sale_post_links_containing_keywords(html: str, keywords: List[str]):
    global most_recent_thread_id

    soup = BeautifulSoup(html, 'html.parser')

    forum_table = soup.find('table')
    table_rows = forum_table.find_all('tr')

    thread_links = []
    for table_row in table_rows:
        thread_link = table_row.find('a')
        if thread_link is not None:
            thread_links.append(thread_link['href'])

    new_thread_links = []
    new_most_recent_thread_id = most_recent_thread_id
    for link in thread_links:
        # get all digits after "topic/" in the thread link
        thread_id = int(re.search(r'(?<=topic/)\d+', link)[0])  # first (and only?) match
        if int(thread_id) > most_recent_thread_id:
            new_most_recent_thread_id = max(int(thread_id), new_most_recent_thread_id)
            new_thread_links.append(link)

    most_recent_thread_id = new_most_recent_thread_id

    valid_thread_links = find_sale_posts_containing_keywords(new_thread_links, keywords)

    return valid_thread_links


def load_last_checked_thread_id():
    global most_recent_thread_id_filepath
    global most_recent_thread_id

    most_recent_thread_id_filepath = os.path.join(os.path.dirname(__file__), MOST_RECENT_THREAD_ID_FILENAME)

    if not os.path.exists(most_recent_thread_id_filepath):
        save_last_checked_thread_id()

    with open(most_recent_thread_id_filepath, 'r') as f:
        most_recent_thread_id = int(f.read())


def save_last_checked_thread_id():
    global most_recent_thread_id_filepath
    global most_recent_thread_id

    with open(most_recent_thread_id_filepath, 'w') as f:
        f.write(str(most_recent_thread_id))


def main():
    load_last_checked_thread_id()
    # We are only getting the first page of for-sale threads. Mountain Project's forum follows
    # the common forum behavior where newly-posted threads and newly replied-to threads are
    # 'bumped' to the top of the first page. It is recommended to run the script every 5-10 minutes
    # because good deals are often gone within 10-20 minutes. It takes much longer (6+ hours) for
    # new/updated posts to overflow to the second page where they would be missed by the script.
    forum_html: str = get_forum_html_from_url(FORUM_URL)
    # check if we even got valid html back
    post_links: List[str] = find_new_sale_post_links_containing_keywords(forum_html, POST_KEYWORDS)

    if len(post_links) > 0:
        notification_tools.email_links_to_address(POST_KEYWORDS, post_links)

    # This comes last because if an exception occurs, the links will not get sent and
    # we don't want to update the last checked thread ID so those threads will get
    # checked next time.
    save_last_checked_thread_id()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
