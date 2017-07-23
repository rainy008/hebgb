#!/usr/bin/env python3
"""
适合于分集选课时第一行为标题的课程
"""

from selenium import webdriver
import time
import re


def hebgb(_name,_password):
    driver = webdriver.PhantomJS()
    url_login = 'http://www.hebgb.gov.cn/login.jsp'
    driver.get(url_login)
    name = driver.find_element_by_id('name')
    password = driver.find_element_by_id('password')
    name.send_keys(_name)
    password.send_keys(_password)
    btn_login = driver.find_element_by_xpath('//input[@class="pbtn03"]')
    btn_login.click()

    url_require_course = 'http://www.hebgb.gov.cn/student/course!list.action?course.course_type=0&init=yes'
    url_elective_course = 'http://www.hebgb.gov.cn/student/course!list.action?course.course_type=1&init=yes'

    driver.get(url_elective_course) #选择选修课
    print(u'=================已登录===============')
    driver.save_screenshot('a.png')
    classes = driver.find_elements_by_xpath('//a[@class="pbtn04a"]')
    #for c in classes:
    classes[0].click()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    print(u'=================已选课===============')
    driver.save_screenshot('b.png')
    current_url = driver.current_url
    course_id = re.search('id=(\d+)', current_url).group(1)

    class_table = driver.find_element_by_xpath('//table[@class="dataTable"]')
    class_trs = class_table.find_elements_by_xpath('.//tr')
    '''
    for tr in class_trs:
        try:
            img = tr.find_element_by_xpath('.//td/img')
        except :
            continue
    '''
    img = class_trs[1].find_element_by_xpath('.//td/img')
    #img = class_trs[2].find_element_by_xpath('.//td/img') #通过图片观察课程目录结构
    click_att = img.get_attribute('onclick')
    

    item_id = re.search('play\((\d+)\)', click_att).group(1)
    url_video = 'http://www.hebgb.gov.cn/student/course!playScorm.action?userCourse.id={}' \
                '&courseItem.id={}&random=0.011350653832778335'.format(course_id, item_id)
    
    #print(url_video)
    driver.get(url_video)
    driver.switch_to.window(driver.window_handles[-1])
    driver.save_screenshot('c.png')
    print('{} 开始学习……'.format(time.ctime().split()[3]))

    driver.find_element_by_xpath('//a[@id="sideBarTab"]').click()
    time.sleep(1)
    driver.save_screenshot('d.png')
    time_text = driver.find_element_by_class_name("jindu").get_attribute('title')
    learn_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(1))
    total_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(2))
    
    print('当前已学习 {}分钟，共需学习 {}分钟'.format(learn_time, total_time))
    ajax_start = 'Ajax.request("/portal/study!start.action?id={}",callback)'.format(course_id)
    ajax_duration = 'Ajax.request("/portal/study!duration.action?id={}",callback)'.format(course_id)
    times = 0 
    while learn_time < total_time and times < 10:
        driver.execute_script(ajax_start)
        time.sleep(60)
        driver.execute_script(ajax_duration)
        learn_time += 1
        times += 1
        print('正在学习中…… 当前已学习 {}分钟'.format(learn_time))
    
    driver.quit()
    print('===========================定时退出===================')
    print('\n')

if __name__ == '__main__':
    name = ' '
    password = '888888'
    while True:
        try:
            hebgb(name, password)
        except:
            pass
