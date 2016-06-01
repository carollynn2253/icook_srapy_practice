# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from icook.items import ReceiptItem
import datetime
import time
import re
import mysql.connector
from mysql.connector import Error

DELAY_PAGE_TIME = 1
PAT = re.compile('https://icook.tw/categories/[0-9]+')

# TABLE_CATEGORY = 'test_categories'
TABLE_CATEGORY = 'categories'
# TABLE_RECEIPT = 'test_receipts'
TABLE_RECEIPT = 'receipts'

#source ~/Desktop/scarpy/bin/activate


class ReceiptSpider(scrapy.Spider):
    name = "receipt"

    def clear_unfinish_category_receipt():
        try:
            conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
            cursor = conn.cursor()
            query = "SELECT id FROM " + TABLE_CATEGORY + " WHERE finish = %s"
            cursor.execute(query, (0,))

            rows = cursor.fetchall()
            ids = [x[0] for x in rows]

            for category_id in ids:
                query = "DELETE FROM " + TABLE_RECEIPT + " WHERE category_id = %s"
                cursor.execute(query, (category_id,))
                conn.commit()

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def query_category_links():
        try:
            conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
            cursor = conn.cursor()
            query = "SELECT category_link FROM " + TABLE_CATEGORY + " WHERE finish = %s"
            cursor.execute(query, (0,))

            rows = cursor.fetchall()
            links = [x[0] for x in rows]

            return links

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def query_category_id(self, url):
        url = re.findall(PAT, url)[0]
        # print url

        try:
            conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
            cursor = conn.cursor()
            query = "SELECT id FROM " + TABLE_CATEGORY + " WHERE category_link =  %s"
            cursor.execute(query, (url,))

            row = cursor.fetchone()

            if row is not None:
                return row[0]
            else:
                return -1

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def set_category_finish(self, category_id):
        # print category_id
        try:
            conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
            cursor = conn.cursor()
            query = """UPDATE """ + TABLE_CATEGORY + """ SET finish = %s WHERE id = %s """
            cursor.execute(query, (1,category_id))
            conn.commit()

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    clear_unfinish_category_receipt()
    start_urls = query_category_links()

    def parse(self, response):
        res = BeautifulSoup(response.body, "lxml")
        receipt_list = res.select('.media')

        next_page = res.select('.next_page > a')
        if not next_page:
            self.set_category_finish(self.query_category_id(response.url))
            print '=====last page.====='
        else:
            next_page_url = 'https://icook.tw' + res.select('.next_page > a')[0]['href']
            time.sleep(DELAY_PAGE_TIME)
            print '[START A PAGE]'+ str(datetime.datetime.now())
            yield scrapy.Request(next_page_url, self.parse)

        for receipt in receipt_list:
            title = receipt.select('.pull-left')[0]['title']
            link =  'https://icook.tw' + receipt.select('.pull-left')[0]['href']
            # print 'title: ' + title + ', link: ' + link
            yield self.createReceiptItem(self.query_category_id(response.url), title, link)


    def createReceiptItem(self, category_id, title, link):
        receipt_item = ReceiptItem()
        receipt_item['category_id'] = category_id
        receipt_item['receipt_title'] = title
        receipt_item['receipt_link'] = link
        # print receipt_item
        return receipt_item
