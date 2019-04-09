# from selenium import webdriver
# def run_scratch_production(productionID, opCode, mess):
#
#     production_url = 'http://127.0.0.1:8000/team_match/production/scratch/build/index.html' \
#           '?id=' + str(productionID) + \
#           '&opCodeAndMess=' + str(opCode) + str(mess)
#     chrome_driver = 'C:\\Users\\413knight\\Desktop\\API\\team_match\\chromedriver.exe'
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)
#     driver.get(production_url)
#     # 指定该opCode对应 notAI 对战
#     driver.add_cookie({'name': opCode, 'value': 'notAI'})
#     driver.add_cookie({'name': 'username', 'value': 'admin'})
#     # driver.close()tion
# run_scratch_production('fdadbad0-36c0-4c22-b9a4-04a3dd58115e', '0123456789123456', '1')
import urllib, urllib.parse
test = "微信公众账号比特量化"
print(test)
new = urllib.parse.quote(test)
print(new)
print(urllib.parse.unquote(new))