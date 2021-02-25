import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(50)

UA_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
}

base_url = 'https://nexus.gobuildrun.com/service/rest/repository/browse/br_private_npm/'
res = requests.get(base_url, headers=UA_HEADER)

soup = BeautifulSoup(res.text, 'xml')
base_menu_list = soup.find_all(name='a')


def parse_menu(url, menu_lt):
    for menu in menu_lt:
        menu_url = url + menu.attrs.get('href')
        menu_res = requests.get(menu_url)
        menu_soup = BeautifulSoup(menu_res.text, 'xml')
        menu_list = menu_soup.find_all(name='a')[1:]
        if not menu_list[0].attrs.get('href').startswith('https'):
            parse_menu(menu_url, menu_list)
        else:
            pool.submit(download_pkg, menu_list)


def download_pkg(url_list):
    for url in url_list:
        url_path = url.attrs.get('href')
        pkg_path, pkg_name = url_path.split('/br_private_npm/')[-1].split('/-/')
        save_path = os.getcwd() + '/' + pkg_path
        pool.submit(save_pkg, url_path, save_path, pkg_name)


def save_pkg(url_path, save_path, pkg_name):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    pkg = requests.get(url_path, headers=UA_HEADER)
    if os.path.isfile(f'{save_path}/{pkg_name}'):
        return
    with open(f'{save_path}/{pkg_name}', 'wb') as f:
        for i in pkg.iter_content():
            f.write(i)


if __name__ == '__main__':
    pool.submit(parse_menu, base_url, base_menu_list)
    # parse_menu(base_url, base_menu_list)
