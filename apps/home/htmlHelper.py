"""
 The Caatinga Team

 mgd 2024-04-08
"""

from bs4 import BeautifulSoup
import re
import os

# split fil path into 3 components
def file_fullname_parse(filepath: str) -> tuple[str, str, str]:
   drive, path = os.path.splitdrive(filepath)
   _, filename = os.path.split(path)
   return (drive, path, filename)


# Change img tag `src` path to a new_img_path & return the modified html
def img_change_path(html_content: str, new_img_path: str) -> str:

    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")

    for img_tag in img_tags:
        src = img_tag.get("src", "")
        if src:
            # Extract the existing path (excluding the image name)
            _, image_name = re.match(r"(.*/)(.*)", src).groups()
            new_src = os.path.join(new_img_path, image_name)
            img_tag["src"] = new_src

    return str(soup)

# Returns a list of all img tag `src` filename
def img_filenames(html_content: str) -> str:

    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")
    images = []
    for img_tag in img_tags:
        src = img_tag.get("src", "")
        if src:
            (_, _, filename) = file_fullname_parse(src)
            images.append(filename)

    return images

# eof