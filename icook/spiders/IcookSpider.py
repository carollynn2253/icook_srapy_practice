# -*- coding: utf-8 -*-
import scrapy
from icook.items import CategoryItem
from icook.items import SubCategoryItem
from bs4 import BeautifulSoup

#source ~./env/bin/activate


class IcookSpider(scrapy.Spider):
    name = "icook"
    start_urls = ['https://icook.tw/categories?ref=homepage']

    def parse(self, response):
        res = BeautifulSoup(response.body, "lxml")
        main_menu_list = res.select('.main-menu');
        for main_menu in main_menu_list:

            category_list = main_menu.select('.panel-group')
            for category in  category_list:
                # print "[TITLE]:"+category.select('.list-title')[0].text
                # category_item = CategoryItem()
                # category_item['category_name'] = category.select('.list-title')[0].text
                # category_item['category_link'] = 'https://icook.tw' + category.select('.list-title')[0]['href']

                list_items = category.select('.list-group-item')
                list_of_items = []
                for item in list_items:
                    sub_category_item = SubCategoryItem()
                    # print "[ITEM]:"+item.select('a')[0].text
                    sub_category_item['sub_category_name'] = item.select('a')[0].text
                    sub_category_item['sub_category_link'] = 'https://icook.tw' + item.select('a')[0]['href']
                    list_of_items.append(sub_category_item)
                # print list_of_items
                # category_item['sub_categories'] = list_of_items
                yield self.createCategoryItem(category.select('.list-title')[0].text, 'https://icook.tw'+category.select('.list-title')[0]['href'], list_of_items)

                # print '============================='


    def createCategoryItem(self, name, link, sub_categories):
        category_item = CategoryItem()
        category_item['category_name'] = name
        category_item['category_link'] = link
        category_item['sub_categories'] = sub_categories
        # print category_item
        return category_item
