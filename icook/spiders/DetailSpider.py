# -*- coding: utf-8 -*-
import scrapy
from icook.items import DetailItem
from icook.items import IngredientItem
from icook.items import StepItem
from bs4 import BeautifulSoup

import datetime
import time
import re
import json
import mysql.connector
print "2"
from mysql.connector import Error

DELAY_PAGE_TIME = 1
PAT = re.compile('https://icook.tw/recipes/[0-9]+')

# TABLE_RECEIPT = 'test_receipts'
TABLE_RECEIPT = 'receipts'

# source ~/Desktop/scarpy/bin/activate


class DetailSpider(scrapy.Spider):
    name = "detail"

    def query_receipt_links():
        try:
            conn = mysql.connector.connect(host='localhost', database='icook', user='root', password='root', port='8889')
            cursor = conn.cursor()
            query = "SELECT receipt_link FROM " + TABLE_RECEIPT + " WHERE finish = %s"
            cursor.execute(query, (0,))

            rows = cursor.fetchall()
            links = [x[0] for x in rows]

            return links

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def query_receipt_id(self, url):
        url = re.findall(PAT, url)[0]
        # print url

        try:
            conn = mysql.connector.connect(host='localhost', database='icook', user='root', password='root', port='8889')
            cursor = conn.cursor()
            # query = "SELECT id FROM " + TABLE_RECEIPT + " WHERE receipt_link =  %s LIMIT 1"
            query = "SELECT id FROM " + TABLE_RECEIPT + " WHERE receipt_link =  %s"
            cursor.execute(query, (url,))

            # row = cursor.fetchone()
            #
            # if row is not None:
            #     return row[0]
            # else:
            #     return -1

            rows = cursor.fetchall()
            ids = [x[0] for x in rows]

            if ids is not None:
                for receipt_id in ids[1:]:
                    if receipt_id is not None:
                        # print receipt_id
                        self.set_receipt_repeated(receipt_id)
                return ids[0]
            else:
                return -1

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def set_receipt_finish(self, receipt_id):
        # print category_id
        try:
            conn = mysql.connector.connect(host='localhost', database='icook', user='root', password='root', port='8889')
            cursor = conn.cursor()
            query = """UPDATE """ + TABLE_RECEIPT + """ SET finish = %s WHERE id = %s """
            cursor.execute(query, (1, receipt_id))
            conn.commit()

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def set_receipt_repeated(self, receipt_id):
        # print category_id
        try:
            conn = mysql.connector.connect(host='localhost', database='icook', user='root', password='root', port='8889')
            cursor = conn.cursor()
            query = """UPDATE """ + TABLE_RECEIPT + """ SET finish = %s WHERE id = %s """
            cursor.execute(query, (2, receipt_id))
            conn.commit()

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    start_urls = query_receipt_links()

    def parse(self, response):
        time.sleep(DELAY_PAGE_TIME)

        res = BeautifulSoup(response.body, "lxml")
        receipt_id = self.query_receipt_id(response.url)

        receipt_detail = res.select('.recipe-detail')[0]

        title = receipt_detail.select('h1')[0].text
        # print title
        image = receipt_detail.select('.row > .col-md-8 > .picture-frame > .strip > .main-pic')[0]['src']
        # print image
        view_count = receipt_detail.select('.row > .col-md-8 > .func > .meta > .views-count')[0].text.replace(",", "")
        # print view_count
        # favorite_count = receipt_detail.select('.row > .col-md-8 > .func > .meta > .fav-count')[0]['binding-counts']
        favorite_count = receipt_detail.select('.row > .col-md-8 > .func > .meta > .fav-count')[0].text
        # print favorite_count
        introduction = receipt_detail.select('.row > .col-md-8 > .recipe-description > div > p')[0].text
        # print introduction

        ingredients = receipt_detail.select('.row > .col-md-4 > .recipe-ingredients > .ingredients > .group > .ingredient')
        list_of_ingredient_item = []
        for ingredient in ingredients:
            ingredient_item = IngredientItem()
            ingredient_item['ingredient_name'] = ingredient.select('.ingredient-name')[0].text
            ingredient_item['ingredient_unit'] = ingredient.select('.ingredient-unit')[0].text
            list_of_ingredient_item.append(ingredient_item)
        # print list_of_ingredient_item

        receipt_steps = receipt_detail.select('.recipe-steps > .steps > ul > .step')
        list_of_steps_item = []
        for step in receipt_steps:
            step_item = StepItem()
            if not step.select('.media > .step-img'):
                step_item['step_image'] = ""
                if len(step.select('.media > .media-body')[0].text.replace(" ", "").strip().split('\n')) > 1:
                    step_item['step_detail'] = step.select('.media > .media-body')[0].text.replace(" ", "").strip().split('\n')[1]
                else:
                    step_item['step_detail'] = ""
                list_of_steps_item.append(step_item)

            else:
                step_item['step_image'] = step.select('.media > .step-img > .strip')[0]['href']
                if len(step.select('.media > .media-body')[0].text.replace(" ", "").strip().split('\n')) > 1:
                    step_item['step_detail'] = step.select('.media > .media-body')[0].text.replace(" ", "").strip().split('\n')[1]
                else:
                    step_item['step_detail'] = ""
                list_of_steps_item.append(step_item)
        # print list_of_steps_item

        self.set_receipt_finish(receipt_id)
        yield self.createDetailItem(receipt_id, title, image, view_count, favorite_count, introduction, list_of_ingredient_item, list_of_steps_item)
        # print '================================================='

    def createDetailItem(self, receipt_id, title, image, view_count, fav_count, introduction, ingredient, step):
        detail_item = DetailItem()
        detail_item['receipt_id'] = receipt_id
        detail_item['title'] = title
        detail_item['image'] = image
        detail_item['views_count'] = view_count
        detail_item['favorite_count'] = fav_count
        detail_item['introduction'] = introduction
        detail_item['ingredient'] = ingredient
        detail_item['step'] = step
        # print detail_item
        return detail_item
