#!/usr/bin/env python3
"""
搜索潜在客户公司
支持多搜索引擎：百度、Bing、DuckDuckGo
支持代理设置
"""

import argparse
import json
import re
import time
import random
import sys
import os
from urllib.parse import quote, urlparse, unquote
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

EXCLUDE_DOMAINS = [
    'google.com', 'bing.com', 'baidu.com', 'youtube.com', 'facebook.com',
    'twitter.com', 'linkedin.com', 'instagram.com', 'tiktok.com', 'weibo.com',
    'zhihu.com', 'taobao.com', 'jd.com', 'tmall.com', 'amazon.com',
    'github.com', 'gitlab.com', 'gitee.com', 'csdn.net', 'juejin.cn',
    'duckduckgo.com', 'wikipedia.org', 'medium.com', 'reddit.com',
]

PROXIES = None

def init_proxies():
    global PROXIES
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    all_proxy = os.environ.get('ALL_PROXY') or os.environ.get('all_proxy')
    
    if https_proxy:
        PROXIES = {'http': https_proxy, 'https': https_proxy}
    elif http_proxy:
        PROXIES = {'http': http_proxy, 'https': http_proxy}
    elif all_proxy:
        PROXIES = {'http': all_proxy, 'https': all_proxy}
    
    if PROXIES:
        print(f"Using proxy: {PROXIES.get('https', 'N/A')}", file=sys.stderr)
    
    return PROXIES


def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }


def is_valid_domain(domain):
    if not domain or len(domain) < 4:
        return False
    if '.' not in domain:
        return False
    for exclude in EXCLUDE_DOMAINS:
        if exclude in domain:
            return False
    return True


def clean_company_name(title):
    title = re.sub(r'\s*[-|]\s*.*$', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def baidu_search(query, limit=50):
    results = []
    url = f"https://www.baidu.com/s?wd={quote(query)}&rn={min(limit, 50)}"
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15, proxies=PROXIES)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for div in soup.select('div.result'):
            title_elem = div.select_one('h3')
            link_elem = div.select_one('a')
            
            if title_elem and link_elem:
                link = link_elem.get('href', '')
                domain = urlparse(link).netloc.replace('www.', '')
                
                if is_valid_domain(domain):
                    results.append({
                        'name': clean_company_name(title_elem.text),
                        'domain': domain,
                        'url': link,
                        'description': '',
                        'source': 'baidu'
                    })
                
                if len(results) >= limit:
                    break
                    
    except Exception as e:
        print(f"Baidu search error: {e}", file=sys.stderr)
    
    return results


def bing_search(query, limit=50):
    results = []
    url = f"https://www.bing.com/search?q={quote(query)}&count={min(limit, 50)}"
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15, proxies=PROXIES)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for li in soup.select('li.b_algo'):
            title_elem = li.select_one('h2')
            link_elem = li.select_one('a')
            snippet_elem = li.select_one('p') or li.select_one('.b_caption p')
            
            if title_elem and link_elem:
                href = link_elem.get('href', '')
                
                if href.startswith('/ck/a?'):
                    continue
                
                domain = urlparse(href).netloc.replace('www.', '')
                
                if is_valid_domain(domain):
                    results.append({
                        'name': clean_company_name(title_elem.text),
                        'domain': domain,
                        'url': href,
                        'description': snippet_elem.text if snippet_elem else '',
                        'source': 'bing'
                    })
                    
    except Exception as e:
        print(f"Bing search error: {e}", file=sys.stderr)
    
    return results


def duckduckgo_search(query, limit=50):
    results = []
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    
    try:
        headers = get_random_headers()
        headers['Referer'] = 'https://duckduckgo.com/'
        
        response = requests.get(url, headers=headers, timeout=15, proxies=PROXIES)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for result in soup.select('.result'):
            title_elem = result.select_one('.result__a')
            snippet_elem = result.select_one('.result__snippet')
            
            if title_elem:
                href = title_elem.get('href', '')
                
                if 'uddg=' in href:
                    actual_url = unquote(href.split('uddg=')[1].split('&')[0])
                else:
                    actual_url = href
                
                domain = urlparse(actual_url).netloc.replace('www.', '')
                
                if is_valid_domain(domain):
                    results.append({
                        'name': clean_company_name(title_elem.text),
                        'domain': domain,
                        'url': actual_url,
                        'description': snippet_elem.text if snippet_elem else '',
                        'source': 'duckduckgo'
                    })
                
                if len(results) >= limit:
                    break
                    
    except Exception as e:
        print(f"DuckDuckGo search error: {e}", file=sys.stderr)
    
    return results


def search_companies(keyword, region=None, limit=50):
    init_proxies()
    
    query = keyword
    if region:
        query = f"{region} {keyword}"
    
    all_results = []
    seen_domains = set()
    
    print(f"Searching: {query}", file=sys.stderr)
    
    for search_func in [baidu_search, bing_search, duckduckgo_search]:
        try:
            results = search_func(query, limit)
            print(f"  {search_func.__name__}: found {len(results)} valid results", file=sys.stderr)
            
            for r in results:
                domain = r['domain']
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    all_results.append(r)
                    
            if len(all_results) >= limit:
                break
                
        except Exception as e:
            print(f"Search error: {e}", file=sys.stderr)
            continue
    
    print(f"  Total results: {len(all_results)}", file=sys.stderr)
    return all_results[:limit]


def main():
    parser = argparse.ArgumentParser(description='Search for potential customer companies')
    parser.add_argument('keyword', help='Search keyword')
    parser.add_argument('--region', '-r', help='Region filter (e.g., 上海, 北京)')
    parser.add_argument('--limit', '-l', type=int, default=50, help='Maximum number of results')
    parser.add_argument('--output', '-o', help='Output file path (JSON)')
    parser.add_argument('--proxy', '-p', help='Proxy URL (e.g., http://127.0.0.1:7890)')
    
    args = parser.parse_args()
    
    if args.proxy:
        os.environ['HTTPS_PROXY'] = args.proxy
        os.environ['HTTP_PROXY'] = args.proxy
    
    results = search_companies(args.keyword, args.region, args.limit)
    
    output = {
        'query': args.keyword,
        'region': args.region,
        'total': len(results),
        'results': results
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
