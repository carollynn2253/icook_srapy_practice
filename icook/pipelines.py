# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
from mysql.connector import Error

import json

# TABLE_CATEGORY = 'test_categories'
TABLE_CATEGORY = 'categories'
# TABLE_RECEIPT = 'test_receipts'
TABLE_RECEIPT = 'receipts'

class IcookPipeline(object):
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
        self.cursor = self.conn.cursor()
        # self.cursor.execute("SELECT * FROM categories")
        # row = self.cursor.fetchone()
        #
        # while row is not None:
        #     print(row)
        #     row = self.cursor.fetchone()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if spider.name not in ['icook']:
            # print 'not icook'
            return item

        parent_id = self.insert_category(item['category_name'], item['category_link'], False)
        if parent_id:
            for sub_category in item['sub_categories']:
                self.insert_category(sub_category['sub_category_name'], sub_category['sub_category_link'], parent_id)
        return item

    def insert_category(self, category_name, category_link, parent_id):
        if parent_id:
            query = "INSERT INTO " + TABLE_CATEGORY + " (category_name, category_link, parent_id) " \
                    "VALUES(%s,%s,%s)"
            args = (category_name, category_link, parent_id)
        else:
            query = "INSERT INTO  " + TABLE_CATEGORY + " (category_name, category_link) " \
                    "VALUES(%s,%s)"
            args = (category_name, category_link)

        try:
            # print query
            self.cursor.execute(query, args)

            if self.cursor.lastrowid:
                # print('last insert id', self.cursor.lastrowid)
                self.conn.commit()
                return self.cursor.lastrowid
            else:
                # print('last insert id not found')
                self.conn.commit()
                return False


        except Error as error:
            print(error)


class ReceiptPipline(object):
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(host='localhost',database='icook',user='root',password='root', port='8889')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SET NAMES utf8mb4")


    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if spider.name not in ['receipt']:
            # print 'not receipt'
            return item

        self.insert_receipt(item['category_id'], item['receipt_title'], item['receipt_link'])
        return item

    def insert_receipt(self, category_id, receipt_title, receipt_link):
        query = "INSERT INTO  " + TABLE_RECEIPT + " (category_id, receipt_title, receipt_link) " \
                "VALUES(%s,%s,%s)"
        args = (category_id, receipt_title, receipt_link)

        try:
            # print query
            self.cursor.execute(query, args)

            if self.cursor.lastrowid:
                # print('last insert id', self.cursor.lastrowid)
                self.conn.commit()
            else:
                print('last insert id not found')
                self.conn.commit()


        except Error as error:
            print(error)

class DetailPipline(object):
    def process_item(self, item, spider):
        if spider.name not in ['detail']:
            # print 'not detail'
            return item

        file_name = 'icook_json/' + str(item['receipt_id']) + '.json'
        self.file = open(file_name, 'wb')
        json_string = json.dumps(item, default=lambda o: o.__dict__, sort_keys=False, indent=4)
        self.file.write(json_string)
        return item
