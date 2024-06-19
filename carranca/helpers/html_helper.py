# Equipe da Canoa -- 2024
#
#
# mgd 2024-04-08

# cSpell:ignore

from bs4 import BeautifulSoup
import re
import os

def file_full_name_parse(file_full_name: str) -> tuple[str, str, str]:
   # split full path into 3 components
   drive, path = os.path.splitdrive(file_full_name)
   _, filename = os.path.split(path)
   return (drive, path, filename)


def img_change_src_path(html_content: str, new_img_path: str) -> str:
    # Change img tag `src` path to a new_img_path & return the modified html
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')

    for img_tag in img_tags:
        src = img_tag.get('src', '')
        if src:
            # Extract the existing path (excluding the image name)
            _, image_name = re.match(r"(.*/)(.*)", src).groups()
            new_src = os.path.join(new_img_path, image_name)
            img_tag['src'] = new_src

    return str(soup)

# Returns a list of all img tag `src` filename
def img_filenames(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    images = []
    for img_tag in img_tags:
        src = img_tag.get('src', '')
        if src:
            (_, _, filename) = file_full_name_parse(src)
            images.append(filename)

    return images

# eof