#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import re
import random
import sys


class AutoGB:
    def __init__(self, name, pwd, require=False, clazz=False):
        self.name = name
        self.pwd = pwd

        self.dcap = DesiredCapabilities.PHANTOMJS.copy()
        self.dcap[
            "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        self.dcap["browserName"] = 'Firefox'
        self.login(self.name, self.pwd)
        self.study(require, clazz)

    def study(self, study_require, study_clazz):
        all_courses = []     # 所以待学网班、必修、选修课程分类地址
        url_courses = 'http://www.hebgb.gov.cn/student/course!list.action?course.course_type={}&init=yes'
        try:
            if study_clazz:   # 学习网班
                clazzes = self.get_clazzes()
                if not clazzes:
                    print('***** 没有网班可学习，请登录网站检查！！！ *****')
                else:
                    all_courses.extend(clazzes)
            if study_require:  # 学习必修课
                url_require_courses_nostudy = url_courses.format('0&noStudy=1')  # 未学
                url_require_courses = url_courses.format(0)  # 已学
                all_courses.append(('未学的必修课程', url_require_courses_nostudy))
                all_courses.append(('正在学习的必修课程', url_require_courses))

            url_elective_courses = url_courses.format(1)
            all_courses.append(('选修课程', url_elective_courses))

            for c in all_courses:   # 开始学习所有课程
                courses = self.get_course_names_ids(c[1])
                if not courses:
                    print('***** “{}” 课程已全部学完！ *****'.format(c[0]))
                else:
                    print('选择“{}” 学习……'.format(c[0]))
                    for course in courses:
                        #print(course[0], course[1])
                        url_video = self.choose_course(course[1])
                        self.learn(url_video, course)
            else:
                print('====== 恭喜你！所有课程已全部学完！！！======')
                sys.exit()
        except Exception as e:
            print('Study:', e)
            raise
        finally:
            self.driver.quit()

    def login(self, name, pwd):
        self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap)  # 每次学完一课后都要重启driver
        url_login = 'http://www.hebgb.gov.cn/login.jsp'  # 登录页面
        try:
            self.driver.get(url_login)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.find_element_by_id('name').send_keys(name)
            self.driver.find_element_by_id('password').send_keys(pwd)
            self.driver.find_element_by_xpath('//input[@class="pbtn03"]').click()
            # self.driver.save_screenshot('0 login.png')
            if self.driver.current_url == url_login:  # 根据网站页面跳转判断是否登录成功
                print('\n***** 账户名或密码不正确，未登录！！！ *****')
            else:
                print('\n===== 用户 {} 已登录 ====='.format(name))
        except Exception as e:
            print('Login:', e)
            raise

    def get_clazzes(self):
        """返回[(网班名，网班url)]列表"""
        url_clazzes = 'http://www.hebgb.gov.cn/student/clazz!myclazz.action?init'  # 我的网班
        try:
            self.driver.get(url_clazzes)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(1)
            # self.driver.save_screenshot('0 clazzes.png')
            clazz_names_urls = []
            clazzes = self.driver.find_elements_by_css_selector("div.col-sm-6.col-md-3")
            for c in clazzes:
                clazz_name = '网班：' + c.find_element_by_css_selector("p.t2").text
                url_clazz = c.find_element_by_css_selector("a.pbtn04").get_attribute("href")
                # print(url_clazz)
                if url_clazz:  # 跳过已结束网班
                    clazz_names_urls.append((clazz_name, url_clazz))
            return clazz_names_urls
        except Exception as e:
            print('Clazz:', e)
            raise

    def get_course_names_ids(self, url_courses):
        """通过网址，返回未学完的[(课程名，课程ID)]列表"""
        try:
            self.driver.get(url_courses)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(1)
            # self.driver.save_screenshot('0 get_ids.png')
            courses = self.driver.find_elements_by_css_selector("div.col-sm-6.col-md-4")
            courses_names_ids = []
            for c in courses:
                course_name = c.find_element_by_css_selector("p.t2").text
                temp = c.find_element_by_css_selector("span.mprogress span").get_attribute("style")
                course_progress = temp.split(':')[1].strip()
                if course_progress == '100%;':  # 注意有分号
                    continue
                temp = c.find_element_by_css_selector("a.pbtn04a").get_attribute("onclick")
                course_id = re.search('videoList\((\d+)\);', temp).group(1)
                courses_names_ids.append((course_name, course_id))
            return courses_names_ids
        except Exception as e:
            print("Get_ids:", e)
            raise

    def choose_course(self, course_id):
        """通过ID，返回视频播放地址"""
        url_get_list = 'http://www.hebgb.gov.cn/student/course!ajaxVideoList.action?userCourse.id={}'
        try:
            self.driver.get(url_get_list.format(course_id))
            #self.driver.switch_to.window(self.driver.window_handles[-1])
            temp = self.driver.page_source
            #print(temp)
            data = int(re.search('.*>(-?\d+)<.*', temp).group(1))
            if data >= 1:  # data=1 直接播放； data>1 div videoList 选集播放
                url_video = 'http://www.hebgb.gov.cn/student/course!playNew.action?userCourse.id={}&index=0'.format(
                    course_id)
            else:  # date = -1  table 选集播放
                rand = random.random()
                url_table = 'http://www.hebgb.gov.cn/student/course!scormList.action?userCourse.id={}&random={}'
                self.driver.get(url_table.format(course_id, rand))
                self.driver.switch_to.window(self.driver.window_handles[-1])
                temp = self.driver.find_element_by_css_selector('table.dataTable img').get_attribute('onclick')
                item_id = re.search('play\((\d+)\);', temp).group(1)
                url_video = 'http://www.hebgb.gov.cn/student/course!playScorm.action?userCourse.id={}&courseItem.id={}&random={}'.format(
                    course_id, item_id, rand)

            return url_video
        except Exception as e:
            print('Choose :', e)
            raise

    def learn(self, url_video, course):
        """每分钟发起一次登记请求，每10分钟刷新一次界面"""
        try:
            self.driver.get(url_video)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print('{} 开始学习《{}》'.format(time.ctime().split()[3], course[0]))
            self.driver.find_element_by_xpath('//a[@id="sideBarTab"]').click()
            time.sleep(1)
            time_text = self.driver.find_element_by_class_name("jindu").get_attribute('title')
            learn_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(1))
            total_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(2))
            print('每 1 分钟 刷新一次时间，请耐心等待……')
            print('当前已学习 {}分钟，共需学习 {}分钟'.format(learn_time, total_time))

            ajax_start = 'Ajax.request("/portal/study!start.action?id={}",callback)'.format(course[1])
            ajax_duration = 'Ajax.request("/portal/study!duration.action?id={}",callback)'.format(course[1])

            times = 0
            while True:
                if learn_time > total_time:
                    print('***** 《{}》 已学完 ***** '.format(course[0]))
                    #self.driver.save_screenshot('0 close.png')
                    self.driver.quit()   # 网页存在 onbeforeunload 事件，只能退出重新登录
                    self.login(self.name, self.pwd)
                    return
                self.driver.execute_script(ajax_start)
                time.sleep(60)
                self.driver.execute_script(ajax_duration)
                learn_time += 1
                print('正在学习中…… 当前已学习 {}分钟'.format(learn_time))
                times += 1
                if times % 10 == 0:
                    self.driver.refresh()
                    print('============定时刷新============')
                    print('\n===继续学习《{}》==='.format(course[0]))
                    print('共需学习{}分钟'.format(total_time))
        except Exception as e:
            print('Learn:', e)
            raise


if __name__ == '__main__':
    name = '130322198204230052'
    password = '888888'
    AutoGB(name, password)
