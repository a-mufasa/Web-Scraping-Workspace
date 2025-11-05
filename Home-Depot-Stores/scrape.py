import httpx
from bs4 import BeautifulSoup
import json
import csv
import re
import time
import sys
from pathlib import Path

# Custom headers to exactly match browser request
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Cookie": 'THD_CACHE_NAV_PERSIST=; AMCV_F6421253512D2C100A490D45%40AdobeOrg=MCMID|19428411125006938243564526140123577999; DELIVERY_ZIP=72758; _px_f394gi7Fvmc43dfg_user_id=YTI3YTZhMDEtODM3MS0xMWYwLThjZDYtODEyNjZlZGZmNWNh; ajs_anonymous_id=fcf50ed1-2492-4b17-83d4-18fdf9374247; trx=5703342737809048219; _gcl_au=1.1.1997457657.1756318455; QuantumMetricUserID=386395dec57e0b5a18c3fc5b00b9c5fd; thda.u=91f05020-a605-3c09-1cb8-16f7c3f087e3; _vwo_uuid_v2=D8973EA37877B7B302D030D8C16D8BAD4|f0212e4ba239551c3737801fe8ab3e13; _sp_id.edb6=984fa9a7-96de-46dd-9ecd-318b2a305bc2.1758223126.1.1758223126..a0487e0b-e255-4ca1-9d59-a141f547caf9..4f40adee-e3a5-401a-95ba-81b62b2a20a2.1758223126424.2; _fbp=fb.1.1758223126476.18856745793786635; _uetvid=4c69ca4094c411f0a0269b33ff78e413; _ga_SR8J66MRNW=GS2.1.s1758223126$o1$g1$t1758223200$j60$l0$h0; _ga_FKD4YPQKPH=GS2.2.s1758661499$o1$g1$t1758661642$j20$l0$h0; _ga_BVDZ2C1N68=GS2.1.s1758661501$o1$g1$t1758661645$j14$l0$h0; _ga_3J2DTZJZ6X=GS2.1.s1760988272$o24$g1$t1760988518$j21$l0$h0; akacd_usbeta=3939128962~rv=36~id=69320020cd7dd16c961579c8290b8ba4; _bman=2aad6d0501053b5bf6b763161f0dc2fa; HD_DC=origin; pxcts=0883c925-b42c-11f0-9cad-5f4c6672bc65; _pxvid=0883c21c-b42c-11f0-9cab-1cde790de501; thda.s=fa88c28b-8c49-342a-1d90-625433f5abce; _ga_9H2R4ZXG4J=GS2.1.s1761676168$o2$g0$t1761676168$j60$l0$h0; _ga=GA1.2.2075105431.1756318454; THDSSO=FnC227410yDDFjjjerJ6q6XOClfEOSwYlqxDyBpFQo6vikY6nBsrgNOjwOB6eoQmUv0eFzzpzYkAaWZBFyb3wLihYeDgoSVS8nKTio9ooU3EJnWRQq2qkBnJAJyFdF9svSLQMmZ2yJEdOMy6qK2zjMRbZ6sp9ISOWKIbR6PtvqysNcTa8nH9FBJS7GhrRJJSdFgsEDj1ciblSVI0jB5TwklwHfG5SQhwty46aHpYtfamUhr1vxWjLqIlJC9abHgyofW9POhmqNUasZKupfpLXm56ra43JngW85dGLokYVo1ktQnKPrSCT2HzXN8MDaaLNuJd2QC93485dpgVlxGxe3AcXqYLU1yFsjgofZrRspa457kgjiX4cmxCXzMeCK2zJVjG0Lzvsnjx0fAA8HVpkrqVYwiXRnblynd1cDZ25x7uKrUASvM6ZzYYLhUWYK2emgyaISWXSooa4kSb1okNeHX9LIMR5rzO96K7oTAeUi8gQwfaJK9emwVyebUu8Fw2eAmXS58fwK6BWCIerKxlzLjVUSAFW2JAXiMEPcgLvbboFF36hLJyBS8sccaLkW1xyEzbFdmdUkcKkQCFuKXZP2jqQ6xVFRffwQ861mBsvWJ77zCrVbfv5WCALgQqY0u2EjURmIiBvhRXaQCwnx6S7YbvOWbeSx8qjI5OYdIMGX1LSorRVhFsKNURuSQF4FIZ41mfL1FC8agjyHUJ8YcnV2j2WSxUXw29hlssCf2TLIh4CCNXNSfANDvTAUVMxZtd; PF=LP12DxhoZ5Xwg5nQX3iQzrmmVGISqBpgMeEsLNwtzBvr; PF.PERSISTENT=eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..aptRkr_XUKN5PHLVOOitGg.huitrjLxZk3HCTNBdNSNHN0MQ8MYL7JCWvJYoGmQtt8HOBJHoXkHqM4J1zdXVYgPBT2NSgcR2IPoiBTwQXqgLxTD9WoUmvQoeu6xrGIeCA-FpQCFBAZwfpx6MlwQTCZH.KejH1wi3UddrPmYodth8AA; _ga_M8YZQYQTBJ=GS2.2.s1761850173$o13$g1$t1761850680$j60$l0$h0; QSI_SI_3pIUG1VWoD316xo_intercept=true; akavpau_prod=1762271794~id=b21235ec8a18e2c5a3c8198d43aefadb; PIM-SESSION-ID=OFw4Prwco9NT385o; ftr_ncd=6; THD_NUGGET=91f05020-a605-3c09-1cb8-16f7c3f087e3; THD_CUSTOMER=eyJzIjoiMDYyRjJFMjhFRUYzOTFBRDBVOmJiNDdlYjcwLTAwMDgtNGY3ZS1hOTJmLTE5NDRiZjA2NmIwOCIsInUiOiIwNjJGMkUyOEVFRjM5MUFEMFUiLCJpIjoiTkdWTFdqNDlLSExEU2ZwVjNWTXoyaXJHVURFLipBQUpUU1FBQ01ESUFBbE5MQUJ4VU1YWkdXaXQwVEV4NVlsTnlhVnBMVlRCelVqTnZkM0kyV2xFOUFBUjBlWEJsQUFORFZGTUFBbE14QUFJd01RLi4qIiwiYyI6IkIyQyIsInQiOiIwNjJGMkUyOEVFRjA5MUFEMFMiLCJ2IjoxNzYyMjc0MjM5OTc1LCJrIjoieSJ9.KZcKRDWDjqUkHB3xu0M-12anlzk647ZQjBKPJlYLAcn-rr5lJuzCmBdIADQ-IkuJ_b_19l1MWGRoiF5TZ0lbuBNAyCcPQkspWaGS_Ro_NIIojiJzE8b6HWfm546JPHWZo9OgdcgMXko_8aTNhoN7wH4Yp7KSjmt0vYrBWIvTE9A; THD_TRANSACT=e5b3dfa1-8eaa-4c42-ba0b-86eb3766fff7; WORKFLOW=LOCALIZED_BY_STORE; THD_FORCE_LOC=0; THD_INTERNAL=0; THD_PERSIST=C4%3D8445%2BRogers%20-%20Rogers%2C%20AR%2B%3A%3BC4_EXP%3D1793810240%3A%3BC12%3Dahmedr.moustafa%40gmail.com%3A%3BC12_EXP%3D1793810240%3A%3BC13%3Dself%3A%3BC13_EXP%3D1793810240%3A%3BC24%3D72758%3A%3BC24_EXP%3D1793810240%3A%3BC39%3D1%3B8%3A00-20%3A00%3B2%3B6%3A00-23%3A00%3B3%3B6%3A00-23%3A00%3B4%3B6%3A00-23%3A00%3B5%3B6%3A00-23%3A00%3B6%3B6%3A00-23%3A00%3B7%3B6%3A00-23%3A00%3A%3BC39_EXP%3D1762277840; DELIVERY_ZIP_TYPE=LOGIN; X-AK-PIM-INJECT=sync; bm_ss=ab8e18ef4e; AKA_A2=A; bm_mi=C9A8A44BEBC9F0FAE34ADD5CD44E4152~YAAQIfjNF4bUWSiaAQAAr+XLVB0SAmUOnmy33ftYY90rRGSyDrqZ/xgmy2sV5FYUZqgXX0jScDK2cpQfWxeiaG5BzwigCERxpTthaEZVz5bQ39w6iQZCPSyZPfZwK3RmrYvQJSX738dHurm3GpZZYY9PFE+rVRccCqf+2ldWwXoaviaFGrkDS8f/Lkxdq5F8CdlqY/ietE1WyAQn53Feizwgk4sd1N3I8UwlazVH4rwRvW/Q3XudPyBVh7ZNlVxNJv0sCF/SGkzxJFdzgPuN8i9D/Ts0cGygCWypsA1bKMABt1/DBtefU95ThKq9d2C90Fp/HXAO0k09L9TclL3QI6E=~1; THD_NR=1; THD_LOCALIZER=%7B%22THD_STRFINDERZIP%22%3A%2272758%22%2C%22THD_STORE_HOURS_EXPIRY%22%3A1762362840%2C%22THD_STORE_HOURS%22%3A%221%3B8%3A00-20%3A00%3B2%3B6%3A00-23%3A00%3B3%3B6%3A00-23%3A00%3B4%3B6%3A00-23%3A00%3B5%3B6%3A00-23%3A00%3B6%3B6%3A00-23%3A00%3B7%3B6%3A00-23%3A00%22%2C%22THD_LOCSTORE%22%3A%228445%2BRogers%20-%20Rogers%2C%20AR%2B%22%2C%22THD_INTERNAL%22%3A%220%22%2C%22THD_FORCE_LOC%22%3A%220%22%2C%22WORKFLOW%22%3A%22LOCALIZED_BY_STORE%22%7D; ak_bmsc=6BE5387A511AA186562EAC757A0501F0~000000000000000000000000000000~YAAQIfjNF8DUWSiaAQAAqejLVB3CBu008UqNVYPNHP/wVIgYecnBX00zUs7StLMfnO91AOwueULOuRQOuIGDZjjE/mXCgFUC2RGTqRrGyyMXDDspowsWg10NldaiGUEFng6BN4aoB7QRK8HHh9A/37Llydrwa4sB/rQ7QpqqReN8IxiCbka/MnxtdoUldTOiHvy6sh0uOrmTO3BKo0yelIPjk4ZkpwOzCnJ3da4+UhIOqoF5bjVUqZsDmSuZt350BkNGypgq2cPIfqXaMCrxZbGa8LIaeL+FOZTToyKfL0Qmnjys/Gk4pB9b1itM0eyl0sIm3PQrlVWkXYq3uTII+I2AGdD5x4I4NSH22+As6aAnHrLjRjE6wr66mjpxdMxWspHq1gZh7pH/sCuEZ7QD4W8DPQSfEN7G31j0CQooTzcyqFKkFGUdmmiihMSJvgw9yiBqGoz+/vmVZ1mPrUWpkAXNc75YdBlRrvJxp57V+3xaGA9Vl9NUdCxDMneatL/H6qPw; QuantumMetricSessionID=ad680b4646eecab3e89ae1926e894ba9; _abck=99DB6B8E864B4AE4BA7EC483F16B407D~0~YAAQIfjNF572WSiaAQAAobTNVA5j3o6U2s9YzlOx/C/lX5Sixot9RWn/yfOW0rK9QvgYkDgRVYkbV1dibtDpU0FpuAYvWrZTxbKOGxkBhiuTimIq/Xq5ifZp8oQpVHQB6g70/vCGTgX3ZD1QFwYyxKldDAi5hxwegzdau+2bmyD+5p5vPBV58jHjPZ/r90pyS2K43/3oUcHifhnUJ993U+Vt7a5WTvrGR3O2Xwpx9TSNPEaq+OgWVIO9CTPUJCu+l9E/Xd3qsPTYQwhfwY2mL/qhinx+PK0XJl4sgH2O+6MDz4mIc363ABIongFJIfXPYFF5fqW6cThZm6GHf2x59kUkl+aDLykzkye/Zp4gY/216kTtX8mpvyCCyHSNbG1ndPYSh42l/xN6afP1dBdpvNVhJqH+ubzed4m+UVKAimlZqNpBmublGyjdKv/r7QuwesmitRl8RWW0jgdb3w3A7mUG1BzMA+4tQKjg14lv9Q0z2Fhas5BLrP6z6Ds+yIUuE/wjsHnV2WzJapLYHNLEk75hZc1qrNeiVBMI3lOgjFc016wc9Mkd2fgRQjeRAMq5XtlO/dNn7AiHmK/VlyIUnPPslB8SqcOipjEzrf7B0RlOb8ilEQ77ls3HUReDUaLGdQdMJexJlDBRP9X9NxoDeRgdbNqIXGKF2tTBNGTMzC5kfSrG0TNFljw3TImxAlxBfefSVMi5y4wATDl5s3fjReEulyQvasGL7W6lecPvyIav3D6QVP98MES9btWloTlxuLOnEZIZKjH8JoXrQCEqF6f4EVUImIZUJPF0+qN85lPUbCf6uvP++9xizpqpHHuI9gZLO582Nky6t31Y4TT3SuSsddqEHA==~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f95Oqh1jbdeFFoZSr4oKO3IETVzhNwRf3qYvHHhAZrEEHNF+ohF+nYBiEKM%2f7SNdFCiwSvWrcne8csh9PahYuoR9CS1+Wstkbj1c~-1; QSI_HistorySession=https%3A%2F%2Fwww.homedepot.com%2Fauth%2Fview%2Fcreateaccount%3Fredirect%3D%2Fl%2FstoreDirectory%26ref%3D~1762274106448%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FstoreDirectory~1762274221995%7Chttps%3A%2F%2Fwww.homedepot.com%2Fauth%2Fview%2Fsignin%3Fredirect%3D%2Fl%2FstoreDirectory%26ref%3D~1762274225504%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FstoreDirectory~1762274243263%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FPR~1762359360687; bm_so=CF3FEE3EC03BF9E1CC836300F180BC66DF1BBE2054EE0DF8C0D41EBC23A65AF8~YAAQKfjNF/5AHyiaAQAAug/5VAVXCbkRW1jeHGm/SxnSgiXaRCwTA24HlQeUQZRbuStWJSr4VqF+EGQJn624HQYxKr4pzky54wuFgg1T/wzLLfJML3dMx7JfBU8s30kFUXuB+bkPHTEeA0ZJyPf229KPZT2NgqFPHE71R9uZsuF5MvoP46K6hyto0jpUUwj72cXAnB4j2hl5VktOA7IK2u48CjppKBY0RaJDCiiUDLdKffmEQlBAHr+MEwk1TvBhhyn7HIsGygakhKrXuB0I7LKamE0KWW2boYWhOXQjDKasNzfY1w6hEieSZYvKCxKbdoDku9qqmFABJSS6fmdIKAo3SB9vAcqqWeQMZYFlbR2O6hD5HO22BSOEzhbfpgnKA6hL5eD7e1W00mHZu++oYSPRmjbrtptNjQIvwIng0O+ptkwoKkh5Xa3U6d3TD0TkfGhfeNS9Jmr77E6w4bffP40=; bm_lso=CF3FEE3EC03BF9E1CC836300F180BC66DF1BBE2054EE0DF8C0D41EBC23A65AF8~YAAQKfjNF/5AHyiaAQAAug/5VAVXCbkRW1jeHGm/SxnSgiXaRCwTA24HlQeUQZRbuStWJSr4VqF+EGQJn624HQYxKr4pzky54wuFgg1T/wzLLfJML3dMx7JfBU8s30kFUXuB+bkPHTEeA0ZJyPf229KPZT2NgqFPHE71R9uZsuF5MvoP46K6hyto0jpUUwj72cXAnB4j2hl5VktOA7IK2u48CjppKBY0RaJDCiiUDLdKffmEQlBAHr+MEwk1TvBhhyn7HIsGygakhKrXuB0I7LKamE0KWW2boYWhOXQjDKasNzfY1w6hEieSZYvKCxKbdoDku9qqmFABJSS6fmdIKAo3SB9vAcqqWeQMZYFlbR2O6hD5HO22BSOEzhbfpgnKA6hL5eD7e1W00mHZu++oYSPRmjbrtptNjQIvwIng0O+ptkwoKkh5Xa3U6d3TD0TkfGhfeNS9Jmr77E6w4bffP40=^1762362200664; bm_sz=AF50D2B8F4217AED0DE5E3C4EAAA0CDE~YAAQKfjNF2xBHyiaAQAAMRn5VB2hJcVf59FQlhHMWC9WX+RamfSu8T+sqg9DsIXy7ILIsGg6p7CC4xeVD2XGtK9PCDiC6de30h6lEKAOfXc2IgZI/kqGw1SS7kb5RRvPTiHHHGsmmXNwCE+a0DwHFVSTPGif1LIu9+cgksqiwkisCwWMMEixGU+OB+uh29GYRvexgoR8tgka5SZNYLMFhgXBxHtYBP/BSUWwIi8ZdsWZwPBcsA6VcxcoPRoDFJwFWv52QySn//PudjmhLIRRmbu5B4P+iWlm8bGaaXS/1SexH+xy4Ss+T71Lu6GRp5Zm/DW+/CRwh/6L+bRvrWUTKAEev5gho74mgJh93M3qsxJCIjsFYkcCRhVQQZO8KSGZSQmyWaxywejSFAAg1h56uGHNKc/5qHPCd+M1Z+VVkQsBU+CqEvAW6HbfWCJupcvh+Btm3pC5EOVJ97c=~3747906~3290932; IN_STORE_API_SESSION=TRUE; RT="z=1&dm=www.homedepot.com&si=99c17541-d222-45a3-9070-8fd2460ea9af&ss=mhm76scv&sl=3&tt=r1&obo=2&rl=1"; kndctr_F6421253512D2C100A490D45_AdobeOrg_cluster=va6; kndctr_F6421253512D2C100A490D45_AdobeOrg_identity=CiYxOTQyODQxMTEyNTAwNjkzODI0MzU2NDUyNjE0MDEyMzU3Nzk5OVIQCN6W8%2DWOMxgBKgNPUjIwAfAB%2DLTkp6Uz; THD_SESSION=; THD_CACHE_NAV_SESSION=; bm_s=YAAQKfjNF55BHyiaAQAAaRz5VAQxl70NKrapyxX3BMsjVP5Kwm/58X+uSAfVcRmTWn1mUjEJIF06QhnHCWLcZcp/IXqmhmY/xFj3cL7anMMvAwOc6KRY6qq73OALguskCGnG99JfDldshkLQY+T9DwZzCSZEiVvcaCLHJ3je8rJ8FZhZ0pDcO18xbgtL+hfwrFtZL0QViqVVYs8LzLsaZsTr39bYdhU4z0uU9Dl+uAhbvLyyBzpSUPaKicb9hvQQXOiIqK5VA7a9yYKnfIXTbgLbG3/oQxltBBuFVHS/O/KBXzl4SPEayruhHPvpzkSYfNNR4jYAJJASanIxjbN6tSdxfj8O+Lj5u4IjqFwIwsohDXe3QJFXumm+OQcMagNC5Ro4E2BKytazIfBHj2CkhgACbvVkHsqN6ewM0Lh6wR4Hmq1oUjvJy9dDq/rj8tYMh8Xs8WYJVM65jmAhqx39TehkQiU3okZl9PrXWRKWH3NWr/RqvWeJylGCh3b/ptT8z/tBz+5ERaaacERyg7gs7l7JhUc3CdKMOxdl3MZi7uoGQwGe1AL0KJQg1ZLtsS+GE3pZmvBb4Q==; bm_sv=32E761D3EFA257ACECA5A8338407969A~YAAQKfjNF59BHyiaAQAAaRz5VB1ZhCbXtgQ7X/Xe68J1hrOQYAtabrmQo5Xl+N8ciH2O2QmPu8C1tda7rR9rrH5gdwSUbOFPSWsEaWifDbSJEiZO4uLI7sWOGXog4JWU6fGYmhjT4tYf0s9d9Jjw4VDx6hPo9w6YtytBwJ7FWvKk5+ww+kR+KuKZITN63wY3ZRtdtW65LHD9OVKCVPPNYtmQfoHgGvxKGAhAxigDcbSMp8Ueu0OvajLc5DAVQT23XhoY~1; _px=Lv9iGCWWRG87YQ0f3nbcyaFHwSFnBjswcdRHaiU4Qg8uHTyaMqtlVZ5y7g4xx2KR4aY8NXOEZGykzQgZkg8vsQ==:1000:PSQhrT7Ei8x5NepAPnn1cbEmRClMM1OjfuFwCcV3NCgI+FiapanHu7wxi9Gh7KlFrwfekb1lsbKD/Ci3MPXP4X8DfS+/W9lwG55+rJUksuhTetbga3lKUpJ/TsZTprgWRYPS31TuWlHkIYxThNq0cDjPUZuOlPayGeJGUKgutDMrHkR/ZJdG5tpsYPhEUt2X2Z1jfFPnPeDOa8nXfkSCd0WMOGRqA8Ddh+S22Zz0mrdVWkVX1KmqF8DJatMkRNrUje9PSr1NYqB/xXpsEEEg8Q==; forterToken=92676b2ca28b4670ba13ea8eae41da42_1762362204553__UDF43_23ck_; _pxde=1f472840332753f50f7c924f84659bd7095f843b9bd493027017a78138babd13:eyJ0aW1lc3RhbXAiOjE3NjIzNjIyMDUyNDUsImluY19pZCI6WyJlM2QyZWU2YWFmYWQ2MmU5Y2ZmMmEzNzZhZmQwMzdhOSJdfQ=='
}

# Create an HTTP/2 client
client = httpx.Client(http2=True, headers=headers, timeout=30, follow_redirects=True)

def extract_apollo_json(soup_obj):
    """
    Searches for a script tag containing __APOLLO_STATE__ and extracts the JSON
    using a regular expression.
    """
    # Use the "string" parameter to avoid the deprecation warning.
    script_tag = soup_obj.find("script", string=re.compile("__APOLLO_STATE__"))
    if not script_tag or not script_tag.string:
        return None
    script_text = script_tag.string.strip()
    # Regex to capture the JSON object between "window.__APOLLO_STATE__ =" and an optional semicolon.
    pattern = re.compile(r"window\.__APOLLO_STATE__\s*=\s*(\{.*\});?", re.DOTALL)
    match = pattern.search(script_text)
    if not match:
        return None
    json_str = match.group(1)
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

# CSV file to write the store info
csv_file = "home_depot_stores.csv"
header = ["Type", "#", "City", "State", "Zip"]

# Check if a state code was provided as command-line argument
target_state = None
if len(sys.argv) > 1:
    target_state = sys.argv[1].upper()
    print(f"Target state specified: {target_state}")
    print(f"Will update only {target_state} stores in existing CSV")
else:
    print("No state specified - will scrape all states")

# Read existing CSV data if it exists and we're doing a targeted update
existing_data = []
if target_state and Path(csv_file).exists():
    print(f"Reading existing CSV file: {csv_file}")
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_row = next(reader)  # Read and verify header
        for row in reader:
            # Keep all rows that don't match the target state
            if len(row) >= 4 and row[3] != target_state:
                existing_data.append(row)
    print(f"Preserved {len(existing_data)} stores from other states")

# Collect new stores data
new_stores = []

# Step 1: Request the store directory page
directory_url = "https://www.homedepot.com/l/storeDirectory"
print(f"Fetching store directory from: {directory_url}")
try:
    response = client.get(directory_url)
except Exception as e:
    print(f"Error fetching {directory_url}: {e}")
    client.close()
    exit(1)

if response.status_code != 200:
    print(f"Error: Received status code {response.status_code} for {directory_url}")
    client.close()
    exit(1)

soup = BeautifulSoup(response.text, "html.parser")
apollo_data = extract_apollo_json(soup)
if not apollo_data:
    print("Error: Could not extract __APOLLO_STATE__ JSON from the directory page.")
    print(f"HTML preview (first 1000 chars):\n{response.text[:1000]}")
    client.close()
    exit(1)

# Extract state entries from the JSON
state_entries = apollo_data.get("ROOT_QUERY", {}) \
                           .get("storeDirectory", {}) \
                           .get("storeDirectory", [])
print(f"Found {len(state_entries)} state entries in the directory.")

# Iterate over each state entry
for state in state_entries:
    state_name = state.get("stateName", "Unknown")
    state_link = state.get("stateLink")
    if not state_link:
        print(f"No stateLink for {state_name}. Skipping.")
        continue
    
    # Extract state code (e.g. "AL") from the stateLink URL
    state_code = state_link.rstrip("/").split("/")[-1]
    
    # If target_state is specified, only process that state
    if target_state and state_code.upper() != target_state:
        continue
    
    print(f"\nProcessing state: {state_name} ({state_code}) - URL: {state_link}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1} for state URL: {state_link}")
            state_response = client.get(state_link)
            if state_response.status_code != 200:
                print(f"Error: Received status code {state_response.status_code} for {state_link}")
                continue
            break  # Success
        except httpx.TimeoutException as te:
            print(f"Timeout on attempt {attempt+1} for {state_link}: {te}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                print("Max retries reached. Skipping this state.")
                state_response = None
                break
        except Exception as e:
            print(f"Error on attempt {attempt+1} for {state_link}: {e}")
            state_response = None
            break
    
    if state_response is None or state_response.status_code != 200:
        continue
    # Parse the state page and extract the __APOLLO_STATE__ JSON
    state_soup = BeautifulSoup(state_response.text, "html.parser")
    state_apollo_data = extract_apollo_json(state_soup)
    if not state_apollo_data:
        print(f"Warning: Could not extract __APOLLO_STATE__ JSON from {state_link}")
        continue
    
    # Find the key that starts with "storeDirectoryByState(" and contains the correct state code.
    store_directory_by_state = None
    for key, value in state_apollo_data.get("ROOT_QUERY", {}).items():
        if key.startswith("storeDirectoryByState(") and f"\"state\":\"{state_code}\"" in key:
            store_directory_by_state = value
            break
    
    if not store_directory_by_state:
        print(f"Warning: No storeDirectoryByState data found for state {state_name} on {state_link}")
        continue
    
    stores_info = store_directory_by_state.get("storesInfo", [])
    if not stores_info:
        print(f"No stores info found for state {state_name}.")
        continue
    
    print(f"Found {len(stores_info)} stores in state {state_name}.")
    
    # Process each store's info
    for store in stores_info:
        address = store.get("address", {})
        city_val = address.get("city", "")
        state_val = address.get("state", "")
        zip_val = address.get("postalCode", "")
        store_url = store.get("url", "")
        if not store_url:
            raise ValueError(f"Missing store URL for store data: {store}")
        # Extract store id as the last part of the URL (after the last slash) & ensure id is always 4 digits by padding with leading zeros
        store_id_val = store_url.rstrip("/").split("/")[-1].zfill(4)
        
        new_stores.append(["Store", store_id_val, city_val, state_val, zip_val])
    
    print(f"Finished processing state: {state_name}")

# Close the HTTP client
client.close()

# Write the combined data to CSV
print(f"\nWriting combined data to {csv_file}")
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    # Write existing data first (sorted by state)
    existing_data.sort(key=lambda x: (x[3], x[1]) if len(x) >= 4 else ("", ""))
    for row in existing_data:
        writer.writerow(row)
    
    # Write new stores data (sorted by state and store number)
    new_stores.sort(key=lambda x: (x[3], x[1]))
    for row in new_stores:
        writer.writerow(row)

print(f"\nScraping complete. Total stores written: {len(existing_data) + len(new_stores)}")
print(f"  - Preserved from other states: {len(existing_data)}")
print(f"  - Newly scraped for {target_state if target_state else 'all states'}: {len(new_stores)}")
print(f"CSV updated: {csv_file}")
