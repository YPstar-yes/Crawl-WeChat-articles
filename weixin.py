import re
import time

import requests

cookies = {'cookie': 'RK=rQa1+Lg2Sp; ptcz=48b9a8b62d972b65fb135c61f9974cc936bd1c3ab1b31d4bd58a5917f05beb55; pgv_pvid=6278140446; pgv_pvi=4091260928; tvfe_boss_uuid=5a1d1ba8a4ae63c5; ua_id=JR1Tx5W9COSNUQuVAAAAAAODb8VamBBophbfpTWEA4U=; pgv_si=s7647235072; rewardsn=; cert=MlyunehiveyT3XbGs1fErhSheJKqqc47; sig=h015223518f766ecc3935782e71a6263fab919dc63f81cb5a8c54679252079c3d6a960b54ec487785ba; uuid=b75d1676ed02b2debb7464220e0931d4; rand_info=CAESIKkDzo0r+T1lwT1rF2qDxCrRiAa8VCARhmPslA94TNTv; slave_bizuin=2390701948; data_bizuin=2390701948; bizuin=2390701948; data_ticket=FpnsP5mkAH62YCyRtaTLjgGQTpkdxQzSpopYPfQFT4kAlKEhGDB54UI0nyYGO+88; slave_sid=bHlMeE4zeVBQWUttdktVYmZQM245TEFhVzFCWktPUFJHNU5JU2lKX0cwTkZ6VTIzaFJtajNFRXNiRkNTTlRHbWx5Vm5MOEpFYmdUb2o5SldXTnBLNEx1ZDU4SlVqT3JaTF81M3o5X1g4anM1WmJWUG5mODQxQzR4OHdWYkYxckN5MDlUY0hjZFRCQVRyUkVH; slave_user=gh_057c792c7f1e; xid=0aca306d9fe2b7dc3e03a3a2dd6c2846; openid2ticket_ofDd_jkKG6_4fNy7RcF7aIovoxlg=weiREBOwWgSeCDfIIVppYRBLy49K8J916Qv/3hgUNfA=; mm_lang=zh_CN'}
#爬取微信公众号文章，并存在本地文本中
def get_content(query):
    #query为要爬取的公众号名称
    #公众号主页
    url = 'https://mp.weixin.qq.com'
    #设置headers
    header = {
        "HOST": "mp.weixin.qq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }

    #读取上一步获取到的cookies



    #登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1849751598，从这里获取token信息
    response = requests.get(url=url, cookies=cookies)
    token = re.findall(r'token=(\d+)', str(response.url))[0]

    #搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    #搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
    query_id = {
        'action': 'search_biz',
        'begin': '0',
        'count': '5',
        'query': query,
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1'
        }
    #打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = requests.get(search_url, cookies=cookies, headers=header, params=query_id)
    #取搜索结果中的第一个公众号
    lists = search_response.json().get('list')[0]
    #获取这个公众号的fakeid，后面爬取公众号文章需要此字段
    fakeid = lists.get('fakeid')

    #微信公众号文章接口地址
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    #搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
    query_id_data = {

        'action': 'list_ex',
        'begin': '0',#不同页，此参数变化，变化规则为每页加5
        'count': '5',
        'fakeid': fakeid,
        'type': '9',
        'query': '',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        }
    #打开搜索的微信公众号文章列表页
    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
    #获取文章总数
    max_num = appmsg_response.json().get('app_msg_cnt')
    #每页至少有5条，获取文章总的页数，爬取时需要分页爬
    num = int(int(max_num) / 5)
    print('总页数：{}'.format(int(num)))
    #起始页begin参数，往后每页加5
    begin = 0
    while num + 1 > 0 :
        query_id_data = {
            'action': 'list_ex',
            'begin': '{}'.format(str(begin)),  # 不同页，此参数变化，变化规则为每页加5
            'count': '5',
            'fakeid': fakeid,
            'type': '9',
            'query': '',
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',

            }
        print('正在翻页：--------------',begin)

        #获取每一页文章的标题和链接地址，并写入本地文本中
        query_fakeid_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
        fakeid_list = query_fakeid_response.json().get('app_msg_list')
        for item in fakeid_list:
            content_link=item.get('link')
            content_title=item.get('title')
            fileName=query+'.csv'
            with open(fileName,'a',encoding='utf-8') as fh:
                fh.write(content_title+":\n"+content_link+"\n")
        num -= 1
        begin = int(begin)
        begin+=5
        time.sleep(2)

if __name__=='__main__':
    try:
        #登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
        query= input('请输入你想爬取的公众号文章 ：')
        print("开始爬取公众号：" + query)
        get_content(query)
        print("爬取完成")
        # gzlist = ['刘润','L先生说','逻辑思维','CSDN']
        # #登录之后，通过微信公众号后台提供的微信公众号文章接口爬取文章
        # for query in gzlist:
        #     #爬取微信公众号文章，并存在本地文本中
        #     print("开始爬取公众号："+query)
        #     get_content(query)
        #     print("爬取完成")
    except Exception as e:
        print(str(e))
