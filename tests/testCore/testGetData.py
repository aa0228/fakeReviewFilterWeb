import unittest
from fakeReviewFilterWeb.core.crawler.asyncGetDataByLinkWithAiohttp \
    import asyncGetData


class TestGetDataFromInternet(unittest.TestCase):
    def testGetData(self):
        url = 'https://www.amazon.com/Featurette-Salt-Ultimate-Female-Action/dp/B004H3H270/ref=cm_cr_arp_d_product_top?ie=UTF8'
        url = 'https://www.amazon.com/gp/product/B00HZYDW5E/ref=s9_acsd_top_hd_bw_b16T7H_c_x_1_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-3&pf_rd_r=SBBRQBSE2BS5KTN1A0E1&pf_rd_t=101&pf_rd_p=bf9c75c1-2cf7-5323-97d7-54c559da3518&pf_rd_i=16318231'
        _, users, _ = asyncGetData(url, 1)
        for user in users:
            print(user)
        print(len(users))
