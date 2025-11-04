import httpx
from bs4 import BeautifulSoup
import json
import csv
import re
import time

# Custom headers to exactly match browser request
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
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
    "Cookie": 'THD_PERSIST=; THD_CACHE_NAV_PERSIST=; AMCV_F6421253512D2C100A490D45%40AdobeOrg=MCMID|19428411125006938243564526140123577999; DELIVERY_ZIP=72758; _px_f394gi7Fvmc43dfg_user_id=YTI3YTZhMDEtODM3MS0xMWYwLThjZDYtODEyNjZlZGZmNWNh; ajs_anonymous_id=fcf50ed1-2492-4b17-83d4-18fdf9374247; trx=5703342737809048219; _gcl_au=1.1.1997457657.1756318455; QuantumMetricUserID=386395dec57e0b5a18c3fc5b00b9c5fd; thda.u=91f05020-a605-3c09-1cb8-16f7c3f087e3; _vwo_uuid_v2=D8973EA37877B7B302D030D8C16D8BAD4|f0212e4ba239551c3737801fe8ab3e13; _sp_id.edb6=984fa9a7-96de-46dd-9ecd-318b2a305bc2.1758223126.1.1758223126..a0487e0b-e255-4ca1-9d59-a141f547caf9..4f40adee-e3a5-401a-95ba-81b62b2a20a2.1758223126424.2; _fbp=fb.1.1758223126476.18856745793786635; _uetvid=4c69ca4094c411f0a0269b33ff78e413; _ga_SR8J66MRNW=GS2.1.s1758223126$o1$g1$t1758223200$j60$l0$h0; _ga_FKD4YPQKPH=GS2.2.s1758661499$o1$g1$t1758661642$j20$l0$h0; _ga_BVDZ2C1N68=GS2.1.s1758661501$o1$g1$t1758661645$j14$l0$h0; _ga_3J2DTZJZ6X=GS2.1.s1760988272$o24$g1$t1760988518$j21$l0$h0; akacd_usbeta=3939128962~rv=36~id=69320020cd7dd16c961579c8290b8ba4; _bman=2aad6d0501053b5bf6b763161f0dc2fa; HD_DC=origin; DELIVERY_ZIP_TYPE=AUTO; pxcts=0883c925-b42c-11f0-9cad-5f4c6672bc65; _pxvid=0883c21c-b42c-11f0-9cab-1cde790de501; thda.s=fa88c28b-8c49-342a-1d90-625433f5abce; _ga_9H2R4ZXG4J=GS2.1.s1761676168$o2$g0$t1761676168$j60$l0$h0; akavpau_prod=1761676488~id=67c3cc54475a6d5d0d973fe3955f227e; _ga=GA1.2.2075105431.1756318454; THDSSO=FnC227410yDDFjjjerJ6q6XOClfEOSwYlqxDyBpFQo6vikY6nBsrgNOjwOB6eoQmUv0eFzzpzYkAaWZBFyb3wLihYeDgoSVS8nKTio9ooU3EJnWRQq2qkBnJAJyFdF9svSLQMmZ2yJEdOMy6qK2zjMRbZ6sp9ISOWKIbR6PtvqysNcTa8nH9FBJS7GhrRJJSdFgsEDj1ciblSVI0jB5TwklwHfG5SQhwty46aHpYtfamUhr1vxWjLqIlJC9abHgyofW9POhmqNUasZKupfpLXm56ra43JngW85dGLokYVo1ktQnKPrSCT2HzXN8MDaaLNuJd2QC93485dpgVlxGxe3AcXqYLU1yFsjgofZrRspa457kgjiX4cmxCXzMeCK2zJVjG0Lzvsnjx0fAA8HVpkrqVYwiXRnblynd1cDZ25x7uKrUASvM6ZzYYLhUWYK2emgyaISWXSooa4kSb1okNeHX9LIMR5rzO96K7oTAeUi8gQwfaJK9emwVyebUu8Fw2eAmXS58fwK6BWCIerKxlzLjVUSAFW2JAXiMEPcgLvbboFF36hLJyBS8sccaLkW1xyEzbFdmdUkcKkQCFuKXZP2jqQ6xVFRffwQ861mBsvWJ77zCrVbfv5WCALgQqY0u2EjURmIiBvhRXaQCwnx6S7YbvOWbeSx8qjI5OYdIMGX1LSorRVhFsKNURuSQF4FIZ41mfL1FC8agjyHUJ8YcnV2j2WSxUXw29hlssCf2TLIh4CCNXNSfANDvTAUVMxZtd; PF=LP12DxhoZ5Xwg5nQX3iQzrmmVGISqBpgMeEsLNwtzBvr; PF.PERSISTENT=eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..aptRkr_XUKN5PHLVOOitGg.huitrjLxZk3HCTNBdNSNHN0MQ8MYL7JCWvJYoGmQtt8HOBJHoXkHqM4J1zdXVYgPBT2NSgcR2IPoiBTwQXqgLxTD9WoUmvQoeu6xrGIeCA-FpQCFBAZwfpx6MlwQTCZH.KejH1wi3UddrPmYodth8AA; _ga_M8YZQYQTBJ=GS2.2.s1761850173$o13$g1$t1761850680$j60$l0$h0; THD_NR=0; QSI_SI_3pIUG1VWoD316xo_intercept=true; bm_ss=ab8e18ef4e; QuantumMetricSessionID=aa46d4fca659de889a0e92a943dbe69f; AKA_A2=A; bm_mi=5B743C4FF50D1D84DC10AE95E4320153~YAAQBfjNFymItDuaAQAA3Cp6Tx1EIV3/HJi7hthBNICk1z5nz9HMLI/ewJiYA63kGsVhID05kPDkVecM6chTHurf6codgGoWXYuSAewpr7TdgojWn9ufDYSKGZN0A9B23IdAiEtLyjSOAnXswKBc4wARkocrJO4MpRNgbpHW44xjhpzM51ifaqAKEr9yLK0QTgRDdTHIV4aehFb0wsDSApjHqI+7fQve0fo6zrrpNz1OrU5YxMHIymSaWqfItbdMbbKwrxDRIKSSbJa0SvQYrzilwDsuNDZu248w6fdd0toV10JtefGv7P26LnhGFheXS9AaAx+5LS0w3k5nKsCjDrU=~1; _abck=99DB6B8E864B4AE4BA7EC483F16B407D~0~YAAQBfjNFzSItDuaAQAAOit6Tw4jw8UNvjHgk9iQWB5nfPnjofP6Q8Pf5lzfOda6JrRTy3E12rAf3o1p9bTVQNtz2J+/RwKoxc5/y6qegvk84TJ2BFN+WoYuuWesDD6HpK8Qk4Q229tDXs8fiAv7ZAS8kpwDg0m7oGaKlkNS14QVTj55N1eBdt46jCXT1rshVBUUJt9ivUZof0P8UoOl+IwRH+Dgvo7EL8QBb0PWE3tDdLoZN4ULNAMTWd//71xBBK9QukYJx1650MxQ2cnHNnhCwpl1O+4IwiGhqFOCTzANsVxvDGyO2e9s/MxCJPX4PlAmjutT+9tknuuOthcQiIKl+gRw+ydhipM2zpTqHxLleVh+plkKCoha7WiIAuXTCwhCPTaeJ4QpGprKSKISPZVNaLduswfAfRGlG69GDYldXj3jWOJiMyRf6RiMo9H/FxMWww9mERvA/uZqnxoy2WVB/Q55G+Mx45y3O4XNezgyIGe/DkMGbEMT7pJ2EVMC9pb2G/yL4IP2jUEUrhoqKkQ5KIThASUUtfcWT5rT9cBFE7cV2tRPoAwNh+xM/ODQpspXEbxH4xwM+DgqknoJFqxp50ixOxjivn5M9RjlJmnoOYnPsDMkG6j3ysH1RZkvbQqElaI=~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f47Rzg7wcTrPRNbko8K2Y6j492f50POCaes2Q5+V0M3PdixaF45uY7HBSOwRXR5XG6IGQdJ1YveaS12nsUeI+4xSXb5yf4DPEQnc~-1; kndctr_F6421253512D2C100A490D45_AdobeOrg_cluster=va6; THD_LOCALIZER=%7B%22THD_STRFINDERZIP%22%3A%2272758%22%2C%22THD_STORE_HOURS_EXPIRY%22%3A1762273598%2C%22THD_STORE_HOURS%22%3A%221%3B8%3A00-20%3A00%3B2%3B6%3A00-23%3A00%3B3%3B6%3A00-23%3A00%3B4%3B6%3A00-23%3A00%3B5%3B6%3A00-23%3A00%3B6%3B6%3A00-23%3A00%3B7%3B6%3A00-23%3A00%22%2C%22THD_LOCSTORE%22%3A%228445%2BRogers%20-%20Rogers%2C%20AR%2B%22%2C%22THD_INTERNAL%22%3A%220%22%2C%22THD_FORCE_LOC%22%3A%221%22%2C%22WORKFLOW%22%3A%22LOC_HISTORY_BY_IP%22%7D; ak_bmsc=DD0F52E125752E91A8411466FA295919~000000000000000000000000000000~YAAQBfjNF6yItDuaAQAA7S16Tx2qBzcqSdz836eIB+ctWc7xK6fmg+BD9gvQDiyRt9wscPg9krRk0v6lyRsdrObPaFWeSTso1bLPdnS9X3lL3aUAb2VUbY8As2GTZwjKcmq91mV0py8HeQAwxJRbwzWHYdNn11uqiFX2AbihOVi/FZl6pjlsvrSzrNNfIsScAE+sCoRZwcCnAnI7Eu4CXGmqIyAWAyMGZfd6VQ1PBisKvUNdXVEA6e6uiHy3qb7S99U/jmOcz01VyJdivKRMLuimNRcT3ySWsHiJ4Y/sOMcxAR+IqH5AYQn1EJP3TX86K2TYYsRImFLt0Qx2lsJlIHyx+pWy1Cncw7Csdk0oAsfRIpTuHSOSw1oYL/g54Pv0QzbplxxU1IFf5LWSMN7K0S0/fvH6x00kwiK9F+1AK7KqLVaYUdIo91W6bytNDL1v3mx2FtPoRpvWZ9y5UKv9Gol0QlciYghVLx2UTUEiAsFCEF2Cy0y+ak7zCFTnZgXTCvsP; QSI_HistorySession=https%3A%2F%2Fwww.homedepot.com%2Fp%2FThe-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2%2F100087613~1761676168471%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FstoreDirectory~1762210512261%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FAK~1762215718392%7Chttps%3A%2F%2Fwww.homedepot.com%2Fl%2FstoreDirectory~1762270000239; bm_so=F6FFEFC8508C3D0885BC45A27459AEFD854891CA2614EC4F2B70D46853B7720F~YAAQkZIuF7DdsCuaAQAA/AOBTwXMibSm8Ifw8CUlMmTbUq9Pmk3zxYYQJnoKEnnhKKUWvQ4wRG0dm/uKNO1Ltva2okiHl+q3WwokZzv149KwNB1W/iQ8ghf6qcSRj23KDM0bpiF4pBi6YzTLGdszdTdKQtWvsN1xTEWu+sfpSG4fjiTNBfq8s3m5XuMaRy07xNeXW7eHBi29ZeywjXEeff4Rca38g/Z9ieWTCMaiE1qtRXpXMKA0OfVIX50dwRMQypQJqAQ/4w6IY1/wApz/eEJrKKqlSDAiSwEJmAlK1e2IQ0uRyUGM2Bxvvj1AYUd7B47u5U81kqKASRwDSo5aNYyTjxbbsEXmUkh4JeBYMaqFo5cDPB87UVNFfK9vgCriFPuwxpWVi9UWzN/8Il7KKwYUV07kLiBqb6Kdvt6RW1ZngwRa/3xF0F/L8MqRFV996vj2ltGCCVKYHcJ1X8KRI6U=; bm_sz=60F3C151FD001CF465D4198FE56649CD~YAAQkZIuF/TssCuaAQAAhk2BTx14P3sdyVvPdgnO46i72mPHz16ctKmuMKCYLfOZAydz0Veug+L9Obeb/e//nQ/GgcyfLTSqBgwgnh/qQ/xvr9H0b0hJ/DEN7NsQnj5XfskRnB4HeFKeKNFQHwuj8wJKHGWFimMyYE9Emu02BjxxwufLLPbIcsBkliO+C/ixGFfeXKbzOnmQ+JVyNijDT4uqGtHsIonU2qnndHKkl7N7hRSTHyLEtzEVbQz3hr6YkldXxNOHVuWjoQmMyhFfrYrR4Wt+eCVrEbYUgTH0LAW6a113y+PqmkejvVw0x3Jtl6xIcJa2Yrinp4cFVMutLFVDsTOTcSCuTtcty2ZWqsCQKmOpaW6IOVrGidIkXHr4JDr352v/XMDIUGj5MT4Sa0cDWpwH8YcIL3miXcuEaKTAdPJzDHQCWGpl+5GGbAr4vDHiWc7ocznh7pXUrb0YNmgT/K0Qehg=~4337989~3425091; IN_STORE_API_SESSION=TRUE; RT="z=1&dm=www.homedepot.com&si=99c17541-d222-45a3-9070-8fd2460ea9af&ss=mhkq20jd&sl=3&tt=ls&obo=2&rl=1"; kndctr_F6421253512D2C100A490D45_AdobeOrg_identity=CiYxOTQyODQxMTEyNTAwNjkzODI0MzU2NDUyNjE0MDEyMzU3Nzk5OVIQCN6W8%2DWOMxgBKgNPUjIwAfAB45yF%5FKQz; bm_s=YAAQKfjNF1rhwieaAQAAok+BTwQN3e7SQ791QDC8cOXSBtJ3z5L+xF1MuFRQd9oq/CEaJjRRwZvIPOHCNYBhfllFtLC8hlCvXSDHFwQf/L8GHfblhwuJHKYuoRWtO0zb9E1ww2CeKSOMTC7I0HG3gYeHY0mUbX4Su/Q0TDzfiXxJmH7CbXGEKa5bP7XogTvumfNNRgCwngqskFUqyGXh2rpAxT5NzpFjWecSiGh+S5Q06TfjlSp9Cyof1kXwQbbL+5MLRZgJCTLIFKKY+vSdnBnvLJdEbPg7hN0ADMQ1arFdqskyDxkVhtMt6jugztIgEKvj4usJErbU2LzcBmLc1rIYEGDCFlSgSErP2A98WyC7ks8c4NfnWhMZVVfwmfooWjRm4FCbMWbSciRjnE5D/MbPZYYcYZ+JQqYjczZCJlL2NFEQZqCjJspc20XTL9xp1lryBNHRMRAe3oYEcRcOfnhlnINnp9zJwQx3pRhg5RwbDPJLVW+RGlIfJc5t0cHdqL22nyiPYICaJLRkLhLI1I85prT9Z11gZagOd/AVeQmO63zzDyeoUnQdVSkXN6ELImZiGE7m/A==; bm_sv=33D11063038933886BBA578FE77BA4EE~YAAQKfjNF1vhwieaAQAAok+BTx0YGc7s/kY7uf/9ZFW1pf/pAeT/7KR9512XDYzTGtQGIXc2j0vqKvmhFOiBg44Crrol5ehA/7eQb1vaJQqD/50t3DSGaqGkNhgO/Xp5RtQgQsX+EfcXgQDJ9p+bsIiOhv/sx1xpwBLZ2qTQUDfQN9XEEHWkH/CW5TT05XxVUom9vuy1dM+WsY0xzBOOyuKmTea0ZW2MBfUGqnXZEObr/+5NcvTn7oac+KuO9NruWnO/~1; bm_lso=F6FFEFC8508C3D0885BC45A27459AEFD854891CA2614EC4F2B70D46853B7720F~YAAQkZIuF7DdsCuaAQAA/AOBTwXMibSm8Ifw8CUlMmTbUq9Pmk3zxYYQJnoKEnnhKKUWvQ4wRG0dm/uKNO1Ltva2okiHl+q3WwokZzv149KwNB1W/iQ8ghf6qcSRj23KDM0bpiF4pBi6YzTLGdszdTdKQtWvsN1xTEWu+sfpSG4fjiTNBfq8s3m5XuMaRy07xNeXW7eHBi29ZeywjXEeff4Rca38g/Z9ieWTCMaiE1qtRXpXMKA0OfVIX50dwRMQypQJqAQ/4w6IY1/wApz/eEJrKKqlSDAiSwEJmAlK1e2IQ0uRyUGM2Bxvvj1AYUd7B47u5U81kqKASRwDSo5aNYyTjxbbsEXmUkh4JeBYMaqFo5cDPB87UVNFfK9vgCriFPuwxpWVi9UWzN/8Il7KKwYUV07kLiBqb6Kdvt6RW1ZngwRa/3xF0F/L8MqRFV996vj2ltGCCVKYHcJ1X8KRI6U=^1762270466160; _px=v1XrfjibgRUWuhhrWstJ7iTEB6FHGeEz35IquMpoN6LDNLFJH0Chd2CFGBLXGPvlinqzpDhlF4AaRaq4wq4j4g==:1000:mUfOhDb5dtWL/8VTIDOsToIUWl4VxgRzPx0SD4NxkyeevWtYbHCUaK5HMNV5qmd6lAzVaOyHdysjvN9LLecidPt+nd4vFQ6iZYvVn4GgVDCfeDKDPU83fosrzo2Fdifn395/Rj+ByScl2xYRXx4HuLHKbIMt64WByU83a5/jUg9oXPYUmvyhurJ7J1SOpWcQCvmHv51UImQ9lRoqCvoD1bjwANuV6iHrh4GTLn6hbMMj6/6N/szTowAz1+/ETIXBfrb2KnKrROCeKRruw+FZRw==; forterToken=92676b2ca28b4670ba13ea8eae41da42_1762270467488__UDF43-m4_23ck_; _pxde=d6b5cc6b1e4505bb71456e6facb368531082bf1cc8549782ae24c02a95d32230:eyJ0aW1lc3RhbXAiOjE3NjIyNzA0Njg3MDAsImluY19pZCI6WyJjOWFiMzdiMGY1NDg4NjA4Njg1N2MwNWYwMmVmNTEwNiJdfQ=='
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

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
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
            
            writer.writerow(["Store", store_id_val, city_val, state_val, zip_val])
        
        print(f"Finished processing state: {state_name}")

# Close the HTTP client
client.close()

print("\nScraping complete. CSV created:", csv_file)
