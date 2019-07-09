import asyncio
import aiohttp
from .getDataByLink import (DEFAULT_REQUEST_HEADERS, DEFAULT_TIMEOUT,
                            getBeautifulSoup,
                            getProductIdFromUrl, getMaxPageCount,
                            getUsersAndReviews, getProduct)


async def asyncGetHtmlContent(url, headers=DEFAULT_REQUEST_HEADERS,
                              timeout=DEFAULT_TIMEOUT):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers,
                                       timeout=timeout) as resp:
                    return await resp.text()
        except:
            print('timeout {}'.format(url))


async def asyncGetAllReviewPageLink(productLink):
    while True:
        content = await asyncGetHtmlContent(productLink)
        soup = getBeautifulSoup(content)
        link = soup.find('a', class_='a-link-emphasis a-text-bold')
        if link:
            break

    link = link['href']
    if link.startswith('http'):
        return link
    return 'https://www.amazon.com' + link


async def asyncGetUsersAndReviewsOfAPage(reviewPageUrl, pageNo,
                                         product):
    if '?' in reviewPageUrl:
        reviewPageUrl += '&pageNumber=' + str(pageNo)
    else:
        reviewPageUrl += '?pageNumber=' + str(pageNo)

    content = await asyncGetHtmlContent(reviewPageUrl)
    soup = getBeautifulSoup(content)

    while soup.find('div', id='cm_cr-review_list') is None:
        content = await asyncGetHtmlContent(reviewPageUrl)
        soup = getBeautifulSoup(content)
        print('wrong!')
    return getUsersAndReviews(soup, product)


async def aioGetData(url, productTypeId):
    reviewPageUrl = await asyncGetAllReviewPageLink(url)

    content = await asyncGetHtmlContent(reviewPageUrl, timeout=2)
    soup = getBeautifulSoup(content)

    product = getProduct(soup)
    product.id = getProductIdFromUrl(reviewPageUrl)
    product.productTypeId = productTypeId

    maxPageCount = getMaxPageCount(soup)

    cors = [asyncGetUsersAndReviewsOfAPage(reviewPageUrl, pageNo, product)
            for pageNo in range(1, maxPageCount + 1)]

    results, _ = await asyncio.wait(cors)

    users = []
    reviews = []
    for future in results:
        _users, _reviews = await future
        users.extend(_users)
        reviews.extend(_reviews)

    return product, users, reviews


def asyncGetData(url, productTypeId):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(aioGetData(url, productTypeId))
    # loop.close()
    return result


if __name__ == '__main__':
    # url = 'https://www.amazon.com/Featurette-Salt-Ultimate-Female-Action/dp/B004H3H270/ref=cm_cr_arp_d_product_top?ie=UTF8'
    url = 'https://www.amazon.com/All-New-Kindle-ereader-Glare-Free-Touchscreen/dp/B00ZV9PXP2/ref=cm_cr_arp_d_product_top?ie=UTF8'
    _, users, _ = asyncGetData(url, 1)
    for user in users:
        print(user)
    print(len(users))
