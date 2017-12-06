#!/usr/bin/python
#coding:utf-8
from selenium import webdriver
import json,re,csv,time
import time
from datetime import datetime
import requests,re
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')



def search_facebook(query,app_id,app_secret):
    url = "https://graph.facebook.com/search?q="+query+"&type=page&access_token="+app_id+"|"+app_secret
    result = json.loads(requests.get(url).content)
    if len(result["data"]) > 0:
        first_id = result["data"][0]["id"]
        first_name = result["data"][0]["name"]

        result_inner= requests.get("https://www.facebook.com/"+first_id)
        soup = BeautifulSoup(result_inner.content,'lxml')
        likes = ''.join(re.findall("[0-9]+",soup.select('._4-u2._3xaf._4-u8 ._4bl9 div')[0].get_text()))
        followers = ''.join(re.findall("[0-9]+",soup.select('._4-u2._3xaf._4-u8 ._4bl9 div')[1].get_text()))
        dic={}
        dic["fb_likes"] = likes
        dic["fb_followers"] = followers
        dic["fb_id"] = first_id
        dic["fb_url"] = result_inner.url
        return dic
    else:
        return {'fb_likes':'','fb_followers':'','fb_id':'','fb_url':''}

def click_script(driver,web_element):
    driver.execute_script("arguments[0].click()",web_element)

def run_script(driver,web_element,value):
    driver.execute_script("arguments[0].setAttribute('value','"+value+"')",web_element)

def instagram_follower(search_keywords,ac,pw):
    driver = webdriver.Chrome()

    driver.get("https://www.instagram.com/")
    k = driver.find_elements_by_xpath('//p[@class="_g9ean"]/a')
    if len(k) > 0:
        click_script(driver,k[0])
    else:
        return {'number_of_posts':'','number_of_followers':'','number_of_followings':'','ref_url':'','search_keywords':'','number_of_hashtag':''}
    time.sleep(3)
    ele = driver.find_elements_by_xpath("//input[@name='username']")
    ele_pw = driver.find_elements_by_xpath("//input[@name='password']")
    if len(ele) > 0 and len(ele_pw) > 0:
        ele[0].send_keys(ac)
        ele_pw[0].send_keys(pw)
        run_script(driver,ele[0],ac)
        run_script(driver,ele_pw[0],pw)
    else:
    	return {'number_of_posts':'','number_of_followers':'','number_of_followings':'','ref_url':'','search_keywords':'','number_of_hashtag':''}

    ele_btn = driver.find_element_by_xpath("//button[@class='_qv64e _gexxb _4tgw8 _njrw0']")

    click_script(driver,ele_btn)

    click_script(driver,ele_btn)

    time.sleep(3)


    print(driver.current_url)
    print("successful login!")

    w = driver.find_elements_by_xpath('//button[@class="_dbnr9"]')
    if len(w) > 0:
        click_script(driver,w[0])

    search_box = driver.find_elements_by_xpath("//input[@type='text']")
    if len(search_box) > 0:
        search_box[0].send_keys(search_keywords)
    else:
        return {'number_of_posts':'','number_of_followers':'','number_of_followings':'','ref_url':'','search_keywords':'','number_of_hashtag':''}
    time.sleep(2)

    if len(driver.find_elements_by_xpath("//span[@class='_sayjy']")) > 0:
        result = driver.find_element_by_xpath("//span[@class='_sayjy']")
        click_script(driver,result)
    else:
        print("not found!")
        return {}
        driver.quit()
    print(driver.current_url)
    driver.get(driver.current_url)
    des = driver.find_elements_by_xpath("//meta[@property='og:description']")
    if len(des) > 0:
    	des = des[0].get_attribute('content')
    else:
    	return {'number_of_posts':'','number_of_followers':'','number_of_followings':'','ref_url':'','search_keywords':'','number_of_hashtag':''}
    data = re.findall(u"([0-9]+) 名粉絲，([0-9]+) 人正在追蹤，([0-9]+) 則貼文 -",des)
    print(data)
    if len(data) == 0:
        dic={}
        dic["number_of_posts"] = ""
        dic["number_of_followers"] = ""
        dic["number_of_followings"] = ""
        dic["ref_url"] = driver.current_url
        dic["search_keywords"] = search_keywords
        dic["number_of_hashtag"] = ""
        return dic
    dic={}
    post_num = int(data[0][0])
    follower = int(data[0][1])
    follow_others =int(data[0][2])
    dic["number_of_posts"] = post_num
    dic["number_of_followers"] = follower
    dic["number_of_followings"] = follow_others
    dic["ref_url"] = driver.current_url
    dic["search_keywords"] = search_keywords

    search_box2 = driver.find_element_by_xpath("//input[@type='text']")
    search_box2.send_keys("#"+search_keywords)
    time.sleep(2)
    if len(driver.find_elements_by_xpath("//div[@class='_sayjy']")) > 0:
        result = driver.find_element_by_xpath("//div[@class='_sayjy']/span/span").text
        dic["number_of_hashtag"] = int(result.replace(',',''))
    else:
        dic["number_of_hashtag"] = ""

    driver.quit()
    return dic

with open("./src/input.list") as f:#read input from list
    items = list(f)

kk=[]
app_id = "facebook_app_id"
app_secret = "facebook_app_secret"
ig_ac = "ig_ac"
ig_pw = "ig_pw"
for item in items:
    dic = instagram_follower(item,ig_ac,ig_pw)
    dic.update(search_facebook(item,app_id,app_secret))
    print(dic)
    with open('search_report_pop.csv', 'a') as f:
        w = csv.DictWriter(f,dic.keys())
        w.writeheader()
        w.writerow(dic)
    time.sleep(30)


