#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
import time
import re
import os


def hebgb(_name,_password,_course):
    dcap = DesiredCapabilities.PHANTOMJS.copy()
    dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
    dcap["browserName"] = 'Firefox'
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '123.exe')
    driver = webdriver.PhantomJS(executable_path=path, desired_capabilities=dcap)
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

    url_course = url_elective_course if _course == '1' else url_require_course
    
    driver.get(url_course)
    print('\n   =================已登录===============')
    #driver.save_screenshot('a.png')
    classes = driver.find_elements_by_xpath('//a[@class="pbtn04a"]')
    #for c in classes:
    classes[0].click()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    print('\n   =================已选课===============')
    #driver.save_screenshot('b.png')
    current_url = driver.current_url
    course_id = re.search('id=(\d+)', current_url).group(1)
    try:
        class_table = driver.find_element_by_xpath('//table[@class="dataTable"]')
        class_trs = class_table.find_elements_by_xpath('.//tr')
        for tr in class_trs:
            try:
                img = tr.find_element_by_xpath('.//td/img')
                break
            except:
                continue
        img = class_trs[1].find_element_by_xpath('.//td/img')
        click_att = img.get_attribute('onclick')
        item_id = re.search('play\((\d+)\)', click_att).group(1)
        url_video = 'http://www.hebgb.gov.cn/student/course!playScorm.action?userCourse.id={}' \
                '&courseItem.id={}&random=0.011350653832778335'.format(course_id, item_id)
    
    #print(url_video)
        driver.get(url_video)
    except:
        pass
    
    driver.switch_to.window(driver.window_handles[-1])
    #driver.save_screenshot('c.png')
    print('\n   {} 开始学习，每 1 分钟显示一次时间…'.format(time.ctime().split()[3]))

    driver.find_element_by_xpath('//a[@id="sideBarTab"]').click()
    time.sleep(1)
    #driver.save_screenshot('d.png')
    time_text = driver.find_element_by_class_name("jindu").get_attribute('title')
    learn_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(1))
    total_time = int(re.search('(\d+)分钟/(\d+)分钟', time_text).group(2))
    
    print('\n   当前已学习 {}分钟，共需学习 {}分钟'.format(learn_time, total_time))
    ajax_start = 'Ajax.request("/portal/study!start.action?id={}",callback)'.format(course_id)
    ajax_duration = 'Ajax.request("/portal/study!duration.action?id={}",callback)'.format(course_id)
    times = 0 
    while learn_time < total_time and times < 10:
        driver.execute_script(ajax_start)
        time.sleep(60)
        driver.execute_script(ajax_duration)
        learn_time += 1
        times += 1
        print('\n   正在学习中…… 当前已学习 {}分钟'.format(learn_time))
    
    driver.quit()
    print('\n   ======== 别动!!!定时退出,自动续杯 ~_~ ========== \n')

if __name__ == '__main__':
    tips = """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    +                   使用本软件前，请认真阅读以下说明：                 +
    +                  （请擦亮你的双眸，看仔细-_-）                       +
    +    = = =                                                             +
    +    =     =                                                           +
    +    =      =      1、本软件仅作技术交流使用，如作他用，概不负责       +
    +    =      =        （GJ非吾意，凭汝自觉-_-）                         +
    +    =      =                                                          +
    +    =     =       2、本软件不提供技术支持                             +
    +    = = =           （有问题别找coder，自己动手丰衣足食-_-）          + 
    +    =    =                                                            + 
    +    =     =       3、本软件为β版，对有些课程失效，不足之处请多包涵   +
    +    =      =        （绝对有BUG，免费的别要求太多-_-）                +
    +    =       =                                                         +
    +    =        =    4、本软件要先选课，再学习，必修课要先上网自学       +
    +    =        =      （tips：选课时长的、带有目录的课-_-）              +
    +                  5、本软件单次最长运行时间300分钟，重新打开后可继续  +
    +                                                                      +
    +                生命时间有限，少喝酒多吃饭，少打游戏多锻炼            +
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    print(tips)
    input('     按回车继续……')
    temp = input('\n    我已明白以上内容，明白（Y）？不明白（N)? :')
    if temp == 'Y' or temp == 'y':
        name = input('\n    请输入身份证号：')
        password = input('\n    请输入密码(默认密码直接按回车键)：')
        course = input('\n  学选修课输入 1，学必修课输入 2 ：')
        print('\n   别急，正在登录……')
        if password == '':
            password = '888888'
        for i in range(30):
            try:
                hebgb(name, password, course)
            except:
                pass
    else:
        print('\n   =========恭喜你!!!你答对了~~~~~!!!==========')
        input()
