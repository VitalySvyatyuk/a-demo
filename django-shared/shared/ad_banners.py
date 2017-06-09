# -*- coding: utf-8 -*-
# This file added to replace advantage banners representation code from shared_tags.py file


def get_ad_banners(lang, app_url=""):
    banners_list = {
        "ru": [
            u'<a class="button kroufr" style="cursor: pointer;" href="%s/kroufr.html" >'
            u'<em>&nbsp;</em>'
            u'<span style="line-height: 35px" >ЧЛЕНСТВО В КРОУФР</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button deposits" style="cursor: pointer;" href="%s/trading/" >'
            u'<em>&nbsp;</em>'
            u'<span style="line-height: 18px">ДЕПОЗИТЫ В 6 ВАЛЮ-<br/>ТАХ И 4 МЕТАЛЛАХ</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            #u'<a class="button courses" style="cursor: pointer;" href="%s/action.html" >\
            #     <em></em>\
            #     <span>БЕСПЛАТНЫЕ<br>КУРСЫ<br>И КОНКУРСЫ</span>\
            #     <b class="clear"></b>\
            # </a>' % (app_url),
            #u'<a class="button education" style="cursor: pointer;" href="%s/education/remote/" >\
            #     <em></em>\
            #     <span>БЕСПЛАТНОЕ<br>FOREX<br>ОБУЧЕНИЕ</span>\
            #     <b class="clear"></b>\
            # </a>' % (app_url),
            u'<a class="button support" style="cursor: pointer;" onclick="SnapEngage.startLink();" >'
            u'<em></em>'
            u'<span style="line-height: 18px">ТЕХНИЧЕСКАЯ<br/>ПОДДЕРЖКА 24/5</span>'
            u'<b class="clear"></b>'
            u'</a>',
            u'<a class="button segregated" style="cursor: pointer;" href="%s/segregate_accounts/" >'
            u'<em></em>'
            u'<span style="line-height: 18px">СЕГРЕГИРОВАННЫЕ<br>СЧЕТА</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            #u'<a class="button multicurrency" style="cursor: pointer;" href="%s/trading/" >\
            #    <em></em>\
            #    <span>МУЛЬТИВАЛЮТ-<br>НОСТЬ СЧЕТОВ</span>\
            #    <b class="clear"></b>\
            # </a>' % (app_url),
            # u'<a class="button partnership" style="cursor: pointer;" href="%s/partnership_fr.html" >\
            #    <em></em>\
            #    <span>ВЫСОКОЕ<br>ПАРТНЕРСКОЕ<br>ВОЗНАГРАЖДЕНИЕ</span>\
            #    <b class="clear"></b>\
            # </a>' % (app_url),
            u'<a class="button crfn" style="cursor: pointer;" href="http://crfin.ru/ru/reestr-chlenov" >'
            u'<em></em>'
            u'<span style="line-height: 35px">РЕГУЛИРУЕТСЯ ЦРФИН</span>'
            u'<b class="clear"></b>'
            u'</a>'
        ],
        "zh-cn": [
            u'<a class="button courses" style="cursor: pointer;" href="%s/action.html" >'
            u'<em></em>'
            u'<span>模拟比赛和奖励</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button support" style="cursor: pointer;" href="%s/about/contacts/" >'
            u'<em></em>'
            u'<span style="padding-top: 13px; height: 47px">技术支持24</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button segregated" style="cursor: pointer;" href="%s/segregate_accounts/" >'
            u'<em></em>'
            u'<span>“隔离账户”服务</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button multicurrency" style="cursor: pointer;" href="%s/trading/" >'
            u'<em></em>'
            u'<span style="padding-top: 13px; height: 47px">多货币账户</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button partnership" style="cursor: pointer;" href="%s/partnership_fr.html" >'
            u'<em></em>'
            u'<span>高佣金合作方案</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url
        ],
        "other": [
            u'<a class="button courses" style="cursor: pointer;" href="%s/action.html" >'
            u'<em></em>'
            u'<span>FREE<br>CONTESTS<br>AND BONUSES</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button support" style="cursor: pointer;" href="%s/about/contacts/" >'
            u'<em></em>'
            u'<span style="padding-top: 13px; height: 47px">TECHNICAL<br>SUPPORT 24</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button segregated" style="cursor: pointer;" href="%s/segregate_accounts/" >'
            u'<em></em>'
            u'<span>SEGREGATED<br>ACCOUNTS</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button multicurrency" style="cursor: pointer;" href="%s/trading/" >'
            u'<em></em>'
            u'<span style="padding-top: 13px; height: 47px">MULTICURRENCY<br>ACCOUNTS</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url,
            u'<a class="button partnership" style="cursor: pointer;" href="%s/partnership_fr.html" >'
            u'<em></em>'
            u'<span>HIGH<br>PARTNER<br>COMPENSATION</span>'
            u'<b class="clear"></b>'
            u'</a>' % app_url
        ]
    }
    return banners_list.get(lang, "other")