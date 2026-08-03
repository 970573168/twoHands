# 设置表名变量
TABLE_NAME="YahooAuctionLinks-dev"

# 扫描所有记录并保存到文件
aws dynamodb scan --table-name $TABLE_NAME --output json > /tmp/items.json

# 提取所有主键并删除
aws dynamodb scan --table-name $TABLE_NAME \
  --projection-expression "crawl_id" \
  --output json | \
  jq -r '.Items[] | {crawl_id: .crawl_id.S} | 
    "{\"crawl_id\": {\"S\": \"" + .crawl_id + "\"}}"' | \
  while read -r key; do
    echo "Deleting: $key"
    aws dynamodb delete-item \
      --table-name $TABLE_NAME \
      --key "$key"
  done




aws dynamodb scan \
    --table-name "AiTokenUsage-dev" \
    --projection-expression "total_tokens" \
    --query "sum(Items[*].total_tokens.N.to_number(@))"


aws dynamodb scan \
  --table-name YahooAuctionActiveItems-dev \
  --projection-expression "modelStatus, pricingStatus" \
  --output json | jq -r '
    [.Items[] | {model: .modelStatus.S, pricing: .pricingStatus.S}] 
    | group_by(.model) 
    | map({status: .[0].model, count: length})'


 # 未扫描的 (last_scanned_date 为空或不是今天)
aws dynamodb scan \
  --table-name ProductCatalog-dev \
  --filter-expression "entity_type = :et AND attribute_not_exists(last_scanned_date)" \
  --expression-attribute-values '{":et":{"S":"PRODUCT"}}' \
  --select COUNT

# 今天已扫描的
TODAY=$(date -d "+9 hours" +%Y-%m-%d)
aws dynamodb scan \
  --table-name ProductCatalog-dev \
  --filter-expression "entity_type = :et AND last_scanned_date = :td" \
  --expression-attribute-values '{
    ":et":{"S":"PRODUCT"},
    ":td":{"S":"'$TODAY'"}
  }' \
  --select COUNT

# 按 last_analysis_status 分组统计
aws dynamodb scan \
  --table-name ProductCatalog-dev \
  --filter-expression "entity_type = :et" \
  --expression-attribute-values '{":et":{"S":"PRODUCT"}}' \
  --projection-expression "last_analysis_status,last_scanned_date" \
  --output json | jq -r '
    "Total: \(.Count)",
    (.Items | group_by(.last_analysis_status.S // "NULL") | 
     map("  \(.[0].last_analysis_status.S // "NULL"): \(length)") | .[])'



# 设置环境
ENV="dev"  # 或 test, prod

# 1. 启动目录发现定时器
aws events enable-rule \
  --name "ProductCatalog-Discovery-Schedule-${ENV}"

# 设置环境
ENV="dev"  # 或 test, prod

# 2. 启动最终复核定时器
aws events enable-rule \
  --name "YahooAuctionFinalCheck-Schedule-${ENV}"

# 设置环境
ENV="dev"  # 或 test, prod
# 3. 启动目录扫描定时器
aws events enable-rule \
  --name "CatalogScanner-Schedule-${ENV}"


查看定时器状态
ENV="dev"

echo "=== EventBridge 定时器状态 ==="
for rule in \
  "ProductCatalog-Discovery-Schedule-${ENV}" \
  "YahooAuctionFinalCheck-Schedule-${ENV}" \
  "CatalogScanner-Schedule-${ENV}"
do
  echo ""
  echo "Rule: $rule"
  aws events describe-rule --name "$rule" \
    --query "{State:State, Schedule:ScheduleExpression}" \
    --output table
done



# 设置环境
ENV="dev"  # 或 test, prod

# 一键启动全部
for rule in \
  "ProductCatalog-Discovery-Schedule-${ENV}" \
  "YahooAuctionFinalCheck-Schedule-${ENV}" \
  "CatalogScanner-Schedule-${ENV}"
do
  echo "Enabling: $rule"
  aws events enable-rule --name "$rule"
done



最近的token使用前100条

aws dynamodb scan \
    --table-name "AiTokenUsage-dev" \
    --projection-expression "occurred_at, task_type, model, total_tokens" \
    --output json | python3 -c "
import json, sys
from datetime import datetime, timezone, timedelta
jst = timezone(timedelta(hours=9))
items = json.load(sys.stdin)['Items']
for i in sorted(items, key=lambda x: x['occurred_at']['S'], reverse=True)[:50]:
    t = datetime.fromisoformat(i['occurred_at']['S'].replace('Z','+00:00')).astimezone(jst)
    print(f\"{t.strftime('%m-%d %H:%M')} | {i['task_type']['S']:20s} | {i['model']['S'][:25]:25s} | {i['total_tokens']['N']:>8s}\")
" 2>/dev/null







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




