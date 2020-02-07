import requests                #访问微博网站以及数据获取
import re                      #解析网页数据
import pyquery as pq           #解析html
import json                    #反序列化
import time

#双引号里放刚刚保存的cookie
COOKIE = "SINAGLOBAL=8555001289125.689.1543978786780; UM_distinctid=16e79c38df8552-06b5b9625226e6-1c3b6a5b-1aeaa0-16e79c38df944a; _ga=GA1.2.803648593.1580537784; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhPlVuiio9cpsQuifaLQT7T5JpX5KMhUgL.Fo-f1KMcSon4So.2dJLoIEBLxK-L12eL1KMLxKqLBo-LBoMLxK.L1-BL1--LxKqL1K.L1-2t; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; ALF=1612495606; SSOLoginState=1580959607; SCF=Agdx5UG9bciVcYJ-10uuKiAPMjex2HlIyUPZD5y7W850d23u5MIO_H2OVTUOf9JhPVSP506KmKzw5dHfNcjoDYI.; SUB=_2A25zP_cnDeRhGeNL4lUX9ibFzTWIHXVQTW_vrDV8PUNbmtAKLRCgkW9NSKsHBh0WC01ZtdFIwYFEhIgwX8FfWCWp; SUHB=079jEUmMo49lhr; TC-V5-G0=eb26629f4af10d42f0485dca5a8e5e20; _s_tentry=login.sina.com.cn; UOR=tech.ifeng.com,widget.weibo.com,login.sina.com.cn; Apache=8750386534301.642.1580959610896; ULV=1580959610904:21:2:1:8750386534301.642.1580959610896:1580537806933; TC-Page-G0=1ae767ccb34a580ffdaaa3a58eb208b8|1580990022|1580990009; webim_unReadCount=%7B%22time%22%3A1580990023929%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',\
    'Cookie': COOKIE
}                              #请求头
DECODE_DICT={
    '%2F':'/',
    'mw1024':'large'
}                              #这是用来解码微博图片url的
URLS=[]                        #用来存放图片url



def query_user():
    name=input('>>:').strip()
    text = req.get('https://s.weibo.com/user?q=%s&Refer=weibo_user'%name, headers=HEADERS).text                 #查找目标用户
    time.sleep(1)
    html=pq.PyQuery(text) #将查找后获得的html转成pyquery对象
    for tag in html(".card .info .name"):    #获取所有带有用户名的标签
        tag = pq.PyQuery(tag)
        if tag.text()==name:
            link=tag.attr('href')
            link='https:'+link
            response = req.get(link.format(name), headers=HEADERS)    #找到标签里用户名与目标用户名一致的标签，获取url,访问该用户
            text=response.text
            enter_album(text)#进入用户的相册
            time.sleep(1)
            download_pic()#开始下载图片
            break


def enter_album(html):
    item_dict = {}                                                  #这个字典用来存放下一页的相关信息
#获取相册第一页的相关信息
    data=re.findall('<script>FM.view\((.*?)\)', html, re.S)         #用正则表达式获取数据
    url=None
    for item in data:
        try:
            item=json.loads(item)                                   #反序列化
            item=item.get('html')
            html=pq.PyQuery(item)
            keyword='photos'
            for tag in html('.tab_link'):
                href=tag.get('href')
                if keyword in href:
                    url='https://weibo.com'+href
                    item_dict['page_id']=re.search('p/(.\d+)/',url).group()[2:-1]
                    break
        except Exception as e:
            continue
#获取第一页所有照片的url以及下一页的相关信息
        if url:
            response = req.get(url,headers=HEADERS)
            htmls=response.content
            data = re.findall('<script>FM.view\((.*?)\)</script>', htmls.decode('utf-8'), re.S)
            for html in data:
                try:
                    html = json.loads(html)
                    html = html.get('html')
                    html = pq.PyQuery(html)
                    next_page=html('.WB_cardwrap').attr('action-data')
                    if next_page:
                        html('.ph_ar_box').each(parse_url)         #获得此页所有含有图片url的标签，并将此标签传到parse_url函数
                        next_page = next_page.split('&')
                        for sub in next_page:
                            sub = sub.split('=')
                            item_dict[sub[0]] = sub[1]
                        get_url(item_dict) #获取相册下一页的图片url
                except Exception as e:
                    continue
            break



def parse_url(index,tag):
    tmp_url=tag.get('action-data').strip("curclear_picSrc=")    #获取未解码的图片url
    url=tmp_url[:tmp_url.find('.jpg')+4]
    for key in DECODE_DICT:
        url=url.replace(key,DECODE_DICT[key])                   #用初始化时的解码字典进行替换，得到图片真正的url
    URLS.append("http:"+url)                                    #将图片url存到URLS列表中


def get_url(data_dict):
    q_url = 'https://weibo.com/p/aj/album/loading'
    user_data=data_dict
    for i in range(1,10000):                               #这里是从第一页获取到最后一页
        params= {
                    'ajwvr': 6,
                    'type': 'photo',
                    'owner_uid': int(user_data['owner_uid']),
                    'viewer_uid': int(user_data['viewer_uid']),
                    'since_id': user_data['since_id'],
                    'page_id': int(user_data['page_id']),
                    'page': i,
                    'ajax_call': 1,
                    '__rnd': time.time(),
                }
        try:
            url = requests.get(q_url, headers=HEADERS, params=params) #刷新下一页
            url = url.json().get('data')
            url = pq.PyQuery(url)
            print("page:%d" % i)
            time.sleep(1)
            url('.ph_ar_box').each(parse_url)
            try:
                user_data['since_id'] = url('.WB_cardwrap').attr('action-data')
                user_data['since_id'] = user_data['since_id'][user_data['since_id'].rfind('since_id=') + 9:]
            except Exception as e:                                    #最后一页则退出
                return None
        except Exception as e:
            print(e)
            continue


def download_pic():
    global URLS
    for url in URLS:
        try:
            content = req.get(url, headers=HEADERS).content
        except Exception as e:
            continue
        filename = url[url.rfind("/") + 1:]
        with open('/Users/wangbo/Downloads/beauty/' + filename, 'wb') as file:
            file.write(content)
        time.sleep(1)
    else:
        URLS = []


if __name__=="__main__":
    req=requests.session()        #创建会话
    query_user()                  #调用函数查找用户