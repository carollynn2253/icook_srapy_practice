# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    category_name = scrapy.Field()
    category_link = scrapy.Field()
    sub_categories = scrapy.Field()

class SubCategoryItem(scrapy.Item):
    sub_category_name = scrapy.Field()
    sub_category_link = scrapy.Field()

class ReceiptItem(scrapy.Item):
    category_id = scrapy.Field()
    receipt_title = scrapy.Field()
    receipt_link = scrapy.Field()

class DetailItem(scrapy.Item):
    receipt_id = scrapy.Field()
    title = scrapy.Field()
    image = scrapy.Field()
    introduction = scrapy.Field()
    ingredient = scrapy.Field()
    step = scrapy.Field()
    views_count = scrapy.Field()
    favorite_count = scrapy.Field()

class IngredientItem(scrapy.Item):
    ingredient_name = scrapy.Field()
    ingredient_unit = scrapy.Field()

class StepItem(scrapy.Item):
    step_image = scrapy.Field()
    step_detail = scrapy.Field()
