# Lol-PatchNote-Scraper

[![CodeFactor](https://www.codefactor.io/repository/github/oscarvsp/lol-patchnote-scraper/badge)](https://www.codefactor.io/repository/github/oscarvsp/lol-patchnote-scraper)

This is a python scraper to get basic information about League of Legends patchs from the [League of Legends patch notes website](https://www.leagueoflegends.com/en-gb/news/tags/patch-notes/).<br>
The text are transformed into markdown format because it made to be used by my discord bot.<br>
I may add more informations later... or not.<br>
But I'll try to maintain it if it's broken so don't hesitate to open an issue if you find a error !

## Usage

### Creation of the Object
Simply instantiate `PatchNote` with the following optional arguments:
- `previous (int)`: to specifie the patch wanted, from the current one (`0` by default to get the current patch, `1` to get the previous one, etc...)
- `lang (str)`: the location code to specifie the langage (`en-gb` by default)

The list of langage available is the same as the [League of legends website](https://www.leagueoflegends.com/en-gb/):<br>
`en-gb`,
`fr-fr`,
`de-de`,
`es-es`,
`en-us`,
`it-it`,
`en-pl`,
`pl-pl`,
`el-gr`,
`ro-ro`,
`hu-hu`,
`cs-cz`,
`es-mx`,
`pt-br`,
`ja-jp`,
`ru-ru`,
`tr-tr`,
`en-au`,
`ko-kr`

### Patch informations
During initialisation, the `PatchNote` object will create the following attributs that can be used to get patch note informations:
- `title (str)`: the title of the patch article
- `season_number (int)`: the number of the season
- `patch_number (int)`: the number of the patch
- `description (str)`: the first paragraph of the article
- `link (str)`: the url of the article
- `overview_image (str)`: the url overview image of the patch

### Advanced informations
The url used to make de requests are also stored as attributs:
- `menu_request_url (str)`: the url used to get the list of patchs.
- `patch_request_url (str)`: the url used to get the data of the patch

## Requirements
The library used are:
- `requests`
- `bs4`
- `markdownify`

See `requirements.txt` to see the specific version used.
