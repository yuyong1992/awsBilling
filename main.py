# coding:utf-8
import decimal
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from time import sleep
import datetime
import csv
import os
import re
import sys
import json


class LoginException(Exception):
    pass


def clear_chrome():
    """
    清理chromedriver和chrome

    :return: none
    """
    kill_chromedriver = r'taskkill /F /IM chromedriver.exe'
    kill_chrome_exe = r'taskkill /F /IM chrome.exe'
    # subprocess.run([kill_chromedriver, "-l"])
    print('清理chromedriver')
    os.system(kill_chromedriver)
    sleep(0.5)
    print('清理chrome\n')
    os.system(kill_chrome_exe)


def get_last_day_of_last_month():
    """
    返回当前时间上一个月的最后一天

    :return: last_month_last_day
    """
    today = datetime.date.today()
    # today = datetime.date(2021, 1, 1)
    this_month_first_day = today.replace(day=1)
    last_month_last_day = this_month_first_day - datetime.timedelta(days=1)

    return last_month_last_day


def get_start_and_end_time():
    """
    账单csv中使用的开始时间

    :return: (last_month_first_day_str, last_month_last_day_str)
    """
    last_month_last_day = get_last_day_of_last_month()
    last_month_first_day = last_month_last_day.replace(day=1)
    last_month_first_day_str = last_month_first_day.strftime('%Y/%m/%d %H:%M:%S')
    # print(last_month_first_day_str)
    time = datetime.time(23, 59, 0)
    last_month_last_day = datetime.datetime.combine(last_month_last_day, time)
    last_month_last_day_str = last_month_last_day.strftime('%Y/%m/%d %H:%M:%S')
    # print(last_month_last_day_str)

    return last_month_first_day_str, last_month_last_day_str


def get_year_and_month_of_last_month():
    """
    返回当前时间上一个月的年份和月份

    :return: (year, month)
    """
    last_month_last_day = get_last_day_of_last_month()

    return last_month_last_day.strftime('%Y-%m').split('-')


def ele_scroll_to_view(driver, ele):
    """
    对浏览器中页面的元素进行操作，使其移动到页面的可视区域

    :param driver: 实例化的浏览器驱动
    :param ele: 要移动的元素
    """
    js = "arguments[0].scrollIntoView();"
    driver.execute_script(js, ele)


def read_config(option):
    config_path = f'{current_file_path()}/config.json'
    with open(config_path) as config_file:
        config_json = json.load(config_file)

        return config_json[option]


def open_chrome():
    """
    实例化chrome浏览器，并返回浏览器实例

    :return: driver
    """
    # 浏览器配置，操作当前以debug模式运行的chrome浏览器
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 指定chrome浏览器使用的用户配置文件目录，实现先登录然后再次打开就已经是登录状态
    chrome_user_data_path = read_config('chrome_user_data_path')  # 从配置文件中读取chrome的用户配置文件路径
    chrome_options.add_argument(f'--user-data-dir={chrome_user_data_path}')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument(r'--user-data-dir=C:\Users\YUYONG\AppData\Local\Google\Chrome\User Data')
    # 禁止打印一些无关的日志
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    # 指定自己的chromedriver路径,version=96.0.4664.45
    chromedriver_path = read_config('chromedriver_path')  # 从配置文件中读取chromedriver路径
    chrome_driver = Service(chromedriver_path)
    # chrome_driver = Service(r"D:/Users/yuyong/Desktop/awsBilling/chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_driver, options=chrome_options)

    # 脚本运行后将浏览器调到最前端窗口
    # driver.switch_to.window(driver.current_window_handle)
    driver.implicitly_wait(10)
    driver.maximize_window()

    return driver


def get_page_data(driver):
    """
    :param driver: 实例化的浏览器驱动
    :return:
    """

    # 定位方式
    path_xpath = "xpath"
    # 生成的CSV文件中是否有 Usage Start Date 字段为空的行
    usage_start_date = False

    # 各个账号之下区域费用之和，与 账号明细之和 对比，用来校验明细或者区域是否有缺失
    all_account_total = decimal.Decimal('0')
    # 账号明细费用之和
    all_detail_total = decimal.Decimal('0')

    year, month = get_year_and_month_of_last_month()
    bill_page_url = f'https://console.aws.amazon.com/billing/home?region=ap-northeast-2#/bills?year={year}&month={month}'
    driver.get(bill_page_url)
    print('访问账单页面')
    sleep(3)

    if driver.title == 'Amazon Web Services Sign-In':
        print(f'当前页面title：{driver.title}')
        driver.quit()
        raise LoginException('请先在chrome浏览器中登录aws网站！')
    print(f'当前页面title：{driver.title}')

    # 切换到按账号展示的账单tab页
    path_account_view_tab = '//*[@id="bills-page-antelope"]/div[6]/div/div/div/div[1]/div[2]/awsui-tabs/div/ul/li[2]/a'
    driver.find_element(by=path_xpath, value=path_account_view_tab).click()
    # sleep(0.5)

    # 写入CSV文件的表头
    header_line = ['InvoiceID', 'PayerAccountId', 'LinkedAccountId', 'RecordType', 'RecordID', 'BillingPeriodStartDate',
                   'BillingPeriodEndDate', 'InvoiceDate', 'PayerAccountName', 'LinkedAccountName', 'TaxationAddress',
                   'PayerPONumber', 'ProductCode', 'ProductName', 'SellerOfRecord', 'UsageType', 'Operation', 'RateId',
                   'ItemDescription', 'UsageStartDate', 'UsageEndDate', 'UsageQuantity', 'BlendedRate',
                   'CurrencyCode',
                   'CostBeforeTax', 'Credits', 'TaxAmount', 'TaxType', 'TotalCost'
                   ]
    write_new_csv(header_line)

    # 整个账户模块下的div列表（包含标题和账户列表）
    path_accounts = '//*[@id="bills-page-antelope"]/div[6]/div/div/div/div[1]/div[2]/awsui-tabs/div/div/div/span/div[2]/div/div/div/div'
    # 获取当前账号下子账号元素的列表
    accounts = driver.find_elements(by=path_xpath, value=path_accounts)
    print(f'账号列表模块有 {len(accounts) - 1} 个 账号')
    # 遍历页面上账号的列表，并逐个点击展开，以拉取账号下的账单列表
    # 从第2个 div 开始是账号，第一个是列表的标题
    for i in range(1, len(accounts)):
        sinnet_account = '605989878643'
        record_type_item = 'LinkedLineItem'
        record_type_total = 'AccountTotal'
        # 写入csv的数据
        # csv第一列为空
        data_item = ['']
        data_account_total = ['']
        # 代付账号加入列表
        data_item.append(sinnet_account)
        data_account_total.append(sinnet_account)
        # print(data_item)
        # print(data_account_total)
        print(f'第 {i} 个账户')
        account = accounts[i]
        # 元素移动到页面可视区域，否则不能操作
        ele_scroll_to_view(driver, account)
        # sleep(0.5)
        # try:
        account.click()
        sleep(0.5)
        path_account_number = f'{path_accounts}[{i + 1}]/awsui-expandable-section/h3'
        account_number = driver.find_element(by=path_xpath, value=path_account_number).text[-13:-1]
        # 用户账号加入列表
        data_item.append(account_number)
        data_account_total.append(account_number)
        # 明细类型加入列表
        data_item.append(record_type_item)
        data_account_total.append(record_type_total)
        # 加入空值
        data_item.append('')
        data_account_total.append('')
        # 开始时间结束时间加入列表
        start_time, end_time = get_start_and_end_time()
        data_item.extend([start_time, end_time])
        data_account_total.extend([start_time, end_time])
        # 用量明细加入5个空值，账号总计加入11个空值
        data_item.extend(['', '', '', '', ''])
        data_account_total.extend(['', '', '', '', '', '', '', '', '', '', ''])
        # 账号合计的描述信息 加入列表
        data_account_total.append(f'关联账号 {account_number} 的总额')
        # 账号合计 加入9个空格
        data_account_total.extend(['', '', '', '', '', '', '', '', ''])

        start_text = f'{account_number} start'
        print(f'{start_text:*^50}')

        # 当前账号合计的费用
        account_fee_total = decimal.Decimal(0)

        # 遍历账号下产品列表
        # 从第二个div开始，第一个div是标题
        path_products = f'//*[@id="bills-page-antelope"]/div[6]/div/div/div/div[1]/div[2]/awsui-tabs/div/div/div/span/div[2]/div/div/div/div[{i + 1}]/awsui-expandable-section/div/span/div/div/div/div'
        products = driver.find_elements(by=path_xpath, value=path_products)
        print(f'账号下下有 {len(products) - 1} 个 产品元素')
        for j in range(1, len(products)):
            print(f'第{j}个产品')
            data_item_product = []
            data_item_product.extend(data_item)
            product = products[j]
            ele_scroll_to_view(driver, product)
            # sleep(0.5)
            # 展开产品详情
            product.click()
            # sleep(0.5)
            # 获取产品名称
            path_product_name = f'{path_products}[{j + 1}]/awsui-expandable-section/h3'
            product_name = driver.find_element(by=path_xpath, value=path_product_name).text
            print(product_name)
            # 产品简称和产品名称加入列表
            data_item_product.extend([product_name, product_name])
            # 销售公司名称加入明细的列表
            data_item_product.append('Amazon Web Services, Inc.')
            # 加入3个空格到明细的列表
            data_item_product.extend(['', '', ''])

            # 当前产品下区域的列表
            path_regions = f'{path_products}[{j + 1}]/awsui-expandable-section/div/span/div[@ng-if="vm.shouldShowProducts(product)"]'
            regions = driver.find_elements(by=path_xpath, value=path_regions)
            print(f'第 {j} 个产品下有 {len(regions)} 个 region元素')
            for m in range(1, len(regions) + 1):
                region = regions[m - 1]
                ele_scroll_to_view(driver, region)
                # sleep(0.5)
                ele_scroll_to_view(driver, region)
                # sleep(0.5)
                # 获取region的名称
                path_region_name = f'{path_regions}[{m}]/awsui-expandable-section/h3'
                region_name = driver.find_element(by=path_xpath, value=path_region_name).text
                print(f'第 {m} 个 region name is {region_name}')
                # 获取regin的费用
                path_region_fee = f'{path_regions}[{m}]/span'
                # region_fee = driver.find_element(by=path_xpath, value=path_region_fee).text.replace('$', '')
                region_fee = re.sub(r'[$,]*', '', driver.find_element(by=path_xpath, value=path_region_fee).text)
                # 账号合计费用
                account_fee_total = account_fee_total + decimal.Decimal(region_fee)
                print(f'第 {m} 个 region fee is {region_fee}')
                # 展开区域下明细类型
                region.click()
                # sleep(0.5)
                path_detail_types = f'{path_region_name}/../div/span/div/div'
                detail_types = driver.find_elements(by=path_xpath, value=path_detail_types)
                # print(f'{len(detail_types)} types of details')
                for n in range(1, len(detail_types) + 1):
                    detail_type = detail_types[n - 1]
                    ele_scroll_to_view(driver, detail_type)
                    # sleep(0.5)
                    # 用量详情的路径
                    path_details = f'{path_detail_types}[{n}]/div'
                    details = driver.find_elements(by=path_xpath, value=path_details)
                    # print(f'第 {n} 个类型下有{len(details) - 1}条明细')
                    for r in range(1, len(details)):
                        data_item_final = []
                        data_item_final.extend(data_item_product)
                        path_detail_item = f'{path_details}[{r + 1}]/div[1]'
                        path_detail_fee = f'{path_details}[{r + 1}]/div[3]'
                        detail_item = driver.find_element(by=path_xpath, value=path_detail_item)
                        # 元素移动到可视区域
                        ele_scroll_to_view(driver, detail_item)
                        detail_item_text = detail_item.text
                        # print(f'detail is: {detail_item_text}')
                        # 明细的描述加入列表
                        data_item_final.append(detail_item_text)
                        # 明细金额的文本
                        detail_fee = re.sub(r'[$,]*', '',
                                            driver.find_element(by=path_xpath, value=path_detail_fee).text)
                        # 明细金额的数字
                        # detail_fee_num = float(detail_fee)
                        all_detail_total = all_detail_total + decimal.Decimal(detail_fee)

                        # 扣税之前的金额，税额，明细最终金额 加入列表
                        # 海外账号 税额都是0，所以扣税之前金额和明细最终金额相同
                        data_item_final.extend(['', '', '', '', '', str(detail_fee), '', '0', '', str(detail_fee)])
                        # 从aws原始的csv文件中匹配account 和 item description，取 Usage Start Date的值，页面上没有
                        rows = read_aws_csv()
                        # print(f'aws 原始的csv文件中数据行数（不算表头）：{len(rows)}')
                        for row in rows:
                            # print('匹配aws的csv文件中的item description，获取Usage Start Date的值')
                            # aws的csv中item description文本内容中间可能会多空格，连续两个空格，正则将多个空格替换为一个
                            # 如果aws中有重复的项，那么取第一匹配到的值
                            # 目前还存在匹配不上的值，由姜玲手动处理
                            item_description_aws = re.sub(' +', '', row[18])
                            item_description_page = re.sub(' +', '', data_item_final[18])
                            if row[2] == data_item_final[2] and item_description_aws == item_description_page:
                                data_item_final[19] = row[19]
                        if data_item_final[19] == '':
                            usage_start_date = True
                        # 明细内容写入csv
                        write_csv(data_item_final)
                        # print(data_item_final)
        # 账号合计的费用加入列表
        data_account_total.append(str(account_fee_total))
        all_account_total = all_account_total + account_fee_total
        # print(f'all_account_total: {all_account_total}')
        write_csv(data_account_total)
        end_text = f'{account_number} end'
        print(f'{end_text:*^50}\n')
        # break
        # sleep(1)
    if all_account_total == all_detail_total:
        if usage_start_date:
            print('Warning：存在Usage Start Date 字段为空的行，请手动检查，并对比aws原始的csv进行补充！！！\n')
        else:
            print('INFO：所有明细的 Usage Start Date 字段已经补充完毕！\n')
    else:
        # remove_csv()
        # print('ERR: 金额校验不通过，获取到的明细可能有缺失，已删除生成的csv，请重新运行脚本。')
        print(f'all_account_total: {all_account_total} -> all_detail_total:{all_detail_total}')
        raise Exception('金额校验不通过，获取到的明细可能有缺失，请检查csv结果后重新运行脚本。')
    driver.quit()


def write_csv(data):
    year, month = get_year_and_month_of_last_month()
    dir_path = current_file_path()
    path = f'{dir_path}/aws_bill_{year}_{month}.csv'
    with open(path, 'a+', newline='') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL, dialect='excel')
        writer.writerow(data)


def write_new_csv(data):
    year, month = get_year_and_month_of_last_month()
    dir_path = current_file_path()
    path = f'{dir_path}/aws_bill_{year}_{month}.csv'
    with open(path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL, dialect='excel')
        writer.writerow(data)


def read_aws_csv():
    year, month = get_year_and_month_of_last_month()
    dir_path = current_file_path()
    path = f'{dir_path}/ecsv_{month}_{year}.csv'
    try:
        with open(path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            csv_data = []
            for row in reader:
                csv_data.append(row)
        return csv_data
    except FileNotFoundError as e:
        print(f'ERR: csv文件未找到{path}')
        raise FileNotFoundError(e)


def current_file_path():
    # return os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(sys.argv[0])


def remove_csv():
    year, month = get_year_and_month_of_last_month()
    dir_path = current_file_path()
    path = f'{dir_path}/aws_bill_{year}_{month}.csv'
    if os.path.exists(path):
        os.remove(path)


if __name__ == '__main__':
    # TODO：添加对页面主要结构的校验，不符合给出提示
    # start = time.time()
    try:
        clear_chrome()
        browser_driver = open_chrome()
        get_page_data(browser_driver)
    except LoginException as e:
        print(f'ERR: {e}\n')
    except Exception as e:
        if 'Message: chrome not reachable' in str(e) or 'Message: no such window' in str(e):
            print('ERR: 脚本运行中 chrome 浏览器被人为关闭!!! 脚本找不到chrome浏览器！！！\n')
        else:
            print(f'ERR: {e}\n')
        # # 脚本运行失败，删除生成的csv
        # remove_csv()
        print(f'ERR: 运行失败，请重新运行脚本！\n')
    else:
        print('脚本执行成功！\n')
    finally:
        # end = time.time()
        # print(f'脚本用时：{end - start}')
        input('按Enter键退出窗口...\n')

