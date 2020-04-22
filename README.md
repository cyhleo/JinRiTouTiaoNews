## JinRiTouTiaoNews
scrapy+pyppeteer，爬取今日头条中新闻及热门评论信息。 

反爬措施：今日头条的首页采取异步加载，请求参数加密的反爬措施；
         热门评论的数据，采取的是ajax异步加载反爬措施。    
解决方法：对于今日头条首页使用pyppeteer来模拟浏览器行为进行反反爬;
         而对于热门评论数据的抓取，则通过开发者工具来分析数据接口url来进行反反爬。   

每条新闻数据 包含如下字段：新闻标题、新闻来源、总评论数、新闻发布时间、新闻内容。       
每条评论数据 包含如下字段：新闻id、评论者的用户名、评论时间、点赞数、评论内容。

## 部分结果展示

新闻信息   
![](https://github.com/cyhleo/JinRiTouTiaoNews/blob/master/image/news.png)    

评论信息   
![](https://github.com/cyhleo/JinRiTouTiaoNews/blob/master/image/comments.png)

## 爬取思路

1. 通过今日头条首页('https://www.toutiao.com/'),
获取每条新闻的id号（如6817605504718602760）。
请求过程中需携带加密参数，加密参数难以破解，故而使用pyppeteer库来模拟浏览器操作，获取网页的源代码。

    编辑下载器中间件NewsHotDownloaderMiddleware，在 process_request方法中使用pyppeteer库模拟浏览器操作，构造HtmlResponse，并将其返回。


2. 访问新闻详情页(如'https://www.toutiao.com/a6817605504718602760/')，
实例化ToutiaoItem，为字段title（新闻标题）、source（来源）、comment_num（总评论数）、time（发布时间）、news_id（新闻id）、news_content（新闻内容）赋值。

    编辑下载器中间件ProxyDownloaderMiddlerware， 使用动态转发，随机获取代理。

    编辑下载器中间件RandomUserAgentDownloaderMiddleware，使用fake_useragent库，随机获取UserAgent。

    编辑 item pipeline MongoDBPipeline，将ToutiaoItem持久化到mongodb数据库。


3. 访问新闻详情页(如'https://www.toutiao.com/article/v2/tab_comments/?aid=24&app_name=toutiao-web&group_id=6817605504718602760&item_id=6817605504718602760&offset=0&count=5')，
解析新闻的热门评论，yield ToutiaoCommentItem实例，yield包含下一页评论url的request对象。

    使用下载器中间件ProxyDownloaderMiddlerware， 采用动态转发，随机获取代理。

    使用下载器中间件RandomUserAgentDownloaderMiddleware，采用fake_useragent库，随机获取UserAgent。

    编辑 item pipeline TimePipeline，将’time’字段由时间戳格式转换为"%Y-%m-%d %H:%M:%S"格式。

    采用item pipeline MongoDBPipeline，将ToutiaoCommentItem持久化到mongodb数据库。


## 运行项目方法
执行 toutiao_test\run.py 文件
