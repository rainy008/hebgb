#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
import time
import re


class AutoGB:
    def __init__(self, name, pwd):
        self.name = name
        self.pwd = pwd

        self.dcap = DesiredCapabilities.PHANTOMJS.copy()
        self.dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        self.dcap["browserName"] = 'Firefox'
        self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap)

        self.url_login = 'http://www.hebgb.gov.cn/login.jsp'
        self.url_require_courses = 'http://www.hebgb.gov.cn/student/course!list.action?course.course_type=0&init=yes'
        self.url_elective_courses = 'http://www.hebgb.gov.cn/student/course!list.action?course.course_type=1&init=yes'

    def study(self):
        self.login()
        self.choose(self.url_elective_courses)
        self.learn()


    def login(self):
        try:
            self.driver.get(self.url_login)
            self.driver.find_element_by_id('name').send_keys(self.name)
            self.driver.find_element_by_id('password').send_keys(self.pwd)
            self.driver.find_element_by_xpath('//input[@class="pbtn03"]').click()
            #要识别页面跳转
        except:
            print('账户名或密码不正确，未登录！！！')
        else:
            print('=================已登录===============')
            self.driver.save_screenshot('0 login.png')

    def choose(self, url_courses):
        try:
            self.driver.get(url_courses)
            classes = self.driver.find_elements_by_xpath('//a[@class="pbtn04a"]')
            classes[0].click()
            time.sleep(1)
        except:
            print('请添加要学习的课程！！！')
        else:
            print('=================已选课===============')
            self.driver.save_screenshot('0 choose.png')

    def learn(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            current_url = self.driver.current_url
            course_id = re.search('id=(\d+)', current_url).group(1)
            class_table = self.driver.find_element_by_xpath('//table[@class="dataTable"]')
            class_trs = class_table.find_elements_by_xpath('.//tr')
            for tr in class_trs:
                try:
                    img = tr.find_element_by_xpath('.//td/img')
                    break
                except:
                    continue
            click_att = img.get_attribute('onclick')
            item_id = re.search('play\((\d+)\)', click_att).group(1)
            url_video = 'http://www.hebgb.gov.cn/student/course!playScorm.action?userCourse.id={}' \
                        '&courseItem.id={}&random=0.011350653832778335'.format(course_id, item_id)
            self.driver.get(url_video)
        except:
            pass
        self.driver.switch_to.window(self.driver.window_handles[-1])
        print('{} 开始学习……'.format(time.ctime().split()[3]))
        self.driver.find_element_by_xpath('//a[@id="sideBarTab"]').click()
        time.sleep(1)
        self.driver.save_screenshot('0 study.png')
        time_text = self.driver.find_element_by_class_name("jindu").get_attribute('title')
        learn_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(1))
        total_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(2))

        print('当前已学习 {}分钟，共需学习 {}分钟'.format(learn_time, total_time))
        ajax_start = 'Ajax.request("/portal/study!start.action?id={}",callback)'.format(course_id)
        ajax_duration = 'Ajax.request("/portal/study!duration.action?id={}",callback)'.format(course_id)
        times = 0
        while learn_time < total_time and times < 10:
            self.driver.execute_script(ajax_start)
            time.sleep(60)
            self.driver.execute_script(ajax_duration)
            learn_time += 1
            times += 1
            print('正在学习中…… 当前已学习 {}分钟'.format(learn_time))

        self.driver.quit()
        print('===========================定时退出===================')
        print('\n')

if __name__ == '__main__':
    name = '130302198804130420 '
    password = '888888'
    student = AutoGB(name, password)
    while True:
        try:
            student.study()
        except:
            pass