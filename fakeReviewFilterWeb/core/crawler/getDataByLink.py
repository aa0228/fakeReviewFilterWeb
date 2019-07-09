import requests
from bs4 import BeautifulSoup
from traceback import print_exc
from datetime import datetime
from concurrent import futures
from multiprocessing import Pool
import re
from ..infoDatabase.reviewModels import Product, ReviewUser, Review


DEFAULT_PARSE_NAME = 'lxml'

DEFAULT_REQUEST_HEADERS = {'Host': 'www.amazon.com',
                           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1'}
DEFAULT_TIMEOUT = 10

DEFAULT_GET_PRODUCT_ID_REGEX = '.*?product-reviews/(.*?)/'
DEFUALT_COMPILED_RE = re.compile(DEFAULT_GET_PRODUCT_ID_REGEX)


def getResponse(url, headers=DEFAULT_REQUEST_HEADERS,
                timeout=DEFAULT_TIMEOUT):
    while True:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except:
            print('time_out {}'.format(url))


def getBeautifulSoup(text, parseName=DEFAULT_PARSE_NAME):
    return BeautifulSoup(text, parseName)


def getAllReviewPageLink(productLink):
    while True:
        resp = getResponse(productLink)
        soup = getBeautifulSoup(resp.text)
        link = soup.find('a', class_="a-link-emphasis a-text-bold")
        if link:
            break

    link = link['href']
    if link.startswith('http'):
        return link
    return 'https://www.amazon.com' + link


def getProductIdFromUrl(url, compliedRegex=DEFUALT_COMPILED_RE):
    """

    匹配成功返回productId
    失败返回None

    """
    m = compliedRegex.search(url)
    if m:
        return m.group(1)


def getProduct(soup):
    """

    从BeautifulSoup对象中提取出product对象的信息
    不包括productTypeId
    暂时忽略id

    return product

    """
    try:
        infoDiv = soup.find('div', id='cm_cr-product_info')
        # 获取商品title
        titleDiv = infoDiv.find('div', class_='a-row product-title')
        title = str(titleDiv.find('a').string)
        # 获取商品price
        priceDiv = infoDiv.find('div', class_='a-row product-price-line')
        price = 0
        if priceDiv:
            price = priceDiv.find('span',
                                  class_='a-color-price arp-price').string
            price = float(price.strip('$'))

        product = Product
        product.name = title
        product.price = price
        return product
    except Exception as e:
        print_exc(e)
        raise ValueError("can't get the product info!")


def getUserIdFromUrl(url, compiledRegex=re.compile('.*?profile/([^/]*)')):
    """

    成功返回userId
    否则返回None

    """
    m = compiledRegex.search(url)
    if m:
        return m.group(1)


def getDateTimeFromStr(timeStr, timeP='on %B %d, %Y'):
    """

    timeStr 的 格式应该是 'on May 1, 2015'

    """
    return datetime.strptime(timeStr, timeP)


def getVoteCountFromString(string):
    """

    格式应该是 '123 is helpful'

    """
    countStr = string.strip().split()[0]
    if countStr == 'One':
        return 1
    else:
        return int(countStr)


def getNextPageUrl(soup):
    try:
        pageDiv = soup.find('div', id='cm_cr-pagination_bar')
        a = pageDiv.find('li', class_='a-last').find('a')
        return 'https://www.amazon.com' + a['href']
    except:
        return None


def getUsersAndReviews(soup, product):
    try:
        reviews = []
        users = []
        with open('test.html', 'w') as file:
            print(soup.prettify(), file=file)
        reviewListDiv = soup.find('div', id='cm_cr-review_list')
        for reviewDiv in reviewListDiv.findAll('div', recursive=False):
            if 'id' not in reviewDiv.attrs:
                continue
            review = Review()
            reviewDiv = reviewDiv.div
            scoreA, summaryA = reviewDiv.div.findAll('a')
            # 提取出评分信息
            review.reviewScore = float(scoreA['title'].split()[0])
            # 提取评论summary信息
            review.reviewContent = str(summaryA.string)

            # 提取评论的user信息
            user = ReviewUser()
            userIdAndTimeDiv = reviewDiv.div.nextSibling
            userInfoA = userIdAndTimeDiv.find('a',
                                              attrs={'data-hook':
                                                     'review-author'})
            user.id = getUserIdFromUrl(userInfoA['href'])
            user.name = str(userInfoA.string)
            review.reviewUserId = user.id

            # 提取评论时间
            timeStr = userIdAndTimeDiv.find('span',
                                            attrs={'data-hook':
                                                   'review-date'}).string
            review.reviewTime = getDateTimeFromStr(timeStr)

            # 提取评论的内容
            reviewContentDiv = userIdAndTimeDiv.nextSibling.nextSibling
            review.reviewContent = str(reviewContentDiv.span.string)

            # 提取评论的有用数信息
            voteDiv = reviewContentDiv.nextSibling
            voteSpan = voteDiv.find('span', class_='review-votes')
            review.reviewUsefulCount = 0
            review.reviewVotedTotalCount = 0
            if voteSpan:
                review.reviewUsefulCount = getVoteCountFromString(voteSpan.
                                                                  string)

            review.productId = product.id
            review.productTypeId = product.productTypeId

            reviews.append(review)
            users.append(user)
        return users, reviews
    except:
        raise ValueError("can't get review data!")


def getData(url, productTypeId):
    reviewPageUrl = getAllReviewPageLink(url)
    users = []
    reviews = []
    product = None
    while reviewPageUrl:
        resp = getResponse(reviewPageUrl)
        soup = getBeautifulSoup(resp.text)
        while soup.find('div', id='cm_cr-review_list') is None:
            resp = getResponse(reviewPageUrl)
            soup = getBeautifulSoup(resp.text)
            print('wrong!')

        if product is None:
            product = getProduct(soup)
            product.id = getProductIdFromUrl(reviewPageUrl)
            product.productTypeId = productTypeId

        users_, reviews_ = getUsersAndReviews(soup, product)
        users.extend(users_)
        reviews.extend(reviews_)
        print(len(users))
        reviewPageUrl = getNextPageUrl(soup)
    return product, users, reviews


def getMaxPageCount(soup):
    pageDiv = soup.find('div', id='cm_cr-pagination_bar')
    lastPageLi = pageDiv.find('li', class_='a-last').previousSibling
    maxPageNum = int(lastPageLi.a.string)
    return maxPageNum


def getReviewPageSoup(url, pageNumber):
    if '?' in url:
        url += '&pageNumber=' + str(pageNumber)
    else:
        url += '?pageNumber=' + str(pageNumber)
    resp = getResponse(url)
    soup = getBeautifulSoup(resp.text)
    while soup.find('div', id='cm_cr-review_list') is None:
        resp = getResponse(url)
        soup = getBeautifulSoup(resp.text)
        print('wrong!')
    return soup


def getDataAsync(url, productTypeId, threadCount=25):
    reviewPageUrl = getAllReviewPageLink(url)

    soup = getReviewPageSoup(reviewPageUrl, 1)
    product = getProduct(soup)
    product.id = getProductIdFromUrl(reviewPageUrl)
    product.productTypeId = productTypeId

    maxPageCount = getMaxPageCount(soup)
    users = []
    reviews = []

    with futures.ThreadPoolExecutor(threadCount) as executor:
        soups = [executor.submit(getReviewPageSoup, reviewPageUrl, i)
                 for i in range(1, maxPageCount + 1)]
        for future in futures.as_completed(soups):
            soup = future.result()
            _users, _reviews = getUsersAndReviews(soup, product)
            users.extend(_users)
            reviews.extend(_reviews)
    return product, users, reviews


def getUsersAndReviewsOfAPage(reviewPageUrl, pageNo, product):
    soup = getReviewPageSoup(reviewPageUrl, pageNo)
    return getUsersAndReviews(soup, product)


pool = Pool()


def getDataParallel(url, productTypeId):
    reviewPageUrl = getAllReviewPageLink(url)
    soup = getReviewPageSoup(reviewPageUrl, 1)
    product = getProduct(soup)
    product.id = getProductIdFromUrl(reviewPageUrl)
    product.productTypeId = productTypeId

    maxPageCount = getMaxPageCount(soup)
    results = pool.starmap(getUsersAndReviewsOfAPage,
                           ((reviewPageUrl, i, product)
                            for i in range(1, maxPageCount + 1)))
    users = []
    reviews = []
    for users_, reviews_ in results:
        users.extend(users_)
        reviews.extend(reviews_)
    return product, users, reviews


def getUsersAndREviewsOfSumPage(reviewPageUrl, start, end, product,
                                threadCount=None):
    users = []
    reviews = []
    with futures.ThreadPoolExecutor(threadCount) as executor:
        soups = [executor.submit(getReviewPageSoup, reviewPageUrl, i)
                 for i in range(start, end)]
        for future in futures.as_completed(soups):
            soup = future.result()
            _users, _reviews = getUsersAndReviews(soup, product)
            users.extend(_users)
            reviews.extend(_reviews)
    return users, reviews


__getDataParallelProcessExecutor = futures.ProcessPoolExecutor()
__getDataParallelProcessExecutor.daemon = True


def getDataParallel2(url, productTypeId, processCount=None):
    reviewPageUrl = getAllReviewPageLink(url)
    soup = getReviewPageSoup(reviewPageUrl, 1)
    product = getProduct(soup)
    product.id = getProductIdFromUrl(reviewPageUrl)
    product.productTypeId = productTypeId

    maxPageCount = getMaxPageCount(soup)
    users = []
    reviews = []
    executor = __getDataParallelProcessExecutor
    # results = [executor.submit(getUsersAndReviewsOfAPage,
    #                            reviewPageUrl, i, product)
    #            for i in range(1, maxPageCount + 1)]
    processCount = executor._max_workers
    perProcessPageCount = max(1, maxPageCount // processCount)
    results = [executor.submit(getUsersAndREviewsOfSumPage,
                               reviewPageUrl, start,
                               start + perProcessPageCount,
                               product, 8)
               for start in range(1, maxPageCount,
                                  perProcessPageCount)]
    for future in futures.as_completed(results):
        users_, reviews_ = future.result()
        users.extend(users_)
        reviews.extend(reviews_)
    return product, users, reviews


def getDataParallel3(url, productTypeId):
    reviewPageUrl = getAllReviewPageLink(url)
    soup = getReviewPageSoup(reviewPageUrl, 1)
    product = getProduct(soup)
    product.id = getProductIdFromUrl(reviewPageUrl)
    product.productTypeId = productTypeId
    pass


if __name__ == '__main__':
    url = 'https://www.amazon.com/All-New-Kindle-ereader-Glare-Free-Touchscreen/dp/B00ZV9PXP2/ref=cm_cr_arp_d_product_top?ie=UTF8'
    # url = 'https://www.amazon.com/Featurette-Salt-Ultimate-Female-Action/dp/B004H3H270/ref=cm_cr_arp_d_product_top?ie=UTF8'
    _, users, _ = getData(url, 1)
    # _, users, _ = getDataParallel2(url, 1)
    print(len(users))
