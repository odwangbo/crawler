import requests
import os

bb = '0' + str(7)
if not os.path.exists('/Users/wangbo/Downloads/rmrb/' + bb):
    os.mkdir('/Users/wangbo/Downloads/rmrb/'+ bb)
for x in range(30):
    if x == 0:
        continue
    elif x < 10:
        aa = '0' + str(x)
    else:
        aa = str(x)
    # 下载1月4日各个分页的新闻报
    url = 'http://paper.people.com.cn/rmrb/page/2020-02/' + bb + '/' + aa + '/rmrb202002' + bb + aa + '.pdf'
    print('要下载的文件是：' + url)
    myfile = requests.get(url)
    if myfile.status_code == 200:
        open('/Users/wangbo/Downloads/rmrb/' + bb + '/rmrb202002' + bb + aa + '.pdf', 'wb').write(myfile.content)
        print('下载完成')
    elif myfile.status_code == 404:
        print('----------------------------到此为止----------------------------')
        break
