"""
A simple python scraper to get League of Legends patchnote informations.
Copyright (C) 2022 - Oscar Van Slijpe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
import logging


        
headers = {'Accept': 'application/json'}

base_url = "https://www.leagueoflegends.com/page-data/"
patchs_notes_menu_url = '/news/tags/patch-notes/'
end_url = "page-data.json"
view_url = "https://www.leagueoflegends.com/"

langs = [
    'en-gb',
    'fr-fr',
    'de-de',
    'es-es',
    'en-us',
    'it-it',
    'en-pl',
    'pl-pl',
    'el-gr',
    'ro-ro',
    'hu-hu',
    'cs-cz',
    'es-mx',
    'pt-br',
    'ja-jp',
    'ru-ru',
    'tr-tr',
    'en-au',
    'ko-kr'
    ]

        
class PatchNote:
    
    def __init__(self, previous : int = 0, lang : str = 'en-gb'):
        
        if lang not in langs:
            logging.error(f"Specified langage is not available. The list of available lang is:\n{langs}")
            raise ValueError
   
        
        self.menu_request_url : str = base_url+lang+patchs_notes_menu_url+end_url
        
        try:
            patch_notes_menu_data = requests.get(self.menu_request_url, headers=headers).json()
        except Exception:
            logging.error(f"An error occured during the requests of the patchnotes menu data at url '{self.menu_request_url}'. Maybe 'lang' is not correct.")
            raise
        
        try:
            patch_note_url = patch_notes_menu_data['result']['data']['articles']['nodes'][previous]['url']['url']
        except Exception:
            logging.error(f"An error occured while extracting the patch note url from the patchnotes menu.")
            raise
        
        self.link :str = view_url + lang + patch_note_url 
        self.patch_request_url : str = base_url+lang+patch_note_url+end_url
        
        try:
            patch_note_data = requests.get(self.patch_request_url, headers=headers).json()
        except Exception:
            logging.error(f"An error occured during the request of the patchnote data at url '{self.patch_request_urlquest_url}'")
            raise
        
        try:
            self.title : str = patch_note_data['result']['data']['all']['nodes'][0]['description']
        except Exception:
            self.title : str = "Patch title"
            logging.warn(f"Unable to found patch note title from the patchnote data. Placeholder text used instead.")
    
        
        try:
            [self.season_number, self.patch_number] = patch_note_data['result']['data']['all']['nodes'][0]['url']['url'].split('/')[3].split('-')[1:3]
        except Exception:
            [self.season_number, self.patch_number] = [0,0]
            logging.warn(f"Unable to found season_number and patch_number from the patchnote data. Placeholder values used instead.")
            
      
        soup = BeautifulSoup(patch_note_data['result']['data']['all']['nodes'][0]['patch_notes_body'][0]['patch_notes']['html'], 'html.parser')
        

        try:
            self.description : str = markdownify(str(soup.blockquote),  heading_style="ATX").replace('>','').strip().replace("\n \n", "\n")
        except Exception:
            self.description : str = "Description of the patch note."
            logging.warn(f"Unable to found patch description from patchnote data. Placeholder text used instead.")
        
        try:
            self.overview_image : str = soup.find(attrs={"class": "skins cboxElement"}).img.get('src')
        except Exception:
            self.overview_image : str = "https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blt8536634d0d5ace2a/5e4f14a406f84d0d618d93ea/LOL_PROMOART_12.jpg"
            logging.warn(f"Unable to found patch overview image from patchnote data. Placeholder image used instead.")

            
        
    def __str__(self):
        return f"{self.season_number}.{self.patch_number}\n{self.title}\n({self.link})\n\n{self.description}\n\n{self.overview_image}\n\n{'-'*10}\n\nMenu url: {self.menu_request_url}\n\nPatch request url: {self.patch_request_url}"
        


        
if __name__ == '__main__':
    patch = PatchNote()
    print(patch)


    