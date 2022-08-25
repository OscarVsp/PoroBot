# -*- coding: utf-8 -*-
import asyncio
import logging
from datetime import date
from datetime import timedelta

import cfscrape
import pickledb
import requests
from bs4 import BeautifulSoup

import modules.FastSnake as FS


class Almanax_scraper:

    scraper = cfscrape.create_scraper(sess=requests.Session())
    base_url = "http://www.krosmoz.com/fr/almanax/"
    database = pickledb.load("cogs/Dofus/almanax.db", False)

    @classmethod
    async def scrape_one_day(cls, date):
        iterate_link = f"{cls.base_url}{date}"

        take_begin = "Récupérer "
        take_end = " et rapporter"
        bonus_take = "Bonus : "

        try:
            html = cls.scraper.get(iterate_link).content

            soup = BeautifulSoup(html, "html.parser")

            dofus_container = soup.find(id="achievement_dofus")
            mid_container = dofus_container.find("div", {"class": "more"})

            bonus_type = str(mid_container.previousSibling).strip()[len(bonus_take) :]

            offering = mid_container.find("p", {"class": "fleft"})
            if offering == None:
                raise Exception
            offering = offering.text
            offering = offering.strip()
            index_start = len(take_begin)

            index_stop = offering.index(take_end)
            offering = offering[index_start:index_stop]

            offering_count = 0

            for s in offering.split():
                if s.isdigit():
                    offering_count = int(s)
                    break
            offering = offering.replace(str(offering_count), "").strip()

            if mid_container.img != None:
                pic = mid_container.img["src"]
            else:
                pic = FS.Images.PLACEHOLDER

            bonus = str(mid_container)
            bonus = bonus[len('<div class="more">') : bonus.index('<div class="more-infos">')].strip()
            bonus = bonus.replace("<b>", "").replace("</b>", "")
            bonus = bonus.replace("<i>", "").replace("</i>", "")
            bonus = bonus.replace("<u>", "").replace("</u>", "")

            data = {
                "date": date.strftime("%d-%m-%y"),
                "item_quantity": offering_count,
                "item": offering,
                "description": bonus.replace("\n", " ").replace("\r\n", " "),
                "bonus": bonus_type.replace("\n", " ").replace("\r\n", " "),
                "item_picture_url": pic,
            }
        except Exception:
            data = {
                "date": date.strftime("%d-%m-%y"),
                "item_quantity": "???",
                "item": "???",
                "description": "???",
                "bonus": "???",
                "item_picture_url": "???",
            }

        cls.database.set(date.strftime("%d-%m-%y"), data)

        logging.info(f"Almanax data of {date.strftime('%d-%m-%y')} has been added to the database.")

        return data

    @classmethod
    async def get_one_day(cls, date):
        """Check if the data is already scraped. If not, scrape it and add it to the database"""
        data = cls.database.get(date.strftime("%d-%m-%y"))
        if data == False:
            return await cls.scrape_one_day(date)
        return data

    @classmethod
    async def get_almanax(cls, advance: int = 0):
        """Scrape the almamanx data.
        if no advance:
            return only the data of today almanax
        else:
            return a list of the data of the advance+1 next day
        """
        if advance == 0:
            data = await cls.get_one_day(date.today())

        else:
            data = []
            for d in range(advance):
                await asyncio.sleep(0.01)
                data.append(await cls.get_one_day((date.today() + timedelta(days=d))))
        cls.database.dump()
        return data
