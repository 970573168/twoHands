import json
import os
import re
import time
import hashlib
import boto3
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'YahooAuctionItems')
table = dynamodb.Table(table_name)

# Environment variables
BASE_URL = os.environ.get('BASE_URL', 'https://auctions.yahoo.co.jp/closedsearch/closedsearch')
USER_AGENT = os.environ.get('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))

# Default parameters from environment
DEFAULT_PARAMS = {
    'b': os.environ.get('PAGE', '1'),
    'n': os.environ.get('ITEMS_PER_PAGE', '50'),
    'select': os.environ.get('SELECT', '6'),
    'mode': os.environ.get('MODE', '3'),
    'dest_pref_code': os.environ.get('DEST_PREF_CODE', '23')
}


def log(level, message, **fields):
    """结构化日志输出"""
    entry = {
        "level": level,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **fields
    }
    print(json.dumps(entry, ensure_ascii=False, default=str))


def normalize_text(text):
    """规范化文本"""
    if not text:
        return ""
    text = str(text).strip()
    # 全角转半角
    text = text.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '０１２３４５６７８９（）（）．，',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789()().,'
    ))
    return re.sub(r'\s+', ' ', text).strip()


def generate_item_id(auction_id):
    """生成稳定的物品ID"""
    if not auction_id:
        return None
    return hashlib.sha256(auction_id.encode('utf-8')).hexdigest()[:32]


def parse_price(price_text):
    """从文本中解析价格"""
    if not price_text:
        return None
    # 移除逗号和货币符号
    price_match = re.search(r'([\d,]+)', str(price_text).replace(',', ''))
    if price_match:
        try:
            return int(price_match.group(1))
        except ValueError:
            return None
    return None


def parse_end_time(time_text):
    """解析拍卖结束时间"""
    if not time_text:
        return None
    
    # 格式: "7/15 23:03終了"
    time_match = re.search(r'(\d+)/(\d+)\s+(\d+):(\d+)終了', time_text)
    if time_match:
        month, day, hour, minute = time_match.groups()
        year = datetime.now().year
        if int(month) > datetime.now().month:
            year -= 1
        try:
            dt = datetime(year, int(month), int(day), int(hour), int(minute))
            return dt.isoformat()
        except ValueError:
            return None
    
    # 尝试ISO格式
    try:
        dt = datetime.fromisoformat(time_text.replace('+09:00', ''))
        return dt.isoformat()
    except:
        return None


def fetch_page(url, params=None, retry_count=0):
    """获取网页内容（带重试）"""
    try:
        if params:
            encoded_params = urlencode(params, quote_via=quote, encoding='utf-8', safe='')
            full_url = f"{url}?{encoded_params}"
        else:
            full_url = url
        
        log('INFO', 'Fetching URL', url=full_url, retry=retry_count)
        
        request = Request(
            full_url,
            headers={
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        )
        
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            content = response.read().decode('utf-8', errors='ignore')
            return content
            
    except HTTPError as e:
        log('WARN', 'HTTP error', status_code=e.code, retry=retry_count)
        if retry_count < MAX_RETRIES and e.code in (408, 429, 500, 502, 503, 504):
            time.sleep(2 ** retry_count)
            return fetch_page(url, params, retry_count + 1)
        raise
    
    except URLError as e:
        log('WARN', 'URL error', error=str(e), retry=retry_count)
        if retry_count < MAX_RETRIES:
            time.sleep(2 ** retry_count)
            return fetch_page(url, params, retry_count + 1)
        raise
    
    except Exception as e:
        log('ERROR', 'Fetch error', error=str(e), retry=retry_count)
        if retry_count < MAX_RETRIES:
            time.sleep(2 ** retry_count)
            return fetch_page(url, params, retry_count + 1)
        raise


def parse_auction_item(item_element):
    """解析单个拍卖物品"""
    try:
        # 查找主链接
        link_element = item_element.find('a', href=re.compile(r'/jp/auction/'))
        if not link_element:
            link_element = item_element.find('a', href=lambda x: x and 'auction' in x)
            if not link_element:
                return None
        
        href = link_element.get('href', '')
        auction_id = href.split('/')[-1] if href else None
        if not auction_id:
            return None
        
        # 提取标题
        title = link_element.get('title', '')
        if not title:
            title_element = item_element.find('p')
            if title_element:
                title_link = title_element.find('a')
                if title_link:
                    title = title_link.get('title', '') or title_link.text.strip()
                else:
                    title = title_element.text.strip()
        
        # 提取价格
        price = None
        price_element = item_element.find('span', string=re.compile(r'[\d,]+円'))
        if price_element:
            price = parse_price(price_element.text)
        if not price:
            price_elements = item_element.find_all('span', class_=re.compile(r'fRZzUL|fWnOMU'))
            for elem in price_elements:
                if '円' in elem.text:
                    price = parse_price(elem.text)
                    if price:
                        break
        
        # 提取出价次数
        bid_count = 0
        bid_element = item_element.find('div', class_=re.compile(r'bAsSfK'))
        if bid_element:
            bid_text = bid_element.text.strip()
            bid_match = re.search(r'(\d+)', bid_text)
            if bid_match:
                bid_count = int(bid_match.group(1))
        
        # 提取结束时间
        end_time = None
        time_element = item_element.find('span', string=re.compile(r'\d+/\d+\s+\d+:\d+終了'))
        if time_element:
            end_time = parse_end_time(time_element.text)
        
        # 提取卖家信息
        seller_name = ''
        seller_element = item_element.find('div', class_=re.compile(r'iiBMKd'))
        if seller_element:
            seller_link = seller_element.find('a')
            if seller_link:
                seller_name = seller_link.text.strip()
        
        # 提取地点
        location = ''
        location_element = item_element.find('p', class_=re.compile(r'bRtBJF'))
        if location_element:
            location_text = location_element.text.strip()
            location_match = re.search(r'(.+)から発送', location_text)
            if location_match:
                location = location_match.group(1).strip()
        
        # 提取图片URL
        image_url = ''
        img_element = item_element.find('img')
        if img_element:
            image_url = img_element.get('src', '') or img_element.get('data-src', '')
        
        # 构建数据
        item_data = {
            'auction_id': auction_id,
            'title': normalize_text(title),
            'price': price,
            'bid_count': bid_count,
            'end_time': end_time,
            'seller_name': normalize_text(seller_name),
            'location': normalize_text(location),
            'image_url': image_url,
            'url': f"https://auctions.yahoo.co.jp{href}" if href else None,
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'ttl': int(time.time()) + 31536000  # 1年TTL
        }
        
        item_id = generate_item_id(auction_id)
        if item_id:
            item_data['item_id'] = item_id
        
        return item_data
        
    except Exception as e:
        log('ERROR', 'Parse error', error=str(e))
        return None


def parse_search_results(html_content):
    """解析搜索结果页面"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找物品容器
        items_container = soup.find('ul', class_=re.compile(r'diTCfG'))
        if not items_container:
            items_container = soup.find('div', id='closedSearchItems')
        
        if not items_container:
            log('WARN', 'No items container found')
            return []
        
        # 查找所有物品元素
        item_elements = items_container.find_all('li', class_=re.compile(r'iDpbCh'))
        if not item_elements:
            item_divs = items_container.find_all('div', class_=re.compile(r'esyVw'))
            item_elements = []
            for div in item_divs:
                parent_li = div.find_parent('li')
                if parent_li:
                    item_elements.append(parent_li)
        
        log('INFO', 'Found items', count=len(item_elements))
        
        # 解析每个物品
        items = []
        for elem in item_elements:
            item_data = parse_auction_item(elem)
            if item_data:
                items.append(item_data)
        
        return items
        
    except Exception as e:
        log('ERROR', 'Parse error', error=str(e))
        return []


def store_items(items, keyword):
    """批量存储物品到DynamoDB"""
    stored_count = 0
    failed_count = 0
    
    for item in items:
        try:
            # 添加关键词
            item['keyword'] = keyword
            
            # 检查是否已存在
            existing = table.get_item(Key={'auction_id': item['auction_id']})
            if 'Item' in existing:
                log('INFO', 'Item already exists', auction_id=item['auction_id'])
                continue
            
            # 存储
            table.put_item(Item=item)
            stored_count += 1
            log('INFO', 'Stored item', auction_id=item['auction_id'], price=item['price'])
        except Exception as e:
            log('ERROR', 'Failed to store item', auction_id=item.get('auction_id'), error=str(e))
            failed_count += 1
    
    return stored_count, failed_count


def lambda_handler(event, context):
    """
    Lambda 入口函数
    
    Event 参数:
    - keyword: 搜索关键词 (默认从环境变量读取)
    - params: 可选参数覆盖默认值
    - store_to_db: 是否存储到数据库 (默认 true)
    - max_pages: 最大爬取页数 (默认 1)
    """
    try:
        # 获取参数
        keyword = event.get('keyword', os.environ.get('SEARCH_KEYWORD', 'スズキバイオリン540'))
        store_to_db = event.get('store_to_db', True)
        max_pages = int(event.get('max_pages', 1))
        
        # 构建参数
        params = DEFAULT_PARAMS.copy()
        params['p'] = keyword
        
        if 'params' in event and isinstance(event['params'], dict):
            params.update(event['params'])
        
        log('INFO', 'Starting scraper', 
            keyword=keyword, 
            params=params,
            max_pages=max_pages)
        
        all_items = []
        current_page = int(params.get('b', 1))
        
        for page in range(max_pages):
            params['b'] = str(current_page + page)
            
            # 获取页面
            html_content = fetch_page(BASE_URL, params)
            
            # 解析物品
            items = parse_search_results(html_content)
            
            if not items:
                log('INFO', 'No items found on page', page=current_page + page)
                break
            
            all_items.extend(items)
            log('INFO', 'Page processed', page=current_page + page, items=len(items))
            
            # 如果物品少于每页数量，说明是最后一页
            if len(items) < int(params.get('n', 50)):
                break
            
            # 避免请求过快
            time.sleep(1)
        
        # 存储到数据库
        stored_count = 0
        failed_count = 0
        
        if store_to_db and all_items:
            stored_count, failed_count = store_items(all_items, keyword)
        
        # 构建响应
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Scraping completed successfully',
                'keyword': keyword,
                'total_items_found': len(all_items),
                'items_stored': stored_count,
                'items_failed': failed_count,
                'pages_processed': min(max_pages, (len(all_items) + int(params['n']) - 1) // int(params['n'])),
                'params': params,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        log('ERROR', 'Handler error', error=str(e), error_type=type(e).__name__)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, ensure_ascii=False)
        }
