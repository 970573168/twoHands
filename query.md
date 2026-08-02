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


###### 目录表

aws dynamodb scan \
    --table-name "ProductCatalog-dev" \
    --output json > product_catalog_all.json

echo "导出完成，$(cat product_catalog_all.json | jq '.Items | length') 条"

pip install openpyxl

python3 << 'EOF'
import json
from openpyxl import Workbook

with open('product_catalog_all.json') as f:
    data = json.load(f)

wb = Workbook()
ws = wb.active
ws.title = 'ProductCatalog'
headers = ['PK', 'SK', 'category', 'brand', 'model', 'entity_type', 'status', 
           'last_scanned_date', 'last_analysis_status', 'modified_at',
           'GSI1PK', 'GSI1SK', 'modified_index_pk']
ws.append(headers)

for item in data['Items']:
    row = [item.get(h, {}).get('S', item.get(h, {}).get('N', '')) for h in headers]
    ws.append(row)

ws.auto_filter.ref = ws.dimensions
wb.save('product_catalog.xlsx')
print(f'完成！{len(data["Items"])} 条 → product_catalog.xlsx')
EOF


product_catalog.xlsx










