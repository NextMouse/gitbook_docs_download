#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   GitBook 文档拉取、图片缓存、链接跳转
   程序功能流程如下:
   1.拉取指定的文档页面列表
   2.根据文档页面列表逐一拉取页面HTML
   3.拉取页面中https://static.gitbook.com/js/111.*.js文件，缓存到本地，并替换原有链接
   5.植入HTML跳转逻辑代码
   6.爬取HTML里的图片链接，缓存图片，并替换原有链接地址，使图片指向本地
   7.代理访问静态文件文档即可
'''
import urllib2, re, os

# 同步到 github 上的目录文件的 url，用于获取 gitbook 页面的索引
# 以https://docs.gitbook.com/为例
docs_root = 'https://docs.gitbook.com/'
# 站点地图地址，GitBook根据目录生成SUMMARY.md文件
docs_summary = 'https://docs.gitbook.com/master/SUMMARY.md'
# 网站访问域名地址
host = 'docs.test.com'

'''
    加载站点地图，读取文档所有列表地址
'''
def load_sitemap():
    r = urllib2.urlopen(docs_summary)
    return r

'''
    根据文档列表地址获取真正的文档页面地址
'''
def extract(line):
    if line.find('.md') == -1:
        return -1
    original_path = re.findall(r"\((.+?)\)", line)[0]
    if original_path.find('README') >= 0:
        real_path = original_path.replace('README.md', '')
    else:
        real_path = original_path.replace('.md', '/')
    return real_path

'''
   保存JS文件
'''
def save_js_file(dir_path, file_name, file, url_regex):
    file_path = dir_path + '/' + file_name
    file_exists = os.path.exists(file_path)
    if not file_exists:
       url = re.search(url_regex, file).group()
       print('Cache Url {0}').format(url)
       if url:
           url_file = urllib2.urlopen(url).read()
           if url_file :
               print('Saved {0}').format(file_path)
               os.makedirs(dir_path)
               with open(file_path, 'w') as f:
                   url_file = re.sub(r"gitbook-xxxx.firebaseio.com", host, url_file)
                   f.write(url_file)

'''
    下载图片
    基于当前图片URL计算HashCode, 并作为文件名
    每次拉取的图片的时候都会判断当前HashCode是否存在。
'''
def download_img(img_url):
    try:
        hcode = hash(img_url)
        fname = '_imgs/' + str(hcode) + '.png'
        if os.path.exists( fname ):
            print(' ==> ' + fname + '  exists...')
            return fname
        img_url = re.sub("\\\\u0026", "&", img_url)
        #print("Open image url: {0}, hashcode: {1}").format(img_url, hcode);
        resp = urllib2.urlopen(img_url, timeout = 10).read()
        if not os.path.exists('_imgs/'):
            os.makedirs('_imgs/')
        print("Save image: {0}").format(fname)
        with open(fname, "wb") as f:
            # 将内容写入图片
            f.write(resp)
        return fname
    except Exception, e:
        print(str(e))
        print(" ==> Error Image Url: {0}").format(img_url)
        return ''

def save_to_file(file, path):
    if path != '/' and path != '' and not os.path.exists(path):
        print('Making {0}').format(path)
        os.makedirs(path)
    # 缓存JS文件
    js_regex = 'https://static.gitbook.com/js/111.*.js'
    js_dir_path = 'js'
    js_file_name = '111.3.3M.js'
    save_js_file(js_dir_path, js_file_name, file, js_regex)

    with open(path + 'index.html', 'w') as html:
        # 清除链接 https://static.gitbook.com/js/111.XXXX.js
        file = re.sub(js_regex, "https://docs.gitbook.cn/" + js_dir_path + '/' + js_file_name + '?t=' + str(random.random()), file)
        # 将所有.lp地址直接设置为失效
        file = re.sub("gitbook-xxxx.firebaseio.com", host, file)
        # 缓存下载所有blobscdn.gitbook.com下的图片
        rets = re.findall(r'https://blobscdn.gitbook.com/v0/b/gitbook-xxxx.appspot.com/o/[^ \f\n\r\t\v/]+\.png.*?(?=")', file)
        for r in rets:
            img_name = download_img(r)
            if len(img_name) > 0:
                r = r.split('?')[0]
                file = re.sub(r, "https://" + host + "/" + img_name, file)
        # 缓存下载所有firebasestorage.googleapis.com下的图片
        rets = re.findall(r'https://firebasestorage.googleapis.com/v0/b/gitbook-xxxx.appspot.com/o/[^ \f\n\r\t\v/]+\.png.*?(?=")', file)
        for r in rets:
            r2 = re.sub('firebasestorage.googleapis.com', 'blobscdn.gitbook.com', r)
            img_name = download_img(r2)
            if len(img_name) > 0:
                r = r.split('?')[0]
                file = re.sub(r, "https://" + host + "/_imgs/" + img_name, file)
        # 替换错误的地址
        file = re.sub('/_imgs/_imgs', "/_imgs", file)
	    # 直接打开而不走路由
        file = re.sub('<head>', '<head><script>window.addEventListener("click",function(e){var t=e.target.closest(\'a[class*="card"]\')||e.target.closest(\'a[class*="navButton"]\')||e.target.closest(\'a[class*="link"]\')||null;if(t!==null){window.location.href=t.href}},false); </script>', file)
        html.write(file)
    print('Saved {0}index.html').format(path)

'''
    打开某一个文件列表并保存
'''
def crawl_page(path):
    print('Loading {0}{1}').format(root, path)
    f = urllib2.urlopen(root + path)
    print('Url Opened!')
    s = f.read()
    print('Read Url Context!')
    save_to_file(s, path)

'''
    开始执行，循环扫描站点地图列表
'''
def crawl_site():
    sitemap = load_sitemap()
    for line in sitemap:
        path = extract(line)
        if path == -1:
            continue
        crawl_page(path)

if __name__ == '__main__':
    crawl_site()