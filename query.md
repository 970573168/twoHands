

数据库下载
pip install boto3 openpyxl

python3 << 'EOF'
import boto3
from datetime import datetime, timezone, timedelta
from openpyxl import Workbook

TABLES = [
    "AiTokenUsage-dev",
    "ProductCatalog-dev",
    "YahooAuctionActiveItems-dev",
    "YahooAuctionBuyCandidates-dev",
    "YahooAuctionItems-dev",
    "YahooAuctionLinks-dev"  # 新增
]

JST = timezone(timedelta(hours=9))

dynamodb = boto3.client("dynamodb")

def format_time(value):
    try:
        # 13位毫秒时间戳
        if value.isdigit() and len(value) == 13:
            return datetime.fromtimestamp(
                int(value) / 1000,
                JST
            ).strftime("%Y-%m-%d %H:%M:%S")

        # 10位秒时间戳
        if value.isdigit() and len(value) == 10:
            return datetime.fromtimestamp(
                int(value),
                JST
            ).strftime("%Y-%m-%d %H:%M:%S")

        # ISO 时间格式
        if "T" in value and ("Z" in value or "+" in value):
            dt = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
            return dt.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        pass

    return value

def convert_value(attr):
    if not attr:
        return ""

    if "S" in attr:
        return format_time(attr["S"])

    if "N" in attr:
        return format_time(attr["N"])

    if "BOOL" in attr:
        return str(attr["BOOL"])

    if "SS" in attr:
        return ",".join(attr["SS"])

    if "NS" in attr:
        return ",".join(attr["NS"])

    if "L" in attr:
        return str(attr["L"])

    if "M" in attr:
        return str(attr["M"])

    if "NULL" in attr:
        return ""

    return str(attr)

wb = Workbook()
wb.remove(wb.active)

for table_name in TABLES:
    print(f"\n开始导出 {table_name}")

    items = []
    scan_kwargs = {
        "TableName": table_name
    }

    try:
        while True:
            response = dynamodb.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            if "LastEvaluatedKey" not in response:
                break

            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        print(f"获取 {len(items)} 条记录")

        columns = set()

        for item in items:
            columns.update(item.keys())

        columns = sorted(list(columns))

        ws = wb.create_sheet(title=table_name[:31])

        ws.append(columns)

        for item in items:
            row = [
                convert_value(item.get(col))
                for col in columns
            ]
            ws.append(row)

        ws.auto_filter.ref = ws.dimensions

        print(f"{table_name} 导出完成")

    except Exception as e:
        print(f"导出 {table_name} 失败: {e}")
        # 创建一个空表标记失败
        ws = wb.create_sheet(title=table_name[:31])
        ws.append(["导出失败", str(e)])

output_file = "dynamodb_all_tables.xlsx"

wb.save(output_file)

print("\n全部完成！")
print(f"生成文件：{output_file}")
EOF


dynamodb_all_tables.xlsx









删除搜索记录
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

python3 -c "
import boto3

dynamodb = boto3.resource('dynamodb')

# 要清空的表列表
tables_to_clear = [
    'YahooAuctionLinks-dev',
    'YahooAuctionItems-dev',
    'YahooAuctionActiveItems-dev',
    'YahooAuctionBuyCandidates-dev',
    'ProductCatalog-dev',
    'AiTokenUsage-dev',
]

for table_name in tables_to_clear:
    try:
        table = dynamodb.Table(table_name)
        
        # 统计总数
        total = 0
        scan_kwargs = {}
        while True:
            response = table.scan(Select='COUNT', **scan_kwargs)
            total += response['Count']
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        print(f'\n📋 {table_name}: {total} 条记录')
        
    except Exception as e:
        print(f'\n⚠️ {table_name}: 不存在或无权限访问 ({e})')

print()
confirm = input('确认删除以上所有表的数据？(yes/no): ')
if confirm.lower() != 'yes':
    print('取消删除')
    exit()

print('\n开始删除...\n')

for table_name in tables_to_clear:
    try:
        table = dynamodb.Table(table_name)
        
        deleted = 0
        scan_kwargs = {}
        
        # 获取表的键名
        key_schema = table.key_schema
        key_names = [k['AttributeName'] for k in key_schema]
        
        with table.batch_writer() as batch:
            while True:
                response = table.scan(**scan_kwargs)
                items = response.get('Items', [])
                
                for item in items:
                    # 构建键字典
                    key = {k: item[k] for k in key_names}
                    batch.delete_item(Key=key)
                    deleted += 1
                
                if 'LastEvaluatedKey' not in response:
                    break
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        print(f'✅ {table_name}: 删除 {deleted} 条')
        
    except Exception as e:
        print(f'❌ {table_name}: 删除失败 ({e})')

print('\n清空完成！')
"

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


