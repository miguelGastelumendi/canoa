"""
 The Caatinga Team

 mgd 2024-04-08
"""

from bs4 import BeautifulSoup
import re
import os

"""
Changes the path of the 'src' attribute in all <img> tags in the HTML content.

Args:
   html_content (str): The HTML content as a string.
   new_path (str): The new path to replace the existing paths of the img TAG.

Returns:
   str: The modified HTML content with updated image paths.
"""
def change_img_paths(html_content: str, new_img_path:str) -> str:

    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')

    for img_tag in img_tags:
        src = img_tag.get('src', '')
        if src:
            # Extract the existing path (excluding the image name)
            existing_path, image_name = re.match(r'(.*/)(.*)', src).groups()
            new_src = os.path.join(new_img_path,image_name);
            img_tag['src'] = new_src

    return str(soup)
