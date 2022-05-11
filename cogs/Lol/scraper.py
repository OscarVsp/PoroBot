import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


        
headers = {'Accept': 'application/json'}

base_url = "https://www.leagueoflegends.com/page-data/"
patchs_notes_menu_url = '/news/tags/patch-notes/'
end_url = "page-data.json"
view_url = "https://www.leagueoflegends.com/"

        
class PatchNote:
    
    def __init__(self, previous : int = 0, lang : str = 'en-gb'):
   
        
        self.menu_request_url : str = base_url+lang+patchs_notes_menu_url+end_url
        
        try:
            patch_notes_menu_data = requests.get(self.menu_request_url, headers=headers).json()
        except (Exception):
            raise PatchNoteException(f"Patch notes menu data request error for url: {self.menu_request_url}")
        
        try:
            patch_note_url = patch_notes_menu_data['result']['data']['articles']['nodes'][previous]['url']['url']
        except (Exception):
            raise PatchNoteException(f"Patch note url not found in patch notes menu data.")
        
        self.link :str = view_url + lang + patch_note_url 
        self.patch_request_url : str = base_url+lang+patch_note_url+end_url
        
        try:
            patch_note_data = requests.get(self.patch_request_url, headers=headers).json()
        except (Exception):
            raise PatchNoteException(f"Patch note data request error for url: {self.patch_request_urlquest_url}")
        
        try:
            self.title : str = patch_note_data['result']['data']['all']['nodes'][0]['description']
        except (Exception):
            self.title : str = "Title Not Found"
            print(f"[Warning] Unable to found patch note title. Placeholder value used instead.")
    
        
        try:
            [self.season_number, self.patch_number] = patch_note_data['result']['data']['all']['nodes'][0]['url']['url'].split('/')[3].split('-')[1:3]
        except (Exception):
            [self.season_number, self.patch_number] = [0,0]
            print(f"[Warning] Unable to found patch season_number and patch_number. Default values used instead.")
            
      
        soup = BeautifulSoup(patch_note_data['result']['data']['all']['nodes'][0]['patch_notes_body'][0]['patch_notes']['html'], 'html.parser')
        

        try:
            self.description : str = markdownify(str(soup.blockquote),  heading_style="ATX").replace('>','').strip().replace("\n \n", "\n")
        except (Exception):
            self.description : str = "Description not found"
            print(f"[Warning] Unable to found patch description. Placeholder values used instead.")
        
        try:
            self.overview_image : str = soup.find(attrs={"class": "skins cboxElement"}).img.get('src')
        except (Exception):
            self.overview_image : str = "https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blt8536634d0d5ace2a/5e4f14a406f84d0d618d93ea/LOL_PROMOART_12.jpg"
            print(f"[Warning] Unable to found patch overview image. Placeholder values used instead.")

            
        
    def __str__(self):
        return f"{self.season_number}.{self.patch_number}\n{self.title}\n({self.link})\n\n{self.description}\n\n{self.overview_image}\n\n{'-'*10}\n\nMenu url: {self.menu_request_url}\n\nPatch request url: {self.patch_request_url}"
        
        

class PatchNoteException(Exception):
        
    def __init__(self, msg : str = None):
        super().__init__(msg)


        
if __name__ == '__main__':
    patch = PatchNote()
    print(patch)


    