# GitBook文档国内访问解决方案

### 拉取文档至本地服务器，实现极速流程访问

### 背景
   国内访问GitBook文档特别慢，但是又想使用GitBook的界面展示以及编辑功能。<br>
   将每个页面的HTML拉取到本地，进行本地访问
   
#### 问题一、111.*.js 文件加载特别慢
>   将此JS缓存到本地，并替换地址指向本地服务器
  
#### 问题二、点击侧边栏等页面跳转链接时会一直加载
>   将此代码加入到每个页面中， 用于监听跳转时刷新页面<br/>
```
    <script>
        window.addEventListener("click", function(e) {
            var t = e.target.closest(\'a[class*="card"]\') 
                ||  e.target.closest(\'a[class*="navButton"]\')
                ||  e.target.closest(\'a[class*="link"]\')
                ||  null;
            if ( t!==null ) {
                window.location.href = t.href
            }
        },false); 
   </script>
```

#### 问题三、各种图片加载很慢
>   图片一般来说有两类:<br>
>   一是页面中以 "https://blobscdn.gitbook.com/v0/b/" 开头的，<br>
>   此类图片只需要缓存到本地，替换原始链接即可<br>
>   二是页面中以 "https://firebasestorage.googleapis.com/v0/b/" 开头的，<br>
>   此类图片是GitBook基于逻辑解析的，如果直接使用此链接访问，只会得到相应的JSON信息。
>   经过研究发现，将firebasestorage.googleapis.com地址替换为blobscdn.gitbook.com后，
>   再次访问则会直接返回页面，注意后面的参数要完整。<br>
>   故首先将页面中的地址替换为blobscdn，然后逐一缓存下来，再替换原始链接。
>   技巧：将图片链接进行hash计算，判断当前图片是否已经缓存，减少拉取次数，优化爬虫方案。

#### 本程序需要在可访问GitBook文档服务器上执行，执行后的文件配置域名本地访问即可。

