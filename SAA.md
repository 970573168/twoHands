[2026/05]
All AWS Certified Solutions Architect - Associate SAA-C03 Questions
Question #1
Topic 1
⼀家公司收集多个⼤洲城市的温度、湿度和⽓压数据。该公司每天从每个站点收集的平均数据量为 500 GB。每
个站点都拥有⾼速互联⽹连接。
该公司希望尽快将所有这些全球站点的数据聚合到⼀个 Amazon S3 存储桶中。该解决⽅案必须最⼤限度地降低
操作复杂性。
哪个解决⽅案满⾜这些要求？
A. 在⽬标 S3 存储桶上启⽤ S3 传输加速。使⽤分段上传将⽹站数据直接上传到⽬标 S3 存储桶。
B. 将每个站点的数据上传到距离最近的区域中的 S3 存储桶。使⽤ S3 跨区域复制将对象复制到⽬标 S3 存储
桶。然后从源 S3 存储桶中删除数据。
C. 每⽇安排 AWS Snowball Edge Storage Optimized 设备作业，将数据从各个站点传输到最近的区域。使
⽤ S3 跨区域复制将对象复制到⽬标 S3 存储桶。
D. 将每个站点的数据上传到距离最近的区域中的 Amazon EC2 实例。将数据存储在 Amazon Elastic Block
Store (Amazon EBS) 卷中。定期创建 EBS 快照并将其复制到包含⽬标 S3 存储桶的区域。在该区域中恢复
EBS 卷。
Question #2
Topic 1
⼀家公司需要分析其专有应⽤程序的⽇志⽂件。这些⽇志以 JSON 格式存储在 Amazon S3 存储桶中。查询将很
简单，并且按需运⾏。解决⽅案架构师需要在对现有架构进⾏最⼩改动的情况下执⾏分析。
解决⽅案架构师应该如何做才能以最⼩的运维开销满⾜这些要求？
A. 使⽤ Amazon Redshift 将所有内容加载到⼀个位置，并根据需要运⾏ SQL 查询。
B. 使⽤ Amazon CloudWatch Logs 存储⽇志。根据需要从 Amazon CloudWatch 控制台运⾏ SQL 查询。
C. 根据需要直接使⽤ Amazon Athena 和 Amazon S3 运⾏查询。
D. 使⽤ AWS Glue 对⽇志进⾏编⽬。根据需要，在 Amazon EMR 上使⽤临时 Apache Spark 集群运⾏ SQL
查询。
https://examlearn.online
[2026/05]
Question #3
Topic 1
⼀家公司使⽤ AWS Organizations 管理不同部⻔的多个 AWS 账户。管理账户中包含⼀个 Amazon S3 存储桶，
⽤于存放项⽬报告。该公司希望限制对该 S3 存储桶的访问权限，仅允许 AWS Organizations 组织内账户的⽤户
访问。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将 aws PrincipalOrgID 全局条件键（引⽤组织 ID）添加到 S3 存储桶策略中。
B. 为每个部⻔创建⼀个组织单元 (OU)。将 aws:PrincipalOrgPaths 全局条件键添加到 S3 存储桶策略中。
C. 使⽤ AWS CloudTrail 监控 CreateAccount、InviteAccountToOrganization、LeaveOrganization 和
RemoveAccountFromOrganization 事件。并据此更新 S3 存储桶策略。
D. 为每个需要访问 S3 存储桶的⽤户添加标签。将 aws:PrincipalTag 全局条件键添加到 S3 存储桶策略中。
Question #4
Topic 1
⼀个应⽤程序运⾏在 VPC 中的 Amazon EC2 实例上。该应⽤程序处理存储在 Amazon S3 存储桶中的⽇志。
EC2 实例需要在⽆法连接到互联⽹的情况下访问 S3 存储桶。
哪种解决⽅案可以提供到 Amazon S3 的私有⽹络连接？
A. 创建到 S3 存储桶的⽹关 VPC 端点。
B. 将⽇志流式传输到 Amazon CloudWatch Logs。将⽇志导出到 S3 存储桶。
C. 在 Amazon EC2 上创建实例配置⽂件，以允许访问 S3。
D. 创建⼀个 Amazon API Gateway API，并创建⼀个私有链接来访问 S3 端点。
https://examlearn.online
[2026/05]
Question #5
Topic 1
⼀家公司在 AWS 上托管了⼀个 Web 应⽤程序，使⽤单个 Amazon EC2 实例将⽤户上传的⽂档存储在 Amazon
EBS 卷中。为了提⾼可扩展性和可⽤性，该公司复制了该架构，并在另⼀个可⽤区创建了第⼆个 EC2 实例和
EBS 卷，并将两者都置于应⽤程序负载均衡器之后。完成此更改后，⽤户反映每次刷新⽹站时，他们只能看到部
分⽂档，⽽⽆法同时看到所有⽂档。
解决⽅案架构师应该提出什么⽅案来确保⽤户能够同时看到所有⽂档？
A. 复制数据，确保两个 EBS 卷都包含所有⽂档。
B. 配置应⽤程序负载均衡器，将⽤户定向到包含⽂档的服务器。
C. 将两个 EBS 卷中的数据复制到 Amazon EFS。修改应⽤程序，使其将新⽂档保存到 Amazon EFS。
D. 配置应⽤程序负载均衡器，将请求发送到两个服务器。从正确的服务器返回每个⽂档。
Question #6
本地的 S3 存储桶。
Topic 1
⼀家公司使⽤ NFS 将⼤型视频⽂件存储在本地⽹络附加存储 (NAS) 中。每个视频⽂件的⼤⼩从 1 MB 到 500 GB
不等。总存储空间为 70 TB，且不再增⻓。该公司决定将视频⽂件迁移到 Amazon S3。该公司必须尽快完成迁
移，同时尽可能减少⽹络带宽的使⽤。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个 S3 存储桶。创建⼀个具有写⼊该 S3 存储桶权限的 IAM ⻆⾊。使⽤ AWS CLI 将所有⽂件复制到
B. 创建⼀个 AWS Snowball Edge 作业。接收⼀台本地的 Snowball Edge 设备。使⽤ Snowball Edge 客户端
将数据传输到该设备。返回该设备，以便 AWS 可以将数据导⼊ Amazon S3。
C. 在本地部署 S3 ⽂件⽹关。创建公共服务端点以连接到 S3 ⽂件⽹关。创建 S3 存储桶。在 S3 ⽂件⽹关上
创建⼀个新的 NFS ⽂件共享。将新的⽂件共享指向 S3 存储桶。将数据从现有的 NFS ⽂件共享传输到 S3 ⽂
件⽹关。
D. 在本地⽹络和 AWS 之间建⽴ AWS Direct Connect 连接。在本地部署 S3 ⽂件⽹关。创建公共虚拟接⼝
(VIF) 以连接到 S3 ⽂件⽹关。创建 S3 存储桶。在 S3 ⽂件⽹关上创建⼀个新的 NFS ⽂件共享。将新的⽂件
共享指向 S3 存储桶。将数据从现有的 NFS ⽂件共享传输到 S3 ⽂件⽹关。
https://examlearn.online
[2026/05]
Question #7
Topic 1
⼀家公司有⼀个应⽤程序⽤于接收传⼊的消息。随后，数⼗个其他应⽤程序和微服务会快速消费这些消息。消息
数量波动很⼤，有时会突然飙升⾄每秒 10 万条。该公司希望解耦解决⽅案并提⾼可扩展性。
哪种解决⽅案能够满⾜这些要求？
A. 将消息持久化到 Amazon Kinesis Data Analytics。配置客户端应⽤程序以读取和处理消息。
B. 将数据导⼊应⽤程序部署到 Amazon EC2 实例上的⾃动扩展组中，以便根据 CPU 指标扩展 EC2 实例的数
量。
C. 将消息写⼊ Amazon Kinesis Data Streams，使⽤单个分⽚。使⽤ AWS Lambda 函数预处理消息并将其
存储在 Amazon DynamoDB 中。配置消费者应⽤程序从 DynamoDB 读取消息以进⾏处理。
D. 将消息发布到具有多个 Amazon Simple Queue Service (Amazon SOS) 订阅的 Amazon Simple
Notification Service (Amazon SNS) 主题。配置消费者应⽤程序以处理来⾃队列的消息。
Question #8
Topic 1
⼀家公司正在将⼀个分布式应⽤程序迁移到 AWS。该应⽤程序服务于各种不同的⼯作负载。原有平台由⼀个主服
务器组成，该服务器协调跨多个计算节点的作业。该公司希望通过⼀个能够最⼤限度提⾼弹性和可扩展性的解决
⽅案来升级该应⽤程序。
解决⽅案架构师应该如何设计架构以满⾜这些要求？
A. 将 Amazon Simple Queue Service (Amazon SQS) 队列配置为作业的⽬标队列。使⽤由 Auto Scaling 组
管理的 Amazon EC2 实例部署计算节点。配置 EC2 Auto Scaling 以使⽤计划扩展。
B. 将 Amazon Simple Queue Service (Amazon SQS) 队列配置为作业的⽬标队列。使⽤由 Auto Scaling 组
管理的 Amazon EC2 实例部署计算节点。根据队列⼤⼩配置 EC2 Auto Scaling。
C. 使⽤由 Auto Scaling 组管理的 Amazon EC2 实例部署主服务器和计算节点。将 AWS CloudTrail 配置为作
业⽬标。根据主服务器的负载配置 EC2 Auto Scaling。
D. 使⽤由 Auto Scaling 组管理的 Amazon EC2 实例部署主服务器和计算节点。将 Amazon EventBridge
（Amazon CloudWatch Events）配置为作业⽬标。根据计算节点的负载配置 EC2 Auto Scaling。
https://examlearn.online
[2026/05]
Question #9
Topic 1
⼀家公司在其数据中⼼运⾏着⼀台 SMB ⽂件服务器。该⽂件服务器存储着⼤量⽂件，这些⽂件在创建后的最初
⼏天内会被频繁访问。7 天后，这些⽂件的访问量骤减。
数据总量不断增⻓，并已接近公司的总存储容量。解决⽅案架构师必须在不影响对最近访问⽂件的低延迟访问的
前提下，增加公司的可⽤存储空间。此外，解决⽅案架构师还必须提供⽂件⽣命周期管理，以避免未来出现存储
问题。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS DataSync 将 SMB ⽂件服务器上超过 7 天的数据复制到 AWS。
B. 创建 Amazon S3 ⽂件⽹关以扩展公司存储空间。创建 S3 ⽣命周期策略，以便在 7 天后将数据迁移到 S3
Glacier 深度归档。
C. 创建⼀个 Amazon FSx for Windows ⽂件服务器⽂件系统，以扩展公司的存储空间。
D. 在每个⽤户的计算机上安装⼀个实⽤程序来访问 Amazon S3。创建⼀个 S3 ⽣命周期策略，以便在 7 天后
将数据过渡到 S3 Glacier 灵活检索。
Question #10
Topic 1
⼀家公司正在AWS上构建⼀个电⼦商务Web应⽤程序。该应⽤程序会将新订单信息发送到Amazon API Gateway
REST API进⾏处理。该公司希望确保订单按照接收顺序进⾏处理。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ API Gateway 集成，在应⽤程序收到订单时向 Amazon Simple Notification Service (Amazon SNS)
主题发布消息。订阅 AWS Lambda 函数以执⾏处理。
B. 使⽤ API ⽹关集成，在应⽤程序收到订单时向 Amazon Simple Queue Service (Amazon SQS) FIFO 队列
发送消息。配置 SQS FIFO 队列以调⽤ AWS Lambda 函数进⾏处理。
C. 使⽤ API ⽹关授权器阻⽌应⽤程序处理订单时的任何请求。
D. 使⽤ API ⽹关集成，在应⽤程序收到订单时向 Amazon Simple Queue Service (Amazon SQS) 标准队列
发送消息。配置 SQS 标准队列以调⽤ AWS Lambda 函数进⾏处理。
https://examlearn.online
[2026/05]
Question #11
Topic 1
⼀家公司有⼀个运⾏在 Amazon EC2 实例上的应⽤程序，该应⽤程序使⽤ Amazon Aurora 数据库。EC2 实例通
过存储在本地⽂件中的⽤户名和密码连接到数据库。该公司希望最⼤限度地减少凭证管理的运维开销。
解决⽅案架构师应该如何实现这⼀⽬标？
A. 使⽤ AWS Secrets Manager。启⽤⾃动轮换。
B. 使⽤ AWS Systems Manager Parameter Store。启⽤⾃动轮换。
C. 创建⼀个 Amazon S3 存储桶，⽤于存储使⽤ AWS Key Management Service (AWS KMS) 加密密钥加密
的对象。将凭证⽂件迁移到 S3 存储桶。将应⽤程序指向该 S3 存储桶。
D. 为每个 EC2 实例创建⼀个加密的 Amazon Elastic Block Store (Amazon EBS) 卷。将新的 EBS 卷附加到
每个 EC2 实例。将凭证⽂件迁移到新的 EBS 卷。将应⽤程序指向新的 EBS 卷。
Question #12
CloudFront 分发。
Web 应⽤程序的端点。
Topic 1
⼀家全球性公司将其 Web 应⽤程序托管在 Amazon EC2 实例上，并部署在应⽤程序负载均衡器 (ALB) 之后。该
Web 应⽤程序包含静态数据和动态数据。公司将静态数据存储在 Amazon S3 存储桶中。公司希望提升静态数据
和动态数据的性能并降低延迟。公司使⽤的是在 Amazon Route 53 注册的⾃有域名。
解决⽅案架构师应该如何满⾜这些要求？
A. 创建⼀个以 S3 存储桶和 ALB 为源的 Amazon CloudFront 分发。配置 Route 53 将流量路由到
B. 创建⼀个以 ALB 为源的 Amazon CloudFront 分发。创建⼀个以 S3 存储桶为终端节点的 AWS Global
Accelerator 标准加速器。配置 Route 53 将流量路由到 CloudFront 分发。
C. 创建⼀个以 S3 存储桶为源的 Amazon CloudFront 分发。创建⼀个以 ALB 和 CloudFront 分发为端点的
AWS Global Accelerator 标准加速器。创建⼀个指向加速器 DNS 名称的⾃定义域名。将该⾃定义域名⽤作
D. 创建⼀个以应⽤负载均衡器 (ALB) 为源的 Amazon CloudFront 分发。创建⼀个以 S3 存储桶为终端节点
的 AWS Global Accelerator 标准加速器。创建两个域名。将⼀个域名指向 CloudFront 的 DNS 名称以⽤于
动态内容。将另⼀个域名指向加速器的 DNS 名称以⽤于静态内容。将这两个域名⽤作 Web 应⽤程序的终端
节点。
https://examlearn.online
[2026/05]
Question #13
Topic 1
⼀家公司每⽉对其 AWS 基础设施进⾏维护。在这些维护活动期间，该公司需要轮换其 Amazon RDS for MySQL
数据库在多个 AWS 区域中的凭证。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将凭证作为密钥存储在 AWS Secrets Manager 中。对所需区域启⽤多区域密钥复制。配置 Secrets
Manager 按计划轮换密钥。
B. 通过创建安全字符串参数，将凭证作为密钥存储在 AWS Systems Manager 中。对所需区域启⽤多区域密
钥复制。配置 Systems Manager 按计划轮换密钥。
C. 将凭证存储在启⽤了服务器端加密 (SSE) 的 Amazon S3 存储桶中。使⽤ Amazon EventBridge
（Amazon CloudWatch Events）调⽤ AWS Lambda 函数来轮换凭证。
D. 使⽤ AWS Key Management Service (AWS KMS) 多区域客户托管密钥将凭证加密为密钥。将密钥存储在
Amazon DynamoDB 全局表中。使⽤ AWS Lambda 函数从 DynamoDB 中检索密钥。使⽤ RDS API 轮换密
钥。
Question #14
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏电⼦商务应⽤程序，这些实例位于应⽤程序负载均衡器 (ALB) 之后。这些
实例运⾏在跨多个可⽤区的 Amazon EC2 ⾃动扩展组中。⾃动扩展组根据 CPU 利⽤率指标进⾏扩展。该电⼦商
务应⽤程序将交易数据存储在托管于⼤型 EC2 实例上的 MySQL 8.0 数据库中。
随着应⽤程序负载的增加，数据库性能迅速下降。该应⽤程序处理的读取请求多于写⼊事务。该公司希望找到⼀
种解决⽅案，能够⾃动扩展数据库以满⾜不可预测的读取⼯作负载需求，同时保持⾼可⽤性。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon Redshift 的单个节点来实现领导者和计算功能。
B. 使⽤ Amazon RDS 进⾏单可⽤区部署 配置 Amazon RDS 以在不同的可⽤区中添加读取器实例。
C. 使⽤多可⽤区部署的 Amazon Aurora。配置 Aurora ⾃动扩展和 Aurora 副本。
D. 将 Amazon ElastiCache ⽤于 Memcached，并搭配 EC2 Spot 实例。
https://examlearn.online
[2026/05]
Question #15
Topic 1
⼀家公司最近迁移到了 AWS，并希望实施⼀个解决⽅案来保护进出⽣产 VPC 的流量。该公司在其本地数据中⼼
部署了⼀台检查服务器，该服务器执⾏流量检查和流量过滤等特定操作。该公司希望在 AWS 云中实现相同的功
能。
哪种解决⽅案能够满⾜这些要求？
A. 在⽣产 VPC 中使⽤ Amazon GuardDuty 进⾏流量检查和流量过滤。
B. 使⽤流量镜像将⽣产 VPC 中的流量镜像到⽣产环境，以便进⾏流量检查和过滤。
C. 使⽤ AWS ⽹络防⽕墙为⽣产 VPC 创建所需的流量检查和流量过滤规则。
D. 使⽤ AWS 防⽕墙管理器为⽣产 VPC 创建所需的流量检查和流量过滤规则。
Question #16
板共享给相应的 IAM ⻆⾊。
Topic 1
⼀家公司在 AWS 上托管了⼀个数据湖。该数据湖包含存储在 Amazon S3 和 Amazon RDS（PostgreSQL 数据
库）中的数据。该公司需要⼀个报表解决⽅案，该⽅案能够提供数据可视化功能，并涵盖数据湖中的所有数据
源。只有公司管理团队才能完全访问所有可视化内容，其他员⼯只能拥有有限的访问权限。
哪种解决⽅案能够满⾜这些要求？
A. 在 Amazon QuickSight 中创建分析。连接所有数据源并创建新数据集。发布仪表板以可视化数据。将仪表
B. 在 Amazon QuickSight 中创建分析。连接所有数据源并创建新数据集。发布仪表板以可视化数据。与相应
的⽤户和组共享仪表板。
C. 为 Amazon S3 中的数据创建 AWS Glue 表和爬⽹程序。创建 AWS Glue 提取、转换和加载 (ETL) 作业以
⽣成报告。将报告发布到 Amazon S3。使⽤ S3 存储桶策略限制对报告的访问。
D. 为 Amazon S3 中的数据创建 AWS Glue 表和爬⽹程序。使⽤ Amazon Athena 联合查询访问 Amazon
RDS for PostgreSQL 中的数据。使⽤ Amazon Athena ⽣成报告。将报告发布到 Amazon S3。使⽤ S3 存储
桶策略限制对报告的访问。
https://examlearn.online
[2026/05]
Question #17
Topic 1
⼀家公司正在实施⼀个新的业务应⽤程序。该应⽤程序运⾏在两个 Amazon EC2 实例上，并使⽤ Amazon S3 存
储桶进⾏⽂档存储。解决⽅案架构师需要确保 EC2 实例可以访问 S3 存储桶。
为了满⾜这⼀要求，解决⽅案架构师应该怎么做？
A. 创建⼀个授予对 S3 存储桶访问权限的 IAM ⻆⾊。将该⻆⾊附加到 EC2 实例。
B. 创建授予对 S3 存储桶访问权限的 IAM 策略。将该策略附加到 EC2 实例。
C. 创建⼀个 IAM 组，授予其对 S3 存储桶的访问权限。将该组附加到 EC2 实例。
D. 创建⼀个 IAM ⽤户，授予其访问 S3 存储桶的权限。将该⽤户帐户附加到 EC2 实例。
Question #18
存储桶时向 SQS 队列发送通知。
Topic 1
⼀个应⽤开发团队正在设计⼀个微服务，⽤于将⼤图像转换为较⼩的压缩图像。当⽤户通过 Web 界⾯上传图像
时，该微服务应将图像存储在 Amazon S3 存储桶中，使⽤ AWS Lambda 函数处理并压缩图像，然后将压缩后的
图像存储到另⼀个 S3 存储桶中。
解决⽅案架构师需要设计⼀个使⽤持久化、⽆状态组件⾃动处理图像的解决⽅案。
以下哪两项操作组合能够满⾜这些要求？
A. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。配置 S3 存储桶，使其在图像上传到 S3
B. 配置 Lambda 函数，使其使⽤ Amazon Simple Queue Service (Amazon SQS) 队列作为调⽤源。当 SQS
消息处理成功后，从队列中删除该消息。
C. 配置 Lambda 函数以监控 S3 存储桶中的新上传⽂件。当检测到上传的图像时，将⽂件名写⼊内存中的⼀
个⽂本⽂件，并使⽤该⽂本⽂件来跟踪已处理的图像。
D. 启动⼀个 Amazon EC2 实例来监控 Amazon Simple Queue Service (Amazon SQS) 队列。当队列中添加
项⽬时，将⽂件名记录到 EC2 实例上的⼀个⽂本⽂件中，并调⽤ Lambda 函数。
E. 配置 Amazon EventBridge（Amazon CloudWatch Events）事件以监控 S3 存储桶。当图像上传时，向
Amazon Appenable Notification Service（Amazon SNS）主题发送警报，并附上应⽤程序所有者的电⼦邮
件地址以便进⼀步处理。
https://examlearn.online
[2026/05]
Question #19
Topic 1
⼀家公司在 AWS 上部署了⼀个三层 Web 应⽤程序。Web 服务器部署在 VPC 的公有⼦⽹中，应⽤服务器和数据
库服务器部署在同⼀ VPC 的私有⼦⽹中。该公司在检查 VPC 中部署了⼀个来⾃ AWS Marketplace 的第三⽅虚
拟防⽕墙设备。该设备配置了⼀个可以接收 IP 数据包的 IP 接⼝。解决
⽅案架构师需要将 Web 应⽤程序与该设备集成，以便在流量到达 Web 服务器之前检查所有发往应⽤程序的流
量。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 在应⽤程序的 VPC 的公共⼦⽹中创建⼀个⽹络负载均衡器，将流量路由到设备进⾏数据包检查。
B. 在应⽤程序的 VPC 的公共⼦⽹中创建应⽤程序负载均衡器，将流量路由到设备进⾏数据包检查。
C. 在检查 VP 中部署传输⽹关，配置路由表，将传⼊的数据包路由到传输⽹关。
D. 在检测 VPC 中部署⽹关负载均衡器。创建⽹关负载均衡器端点以接收传⼊数据包并将数据包转发到设备。
Question #20
Topic 1
⼀家公司希望提升将⼤量⽣产数据克隆到同⼀ AWS 区域内测试环境的能⼒。数据存储在 Amazon EC2 实例的
Amazon Elastic Block Store (Amazon EBS) 卷上。对克隆数据的修改不得影响⽣产环境。访问这些数据的软件
需要始终保持⾼ I/O 性能。
解决⽅案架构师需要尽可能缩短将⽣产数据克隆到测试环境所需的时间。
哪种解决⽅案能够满⾜这些要求？
A. 对⽣产环境的 EBS 卷进⾏ EBS 快照。将快照恢复到测试环境中的 EC2 实例存储卷上。
B. 配置⽣产环境 EBS 卷以使⽤ EBS 多实例附加功能。对⽣产环境 EBS 卷进⾏ EBS 快照。将⽣产环境 EBS
卷附加到测试环境中的 EC2 实例。
C. 对⽣产环境的 EBS 卷进⾏ EBS 快照。创建并初始化新的 EBS 卷。在从⽣产环境的 EBS 快照恢复卷之前，
将新的 EBS 卷附加到测试环境中的 EC2 实例。
D. 对⽣产环境的 EBS 卷进⾏ EBS 快照。在 EBS 快照上启⽤ EBS 快速快照恢复功能。将快照恢复到新的
EBS 卷。将新的 EBS 卷附加到测试环境中的 EC2 实例。
https://examlearn.online
[2026/05]
Question #21
Topic 1
⼀家电商公司想在AWS上推出⼀个每⽇⼀单的特价商品⽹站。每天只推出⼀款商品，限时24⼩时。该公司希望在
⾼峰时段能够以毫秒级的延迟处理每⼩时数百万次的请求。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ Amazon S3 将整个⽹站托管在不同的 S3 存储桶中。添加 Amazon CloudFront 分发。将 S3 存储桶
设置为分发的源。将订单数据存储在 Amazon S3 中。
B. 将完整的⽹站部署在跨多个可⽤区运⾏于⾃动扩展组的 Amazon EC2 实例上。添加⼀个应⽤程序负载均衡
器 (ALB) 来分配⽹站流量。再添加⼀个 ALB ⽤于后端 API。将数据存储在 Amazon RDS for MySQL 中。
C. 将整个应⽤程序迁移到容器中运⾏。将容器托管在 Amazon Elastic Kubernetes Service (Amazon EKS)
上。使⽤ Kubernetes 集群⾃动扩缩器来增加或减少 Pod 数量，以应对突发流量。将数据存储在 Amazon
RDS for MySQL 中。
D. 使⽤ Amazon S3 存储桶托管⽹站的静态内容。部署 Amazon CloudFront 分发。将 S3 存储桶设置为源。
Question #22
A. S3 标准
B. S3 智能分层
使⽤ Amazon API Gateway 和 AWS Lambda 函数实现后端 API。将数据存储在 Amazon DynamoDB 中。
Topic 1
⼀位解决⽅案架构师正在使⽤ Amazon S3 设计⼀款新型数字媒体应⽤程序的存储架构。媒体⽂件必须能够应对
可⽤区丢失的情况。有些⽂件访问频繁，⽽另⼀些⽂件访问频率低且访问模式不可预测。解决⽅案架构师必须尽
可能降低存储和检索媒体⽂件的成本。
哪种存储⽅案能够满⾜这些要求？
C. S3 标准-不频繁访问 (S3 标准-IA)
D. S3 单区-不频繁访问 (S3 单区-IA)
https://examlearn.online
[2026/05]
Question #23
Topic 1
⼀家公司使⽤ Amazon S3 标准存储来存储备份⽂件。这些⽂件在⼀个⽉内会被频繁访问。但是，⼀个⽉后这些
⽂件将不再被访问。该公司必须⽆限期地保留这些⽂件。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置 S3 智能分层以⾃动迁移对象。
B. 创建⼀个 S3 ⽣命周期配置，以便在 1 个⽉后将对象从 S3 标准版迁移到 S3 Glacier 深度归档版。
C. 创建⼀个 S3 ⽣命周期配置，使对象在 1 个⽉后从 S3 标准版过渡到 S3 标准版 - 不频繁访问版 (S3 标准版- IA)。
D. 创建⼀个 S3 ⽣命周期配置，以便在 1 个⽉后将对象从 S3 标准版过渡到 S3 单区-不频繁访问版 (S3 单区
IA)。
Question #24
Topic 1
⼀家公司在最近的账单中发现 Amazon EC2 费⽤增加。计费团队注意到部分 EC2 实例的实例类型出现了不必要
的垂直扩展。解决⽅案架构师需要创建⼀个图表，对⽐过去两个⽉的 EC2 费⽤，并进⾏深⼊分析，以找出垂直扩
展的根本原因。
解决⽅案架构师应该如何以最⼩的运维开销⽣成这些信息？
A. 使⽤ AWS Budgets 创建预算报告，并根据实例类型⽐较 EC2 成本。
B. 使⽤ Cost Explorer 的精细筛选功能，根据实例类型对 EC2 成本进⾏深⼊分析。
C. 使⽤ AWS 账单和成本管理仪表板中的图表，⽐较过去 2 个⽉内不同实例类型的 EC2 成本。
D. 使⽤ AWS 成本和使⽤情况报告创建报告并将其发送到 Amazon S3 存储桶。使⽤ Amazon QuickSight 并
以 Amazon S3 为数据源，根据实例类型⽣成交互式图表。
https://examlearn.online
[2026/05]
Question #25
Topic 1
⼀家公司正在设计⼀个应⽤程序。该应⽤程序使⽤ AWS Lambda 函数通过 Amazon API Gateway 接收信息，并
将信息存储在 Amazon Aurora PostgreSQL 数据库中。
在概念验证阶段，该公司需要⼤幅提⾼ Lambda 函数的配额，以处理需要加载到数据库中的⼤量数据。解决⽅案
架构师必须推荐⼀种新的设计⽅案，以提⾼可扩展性并最⼤限度地减少配置⼯作量。
哪种解决⽅案能够满⾜这些要求？
A. 将 Lambda 函数代码重构为运⾏在 Amazon EC2 实例上的 Apache Tomcat 代码。使⽤原⽣ Java 数据库
连接 (JDBC) 驱动程序连接数据库。
B. 将平台从 Aurora 更改为 Amazon DynamoDB。配置 DynamoDB Accelerator (DAX) 集群。使⽤ DAX 客
户端 SDK 将现有的 DynamoDB API 调⽤指向 DAX 集群。
C. 设置两个 Lambda 函数。配置⼀个函数接收信息。配置另⼀个函数将信息加载到数据库中。使⽤ Amazon
Simple Notification Service (Amazon SNS) 集成这两个 Lambda 函数。
Question #26
D. 设置两个 Lambda 函数。配置⼀个函数接收信息。配置另⼀个函数将信息加载到数据库中。使⽤ Amazon
Simple Queue Service (Amazon SQS) 队列集成这两个 Lambda 函数。
⼀家公司需要审查其 AWS 云部署，以确保其 Amazon S3 存储桶没有未经授权的配置更改。
解决⽅案架构师应该如何做才能实现这⼀⽬标？
A. 使⽤适当的规则启⽤ AWS Config。
B. 启⽤ AWS Trusted Advisor 并进⾏相应的检查。
C. 使⽤合适的评估模板启⽤亚⻢逊督察器。
Topic 1
D. 启⽤ Amazon S3 服务器访问⽇志记录。配置 Amazon EventBridge（Amazon CloudWatch Events）。
https://examlearn.online
[2026/05]
Question #27
Topic 1
⼀家公司即将推出⼀款新应⽤，并将在 Amazon CloudWatch 控制⾯板上显示应⽤指标。该公司的产品经理需要
定期访问此控制⾯板。该产品经理没有 AWS 账户。解决⽅案架构师必须遵循最⼩权限原则，为该产品经理提供
访问权限。
哪种解决⽅案能够满⾜这些要求？
A. 从 CloudWatch 控制台共享仪表板。输⼊产品经理的电⼦邮件地址，并完成共享步骤。向产品经理提供仪
表板的共享链接。
B. 专⻔为产品经理创建⼀个 IAM ⽤户。将 CloudWatchReadOnlyAccess AWS 托管策略附加到该⽤户。将
新的登录凭证分享给产品经理。将正确的控制⾯板的浏览器 URL 分享给产品经理。
C. 为公司员⼯创建 IAM ⽤户。将 ViewOnlyAccess AWS 托管策略附加到该 IAM ⽤户。将新的登录凭证分享
给产品经理。请产品经理访问 CloudWatch 控制台，并在“仪表盘”部分按名称找到相应的仪表盘。
D. 在公有⼦⽹中部署堡垒服务器。当产品经理需要访问控制⾯板时，启动服务器并共享 RDP 凭证。在堡垒服
务器上，确保浏览器已配置为使⽤缓存的 AWS 凭证打开控制⾯板 URL，且这些凭证具有查看控制⾯板的相应
权限。
Question #28
Topic 1
⼀家公司正在将应⽤程序迁移到 AWS。这些应⽤程序部署在不同的账户中。该公司使⽤ AWS Organizations 集
中管理这些账户。该公司的安全团队需要⼀个跨所有账户的单点登录 (SSO) 解决⽅案。该公司必须继续管理其本
地⾃管理 Microsoft Active Directory 中的⽤户和组。
哪种解决⽅案能够满⾜这些要求？
A. 从 AWS SSO 控制台启⽤ AWS 单点登录 (AWS SSO)。使⽤ AWS Directory Service for Microsoft Active
Directory 创建单向林信任或单向域信任，将公司⾃管理的 Microsoft Active Directory 与 AWS SSO 连接起
来。
B. 从 AWS SSO 控制台启⽤ AWS 单点登录 (AWS SSO)。使⽤ AWS Directory Service for Microsoft Active
Directory 创建双向林信任，将公司⾃管理的 Microsoft Active Directory 与 AWS SSO 连接起来。
C. 使⽤ AWS Directory Service。与公司⾃⾏管理的 Microsoft Active Directory 创建双向信任关系。
D. 在本地部署身份提供商 (IdP)。从 AWS SSO 控制台启⽤ AWS 单点登录 (AWS SSO)。
https://examlearn.online
[2026/05]
Question #29
Topic 1
⼀家公司提供基于 UDP 连接的互联⽹语⾳协议 (VoIP) 服务。该服务由运⾏在⾃动扩展组中的 Amazon EC2 实例
组成。该公司在多个 AWS 区域部署了服务。
该公司需要将⽤户路由到延迟最低的区域，并且还需要在区域之间实现⾃动故障转移。
哪种解决⽅案能够满⾜这些要求？
A. 部署⽹络负载均衡器 (NLB) 和关联的⽬标组。将⽬标组与⾃动扩展组关联。在每个区域中，将 NLB ⽤作
AWS 全球加速器终端节点。
B. 部署应⽤程序负载均衡器 (ALB) 和关联的⽬标组。将⽬标组与⾃动扩展组关联。在每个区域中，将 ALB ⽤
作 AWS 全球加速器终端节点。
C. 部署⽹络负载均衡器 (NLB) 和关联的⽬标组。将⽬标组与⾃动扩展组关联。创建指向每个 NLB 别名的
Amazon Route 53 延迟记录。创建使⽤该延迟记录作为源的 Amazon CloudFront 分发。
D. 部署应⽤程序负载均衡器 (ALB) 和关联的⽬标组。将⽬标组与⾃动扩展组关联。创建⼀条指向每个 ALB 别
名的 Amazon Route 53 加权记录。部署⼀个使⽤该加权记录作为源的 Amazon CloudFront 分发。
Question #30
Topic 1
⼀个开发团队每⽉在其启⽤了性能洞察的通⽤型 Amazon RDS for MySQL 数据库实例上运⾏资源密集型测试。
测试每⽉持续 48 ⼩时，并且是唯⼀使⽤该数据库的进程。该团队希望在不降低数据库实例的计算和内存性能的
前提下，降低运⾏测试的成本。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 测试完成后停⽌数据库实例。必要时重新启动数据库实例。
B. 使⽤数据库实例的⾃动扩展策略，以便在测试完成后⾃动扩展。
C. 测试完成后创建快照。终⽌数据库实例，并在需要时恢复快照。
D. 测试完成后，将数据库实例修改为低容量实例。必要时再次修改数据库实例。
https://examlearn.online
[2026/05]
Question #31
Topic 1
⼀家将其 Web 应⽤程序托管在 AWS 上的公司希望确保所有 Amazon EC2 实例、Amazon RDS 数据库实例和
Amazon Redshift 集群都已配置标签。该公司希望尽可能减少配置和运⾏此检查的⼯作量。
解决⽅案架构师应该如何实现这⼀⽬标？
A. 使⽤ AWS Config 规则定义和检测未正确标记的资源。
B. 使⽤成本浏览器显示未正确标记的资源。⼿动标记这些资源。
C. 编写 API 调⽤来检查所有资源是否已正确分配标签。定期在 EC2 实例上运⾏代码。
D. 编写 API 调⽤来检查所有资源是否已正确分配标签。通过 Amazon CloudWatch 调度 AWS Lambda 函数
定期运⾏代码。
Question #32
Topic 1
⼀个开发团队需要托管⼀个⽹站，供其他团队访问。⽹站内容包括 HTML、CSS、客户端 JavaScript 和图⽚。
哪种⽹站托管⽅式最具成本效益？
A. 将⽹站容器化并托管在 AWS Fargate 上。
B. 创建⼀个 Amazon S3 存储桶并将⽹站托管在那⾥。
C. 在 Amazon EC2 实例上部署 Web 服务器来托管⽹站。
D. 使⽤ Express.js 框架的 AWS Lambda ⽬标配置应⽤程序负载均衡器。
https://examlearn.online
[2026/05]
Question #33
Topic 1
⼀家公司在 AWS 上运⾏⼀个在线市场 Web 应⽤程序。该应⽤程序在⾼峰时段服务数⼗万⽤户。该公司需要⼀个
可扩展的、近乎实时的解决⽅案，以便与其他⼏个内部应⽤程序共享数百万笔⾦融交易的详细信息。此外，交易
还需要经过处理，去除敏感数据，然后才能存储到⽂档数据库中，以实现低延迟检索。
解决⽅案架构师应该推荐什么⽅案来满⾜这些要求？
A. 将交易数据存储到 Amazon DynamoDB 中。在 DynamoDB 中设置规则，以便在每次写⼊交易时删除敏感
数据。使⽤ DynamoDB Streams 与其他应⽤程序共享交易数据。
B. 将交易数据流式传输到 Amazon Kinesis Data Firehose，以便将数据存储在 Amazon DynamoDB 和
Amazon S3 中。使⽤ AWS Lambda 与 Kinesis Data Firehose 的集成来移除敏感数据。其他应⽤程序可以使
⽤存储在 Amazon S3 中的数据。
C. 将交易数据流式传输到 Amazon Kinesis Data Streams。使⽤ AWS Lambda 集成从每笔交易中移除敏感
数据，然后将交易数据存储在 Amazon DynamoDB 中。其他应⽤程序可以从 Kinesis 数据流中使⽤这些交易
数据。
以使⽤存储在 Amazon S3 中的事务⽂件。
Question #34
D. 将批量事务数据以⽂件形式存储在 Amazon S3 中。使⽤ AWS Lambda 处理每个⽂件，并在更新 Amazon
S3 中的⽂件之前删除敏感数据。Lambda 函数随后将数据存储在 Amazon DynamoDB 中。其他应⽤程序可
Topic 1
⼀家公司将其多层应⽤程序托管在 AWS 上。为了满⾜合规性、治理、审计和安全要求，该公司必须跟踪其 AWS
资源上的配置更改，并记录对这些资源的 API 调⽤历史记录。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 使⽤ AWS CloudTrail 跟踪配置更改，使⽤ AWS Config 记录 API 调⽤。
B. 使⽤ AWS Config 跟踪配置更改，使⽤ AWS CloudTrail 记录 API 调⽤。
C. 使⽤ AWS Config 跟踪配置更改，使⽤ Amazon CloudWatch 记录 API 调⽤。
D. 使⽤ AWS CloudTrail 跟踪配置更改，使⽤ Amazon CloudWatch 记录 API 调⽤。
https://examlearn.online
[2026/05]
Question #35
Topic 1
⼀家公司正准备在 AWS 云上推出⾯向公众的 Web 应⽤程序。该架构由位于 VPC 内的 Amazon EC2 实例组成，
并由弹性负载均衡器 (ELB) 提供⽀持。DNS 服务由第三⽅提供。该公司解决⽅案架构师必须推荐⼀种能够检测和
防御⼤规模 DDoS 攻击的解决⽅案。
哪种解决⽅案符合这些要求？
A. 在账户上启⽤ Amazon GuardDuty。
B. 在 EC2 实例上启⽤ Amazon Inspector。
C. 启⽤ AWS Shield 并将其分配给 Amazon Route 53。
D. 启⽤ AWS Shield Advanced 并将 ELB 分配给它。
Question #36
密 (SSE-S3)。配置 S3 存储桶之间的复制。
Topic 1
⼀家公司正在 AWS 云上构建⼀个应⽤程序。该应⽤程序会将数据存储在两个 AWS 区域的 Amazon S3 存储桶
中。该公司必须使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥来加密存储在 S3 存储桶中的
所有数据。两个 S3 存储桶中的数据必须使⽤相同的 KMS 密钥进⾏加密和解密。数据和密钥必须分别存储在两个
区域中。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 在每个区域中创建⼀个 S3 存储桶。将 S3 存储桶配置为使⽤ Amazon S3 管理的加密密钥进⾏服务器端加
B. 创建客户管理的多区域 KMS 密钥。在每个区域中创建⼀个 S3 存储桶。配置 S3 存储桶之间的复制。配置
应⽤程序使⽤客户端加密的 KMS 密钥。
C. 在每个区域中创建客户管理的 KMS 密钥和 S3 存储桶。配置 S3 存储桶以使⽤ Amazon S3 管理的加密密
钥 (SSE-S3) 进⾏服务器端加密。配置 S3 存储桶之间的复制。
D. 在每个区域中创建客户管理的 KMS 密钥和⼀个 S3 存储桶。配置 S3 存储桶以使⽤基于 AWS KMS 密钥的
服务器端加密 (SSE-KMS)。配置 S3 存储桶之间的复制。
https://examlearn.online
[2026/05]
Question #37
Topic 1
⼀家公司最近在其 AWS 账户的 Amazon EC2 实例上启动了各种新的⼯作负载。该公司需要制定⼀个策略，以便
远程安全地访问和管理这些实例。该公司需要实施⼀个可重复的流程，该流程能够与 AWS 原⽣服务协同⼯作，
并遵循 AWS 架构完善框架。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ EC2 串⾏控制台直接访问每个实例的终端界⾯进⾏管理。
B. 将相应的 IAM ⻆⾊附加到每个现有实例和新实例。使⽤ AWS Systems Manager Session Manager 建⽴
远程 SSH 会话。
C. 创建管理 SSH 密钥对。将公钥加载到每个 EC2 实例中。在公共⼦⽹中部署堡垒主机，为每个实例的管理
提供隧道。
D. 建⽴ AWS 站点到站点 VPN 连接。指示管理员使⽤其本地计算机，通过 VPN 隧道使⽤ SSH 密钥直接连接
到实例。
Question #38
Topic 1
⼀家公司在 Amazon S3 上托管了⼀个静态⽹站，并使⽤ Amazon Route 53 进⾏ DNS 解析。该⽹站的全球访问
量正在激增。该公司必须降低⽤户访问该⽹站的延迟。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将包含⽹站的 S3 存储桶复制到所有 AWS 区域。添加 Rout 53 地理位置路由条⽬。
B. 在 AWS Global Accelerator 中配置加速器。将提供的 IP 地址与 S3 存储桶关联。编辑 Route 53 条⽬，使
其指向加速器的 IP 地址。
C. 在 S3 存储桶前⾯添加 Amazon CloudFront 分发。编辑 Route 53 条⽬，使其指向 CloudFront 分发。
D. 在存储桶上启⽤ S3 传输加速。编辑 Route 53 条⽬，使其指向新的端点。
https://examlearn.online
[2026/05]
Question #39
Topic 1
⼀家公司在其⽹站上维护着⼀个可搜索的商品库。数据存储在 Amazon RDS for MySQL 数据库表中，该表包含
超过 1000 万⾏数据。该数据库拥有 2 TB 的通⽤型 SSD 存储空间。每天，该公司⽹站都会对这些数据进⾏数百
万次更新。
该公司注意到，某些插⼊操作需要 10 秒或更⻓时间才能完成。该公司已确定数据库存储性能是造成此性能问题的
原因。
哪种解决⽅案可以解决此性能问题？
A. 将存储类型更改为已配置 IOPS SSD。
B. 将数据库实例更改为内存优化型实例类。
C. 将数据库实例更改为可突发性能实例类。
D. 启⽤ MySQL 原⽣异步复制的多可⽤区 RDS 只读副本。
Question #40
到 Amazon S3 Glacier。
14 天的数据。
Topic 1
⼀家公司拥有数千台边缘设备，每天共产⽣ 1 TB 的状态警报。每条警报的⼤⼩约为 2 KB。解决⽅案架构师需要
实施⼀个解决⽅案来接收和存储这些警报，以便⽇后进⾏分析。
该公司希望实现⾼可⽤性解决⽅案。然⽽，该公司需要尽可能降低成本，并且不希望管理额外的基础设施。此
外，该公司希望保留 14 天的数据以供⽴即分析，并将超过 14 天的数据存档。在
满⾜这些要求的前提下，哪种解决⽅案的运⾏效率最⾼？
A. 创建⼀个 Amazon Kinesis Data Firehose 数据流来接收告警。配置 Kinesis Data Firehose 数据流，将告
警发送到 Amazon S3 存储桶。设置 S3 ⽣命周期配置，以便在 14 天后将数据迁移到 Amazon S3 Glacier。
B. 在两个可⽤区启动 Amazon EC2 实例，并将其置于弹性负载均衡器 (ELB) 后⽅以接收告警。在 EC2 实例
上创建⼀个脚本，将告警存储在 Amazon S3 存储桶中。设置 S3 ⽣命周期配置，以便在 14 天后将数据迁移
C. 创建⼀个 Amazon Kinesis Data Firehose 数据流来接收告警。配置 Kinesis Data Firehose 数据流，将告
警发送到 Amazon OpenSearch Service（Amazon Elasticsearch Service）集群。设置 Amazon
OpenSearch Service（Amazon Elasticsearch Service）集群，使其每天⼿动创建快照，并删除集群中超过
D. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 标准队列来接收警报，并将消息保留期设置为
14 天。配置消费者轮询 SQS 队列，检查消息的期限，并根据需要分析消息数据。如果消息已超过 14 天，消
费者应将消息复制到 Amazon S3 存储桶，并从 SQS 队列中删除该消息。
https://examlearn.online
[2026/05]
Question #41
Topic 1
⼀家公司的应⽤程序集成了多个软件即服务 (SaaS) 数据源以进⾏数据采集。该公司运⾏ Amazon EC2 实例来接
收数据，并将数据上传到 Amazon S3 存储桶进⾏分析。接收和上传数据的同⼀个 EC2 实例还会在上传完成后向
⽤户发送通知。该公司注意到应⽤程序性能缓慢，并希望尽可能地提升性能。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 创建⼀个⾃动扩展组，以便 EC2 实例可以横向扩展。配置 S3 事件通知，以便在上传到 S3 存储桶完成
后，向 Amazon Simple Notification Service (Amazon SNS) 主题发送事件。
B. 创建⼀个 Amazon AppFlow 流，⽤于在每个 SaaS 源和 S3 存储桶之间传输数据。配置 S3 事件通知，以
便在上传到 S3 存储桶完成后向 Amazon Simple Notification Service (Amazon SNS) 主题发送事件。
C. 为每个 SaaS 源创建⼀条 Amazon EventBridge（Amazon CloudWatch Events）规则，⽤于发送输出数
据。将 S3 存储桶配置为该规则的⽬标。创建第⼆条 EventBridge（CloudWatch Events）规则，⽤于在上传
到 S3 存储桶完成后发送事件。将 Amazon Simple Notification Service（Amazon SNS）主题配置为第⼆条
规则的⽬标。
D. 创建⼀个 Docker 容器来代替 EC2 实例。将容器化应⽤程序托管在 Amazon Elastic Container Service
Amazon Simple Notification Service (Amazon SNS) 主题发送事件。
Question #42
(Amazon ECS) 上。配置 Amazon CloudWatch Container Insights，以便在上传到 S3 存储桶完成后向
Topic 1
⼀家公司在单个 VPC 中的 Amazon EC2 实例上运⾏⼀个⾼可⽤性图像处理应⽤程序。这些 EC2 实例运⾏在多个
可⽤区内的多个⼦⽹中。这些 EC2 实例之间互不通信。但是，它们通过同⼀个 NAT ⽹关从 Amazon S3 下载图
像，并将图像上传到 Amazon S3。该公司担⼼数据传输费⽤。
该公司避免区域数据传输费⽤的最经济有效的⽅法是什么？
A. 在每个可⽤区启动 NAT ⽹关。
B. 将 NAT ⽹关替换为 NAT 实例。
C. 为 Amazon S3 部署⽹关 VPC 端点。
D. 配置 EC2 专⽤主机来运⾏ EC2 实例。
https://examlearn.online
[2026/05]
Question #43
Topic 1
⼀家公司有⼀个本地应⽤程序，会⽣成⼤量对时间要求较⾼的数据，这些数据会备份到 Amazon S3。随着应⽤程
序规模的扩⼤，⽤户开始抱怨⽹络带宽不⾜。解决⽅案架构师需要设计⼀个⻓期解决⽅案，既能确保及时将数据
备份到 Amazon S3，⼜能最⼤限度地减少对内部⽤户⽹络连接的影响。
哪个解决⽅案符合这些要求？
A. 建⽴ AWS VPN 连接，并通过 VPC ⽹关终端节点代理所有流量。
B. 建⽴新的 AWS Direct Connect 连接，并通过此新连接直接传输备份流量。
C. 每⽇订购 AWS Snowball 设备。将数据加载到 Snowball 设备上，并每天将设备退还给 AWS。
D. 通过 AWS 管理控制台提交⽀持⼯单。请求移除账户中的 S3 服务限制。
Question #44
A. 在 S3 存储桶上启⽤版本控制。
B. 在 S3 存储桶上启⽤ MFA 删除。
⼀家公司拥有⼀个包含关键数据的 Amazon S3 存储桶。该公司必须保护这些数据免遭意外删除。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
C. 在 S3 存储桶上创建存储桶策略。
D. 启⽤ S3 存储桶的默认加密。
E. 为 S3 存储桶中的对象创建⽣命周期策略。
Topic 1
https://examlearn.online
[2026/05]
Question #45
⼀家公司的数据摄取⼯作流包含以下内容：
• ⽤于接收新数据交付通知的 Amazon Simple Notification Service (Amazon SNS) 主题；
Topic 1
• ⽤于处理数据并记录元数据的 AWS Lambda 函数。
该公司发现，由于⽹络连接问题，摄取⼯作流偶尔会失败。发⽣此类故障时，除⾮该公司⼿动重新运⾏作业，否
则 Lambda 函数不会摄取相应的数据。
解决⽅案架构师应采取哪些措施组合来确保 Lambda 函数将来能够摄取所有数据？（选择两项。）
A. 在多个可⽤区部署 Lambda 函数。
B. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列，并将其订阅到 SNS 主题。
C. 增加分配给 Lambda 函数的 CPU 和内存。
D. 增加 Lambda 函数的预置吞吐量。
E. 修改 Lambda 函数，使其从 Amazon Simple Queue Service (Amazon SQS) 队列读取数据。
Question #46
除包含 PII 的对象。
Topic 1
⼀家公司开发了⼀款⾯向⻔店的营销服务应⽤。该服务基于⻔店顾客之前的购买记录。⻔店通过SFTP将交易数据
上传⾄公司，公司会对数据进⾏处理和分析，以⽣成新的营销⽅案。部分⽂件⼤⼩超过200GB。
近期，公司发现部分⻔店上传的⽂件中包含不应包含的个⼈身份信息（PII）。公司希望在再次发⽣PII共享时，管
理员能够收到警报。此外，公司还希望实现⾃动修复。
解决⽅案架构师应如何以最⼩的开发⼯作量满⾜这些要求？
A. 使⽤ Amazon S3 存储桶作为安全传输点。使⽤ Amazon Inspector 扫描存储桶中的对象。如果对象包含
个⼈身份信息 (PII)，则触发 S3 ⽣命周期策略以删除包含 PII 的对象。
B. 使⽤ Amazon S3 存储桶作为安全传输点。使⽤ Amazon Macie 扫描存储桶中的对象。如果对象包含个⼈
身份信息 (PII)，则使⽤ Amazon Simple Notification Service (Amazon SNS) 向管理员发出通知，要求其删
C. 在 AWS Lambda 函数中实现⾃定义扫描算法。当对象加载到存储桶中时触发该函数。如果对象包含个⼈
身份信息 (PII)，则使⽤ Amazon Simple Notification Service (Amazon SNS) 向管理员发出通知，要求其删
除包含 PII 的对象。
D. 在 AWS Lambda 函数中实现⾃定义扫描算法。当对象加载到存储桶时触发该函数。如果对象包含个⼈身份
信息 (PII)，则使⽤ Amazon Simple Email Service (Amazon SES) 向管理员发送通知，并触发 S3 ⽣命周期
策略以删除包含 PII 的对象。
https://examlearn.online
[2026/05]
Question #47
Topic 1
⼀家公司需要保证在特定 AWS 区域的三个特定可⽤区内获得⾜够的 Amazon EC2 容量，⽤于即将举办的为期⼀
周的活动。
该公司应该如何做才能保证获得所需的 EC2 容量？
A. 购买指定所需区域的预留实例。
B. 创建按需容量预留，并指定所需的区域。
C. 购买指定区域和所需三个可⽤区的预留实例。
D. 创建⼀个按需容量预留，指定所需的区域和三个可⽤区。
Question #48
Topic 1
⼀家公司的⽹站使⽤ Amazon EC2 实例存储其商品⽬录。该公司希望确保⽬录具有⾼可⽤性，并且存储在持久位
置。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 将⽬录迁移到 Amazon ElastiCache for Redis。
B. 部署具有更⼤实例存储的更⼤ EC2 实例。
C. 将⽬录从实例存储移动到 Amazon S3 Glacier Deep Archive。
D. 将⽬录移动到 Amazon Elastic File System (Amazon EFS) ⽂件系统。
https://examlearn.online
[2026/05]
Question #49
Topic 1
⼀家公司按⽉存储通话记录⽂件。⽤户会在通话发⽣后⼀年内随机访问这些⽂件，但⼀年后访问频率较低。该公
司希望优化其解决⽅案，使⽤户能够尽快查询和检索⼀年以内的⽂件。检索较旧⽂件存在⼀定的延迟是可以接受
的。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将带有标签的单个⽂件存储在 Amazon S3 Glacier Instant Retrieval 中。查询标签以从 S3 Glacier
Instant Retrieval 中检索⽂件。
B. 将单个⽂件存储在 Amazon S3 智能分层存储中。使⽤ S3 ⽣命周期策略在 1 年后将⽂件迁移到 S3 Glacier
灵活检索存储。使⽤ Amazon Athena 查询和检索 Amazon S3 中的⽂件。使⽤ S3 Glacier Select 查询和检
索 S3 Glacier 中的⽂件。
C. 将带有标签的单个⽂件存储在 Amazon S3 标准存储中。将每个归档⽂件的搜索元数据存储在 Amazon S3
标准存储中。使⽤ S3 ⽣命周期策略，在 1 年后将⽂件迁移到 S3 Glacier 即时检索。通过搜索 Amazon S3
中的元数据来查询和检索⽂件。
Question #50
D. 将单个⽂件存储在 Amazon S3 标准存储中。使⽤ S3 ⽣命周期策略在 1 年后将⽂件移动到 S3 Glacier 深
度归档。将搜索元数据存储在 Amazon RDS 中。从 Amazon RDS 查询⽂件。从 S3 Glacier 深度归档中检索
⽂件。
Topic 1
⼀家公司在 1000 个 Amazon EC2 Linux 实例上运⾏⽣产⼯作负载，该⼯作负载由第三⽅软件驱动。该公司需要
尽快为所有 EC2 实例上的第三⽅软件打补丁，以修复⼀个关键的安全漏洞。
解决⽅案架构师应该如何满⾜这些要求？
A. 创建⼀个 AWS Lambda 函数，将补丁应⽤到所有 EC2 实例。
B. 配置 AWS Systems Manager Patch Manager 将补丁应⽤到所有 EC2 实例。
C. 安排 AWS Systems Manager 维护窗⼝，将补丁应⽤到所有 EC2 实例。
D. 使⽤ AWS Systems Manager Run Command 运⾏⾃定义命令，将补丁应⽤到所有 EC2 实例。
https://examlearn.online
[2026/05]
Question #51
Topic 1
⼀家公司正在开发⼀款应⽤程序，该程序提供订单发货统计数据，可通过 REST API 获取。该公司希望提取发货
统计数据，将其整理成易于阅读的 HTML 格式，并每天早上同时将报告发送到多个电⼦邮件地址。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 配置应⽤程序将数据发送到 Amazon Kinesis Data Firehose。
B. 使⽤ Amazon Simple Email Service (Amazon SES) 格式化数据并通过电⼦邮件发送报告。
C. 创建⼀个 Amazon EventBridge（Amazon CloudWatch Events）计划事件，该事件会调⽤ AWS Glue 作
业来查询应⽤程序的 API 以获取数据。
D. 创建⼀个 Amazon EventBridge（Amazon CloudWatch Events）计划事件，该事件调⽤ AWS Lambda
函数来查询应⽤程序的 API 以获取数据。
E. 将应⽤程序数据存储在 Amazon S3 中。创建⼀个 Amazon Simple Notification Service (Amazon SNS)
主题作为 S3 事件⽬标，以便通过电⼦邮件发送报告。
Question #52
S3 进⾏存储。
Topic 1
⼀家公司希望将其本地应⽤程序迁移到 AWS。该应⽤程序⽣成的输出⽂件⼤⼩从⼏⼗ GB 到⼏百 TB 不等。应⽤
程序数据必须存储在标准⽂件系统结构中。该公司需要⼀个能够⾃动扩展、⾼可⽤且运维开销最⼩的解决⽅案。
哪种解决⽅案能够满⾜这些要求？
A. 将应⽤程序迁移到 Amazon Elastic Container Service (Amazon ECS) 上以容器形式运⾏。使⽤ Amazon
B. 将应⽤程序迁移到 Amazon Elastic Kubernetes Service (Amazon EKS) 上以容器形式运⾏。使⽤
Amazon Elastic Block Store (Amazon EBS) 进⾏存储。
C. 将应⽤程序迁移到多可⽤区⾃动扩展组中的 Amazon EC2 实例。使⽤ Amazon Elastic File System
(Amazon EFS) 进⾏存储。
D. 将应⽤程序迁移到多可⽤区⾃动扩展组中的 Amazon EC2 实例。使⽤ Amazon Elastic Block Store
(Amazon EBS) 进⾏存储。
https://examlearn.online
[2026/05]
Question #53
Topic 1
⼀家公司需要将其会计记录存储在 Amazon S3 中。这些记录必须能够⽴即访问 1 年，然后必须归档 9 年。在整
个 10 年期间，公司内的任何⼈员，包括管理员⽤户和 root ⽤户，都不能删除这些记录。记录的存储必须具有最
⾼的可靠性。
哪种解决⽅案能够满⾜这些要求？
A. 将记录存储在 S3 Glacier 中，保存期限为 10 年。使⽤访问控制策略，禁⽌在 10 年内删除这些记录。
B. 使⽤ S3 智能分层存储记录。使⽤ IAM 策略禁⽌删除记录。10 年后，更改 IAM 策略以允许删除。
C. 使⽤ S3 ⽣命周期策略，在 1 年后将记录从 S3 标准版迁移到 S3 Glacier 深度归档版。使⽤ S3 对象锁
定，并在合规模式下锁定 10 年。
D. 使⽤ S3 ⽣命周期策略，在 1 年后将记录从 S3 标准版过渡到 S3 单区域低频访问版 (S3 单区域-IA)。在治
理模式下使⽤ S3 对象锁定，期限为 10 年。
Question #54
Topic 1
⼀家公司在 AWS 上运⾏多个 Windows ⼯作负载。该公司员⼯使⽤托管在两个 Amazon EC2 实例上的 Windows
⽂件共享。这些⽂件共享之间会同步数据并维护数据副本。该公司需要⼀个⾼可⽤性且持久的存储解决⽅案，以
保留⽤户当前访问⽂件的⽅式。
解决⽅案架构师应该如何满⾜这些要求？
A. 将所有数据迁移到 Amazon S3。设置 IAM 身份验证，以便⽤户访问⽂件。
B. 设置 Amazon S3 ⽂件⽹关。将 S3 ⽂件⽹关挂载到现有的 EC2 实例上。
C. 将⽂件共享环境扩展到采⽤多可⽤区配置的 Amazon FSx for Windows ⽂件服务器。将所有数据迁移到
FSx for Windows ⽂件服务器。
D. 将⽂件共享环境扩展到采⽤多可⽤区配置的 Amazon Elastic File System (Amazon EFS)。将所有数据迁
移到 Amazon EFS。
https://examlearn.online
[2026/05]
Question #55
Topic 1
⼀位解决⽅案架构师正在开发⼀个包含多个⼦⽹的 VPC 架构。该架构将托管使⽤ Amazon EC2 实例和 Amazon
RDS 数据库实例的应⽤程序。该架构包含两个可⽤区中的六个⼦⽹。每个可⽤区都包含⼀个公有⼦⽹、⼀个私有
⼦⽹和⼀个专⽤于数据库的⼦⽹。只有在私有⼦⽹中运⾏的 EC2 实例才能访问 RDS 数据库。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个新的路由表，排除指向公共⼦⽹ CIDR 块的路由。将该路由表与数据库⼦⽹关联。
B. 创建⼀个安全组，拒绝来⾃分配给公共⼦⽹中实例的安全组的⼊站流量。将该安全组附加到数据库实例。
C. 创建⼀个安全组，允许来⾃该安全组的⼊站流量，并将该安全组分配给私有⼦⽹中的实例。将该安全组附
加到数据库实例。
D. 在公有⼦⽹和私有⼦⽹之间创建新的对等连接。在私有⼦⽹和数据库⼦⽹之间创建不同的对等连接。
Question #56
Topic 1
⼀家公司已在 Amazon Route 53 注册了域名。该公司使⽤位于 ca-central-1 区域的 Amazon API Gateway 作为
其后端微服务 API 的公共接⼝。第三⽅服务可以安全地使⽤这些 API。该公司希望使⽤公司域名和相应的证书来
设计其 API Gateway URL，以便第三⽅服务可以使⽤ HTTPS。
哪种解决⽅案能够满⾜这些要求？
A. 在 API ⽹关中创建名称为“Endpoint-URL”、值为“公司域名”的阶段变量，以覆盖默认 URL。将与公司域名
关联的公有证书导⼊ AWS Certificate Manager (ACM)。
B. 使⽤公司域名创建 Routal 53 DNS 记录。将别名记录指向区域 API ⽹关阶段端点。将与公司域名关联的公
有证书导⼊到 us-east-1 区域的 AWS Certificate Manager (ACM) 中。
C. 创建区域 API ⽹关端点。将 API ⽹关端点与公司域名关联。将与公司域名关联的公有证书导⼊到同⼀区域
的 AWS Certificate Manager (ACM) 中。将该证书附加到 API ⽹关端点。配置 Route 53 将流量路由到 API
⽹关端点。
D. 创建区域 API ⽹关端点。将 API ⽹关端点与公司域名关联。将与公司域名关联的公有证书导⼊到美国东部
1 区域的 AWS Certificate Manager (ACM) 中。将该证书附加到 API ⽹关 API。创建包含公司域名的 Route
53 DNS 记录。将 A 记录指向公司域名。
https://examlearn.online
[2026/05]
Question #57
Topic 1
⼀家公司运营着⼀个热⻔的社交媒体⽹站。该⽹站允许⽤户上传图⽚与其他⽤户分享。该公司希望确保图⽚不包
含不当内容。该公司需要⼀个能够最⼤限度减少开发⼯作量的解决⽅案。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 使⽤ Amazon Comprehend 检测不当内容。对于置信度较低的预测，则使⽤⼈⼯审核。
B. 使⽤亚⻢逊 Rekognition 检测不当内容。对于置信度较低的预测，则使⽤⼈⼯审核。
C. 使⽤ Amazon SageMaker 检测不当内容。使⽤真实数据标记置信度较低的预测结果。
D. 使⽤ AWS Fargate 部署⾃定义机器学习模型来检测不当内容。使⽤真实标签标记置信度较低的预测结果。
Question #58
⼀家公司希望将其关键应⽤程序运⾏在容器中，以满⾜可扩展性和可⽤性的要求。该公司更倾向于专注于关键应
⽤程序的维护，⽽不愿负责配置和管理运⾏容器化⼯作负载的底层基础设施。
解决⽅案架构师应该如何满⾜这些要求？
A. 使⽤ Amazon EC2 实例，并在实例上安装 Docker。
B. 在 Amazon EC2 ⼯作节点上使⽤ Amazon Elastic Container Service (Amazon ECS)。
C. 在 AWS Fargate 上使⽤ Amazon Elastic Container Service (Amazon ECS)。
Amazon EC2 实例。
Question #59
Redshift ⽤于分析。
Topic 1
D. 使⽤来⾃ Amazon Elastic Container Service (Amazon ECS) 优化的 Amazon Machine Image (AMI) 的
Topic 1
⼀家公司托管着超过 300 个全球⽹站和应⽤程序。该公司需要⼀个平台来分析每天超过 30 TB 的点击流数据。
解决⽅案架构师应该如何传输和处理这些点击流数据？
A. 设计⼀个 AWS 数据管道，将数据归档到 Amazon S3 存储桶，并运⾏ Amazon EMR 集群来⽣成分析。
B. 创建⼀个 Amazon EC2 实例的⾃动扩展组来处理数据，并将其发送到 Amazon S3 数据湖，供 Amazon
C. 将数据缓存到 Amazon CloudFront。将数据存储在 Amazon S3 存储桶中。当有对象添加到 S3 存储桶
时，运⾏ AWS Lambda 函数来处理数据以进⾏分析。
D. 从 Amazon Kinesis Data Streams 收集数据。使⽤ Amazon Kinesis Data Firehose 将数据传输到
Amazon S3 数据湖。将数据加载到 Amazon Redshift 中进⾏分析。
https://examlearn.online
[2026/05]
Question #60
Topic 1
⼀家公司在 AWS 上托管了⼀个⽹站。该⽹站位于⼀个应⽤程序负载均衡器 (ALB) 之后，该 ALB 配置为分别处理
HTTP 和 HTTPS 请求。该公司希望将所有发送到该⽹站的请求转发为使⽤ HTTPS。
解决⽅案架构师应该如何满⾜此要求？
A. 更新 ALB 的⽹络 ACL，使其仅接受 HTTPS 流量。
B. 创建⼀条规则，将 URL 中的 HTTP 替换为 HTTPS。
C. 在 ALB 上创建监听器规则，将 HTTP 流量重定向到 HTTPS。
D. 将 ALB 替换为配置为使⽤服务器名称指示 (SNI) 的⽹络负载均衡器。
Question #61
Topic 1
⼀家公司正在 AWS 上开发⼀个两层 Web 应⽤程序。该公司开发⼈员已将该应⽤程序部署在 Amazon EC2 实例
上，该实例直接连接到后端 Amazon RDS 数据库。该公司不得在应⽤程序中硬编码数据库凭证。此外，该公司还
必须实现⼀种解决⽅案，以定期⾃动轮换数据库凭证。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将数据库凭证存储在实例元数据中。使⽤ Amazon EventBridge（Amazon CloudWatch Events）规则运
⾏⼀个计划的 AWS Lambda 函数，该函数同时更新 RDS 凭证和实例元数据。
B. 将数据库凭证存储在加密的 Amazon S3 存储桶中的配置⽂件⾥。使⽤ Amazon EventBridge（Amazon
CloudWatch Events）规则运⾏⼀个定时 AWS Lambda 函数，该函数同时更新 RDS 凭证和配置⽂件中的凭
证。使⽤ S3 版本控制功能，确保能够回退到之前的值。
C. 将数据库凭证作为密钥存储在 AWS Secrets Manager 中。启⽤密钥的⾃动轮换。将所需的权限附加到
EC2 ⻆⾊，以授予对该密钥的访问权限。
D. 将数据库凭证作为加密参数存储在 AWS Systems Manager Parameter Store 中。启⽤加密参数的⾃动轮
换。将所需的权限附加到 EC2 ⻆⾊，以授予对加密参数的访问权限。
https://examlearn.online
[2026/05]
Question #62
Topic 1
⼀家公司正在将⼀个新的公共 Web 应⽤程序部署到 AWS。该应⽤程序将运⾏在应⽤程序负载均衡器 (ALB) 之
后。该应⽤程序需要在边缘端使⽤由外部证书颁发机构 (CA) 颁发的 SSL/TLS 证书进⾏加密。该证书必须在过期
前每年轮换⼀次。
解决⽅案架构师应该如何满⾜这些要求？
A. 使⽤ AWS Certificate Manager (ACM) 颁发 SSL/TLS 证书。将证书应⽤到 ALB。使⽤托管续订功能⾃动
轮换证书。
B. 使⽤ AWS Certificate Manager (ACM) 颁发 SSL/TLS 证书。从证书导⼊密钥材料。将证书应⽤到 AL。使
⽤托管续订功能⾃动轮换证书。
C. 使⽤ AWS Certificate Manager (ACM) 私有证书颁发机构从根 CA 颁发 SSL/TLS 证书。将证书应⽤到
ALB。使⽤托管续订功能⾃动轮换证书。
D. 使⽤ AWS Certificate Manager (ACM) 导⼊ SSL/TLS 证书。将证书应⽤到 ALB。使⽤ Amazon
EventBridge（Amazon CloudWatch Events）在证书即将过期时发送通知。⼿动轮换证书。
Question #63
将其存储回 Amazon S3。
Topic 1
⼀家公司在 AWS 上运⾏其基础设施，其⽂档管理应⽤程序拥有 70 万注册⽤户。该公司计划开发⼀款产品，将⼤
型 .pdf ⽂件转换为 .jpg 图像⽂件。这些 .pdf ⽂件的平均⼤⼩为 5 MB。该公司需要存储原始⽂件和转换后的⽂
件。解决⽅案架构师必须设计⼀个可扩展的解决⽅案，以满⾜未来快速增⻓的需求。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将 .pdf ⽂件保存到 Amazon S3。配置 S3 PUT 事件以调⽤ AWS Lambda 函数将⽂件转换为 .jpg 格式并
B. 将 .pdf ⽂件保存到 Amazon DynamoDB 使⽤ DynamoDB Streams 功能调⽤ AWS Lambda 函数将⽂件
转换为 .jpg 格式并存储回 DynamoDB。
C. 将 .pdf ⽂件上传到包含 Amazon EC2 实例、Amazon Elastic Block Store (Amazon EBS) 存储和 Auto
Scaling 组的 AWS Elastic Beanstalk 应⽤程序。使⽤ EC2 实例中的程序将⽂件转换为 .jpg 格式。将 .pdf ⽂
件和 .jpg ⽂件保存到 EBS 存储中。
D. 将 .pdf ⽂件上传到包含 Amazon EC2 实例、Amazon Elastic File System (Amazon EFS) 存储和 Auto
Scaling 组的 AWS Elastic Beanstalk 应⽤程序。使⽤ EC2 实例中的程序将⽂件转换为 .jpg 格式。将 .pdf ⽂
件和 .jpg ⽂件保存到 EBS 存储中。
https://examlearn.online
[2026/05]
Question #64
Topic 1
⼀家公司在本地运⾏的 Windows ⽂件服务器上拥有超过 5 TB 的⽂件数据。⽤户和应⽤程序每天都会与这些数据
交互。
该公司正在将其 Windows ⼯作负载迁移到 AWS。随着迁移的进⾏，该公司需要以最低延迟访问 AWS 和本地⽂
件存储。该公司需要⼀个能够最⼤限度减少运维开销且⽆需对现有⽂件访问模式进⾏重⼤更改的解决⽅案。该公
司使⽤ AWS 站点到站点 VPN 连接来连接到 AWS。
解决⽅案架构师应该如何满⾜这些要求？
A. 在 AWS 上部署和配置 Amazon FSx for Windows ⽂件服务器。将本地⽂件数据迁移到 FSx for Windows
⽂件服务器。重新配置⼯作负载以使⽤ AWS 上的 FSx for Windows ⽂件服务器。
B. 在本地部署和配置 Amazon S3 ⽂件⽹关。将本地⽂件数据迁移到 S3 ⽂件⽹关。重新配置本地⼯作负载和
云⼯作负载以使⽤ S3 ⽂件⽹关。
C. 在本地部署和配置 Amazon S3 ⽂件⽹关。将本地⽂件数据迁移到 Amazon S3。根据每个⼯作负载的位
置，重新配置⼯作负载以直接使⽤ Amazon S3 或 S3 ⽂件⽹关。
D. 在 AWS 上部署和配置 Amazon FSx for Windows ⽂件服务器。在本地部署和配置 Amazon FSx ⽂件⽹
关。将本地⽂件数据迁移到 FSx ⽂件⽹关。配置云⼯作负载以使⽤ AWS 上的 FSx for Windows ⽂件服务
器。配置本地⼯作负载以使⽤ FSx ⽂件⽹关。
Question #65
Topic 1
某医院最近部署了⼀个基于 Amazon API Gateway 和 AWS Lambda 的 RESTful API。该医院使⽤ API Gateway
和 Lambda 上传 PDF 和 JPEG 格式的报告。医院需要修改 Lambda 代码，以识别报告中的受保护健康信息
(PHI)。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤现有的 Python 库从报告中提取⽂本，并从提取的⽂本中识别 PHI。
B. 使⽤ Amazon Textract 从报告中提取⽂本。使⽤ Amazon SageMaker 从提取的⽂本中识别 PHI（受保护
的健康信息）。
C. 使⽤ Amazon Textract 从报告中提取⽂本。使⽤ Amazon Comprehend Medical 从提取的⽂本中识别
PHI（受保护的健康信息）。
D. 使⽤ Amazon Rekognition 从报告中提取⽂本。使⽤ Amazon Comprehend Medical 从提取的⽂本中识别
PHI（受保护的健康信息）。
https://examlearn.online
[2026/05]
Question #66
Topic 1
⼀家公司有⼀个应⽤程序，会⽣成⼤量⽂件，每个⽂件⼤⼩约为 5 MB。这些⽂件存储在 Amazon S3 中。公司政
策要求⽂件必须保存 4 年才能删除。由于⽂件包含难以重现的关键业务数据，因此需要始终能够⽴即访问。⽂件
在创建后的前 30 天内访问频繁，但 30 天后访问频率很低。
哪种存储⽅案最具成本效益？
A. 创建⼀个 S3 存储桶⽣命周期策略，将⽂件从 S3 标准存储桶移动到 S3 Glacier 存储桶，并在对象创建 4
年后删除这些⽂件。
B. 创建 S3 存储桶⽣命周期策略，在对象创建 30 天后将⽂件从 S3 标准存储桶移动到 S3 单区域低频访问存
储桶 (S3 One Zone-IA)。在对象创建 4 年后删除这些⽂件。
C. 创建 S3 存储桶⽣命周期策略，在对象创建 30 天后将⽂件从 S3 标准存储桶移动到 S3 标准存储桶 - 不频
繁访问存储桶 (S3 标准存储桶 - IA)。在对象创建 4 年后删除这些⽂件。
D. 创建 S3 存储桶⽣命周期策略，在对象创建 30 天后将⽂件从 S3 标准存储桶移动到 S3 标准存储桶（不频
繁访问）（S3 标准存储桶-IA）。在对象创建 4 年后，将⽂件移动到 S3 Glacier 存储桶。
Question #67
Topic 1
⼀家公司在多个 Amazon EC2 实例上托管⼀个应⽤程序。该应⽤程序处理来⾃ Amazon SQS 队列的消息，将数
据写⼊ Amazon RDS 表，然后从队列中删除该消息。RDS 表中偶尔会出现重复记录。SQS 队列中不包含任何重
复消息。
解决⽅案架构师应该如何确保消息只被处理⼀次？
A. 使⽤ CreateQueue API 调⽤创建⼀个新队列。
B. 使⽤ AddPermission API 调⽤添加适当的权限。
C. 使⽤ ReceiveMessage API 调⽤来设置合适的等待时间。
D. 使⽤ ChangeMes sageVisibility API 调⽤来增加可⻅性超时时间。
https://examlearn.online
[2026/05]
Question #68
Topic 1
⼀位解决⽅案架构师正在设计⼀种新的混合架构，以将公司的本地基础设施扩展到 AWS。该公司需要与 AWS 区
域建⽴⾼可⽤性连接，并保持低延迟。该公司需要最⼤限度地降低成本，并且愿意在主连接发⽣故障时接受较低
的流量。
为了满⾜这些要求，解决⽅案架构师应该怎么做？
A. 建⽴与区域的 AWS Direct Connect 连接。如果主 Direct Connect 连接出现故障，则建⽴ VPN 连接作为
备⽤连接。
B. 为特定区域配置⼀条⽤于私有连接的 VPN 隧道。配置第⼆条 VPN 隧道，⽤于私有连接，并在主 VPN 连接
发⽣故障时作为备份。
C. 建⽴到区域的 AWS Direct Connect 连接。如果主 Direct Connect 连接发⽣故障，则建⽴到同⼀区域的第
⼆个 Direct Connect 连接作为备份。
D. 建⽴与区域的 AWS Direct Connect 连接。使⽤ AWS CLI 中的 Direct Connect 故障转移属性，以便在主
Direct Connect 连接发⽣故障时⾃动创建备份连接。
Question #69
PostgreSQL 跨区域复制。
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个业务关键型 Web 应⽤程序，该实例位于应⽤程序负载均衡器 (APP) 后
⽅。这些 EC2 实例位于⼀个⾃动扩展组中。该应⽤程序使⽤部署在单个可⽤区中的 Amazon Aurora
PostgreSQL 数据库。该公司希望该应⽤程序具有⾼可⽤性，并尽可能减少停机时间和数据丢失。
哪种解决⽅案能够以最⼩的运维⼯作量满⾜这些要求？
A. 将 EC2 实例放置在不同的 AWS 区域中。使⽤ Amazon Route 53 健康检查来重定向流量。使⽤ Aurora
B. 配置⾃动扩展组以使⽤多个可⽤区。将数据库配置为多可⽤区模式。为数据库配置 Amazon RDS 代理实
例。
C. 配置⾃动扩展组以使⽤⼀个可⽤区。每⼩时⽣成数据库快照。发⽣故障时，从快照恢复数据库。
D. 配置⾃动扩展组以使⽤多个 AWS 区域。将应⽤程序数据写⼊ Amazon S3。使⽤ S3 事件通知启动 AWS
Lambda 函数，将数据写⼊数据库。
https://examlearn.online
[2026/05]
Question #70
Topic 1
⼀家公司的 HTTP 应⽤程序位于⽹络负载均衡器 (NLB) 之后。NLB 的⽬标组配置为使⽤⼀个 Amazon EC2 Auto
Scaling 组，该组包含多个运⾏该 Web 服务的 EC2 实例。
该公司发现 NLB ⽆法检测到该应⽤程序的 HTTP 错误。这些错误需要⼿动重启运⾏该 Web 服务的 EC2 实例才
能解决。该公司需要在不编写⾃定义脚本或代码的情况下提⾼应⽤程序的可⽤性。
解决⽅案架构师应该如何满⾜这些要求？
A. 在 NLB 上启⽤ HTTP 健康检查，并提供公司应⽤程序的 URL。
B. 在 EC2 实例上添加⼀个定时任务，每分钟检查⼀次本地应⽤程序的⽇志。如果检测到 HTTP 错误，应⽤程
序将重新启动。
C. 将⽹络负载均衡器 (NLB) 替换为应⽤程序负载均衡器。通过提供公司应⽤程序的 URL 来启⽤ HTTP 健康
检查。配置⾃动扩展操作以替换不健康的实例。
D. 创建⼀个 Amazon CloudWatch 警报，⽤于监控 NLB 的 UnhealthyHostCount 指标。配置⼀个⾃动扩展
操作，以便在警报处于 ALARM 状态时替换不健康的实例。
Question #71
DynamoDB。
Topic 1
⼀家公司运营⼀款购物应⽤程序，该应⽤程序使⽤ Amazon DynamoDB 存储客户信息。如果发⽣数据损坏，解
决⽅案架构师需要设计⼀个解决⽅案，以满⾜ 15 分钟的恢复点⽬标 (RPO) 和 1 ⼩时的恢复时间⽬标 (RTO)。
解决⽅案架构师应该推荐什么⽅案来满⾜这些要求？
A. 配置 DynamoDB 全局表。为了实现 RPO 恢复，请将应⽤程序指向不同的 AWS 区域。
B. 配置 DynamoDB 时间点恢复。对于 RPO 恢复，将数据还原到所需的时间点。
C. 每⽇将 DynamoDB 数据导出到 Amazon S3 Glacier。为了实现 RPO 恢复，将数据从 S3 Glacier 导⼊到
D. 为 DynamoDB 表每 15 分钟设置⼀次 Amazon Elastic Block Store (Amazon EBS) 快照。对于 RPO 恢
复，请使⽤ EBS 快照还原 DynamoDB 表。
https://examlearn.online
[2026/05]
Question #72
Topic 1
⼀家公司运⾏⼀个照⽚处理应⽤程序，需要频繁地从位于同⼀ AWS 区域的 Amazon S3 存储桶上传和下载图⽚。
解决⽅案架构师注意到数据传输费⽤增加，需要实施⼀个解决⽅案来降低这些费⽤。
解决⽅案架构师该如何满⾜这⼀要求？
A. 将 Amazon API Gateway 部署到公共⼦⽹中，并调整路由表以通过它路由 S3 调⽤。
B. 在公共⼦⽹中部署 NAT ⽹关，并附加允许访问 S3 存储桶的端点策略。
C. 将应⽤程序部署到公共⼦⽹中，并允许其通过互联⽹⽹关路由以访问 S3 存储桶。
D. 在 VPC 中部署 S3 VPC ⽹关端点，并附加允许访问 S3 存储桶的端点策略。
Question #73
Topic 1
⼀家公司最近在私有⼦⽹的 Amazon EC2 上启动了基于 Linux 的应⽤程序实例，并在 VPC 的公有⼦⽹的
Amazon EC2 实例上启动了基于 Linux 的堡垒主机。解决⽅案架构师需要从公司内部⽹络经由公司互联⽹连接到
堡垒主机和应⽤程序服务器。解决⽅案架构师必须确保所有 EC2 实例的安全组都允许这种访问。
为了满⾜这些要求，解决⽅案架构师应该采取哪些步骤组合？（选择两项。）
A. 将堡垒主机的当前安全组替换为仅允许来⾃应⽤程序实例的⼊站访问的安全组。
B. 将堡垒主机的当前安全组替换为仅允许公司内部 IP 范围⼊站访问的安全组。
C. 将堡垒主机的当前安全组替换为仅允许公司外部 IP 范围⼊站访问的安全组。
D. 将应⽤程序实例的当前安全组替换为仅允许从堡垒主机的私有 IP 地址进⾏⼊站 SSH 访问的安全组。
E. 将应⽤程序实例的当前安全组替换为仅允许从堡垒主机的公共 IP 地址进⾏⼊站 SSH 访问的安全组。
https://examlearn.online
[2026/05]
Question #74
Topic 1
⼀位解决⽅案架构师正在设计⼀个两层 Web 应⽤程序。该应⽤程序包含⼀个⾯向公众的 Web 层，托管在
Amazon EC2 的公有⼦⽹中。数据库层由运⾏在 Amazon EC2 私有⼦⽹中的 Microsoft SQL Server 组成。安全
性是公司的⾸要任务。
在这种情况下，应该如何配置安全组？（选择两项。）
A. 配置 Web 层的安全组，允许来⾃ 0.0.0.0/0 的 443 端⼝⼊站流量。
B. 配置 Web 层的安全组，允许来⾃ 0.0.0.0/0 的 443 端⼝的出站流量。
C. 配置数据库层的安全组，允许来⾃ Web 层安全组的 1433 端⼝⼊站流量。
D. 配置数据库层的安全组，允许端⼝ 443 和 1433 上的出站流量到 Web 层的安全组。
E. 配置数据库层的安全组，允许来⾃ Web 层安全组的 443 和 1433 端⼝的⼊站流量。
Question #75
Topic 1
⼀家公司希望将⼀个多层应⽤程序从本地迁移到 AWS 云，以提升其性能。该应⽤程序由多个应⽤层组成，这些
应⽤层通过 RESTful 服务相互通信。当某⼀层过载时，事务就会被丢弃。解决⽅案架构师必须设计⼀个能够解决
这些问题并实现应⽤程序现代化的⽅案。
哪个⽅案既满⾜这些要求，⼜具有最⾼的运维效率？
A. 使⽤ Amazon API Gateway 并将事务直接发送到 AWS Lambda 函数作为应⽤层。使⽤ Amazon Simple
Queue Service (Amazon SQS) 作为应⽤服务之间的通信层。
B. 使⽤ Amazon CloudWatch 指标分析应⽤程序性能历史记录，以确定性能故障期间服务器的峰值利⽤率。
增加应⽤程序服务器的 Amazon EC2 实例的⼤⼩，以满⾜峰值需求。
C. 使⽤ Amazon Simple Notification Service (Amazon SNS) 处理运⾏在 Amazon EC2 上的应⽤程序服务
器之间的消息传递，这些服务器位于⾃动扩展组中。使⽤ Amazon CloudWatch 监控 SNS 队列⻓度，并根据
需要进⾏扩展或缩减。
D. 使⽤ Amazon Simple Queue Service (Amazon SQS) 处理运⾏在 Amazon EC2 上的应⽤程序服务器之间
的消息传递，这些服务器位于⾃动扩展组中。使⽤ Amazon CloudWatch 监控 SQS 队列⻓度，并在检测到通
信故障时进⾏扩展。
https://examlearn.online
[2026/05]
Question #76
Topic 1
⼀家公司每天从位于同⼀⼯⼚的多台机器接收 10 TB 的仪器数据。这些数据以 JSON ⽂件的形式存储在⼯⼚内部
数据中⼼的存储区域⽹络 (SAN) 上。该公司希望将这些数据发送到 Amazon S3，以便多个其他系统能够访问这
些数据，从⽽提供关键的近实时分析。由于数据被视为敏感信息，因此安全传输⾄关重要。
哪种解决⽅案能够提供最可靠的数据传输？
A. 通过公共互联⽹进⾏ AWS DataSync
B. 通过 AWS Direct Connect 进⾏ AWS DataSync
C. 通过公共互联⽹使⽤ AWS 数据库迁移服务 (AWS DMS)
D. 通过 AWS Direct Connect 使⽤ AWS 数据库迁移服务 (AWS DMS)
Question #77
Topic 1
⼀家公司需要为其应⽤程序配置实时数据采集架构。该公司需要⼀个 API、⼀个在数据流传输过程中转换数据的
流程以及⼀个数据存储解决⽅案。
哪种解决⽅案能够以最⼩的运维开销满⾜这些需求？
A. 部署⼀个 Amazon EC2 实例来托管⼀个 API，该 API 会将数据发送到 Amazon Kinesis 数据流。创建⼀个
Amazon Kinesis Data Firehose 传输流，并将 Kinesis 数据流⽤作数据源。使⽤ AWS Lambda 函数转换数
据。使⽤ Kinesis Data Firehose 传输流将数据发送到 Amazon S3。
B. 部署⼀个 Amazon EC2 实例来托管⼀个向 AWS Glue 发送数据的 API。停⽌ EC2 实例的源/⽬标检查。使
⽤ AWS Glue 转换数据并将其发送到 Amazon S3。
C. 配置 Amazon API Gateway API 以将数据发送到 Amazon Kinesis 数据流。创建使⽤ Kinesis 数据流作为
数据源的 Amazon Kinesis Data Firehose 传输流。使⽤ AWS Lambda 函数转换数据。使⽤ Kinesis Data
Firehose 传输流将数据发送到 Amazon S3。
D. 配置 Amazon API Gateway API 以将数据发送到 AWS Glue。使⽤ AWS Lambda 函数转换数据。使⽤
AWS Glue 将数据发送到 Amazon S3。
https://examlearn.online
[2026/05]
Question #78
⼀家公司需要将⽤户交易数据保存在 Amazon DynamoDB 表中，并且必须保留数据 7 年。
满⾜这些要求的最⾼效解决⽅案是什么？
A. 使⽤ DynamoDB 时间点恢复功能持续备份表。
B. 使⽤ AWS Backup 为该表创建备份计划和保留策略。
Topic 1
C. 使⽤ DynamoDB 控制台创建表的按需备份。将备份存储在 Amazon S3 存储桶中。为 S3 存储桶设置 S3
⽣命周期配置。
D. 创建⼀条 Amazon EventBridge（Amazon CloudWatch Events）规则以调⽤ AWS Lambda 函数。配置
Lambda 函数以备份表并将备份存储在 Amazon S3 存储桶中。为 S3 存储桶设置 S3 ⽣命周期配置。
Question #79
Topic 1
⼀家公司计划使⽤ Amazon DynamoDB 表进⾏数据存储。该公司⾮常关注成本优化。该表在⼤多数早晨不会被
使⽤。在晚上，读写流量通常难以预测。流量⾼峰出现时，会⾮常迅速。
解决⽅案架构师应该提出什么建议？
A. 以按需容量模式创建 DynamoDB 表。
B. 创建⼀个具有全局⼆级索引的 DynamoDB 表。
C. 创建⼀个具有预置容量和⾃动扩展功能的 DynamoDB 表。
D. 在预置容量模式下创建 DynamoDB 表，并将其配置为全局表。
https://examlearn.online
[2026/05]
Question #80
Topic 1
⼀家公司最近与⼀家 AWS 托管服务提供商 (MSP) 合作伙伴签订了合同，以协助其进⾏应⽤程序迁移。解决⽅案
架构师需要将现有 AWS 账户中的 Amazon 系统映像 (AMI) 共享给 MSP 合作伙伴的 AWS 账户。该 AMI 由
Amazon Elastic Block Store (Amazon EBS) 提供⽀持，并使⽤ AWS Key Management Service (AWS KMS) 客
户管理的密钥来加密 EBS 卷快照。
解决⽅案架构师与 MSP 合作伙伴的 AWS 账户共享 AMI 的最安全⽅式是什么？
A. 将加密的 AMI 和快照公开提供。修改密钥策略，允许 MSP 合作伙伴的 AWS 账户使⽤该密钥。
B. 修改 AMI 的 launchPermission 属性。仅与 MSP 合作伙伴的 AWS 账户共享该 AMI。修改密钥策略，允许
MSP 合作伙伴的 AWS 账户使⽤该密钥。
C. 修改 AMI 的 launchPermission 属性。仅与 MSP 合作伙伴的 AWS 账户共享此 AMI。修改密钥策略，使其
信任由 MSP 合作伙伴拥有的新 KMS 密钥进⾏加密。
D. 将源账户中的 AMI 导出到 MSP 合作伙伴 AWS 账户中的 Amazon S3 存储桶，使⽤ MSP 合作伙伴拥有的
新 KMS 密钥加密 S3 存储桶。复制 AMI 并在 MSP 合作伙伴的 AWS 账户中启动它。
Question #81
Topic 1
⼀位解决⽅案架构师正在为部署在 AWS 上的新应⽤程序设计云架构。该应⽤程序需要并⾏运⾏，并根据待处理
作业的数量按需添加和移除应⽤程序节点。处理器应⽤程序是⽆状态的。解决⽅案架构师必须确保应⽤程序松耦
合，并且作业项持久存储。
解决⽅案架构师应该采⽤哪种设计？
A. 创建⼀个 Amazon SNS 主题，⽤于发送需要处理的作业。创建⼀个包含处理器应⽤程序的 Amazon 系统
映像 (AMI)。创建⼀个使⽤该 AMI 的启动配置。使⽤该启动配置创建⼀个⾃动扩展组。设置⾃动扩展组的扩
展策略，使其根据 CPU 使⽤率添加和删除节点。
B. 创建⼀个 Amazon SQS 队列来存放需要处理的作业。创建⼀个包含处理器应⽤程序的 Amazon 系统映像
(AMI)。创建⼀个使⽤该 AMI 的启动配置。使⽤该启动配置创建⼀个⾃动扩展组。设置⾃动扩展组的扩展策
略，使其根据⽹络使⽤情况添加和删除节点。
C. 创建⼀个 Amazon SQS 队列来存放需要处理的作业。创建⼀个包含处理器应⽤程序的 Amazon 系统映像
(AMI)。创建⼀个使⽤该 AMI 的启动模板。使⽤该启动模板创建⼀个 Auto Scaling 组。设置 Auto Scaling 组
的扩展策略，使其根据 SQS 队列中的项⽬数来添加和删除节点。
D. 创建⼀个 Amazon SNS 主题，⽤于发送需要处理的作业。创建⼀个包含处理器应⽤程序的 Amazon 系统
映像 (AMI)。创建⼀个使⽤该 AMI 的启动模板。使⽤该启动模板创建⼀个 Auto Scaling 组。设置 Auto
Scaling 组的扩展策略，使其根据发布到 SNS 主题的消息数量来添加和删除节点。
https://examlearn.online
[2026/05]
Question #82
⼀家公司将其 Web 应⽤程序托管在 AWS 云上。该公司配置了弹性负载均衡器 (ELB) 以使⽤导⼊到 AWS
Certificate Manager (ACM) 中的证书。该公司的安全团队必须在每个证书到期前 30 天收到通知。
解决⽅案架构师应该推荐什么⽅案来满⾜此要求？
Topic 1
A. 在 ACM 中添加⼀条规则，从任何证书到期前 30 天开始，每天向 Amazon Simple Notification Service
(Amazon SNS) 主题发布⾃定义消息。
B. 创建⼀个 AWS Config 规则，检查 30 天内即将过期的证书。配置 Amazon EventBridge（Amazon
CloudWatch Events），以便在 AWS Config 报告不合规资源时，通过 Amazon Simple Notification Service
（Amazon SNS）触发⾃定义警报。
C. 使⽤ AWS Trusted Advisor 检查 30 天内即将过期的证书。创建⼀个基于 Trusted Advisor 指标的
Amazon CloudWatch 警报，⽤于检查状态变化。配置该警报，使其通过 Amazon Simple Notification
Service (Amazon SNS) 发送⾃定义警报。
Question #83
D. 创建⼀条 Amazon EventBridge（Amazon CloudWatch Events）规则，⽤于检测任何将在 30 天内过期
的证书。配置该规则以调⽤ AWS Lambda 函数。配置该 Lambda 函数以通过 Amazon Simple Notification
Service（Amazon SNS）发送⾃定义警报。
Topic 1
⼀家公司的动态⽹站托管在美国的本地服务器上。该公司即将在欧洲推出产品，并希望优化欧洲新⽤户的⽹站加
载速度。⽹站的后端必须保留在美国。产品将在⼏天后上线，因此需要⽴即找到解决⽅案。
解决⽅案架构师应该提出什么建议？
A. 在 us-east-1 区域启动 Amazon EC2 实例，并将⽹站迁移到该实例。
B. 将⽹站迁移到 Amazon S3。使⽤跨区域复制。
C. 使⽤ Amazon CloudFront，并⾃定义源指向本地服务器。
D. 使⽤指向本地服务器的 Amazon Route 53 地理位置路由策略。
https://examlearn.online
[2026/05]
Question #84
Topic 1
⼀家公司希望降低其现有三层 Web 架构的成本。Web 服务器、应⽤服务器和数据库服务器分别运⾏在 Amazon
EC2 实例上，⽤于开发、测试和⽣产环境。EC2 实例在⾼峰时段的平均 CPU 利⽤率为 30%，在⾮⾼峰时段的平
均 CPU 利⽤率为 10%。
⽣产环境的 EC2 实例 24 ⼩时运⾏。开发和测试环境的 EC2 实例每天⾄少运⾏ 8 ⼩时。该公司计划实施⾃动化
流程，在开发和测试环境的 EC2 实例不使⽤时⾃动停⽌它们。
哪种 EC2 实例购买⽅案能够以最具成本效益的⽅式满⾜该公司的需求？
A. ⽣产环境的 EC2 实例请使⽤竞价型实例。开发和测试环境的 EC2 实例请使⽤预留实例。
B. ⽣产环境的 EC2 实例请使⽤预留实例。开发和测试环境的 EC2 实例请使⽤按需实例。
C. ⽣产环境的 EC2 实例使⽤竞价型实例。开发和测试环境的 EC2 实例使⽤预留实例。
D. ⽣产环境的 EC2 实例使⽤按需实例，开发和测试环境的 EC2 实例使⽤竞价型实例。
Question #85
Topic 1
⼀家公司有⼀个⽣产环境的Web应⽤程序，⽤户可以通过Web界⾯或移动应⽤程序上传⽂档。根据⼀项新的监管
要求，新⽂档⼀旦存储就不能修改或删除。
解决⽅案架构师应该如何满⾜这⼀要求？
A. 将上传的⽂档存储在启⽤了 S3 版本控制和 S3 对象锁定的 Amazon S3 存储桶中。
B. 将上传的⽂档存储在 Amazon S3 存储桶中。配置 S3 ⽣命周期策略，定期归档⽂档。
C. 将上传的⽂档存储在启⽤了 S3 版本控制功能的 Amazon S3 存储桶中。配置访问控制列表 (ACL) 以限制
所有访问权限为只读。
D. 将上传的⽂档存储在 Amazon Elastic File System (Amazon EFS) 卷上。通过以只读模式挂载该卷来访问
数据。
https://examlearn.online
[2026/05]
Question #86
Topic 1
⼀家公司有多台 Web 服务器需要频繁访问同⼀个 Amazon RDS MySQL 多可⽤区数据库实例。该公司希望找到
⼀种安全的数据库连接⽅式，同时满⾜频繁轮换⽤户凭证的安全要求。
哪种解决⽅案能够满⾜这些要求？
A. 将数据库⽤户凭证存储在 AWS Secrets Manager 中。授予必要的 IAM 权限，以允许 Web 服务器访问
AWS Secrets Manager。
B. 将数据库⽤户凭证存储在 AWS Systems Manager OpsCenter 中。授予必要的 IAM 权限，以允许 Web 服
务器访问 OpsCenter。
C. 将数据库⽤户凭证存储在安全的 Amazon S3 存储桶中。授予必要的 IAM 权限，以允许 Web 服务器检索
凭证并访问数据库。
D. 将数据库⽤户凭证存储在使⽤ AWS Key Management Service (AWS KMS) 加密的⽂件中，并放置在
Web 服务器⽂件系统上。Web 服务器应能够解密这些⽂件并访问数据库。
Question #87
Topic 1
⼀家公司在 AWS Lambda 函数上托管了⼀个应⽤程序，这些函数通过 Amazon API Gateway API 调⽤。
Lambda 函数会将客户数据保存到 Amazon Aurora MySQL 数据库中。每当该公司升级数据库时，Lambda 函数
都⽆法建⽴数据库连接，直到升级完成。结果是，部分事件的客户数据⽆法被记录。
解决⽅案架构师需要设计⼀个解决⽅案来存储数据库升级期间创建的客户数据。
哪个解决⽅案能够满⾜这些要求？
A. 配置⼀个 Amazon RDS 代理，使其位于 Lambda 函数和数据库之间。配置 Lambda 函数以连接到 RDS 代
理。
B. 将 Lambda 函数的运⾏时间增加到最⼤值。在将客户数据存储到数据库的代码中创建重试机制。
C. 将客户数据持久化到 Lambda 本地存储。配置新的 Lambda 函数以扫描本地存储并将客户数据保存到数据
库。
D. 将客户数据存储在 Amazon Simple Queue Service (Amazon SQS) FIFO 队列中。创建⼀个新的 Lambda
函数，该函数轮询队列并将客户数据存储到数据库中。
https://examlearn.online
[2026/05]
Question #88
Topic 1
⼀家调查公司多年来⼀直在收集美国各地的数据。该公司将数据存储在容量为 3 TB 且仍在增⻓的 Amazon S3 存
储桶中。该公司已开始与⼀家拥有 S3 存储桶的欧洲营销公司共享数据。该公司希望确保数据传输成本尽可能
低。
哪种解决⽅案能够满⾜这些要求？
A. 在公司的 S3 存储桶上配置请求者付费功能。
B. 配置公司 S3 存储桶到营销公司 S3 存储桶之⼀的 S3 跨区域复制。
C. 为营销公司配置跨账户访问权限，以便营销公司可以访问公司的 S3 存储桶。
D. 配置公司的 S3 存储桶以使⽤ S3 智能分层。将该 S3 存储桶与营销公司的⼀个 S3 存储桶同步。
Question #89
Topic 1
⼀家公司使⽤ Amazon S3 存储其机密审计⽂档。S3 存储桶采⽤存储桶策略，根据最⼩权限原则限制对审计团队
IAM ⽤户凭证的访问。公司管理层担⼼ S3 存储桶中的⽂档会被意外删除，因此希望找到更安全的解决⽅案。
解决⽅案架构师应该如何保护这些审计⽂档？
A. 在 S3 存储桶上启⽤版本控制和 MFA 删除功能。
B. 为每个审计团队 IAM ⽤户帐户启⽤ IAM ⽤户凭据的多因素身份验证 (MFA)。
C. 在审计团队的 IAM ⽤户帐户中添加 S3 ⽣命周期策略，以在审计⽇期期间拒绝 s3:DeleteObject 操作。
D. 使⽤ AWS Key Management Service (AWS KMS) 对 S3 存储桶进⾏加密，并限制审计团队 IAM ⽤户帐户
访问 KMS 密钥。
https://examlearn.online
[2026/05]
Question #90
Topic 1
⼀家公司使⽤ SQL 数据库存储可公开访问的电影数据。该数据库运⾏在 Amazon RDS 单可⽤区数据库实例上。
⼀个脚本每天随机运⾏查询，记录数据库中新增电影的数量。该脚本必须在⼯作时间内报告最终总数。
公司开发团队注意到，当脚本运⾏时，数据库性能不⾜以满⾜开发任务的需求。解决⽅案架构师必须推荐⼀个解
决⽅案来解决此问题。
哪个解决⽅案能够在满⾜此要求的同时，将运维开销降⾄最低？
A. 将数据库实例修改为多可⽤区部署。
B. 创建数据库的只读副本。配置脚本，使其仅查询该只读副本。
C. 指示开发团队每天结束时⼿动导出数据库中的条⽬。
D. 使⽤ Amazon ElastiCache 缓存脚本针对数据库运⾏的常⽤查询。
Question #91
⼀家公司在 VPC 中的 Amazon EC2 实例上运⾏多个应⽤程序。其中⼀个应⽤程序需要调⽤ Amazon S3 API 来
存储和读取对象。根据公司的安全规定，不允许应⽤程序的任何流量通过互联⽹传输。
哪种解决⽅案能够满⾜这些要求？
A. 配置 S3 ⽹关端点。
B. 在私有⼦⽹中创建 S3 存储桶。
C. 在与 EC2 实例相同的 AWS 区域中创建 S3 存储桶。
D. 在与 EC2 实例相同的⼦⽹中配置 NAT ⽹关。
Question #92
Topic 1
Topic 1
⼀家公司将敏感⽤户信息存储在 Amazon S3 存储桶中。该公司希望从运⾏在 VPC 内 Amazon EC2 实例上的应
⽤层安全地访问该存储桶。
解决⽅案架构师应采取哪些步骤组合来实现此⽬标？（选择两项。）
A. 在 VPC 内为 Amazon S3 配置 VPC ⽹关终端节点。
B. 创建存储桶策略，使 S3 存储桶中的对象公开。
C. 创建⼀个存储桶策略，将访问权限限制在 VPC 中运⾏的应⽤程序层。
D. 创建⼀个具有 S3 访问策略的 IAM ⽤户，并将 IAM 凭证复制到 EC2 实例。
E. 创建⼀个 NAT 实例，并让 EC2 实例使⽤该 NAT 实例访问 S3 存储桶。
https://examlearn.online
[2026/05]
Question #93
Topic 1
⼀家公司运⾏着⼀个基于 MySQL 数据库的本地应⽤程序。该公司正在将该应⽤程序迁移到 AWS，以提⾼其弹性
和可⽤性。
当前架构在正常运⾏期间数据库读取活动⾮常频繁。公司开发团队每隔 4 ⼩时会从⽣产环境数据库导出完整数
据，并将其填充到测试环境中的数据库。在此期间，⽤户会遇到⽆法接受的应⽤程序延迟。在导出过程完成之
前，开发团队⽆法使⽤测试环境。
解决⽅案架构师必须推荐⼀种能够缓解应⽤程序延迟问题的替代架构。此外，该替代架构还必须确保开发团队能
够继续⽆延迟地使⽤测试环境。
哪种解决⽅案满⾜这些要求？
A. ⽣产环境使⽤配备多可⽤区 Aurora 副本的 Amazon Aurora MySQL。通过使⽤ mysqldump ⼯具实施备份
和恢复流程来填充暂存数据库。
B. ⽣产环境使⽤配备多可⽤区 Aurora 副本的 Amazon Aurora MySQL。使⽤数据库克隆按需创建暂存数据
库。
C. 使⽤ Amazon RDS for MySQL 进⾏多可⽤区部署，并为⽣产环境配置只读副本。将备⽤实例⽤于暂存数
据库。
D. 使⽤ Amazon RDS for MySQL，采⽤多可⽤区部署，并为⽣产环境配置只读副本。通过使⽤ mysqldump
⼯具实施备份和恢复流程来填充暂存数据库。
Question #94
在 Amazon Aurora 数据库集群中。
Topic 1
⼀家公司正在设计⼀个应⽤程序，⽤户可以通过该程序将⼩⽂件上传到 Amazon S3。⽤户上传⽂件后，需要对⽂
件进⾏⼀次性的简单处理，以转换数据并将其保存为 JSON 格式，供后续分析。
每个⽂件上传后都必须尽快处理。需求会波动。有些⽇⼦⽤户会上传⼤量⽂件，⽽有些⽇⼦⽤户可能只上传少量
⽂件甚⾄不上传⽂件。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 配置 Amazon EMR 以从 Amazon S3 读取⽂本⽂件。运⾏处理脚本以转换数据。将⽣成的 JSON ⽂件存储
B. 配置 Amazon S3 向 Amazon Simple Queue Service (Amazon SQS) 队列发送事件通知。使⽤ Amazon
EC2 实例从队列中读取数据并进⾏处理。将⽣成的 JSON ⽂件存储在 Amazon DynamoDB 中。
C. 配置 Amazon S3 向 Amazon Simple Queue Service (Amazon SQS) 队列发送事件通知。使⽤ AWS
Lambda 函数从队列中读取数据并进⾏处理。将⽣成的 JSON ⽂件存储在 Amazon DynamoDB 中。
D. 配置 Amazon EventBridge（Amazon CloudWatch Events），使其在上传新⽂件时向 Amazon Kinesis
Data Streams 发送事件。使⽤ AWS Lambda 函数从数据流中获取事件并处理数据。将⽣成的 JSON ⽂件存
储在 Amazon Aurora 数据库集群中。
https://examlearn.online
[2026/05]
Question #95
⼀款应⽤程序允许公司总部的⽤户访问产品数据。产品数据存储在 Amazon RDS MySQL 数据库实例中。运维团
队已发现应⽤程序性能下降的原因，并希望将读取流量与写⼊流量分离。解决⽅案架构师需要快速优化应⽤程序
性能。
他应该提出什么建议？
A. 将现有数据库更改为多可⽤区部署。从主可⽤区处理读取请求。
Topic 1
B. 将现有数据库更改为多可⽤区部署。从辅助可⽤区处理读取请求。
C. 为数据库创建只读副本。将只读副本配置为拥有源数据库⼀半的计算和存储资源。
D. 为数据库创建只读副本。配置只读副本，使其拥有与源数据库相同的计算和存储资源。
https://examlearn.online
[2026/05]
Question #96
Amazon EC2 管理员创建了以下策略，该策略与包含多个⽤户的 IAM 组相关联：
Topic 1
此策略会产⽣什么影响？
A. ⽤户可以终⽌除 us-east-1 区域以外的任何 AWS 区域中的 EC2 实例。
B. ⽤户可以终⽌位于 us-east-1 区域的 IP 地址为 10.100.100.1 的 EC2 实例。
C. 当⽤户的源 IP 为 10.100.100.254 时，⽤户可以在 us-east-1 区域中终⽌ EC2 实例。
D. 当⽤户的源 IP 为 10.100.100.254 时，⽤户⽆法在 us-east-1 区域中终⽌ EC2 实例。
https://examlearn.online
[2026/05]
Question #97
Topic 1
⼀家公司在本地部署了庞⼤的 Microsoft SharePoint 服务，需要使⽤ Microsoft Windows 共享⽂件存储。该公
司希望将此⼯作负载迁移到 AWS 云，并正在考虑各种存储⽅案。该存储解决⽅案必须具备⾼可⽤性，并与
Active Directory 集成以实现访问控制。
哪种解决⽅案能够满⾜这些要求？
A. 配置 Amazon EFS 存储并设置 Active Directory 域以进⾏身份 验证。
B. 在两个可⽤区中的 AWS Storage Gateway ⽂件⽹关上创建 SMB ⽂件共享。
C. 创建⼀个 Amazon S3 存储桶，并将 Microsoft Windows Server 配置为将其挂载为卷。
D. 在 AWS 上创建 Amazon FSx for Windows ⽂件服务器⽂件系统，并设置 Active Directory 域进⾏身份验
证。
Question #98
Topic 1
⼀家图像处理公司有⼀个供⽤户上传图像的 Web 应⽤程序。该应⽤程序会将图像上传到 Amazon S3 存储桶。该
公司已设置 S3 事件通知，将对象创建事件发布到 Amazon Simple Queue Service (Amazon SQS) 标准队列。
SQS 队列作为 AWS Lambda 函数的事件源，该函数处理图像并将结果通过电⼦邮件发送给⽤户。
⽤户反映，他们收到的每张上传图像都会收到多封电⼦邮件。解决⽅案架构师确定，SQS 消息会多次调⽤
Lambda 函数，从⽽导致发送多封电⼦邮件。
解决⽅案架构师应该如何以最⼩的运维开销解决此问题？
A. 通过将 ReceiveMessage 等待时间增加到 30 秒，在 SQS 队列中设置⻓轮询。
B. 将 SQS 标准队列更改为 SQS FIFO 队列。使⽤消息去重 ID 丢弃重复消息。
C. 将 SQS 队列中的可⻅性超时时间增加到⼤于函数超时时间和批处理窗⼝超时时间之和的值。
D. 修改 Lambda 函数，使其在处理消息之前，读取消息后⽴即从 SQS 队列中删除每条消息。
https://examlearn.online
[2026/05]
Question #99
Topic 1
⼀家公司正在为其托管在本地数据中⼼的游戏应⽤程序部署共享存储解决⽅案。该公司需要能够使⽤ Lustre 客户
端访问数据。该解决⽅案必须是完全托管的。
哪种解决⽅案满⾜这些要求？
A. 创建 AWS Storage Gateway ⽂件⽹关。创建使⽤所需客户端协议的⽂件共享。将应⽤程序服务器连接到
该⽂件共享。
B. 创建⼀个 Amazon EC2 Windows 实例。在该实例上安装并配置 Windows ⽂件共享⻆⾊。将应⽤程序服务
器连接到该⽂件共享。
C. 创建⼀个 Amazon Elastic File System (Amazon EFS) ⽂件系统，并将其配置为⽀持 Lustre。将该⽂件系
统附加到源服务器。将应⽤程序服务器连接到该⽂件系统。
D. 创建⼀个 Amazon FSx for Lustre ⽂件系统。将该⽂件系统连接到源服务器。将应⽤服务器连接到该⽂件
系统。
Question #100
Topic 1
⼀家公司的容器化应⽤程序运⾏在 Amazon EC2 实例上。该应⽤程序需要下载安全证书才能与其他业务应⽤程序
通信。该公司需要⼀个⾼度安全的解决⽅案，以近乎实时的⽅式加密和解密证书。此外，该解决⽅案还需要在数
据加密后将其存储在⾼可⽤性存储中。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为加密证书创建 AWS Secrets Manager 密钥。根据需要⼿动更新证书。使⽤细粒度的 IAM 访问权限控制
对数据的访问。
B. 创建⼀个使⽤ Python 加密库来接收和执⾏加密操作的 AWS Lambda 函数。将该函数存储在 Amazon S3
存储桶中。
C. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。允许 EC2 ⻆⾊使⽤该 KMS 密钥进⾏加
密操作。将加密数据存储在 Amazon S3 上。
D. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。允许 EC2 ⻆⾊使⽤该 KMS 密钥进⾏加
密操作。将加密数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷上。
https://examlearn.online
[2026/05]
Question #101
Topic 1
解决⽅案架构师正在设计⼀个包含公有⼦⽹和私有⼦⽹的 VPC。该 VPC 和⼦⽹使⽤ IPv4 CIDR 块。为了实现⾼
可⽤性，三个可⽤区 (AZ) 中每个可⽤区都包含⼀个公有⼦⽹和⼀个私有⼦⽹。公有⼦⽹通过互联⽹⽹关访问互联
⽹。私有⼦⽹需要访问互联⽹才能让 Amazon EC2 实例下载软件更新。
解决⽅案架构师应该如何为私有⼦⽹启⽤互联⽹访问？
A. 为每个可⽤区 (AZ) 中的每个公有⼦⽹创建三个 NAT ⽹关。为每个可⽤区创建⼀个私有路由表，将⾮ VPC
流量转发到其可⽤区中的 NAT ⽹关。
B. 创建三个 NAT 实例，每个可⽤区 (AZ) 中的每个私有⼦⽹⼀个。为每个可⽤区创建⼀个私有路由表，将⾮
VPC 流量转发到其可⽤区中的 NAT 实例。
C. 在其中⼀个私有⼦⽹上创建第⼆个互联⽹⽹关。更新私有⼦⽹的路由表，将⾮ VPC 流量转发到该私有互联
⽹⽹关。
D. 在其中⼀个公有⼦⽹上创建⼀个仅供出站流量使⽤的互联⽹⽹关。更新私有⼦⽹的路由表，将⾮ VPC 流量
转发到该仅供出站流量使⽤的互联⽹⽹关。
Question #102
Topic 1
⼀家公司希望将本地数据中⼼迁移到 AWS。该数据中⼼托管着⼀台 SFTP 服务器，其数据存储在基于 NFS 的⽂
件系统上。该服务器存储着 200 GB 的数据，需要进⾏迁移。该服务器必须托管在使⽤ Amazon Elastic File
System (Amazon EFS) ⽂件系统的 Amazon EC2 实例上。
解决⽅案架构师应该采取哪些步骤组合来实现此任务的⾃动化？（选择两项。）
A. 将 EC2 实例启动到与 EFS ⽂件系统相同的可⽤区。
B. 在本地数据中⼼安装 AWS DataSync 代理。
C. 在 EC2 实例上为数据创建辅助 Amazon Elastic Block Store (Amazon EBS) 卷。
D. ⼿动使⽤操作系统复制命令将数据推送到 EC2 实例。
E. 使⽤ AWS DataSync 为本地 SFTP 服务器创建合适的位置配置。
https://examlearn.online
[2026/05]
Question #103
Topic 1
⼀家公司有⼀个 AWS Glue 提取、转换和加载 (ETL) 作业，每天同⼀时间运⾏。该作业处理存储在 Amazon S3
存储桶中的 XML 数据。每天都有新数据添加到 S3 存储桶中。解决⽅案架构师注意到，AWS Glue 在每次运⾏时
都会处理所有数据。
解决⽅案架构师应该如何做才能防⽌ AWS Glue 重复处理旧数据？
A. 编辑职位以使⽤职位书签。
B. 编辑作业，在数据处理完成后删除数据。
C. 将 NumberOfWorkers 字段设置为 1，从⽽编辑该作业。
D. 使⽤ FindMatches 机器学习 (ML) 转换。
Question #104
Topic 1
解决⽅案架构师需要为⽹站设计⾼可⽤性基础架构。该⽹站由运⾏在 Amazon EC2 实例上的 Windows Web 服
务器提供⽀持。解决⽅案架构师必须实施⼀个能够缓解来⾃数千个 IP 地址的⼤规模 DDoS 攻击的解决⽅案。⽹站
停机是不可接受的。
解决⽅案架构师应该采取哪些措施来保护⽹站免受此类攻击？（选择两项。）
A. 使⽤ AWS Shield Advanced 阻⽌ DDoS 攻击。
B. 配置 Amazon GuardDuty ⾃动阻⽌攻击者。
C. 配置⽹站以使⽤ Amazon CloudFront 来处理静态和动态内容。
D. 使⽤ AWS Lambda 函数⾃动将攻击者 IP 地址添加到 VPC ⽹络 ACL 中。
E. 在⾃动扩展组中使⽤ EC2 Spot 实例，并将⽬标跟踪扩展策略设置为 80% CPU 利⽤率。
https://examlearn.online
[2026/05]
Question #105
Topic 1
⼀家公司正准备部署⼀个新的⽆服务器⼯作负载。解决⽅案架构师必须遵循最⼩权限原则来配置运⾏ AWS
Lambda 函数所需的权限。该函数将通过 Amazon EventBridge（Amazon CloudWatch Events）规则调⽤。
哪种解决⽅案满⾜这些要求？
A. 为函数添加执⾏⻆⾊，操作为 lambda:InvokeFunction，主体为 *。
B. 为函数添加执⾏⻆⾊，操作为 lambda:InvokeFunction，主体为 Service: lambda.amazonaws.com。
C. 向函数添加基于资源的策略，其中 lambda:* 作为操作，Service: events.amazonaws.com 作为主体。
D. 向函数添加基于资源的策略，其中 lambda:InvokeFunction 为操作，Service: events.amazonaws.com
为主体。
Question #106
⼀家公司准备将机密数据存储在 Amazon S3 中。出于合规性考虑，数据必须进⾏静态加密。加密密钥的使⽤情
况必须记录以备审计。密钥必须每年轮换⼀次。
哪种解决⽅案既满⾜这些要求，⼜具有最⾼的运⾏效率？
A. 使⽤客户提供的密钥进⾏服务器端加密 (SSE-C)
B. 使⽤ Amazon S3 管理密钥的服务器端加密 (SSE-S3)
C. 使⽤ AWS KMS 密钥进⾏服务器端加密 (SSE-KMS)，并⼿动轮换密钥。
D. 使⽤ AWS KMS 密钥的服务器端加密 (SSE-KMS)，并启⽤⾃动轮换
Question #107
Topic 1
Topic 1
⼀家共享单⻋公司正在开发⼀种多层架构，⽤于在⾼峰运营时段追踪单⻋位置。该公司希望在其现有的分析平台
中使⽤这些数据点。解决⽅案架构师必须确定⽀持此架构的最可⾏的多层⽅案。这些数据点必须能够通过 REST
API 访问。
以下哪个操作满⾜存储和检索位置数据的这些要求？
A. 将 Amazon Athena 与 Amazon S3 结合使⽤。
B. 将 Amazon API Gateway 与 AWS Lambda 结合使⽤。
C. 将 Amazon QuickSight 与 Amazon Redshift 结合使⽤。
D. 将 Amazon API Gateway 与 Amazon Kinesis Data Analytics 结合使⽤。
https://examlearn.online
[2026/05]
Question #108
Topic 1
⼀家公司拥有⼀个汽⻋销售⽹站，该⽹站将⻋辆信息存储在 Amazon RDS 数据库中。当⻋辆售出后，需要从⽹站
上删除该⻋辆信息，并将数据发送到多个⽬标系统。
解决⽅案架构师应该推荐哪种设计⽅案？
A. 创建⼀个 AWS Lambda 函数，当 Amazon RDS 上的数据库更新时触发该函数，将信息发送到 Amazon
Simple Queue Service (Amazon SQS) 队列，供⽬标使⽤。
B. 创建⼀个 AWS Lambda 函数，当 Amazon RDS 上的数据库更新时触发该函数，将信息发送到 Amazon
Simple Queue Service (Amazon SQS) FIFO 队列，供⽬标使⽤。
C. 订阅 RDS 事件通知，并将 Amazon Simple Queue Service (Amazon SQS) 队列分发到多个 Amazon
Simple Notification Service (Amazon SNS) 主题。使⽤ AWS Lambda 函数更新⽬标。
D. 订阅 RDS 事件通知，并将 Amazon Simple Notification Service (Amazon SNS) 主题分发到多个
Amazon Simple Queue Service (Amazon SQS) 队列。使⽤ AWS Lambda 函数更新⽬标。
Question #109
Topic 1
⼀家公司需要在 Amazon S3 中存储数据，并且必须防⽌数据被更改。该公司希望上传到 Amazon S3 的新对象
在⼀段时间内保持不可更改状态，直到公司决定修改这些对象为⽌。只有公司 AWS 账户中的特定⽤户才有权删
除这些对象。
解决⽅案架构师应该如何满⾜这些要求？
A. 创建⼀个 S3 Glacier 存储库。对对象应⽤⼀次写⼊多次读取 (WORM) 存储库锁定策略。
B. 创建⼀个启⽤ S3 对象锁定的 S3 存储桶。启⽤版本控制。设置保留期为 100 年。将治理模式设置为 S3 存
储桶新对象的默认保留模式。
C. 创建⼀个 S3 存储桶。使⽤ AWS CloudTrail 跟踪任何修改对象的 S3 API 事件。收到通知后，从公司拥有
的任何备份版本中恢复已修改的对象。
D. 创建⼀个启⽤ S3 对象锁定的 S3 存储桶。启⽤版本控制。为对象添加法律保留。将
s3:PutObjectLegalHold 权限添加到需要删除对象的⽤户的 IAM 策略中。
https://examlearn.online
[2026/05]
Question #110
Topic 1
⼀家社交媒体公司允许⽤户上传图⽚到其⽹站。该⽹站运⾏在 Amazon EC2 实例上。在上传请求期间，⽹站会将
图⽚调整为标准尺⼨，并将调整后的图⽚存储在 Amazon S3 中。⽤户反映上传速度较慢。
该公司需要降低应⽤程序内部的耦合度并提⾼⽹站性能。解决⽅案架构师必须设计出运营效率最⾼的图⽚上传流
程。
为了满⾜这些要求，解决⽅案架构师应该采取哪些措施组合？（选择两项。）
A. 配置应⽤程序将图像上传到 S3 Glacier。
B. 配置 Web 服务器将原始图像上传到 Amazon S3。
C. 配置应⽤程序，使其能够通过使⽤预签名 URL，直接从每个⽤户的浏览器将图像上传到 Amazon S3。
D. 配置 S3 事件通知，以便在上传图像时调⽤ AWS Lambda 函数。使⽤该函数调整图像⼤⼩。
E. 创建⼀个 Amazon EventBridge（Amazon CloudWatch Events）规则，按计划调⽤ AWS Lambda 函数
来调整上传图像的⼤⼩。
Question #111
MySQL 数据库复制到另⼀个可⽤区。
Topic 1
⼀家公司最近将消息处理系统迁移到了 AWS。该系统接收消息到运⾏在 Amazon EC2 实例上的 ActiveMQ 队列
中。消息由运⾏在 Amazon EC2 上的消费者应⽤程序处理。消费者应⽤程序处理消息并将结果写⼊运⾏在
Amazon EC2 上的 MySQL 数据库。该公司希望该应⽤程序具有⾼可⽤性和低运维复杂度。
哪种架构能够提供最⾼的可⽤性？
A. 在另⼀个可⽤区添加第⼆个 ActiveMQ 服务器。在另⼀个可⽤区添加⼀个额外的消费者 EC2 实例。将
B. 使⽤ Amazon MQ，并在两个可⽤区配置主备代理。在另⼀个可⽤区添加⼀个额外的消费者 EC2 实例。将
MySQL 数据库复制到另⼀个可⽤区。
C. 使⽤配置了跨两个可⽤区的主备代理的 Amazon MQ。在另⼀个可⽤区中添加⼀个额外的消费者 EC2 实
例。使⽤启⽤了多可⽤区功能的 Amazon RDS for MySQL。
D. 使⽤ Amazon MQ，并在两个可⽤区配置主备代理。为跨两个可⽤区的消费者 EC2 实例添加⾃动扩展组。
使⽤启⽤多可⽤区功能的 Amazon RDS for MySQL。
https://examlearn.online
[2026/05]
Question #112
Topic 1
⼀家公司在本地服务器上托管了⼀个容器化的 Web 应⽤程序，这些服务器⽤于处理传⼊的请求。请求数量正在快
速增⻓，本地服务器⽆法处理不断增加的请求。该公司希望将应⽤程序迁移到 AWS，并尽可能减少代码更改和开
发⼯作量。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ Amazon Elastic Container Service (Amazon ECS) 上的 AWS Fargate 来运⾏容器化的 Web 应⽤程
序，并启⽤服务⾃动扩展。使⽤应⽤程序负载均衡器来分发传⼊的请求。
B. 使⽤两个 Amazon EC2 实例来托管容器化的 Web 应⽤程序。使⽤应⽤程序负载均衡器来分发传⼊的请
求。
C. 使⽤ AWS Lambda，并编写使⽤受⽀持编程语⾔之⼀的新代码。创建多个 Lambda 函数来应对负载。使
⽤ Amazon API Gateway 作为 Lambda 函数的⼊⼝点。
D. 使⽤⾼性能计算 (HPC) 解决⽅案，例如 AWS ParallelCluster，建⽴⼀个 HPC 集群，以适当的规模处理传
⼊的请求。
Question #113
业以使其在 AWS 云中继续运⾏。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司使⽤ 50 TB 的数据进⾏报表⽣成。该公司希望将这些数据从本地迁移到 AWS 云平台。该公司数据中⼼
的⼀个⾃定义应⽤程序每周运⾏⼀次数据转换作业。该公司计划暂停该应⽤程序，直到数据传输完成，因此需要
尽快启动传输过程。
数据中⼼没有可⽤的⽹络带宽来⽀持额外的⼯作负载。解决⽅案架构师必须完成数据传输，并且必须配置转换作
A. 使⽤ AWS DataSync 迁移数据。使⽤ AWS Glue 创建⾃定义转换作业。
B. 订购⼀台 AWS Snowcone 设备来传输数据。将转换应⽤程序部署到该设备上。
C. 订购⼀台 AWS Snowball Edge Storage Optimized 设备。将数据复制到该设备。使⽤ AWS Glue 创建⾃
定义转换作业。
D. 订购⼀台包含 Amazon EC2 计算资源的 AWS Snowball Edge Storage Optimized 设备。将数据复制到该
设备。在 AWS 上创建⼀个新的 EC2 实例来运⾏转换应⽤程序。
https://examlearn.online
[2026/05]
Question #114
Topic 1
⼀家公司开发了⼀款图像分析应⽤程序，⽤户可以上传照⽚并添加相框。⽤户上传照⽚时会同时上传元数据，以
指定要添加的相框。该应⽤程序使⽤单个 Amazon EC2 实例和 Amazon DynamoDB 来存储元数据。
随着应⽤程序越来越受欢迎，⽤户数量也在不断增⻓。公司预计并发⽤户数量会因⼀天中的不同时间和⼀周中的
不同⽇期⽽显著变化。公司必须确保应⽤程序能够扩展以满⾜不断增⻓的⽤户群的需求。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Lambda 处理照⽚。将照⽚和元数据存储在 DynamoDB 中。
B. 使⽤ Amazon Kinesis Data Firehose 处理照⽚并存储照⽚和元数据。
C. 使⽤ AWS Lambda 处理照⽚。将照⽚存储在 Amazon S3 中。保留 DynamoDB ⽤于存储元数据。
D. 将 EC2 实例数量增加到三个。使⽤预置 IOPS SSD (io2) Amazon Elastic Block Store (Amazon EBS) 卷
来存储照⽚和元数据。
Question #115
Topic 1
⼀家医疗记录公司在 Amazon EC2 实例上托管了⼀个应⽤程序。该应⽤程序处理存储在 Amazon S3 上的客户数
据⽂件。这些 EC2 实例托管在公共⼦⽹中。EC2 实例通过互联⽹访问 Amazon S3，但不需要任何其他⽹络访问
权限。现在
⼀项新要求规定，⽂件传输的⽹络流量必须⾛私有路径，⽽不能通过互联⽹传输。
为了满⾜此要求，解决⽅案架构师应该建议对⽹络架构进⾏哪项更改？
A. 创建 NAT ⽹关。配置公有⼦⽹的路由表，使流量通过 NAT ⽹关发送到 Amazon S3。
B. 配置 EC2 实例的安全组，限制出站流量，只允许到 S3 前缀列表的流量。
C. 将 EC2 实例迁移到私有⼦⽹。为 Amazon S3 创建 VPC 终端节点，并将该终端节点链接到私有⼦⽹的路
由表。
D. 从 VPC 中移除互联⽹⽹关。设置 AWS Direct Connect 连接，并通过 Direct Connect 连接将流量路由到
Amazon S3。
https://examlearn.online
[2026/05]
Question #116
Topic 1
⼀家公司使⽤⼀款流⾏的内容管理系统 (CMS) 来管理其企业⽹站。然⽽，所需的补丁更新和维护⼯作量巨⼤。该
公司正在重新设计⽹站，并希望找到新的解决⽅案。该⽹站每年更新四次，⽆需提供任何动态内容。该解决⽅案
必须具备⾼可扩展性和增强的安全性。
以下哪两项变更组合能够以最⼩的运营成本满⾜这些要求？
A. 在⽹站前端配置 Amazon CloudFront 以使⽤ HTTPS 功能。
B. 在⽹站前⾯部署 AWS WAF Web ACL 以提供 HTTPS 功能。
C. 创建并部署 AWS Lambda 函数来管理和提供⽹站内容。
D. 创建新⽹站和 Amazon S3 存储桶。将⽹站部署到启⽤静态⽹站托管功能的 S3 存储桶中。
E. 创建新⽹站。使⽤位于应⽤程序负载均衡器后⾯的 Amazon EC2 实例⾃动扩展组来部署⽹站。
Question #117
Elasticsearch Service）。
（Amazon Elasticsearch Service）。
Topic 1
⼀家公司将其应⽤程序⽇志存储在 Amazon CloudWatch Logs ⽇志组中。⼀项新策略要求该公司将所有应⽤程
序⽇志近乎实时地存储在 Amazon OpenSearch Service（Amazon Elasticsearch Service）中。
哪种解决⽅案能够以最⼩的运维开销满⾜此要求？
A. 配置 CloudWatch Logs 订阅，将⽇志流式传输到 Amazon OpenSearch Service（Amazon
B. 创建⼀个 AWS Lambda 函数。使⽤⽇志组调⽤该函数，将⽇志写⼊ Amazon OpenSearch Service
C. 创建 Amazon Kinesis Data Firehose 传输流。将⽇志组配置为传输流的源。将 Amazon OpenSearch
Service（Amazon Elasticsearch Service）配置为传输流的⽬标。
D. 在每个应⽤服务器上安装并配置 Amazon Kinesis Agent，以将⽇志传递到 Amazon Kinesis Data
Streams。配置 Kinesis Data Streams，以将⽇志传递到 Amazon OpenSearch Service（Amazon
Elasticsearch Service）。
https://examlearn.online
[2026/05]
Question #118
Topic 1
⼀家公司正在构建⼀个基于 Web 的应⽤程序，该应⽤程序运⾏在多个可⽤区的 Amazon EC2 实例上。该 Web
应⽤程序将提供⼀个总⼤⼩约为 900 TB 的⽂本⽂件库。该公司预计该 Web 应⽤程序将⾯临⾼峰访问量。解决⽅
案架构师必须确保⽤于存储⽂本⽂件的存储组件能够始终满⾜应⽤程序的需求。该公司也关注解决⽅案的总体成
本。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. Amazon Elastic Block Store (Amazon EBS)
B. Amazon Elastic File System (Amazon EFS)
C. Amazon OpenSearch Service（Amazon Elasticsearch Service）
D. 亚⻢逊S3
Question #119
Topic 1
⼀家全球性公司正在使⽤ Amazon API Gateway 为其位于 us-east-1 区域和 ap-southeast-2 区域的会员俱乐部
⽤户设计 REST API。解决⽅案架构师必须设计⼀个解决⽅案，以保护这些跨多个账户的 API Gateway 管理的
REST API 免受 SQL 注⼊和跨站脚本攻击。
哪种解决⽅案能够以最少的管理⼯作量满⾜这些要求？
A. 在两个区域中都设置 AWS WAF。将区域 Web ACL 与 API 阶段关联。
B. 在两个区域中都设置 AWS 防⽕墙管理器。集中配置 AWS WAF 规则。
C. 在 Bath 区域中设置 AWS Shield。将区域 Web ACL 与 API 阶段关联。
D. 在其中⼀个区域中设置 AWS Shield。将区域 Web ACL 与 API 阶段关联。
https://examlearn.online
[2026/05]
Question #120
Topic 1
⼀家公司在 us-west-2 区域的三个 Amazon EC2 实例上部署了⾃管理 DNS 解决⽅案，这些实例位于⽹络负载均
衡器 (NLB) 之后。该公司的⼤部分⽤户位于美国和欧洲。该公司希望提⾼该解决⽅案的性能和可⽤性。该公司在
eu-west-1 区域启动并配置了三个 EC2 实例，并将这些 EC2 实例添加为新 NLB 的⽬标。
该公司可以使⽤哪种解决⽅案将流量路由到所有 EC2 实例？
A. 创建 Amazon Route 53 地理位置路由策略，将请求路由到两个 NLB 中的⼀个。创建 Amazon
CloudFront 分发。使⽤ Route 53 记录作为分发的源。
B. 在 AWS Global Accelerator 中创建⼀个标准加速器。在 us-west-2 和 eu-west-1 中创建终端节点组。将
这两个 NLB 添加为终端节点组的终端节点。
C. 为六个 EC2 实例附加弹性 IP 地址。创建 Amazon Route 53 地理位置路由策略，将请求路由到这六个
EC2 实例中的⼀个。创建 Amazon CloudFront 分发。使⽤ Route 53 记录作为分发的源。
D. 将两个⽹络负载均衡器 (NLB) 替换为两个应⽤程序负载均衡器 (ALB)。创建 Amazon Route 53 延迟路由
策略，将请求路由到其中⼀个 ALB。创建 Amazon CloudFront 分发。使⽤ Route 53 记录作为分发的源。
Question #121
Topic 1
⼀家公司在 AWS 上运⾏在线事务处理 (OLTP) ⼯作负载。该⼯作负载使⽤多可⽤区部署中的未加密 Amazon
RDS 数据库实例。每天都会从该实例创建数据库快照。
解决⽅案架构师应该如何确保数据库和快照始终加密？
A. 对最新数据库快照进⾏加密。通过恢复加密快照来替换现有数据库实例。
B. 创建⼀个新的加密 Amazon Elastic Block Store (Amazon EBS) 卷，并将快照复制到该卷中。启⽤数据库
实例的加密功能。
C. 复制快照并使⽤ AWS Key Management Service (AWS KMS) 启⽤加密。将加密快照恢复到现有数据库实
例。
D. 将快照复制到使⽤ AWS Key Management Service (AWS KMS) 托管密钥 (SSE-KMS) 进⾏服务器端加密
的 Amazon S3 存储桶中。
https://examlearn.online
[2026/05]
Question #122
⼀家公司希望构建可扩展的密钥管理基础设施，以⽀持需要在应⽤程序中加密数据的开发⼈员。
解决⽅案架构师应该如何做才能减轻运维负担？
A. 使⽤多因素身份验证 (MFA) 来保护加密密钥。
B. 使⽤ AWS Key Management Service (AWS KMS) 来保护加密密钥。
C. 使⽤ AWS Certificate Manager (ACM) 创建、存储和分配加密密钥。
D. 使⽤ IAM 策略来限制有权访问加密密钥的⽤户范围。
Question #123
EC2 实例。
Topic 1
Topic 1
⼀家公司在两个 Amazon EC2 实例上托管了⼀个动态 Web 应⽤程序。该公司拥有⾃⼰的 SSL 证书，每个实例上
都部署了该证书以执⾏ SSL 终⽌。
最近流量激增，运维团队发现 SSL 加密和解密导致 Web 服务器的计算能⼒达到极限。
解决⽅案架构师应该如何提⾼应⽤程序的性能？
A. 使⽤ AWS Certificate Manager (ACM) 创建新的 SSL 证书。将 ACM 证书安装到每个实例上。
B. 创建 Amazon S3 存储桶，并将 SSL 证书迁移到 S3 存储桶。配置 EC2 实例以引⽤该存储桶进⾏ SSL 终
⽌。
C. 创建另⼀个 EC2 实例作为代理服务器。将 SSL 证书迁移到新实例，并将其配置为将连接定向到现有的
D. 将 SSL 证书导⼊ AWS Certificate Manager (ACM)。创建⼀个应⽤程序负载均衡器，并配置⼀个使⽤来⾃
ACM 的 SSL 证书的 HTTPS 监听器。
https://examlearn.online
[2026/05]
Question #124
Topic 1
⼀家公司有⼀个⾼度动态的批处理作业，需要使⽤多个 Amazon EC2 实例来完成。该作业本质上是⽆状态的，可
以随时启动和停⽌⽽不会产⽣任何负⾯影响，通常需要 60 分钟以上才能完成。该公司已委托解决⽅案架构师设
计⼀个可扩展且经济⾼效的解决⽅案，以满⾜该作业的需求。
解决⽅案架构师应该提出什么建议？
A. 部署 EC2 Spot 实例。
B. 购买 EC2 预留实例。
C. 实施 EC2 按需实例。
D. 在 AWS Lambda 上实现处理。
Question #125
Topic 1
⼀家公司在 AWS 上运⾏其两层架构的电⼦商务⽹站。Web 层包含⼀个负载均衡器，⽤于将流量发送到 Amazon
EC2 实例。数据库层使⽤ Amazon RDS 数据库实例。EC2 实例和 RDS 数据库实例都不应暴露于公共互联⽹。
EC2 实例需要访问互联⽹才能通过第三⽅ Web 服务完成订单⽀付处理。该应⽤程序必须具有⾼可⽤性。
以下哪两项配置选项组合能够满⾜这些要求？
A. 使⽤⾃动扩展组在私有⼦⽹中启动 EC2 实例。在私有⼦⽹中部署 RDS 多可⽤区数据库实例。
B. 配置⼀个 VPC，该 VPC 包含两个私有⼦⽹和两个跨两个可⽤区的 NAT ⽹关。在私有⼦⽹中部署应⽤程序
负载均衡器。
C. 使⽤⾃动扩展组在两个可⽤区的公共⼦⽹中启动 EC2 实例。在私有⼦⽹中部署 RDS 多可⽤区数据库实
例。
D. 配置⼀个 VPC，包含⼀个公有⼦⽹、⼀个私有⼦⽹和两个跨两个可⽤区的 NAT ⽹关。在公有⼦⽹中部署应
⽤程序负载均衡器。D
. 配置⼀个 VPC，包含两个公有⼦⽹、两个私有⼦⽹和两个跨两个可⽤区的 NAT ⽹关。在公有⼦⽹中部署应
⽤程序负载均衡器。
https://examlearn.online
[2026/05]
Question #126
Topic 1
解决⽅案架构师需要实施⼀项解决⽅案来降低公司的存储成本。公司所有数据都存储在 Amazon S3 标准存储类
别中。公司必须将所有数据保留⾄少 25 年。最近 2 年的数据必须具有⾼可⽤性，并且可以⽴即检索。
哪种解决⽅案能够满⾜这些要求？
A. 设置 S3 ⽣命周期策略，⽴即将对象迁移到 S3 Glacier Deep Archive。
B. 设置 S3 ⽣命周期策略，将对象在 2 年后迁移到 S3 Glacier Deep Archive。
C. 使⽤ S3 智能分层。激活归档选项，确保数据归档到 S3 Glacier Deep Archive 中。
D. 设置 S3 ⽣命周期策略，⽴即将对象迁移到 S3 单区不频繁访问 (S3 单区-IA)，并在 2 年后迁移到 S3
Glacier 深度存档。
Question #127
Topic 1
⼀家媒体公司正在评估将其系统迁移到 AWS 云的可能性。该公司需要⾄少 10 TB 的存储空间，并具备尽可能⾼
的 I/O 性能⽤于视频处理；300 TB 的⾼持久性存储空间⽤于存储媒体内容；以及 900 TB 的存储空间，⽤于存储
不再使⽤的归档媒体。
解决⽅案架构师应该推荐哪⼀组服务来满⾜这些需求？
A. 使⽤ Amazon EBS 实现最佳性能，使⽤ Amazon S3 实现持久数据存储，使⽤ Amazon S3 Glacier 实现归
档存储。
B. 使⽤ Amazon EBS 实现最佳性能，使⽤ Amazon EFS 实现持久数据存储，使⽤ Amazon S3 Glacier 实现
归档存储。
C. 使⽤ Amazon EC2 实例存储以获得最佳性能，使⽤ Amazon EFS 进⾏持久数据存储，使⽤ Amazon S3
进⾏归档存储。
D. 使⽤ Amazon EC2 实例存储以获得最佳性能，使⽤ Amazon S3 以获得持久数据存储，使⽤ Amazon S3
Glacier 以获得归档存储。
https://examlearn.online
[2026/05]
Question #128
Topic 1
⼀家公司希望在 AWS 云平台上以容器形式运⾏应⽤程序。这些应⽤程序是⽆状态的，能够容忍底层基础设施的
中断。该公司需要⼀种能够最⼤限度降低成本和运维开销的解决⽅案。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 在 Amazon EC2 ⾃动扩展组中使⽤竞价型实例来运⾏应⽤程序容器。
B. 在 Amazon Elastic Kubernetes Service (Amazon EKS) 管理的节点组中使⽤竞价型实例。
C. 使⽤ Amazon EC2 ⾃动扩展组中的按需实例来运⾏应⽤程序容器。
D. 在 Amazon Elastic Kubernetes Service (Amazon EKS) 管理的节点组中使⽤按需实例。
Question #129
A. 将 PostgreSQL 数据库迁移到 Amazon Aurora。
Topic 1
⼀家公司在本地运⾏⼀个多层 Web 应⽤程序。该 Web 应⽤程序采⽤容器化部署，运⾏在多个 Linux 主机上，这
些主机连接到⼀个包含⽤户记录的 PostgreSQL 数据库。维护基础设施和容量规划的运维成本限制了公司的发
展。解决⽅案架构师需要改进该应⽤程序的基础设施。
为了实现这⼀⽬标，解决⽅案架构师应该采取哪些措施组合？（选择两项。）
B. 将 Web 应⽤程序迁移到 Amazon EC2 实例上托管。
C. 为 Web 应⽤程序内容设置 Amazon CloudFront 分发。
D. 在 Web 应⽤程序和 PostgreSQL 数据库之间设置 Amazon ElastiCache。
E. 将 Web 应⽤程序迁移到 AWS Fargate 上，并使⽤ Amazon Elastic Container Service (Amazon ECS) 进
⾏托管。
https://examlearn.online
[2026/05]
Question #130
Topic 1
⼀个应⽤程序运⾏在多个可⽤区 (Availability Zone) 的 Amazon EC2 实例上。这些实例运⾏在由应⽤程序负载均
衡器 (Application Load Balancer) 管理的 Amazon EC2 ⾃动扩展 (Auto Scaling) 组中。当 EC2 实例的 CPU 利
⽤率在 40% 或接近 40% 时，应⽤程序性能最佳。
解决⽅案架构师应该如何做才能使组内所有实例都达到所需的性能？
A. 使⽤简单的扩展策略动态扩展⾃动扩展组。
B. 使⽤⽬标跟踪策略动态扩展⾃动扩展组。
C. 使⽤ AWS Lambda 函数更新所需的⾃动扩展组容量。
D. 使⽤计划的扩展操作来扩展和缩减⾃动扩展组。
Question #131
⼀家公司正在开发⼀款⽂件共享应⽤程序，该应⽤程序将使⽤ Amazon S3 存储桶进⾏存储。该公司希望通过
Amazon CloudFront 分发来提供所有⽂件。该公司不希望⽤户直接通过访问 S3 URL 来访问这些⽂件。
解决⽅案架构师应该如何满⾜这些要求？
A. 为每个 S3 存储桶编写单独的策略，仅授予 CloudFront 访问权限读取权限。
名称 (ARN)。
Question #132
B. 创建⼀个 IAM ⽤户。授予该⽤户对 S3 存储桶中对象的读取权限。将该⽤户分配给 CloudFront。
Topic 1
C. 编写⼀个 S3 存储桶策略，将 CloudFront 分发 ID 指定为主体，并将⽬标 S3 存储桶指定为 Amazon 资源
D. 创建源访问身份 (OAI)。将 OAI 分配给 CloudFront 分发。配置 S3 存储桶权限，使只有 OAI 拥有读取权
限。
Topic 1
⼀家公司的⽹站为⽤户提供可下载的历史性能报告。该⽹站需要⼀个能够满⾜公司全球⽹站需求的解决⽅案。该
解决⽅案应经济⾼效、最⼤限度地减少基础设施资源的投⼊，并提供尽可能快的响应时间。
解决⽅案架构师应该推荐哪种组合来满⾜这些要求？
A. Amazon CloudFront 和 Amazon S3
B. AWS Lambda 和 Amazon DynamoDB
C. 使⽤ Amazon EC2 ⾃动扩展的应⽤程序负载均衡器
D. 带有内部应⽤程序负载均衡器的 Amazon Route 53
https://examlearn.online
[2026/05]
Question #133
Topic 1
⼀家公司在本地运⾏Oracle数据库。作为公司迁移到AWS的⼀部分，该公司希望将数据库升级到最新版本。该公
司还希望为数据库设置灾难恢复（DR）。该公司需要最⼤限度地减少⽇常运营和灾难恢复设置所需的运维开销。
此外，该公司还需要保持对数据库底层操作系统的访问。
哪种解决⽅案能够满⾜这些要求？
A. 将 Oracle 数据库迁移到 Amazon EC2 实例。设置数据库复制到不同的 AWS 区域。
B. 将 Oracle 数据库迁移到 Amazon RDS for Oracle。启⽤跨区域⾃动备份，将快照复制到另⼀个 AWS 区
域。
C. 将 Oracle 数据库迁移到 Amazon RDS Custom for Oracle。在另⼀个 AWS 区域中为该数据库创建只读副
本。
D. 将 Oracle 数据库迁移到 Amazon RDS for Oracle。在另⼀个可⽤区创建备⽤数据库。
Question #134
Athena 查询数据。
Topic 1
⼀家公司希望将其应⽤程序迁移到⽆服务器解决⽅案。该⽆服务器解决⽅案需要使⽤ SL 分析现有数据和新数
据。该公司将数据存储在 Amazon S3 存储桶中。数据需要加密，并且必须复制到不同的 AWS 区域。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个新的 S3 存储桶。将数据加载到新的 S3 存储桶中。使⽤ S3 跨区域复制 (CRR) 将加密对象复制到
另⼀个区域的 S3 存储桶。使⽤ AWS KMS 多区域密钥 (SSE-KMS) 进⾏服务器端加密。使⽤ Amazon
B. 创建⼀个新的 S3 存储桶。将数据加载到新的 S3 存储桶中。使⽤ S3 跨区域复制 (CRR) 将加密对象复制到
另⼀个区域的 S3 存储桶。使⽤服务器端加密和 AWS KMS 多区域密钥 (SSE-KMS)。使⽤ Amazon RDS 查
询数据。
C. 将数据加载到现有的 S3 存储桶中。使⽤ S3 跨区域复制 (CRR) 将加密对象复制到另⼀个区域中的 S3 存储
桶。使⽤ Amazon S3 管理的加密密钥 (SSE-S3) 进⾏服务器端加密。使⽤ Amazon Athena 查询数据。
D. 将数据加载到现有的 S3 存储桶中。使⽤ S3 跨区域复制 (CRR) 将加密对象复制到另⼀个区域中的 S3 存储
桶。使⽤ Amazon S3 管理的加密密钥 (SSE-S3) 进⾏服务器端加密。使⽤ Amazon RDS 查询数据。
https://examlearn.online
[2026/05]
Question #135
Topic 1
⼀家公司在 AWS 上运⾏⼯作负载。该公司需要连接到外部提供商的服务。该服务托管在提供商的 VPC 中。根据
该公司安全团队的要求，连接必须是私密的，并且必须仅限于⽬标服务。连接必须只能从该公司⾃身的 VPC 发
起。
哪种解决⽅案能够满⾜这些要求？
A. 在公司 VPC 和提供商 VPC 之间创建 VPC 对等连接。更新路由表以连接到⽬标服务。
B. 请服务提供商在其 VPC 中创建虚拟专⽤⽹关。使⽤ AWS PrivateLink 连接到⽬标服务。
C. 在公司 VP 的公共⼦⽹中创建 NAT ⽹关，更新路由表以连接到⽬标服务。
D. 请服务提供商为⽬标服务创建 VPC 终端节点。使⽤ AWS PrivateLink 连接到⽬标服务。
Question #136
A. 创建⼀个持续复制任务。
B. 创建本地数据库的数据库备份。
Topic 1
⼀家公司正在将其本地 PostgreSQL 数据库迁移到 Amazon Aurora PostgreSQL。迁移期间，本地数据库必须保
持在线且可访问。Aurora 数据库必须与本地数据库保持同步。
解决⽅案架构师必须采取哪些措施组合才能满⾜这些要求？（选择两项。）
C. 创建 AWS 数据库迁移服务 (AWS DMS) 复制服务器。
D. 使⽤ AWS Schema Conversion Tool (AWS SCT) 转换数据库架构。
E. 创建 Amazon EventBridge（Amazon CloudWatch Events）规则以监控数据库同步。
https://examlearn.online
[2026/05]
Question #137
Topic 1
⼀家公司使⽤ AWS Organizations 为每个业务部⻔创建专⽤的 AWS 账户，以便根据需求独⽴管理各业务部⻔的
账户。其中⼀个账户的根⽤户邮箱地址收到了⼀封通知邮件，但该账户的根邮箱收件⼈却错过了。该公司希望确
保以后不会再错过任何通知。未来的通知必须仅限账户管理员查看。
哪种解决⽅案能够满⾜这些要求？
A. 配置公司的电⼦邮件服务器，将发送到 AWS 账户根⽤户电⼦邮件地址的通知电⼦邮件转发给组织中的所有
⽤户。
B. 将所有 AWS 账户根⽤户电⼦邮件地址配置为分发列表，发送给少数可以响应警报的管理员。在 AWS
Organizations 控制台中或通过编程⽅式配置 AWS 账户备⽤联系⼈。
C. 配置所有 AWS 账户根⽤户电⼦邮件消息，使其发送给⼀位管理员，该管理员负责监控警报并将这些警报转
发给相应的组。
D. 将所有现有 AWS 账户和所有新创建的账户配置为使⽤相同的根⽤户电⼦邮件地址。在 AWS
Organizations 控制台中或通过编程⽅式配置 AWS 账户的备⽤联系⼈。
Question #138
Topic 1
⼀家公司在 AWS 上运⾏其电⼦商务应⽤程序。每个新订单都会以消息的形式发布到运⾏于同⼀可⽤区内
Amazon EC2 实例上的 RabbitMQ 队列中。这些消息由运⾏于另⼀个 EC2 实例上的应⽤程序进⾏处理。该应⽤
程序将订单详情存储在另⼀个 EC2 实例上的 PostgreSQL 数据库中。所有 EC2 实例均位于同⼀可⽤区。
该公司需要重新设计其架构，以在保证最⾼可⽤性的同时，尽可能降低运维开销。
解决⽅案架构师应该如何满⾜这些要求？
A. 将队列迁移到 Amazon MQ 上的⼀对冗余（主备）RabbitMQ 实例。为托管应⽤程序的 EC2 实例创建⼀个
多可⽤区⾃动扩展组。为托管 PostgreSQL 数据库的 EC2 实例创建另⼀个多可⽤区⾃动扩展组。
B. 将队列迁移到 Amazon MQ 上的⼀对冗余（主备）RabbitMQ 实例。为托管应⽤程序的 EC2 实例创建多可
⽤区⾃动扩展组。将数据库迁移到 Amazon RDS for PostgreSQL 的多可⽤区部署上运⾏。
C. 为托管 RabbitMQ 队列的 EC2 实例创建⼀个多可⽤区⾃动扩展组。为托管应⽤程序的 EC2 实例创建另⼀
个多可⽤区⾃动扩展组。将数据库迁移到 Amazon RDS for PostgreSQL 的多可⽤区部署上运⾏。
D. 为托管 RabbitMQ 队列的 EC2 实例创建⼀个多可⽤区⾃动伸缩组。为托管应⽤程序的 EC2 实例创建另⼀
个多可⽤区⾃动伸缩组。为托管 PostgreSQL 数据库的 EC2 实例创建第三个多可⽤区⾃动伸缩组。
https://examlearn.online
[2026/05]
Question #139
Topic 1
报告团队每天都会收到存储在 Amazon S3 存储桶中的⽂件。为了配合 Amazon QuickSight 使⽤，报告团队每天
会在同⼀时间⼿动审核并将⽂件从初始 S3 存储桶复制到分析 S3 存储桶。现在，其他团队开始向初始 S3 存储桶
发送更多、更⼤的⽂件。
报告团队希望在⽂件进⼊初始 S3 存储桶的同时，⾃动将其移动到分析 S3 存储桶。此外，报告团队还希望使⽤
AWS Lambda 函数对复制的数据运⾏模式匹配代码。最后，报告团队还希望将数据⽂件发送到 Amazon
SageMaker Pipelines 中的管道。
解决⽅案架构师应该如何做才能以最⼩的运维开销满⾜这些需求？
A. 创建⼀个 Lambda 函数，将⽂件复制到分析 S3 存储桶。为分析 S3 存储桶创建⼀个 S3 事件通知。将
Lambda 和 SageMaker Pipelines 配置为事件通知的⽬标。将事件类型配置为 s3:ObjectCreated:Put。
B. 创建⼀个 Lambda 函数，将⽂件复制到分析 S3 存储桶。配置分析 S3 存储桶，使其向 Amazon
EventBridge（Amazon CloudWatch Events）发送事件通知。在 EventBridge（CloudWatch Events）中配
置 ObjectCreated 规则。将 Lambda 和 SageMaker Pipelines 配置为该规则的⽬标。
C. 配置 S3 存储桶之间的 S3 复制。为分析 S3 存储桶创建 S3 事件通知。将 Lambda 和 SageMaker
Pipelines 配置为事件通知的⽬标。将事件类型配置为 s3:ObjectCreated:Put。
D. 配置 S3 存储桶之间的 S3 复制。配置分析 S3 存储桶，使其向 Amazon EventBridge（Amazon
Question #140
CloudWatch Events）发送事件通知。在 EventBridge（CloudWatch Events）中配置 ObjectCreated 规
则。将 Lambda 和 SageMaker Pipelines 配置为该规则的⽬标。
Topic 1
⼀位解决⽅案架构师需要帮助⼀家公司优化在 AWS 上运⾏应⽤程序的成本。该应⽤程序将使⽤ Amazon EC2 实
例、AWS Fargate 和 AWS Lambda 进⾏计算。EC2
实例将运⾏应⽤程序的数据采集层。EC2 的使⽤情况将是零星且不可预测的。运⾏在 EC2 实例上的⼯作负载随时
可能中断。应⽤程序的前端将运⾏在 Fargate 上，⽽ Lambda 将提供 API 层服务。前端和 API 层的利⽤率在未来
⼀年内是可预测的。
哪种购买⽅案组合能够为托管此应⽤程序提供最具成本效益的解决⽅案？（选择两项。）
A. 使⽤竞价型实例作为数据摄取层
B. 使⽤按需实例作为数据摄取层
C. 为前端和 API 层购买 1 年计算节省计划。
D. 为数据摄取层购买 1 年期全预付预留实例。
E. 为前端和 API 层购买 1 年 EC2 实例节省计划。
https://examlearn.online
[2026/05]
Question #141
Topic 1
⼀家公司运营着⼀个基于⽹络的⻔户⽹站，为⽤户提供全球突发新闻、本地警报和天⽓更新。该⻔户⽹站通过静
态和动态内容相结合的⽅式，为每位⽤户提供个性化的视图。内容通过运⾏在应⽤程序负载均衡器 (ALB) 后⾯的
Amazon EC2 实例上的 API 服务器，以 HTTPS 协议提供。该公司希望⻔户⽹站能够以最快的速度向全球⽤户提
供这些内容。
解决⽅案架构师应该如何设计应⽤程序，才能确保所有⽤户的延迟最低？
A. 将应⽤程序堆栈部署在单个 AWS 区域中。使⽤ Amazon CloudFront 提供所有静态和动态内容，并将 ALB
指定为源。
B. 在两个 AWS 区域中部署应⽤程序堆栈。使⽤ Amazon Route 53 延迟路由策略，从最近的区域中的 ALB
提供所有内容。
C. 将应⽤程序堆栈部署在单个 AWS 区域中。使⽤ Amazon CloudFront 提供静态内容。直接从 ALB 提供动
态内容。
D. 在两个 AWS 区域中部署应⽤程序堆栈。使⽤ Amazon Route 53 地理位置路由策略，从最近的区域中的
ALB 提供所有内容。
Question #142
Lambda 来运⾏应⽤程序。
Lambda 来运⾏应⽤程序。
Topic 1
⼀家游戏公司正在设计⼀个⾼可⽤性架构。该应⽤程序运⾏在修改过的 Linux 内核上，并且仅⽀持基于 UDP 的
流量。该公司需要前端层提供最佳的⽤户体验。该层必须具有低延迟，将流量路由到最近的边缘节点，并为应⽤
程序端点提供静态 IP 地址。
解决⽅案架构师应该如何满⾜这些要求？
A. 配置 Amazon Route 53 将请求转发到应⽤程序负载均衡器。在 AWS 应⽤程序⾃动扩展中使⽤ AWS
B. 配置 Amazon CloudFront 将请求转发到⽹络负载均衡器。在 AWS 应⽤程序⾃动扩展组中使⽤ AWS
C. 配置 AWS Global Accelerator 将请求转发到⽹络负载均衡器。使⽤ EC2 ⾃动扩展组中的 Amazon EC2 实
例来运⾏应⽤程序。
D. 配置 Amazon API Gateway 将请求转发到应⽤程序负载均衡器。使⽤ EC2 ⾃动扩展组中的 Amazon EC2
实例来运⾏该应⽤程序。
https://examlearn.online
[2026/05]
Question #143
Topic 1
⼀家公司希望将其现有的本地单体应⽤迁移到 AWS。该公司希望尽可能保留前端代码和后端代码，但同时希望将
应⽤拆分成多个更⼩的应⽤，并由不同的团队分别管理。该公司需要⼀个⾼度可扩展且能最⼤限度降低运维开销
的解决⽅案。
哪种解决⽅案能够满⾜这些要求？
A. 将应⽤程序托管在 AWS Lambda 上。将应⽤程序与 Amazon API Gateway 集成。
B. 使⽤ AWS Amplify 托管应⽤程序。将应⽤程序连接到与 AWS Lambda 集成的 Amazon API Gateway
API。
C. 将应⽤程序托管在 Amazon EC2 实例上。设置应⽤程序负载均衡器，并将⾃动扩展组中的 EC2 实例作为
⽬标。
D. 将应⽤程序托管在 Amazon Elastic Container Service (Amazon ECS) 上。设置⼀个以 Amazon ECS 为
⽬标的应⽤程序负载均衡器。
Question #144
Topic 1
⼀家公司最近开始使⽤ Amazon Aurora 作为其全球电⼦商务应⽤程序的数据存储。开发⼈员反映，在运⾏⼤型
报表时，该电⼦商务应⽤程序的性能表现不佳。解决⽅案架构师在查看 Amazon CloudWatch 中的指标后发现，
在运⾏⽉度报表时，ReadIOPS 和 CPUUtilization 指标会出现峰值。
哪种解决⽅案最具成本效益？
A. 将⽉度报告迁移到 Amazon Redshift。
B. 将⽉度报告迁移到 Aurora 副本。
C. 将 Aurora 数据库迁移到更⼤的实例类。
D. 增加 Aurora 实例的配置 IOPS。
https://examlearn.online
[2026/05]
Question #145
Topic 1
⼀家公司在单个 Amazon EC2 按需实例上托管了⼀个⽹站分析应⽤程序。该分析软件使⽤ PHP 编写，并使⽤
MySQL 数据库。分析软件、提供 PHP 的 Web 服务器和数据库服务器都托管在该 EC2 实例上。该应⽤程序在⾼
峰时段出现性能下降，并出现 5xx 错误。该公司需要使应⽤程序能够⽆缝扩展。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将数据库迁移到 Amazon RDS for MySQL 数据库实例。创建 Web 应⽤程序的 AMI。使⽤该 AMI 启动第
⼆个 EC2 按需实例。使⽤应⽤程序负载均衡器将负载分配到每个 EC2 实例。
B. 将数据库迁移到 Amazon RDS for MySQL 数据库实例。创建 Web 应⽤程序的 AMI。使⽤该 AMI 启动第
⼆个 EC2 按需实例。使⽤ Amazon Route 53 加权路由将负载分配到两个 EC2 实例上。
C. 将数据库迁移到 Amazon Aurora MySQL 数据库实例。创建⼀个 AWS Lambda 函数来停⽌ EC2 实例并更
改实例类型。创建⼀个 Amazon CloudWatch 警报，以便在 CPU 利⽤率超过 75% 时调⽤ Lambda 函数。
D. 将数据库迁移到 Amazon Aurora MySQL 数据库实例。创建 Web 应⽤程序的 AMI。将该 AMI 应⽤到启动
模板。使⽤该启动模板创建 Auto Scaling 组。配置启动模板以使⽤ Spot 实例。将应⽤程序负载均衡器附加
到 Auto Scaling 组。
Question #146
Topic 1
⼀家公司在⽣产环境中运⾏⼀个⽆状态 Web 应⽤程序，该应⽤程序部署在⼀组 Amazon EC2 按需实例上，并通
过应⽤程序负载均衡器进⾏管理。该应⽤程序在每个⼯作⽇的 8 ⼩时内使⽤量很⾼。夜间使⽤量适中且稳定。周
末使⽤量很低。
该公司希望在不影响应⽤程序可⽤性的前提下，最⼤限度地降低 EC2 成本。
哪种解决⽅案能够满⾜这些要求？
A. 对所有⼯作负载使⽤竞价型实例。
B. 使⽤预留实例来满⾜基本使⽤需求。对于应⽤程序所需的任何额外容量，请使⽤竞价型实例。
C. 对于基本使⽤级别，请使⽤按需实例。对于应⽤程序所需的任何额外容量，请使⽤竞价型实例。
D. 对于基本使⽤级别，请使⽤专⽤实例。对于应⽤程序所需的任何额外容量，请使⽤按需实例。
https://examlearn.online
[2026/05]
Question #147
Topic 1
⼀家公司需要将关键应⽤程序的应⽤程序⽇志⽂件保留 10 年。应⽤程序团队会定期访问最近⼀个⽉的⽇志进⾏故
障排除，但很少访问超过⼀个⽉的⽇志。该应⽤程序每⽉⽣成超过 10 TB 的⽇志。
哪种存储⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将⽇志存储在 Amazon S3 中。使⽤ AWS Backup 将超过 1 个⽉的⽇志迁移到 S3 Glacier Deep
Archive。
B. 将⽇志存储在 Amazon S3 中。使⽤ S3 ⽣命周期策略将超过 1 个⽉的⽇志移动到 S3 Glacier Deep
Archive。
C. 将⽇志存储在 Amazon CloudWatch Logs 中。使⽤ AWS Backup 将超过 1 个⽉的⽇志迁移到 S3 Glacier
Deep Archive。
D. 将⽇志存储在 Amazon CloudWatch Logs 中。使⽤ Amazon S3 ⽣命周期策略将超过 1 个⽉的⽇志移动到
S3 Glacier Deep Archive。
Question #148
Topic 1
⼀家公司的数据采集⼯作流包含以下组件：
⼀个⽤于接收新数据交付通知的 Amazon Simple Notification Service (Amazon SNS) 主题；
⼀个⽤于处理和存储数据的 AWS Lambda 函数。
由于⽹络连接问题，采集⼯作流偶尔会失败。发⽣故障时，除⾮公司⼿动重新运⾏作业，否则相应的数据不会被
采集。
解决⽅案架构师应该如何做才能确保所有通知最终都能被处理？
A. 配置 Lambda 函数以跨多个可⽤区部署。
B. 修改 Lambda 函数的配置，增加该函数的 CPU 和内存分配。
C. 配置 SNS 主题的重试策略，增加重试次数和重试之间的等待时间。
D. 将 Amazon Simple Queue Service (Amazon SQS) 队列配置为故障处理⽬标。修改 Lambda 函数以处理
队列中的消息。
https://examlearn.online
[2026/05]
Question #149
Topic 1
⼀家公司提供⼀项⽣成事件数据的服务。该公司希望使⽤ AWS 来处理接收到的事件数据。数据按照特定的顺序
写⼊，并且在整个处理过程中必须保持该顺序。该公司希望实施⼀个能够最⼤限度降低运维开销的解决⽅案。
解决⽅案架构师应该如何实现这⼀⽬标？
A. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) FIFO 队列来保存消息。设置⼀个 AWS
Lambda 函数来处理队列中的消息。
B. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题，⽤于发送包含待处理有效负载的通
知。将 AWS Lambda 函数配置为订阅者。
C. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 标准队列来保存消息。设置⼀个 AWS Lambda
函数来独⽴处理队列中的消息。
D. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题，⽤于发送包含待处理有效负载的通
知。将 Amazon Simple Queue Service (Amazon SQS) 队列配置为订阅者。
Question #150
Topic 1
⼀家公司正在将应⽤程序从本地服务器迁移到 Amazon EC2 实例。作为迁移设计要求的⼀部分，解决⽅案架构师
必须实现基础设施指标告警。如果 CPU 利⽤率在短时间内飙升⾄ 50% 以上，公司⽆需采取任何措施。但是，如
果 CPU 利⽤率飙升⾄ 50% 以上，并且磁盘读取 IOPS 同时很⾼，则公司需要尽快采取⾏动。解决⽅案架构师还
必须减少误报。为了
满⾜这些要求，解决⽅案架构师应该怎么做？
A. 尽可能创建 Amazon CloudWatch 复合警报。
B. 创建 Amazon CloudWatch 控制⾯板，以可视化指标并快速应对问题。
C. 创建 Amazon CloudWatch Synthetics canary 来监控应⽤程序并发出警报。
D. 尽可能创建具有多个指标阈值的单个 Amazon CloudWatch 指标警报。
https://examlearn.online
[2026/05]
Question #151
Topic 1
⼀家公司希望将其本地数据中⼼迁移到 AWS。根据该公司的合规性要求，它只能使⽤ ap-northeast-3 区域。公
司管理员不允许将 VPC 连接到互联⽹。
哪些解决⽅案能够满⾜这些要求？（选择两个。）
A. 使⽤ AWS Control Tower 实施数据驻留保护措施，拒绝互联⽹访问，并拒绝访问除 ap-northeast-3 区域
之外的所有 AWS 区域。
B. 使⽤ AWS WAF 中的规则阻⽌互联⽹访问。在 AWS 账户设置中拒绝访问除 ap-northeast-3 区域之外的所
有 AWS 区域。
C. 使⽤ AWS Organizations 配置服务控制策略 (SCP)，阻⽌ VPC 获取互联⽹访问权限。拒绝访问除 ap
northeast-3 区域之外的所有 AWS 区域。
D. 在每个 VPC 中为⽹络 ACL 创建出站规则，拒绝来⾃ 0.0.0.0/0 的所有流量。为每个⽤户创建 IAM 策略，
以防⽌使⽤除 ap-northeast-3 以外的任何 AWS 区域。
E. 使⽤ AWS Config 激活托管规则，以检测和警报互联⽹⽹关，并检测和警报部署在 ap-northeast-3 之外的
新资源。
Question #152
Topic 1
⼀家公司使⽤三层架构的Web应⽤程序为新员⼯提供培训。该应⽤程序每天仅被访问12⼩时。该公司使⽤
Amazon RDS for MySQL数据库实例存储信息，并希望最⼤限度地降低成本。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 为 AWS Systems Manager Session Manager 配置 IAM 策略。为该策略创建 IAM ⻆⾊。更新该⻆⾊的信
任关系。设置数据库实例的⾃动启动和停⽌。
B. 创建⼀个 Amazon ElastiCache for Redis 缓存集群，使⽤户在数据库实例停⽌时仍能访问缓存中的数据。
数据库实例启动后，使缓存失效。
C. 启动⼀个 Amazon EC2 实例。创建⼀个 IAM ⻆⾊，授予其访问 Amazon RDS 的权限。将该⻆⾊附加到
EC2 实例。配置⼀个 cron 作业，以便按所需计划启动和停⽌ EC2 实例。
D. 创建 AWS Lambda 函数来启动和停⽌数据库实例。创建 Amazon EventBridge（Amazon CloudWatch
Events）计划规则来调⽤ Lambda 函数。将 Lambda 函数配置为这些规则的事件⽬标。
https://examlearn.online
[2026/05]
Question #153
Topic 1
⼀家公司销售由流⾏歌曲⽚段制作的铃声。这些铃声⽂件存储在 Amazon S3 标准版中，⼤⼩⾄少为 128 KB。该
公司拥有数百万个⽂件，但超过 90 天的铃声下载量很少。该公司需要在节省存储成本的同时，确保⽤户能够随
时访问访问量最⾼的⽂件。
为了以最具成本效益的⽅式满⾜这些要求，该公司应该采取哪种措施？
A. 为对象的初始存储层配置 S3 标准-不频繁访问 (S3 标准-IA) 存储。
B. 将⽂件移⾄ S3 智能分层存储，并将其配置为在 90 天后将对象移⾄成本较低的存储层。
C. 配置 S3 库存以管理对象，并在 90 天后将其移⾄ S3 标准-不频繁访问 (S3 标准-1A)。
D. 实施 S3 ⽣命周期策略，在 90 天后将对象从 S3 标准迁移到 S3 标准 - 不频繁访问 (S3 标准-1A)。
Question #154
Topic 1
⼀家公司需要将⼀项医学试验的结果保存到 Amazon S3 存储库中。该存储库必须允许少数科学家添加新⽂件，
并且必须限制所有其他⽤户只有只读访问权限。任何⽤户都不能修改或删除存储库中的任何⽂件。该公司必须将
存储库中的每个⽂件⾄少保留⼀年。
哪种解决⽅案能够满⾜这些要求？
A. 在治理模式下使⽤ S3 对象锁定，法律保留期限为 1 年。
B. 使⽤ S3 对象锁定，在合规模式下保留 365 天。
C. 使⽤ IAM ⻆⾊限制所有⽤户删除或更改 S3 存储桶中的对象。使⽤ S3 存储桶策略仅允许具有该 IAM ⻆⾊
的⽤户访问。
D. 配置 S3 存储桶，使其在每次添加对象时调⽤ AWS Lambda 函数。配置该函数以跟踪已保存对象的哈希
值，以便对已修改的对象进⾏相应标记。
https://examlearn.online
[2026/05]
Question #155
Topic 1
⼀家⼤型媒体公司在 AWS 上托管了⼀个 Web 应⽤程序。该公司希望缓存机密媒体⽂件，以便世界各地的⽤户都
能可靠地访问这些⽂件。内容存储在 Amazon S3 存储桶中。⽆论请求来⾃何处，该公司都必须快速交付内容。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS DataSync 将 S3 存储桶连接到 Web 应⽤程序。
B. 部署 AWS Global Accelerator 将 S3 存储桶连接到 Web 应⽤程序。
C. 部署 Amazon CloudFront 将 S3 存储桶连接到 CloudFront 边缘服务器。
D. 使⽤ Amazon Simple Queue Service (Amazon SQS) 将 S3 存储桶连接到 Web 应⽤程序。
Question #156
Topic 1
⼀家公司会产⽣来⾃不同数据库的批量数据，以及来⾃⽹络传感器和应⽤程序 API 的实时流数据。该公司需要将
所有数据整合到⼀个位置以进⾏业务分析。该公司需要处理传⼊的数据，然后将其暂存到不同的 Amazon S3 存
储桶中。之后，团队将运⾏⼀次性查询并将数据导⼊商业智能⼯具，以显示关键绩效指标 (KPI)。
以下哪两项步骤组合能够以最⼩的运营开销满⾜这些要求？
A. 使⽤ Amazon Athena 进⾏⼀次性查询。使⽤ Amazon QuickSight 创建 KPI 仪表板。
B. 使⽤ Amazon Kinesis Data Analytics 进⾏⼀次性查询。使⽤ Amazon QuickSight 创建 KPI 仪表板。
C. 创建⾃定义 AWS Lambda 函数，将数据库中的各个记录移动到 Amazon Redshift 集群。
D. 使⽤ AWS Glue 提取、转换和加载 (ETL) 作业将数据转换为 JSON 格式。将数据加载到多个 Amazon
OpenSearch Service（Amazon Elasticsearch Service）集群中。
E. 使⽤ AWS Lake Formation 中的蓝图来识别可以导⼊数据湖的数据。使⽤ AWS Glue 抓取数据源，提取数
据，并将数据以 Apache Parquet 格式加载到 Amazon S3 中。
https://examlearn.online
[2026/05]
Question #157
Topic 1
⼀家公司将数据存储在 Amazon Aurora PostgreSQL 数据库集群中。该公司必须将所有数据保存 5 年，并在 5
年后删除所有数据。此外，该公司还必须⽆限期地保留数据库中执⾏操作的审计⽇志。⽬前，该公司已为 Aurora
配置了⾃动备份。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. ⼿动对数据库集群进⾏快照。
B. 为⾃动备份创建⽣命周期策略。
C. 配置⾃动备份保留期限为 5 年。
D. 为数据库集群配置 Amazon CloudWatch Logs 导出。
E. 使⽤ AWS Backup 进⾏备份，并将备份保留 5 年。
Question #158
A. 亚⻢逊云前沿
B. AWS 全球加速器
Topic 1
⼀位解决⽅案架构师正在优化⼀个即将举办的⾳乐活动的⽹站。演出视频将实时直播，之后也可点播观看。预计
该活动将吸引全球在线观众。
哪项服务能够同时提升实时直播和点播播放的性能？
C. 亚⻢逊53号公路
D. Amazon S3 传输加速
https://examlearn.online
[2026/05]
Question #159
⼀家公司运⾏着⼀个可公开访问的⽆服务器应⽤程序，该应⽤程序使⽤ Amazon API Gateway 和 AWS
Lambda。最近，由于僵⼫⽹络的欺诈请求，该应⽤程序的流量激增。
解决⽅案架构师应该采取哪些步骤来阻⽌来⾃未经授权⽤户的请求？（选择两项。）
A. 创建⼀个使⽤计划，其中包含⼀个仅与真实⽤户共享的 API 密钥。
B. 在 Lambda 函数中集成逻辑，忽略来⾃欺诈性 IP 地址的请求。
C. 实施 AWS WAF 规则，以定位恶意请求并触发操作来过滤它们。
D. 将现有的公共 API 转换为私有 API。更新 DNS 记录，将⽤户重定向到新的 API 端点。
E. 为每个尝试访问 API 的⽤户创建⼀个 IAM ⻆⾊。⽤户在发起 API 调⽤时将承担该⻆⾊。
Question #160
B. 亚⻢逊S3冰川
Topic 1
Topic 1
⼀家电商公司将其分析应⽤程序托管在 AWS 云平台上。该应⽤程序每⽉⽣成约 300 MB 的数据，数据以 JSON
格式存储。该公司正在评估⼀种灾难恢复解决⽅案来备份这些数据。数据必须在需要时可在⼏毫秒内访问，并且
必须保留 30 天。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. Amazon OpenSearch Service（Amazon Elasticsearch Service）
C. Amazon S3 标准
D. Amazon RDS for PostgreSQL
https://examlearn.online
[2026/05]
Question #161
Topic 1
⼀家公司有⼀个⼩型 Python 应⽤程序，⽤于处理 JSON ⽂档并将结果输出到本地 SQL 数据库。该应⽤程序每天
运⾏数千次。该公司希望将该应⽤程序迁移到 AWS 云。该公司需要⼀个⾼可⽤性解决⽅案，该⽅案能够最⼤限
度地提⾼可扩展性并最⼤限度地降低运维开销。
哪种解决⽅案能够满⾜这些要求？
A. 将 JSON ⽂档放⼊ Amazon S3 存储桶。在多个 Amazon EC2 实例上运⾏ Python 代码来处理这些⽂档。
将处理结果存储在 Amazon Aurora 数据库集群中。
B. 将 JSON ⽂档放⼊ Amazon S3 存储桶。创建⼀个 AWS Lambda 函数，运⾏ Python 代码来处理到达 S3
存储桶的⽂档。将处理结果存储在 Amazon Aurora 数据库集群中。
C. 将 JSON ⽂档放置在 Amazon Elastic Block Store (Amazon EBS) 卷中。使⽤ EBS 多实例附加功能将该
卷附加到多个 Amazon EC2 实例。在这些 EC2 实例上运⾏ Python 代码来处理⽂档。将处理结果存储在
Amazon RDS 数据库实例中。
D. 将 JSON ⽂档作为消息放⼊ Amazon Simple Queue Service (Amazon SQS) 队列中。将 Python 代码作
为容器部署到配置为 Amazon EC2 启动类型的 Amazon Elastic Container Service (Amazon ECS) 集群上。
使⽤该容器处理 SQS 消息。将结果存储在 Amazon RDS 数据库实例上。
Question #162
哪种 AWS 服务组合能够满⾜这些要求？
Topic 1
⼀家公司希望利⽤ AWS 上的⾼性能计算 (HPC) 基础设施进⾏⾦融⻛险建模。该公司的 HPC ⼯作负载运⾏在
Linux 系统上。每个 HPC ⼯作流运⾏在数百个 Amazon EC2 Spot 实例上，⽣命周期较短，并⽣成数千个输出⽂
件，这些⽂件最终存储在持久存储中，⽤于分析和⻓期使⽤。
该公司正在寻找⼀种云存储解决⽅案，该⽅案允许将本地数据复制到⻓期持久存储，以便所有 EC2 实例都可以处
理这些数据。此外，该解决⽅案还应是⼀个⾼性能⽂件系统，并与持久存储集成，⽤于读取和写⼊数据集和输出
⽂件。
A. Amazon FSx for Lustre 与 Amazon S3 集成
B. Amazon FSx for Windows ⽂件服务器与 Amazon S3 集成
C. Amazon S3 Glacier 与 Amazon Elastic Block Store (Amazon EBS) 集成
D. 集成了 Amazon Elastic Block Store (Amazon EBS) 通⽤ SSD (gp2) 卷的 VPC 端点的 Amazon S3 存储
桶
https://examlearn.online
[2026/05]
Question #163
Topic 1
⼀家公司正在本地构建容器化应⽤程序，并决定将其迁移到 AWS。该应⽤程序部署后不久将拥有数千⽤户。该公
司不确定如何⼤规模管理容器部署。该公司需要以⾼可⽤性架构部署容器化应⽤程序，并最⼤限度地降低运维开
销。
哪种解决⽅案能够满⾜这些要求？
A. 将容器镜像存储在 Amazon Elastic Container Registry (Amazon ECR) 存储库中。使⽤启动类型为 AWS
Fargate 的 Amazon Elastic Container Service (Amazon ECS) 集群来运⾏容器。使⽤⽬标跟踪功能，根据
需求⾃动扩展。
B. 将容器镜像存储在 Amazon Elastic Container Registry (Amazon ECR) 存储库中。使⽤启动类型为
Amazon EC2 的 Amazon Elastic Container Service (Amazon ECS) 集群来运⾏容器。使⽤⽬标跟踪功能，
根据需求⾃动扩展。
C. 将容器镜像存储在运⾏于 Amazon EC2 实例上的存储库中。在分布于多个可⽤区的 EC2 实例上运⾏容
器。在 Amazon CloudWatch 中监控平均 CPU 利⽤率。根据需要启动新的 EC2 实例。
D. 创建⼀个包含容器镜像的 Amazon EC2 Amazon 系统镜像 (AMI)。在跨多个可⽤区的⾃动扩展组中启动
EC2 实例。使⽤ Amazon CloudWatch 警报，在平均 CPU 利⽤率超过阈值时扩展 EC2 实例。
Question #164
哪种解决⽅案既满⾜这些要求，⼜具有最⾼的运⾏效率？
Topic 1
⼀家公司有两个应⽤程序：⼀个发送应⽤程序，⽤于发送带有待处理有效负载的消息；以及⼀个处理应⽤程序，
⽤于接收带有有效负载的消息。该公司希望部署⼀项 AWS 服务来处理这两个应⽤程序之间的消息。发送应⽤程
序每⼩时⼤约可以发送 1000 条消息。消息的处理时间可能⻓达 2 天：如果消息处理失败，则必须将其保留，以
免影响剩余消息的处理。
A. 设置⼀个运⾏ Redis 数据库的 Amazon EC2 实例。配置两个应⽤程序使⽤该实例。分别⽤于存储、处理和
删除消息。
B. 使⽤ Amazon Kinesis 数据流接收来⾃发送应⽤程序的消息。将处理应⽤程序与 Kinesis 客户端库 (KCL)
集成。
C. 将发送⽅和处理⽅应⽤程序与 Amazon Simple Queue Service (Amazon SQS) 队列集成。配置死信队列
以收集处理失败的消息。
D. 将处理应⽤程序订阅到 Amazon Simple Notification Service (Amazon SNS) 主题，以接收待处理的通
知。集成发送应⽤程序以向 SNS 主题写⼊数据。
https://examlearn.online
[2026/05]
Question #165
Topic 1
解决⽅案架构师需要设计⼀个使⽤ Amazon CloudFront 和 Amazon S3 源来存储静态⽹站的解决⽅案。公司的
安全策略要求所有⽹站流量都必须经过 AWS WAF 的检查。
解决⽅案架构师应该如何满⾜这些要求？
A. 配置 S3 存储桶策略，使其仅接受来⾃ AWS WAF Amazon 资源名称 (ARN) 的请求。
B. 配置 Amazon CloudFront 将所有传⼊请求转发到 AWS WAF，然后再从 S3 源请求内容。
C. 配置⼀个安全组，仅允许 Amazon CloudFront IP 地址访问 Amazon S3。将 AWS WAF 与 CloudFront 关
联。
D. 配置 Amazon CloudFront 和 Amazon S3 使⽤源访问身份 (OAI) 来限制对 S3 存储桶的访问。在分发上启
⽤ AWS WAF。
Question #166
A. 为⽂件⽣成预签名 URL。
Topic 1
某全球性活动的组织者希望将每⽇报告以静态 HTML ⻚⾯的形式发布到⽹上。预计这些⻚⾯将吸引来⾃世界各地
数百万⽤户的浏览量。⽂件存储在 Amazon S3 存储桶中。⼀位解决⽅案架构师受命设计⼀个⾼效的解决⽅案。
为了实现这⼀⽬标，这位解决⽅案架构师应该采取什么⾏动？
B. 使⽤跨区域复制到所有区域。
C. 使⽤亚⻢逊 Route 53 的地理位置功能。
D. 使⽤ Amazon CloudFront，并将 S3 存储桶作为其源。
https://examlearn.online
[2026/05]
Question #167
Topic 1
⼀家公司在 Amazon EC2 实例集群上运⾏⽣产应⽤程序。该应⽤程序从 Amazon SQS 队列读取数据并并⾏处理
消息。消息量不可预测，且流量经常出现间歇性波动。该应⽤程序需要持续处理消息，不能出现任何停机时间。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 完全使⽤竞价型实例来处理所需的最⼤容量。
B. 仅使⽤预留实例来处理所需的最⼤容量。
C. 使⽤预留实例作为基本容量，使⽤竞价实例来处理额外的容量。
D. 使⽤预留实例作为基本容量，使⽤按需实例来处理额外容量。
Question #168
⼀个安全团队希望限制对团队所有 AWS 账户中特定服务或操作的访问。所有账户都属于 AWS Organizations 中
的⼀个⼤型组织。该解决⽅案必须具有可扩展性，并且必须有⼀个统⼀的权限管理⼊⼝。
解决⽅案架构师应该如何实现这⼀⽬标？
A. 创建 ACL 以提供对服务或操作的访问权限。
B. 创建⼀个安全组以允许帐户，并将其附加到⽤户组。
C. 在每个账户中创建跨账户⻆⾊，以拒绝访问服务或操作。
D. 在根组织单元中创建服务控制策略，以拒绝访问服务或操作。
Question #169
Topic 1
Topic 1
⼀家公司由于近期遭受⽹络攻击，对其公共 Web 应⽤程序的安全性感到担忧。该应⽤程序使⽤了应⽤程序负载均
衡器 (ALB)。解决⽅案架构师必须降低该应⽤程序遭受 DDoS 攻击的⻛险。
为了满⾜这⼀要求，解决⽅案架构师应该采取哪些措施？
A. 将 Amazon Inspector 代理添加到 ALB。
B. 配置 Amazon Macie 以防⽌攻击。
C. 启⽤ AWS Shield Advanced 以防⽌攻击。
D. 配置 Amazon GuardDuty 来监控 ALB。
https://examlearn.online
[2026/05]
Question #170
Topic 1
⼀家公司的 Web 应⽤程序运⾏在 Amazon EC2 实例上，并位于应⽤程序负载均衡器之后。该公司最近更改了策
略，现在要求该应⽤程序只能从特定国家/地区访问。
哪种配置可以满⾜此要求？
A. 为 EC2 实例配置安全组。
B. 在应⽤程序负载均衡器上配置安全组。
C. 在 VPC 中的应⽤程序负载均衡器上配置 AWS WAF。
D. 为包含 EC2 实例的⼦⽹配置⽹络 ACL。
Question #171
解决⽅案架构师应该如何实现这⼀⽬标？
Topic 1
⼀家公司向⽤户提供 API，该 API 可根据商品价格⾃动查询税费。该公司仅在节假⽇期间会遇到⼤量查询，导致
响应速度变慢。解决⽅案架构师需要设计⼀个可扩展且弹性的解决⽅案。
A. 提供托管在 Amazon EC2 实例上的 API。当发出 API 请求时，EC2 实例会执⾏所需的计算。
B. 使⽤ Amazon API Gateway 设计⼀个 REST API，该 API 接受商品名称作为参数。API Gateway 将商品名
称传递给 AWS Lambda 进⾏税费计算。
C. 创建⼀个应⽤程序负载均衡器，其后端连接两个 Amazon EC2 实例。这两个 EC2 实例将根据接收到的商
品名称计算税费。
D. 使⽤ Amazon API Gateway 设计⼀个 REST API，该 API 连接到托管在 Amazon EC2 实例上的 API。API
Gateway 接收商品名称并将其传递给 EC2 实例以进⾏税费计算。
https://examlearn.online
[2026/05]
Question #172
Topic 1
解决⽅案架构师正在为应⽤程序创建新的 Amazon CloudFront 分发。⽤户提交的部分信息较为敏感。该应⽤程
序使⽤ HTTPS，但还需要额外的安全层。敏感信息应在整个应⽤程序堆栈中受到保护，并且对信息的访问应限制
在特定应⽤程序范围内。
解决⽅案架构师应该采取什么措施？
A. 配置 CloudFront 签名 URL。
B. 配置 CloudFront 签名 cookie。
C. 配置 CloudFront 字段级加密配置⽂件。
D. 配置 CloudFront，并将查看器协议策略的源协议策略设置为“仅限 HTTPS”。
Question #173
Topic 1
⼀家游戏公司在 AWS 上托管了⼀个基于浏览器的应⽤程序。该应⽤程序的⽤户会访问⼤量存储在 Amazon S3 中
的视频和图像。所有⽤户访问的内容都相同。
该应⽤程序越来越受欢迎，全球数百万⽤户都在访问这些媒体⽂件。该公司希望在向⽤户提供这些⽂件的同时，
降低源服务器的负载。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在 Web 服务器前⾯部署 AWS Global Accelerator 加速器。
B. 在 S3 存储桶前⾯部署 Amazon CloudFront Web 分发。
C. 在 Web 服务器前⾯部署 Amazon ElastiCache for Redis 实例。
D. 在 Web 服务器前⾯部署 Amazon ElastiCache for Memcached 实例。
https://examlearn.online
[2026/05]
Question #174
Topic 1
⼀家公司有⼀个多层应⽤程序，该应⽤程序在单个可⽤区内的 Amazon EC2 ⾃动扩展组中运⾏六个前端 Web 服
务器，并由应⽤程序负载均衡器 (ALB) 提供⽀持。解决⽅案架构师需要修改基础架构以实现⾼可⽤性，但不能修
改应⽤程序本身。
解决⽅案架构师应该选择哪种架构来实现⾼可⽤性？
A. 创建⼀个⾃动扩展组，该组在两个区域中分别使⽤三个实例。
B. 修改⾃动扩展组，使其在两个可⽤区中各使⽤三个实例。
C. 创建⼀个⾃动扩展模板，该模板可⽤于在另⼀个区域中快速创建更多实例。
D. 将 Amazon EC2 实例前⾯的 ALB 改为轮询配置，以平衡 Web 层的流量。
Question #175
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家电商公司使⽤ Amazon API Gateway 和 AWS Lambda 函数开发了⼀个订单处理应⽤程序。该应⽤程序将数
据存储在 Amazon Aurora PostgreSQL 数据库中。在最近的⼀次促销活动中，客户订单量突然激增。部分客户遇
到了超时问题，导致应⽤程序⽆法处理这些客户的订单。
解决⽅案架构师发现，由于⼤量连接处于打开状态，数据库的 CPU 和内存使⽤率都很⾼。解决⽅案架构师需要在
尽可能减少对应⽤程序更改的情况下，防⽌超时错误再次发⽣。
A. 为 Lambda 函数配置预置并发。将数据库修改为跨多个 AWS 区域的全局数据库。
B. 使⽤ Amazon RDS Proxy 为数据库创建代理。修改 Lambda 函数，使其使⽤ RDS Proxy 端点⽽不是数据
库端点。
C. 在不同的 AWS 区域中为数据库创建只读副本。使⽤ API ⽹关中的查询字符串参数将流量路由到只读副
本。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据从 Aurora PostgreSQL 迁移到 Amazon DynamoDB。修
改 Lambda 函数以使⽤ DynamoDB 表。
https://examlearn.online
[2026/05]
Question #176
Topic 1
⼀个应⽤程序运⾏在私有⼦⽹中的 Amazon EC2 实例上。该应⽤程序需要访问 Amazon DynamoDB 表。
如何在确保流量不离开 AWS ⽹络的前提下，以最安全的⽅式访问该表？
A. 使⽤ DynamoDB 的 VPC 端点。
B. 在公共⼦⽹中使⽤ NAT ⽹关。
C. 在私有⼦⽹中使⽤ NAT 实例。
D. 使⽤连接到 VPC 的互联⽹⽹关。
Question #177
解决⽅案架构师应该提出什么建议来满⾜这⼀需求？
Topic 1
⼀家娱乐公司使⽤ Amazon DynamoDB 存储媒体元数据。该应⽤程序读取密集型，存在延迟问题。该公司没有
⾜够的⼈⼿来处理额外的运维⼯作，需要在不重新配置应⽤程序的情况下提⾼ DynamoDB 的性能效率。
A. 使⽤ Amazon ElastiCache for Redis。
B. 使⽤ Amazon DynamoDB Accelerator (DAX)。
C. 使⽤ DynamoDB 全局表复制数据。
D. 使⽤启⽤⾃动发现功能的 Amazon ElastiCache for Memcached。
https://examlearn.online
[2026/05]
Question #178
Topic 1
⼀家公司的基础设施由位于同⼀ AWS 区域的 Amazon EC2 实例和 Amazon RDS 数据库实例组成。该公司希望
将数据备份到另⼀个区域。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ AWS Backup 将 EC2 备份和 RDS 备份复制到单独的区域。
B. 使⽤ Amazon 数据⽣命周期管理器 (Amazon DLM) 将 EC2 备份和 RDS 备份复制到单独的区域。
C. 创建 EC2 实例的 Amazon 系统映像 (AMI)。将 AMI 复制到单独的区域。在单独的区域中为 RDS 数据库实
例创建只读副本。
D. 创建 Amazon Elastic Block Store (Amazon EBS) 快照。将 EBS 快照复制到单独的区域。创建 RDS 快
照。将 RDS 快照导出到 Amazon S3。配置 S3 跨区域复制 (CRR) 到单独的区域。
Question #179
为了满⾜此要求，解决⽅案架构师应该怎么做？
Topic 1
解决⽅案架构师需要安全地存储应⽤程序⽤于访问 Amazon RDS 数据库实例的数据库⽤户名和密码。该应⽤程序
运⾏在 Amazon EC2 实例上。解决⽅案架构师希望在 AWS Systems Manager Parameter Store 中创建⼀个安
全参数。
A. 创建⼀个具有参数存储读取权限的 IAM ⻆⾊。允许解密⽤于加密该参数的 AWS Key Management
Service (AWS KMS) 密钥。将此 IAM ⻆⾊分配给 EC2 实例。
B. 创建⼀条 IAM 策略，允许读取参数存储中的参数。允许解密⽤于加密该参数的 AWS Key Management
Service (AWS KMS) 密钥。将此 IAM 策略分配给 EC2 实例。
C. 在参数存储参数和 EC2 实例之间创建 IAM 信任关系。在信任策略中指定 Amazon RDS 作为主体。
D. 在数据库实例和 EC2 实例之间创建 IAM 信任关系。在信任策略中指定 Systems Manager 作为主体。
https://examlearn.online
[2026/05]
Question #180
Topic 1
⼀家公司正在设计⼀个基于 API 的云通信平台。该应⽤程序托管在 Amazon EC2 实例上，并由⽹络负载均衡器
(NLB) 提供⽀持。该公司使⽤ Amazon API Gateway 为外部⽤户提供通过 API 访问该应⽤程序的权限。该公司希
望保护该平台免受 SQL 注⼊等 Web 攻击，并希望检测和缓解⼤规模、复杂的 DDoS 攻击。
哪种解决⽅案组合能够提供最佳保护？（选择两项。）
A. 使⽤ AWS WAF 保护 NLB。
B. 将 AWS Shield Advanced 与 NLB 结合使⽤。
C. 使⽤ AWS WAF 保护 Amazon API Gateway。
D. 将 Amazon GuardDuty 与 AWS Shield Standard 结合使⽤
E. 将 AWS Shield Standard 与 Amazon API Gateway 结合使⽤。
Question #181
解决⽅案架构师应该推荐哪种⽅式来实现微服务之间的通信？
Topic 1
⼀家公司有⼀个运⾏在 Amazon EC2 实例上的传统数据处理应⽤程序。数据按顺序处理，但结果顺序⽆关紧要。
该应⽤程序采⽤单体架构。公司扩展应⽤程序以满⾜不断增⻓的需求的唯⼀⽅法是增加实例的规模。
公司开发⼈员决定重写该应⽤程序，使其在 Amazon Elastic Container Service (Amazon ECS) 上使⽤微服务架
构。
A. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。向数据⽣产者添加代码，并将数据发送
到该队列。向数据消费者添加代码，以处理来⾃该队列的数据。
B. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。向数据⽣产者添加代码，并将通知
发布到该主题。向数据消费者添加代码，使其订阅该主题。
C. 创建⼀个 AWS Lambda 函数来传递消息。在数据⽣产者中添加代码，以使⽤数据对象调⽤ Lambda 函
数。在数据消费者中添加代码，以接收从 Lambda 函数传递的数据对象。
D. 创建⼀个 Amazon DynamoDB 表。启⽤ DynamoDB Streams。在数据⽣产者中添加代码，将数据插⼊到
表中。在数据消费者中添加代码，使⽤ DynamoDB Streams API 检测新的表条⽬并检索数据。
https://examlearn.online
[2026/05]
Question #182
Topic 1
⼀家公司希望将其 MySQL 数据库从本地迁移到 AWS。该公司最近遭遇了⼀次数据库宕机，对业务造成了严重影
响。为了确保此类事件不再发⽣，该公司希望在 AWS 上找到⼀个可靠的数据库解决⽅案，该⽅案能够最⼤限度
地减少数据丢失，并将每笔交易存储在⾄少两个节点上。
哪种解决⽅案符合这些要求？
A. 创建⼀个 Amazon RDS 数据库实例，并将其同步复制到三个可⽤区中的三个节点。
B. 创建⼀个启⽤多可⽤区功能的 Amazon RDS MySQL 数据库实例，以同步复制数据。
C. 创建⼀个 Amazon RDS MySQL 数据库实例，然后在单独的 AWS 区域中创建⼀个只读副本，以同步复制
数据。
D. 创建⼀个安装了 MySQL 引擎的 Amazon EC2 实例，该实例触发⼀个 AWS Lambda 函数，将数据同步复
制到 Amazon RDS MySQL 数据库实例。
Question #183
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在构建⼀个新的动态订购⽹站。该公司希望最⼤限度地减少服务器维护和补丁⼯作。该⽹站必须具有
⾼可⽤性，并且必须能够尽快扩展读写容量以满⾜⽤户需求的变化。
A. 将静态内容托管在 Amazon S3 中。使⽤ Amazon API Gateway 和 AWS Lambda 托管动态内容。使⽤按
需容量的 Amazon DynamoDB 作为数据库。配置 Amazon CloudFront 来分发⽹站内容。
B. 将静态内容托管在 Amazon S3 中。使⽤ Amazon API Gateway 和 AWS Lambda 托管动态内容。使⽤
Amazon Aurora 和 Aurora Auto Scaling 作为数据库。配置 Amazon CloudFront 以交付⽹站内容。
C. 将所有⽹站内容托管在 Amazon EC2 实例上。创建⾃动扩展组以扩展 EC2 实例。使⽤应⽤程序负载均衡
器来分配流量。使⽤预置写⼊容量的 Amazon DynamoDB 数据库。
D. 将所有⽹站内容托管在 Amazon EC2 实例上。创建⾃动扩展组来扩展 EC2 实例。使⽤应⽤程序负载均衡
器来分配流量。数据库使⽤ Amazon Aurora 和 Aurora ⾃动扩展。
https://examlearn.online
[2026/05]
Question #184
Topic 1
⼀家公司拥有⼀个⽤于软件⼯程的 AWS 账户。该 AWS 账户通过⼀对 AWS Direct Connect 连接访问公司内部数
据中⼼。所有⾮ VPC 流量都路由到虚拟专⽤⽹关。
⼀个开发团队最近通过控制台创建了⼀个 AWS Lambda 函数。该开发团队需要允许该函数访问运⾏在公司数据
中⼼私有⼦⽹中的数据库。
哪种解决⽅案能够满⾜这些要求？
A. 配置 Lambda 函数在具有适当安全组的 VPC 中运⾏。
B. 从 AWS 到数据中⼼建⽴ VPN 连接。将 Lambda 函数的流量通过 VPN 路由。
C. 更新 VPC 中的路由表，允许 Lambda 函数通过 Direct Connect 访问本地数据中⼼。
D. 创建弹性 IP 地址。配置 Lambda 函数，使其通过弹性 IP 地址发送流量，⽽⽆需弹性⽹络接⼝。
Question #185
Topic 1
⼀家公司使⽤ Amazon ECS 运⾏⼀个应⽤程序。该应⽤程序会创建原始图像的调整⼤⼩版本，然后调⽤ Amazon
S3 API 将调整⼤⼩后的图像存储在 Amazon S3 中。
解决⽅案架构师如何确保该应⽤程序拥有访问 Amazon S3 的权限？
A. 更新 AWS IAM 中的 S3 ⻆⾊，允许从 Amazon ECS 进⾏读/写访问，然后重新启动容器。
B. 创建⼀个具有 S3 权限的 IAM ⻆⾊，然后将该⻆⾊指定为任务定义中的 taskRoleArn。
C. 创建⼀个安全组，允许从 Amazon ECS 访问 Amazon S3，并更新 ECS 集群使⽤的启动配置。
D. 创建⼀个具有 S3 权限的 IAM ⽤户，然后以该账户登录后重新启动 ECS 集群的 Amazon EC2 实例。
https://examlearn.online
[2026/05]
Question #186
Topic 1
⼀家公司有⼀个基于 Windows 的应⽤程序，需要将其迁移到 AWS。该应⽤程序需要使⽤⼀个共享的 Windows
⽂件系统，该系统连接到多个 Amazon EC2 Windows 实例，⽽这些实例部署在多个可⽤区：
解决⽅案架构师应该如何满⾜此要求？
A. 将 AWS Storage Gateway 配置为卷⽹关模式。将卷挂载到每个 Windows 实例。
B. 配置 Amazon FSx for Windows ⽂件服务器。将 Amazon FSx ⽂件系统挂载到每个 Windows 实例。
C. 使⽤ Amazon Elastic File System (Amazon EFS) 配置⽂件系统。将 EFS ⽂件系统挂载到每个 Windows
实例。
D. 配置所需⼤⼩的 Amazon Elastic Block Store (Amazon EBS) 卷。将每个 EC2 实例连接到该卷。将卷内的
⽂件系统挂载到每个 Windows 实例。
Question #187
哪些解决⽅案符合这些要求？（选择两个。）
Topic 1
⼀家公司正在开发⼀款电⼦商务应⽤，该应⽤将包含负载均衡的前端、基于容器的应⽤以及关系型数据库。解决
⽅案架构师需要创建⼀个⾼可⽤性的解决⽅案，并尽可能减少⼈⼯⼲预。
A. 在多可⽤区模式下创建 Amazon RDS 数据库实例。
B. 在另⼀个可⽤区中创建 Amazon RDS 数据库实例和⼀个或多个副本。
C. 创建⼀个基于 Amazon EC2 实例的 Docker 集群来处理动态应⽤程序负载。
D. 创建⼀个 Amazon Elastic Container Service (Amazon ECS) 集群，启动类型为 Fargate，以处理动态应
⽤程序负载。
E. 创建⼀个 Amazon Elastic Container Service (Amazon ECS) 集群，启动类型为 Amazon EC2，以处理动
态应⽤程序负载。
https://examlearn.online
[2026/05]
Question #188
Topic 1
⼀家公司使⽤ Amazon S3 作为其数据湖。该公司新来了⼀位合作伙伴，该合作伙伴必须使⽤ SFTP 上传数据⽂
件。解决⽅案架构师需要实现⼀个⾼可⽤性的 SFTP 解决⽅案，同时最⼤限度地降低运维开销。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Transfer Family 配置⼀个⽀持 SFTP 的服务器，并设置⼀个可公开访问的终端节点。选择 S3
数据湖作为⽬标位置。
B. 使⽤ Amazon S3 ⽂件⽹关作为 SFTP 服务器。将 S3 ⽂件⽹关端点 URL 公开给新合作伙伴。与新合作伙
伴共享 S3 ⽂件⽹关端点。
C. 在虚拟专⽤⽹络 (VP) 的私有⼦⽹中启动⼀个 Amazon EC2 实例。指示新合作伙伴使⽤ VPN 将⽂件上传到
该 EC2 实例。在该 EC2 实例上运⾏⼀个 cron 作业脚本，将⽂件上传到 S3 数据湖。
D. 在 VPC 的私有⼦⽹中启动 Amazon EC2 实例。在 EC2 实例前部署⽹络负载均衡器 (NLB)。为 NLB 创建
SFTP 监听端⼝。将 NLB 主机名共享给新的合作伙伴。在 EC2 实例上运⾏ cron 作业脚本，将⽂件上传到 S3
数据湖。
Question #189
Topic 1
⼀家公司需要存储合同⽂件。合同有效期为5年。在这5年期间，公司必须确保⽂件不会被覆盖或删除。公司需要
对静态⽂件进⾏加密，并每年⾃动轮换加密密钥。
为了以最⼩的运营开销满⾜这些要求，解决⽅案架构师应该采取哪些步骤组合？（选择两项。）
A. 将⽂档存储在 Amazon S3 中。使⽤ S3 对象锁定的治理模式。
B. 将⽂档存储在 Amazon S3 中。使⽤合规模式下的 S3 对象锁定。
C. 使⽤ Amazon S3 管理的加密密钥 (SSE-S3) 进⾏服务器端加密。配置密钥轮换。
D. 使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥进⾏服务器端加密。配置密钥轮换。
E. 使⽤ AWS Key Management Service (AWS KMS) 和客户提供的（导⼊的）密钥进⾏服务器端加密。配置
密钥轮换。
https://examlearn.online
[2026/05]
Question #190
Topic 1
⼀家公司拥有⼀个基于 Java 和 PHP 的 Web 应⽤程序。该公司计划将该应⽤程序从本地迁移到 AWS。该公司需
要能够频繁地测试新的⽹站功能。此外，该公司还需要⼀个⾼可⽤性、可托管且运维成本极低的解决⽅案。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个 Amazon S3 存储桶。在 S3 存储桶上启⽤静态⽹站托管。将静态内容上传到 S3 存储桶。使⽤
AWS Lambda 处理所有动态内容。
B. 将 Web 应⽤程序部署到 AWS Elastic Beanstalk 环境。使⽤ URL 切换在多个 Elastic Beanstalk 环境之间
切换，以进⾏功能测试。
C. 将 Web 应⽤程序部署到已配置 Java 和 PHP 的 Amazon EC2 实例上。使⽤⾃动扩展组和应⽤程序负载均
衡器来管理⽹站的可⽤性。
D. 将 Web 应⽤程序容器化。将 Web 应⽤程序部署到 Amazon EC2 实例。使⽤ AWS 负载均衡控制器在包含
⽤于测试的新功能的容器之间动态路由流量。
Question #191
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司使⽤订购应⽤程序，将客户信息存储在 Amazon RDS for MySQL 数据库中。在正常⼯作时间内，员⼯
会运⾏⼀次性查询以⽣成报表。由于报表查询运⾏时间过⻓，订单处理过程中会出现超时。公司需要在不影响员
⼯执⾏查询的前提下消除超时问题。
A. 创建只读副本。将报表查询迁移到只读副本。
B. 创建只读副本。将排序应⽤程序分发到主数据库实例和只读副本。
C. 将订购应⽤程序迁移到具有按需容量的 Amazon DynamoDB。
D. 将报告查询安排在⾮⾼峰时段进⾏。
https://examlearn.online
[2026/05]
Question #192
Topic 1
⼀家医院希望为其⼤量的历史书⾯记录创建数字副本。医院每天都会新增数百份⽂档。医院的数据团队将扫描这
些⽂档并将其上传到 AWS 云平台。
解决⽅案架构师必须实现⼀个解决⽅案，⽤于分析这些⽂档、提取医疗信息并存储⽂档，以便应⽤程序可以对数
据运⾏ SQL 查询。该解决⽅案必须最⼤限度地提⾼可扩展性和运⾏效率。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 将⽂档信息写⼊运⾏ MySQL 数据库的 Amazon EC2 实例。
B. 将⽂档信息写⼊ Amazon S3 存储桶。使⽤ Amazon Athena 查询数据。
C. 创建⼀个 Amazon EC2 实例的⾃动扩展组，以运⾏⼀个⾃定义应⽤程序，该应⽤程序处理扫描的⽂件并提
取医疗信息。
D. 创建⼀个 AWS Lambda 函数，当有新⽂档上传时运⾏。使⽤ Amazon Rekognition 将⽂档转换为原始⽂
本。使⽤ Amazon Transcribe Medical 从⽂本中检测并提取相关的医疗信息。
Question #193
解决⽅案架构师应该如何满⾜这⼀要求？
E. 创建⼀个 AWS Lambda 函数，当有新⽂档上传时运⾏。使⽤ Amazon Textract 将⽂档转换为纯⽂本。使
⽤ Amazon Comprehend Medical 从⽂本中检测并提取相关的医疗信息。
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个批处理应⽤程序。该应⽤程序的后端包含多个 Amazon RDS 数据库。
该应⽤程序导致数据库读取次数过多。解决⽅案架构师必须在确保⾼可⽤性的前提下减少数据库读取次数。
A. 添加 Amazon RDS 只读副本。
B. 使⽤ Amazon ElastiCache for Redis。
C. 使⽤ Amazon Route 53 DNS 缓存
D. 使⽤ Amazon ElastiCache 代替 Memcached。
https://examlearn.online
[2026/05]
Question #194
Topic 1
⼀家公司需要在 AWS 上运⾏⼀个关键应⽤程序。该公司需要使⽤ Amazon EC2 作为该应⽤程序的数据库。该数
据库必须具备⾼可⽤性，并且在发⽣故障事件时必须能够⾃动故障转移。
哪种解决⽅案能够满⾜这些要求？
A. 启动两个 EC2 实例，每个实例位于同⼀ AWS 区域的不同可⽤区。在两个 EC2 实例上都安装数据库。将这
两个 EC2 实例配置为集群。设置数据库复制。
B. 在可⽤区中启动⼀个 EC2 实例。将数据库安装到该 EC2 实例上。使⽤ Amazon 系统映像 (AMI) 备份数
据。如果发⽣中断事件，请使⽤ AWS CloudFormation ⾃动配置 EC2 实例。
C. 启动两个 EC2 实例，每个实例位于不同的 AWS 区域。在两个 EC2 实例上安装数据库。设置数据库复制。
将数据库故障转移到第⼆个区域。
D. 在可⽤区中启动⼀个 EC2 实例。将数据库安装到该 EC2 实例上。使⽤ Amazon 系统映像 (AMI) 备份数
据。如果发⽣中断事件，请使⽤ EC2 ⾃动恢复功能来恢复实例。
Question #195
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司的订单系统将客户的订单请求发送到 Amazon EC2 实例。EC2 实例处理订单，然后将订单存储在
Amazon RDS 数据库中。⽤户反映，当系统发⽣故障时，他们必须重新处理订单。该公司希望拥有⼀个弹性解决
⽅案，能够在系统中断时⾃动处理订单。
A. 将 EC2 实例移⾄⾃动扩展组。创建 Amazon EventBridge（Amazon CloudWatch Events）规则，以定位
Amazon Elastic Container Service（Amazon ECS）任务。
B. 将 EC2 实例移⾄应⽤程序负载均衡器 (ALB) 后⾯的⾃动扩展组。更新订单系统，使其向 ALB 端点发送消
息。
C. 将 EC2 实例移⾄⾃动扩展组。配置订单系统，使其将消息发送到 Amazon Simple Queue Service
(Amazon SQS) 队列。配置 EC2 实例，使其从队列中消费消息。
D. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。创建⼀个 AWS Lambda 函数，并
将该函数订阅到该 SNS 主题。配置订单系统以向该 SNS 主题发送消息。使⽤ AWS Systems Manager Run
Command 向 EC2 实例发送命令以处理这些消息。
https://examlearn.online
[2026/05]
Question #196
Topic 1
⼀家公司在庞⼤的 Amazon EC2 实例集群上运⾏⼀个应⽤程序。该应⽤程序会读取和写⼊ Amazon DynamoDB
表中的数据。DynamoDB 表的⼤⼩持续增⻓，但应⽤程序只需要最近 30 天的数据。该公司需要⼀个能够最⼤限
度降低成本和开发⼯作量的解决⽅案。
哪个解决⽅案符合这些要求？
A. 使⽤ AWS CloudFormation 模板部署完整的解决⽅案。每 30 天重新部署⼀次 CloudFormation 堆栈，并
删除原始堆栈。
B. 使⽤从 AWS Marketplace 下载的监控应⽤程序运⾏ EC2 实例。配置该监控应⽤程序，使其使⽤ Amazon
DynamoDB Streams 存储表中新条⽬的创建时间戳。使⽤运⾏在该 EC2 实例上的脚本删除时间戳超过 30 天
的条⽬。
C. 配置 Amazon DynamoDB Streams，使其在表中创建新项时调⽤ AWS Lambda 函数。配置 Lambda 函
数，使其删除表中超过 30 天的项。
D. 扩展应⽤程序，为表中创建的每个新项添加⼀个属性，该属性的值为当前时间戳加 30 天。配置
DynamoDB 将该属性⽤作 TTL 属性。
Question #197
Topic 1
⼀家公司有⼀个运⾏在本地 Windows 服务器上的 Microsoft .NET 应⽤程序。该应⽤程序使⽤ Oracle 数据库标
准版服务器存储数据。该公司计划将其迁移到 AWS，并希望在迁移过程中尽可能减少开发变更。AWS 应⽤程序
环境需要具备⾼可⽤性。
为了满⾜这些要求，该公司应该采取哪些措施组合？（选择两项。）
A. 将应⽤程序重构为⽆服务器架构，使⽤运⾏ .NET Core 的 AWS Lambda 函数。
B. 在 AWS Elastic Beanstalk 上，使⽤ .NET 平台，以多可⽤区部署⽅式重新托管应⽤程序。
C. 使⽤ Amazon Linux Amazon Machine Image (AMI) 将应⽤程序重新平台化，使其在 Amazon EC2 上运
⾏。
D. 在多可⽤区部署中，使⽤ AWS 数据库迁移服务 (AWS DMS) 将 Oracle 数据库迁移到 Amazon
DynamoDB。
E. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将 Oracle 数据库从多可⽤区部署迁移到 Amazon RDS 上的
Oracle 数据库。
https://examlearn.online
[2026/05]
Question #198
Topic 1
⼀家公司在本地数据中⼼的 Kubernetes 集群上运⾏容器化应⽤程序，并使⽤ MongoDB 数据库进⾏数据存储。
该公司希望将部分环境迁移到 AWS，但⽬前⽆法更改代码或部署⽅式。该公司需要⼀个能够最⼤限度降低运维开
销的解决⽅案。
哪个解决⽅案符合这些要求？
A. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 Amazon EC2 ⼯作节点进⾏计算，并使⽤
EC2 上的 MongoDB 进⾏数据存储。
B. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 AWS Fargate 进⾏计算，并使⽤ Amazon
DynamoDB 进⾏数据存储。
C. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 Amazon EC2 ⼯作节点进⾏计算，并使⽤
Amazon DynamoDB 进⾏数据存储。
D. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 AWS Fargate 进⾏计算，并使⽤ Amazon
DocumentDB (与 MongoDB 兼容) 进⾏数据存储。
Question #199
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家电话营销公司正在AWS上设计其客户呼叫中⼼功能。该公司需要⼀个能够提供多说话⼈识别并⽣成转录⽂件
的解决⽅案。该公司希望查询这些转录⽂件以分析业务模式。出于审计⽬的，转录⽂件必须保存7年。
A. 使⽤ Amazon Rekognition 进⾏多说话⼈识别。将转录⽂件存储在 Amazon S3 中。使⽤机器学习模型进
⾏转录⽂件分析。
B. 使⽤ Amazon Transcribe 进⾏多说话⼈识别。使⽤ Amazon Athena 进⾏转录⽂件分析。
C. 使⽤ Amazon Translate 进⾏多说话⼈识别。将转录⽂件存储在 Amazon Redshift 中。使⽤ SQL 查询进
⾏转录⽂件分析。
D. 使⽤ Amazon Rekognition 进⾏多说话⼈识别。将转录⽂件存储在 Amazon S3 中。使⽤ Amazon
Textract 进⾏转录⽂件分析。
https://examlearn.online
[2026/05]
Question #200
Topic 1
⼀家公司将其应⽤程序托管在 AWS 上。该公司使⽤ Amazon Cognito 管理⽤户。当⽤户登录应⽤程序时，应⽤
程序会通过托管在 Amazon API Gateway 中的 REST API 从 Amazon DynamoDB 获取所需数据。该公司希望获
得⼀个 AWS 托管解决⽅案，以控制对 REST API 的访问，从⽽减少开发⼯作量。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 配置 AWS Lambda 函数作为 API Gateway 中的授权器，以验证哪个⽤户发出了请求。
B. 为每个⽤户创建并分配⼀个 API 密钥，该密钥必须随每个请求⼀起发送。使⽤ AWS Lambda 函数验证该
密钥。
C. 在每个请求的标头中发送⽤户的电⼦邮件地址。调⽤ AWS Lambda 函数来验证具有该电⼦邮件地址的⽤
户是否拥有适当的访问权限。
D. 在 API Gateway 中配置 Amazon Cognito ⽤户池授权器，以允许 Amazon Cognito 验证每个请求。
Question #201
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司正在开发⼀项⾯向移动应⽤⽤户的营销传播服务。该公司需要通过短信服务 (SMS) 向⽤户发送确认信
息。⽤户必须能够回复这些短信。公司需要将⽤户的回复保存⼀年以供分析。
A. 创建 Amazon Connect 联系⼈流程以发送短信。使⽤ AWS Lambda 处理回复。
B. 构建 Amazon Pinpoint 旅程。配置 Amazon Pinpoint 将事件发送到 Amazon Kinesis 数据流以进⾏分析和
存档。
C. 使⽤ Amazon Simple Queue Service (Amazon SQS) 分发短信。使⽤ AWS Lambda 处理回复。
D. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) FIFO 主题。将 Amazon Kinesis 数据流订
阅到该 SNS 主题，以便进⾏分析和归档。
https://examlearn.online
[2026/05]
Question #202
Topic 1
⼀家公司计划将其数据迁移到 Amazon S3 存储桶。数据在存储到 S3 存储桶时必须加密。此外，加密密钥必须
每年⾃动轮换。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 将数据移动到 S3 存储桶。使⽤ Amazon S3 管理的加密密钥 (SSE-S3) 进⾏服务器端加密。使⽤ SSE-S3
加密密钥的内置密钥轮换机制。
B. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。启⽤⾃动密钥轮换。将 S3 存储桶的默
认加密⾏为设置为使⽤客户管理的 KMS 密钥。将数据移动到 S3 存储桶。
C. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。将 S3 存储桶的默认加密⾏为设置为使
⽤该客户管理的 KMS 密钥。将数据迁移到 S3 存储桶。每年⼿动轮换 KMS 密钥。
D. 在将数据移动到 S3 存储桶之前，使⽤客户密钥材料对数据进⾏加密。创建⼀个不包含密钥材料的 AWS
Key Management Service (AWS KMS) 密钥。将客户密钥材料导⼊到 KMS 密钥中。启⽤⾃动密钥轮换。
Question #203
Topic 1
⼀家⾦融公司的客户通过发送短信预约财务顾问。⼀个运⾏在 Amazon EC2 实例上的 Web 应⽤程序接收这些预
约请求。短信通过该 Web 应⽤程序发布到 Amazon Simple Queue Service (Amazon SQS) 队列。另⼀个运⾏在
EC2 实例上的应⽤程序随后向客户发送会议邀请和会议确认电⼦邮件。成功安排会议后，该应⽤程序会将会议信
息存储在 Amazon DynamoDB 数据库中。
随着公司规模的扩⼤，客户反映收到会议邀请的时间越来越⻓。
解决⽅案架构师应该如何建议来解决这个问题？
A. 在 DynamoDB 数据库前⾯添加 DynamoDB Accelerator (DAX) 集群。
B. 在接受预约请求的 Web 应⽤程序前⾯添加 Amazon API Gateway API。
C. 添加 Amazon CloudFront 分发。将源设置为接受预约请求的 Web 应⽤程序。
D. 为发送会议邀请的应⽤程序添加⼀个⾃动伸缩组。配置⾃动伸缩组，使其根据 SQS 队列的深度进⾏伸缩。
https://examlearn.online
[2026/05]
Question #204
Topic 1
⼀家在线零售公司拥有超过 5000 万活跃⽤户，每天收到超过 25000 笔订单。该公司收集⽤户的购买数据并将
其存储在 Amazon S3 中。其他⽤户数据则存储在 Amazon RDS 中。
该公司希望将所有数据提供给各个团队，以便他们进⾏数据分析。该解决⽅案必须能够对数据进⾏细粒度的权限
管理，并且必须最⼤限度地降低运营成本。
哪种解决⽅案能够满⾜这些要求？
A. 将采购数据迁移到 Amazon RDS 并直接写⼊。使⽤ RDS 访问控制来限制访问权限。
B. 安排⼀个 AWS Lambda 函数定期将数据从 Amazon RDS 复制到 Amazon S3。创建 AWS Glue 爬⾍。使
⽤ Amazon Athena 查询数据。使⽤ S3 策略限制访问权限。
C. 使⽤ AWS Lake Formation 创建数据湖。创建到 Amazon RDS 的 AWS Glue JDBC 连接。在 Lake
Formation 中注册 S3 存储桶。使⽤ Lake Formation 访问控制来限制访问权限。
D. 创建 Amazon Redshift 集群。安排⼀个 AWS Lambda 函数定期将数据从 Amazon S3 和 Amazon RDS 复
制到 Amazon Redshift。使⽤ Amazon Redshift 访问控制来限制访问权限。
Question #205
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在⾃有数据中⼼托管了⼀个营销⽹站。该⽹站由静态⽂档组成，运⾏在单台服务器上。管理员不经常更
新⽹站内容，并使⽤ SFTP 客户端上传新⽂档。
该公司决定将⽹站托管在 AWS 上，并使⽤ Amazon CloudFront。该公司的解决⽅案架构师创建了⼀个
CloudFront 分发。解决⽅案架构师必须设计出最具成本效益和弹性的⽹站托管架构，作为 CloudFront 源站。
A. 使⽤ Amazon Lightsail 创建虚拟服务器。在 Lightsail 实例中配置 Web 服务器。使⽤ SFTP 客户端上传⽹
站内容。
B. 为 Amazon EC2 实例创建 AWS ⾃动扩展组。使⽤应⽤程序负载均衡器。使⽤ SFTP 客户端上传⽹站内
容。
C. 创建⼀个私有的 Amazon S3 存储桶。使⽤ S3 存储桶策略允许 CloudFront 源访问身份 (OAI) 访问。使⽤
AWS CLI 上传⽹站内容。
D. 创建⼀个公共的 Amazon S3 存储桶。配置 AWS Transfer 以⽀持 SFTP。配置 S3 存储桶⽤于⽹站托管。
使⽤ SFTP 客户端上传⽹站内容。
https://examlearn.online
[2026/05]
Question #206
Topic 1
⼀家公司需要管理 Amazon 系统映像 (AMI)。该公司⽬前将 AMI 复制到创建 AMI 的同⼀ AWS 区域。该公司需要
设计⼀个应⽤程序，⽤于捕获 AWS API 调⽤，并在其账户中调⽤ Amazon EC2 CreateImage API 操作时发送警
报。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个 AWS Lambda 函数来查询 AWS CloudTrail ⽇志，并在检测到 CreateImage API 调⽤时发送警
报。
B. 配置 AWS CloudTrail，使其在更新的⽇志发送到 Amazon S3 时发出 Amazon Simple Notification
Service (Amazon SNS) 通知。使⽤ Amazon Athena 创建⼀个新表，并在检测到 API 调⽤时查询
CreateImage。
C. 为 CreateImage API 调⽤创建 Amazon EventBridge（Amazon CloudWatch Events）规则。将⽬标配置
为 Amazon Simple Notification Service（Amazon SNS）主题，以便在检测到 CreateImage API 调⽤时发
送警报。
D. 将 Amazon Simple Queue Service (Amazon SQS) FIFO 队列配置为 AWS CloudTrail ⽇志的⽬标。创建
⼀个 AWS Lambda 函数，以便在检测到 CreateImage API 调⽤时向 Amazon Simple Notification Service
(Amazon SNS) 主题发送警报。
Question #207
Topic 1
⼀家公司拥有⼀个异步 API，⽤于接收⽤户请求，并根据请求类型将请求分发到相应的微服务进⾏处理。该公司
使⽤ Amazon API Gateway 部署 API 前端，并使⽤ AWS Lambda 函数调⽤ Amazon DynamoDB 来存储⽤户请
求，然后再将其分发到处理微服务。
该公司已在预算范围内配置了尽可能多的 DynamoDB 吞吐量，但仍然遇到可⽤性问题，导致⽤户请求丢失。
解决⽅案架构师应该如何解决这个问题，才能在不影响现有⽤户的情况下解决此问题？
A. 在 API ⽹关上添加服务器端限速限制。
B. 使⽤ DynamoDB Accelerator (DAX) 和 Lambda 来缓冲对 DynamoDB 的写⼊。
C. 在 DynamoDB 中为包含⽤户请求的表创建⼆级索引。
D. 使⽤ Amazon Simple Queue Service (Amazon SQS) 队列和 Lambda 来缓冲对 DynamoDB 的写⼊。
https://examlearn.online
[2026/05]
Question #208
Topic 1
⼀家公司需要将数据从 Amazon EC2 实例迁移到 Amazon S3 存储桶。该公司必须确保没有任何 API 调⽤和数据
通过公共互联⽹路由。只有 EC2 实例才能访问 S3 存储桶并上传数据。
哪种解决⽅案能够满⾜这些要求？
A. 在 EC2 实例所在的⼦⽹中为 Amazon S3 创建⼀个接⼝ VPC 终端节点。将资源策略附加到 S3 存储桶，仅
允许 EC2 实例的 IAM ⻆⾊访问。
B. 在 EC2 实例所在的可⽤区中，为 Amazon S3 创建⽹关 VPC 终端节点。将相应的安全组附加到该终端节
点。将资源策略附加到 S3 存储桶，仅允许 EC2 实例的 IAM ⻆⾊访问。
C. 在 EC2 实例内部运⾏ nslookup ⼯具，获取 S3 存储桶服务 API 端点的私有 IP 地址。在 VPC 路由表中创
建⼀条路由，为 EC2 实例提供访问 S3 存储桶的权限。为 S3 存储桶附加资源策略，仅允许 EC2 实例的 IAM
⻆⾊访问。
D. 使⽤ AWS 提供的公开 ip-ranges.json ⽂件获取 S3 存储桶服务 API 端点的私有 IP 地址。在 VPC 路由表
中创建⼀条路由，为 EC2 实例提供对 S3 存储桶的访问权限。为 S3 存储桶附加资源策略，仅允许 EC2 实例
的 IAM ⻆⾊访问。
Question #209
Topic 1
⼀位解决⽅案架构师正在设计⼀个部署到 AWS 云的新应⽤程序的架构。该应⽤程序将在 Amazon EC2 按需实例
上运⾏，并可跨多个可⽤区⾃动扩展。EC2 实例会在⼀天中频繁地进⾏扩展和缩减。应⽤程序负载均衡器 (ALB)
将负责负载分配。该架构需要⽀持分布式会话数据管理。公司愿意在必要时修改代码。
解决⽅案架构师应该如何确保该架构⽀持分布式会话数据管理？
A. 使⽤ Amazon ElastiCache 管理和存储会话数据。
B. 使⽤ ALB 的会话亲和性（粘性会话）来管理会话数据。
C. 使⽤ AWS Systems Manager 中的 Session Manager 来管理会话。
D. 使⽤ AWS 安全令牌服务 (AWS STS) 中的 GetSessionToken API 操作来管理会话。
https://examlearn.online
[2026/05]
Question #210
Topic 1
⼀家公司提供快速增⻓的⻝品配送服务。由于业务增⻓，该公司的订单处理系统在⾼峰时段⾯临扩展性问题。⽬
前的架构包括：
• ⼀组运⾏在 Amazon EC2 Auto Scaling 组中的 Amazon EC2 实例，⽤于从应⽤程序收集订单
；• 另⼀组运⾏在 Amazon EC2 Auto Scaling 组中的 EC2 实例，⽤于处理订单。
订单收集过程很快，但订单处理过程可能需要更⻓时间。数据不能因扩展事件⽽丢失。
解决⽅案架构师必须确保订单收集过程和订单处理过程在⾼峰时段都能正常扩展。该解决⽅案必须优化公司 AWS
资源的利⽤率。
哪个解决⽅案满⾜这些要求？
A. 使⽤ Amazon CloudWatch 指标监控 Auto Scaling 组中每个实例的 CPU 使⽤情况。根据峰值⼯作负载值
配置每个 Auto Scaling 组的最⼩容量。
B. 使⽤ Amazon CloudWatch 指标监控 Auto Scaling 组中每个实例的 CPU 使⽤情况。配置 CloudWatch 警
报，以调⽤ Amazon Simple Notification Service (Amazon SNS) 主题，从⽽按需创建额外的 Auto Scaling
组。
C. 配置两个 Amazon Simple Queue Service (Amazon SQS) 队列：⼀个⽤于订单收集，另⼀个⽤于订单履
⾏。配置 EC2 实例轮询各⾃的队列。根据队列发送的通知扩展⾃动扩展组。
D. 配置两个 Amazon Simple Queue Service (Amazon SQS) 队列：⼀个⽤于订单收集，另⼀个⽤于订单履
⾏。配置 EC2 实例轮询各⾃的队列。创建⼀个基于每个实例积压订单量的指标。根据此指标扩展 Auto
Scaling 组。
Question #211
哪个解决⽅案满⾜这些要求？
Topic 1
⼀家公司托管多个⽣产应⽤程序。其中⼀个应⽤程序使⽤了来⾃多个 AWS 区域的 Amazon EC2、AWS
Lambda、Amazon RDS、Amazon Simple Notification Service (Amazon SNS) 和 Amazon Simple Queue
Service (Amazon SQS) 的资源。所有公司资源都带有名为“application”的标签，并对应⼀个与每个应⽤程序对
应的值。解决⽅案架构师必须提供最快捷的⽅法来识别所有已标记的组件。
A. 使⽤ AWS CloudTrail ⽣成带有应⽤程序标签的资源列表。
B. 使⽤ AWS CLI 查询所有区域中的每个服务，以报告已标记的组件。
C. 在 Amazon CloudWatch Logs Insights 中运⾏查询，以报告具有 application 标签的组件。
D. 使⽤ AWS 资源组标签编辑器运⾏查询，以报告具有应⽤程序标签的全局资源。
https://examlearn.online
[2026/05]
Question #212
Topic 1
⼀家公司需要每天将其数据库导出到 Amazon S3，供其他团队访问。导出的对象⼤⼩在 2 GB 到 5 GB 之间。数
据的 S3 访问模式变化多端且更新迅速。数据必须能够⽴即访问，并且必须保持可访问状态⻓达 3 个⽉。该公司
需要最具成本效益的解决⽅案，且不会增加检索时间。
该公司应该使⽤哪种 S3 存储类别来满⾜这些要求？
A. S3智能分层
B. S3 冰川即时检索
C. S3 标准
D. S3 标准-不频繁访问 (S3 标准-IA)
Question #213
解决⽅案架构师应该提出哪些建议来满⾜这些要求？
Topic 1
⼀家公司正在开发⼀款新的移动应⽤。该公司必须实施适当的流量过滤，以保护其应⽤负载均衡器 (ALB) 免受常
⻅的应⽤层攻击，例如跨站脚本攻击或 SQL 注⼊。该公司的基础设施和运维⼈员有限。该公司需要减少其在管
理、更新和保护其 AWS 环境服务器⽅⾯的责任。
A. 配置 AWS WAF 规则并将其与 ALB 关联。
B. 使⽤启⽤公共托管的 Amazon S3 部署应⽤程序。
C. 部署 AWS Shield Advanced 并将 ALB 添加为受保护资源。
D. 创建⼀个新的 ALB，将流量定向到运⾏第三⽅防⽕墙的 Amazon EC2 实例，然后该防⽕墙将流量传递给当
前的 ALB。
https://examlearn.online
[2026/05]
Question #214
Topic 1
⼀家公司的报表系统每天向 Amazon S3 存储桶发送数百个 .csv ⽂件。该公司必须将这些⽂件转换为 Apache
Parquet 格式，并将转换后的⽂件存储在转换后的数据存储桶中。
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
A. 创建⼀个已安装 Apache Spark 的 Amazon EMR 集群。编写⼀个 Spark 应⽤程序来转换数据。使⽤ EMR
⽂件系统 (EMRFS) 将⽂件写⼊转换后的数据桶。
B. 创建 AWS Glue 爬⾍程序以发现数据。创建 AWS Glue 提取、转换和加载 (ETL) 作业以转换数据。在输出
步骤中指定转换后的数据存储桶。
C. 使⽤ AWS Batch 创建 Bash 语法的作业定义，以转换数据并将数据输出到转换后的数据存储桶。使⽤该作
业定义提交作业。将作业类型指定为数组作业。
D. 创建⼀个 AWS Lambda 函数来转换数据，并将转换后的数据输出到 S3 存储桶。为该 S3 存储桶配置事件
通知。将 Lambda 函数指定为事件通知的⽬标位置。
Question #215
解决⽅案架构师应该如何以最低成本迁移和存储这些数据？
Archive。
Glacier。
Topic 1
⼀家公司在其数据中⼼的⽹络附加存储 (NAS) 中存储了 700 TB 的备份数据。这些备份数据需要满⾜不频繁的监
管要求，并且必须保留 7 年。该公司决定将这些备份数据从其数据中⼼迁移到 AWS。迁移必须在 1 个⽉内完成。
该公司在其公共互联⽹连接上拥有 500 Mbps 的专⽤带宽可⽤于数据传输。
A. 订购 AWS Snowball 设备以传输数据。使⽤⽣命周期策略将⽂件迁移到 Amazon S3 Glacier Deep
B. 在数据中⼼和 Amazon VPC 之间部署 VPN 连接。使⽤ AWS CLI 将数据从本地复制到 Amazon S3
C. 提供 500 Mbps 的 AWS Direct Connect 连接，并将数据传输到 Amazon S3。使⽤⽣命周期策略将⽂件
迁移到 Amazon S3 Glacier Deep Archive。
D. 使⽤ AWS DataSync 传输数据，并在本地部署 DataSync 代理。使⽤ DataSync 任务将⽂件从本地 NAS
存储复制到 Amazon S3 Glacier。
https://examlearn.online
[2026/05]
Question #216
Topic 1
⼀家公司拥有⼀个⽆服务器⽹站，该⽹站在 Amazon S3 存储桶中存储了数百万个对象。该公司使⽤该 S3 存储
桶作为 Amazon CloudFront 分发的源。在加载对象之前，该公司没有对 S3 存储桶进⾏加密。解决⽅案架构师需
要为所有现有对象以及将来添加到 S3 存储桶的所有对象启⽤加密。
哪种解决⽅案能够以最少的⼯作量满⾜这些要求？
A. 创建⼀个新的 S3 存储桶。启⽤新 S3 存储桶的默认加密设置。将所有现有对象下载到临时本地存储。将这
些对象上传到新的 S3 存储桶。
B. 启⽤ S3 存储桶的默认加密设置。使⽤ S3 清单功能创建⼀个 .csv ⽂件，列出所有未加密的对象。运⾏⼀
个 S3 批量操作作业，使⽤ copy 命令加密这些对象。
C. 使⽤ AWS Key Management Service (AWS KMS) 创建新的加密密钥。更改 S3 存储桶的设置，使⽤
AWS KMS 管理的加密密钥进⾏服务器端加密 (SSE-KMS)。启⽤ S3 存储桶的版本控制。
D. 在 AWS 管理控制台中导航⾄ Amazon S3。浏览 S3 存储桶中的对象。按加密字段排序。选择每个未加密
的对象。使⽤“修改”按钮将默认加密设置应⽤于 S3 存储桶中的每个未加密对象。
Question #217
解决⽅案架构师应该如何满⾜这些要求？
AWS 区域中创建 Aurora 副本。
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个全球 Web 应⽤程序，该实例位于应⽤程序负载均衡器 (APP) 之后。该
应⽤程序将数据存储在 Amazon Aurora 中。该公司需要创建⼀个灾难恢复解决⽅案，能够承受最多 30 分钟的停
机时间和潜在的数据丢失。该解决⽅案⽆需在主基础设施运⾏正常时处理负载。
A. 部署应⽤程序，并确保所需的基础设施元素就绪。使⽤ Amazon Route 53 配置主备故障转移。在第⼆个
B. 在第⼆个 AWS 区域中托管⼀个缩减规模的应⽤程序部署。使⽤ Amazon Route 53 配置主动-主动故障转
移。在第⼆个区域中创建 Aurora 副本。
C. 在第⼆个 AWS 区域中复制主基础设施。使⽤ Amazon Route 53 配置主动-主动故障转移。创建⼀个
Aurora 数据库，并从最新快照进⾏恢复。
D. 使⽤ AWS Backup 备份数据。利⽤备份数据在第⼆个 AWS 区域中创建所需的基础设施。使⽤ Amazon
Route 53 配置主备故障转移。在第⼆个区域中创建 Aurora 的第⼆个主实例。
https://examlearn.online
[2026/05]
Question #218
Topic 1
⼀家公司在公有⼦⽹的 Amazon EC2 实例上运⾏着⼀台 Web 服务器，该实例拥有弹性 IP 地址。默认安全组已分
配给该 EC2 实例。默认⽹络 ACL 已被修改，以阻⽌所有流量。解决⽅案架构师需要使 Web 服务器能够通过
443 端⼝从任何位置访问。
以下哪两项步骤组合可以实现此⽬标？
A. 创建⼀个安全组，并添加⼀条规则，允许来⾃源 0.0.0.0/0 的 TCP 端⼝ 443。
B. 创建⼀个安全组，并添加⼀条规则，允许 TCP 端⼝ 443 到⽬标 0.0.0.0/0。
C. 更新⽹络 ACL，允许来⾃源 0.0.0.0/0 的 TCP 端⼝ 443。
D. 更新⽹络 ACL，允许从源 0.0.0.0/0 到⽬标 0.0.0.0/0 的⼊站/出站 TCP 端⼝ 443。
E. 更新⽹络 ACL，允许从源 0.0.0.0/0 ⼊站 TCP 端⼝ 443 和到⽬标 0.0.0.0/0 出站 TCP 端⼝ 32768
65535。
Question #219
哪种解决⽅案能够以最⾼效的⽅式解决这些问题？
Topic 1
⼀家公司的应⽤程序出现性能问题。该应⽤程序是有状态的，需要在 Amazon EC2 实例上完成内存任务。该公司
使⽤ AWS CloudFormation 部署基础设施，并采⽤了 M5 EC2 实例系列。随着流量增加，应⽤程序性能下降。
⽤户反映在访问应⽤程序时遇到延迟。
A. 将 EC2 实例替换为运⾏在⾃动扩展组中的 T3 EC2 实例。使⽤ AWS 管理控制台进⾏更改。
B. 修改 CloudFormation 模板，使 EC2 实例在⾃动扩展组中运⾏。必要时，⼿动增加⾃动扩展组的期望容量
和最⼤容量。
C. 修改 CloudFormation 模板。将 EC2 实例替换为 R5 EC2 实例。使⽤ Amazon CloudWatch 内置的 EC2
内存指标来跟踪应⽤程序性能，以便进⾏未来的容量规划。
D. 修改 CloudFormation 模板。将 EC2 实例替换为 R5 EC2 实例。在 EC2 实例上部署 Amazon
CloudWatch 代理，以⽣成⾃定义应⽤程序延迟指标，⽤于未来的容量规划。
https://examlearn.online
[2026/05]
Question #220
Topic 1
⼀位解决⽅案架构师正在使⽤ Amazon API Gateway 设计⼀个新的 API，该 API 将接收来⾃⽤户的请求。请求量
波动很⼤；有时⼏个⼩时都收不到任何请求。数据处理将异步进⾏，但应在请求发出后⼏秒钟内完成。
为了以最低成本满⾜需求，解决⽅案架构师应该让 API 调⽤哪种计算服务？
A. AWS Glue 作业
B. AWS Lambda 函数
C. 托管在 Amazon Elastic Kubernetes Service (Amazon EKS) 中的容器化服务
D. 托管在 Amazon ECS 中的容器化服务，使⽤ Amazon EC2
Question #221
Topic 1
⼀家公司在多个 Amazon Linux EC2 实例上运⾏⼀个应⽤程序。出于合规性要求，该公司必须保留所有应⽤程序
⽇志⽂件 7 年。这些⽇志⽂件将由⼀个报告⼯具进⾏分析，该⼯具必须能够同时访问所有⽂件。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. Amazon Elastic Block Store (Amazon EBS)
B. Amazon Elastic File System (Amazon EFS)
C. Amazon EC2 实例存储
D. 亚⻢逊S3
https://examlearn.online
[2026/05]
Question #222
Topic 1
⼀家公司聘请了⼀家外部供应商在其AWS账户中执⾏⼯作。该供应商使⽤⼀款⾃动化⼯具，该⼯具托管在供应商
拥有的AWS账户中。该供应商没有访问公司AWS账户的IAM权限。
解决⽅案架构师应该如何授予该供应商此访问权限？
A. 在公司账户中创建⼀个 IAM ⻆⾊，并将访问权限委派给供应商的 IAM ⻆⾊。为该⻆⾊附加供应商所需的相
应 IAM 策略。
B. 在公司账户中创建⼀个 IAM ⽤户，并设置符合密码复杂度要求的密码。为该⽤户附加供应商要求的相应
IAM 策略和权限。
C. 在公司账户中创建⼀个 IAM 组。将供应商账户中的⼯具 IAM ⽤户添加到该组。为该组附加供应商所需的相
应 IAM 策略和权限。
D. 在 IAM 控制台中选择“AWS 账户”作为提供商类型，创建⼀个新的身份提供商。提供供应商的 AWS 账户 ID
和⽤户名。将供应商所需的相应 IAM 策略附加到新提供商，以授予其所需的权限。
Question #223
Topic 1
⼀家公司已将⼀个 Java Spring Boot 应⽤程序部署为 Pod，该 Pod 运⾏在私有⼦⽹中的 Amazon Elastic
Kubernetes Service (Amazon EKS) 上。该应⽤程序需要向 Amazon DynamoDB 表写⼊数据。解决⽅案架构师
必须确保应⽤程序能够在不向互联⽹暴露流量的情况下与 DynamoDB 表进⾏交互。
解决⽅案架构师应采取哪些步骤组合来实现此⽬标？（选择两项。）
A. 将具有⾜够权限的 IAM ⻆⾊附加到 EKS pod。
B. 将具有⾜够权限的 IAM ⽤户附加到 EKS pod。
C. 允许通过私有⼦⽹的⽹络 ACL 向 DynamoDB 表建⽴出站连接。
D. 为 DynamoDB 创建 VPC 端点。
E. 将访问密钥嵌⼊ Java Spring Boot 代码中。
https://examlearn.online
[2026/05]
Question #224
Topic 1
⼀家公司最近将其 Web 应⽤程序迁移到 AWS，⽅法是将应⽤程序重新托管在单个 AWS 区域中的 Amazon EC2
实例上。该公司希望重新设计其应⽤程序架构，使其具有⾼可⽤性和容错性。流量必须随机到达所有正在运⾏的
EC2 实例。
为了满⾜这些要求，该公司应该采取哪些步骤组合？（选择两项。）
A. 创建 Amazon Route 53 故障转移路由策略。
B. 创建 Amazon Route 53 加权路由策略。
C. 创建 Amazon Route 53 多值应答路由策略。
D. 启动三个 EC2 实例：两个实例位于⼀个可⽤区，⼀个实例位于另⼀个可⽤区。
E. 启动四个 EC2 实例：两个实例位于⼀个可⽤区，两个实例位于另⼀个可⽤区。
Question #225
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
Topic 1
⼀家媒体公司在本地收集和分析⽤户活动数据。该公司希望将此功能迁移到 AWS。⽤户活动数据存储将持续增
⻓，最终达到 PB 级。该公司需要构建⼀个⾼可⽤性的数据采集解决⽅案，以便使⽤ SQL 对现有数据和新数据进
⾏按需分析。
A. 将活动数据发送到 Amazon Kinesis 数据流。配置该数据流，使其将数据传输到 Amazon S3 存储桶。
B. 将活动数据发送到 Amazon Kinesis Data Firehose 传输流。配置该流以将数据传输到 Amazon Redshift
集群。
C. 将活动数据放⼊ Amazon S3 存储桶中。配置 Amazon S3，以便在数据到达 S3 存储桶时对数据运⾏ AWS
Lambda 函数。
D. 在分布于多个可⽤区的 Amazon EC2 实例上创建数据摄取服务。配置该服务以将数据转发到 Amazon
RDS 多可⽤区数据库。
https://examlearn.online
[2026/05]
Question #226
Topic 1
⼀家公司使⽤运⾏在 Amazon EC2 实例上的 RESTful Web 服务应⽤程序，从数千台远程设备收集数据。该 EC2
实例接收原始数据，转换原始数据，并将所有数据存储在 Amazon S3 存储桶中。远程设备的数量很快将增加到
数百万台。该公司需要⼀个⾼度可扩展的解决⽅案，以最⼤限度地降低运营成本。
解决⽅案架构师应该采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 使⽤ AWS Glue 处理 Amazon S3 中的原始数据。
B. 使⽤ Amazon Route 53 将流量路由到不同的 EC2 实例。
C. 添加更多 EC2 实例以适应不断增加的传⼊数据量。
D. 将原始数据发送到 Amazon Simple Queue Service (Amazon SQS)。使⽤ EC2 实例处理数据。
E. 使⽤ Amazon API Gateway 将原始数据发送到 Amazon Kinesis 数据流。配置 Amazon Kinesis Data
Firehose，使其使⽤该数据流作为数据源，将数据传输到 Amazon S3。
Question #227
Topic 1
⼀家公司需要将其 AWS CloudTrail ⽇志保留 3 年。该公司通过⽗账户中的 AWS Organizations 在多个 AWS 账
户中强制使⽤ CloudTrail。CloudTrail 的⽬标 S3 存储桶已配置为启⽤ S3 版本控制。此外，还设置了 S3 ⽣命周
期策略，⽤于在 3 年后删除现有对象。S3
存储桶使⽤四年后，其指标显示对象数量持续增⻓。然⽽，发送到 S3 存储桶的新 CloudTrail ⽇志数量却保持稳
定。
哪种解决⽅案能够以最具成本效益的⽅式删除超过 3 年的对象？
A. 将组织的集中式 CloudTrail 跟踪配置为在 3 年后使对象过期。
B. 配置 S3 ⽣命周期策略，删除以前的版本以及当前版本。
C. 创建⼀个 AWS Lambda 函数，⽤于枚举并删除 Amazon S3 中超过 3 年的对象。
D. 将⽗帐户配置为交付到 S3 存储桶的所有对象的拥有者。
https://examlearn.online
[2026/05]
Question #228
Topic 1
⼀家公司拥有⼀个 API，⽤于接收来⾃⼀系列监控设备的实时数据。该 API 将这些数据存储在 Amazon RDS 数据
库实例中，以便后续分析。监控设备发送到 API 的数据量会波动。在流量⾼峰期，API 经常返回超时错误。
经过⽇志检查，该公司确定数据库⽆法处理来⾃ API 的⼤量写⼊流量。解决⽅案架构师必须尽可能减少数据库连
接数，并确保在流量⾼峰期数据不会丢失。
哪种解决⽅案能够满⾜这些要求？
A. 将数据库实例的⼤⼩增加到具有更多可⽤内存的实例类型。
B. 将数据库实例修改为多可⽤区数据库实例。配置应⽤程序以写⼊所有活动的 RDS 数据库实例。
C. 修改 API，将传⼊数据写⼊ Amazon Simple Queue Service (Amazon SQS) 队列。使⽤ Amazon SQS 调
⽤的 AWS Lambda 函数，将队列中的数据写⼊数据库。
D. 修改 API，使其能够将传⼊数据写⼊ Amazon Simple Notification Service (Amazon SNS) 主题。使⽤
Amazon SNS 调⽤的 AWS Lambda 函数，将主题中的数据写⼊数据库。
Question #229
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司⾃⾏管理运⾏ MySQL 数据库的 Amazon EC2 实例。该公司⽬前需要⼿动管理复制和扩展，以应对需求
的增减。现在，该公司需要⼀种新的解决⽅案，能够简化按需向数据库层添加或移除计算容量的过程。此外，该
解决⽅案还必须提供更⾼的性能、扩展性和持久性，同时最⼤限度地减少运维⼯作量。
A. 将数据库迁移到 Amazon Aurora Serverless for Aurora MySQL。
B. 将数据库迁移到 Amazon Aurora Serverless for Aurora PostgreSQL。
C. 将多个数据库合并成⼀个更⼤的 MySQL 数据库。在更⼤的 EC2 实例上运⾏这个更⼤的数据库。
D. 为数据库层创建 EC2 ⾃动扩展组。将现有数据库迁移到新环境。
https://examlearn.online
[2026/05]
Question #230
Topic 1
⼀家公司担⼼正在使⽤的两个NAT实例将⽆法再满⾜公司应⽤程序所需的流量。解决⽅案架构师希望实施⼀个⾼
可⽤性、容错性和⾃动可扩展的解决⽅案。这位
解决⽅案架构师应该提出什么建议？
A. 删除两个 NAT 实例，并将它们替换为同⼀可⽤区中的两个 NAT ⽹关。
B. 对不同可⽤区中的 NAT 实例使⽤带有⽹络负载均衡器的⾃动扩展组。
C. 删除两个 NAT 实例，并⽤位于不同可⽤区中的两个 NAT ⽹关替换它们。
D. 将两个 NAT 实例替换为不同可⽤区中的 Spot 实例，并部署⽹络负载均衡器。
Question #231
Topic 1
⼀个应⽤程序运⾏在 VPC A 中具有弹性 IP 地址的 Amazon EC2 实例上。该应⽤程序需要访问 VPC B 中的数据
库。两个 VPC 都位于同⼀个 AWS 账户中。
哪种解决⽅案能够以最安全的⽅式提供所需的访问权限？
A. 创建⼀个数据库实例安全组，允许来⾃ VPC A 中应⽤程序服务器的公共 IP 地址的所有流量。
B. 在 VPC A 和 VPC B 之间配置 VPC 对等连接。
C. 使数据库实例可公开访问。为数据库实例分配⼀个公共 IP 地址。
D. 在 VPC 中启动具有弹性 IP 地址的 EC2 实例。B. 通过新的 EC2 实例代理所有请求。
https://examlearn.online
[2026/05]
Question #232
Topic 1
⼀家公司在亚⻢逊 EC2 实例上为客户运⾏演示环境。每个环境都隔离在各⾃的 VPC 中。当 RDP 或 SSH 访问某
个环境建⽴时，该公司运维团队需要收到通知。
A. 配置 Amazon CloudWatch Application Insights，以便在检测到 RDP 或 SSH 访问时创建 AWS Systems
Manager OpsItems。
B. 使⽤ IAM 实例配置⽂件配置 EC2 实例，该配置⽂件具有附加了 AmazonSSMManagedInstanceCore 策略
的 IAM ⻆⾊。
C. 将 VPC 流⽇志发布到 Amazon CloudWatch Logs。创建所需的指标筛选器。创建 Amazon CloudWatch
指标警报，并设置警报处于 ALARM 状态时的通知操作。
D. 配置⼀条 Amazon EventBridge 规则，监听 EC2 实例状态变更通知类型的事件。将 Amazon Simple
Notification Service (Amazon SNS) 主题配置为⽬标。让运维团队订阅该主题。
Question #233
以下哪两项操作组合可以实现此⽬的？
A. 确保 root ⽤户使⽤强密码。
解决⽅案架构师创建了⼀个新的 AWS 账户，现在需要确保 AWS 账户根⽤户的访问权限。
B. 为 root ⽤户启⽤多因素身份验证。
C. 将 root ⽤户访问密钥存储在加密的 Amazon S3 存储桶中。
D. 将 root ⽤户添加到具有管理权限的组中。
E. 通过内联策略⽂档，为 root ⽤户应⽤所需的权限。
Topic 1
https://examlearn.online
[2026/05]
Question #234
Topic 1
⼀家公司正在构建⼀个新的基于 Web 的客户关系管理应⽤程序。该应⽤程序将使⽤多个 Amazon EC2 实例，这
些实例由位于应⽤程序负载均衡器 (ALB) 后⾯的 Amazon Elastic Block Store (Amazon EBS) 卷提供⽀持。该应
⽤程序还将使⽤ Amazon Aurora 数据库。应⽤程序的所有数据在静态存储和传输过程中都必须加密。
哪种解决⽅案能够满⾜这些要求？
A. 在应⽤负载均衡器 (ALB) 上使⽤ AWS Key Management Service (AWS KMS) 证书来加密传输中的数据。
使⽤ AWS Certificate Manager (ACM) 对静态的 EBS 卷和 Aurora 数据库存储进⾏加密。
B. 使⽤ AWS 根账户登录 AWS 管理控制台。上传公司加密证书。在根账户中，选择启⽤该账户所有静态数据
和传输中数据的加密选项。
C. 使⽤ AWS Key Management Service (AWS KMS) 对 EBS 卷和 Aurora 数据库的静态存储进⾏加密。将
AWS Certificate Manager (ACM) 证书附加到 ALB，以加密传输中的数据。
D. 使⽤ BitLocker 加密所有静态数据。将公司的 TLS 证书密钥导⼊ AWS Key Management Service (AWS
KMS)。将 KMS 密钥附加到 ALB，以加密传输中的数据。
Question #235
解决⽅案架构师应该提出什么建议？
Topic 1
⼀家公司正在将其本地部署的 Oracle 数据库迁移到 Amazon Aurora PostgreSQL。该数据库包含多个应⽤程
序，这些应⽤程序会写⼊相同的表。这些应⽤程序需要逐个迁移，每次迁移间隔⼀个⽉。管理层表示担⼼该数据
库的读写操作量很⼤。在整个迁移过程中，必须确保两个数据库之间的数据保持同步。
A. 使⽤ AWS DataSync 进⾏初始迁移。使⽤ AWS 数据库迁移服务 (AWS DMS) 创建变更数据捕获 (CDC) 复
制任务和表映射以选择所有表。
B. 使⽤ AWS DataSync 进⾏初始迁移。使⽤ AWS 数据库迁移服务 (AWS DMS) 创建完整加载加变更数据捕
获 (CDC) 复制任务，并创建表映射以选择所有表。
C. 使⽤ AWS Schema Conversion Tool 和 AWS Database Migration Service (AWS DMS)，并采⽤内存优
化的复制实例。创建⼀个包含完整加载和变更数据捕获 (CDC) 的复制任务，并创建⼀个表映射以选择所有
表。
D. 使⽤ AWS Schema Conversion Tool 和 AWS Database Migration Service (AWS DMS)，并采⽤计算优
化型复制实例。创建⼀个包含完整加载和变更数据捕获 (CDC) 的复制任务，并创建⼀个表映射来选择最⼤的
表。
https://examlearn.online
[2026/05]
Question #236
Topic 1
⼀家公司有⼀个三层架构的图⽚共享应⽤程序。该应⽤程序使⽤⼀个 Amazon EC2 实例作为前端层，另⼀个
EC2 实例作为应⽤层，第三个 EC2 实例作为 MySQL 数据库。解决⽅案架构师必须设计⼀个可扩展、⾼可⽤的解
决⽅案，并且该⽅案需要对应⽤程序进⾏最少的更改。
哪个解决⽅案满⾜这些要求？
A. 使⽤ Amazon S3 托管前端层。使⽤ AWS Lambda 函数构建应⽤层。将数据库迁移到 Amazon
DynamoDB 表。使⽤ Amazon S3 存储和提供⽤户图⽚。
B. 前端层和应⽤层均采⽤负载均衡的多可⽤区 AWS Elastic Beanstalk 环境。将数据库迁移到具有多个只读
副本的 Amazon RDS 数据库实例，以提供⽤户图像服务。
C. 使⽤ Amazon S3 托管前端层。使⽤⾃动扩展组中的 EC2 实例集群来托管应⽤层。将数据库迁移到内存优
化型实例类型，以存储和提供⽤户图像。
D. 前端层和应⽤层均使⽤负载均衡的多可⽤区 AWS Elastic Beanstalk 环境。将数据库迁移到 Amazon RDS
多可⽤区数据库实例。使⽤ Amazon S3 存储和提供⽤户图⽚。
Question #237
哪个解决⽅案能够满⾜这些要求？
Topic 1
运⾏在 VPC-A 的 Amazon EC2 实例上的应⽤程序需要访问 VPC-B 中另⼀个 EC2 实例上的⽂件。这两个 VPC
位于不同的 AWS 账户中。⽹络管理员需要设计⼀个解决⽅案，以配置从 VPC-A 到 VPC-B 中 EC2 实例的安全访
问。该连接不应存在单点故障或带宽限制。
A. 在 VPC-A 和 VPC-B 之间建⽴ VPC 对等连接。
B. 为在 VPC-B 中运⾏的 EC2 实例设置 VPC ⽹关端点。
C. 将虚拟专⽤⽹关连接到 VPC-B，并设置从 VPC-A 的路由。
D. 为在 VPC-B 中运⾏的 EC2 实例创建私有虚拟接⼝ (VIF)，并添加来⾃ VPC-A 的适当路由。
https://examlearn.online
[2026/05]
Question #238
Topic 1
⼀家公司希望为其⼯程师团队试⽤独⽴的 AWS 账户。该公司希望在每个账户的 Amazon EC2 实例使⽤量超过特
定阈值时⽴即收到通知。
解决⽅案架构师应该如何以最具成本效益的⽅式满⾜此需求？
A. 使⽤ Cost Explorer 创建按服务划分的每⽇成本报告。按 EC2 实例筛选报告。配置 Cost Explorer，使其
在成本超过阈值时发送 Amazon Simple Email Service (Amazon SES) 通知。
B. 使⽤ Cost Explorer 创建按服务划分的⽉度成本报告。按 EC2 实例筛选报告。配置 Cost Explorer，使其
在成本超过阈值时发送 Amazon Simple Email Service (Amazon SES) 通知。
C. 使⽤ AWS Budgets 为每个账户创建成本预算。将周期设置为每⽉。将范围设置为 EC2 实例。为预算设置
警报阈值。配置 Amazon Simple Notification Service (Amazon SNS) 主题，以便在超出阈值时接收通知。
D. 使⽤ AWS 成本和使⽤情况报告创建按⼩时粒度划分的报告。将报告数据与 Amazon Athena 集成。使⽤
Amazon EventBridge 安排 Athena 查询。配置 Amazon Simple Notification Service (Amazon SNS) 主
题，以便在超过阈值时接收通知。
Question #239
哪种解决⽅案能够以最⾼效的⽅式部署该函数？
Topic 1
解决⽅案架构师需要为公司的应⽤程序设计⼀个新的微服务。客户端必须能够调⽤ HTTPS 端点来访问该微服
务。该微服务还必须使⽤ AWS Identity and Access Management (IAM) 进⾏身份验证。解决⽅案架构师将使⽤
⼀个⽤ Go 1.x 编写的 AWS Lambda 函数来编写该微服务的逻辑。
A. 创建⼀个 Amazon API Gateway REST API。配置该⽅法以使⽤ Lambda 函数。在 API 上启⽤ IAM 身份验
证。
B. 为该函数创建 Lambda 函数 URL。指定 AWS_IAM 作为身份验证类型。
C. 创建 Amazon CloudFront 分发。将函数部署到 Lambda@Edge。将 IAM 身份验证逻辑集成到
Lambda@Edge 函数中。
D. 创建 Amazon CloudFront 分发。将函数部署到 CloudFront Functions。指定 AWS_IAM 作为身份验证类
型。
https://examlearn.online
[2026/05]
Question #240
Topic 1
⼀家公司之前已将其数据仓库解决⽅案迁移到 AWS。该公司还拥有 AWS Direct Connect 连接。公司办公室⽤户
使⽤可视化⼯具查询数据仓库。数据仓库返回的查询结果平均⼤⼩为 50 MB，⽽可视化⼯具发送的每个⽹⻚⼤⼩
约为 500 KB。数据仓库返回的结果集未被缓存。
哪种解决⽅案能为该公司提供最低的数据传输出站成本？
A. 将可视化⼯具托管在本地，并通过互联⽹直接查询数据仓库。
B. 将可视化⼯具托管在与数据仓库相同的 AWS 区域中。通过互联⽹访问它。
C. 将可视化⼯具托管在本地，并通过同⼀ AWS 区域内的 Direct Connect 连接直接查询数据仓库。
D. 将可视化⼯具托管在与数据仓库相同的 AWS 区域中，并通过同⼀区域中的 Direct Connect 连接访问它。
Question #241
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
Topic 1
⼀家在线学习公司正在迁移到 AWS 云平台。该公司使⽤ PostgreSQL 数据库维护学⽣记录。该公司需要⼀个解
决⽅案，使其数据能够始终在多个 AWS 区域中保持在线可⽤。
A. 将 PostgreSQL 数据库迁移到 Amazon EC2 实例上的 PostgreSQL 集群。
B. 将 PostgreSQL 数据库迁移到启⽤了多可⽤区功能的 Amazon RDS for PostgreSQL 数据库实例。
C. 将 PostgreSQL 数据库迁移到 Amazon RDS for PostgreSQL 数据库实例。在另⼀个区域中创建只读副
本。
D. 将 PostgreSQL 数据库迁移到 Amazon RDS for PostgreSQL 数据库实例。设置数据库快照以便复制到另
⼀个区域。
https://examlearn.online
[2026/05]
Question #242
Topic 1
⼀家公司使⽤七个 Amazon EC2 实例在 AWS 上托管其 Web 应⽤程序。该公司要求在 DNS 查询中返回所有运⾏
正常的 EC2 实例的 IP 地址。
应该使⽤哪种策略来满⾜此要求？
A. 简单路由策略
B. 延迟路由策略
C. 多值路由策略
D. 地理位置路由策略
Question #243
Topic 1
⼀家医学研究实验室⽣成了与⼀项新研究相关的数据。该实验室希望以最⼩的延迟将这些数据提供给全国各地的
诊所，供其在本地部署的基于⽂件的应⽤程序使⽤。数据⽂件存储在 Amazon S3 存储桶中，每个诊所的存储桶
都具有只读权限。
解决⽅案架构师应该提出怎样的建议才能满⾜这些要求？
A. 在每家诊所的本地服务器上部署⼀个 AWS Storage Gateway ⽂件⽹关，作为虚拟机 (VM) 使⽤。
B. 使⽤ AWS DataSync 将⽂件迁移到各诊所的本地应⽤程序进⾏处理。
C. 在每个诊所的本地部署 AWS Storage Gateway 卷⽹关作为虚拟机 (VM)。
D. 将 Amazon Elastic File System (Amazon EFS) ⽂件系统附加到每个诊所的本地服务器。
https://examlearn.online
[2026/05]
Question #244
Topic 1
⼀家公司使⽤的内容管理系统运⾏在单个 Amazon EC2 实例上。该 EC2 实例同时包含 Web 服务器和数据库软
件。该公司必须确保其⽹站平台的⾼可⽤性，并且能够扩展以满⾜⽤户需求。
解决⽅案架构师应该提出怎样的建议来满⾜这些要求？
A. 将数据库迁移到 Amazon RDS，并启⽤⾃动备份。在同⼀可⽤区中⼿动启动另⼀个 EC2 实例。在该可⽤区
中配置应⽤程序负载均衡器，并将这两个实例设置为⽬标。
B. 将数据库迁移到与现有 EC2 实例位于同⼀可⽤区的 Amazon Aurora 实例，并配置⼀个只读副本。在同⼀
可⽤区⼿动启动另⼀个 EC2 实例。配置应⽤程序负载均衡器，并将这两个 EC2 实例设置为⽬标。
C. 将数据库迁移到 Amazon Aurora，并在另⼀个可⽤区中创建⼀个只读副本。从 EC2 实例创建 Amazon 系
统映像 (AMI)。在两个可⽤区中配置应⽤程序负载均衡器。附加⼀个跨两个可⽤区使⽤该 AMI 的⾃动扩展
组。
D. 将数据库迁移到单独的 EC2 实例，并安排备份到 Amazon S3。从原始 EC2 实例创建 Amazon 系统映像
(AMI)。在两个可⽤区中配置应⽤程序负载均衡器。附加⼀个跨两个可⽤区使⽤该 AMI 的⾃动扩展组。
Question #245
Topic 1
⼀家公司正在 AWS 上发布⼀款应⽤程序。该应⽤程序使⽤应⽤程序负载均衡器 (ALB) 将流量定向到同⼀⽬标组
中的⾄少两个 Amazon EC2 实例。这些实例位于每个环境的⾃动扩展组中。该公司需要⼀个开发环境和⼀个⽣产
环境。⽣产环境会有流量⾼峰期。
哪种解决⽅案能够以最具成本效益的⽅式配置开发环境？
A. 在开发环境中重新配置⽬标组，使其仅包含⼀个 EC2 实例作为⽬标。
B. 将 ALB 负载均衡算法改为最少未完成请求。
C. 减少两个环境中 EC2 实例的规模。
D. 减少开发环境⾃动扩展组中 EC2 实例的最⼤数量。
https://examlearn.online
[2026/05]
Question #246
Topic 1
⼀家公司在多个可⽤区中的 Amazon EC2 实例上运⾏ Web 应⽤程序。这些 EC2 实例位于私有⼦⽹中。解决⽅案
架构师部署了⼀个⾯向互联⽹的应⽤程序负载均衡器 (ALB)，并将这些 EC2 实例指定为⽬标组。但是，互联⽹流
量⽆法到达这些 EC2 实例。
解决⽅案架构师应该如何重新配置 架构以解决此问题？
A. 将应⽤负载均衡器 (ALB) 替换为⽹络负载均衡器 (NAT)。在公共⼦⽹中配置 NAT ⽹关以允许互联⽹流量。
B. 将 EC2 实例迁移到公共⼦⽹。向 EC2 实例的安全组添加规 则，允许出站流量访问 0.0.0.0/0。
C. 更新 EC2 实例⼦⽹的路由表，将 0.0.0.0/0 的流量通过互联⽹⽹关路由发送。向 EC2 实例的安全组添加⼀
条规则，允许出站流量访问 0.0.0.0/0。
D. 在每个可⽤区中创建公有⼦⽹。将公有⼦⽹与 ALB 关联。更新公有⼦⽹的路由表，添加指向私有⼦⽹的路
由。
Question #247
A. 在 RDS 主节点上启⽤ binlog 复制。
Topic 1
⼀家公司在 Amazon RDS 上部署了⼀个 MySQL 数据库。由于事务处理量增加，数据库⽀持团队报告称该数据库
实例读取速度变慢，并建议添加⼀个只读副本。
解决⽅案架构师在实施此更改之前应该采取哪些措施？（选择两项。）
B. 为源数据库实例选择故障转移优先级。
C. 允许⻓时间运⾏的事务在源数据库实例上完成。
D. 创建⼀个全局表，并指定该表将在哪些 AWS 区域可⽤。
E. 将源实例上的备份保留期设置为 0 以外的值，以启⽤⾃动备份。
https://examlearn.online
[2026/05]
Question #248
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏分析软件。该软件接受⽤户提交的作业请求，以处理已上传到 Amazon S3
的数据。⽤户报告称，部分提交的数据未被处理。Amazon CloudWatch 显示，EC2 实例的 CPU 利⽤率持续接
近或达到 100%。该公司希望提升系统性能，并根据⽤户负载扩展系统。
解决⽅案架构师应该如何满⾜这些要求？
A. 创建实例副本。将所有实例置于应⽤程序负载均衡器之后。
B. 为 Amazon S3 创建 S3 VPC 终端节点。更新软件以引⽤该终端节点。
C. 停⽌ EC2 实例。将实例类型修改为具有更强⼤的 CPU 和更多内存的实例。重新启动实例。
D. 将传⼊请求路由⾄ Amazon Simple Queue Service (Amazon SQS)。根据队列⼤⼩配置 EC2 Auto
Scaling 组。更新软件以从队列中读取数据。
Question #249
哪种 AWS 解决⽅案满⾜这些要求？
Topic 1
⼀家公司正在为托管在 AWS 云上的媒体应⽤程序部署共享存储解决⽅案。该公司需要能够使⽤ SMB 客户端访问
数据。该解决⽅案必须是完全托管的。
A. 创建 AWS Storage Gateway 卷⽹关。创建使⽤所需客户端协议的⽂件共享。将应⽤程序服务器连接到该
⽂件共享。
B. 创建 AWS Storage Gateway 磁带⽹关。配置磁带以使⽤ Amazon S3。将应⽤程序服务器连接到磁带⽹
关。
C. 创建⼀个 Amazon EC2 Windows 实例。在该实例上安装并配置 Windows ⽂件共享⻆⾊。将应⽤程序服
务器连接到该⽂件共享。
D. 创建 Amazon FSx for Windows ⽂件服务器⽂件系统。将该⽂件系统附加到源服务器。将应⽤程序服务器
连接到该⽂件系统。
https://examlearn.online
[2026/05]
Question #250
Topic 1
某公司安全团队要求将⽹络流量捕获到 VPC 流⽇志中。这些⽇志将在 90 天内频繁访问，之后将间歇性访问。
解决⽅案架构师在配置⽇志时应该如何满⾜这些要求？
A. 使⽤ Amazon CloudWatch 作为⽬标。将 CloudWatch ⽇志组的过期时间设置为 90 天。
B. 使⽤ Amazon Kinesis 作为⽬标。配置 Kinesis 流，使其始终保留⽇志 90 天。
C. 使⽤ AWS CloudTrail 作为⽬标。配置 CloudTrail 以保存到 Amazon S3 存储桶，并启⽤ S3 智能分层。
D. 使⽤ Amazon S3 作为⽬标。启⽤ S3 ⽣命周期策略，在 90 天后将⽇志迁移到 S3 标准-不频繁访问 (S3
Standard-IA)。
Question #251
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀个 Amazon EC2 实例位于新 VPC 的私有⼦⽹中。该⼦⽹没有出站互联⽹访问权限，但 EC2 实例需要能够从外
部供应商下载每⽉安全更新。
A. 创建⼀个互联⽹⽹关，并将其附加到 VPC。配置私有⼦⽹路由表，使互联⽹⽹关成为默认路由。
B. 创建⼀个 NAT ⽹关，并将其放置在公共⼦⽹中。配置私有⼦⽹路由表，将 NAT ⽹关⽤作默认路由。
C. 创建⼀个 NAT 实例，并将其放置在与 EC2 实例相同的⼦⽹中。配置私有⼦⽹路由表，将 NAT 实例⽤作默
认路由。
D. 创建⼀个互联⽹⽹关，并将其附加到 VPC。创建⼀个 NAT 实例，并将其放置在与 EC2 实例相同的⼦⽹
中。配置私有⼦⽹路由表，将互联⽹⽹关⽤作默认路由。
https://examlearn.online
[2026/05]
Question #252
解决⽅案架构师需要设计⼀个系统来存储客户案例⽂件。这些⽂件是公司的核⼼资产，⾮常重要。⽂件数量会随
着时间推移⽽增⻓。
这些⽂件必须能够同时被运⾏在 Amazon EC2 实例上的多个应⽤服务器访问。该解决⽅案必须具备内置冗余机
制。
哪个解决⽅案满⾜这些要求？
A. Amazon Elastic File System (Amazon EFS)
B. Amazon Elastic Block Store (Amazon EBS)
C. Amazon S3 Glacier Deep 存档
D. AWS备份
Topic 1
https://examlearn.online
[2026/05]
Question #253
解决⽅案架构师创建了两条 IAM 策略：策略 1 和策略 2。这两条策略都附加到⼀个 IAM 组。
Topic 1
⼀位云⼯程师被添加为该 IAM 组的 IAM ⽤户。这位云⼯程师将能够执⾏什么操作？
A. 删除 IAM ⽤户
B. 删除⽬录
https://examlearn.online
[2026/05]
C. 删除 Amazon EC2 实例
D. 从 Amazon CloudWatch Logs 中删除⽇志
Question #254
⼀家公司正在审查最近将⼀个三层应⽤程序迁移到 VPC 的情况。安全团队发现，应⽤程序层之间的 Amazon
EC2 安全组⼊⼝和出⼝规则没有应⽤最⼩权限原则。
解决⽅案架构师应该如何解决这个问题？
A. 使⽤实例 ID 作为源或⽬标创建安全组规则。
B. 使⽤安全组 ID 作为源或⽬标创建安全组规则。
C. 使⽤ VPC CIDR 块作为源或⽬标创建安全组规则。
D. 使⽤⼦⽹ CIDR 块作为源或⽬标创建安全组规则。
Question #255
解决⽅案架构师应该如何重构此流程以防⽌创建多个订单？
Firehose 检索消息并处理订单。
Topic 1
Topic 1
⼀家公司的电商结账流程会将订单写⼊数据库并调⽤服务处理付款。⽤户在结账过程中经常遇到超时问题。当⽤
户重新提交结账表单时，系统会为同⼀笔交易创建多个不同的订单。
A. 配置 Web 应⽤程序向 Amazon Kinesis Data Firehose 发送订单消息。设置⽀付服务从 Kinesis Data
B. 在 AWS CloudTrail 中创建⼀条规则，根据已记录的应⽤程序路径请求调⽤ AWS Lambda 函数。使⽤
Lambda 函数查询数据库、调⽤⽀付服务并传递订单信息。
C. 将订单存储到数据库中。向 Amazon Simple Notification Service (Amazon SNS) 发送包含订单号的消
息。设置⽀付服务轮询 Amazon SNS，检索消息并处理订单。
D. 将订单存储到数据库中。向 Amazon Simple Queue Service (Amazon SQS) 先进先出 (FIFO) 队列发送包
含订单号的消息。设置⽀付服务以检索该消息并处理订单。从队列中删除该消息。
https://examlearn.online
[2026/05]
Question #256
Topic 1
⼀位解决⽅案架构师正在使⽤ Amazon S3 存储桶实现⼀个⽂档审阅应⽤程序。该解决⽅案必须防⽌⽂档被意外
删除，并确保所有版本的⽂档都可⽤。⽤户必须能够下载、修改和上传⽂档。
为了满⾜这些要求，应该采取哪些操作组合？（选择两项。）
A. 启⽤只读存储桶 ACL。
B. 启⽤存储桶的版本控制。
C. 将 IAM 策略附加到存储桶。
D. 在存储桶上启⽤ MFA 删除。
E. 使⽤ AWS KMS 对存储桶进⾏加密。
Question #257
为了满⾜这些要求，该公司应该如何将数据迁移到 Amazon S3？
Firehose。将数据存储在 Amazon S3 中。
Topic 1
⼀家公司正在构建⼀个解决⽅案，⽤于报告 AWS 账户中所有应⽤程序的 Amazon EC2 Auto Scaling 事件。该公
司需要使⽤⽆服务器解决⽅案将 EC2 Auto Scaling 状态数据存储在 Amazon S3 中。然后，该公司将使⽤
Amazon S3 中的数据在控制⾯板中提供近乎实时的更新。该解决⽅案不得影响 EC2 实例的启动速度。
A. 使⽤ Amazon CloudWatch 指标流将 EC2 Auto Scaling 状态数据发送到 Amazon Kinesis Data
B. 启动 Amazon EMR 集群以收集 EC2 Auto Scaling 状态数据，并将数据发送到 Amazon Kinesis Data
Firehose。将数据存储在 Amazon S3 中。
C. 创建⼀条 Amazon EventBridge 规则，按计划调⽤ AWS Lambda 函数。配置 Lambda 函数，使其将 EC2
Auto Scaling 状态数据直接发送到 Amazon S3。
D. 在启动 EC2 实例期间使⽤引导脚本安装 Amazon Kinesis Agent。配置 Kinesis Agent 以收集 EC2 Auto
Scaling 状态数据并将数据发送到 Amazon Kinesis Data Firehose。将数据存储在 Amazon S3 中。
https://examlearn.online
[2026/05]
Question #258
Topic 1
⼀家公司有⼀个应⽤程序，每⼩时会将数百个 .csv ⽂件上传到 Amazon S3 存储桶中。每个⽂件⼤⼩为 1 GB。
每次上传⽂件时，该公司都需要将⽂件转换为 Apache Parquet 格式，并将转换后的⽂件上传到 S3 存储桶。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个 AWS Lambda 函数，⽤于下载 .csv ⽂件，将⽂件转换为 Parquet 格式，并将输出⽂件放⼊ S3
存储桶中。针对每个 S3 PUT 事件调⽤该 Lambda 函数。
B. 创建⼀个 Apache Spark 作业，⽤于读取 .csv ⽂件，将⽂件转换为 Parquet 格式，并将输出⽂件放⼊ S3
存储桶。为每个 S3 PUT 事件创建⼀个 AWS Lambda 函数来调⽤ Spark 作业。
C. 为应⽤程序存放 .csv ⽂件的 S3 存储桶创建 AWS Glue 表和 AWS Glue 爬⽹程序。安排⼀个 AWS
Lambda 函数定期使⽤ Amazon Athena 查询 AWS Glue 表，将查询结果转换为 Parquet 格式，并将输出⽂
件放⼊ S3 存储桶。
D. 创建⼀个 AWS Glue 提取、转换和加载 (ETL) 作业，将 .csv ⽂件转换为 Parquet 格式，并将输出⽂件放
⼊ S3 存储桶。为每个 S3 PUT 事件创建⼀个 AWS Lambda 函数来调⽤该 ETL 作业。
Question #259
解决⽅案架构师应该推荐哪种解决⽅案来满⾜这些要求？
Topic 1
⼀家公司正在为所有运⾏在 Amazon RDS 数据库实例上的数据库实施新的数据保留策略。该公司必须⾄少保留 2
年的每⽇备份。备份必须具有⼀致性且可恢复。
A. 在 AWS Backup 中创建⼀个备份库来保留 RDS 备份。创建⼀个新的备份计划，设置每⽇备份计划，并将
备份有效期设置为创建后 2 年。将 RDS 数据库实例分配给该备份计划。
B. 为 RDS 数据库实例配置每⽇快照备份窗⼝。为每个 RDS 数据库实例分配 2 年的快照保留策略。使⽤
Amazon Data Lifecycle Manager (Amazon DLM) 来安排快照删除。
C. 配置数据库事务⽇志⾃动备份到 Amazon CloudWatch Logs，过期时间为 2 年。
D. 配置 AWS 数据库迁移服务 (AWS DMS) 复制任务。部署复制实例，并配置变更数据捕获 (CDC) 任务，将
数据库变更流式传输到 Amazon S3 作为⽬标。配置 S3 ⽣命周期策略，以便在 2 年后删除快照。
https://examlearn.online
[2026/05]
Question #260
Topic 1
⼀家公司的合规团队需要将其⽂件共享迁移到 AWS。这些共享运⾏在 Windows Server SMB ⽂件共享上。公司
内部的⾃管理 Active Directory 控制着对这些⽂件和⽂件夹的访问。
该公司希望使⽤ Amazon FSx for Windows File Server 作为解决⽅案的⼀部分。迁移到 AWS 后，该公司必须确
保本地 Active Directory 组限制对 FSx for Windows File Server SMB 合规共享、⽂件夹和⽂件的访问。该公司
已创建了⼀个 FSx for Windows File Server ⽂件系统。
哪种解决⽅案能够满⾜这些要求？
A. 创建 Active Directory 连接器以连接到 Active Directory。将 Active Directory 组映射到 IAM 组以限制访
问。
B. 分配⼀个带有“限制”标签键和“合规性”标签值的标签。将 Active Directory 组映射到 IAM 组以限制访问。
C. 创建⼀个与 FSx for Windows ⽂件服务器直接关联的 IAM 服务相关⻆⾊，以限制访问。
D. 将⽂件系统加⼊ Active Directory 以限制访问。
Question #261
Topic 1
⼀家公司最近宣布⾯向全球⽤户推出其零售⽹站。该⽹站运⾏在多个 Amazon EC2 实例上，这些实例位于弹性负
载均衡器 (ELB) 后⽅。这些实例运⾏在跨多个可⽤区的⾃动扩展组中。
该公司希望根据客户访问⽹站所使⽤的设备，为其提供不同版本的内容。
解决⽅案架构师应采取哪些措施组合来满⾜这些要求？（选择两项。）
A. 配置 Amazon CloudFront 以缓存内容的多个版本。
B. 在⽹络负载均衡器中配置主机头，将流量转发到不同的实例。
C. 配置 Lambda@Edge 函数，根据 User-Agent 标头向⽤户发送特定对象。
D. 配置 AWS Global Accelerator。将请求转发到⽹络负载均衡器 (NLB)。配置 NLB 以建⽴基于主机的路
由，将请求转发到不同的 EC2 实例。
E. 配置 AWS Global Accelerator。将请求转发到⽹络负载均衡器 (NLB)。配置 NLB 以建⽴基于路径的路
由，将请求转发到不同的 EC2 实例。
https://examlearn.online
[2026/05]
Question #262
Topic 1
⼀家公司计划在其多层 Web 应⽤程序中使⽤ Amazon ElastiCache。解决⽅案架构师为 ElastiCache 集群创建了
⼀个 Cache VPC，并为应⽤程序的 Amazon EC2 实例创建了⼀个 App VPC。这两个 VPC 都位于 us-east-1 区
域。
解决⽅案架构师必须实现⼀个解决⽅案，使应⽤程序的 EC2 实例能够访问 ElastiCache 集群。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在两个 VPC 之间创建对等连接。在两个 VPC 中为该对等连接添加路由表条⽬。为 ElastiCache 集群的安
全组配置⼊站规则，以允许来⾃应⽤程序安全组的⼊站连接。
B. 创建⼀个 Transit VPC。更新 Cache VPC 和 App VPC 中的 VPC 路由表，将流量路由到 Transit VPC。为
ElastiCache 集群的安全组配置⼊站规则，允许来⾃应⽤程序安全组的⼊站连接。
C. 在两个 VPC 之间创建对等连接。在两个 VPC 中为该对等连接添加路由表条⽬。为该对等连接的安全组配
置⼊站规则，以允许来⾃应⽤程序安全组的⼊站连接。
D. 创建⼀个 Transit VPC。更新 Cache VPC 和 App VPC 中的 VPC 路由表，将流量路由到 Transit VPC。为
Transit VPC 的安全组配置⼊站规则，允许来⾃应⽤程序安全组的⼊站连接。
Question #263
Topic 1
⼀家公司正在构建⼀个包含多个微服务的应⽤程序。该公司决定使⽤容器技术将其软件部署在 AWS 上。该公司
需要⼀个能够最⼤限度减少维护和扩展⼯作量的解决⽅案。该公司⽆法管理额外的基础设施。
为了满⾜这些要求，解决⽅案架构师应该采取哪些措施组合？（选择两项。）
A. 部署 Amazon Elastic Container Service (Amazon ECS) 集群。
B. 在跨越多个可⽤区的 Amazon EC2 实例上部署 Kubernetes 控制平⾯。
C. 部署 Amazon Elastic Container Service (Amazon ECS) 服务，启动类型为 Amazon EC2。指定所需的任
务编号级别⼤于或等于 2。
D. 部署⼀个启动类型为 Fargate 的 Amazon Elastic Container Service (Amazon ECS) 服务。指定所需的任
务编号级别⼤于或等于 2。
E. 在跨多个可⽤区的 Amazon EC2 实例上部署 Kubernetes ⼯作节点。创建⼀个部署，为每个微服务指定两
个或多个副本。
https://examlearn.online
[2026/05]
Question #264
Topic 1
⼀家公司有⼀个托管在 10 个 Amazon EC2 实例上的 Web 应⽤程序，流量由 Amazon Route 53 路由。该公司在
尝试浏览该应⽤程序时偶尔会遇到超时错误。⽹络团队发现某些 DNS 查询返回了不健康实例的 IP 地址，导致了
超时错误。
解决⽅案架构师应该采取什么措施来解决这些超时错误？
A. 为每个 EC2 实例创建⼀个 Route 53 简单路由策略记录。将健康检查与每个记录关联起来。
B. 为每个 EC2 实例创建 Route 53 故障转移路由策略记录。将运⾏状况检查与每条记录关联。
C. 创建⼀个以 EC2 实例为源的 Amazon CloudFront 分发。将运⾏状况检查与 EC2 实例关联起来。
D. 在 EC2 实例前⾯创建⼀个带有健康检查的应⽤程序负载均衡器 (ALB)。从 Route 53 路由到 ALB。
Question #265
哪种解决⽅案既满⾜这些要求，⼜最安全？
Topic 1
解决⽅案架构师需要设计⼀个⾼可⽤性应⽤程序，该应⽤程序包含 Web 层、应⽤层和数据库层。HTTPS 内容分
发应尽可能靠近⽹络边缘，并尽可能缩短分发时间。
A. 配置⼀个公共应⽤程序负载均衡器 (ALB)，该均衡器在公共⼦⽹中使⽤多个冗余的 Amazon EC2 实例。配
置 Amazon CloudFront，使其使⽤该公共 ALB 作为源来提供 HTTPS 内容。
B. 配置⼀个公共应⽤程序负载均衡器，该均衡器使⽤私有⼦⽹中的多个冗余 Amazon EC2 实例。配置
Amazon CloudFront，以使⽤这些 EC2 实例作为源来提供 HTTPS 内容。
C. 配置⼀个公共应⽤程序负载均衡器 (ALB)，该均衡器在私有⼦⽹中使⽤多个冗余的 Amazon EC2 实例。配
置 Amazon CloudFront，使其使⽤该公共 ALB 作为源来提供 HTTPS 内容。
D. 配置⼀个公共应⽤程序负载均衡器，该均衡器使⽤多个冗余的 Amazon EC2 实例，这些实例位于公共⼦⽹
中。配置 Amazon CloudFront，以使⽤这些 EC2 实例作为源来提供 HTTPS 内容。
https://examlearn.online
[2026/05]
Question #266
Topic 1
⼀家公司在 AWS 上运⾏着⼀个热⻔游戏平台。该应⽤对延迟⾮常敏感，因为延迟会影响⽤户体验，并可能给部
分玩家带来不公平的优势。该应⽤已部署在所有 AWS 区域，运⾏在 Amazon EC2 实例上，这些实例属于⾃动扩
展组，并配置在应⽤程序负载均衡器 (ALB) 之后。解决⽅案架构师需要实现⼀种机制来监控应⽤的运⾏状况，并
将流量重定向到运⾏状况良好的终端节点。
哪种解决⽅案满⾜这些要求？
A. 在 AWS Global Accelerator 中配置加速器。为应⽤程序监听的端⼝添加监听器，并将其附加到每个区域中
的区域终端节点。将 ALB 添加为终端节点。
B. 创建 Amazon CloudFront 分发，并将 ALB 指定为源服务器。配置缓存⾏为以使⽤源缓存标头。使⽤ AWS
Lambda 函数优化流量。
C. 创建 Amazon CloudFront 分发，并将 Amazon S3 指定为源服务器。配置缓存⾏为以使⽤源缓存标头。使
⽤ AWS Lambda 函数优化流量。
D. 配置 Amazon DynamoDB 数据库作为应⽤程序的数据存储。创建 DynamoDB Accelerator (DAX) 集群作
为 DynamoDB 的内存缓存，⽤于托管应⽤程序数据。
Question #267
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司拥有100万移动应⽤⽤户。该公司必须近乎实时地分析数据使⽤情况，同时还必须近乎实时地加密数
据，并将数据以Apache Parquet格式集中存储，以便进⾏后续处理。
A. 创建 Amazon Kinesis 数据流，将数据存储在 Amazon S3 中。创建 Amazon Kinesis Data Analytics 应⽤
程序来分析数据。调⽤ AWS Lambda 函数将数据发送到 Kinesis Data Analytics 应⽤程序。
B. 创建 Amazon Kinesis 数据流，将数据存储在 Amazon S3 中。创建 Amazon EMR 集群来分析数据。调⽤
AWS Lambda 函数将数据发送到 EMR 集群。
C. 创建 Amazon Kinesis Data Firehose 传输流，将数据存储在 Amazon S3 中。创建 Amazon EMR 集群来
分析数据。
D. 创建⼀个 Amazon Kinesis Data Firehose 传输流，将数据存储在 Amazon S3 中。创建⼀个 Amazon
Kinesis Data Analytics 应⽤程序来分析数据。
https://examlearn.online
[2026/05]
Question #268
Topic 1
⼀家游戏公司有⼀个⽤于显示游戏分数的 Web 应⽤程序。该应⽤程序运⾏在 Amazon EC2 实例上，并通过应⽤
程序负载均衡器进⾏管理。应⽤程序将数据存储在 Amazon RDS for MySQL 数据库中。⽤户开始遇到因数据库
读取性能问题导致的⻓时间延迟和中断。该公司希望在尽量减少对应⽤程序架构更改的情况下改善⽤户体验。
解决⽅案架构师应该如何满⾜这些要求？
A. 在数据库前端使⽤ Amazon ElastiCache。
B. 在应⽤程序和数据库之间使⽤ RDS 代理。
C. 将应⽤程序从 EC2 实例迁移到 AWS Lambda。
D. 将数据库从 Amazon RDS for MySQL 迁移到 Amazon DynamoDB。
Question #269
解决⽅案架构师应该提出什么建议？
Topic 1
⼀家电商公司发现其基于 Amazon RDS 的 Web 应⽤程序性能下降。性能下降的原因是业务分析师触发的只读
SQL 查询数量增加。解决⽅案架构师需要在对现有 Web 应⽤程序进⾏最⼩改动的情况下解决此问题。
A. 将数据导出到 Amazon DynamoDB，让业务分析师运⾏他们的查询。
B. 将数据加载到 Amazon ElastiCache 中，并让业务分析师运⾏他们的查询。
C. 创建主数据库的只读副本，让业务分析师运⾏他们的查询。
D. 将数据复制到 Amazon Redshift 集群中，并让业务分析师运⾏他们的查询。
https://examlearn.online
[2026/05]
Question #270
Topic 1
⼀家公司使⽤集中式 AWS 账户将⽇志数据存储在多个 Amazon S3 存储桶中。解决⽅案架构师需要确保数据在上
传到 S3 存储桶之前已进⾏静态加密，并且在传输过程中也必须加密。
哪种解决⽅案满⾜这些要求？
A. 使⽤客户端加密对上传到 S3 存储桶的数据进⾏加密。
B. 使⽤服务器端加密对上传到 S3 存储桶的数据进⾏加密。
C. 创建存储桶策略，要求对 S3 上传使⽤服务器端加密和 S3 管理的加密密钥 (SSE-S3)。
D. 启⽤安全选项，使⽤默认的 AWS Key Management Service (AWS KMS) 密钥对 S3 存储桶进⾏加密。
Question #271
A. 增加⾃动扩展组的最⼩容量。
Topic 1
⼀位解决⽅案架构师发现，夜间批处理作业会在达到所需的 Amazon EC2 容量之前⾃动扩展 1 ⼩时。峰值容量每
晚都相同，批处理作业总是在凌晨 1 点开始。这位解决⽅案架构师需要找到⼀种经济⾼效的解决⽅案，既能快速
达到所需的 EC2 容量，⼜能让⾃动扩展组在批处理作业完成后缩减容量。
为了满⾜这些要求，这位解决⽅案架构师应该怎么做？
B. 增加⾃动扩展组的最⼤容量。
C. 配置计划扩展以扩展到所需的计算级别。
D. 更改扩展策略，在每次扩展操作期间添加更多 EC2 实例。
https://examlearn.online
[2026/05]
Question #272
Topic 1
⼀家公司使⽤⼀组位于应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2 实例来运⾏动态⽹站。该⽹站需要⽀持
多种语⾔，以便服务全球客户。该⽹站的架构运⾏在 us-west-1 区域，对于位于世界其他地区的⽤户来说，请求
延迟较⾼。
⽆论⽤户身处何地，⽹站都需要快速⾼效地响应请求。然⽽，该公司不希望跨多个区域重新构建 现有架构。
解决⽅案架构师应该如何满⾜这些要求？
A. 将现有架构替换为从 Amazon S3 存储桶提供服务的⽹站。配置 Amazon CloudFront 分发，并将 S3 存储
桶作为源。将缓存⾏为设置为基于 Accept-Language 请求标头进⾏缓存。
B. 配置以 ALB 为源的 Amazon CloudFront 分发。将缓存⾏为设置设为基于 Accept-Language 请求标头进
⾏缓存。
C. 创建⼀个与 ALB 集成的 Amazon API Gateway API。将 API 配置为使⽤ HTTP 集成类型。设置⼀个 API
Gateway 阶段，以根据 Accept-Language 请求标头启⽤ API 缓存。
D. 在每个额外的区域中启动⼀个 EC2 实例，并将 NGINX 配置为该区域的缓存服务器。将所有 EC2 实例和
ALB 置于具有地理位置路由策略的 Amazon Route 53 记录集之后。
Question #273
Topic 1
⼀家快速发展的电⼦商务公司⽬前在单个 AWS 区域运⾏其⼯作负载。解决⽅案架构师需要制定⼀个包含不同
AWS 区域的灾难恢复 (DR) 策略。该公司希望其数据库在 DR 区域中保持最新状态，并尽可能降低延迟。DR 区
域中的其余基础设施需要以较低的容量运⾏，并且必须能够在必要时进⾏扩展。
哪种解决⽅案能够以最低的恢复时间⽬标 (RTO) 满⾜这些要求？
A. 使⽤带有试点部署的 Amazon Aurora 全球数据库。
B. 使⽤具有热备部署的 Amazon Aurora 全局数据库。
C. 使⽤带有试点部署的 Amazon RDS 多可⽤区数据库实例。
D. 使⽤具有热备部署的 Amazon RDS 多可⽤区数据库实例。
https://examlearn.online
[2026/05]
Question #274
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个应⽤程序。该公司需要为该应⽤程序实施灾难恢复 (DR) 解决⽅案。该
DR 解决⽅案的恢复时间⽬标 (RTO) 必须⼩于 4 ⼩时。此外，该 DR 解决⽅案在正常运⾏期间还需要尽可能减少
对 AWS 资源的占⽤。
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
A. 创建 Amazon 系统映像 (AMI) 来备份 EC2 实例。将 AMI 复制到辅助 AWS 区域。使⽤ AWS Lambda 和
⾃定义脚本⾃动部署辅助区域中的基础设施。
B. 创建 Amazon 系统映像 (AMI) 以备份 EC2 实例。将 AMI 复制到辅助 AWS 区域。使⽤ AWS
CloudFormation ⾃动部署辅助区域中的基础设施。
C. 在辅助 AWS 区域中启动 EC2 实例。始终保持辅助区域中的 EC2 实例处于活动状态。
D. 在辅助可⽤区启动 EC2 实例。始终保持辅助可⽤区中的 EC2 实例处于活动状态。
Question #275
Topic 1
⼀家公司运⾏着⼀个内部的基于浏览器的应⽤程序。该应⽤程序运⾏在应⽤程序负载均衡器后⾯的 Amazon EC2
实例上。这些实例运⾏在跨多个可⽤区的 Amazon EC2 ⾃动扩展组中。该⾃动扩展组在⼯作时间内最多可扩展到
20 个实例，但在夜间会缩减到 2 个实例。员⼯抱怨说，应⽤程序在早上运⾏速度⾮常慢，但到上午中段时运⾏良
好。
应该如何调整扩展策略才能解决员⼯的抱怨并最⼤限度地降低成本？
A. 在办公室开⻔前不久，执⾏⼀项计划操作，将所需容量设置为 20。
B. 实施在较低 CPU 阈值下触发的阶梯式缩放操作，并减少冷却时间。
C. 实现⽬标跟踪操作，在较低的 CPU 阈值下触发，并减少冷却时间。
D. 在办公室开⻔前不久，实施⼀项计划⾏动，将最⼩和最⼤容量设置为 20。
https://examlearn.online
[2026/05]
Question #276
Topic 1
⼀家公司在⾃动扩展组中的多个 Amazon EC2 实例上部署了⼀个多层应⽤程序。该应⽤程序的数据层使⽤
Amazon RDS for Oracle 实例，并采⽤ Oracle 特有的 PL/SQL 函数。应⽤程序的流量⼀直在稳步增⻓，导致
EC2 实例过载，RDS 实例的存储空间也即将耗尽。⾃动扩展组没有设置任何扩展指标，仅定义了最⼩健康实例
数。该公司预测，流量将以稳定但不可预测的速度持续增⻓，之后才会趋于平稳。
解决⽅案架构师应该采取哪些措施来确保系统能够⾃动扩展以应对不断增⻓的流量？（选择两项。）
A. 在 RDS for Oracle 实例上配置存储⾃动扩展。
B. 将数据库迁移到 Amazon Aurora 以使⽤⾃动扩展存储。
C. 在 RDS for Oracle 实例上配置低可⽤存储空间警报。
D. 配置⾃动扩展组，使其使⽤平均 CPU 作为扩展指标。
E. 配置⾃动扩展组，使其使⽤平均可⽤内存作为扩展指标。
Question #277
哪种存储⽅案最具成本效益？
EBS)。
Topic 1
⼀家公司提供在线视频内容发布和转码服务，以便任何移动平台都能使⽤。该应⽤架构采⽤ Amazon Elastic File
System (Amazon EFS) Standard 来收集和存储视频，以便多个 Amazon EC2 Linux 实例可以访问这些视频内容
进⾏处理。随着服务⽇益普及，存储成本也变得越来越⾼。
A. 使⽤ AWS Storage Gateway 存储⽂件来存储和处理视频内容。
B. 使⽤ AWS Storage Gateway 存储卷来存储和处理视频内容。
C. 使⽤ Amazon EFS 存储视频内容。处理完成后，将⽂件传输到 Amazon Elastic Block Store (Amazon
D. 使⽤ Amazon S3 存储视频内容。将⽂件临时移动到连接到服务器的 Amazon Elastic Block Store
(Amazon EBS) 卷上进⾏处理。
https://examlearn.online
[2026/05]
Question #278
Topic 1
⼀家公司希望创建⼀个应⽤程序，以层级结构化的⽅式存储员⼯数据。该公司需要对⾼流量的员⼯数据查询提供
最低延迟响应，并且必须保护所有敏感数据。此外，如果员⼯数据中包含任何财务信息，该公司还需要每⽉收到
电⼦邮件通知。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 使⽤ Amazon Redshift 将员⼯数据以层级结构存储。每⽉将数据卸载到 Amazon S3。
B. 使⽤ Amazon DynamoDB 以层级结构存储员⼯数据。每⽉将数据导出到 Amazon S3。
C. 为 AWS 账户配置 Amazon Macie。将 Macie 与 Amazon EventBridge 集成，以便每⽉向 AWS Lambda
发送事件。
D. 使⽤ Amazon Athena 分析 Amazon S3 中的员⼯数据。将 Athena 与 Amazon QuickSight 集成，以发布
分析仪表板并与⽤户共享仪表板。
E. 为 AWS 账户配置 Amazon Macie。将 Macie 与 Amazon EventBridge 集成，通过 Amazon Simple
Notification Service (Amazon SNS) 订阅发送每⽉通知。
Question #279
哪种解决⽅案能够满⾜这些要求？
冷存储。将每个备份的保留期设置为 7 年。
Topic 1
⼀家公司有⼀个应⽤程序，该应⽤程序由 Amazon DynamoDB 表提供⽀持。该公司的合规性要求规定，数据库
备份必须每⽉进⾏⼀次，备份⽂件必须可⽤ 6 个⽉，并且必须保留 7 年。
A. 创建⼀个 AWS 备份计划，每⽉第⼀天备份 DynamoDB 表。指定⽣命周期策略，将备份在 6 个⽉后转换为
B. 每⽉第⼀天创建 DynamoDB 表的按需备份。6 个⽉后将备份迁移到 Amazon S3 Glacier Flexible
Retrieval。创建 S3 ⽣命周期策略，删除超过 7 年的备份。
C. 使⽤ AWS SDK 开发⼀个脚本，⽤于按需备份 DynamoDB 表。设置⼀条 Amazon EventBridge 规则，使
其在每⽉的第⼀天运⾏该脚本。创建第⼆个脚本，使其在每⽉的第⼆天运⾏，将超过 6 个⽉的 DynamoDB 备
份迁移到冷存储，并删除超过 7 年的备份。
D. 使⽤ AWS CLI 创建 DynamoDB 表的按需备份。设置⼀条 Amazon EventBridge 规则，通过 cron 表达式
在每⽉的第⼀天运⾏该命令。在命令中指定将备份在 6 个⽉后迁移到冷存储，并在 7 年后删除备份。
https://examlearn.online
[2026/05]
Question #280
Topic 1
⼀家公司在其⽹站上使⽤了 Amazon CloudFront。该公司已在 CloudFront 分发上启⽤⽇志记录，⽇志保存在该
公司的⼀个 Amazon S3 存储桶中。该公司需要对这些⽇志进⾏⾼级分析并构建可视化图表。
解决⽅案架构师应该如何满⾜这些需求？
A. 使⽤ Amazon Athena 中的标准 SQL 查询分析 S3 存储桶中的 CloudFront ⽇志。使⽤ AWS Glue 可视化
结果。
B. 使⽤ Amazon Athena 中的标准 SQL 查询分析 S3 存储桶中的 CloudFront ⽇志。使⽤ Amazon
QuickSight 将结果可视化。
C. 使⽤ Amazon DynamoDB 中的标准 SQL 查询分析 S3 存储桶中的 CloudFront ⽇志。使⽤ AWS Glue 可
视化结果。
D. 使⽤ Amazon DynamoDB 中的标准 SQL 查询分析 S3 存储桶中的 CloudFront ⽇志。使⽤ Amazon
QuickSight 将结果可视化。
Question #281
哪种解决⽅案满⾜这些要求？
Topic 1
⼀家公司使⽤ Amazon RDS for PostgreSQL 数据库实例运⾏着⼤量 Web 服务器。在例⾏合规性检查后，该公
司设定了⼀项标准，要求所有⽣产数据库的恢复点⽬标 (RPO) ⼩于 1 秒。
A. 为数据库实例启⽤多可⽤区部署。
B. 在⼀个可⽤区中为数据库实例启⽤⾃动扩展。
C. 在⼀个可⽤区中配置数据库实例，并在另⼀个可⽤区中创建多个只读副本。
D. 在⼀个可⽤区中配置数据库实例，并配置 AWS 数据库迁移服务 (AWS DMS) 变更数据捕获 (CDC) 任务。
https://examlearn.online
[2026/05]
Question #282
Topic 1
⼀家公司运⾏⼀个 Web 应⽤程序，该应⽤程序部署在 VPC 私有⼦⽹中的 Amazon EC2 实例上。⼀个跨公有⼦
⽹的应⽤程序负载均衡器 (ALB) 将 Web 流量定向到这些 EC2 实例。该公司希望实施新的安全措施，以限制从
ALB 到 EC2 实例的⼊站流量，同时阻⽌来⾃ EC2 实例私有⼦⽹内外任何其他来源的访问。
哪种解决⽅案能够满⾜这些要求？
A. 在路由表中配置路由，将来⾃互联⽹的流量定向到 EC2 实例的私有 IP 地址。
B. 配置 EC2 实例的安全组，使其仅允许来⾃ ALB 安全组的流量。
C. 将 EC2 实例迁移到公有⼦⽹中。为 EC2 实例分配⼀组弹性 IP 地址。
D. 配置 ALB 的安全组，允许任何端⼝上的任何 TCP 流量。
Question #283
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家研究公司运⾏的实验由⼀个仿真应⽤程序和⼀个可视化应⽤程序提供⽀持。仿真应⽤程序运⾏在 Linux 系统
上，每 5 分钟将中间数据输出到 NFS 共享。可视化应⽤程序是⼀个 Windows 桌⾯应⽤程序，⽤于显示仿真输
出，并且需要 SMB ⽂件系统。
该公司维护着两个同步的⽂件系统。这种策略导致数据重复和资源利⽤效率低下。该公司需要在不更改任何应⽤
程序代码的情况下，将这两个应⽤程序迁移到 AWS。
A. 将两个应⽤程序都迁移到 AWS Lambda。创建⼀个 Amazon S3 存储桶，⽤于在应⽤程序之间交换数据。
B. 将两个应⽤程序都迁移到 Amazon Elastic Container Service (Amazon ECS)。配置 Amazon FSx ⽂件⽹
关以进⾏存储。
C. 将仿真应⽤程序迁移到 Linux Amazon EC2 实例。将可视化应⽤程序迁移到 Windows EC2 实例。配置
Amazon Simple Queue Service (Amazon SQS) 以在应⽤程序之间交换数据。
D. 将仿真应⽤程序迁移到 Linux Amazon EC2 实例。将可视化应⽤程序迁移到 Windows EC2 实例。配置
Amazon FSx for NetApp ONTAP 以进⾏存储。
https://examlearn.online
[2026/05]
Question #284
Topic 1
作为预算规划的⼀部分，管理层需要⼀份按⽤户列出的 AWS 计费项⽬报告。这些数据将⽤于编制部⻔预算。解
决⽅案架构师需要确定获取此报告信息的最有效⽅法。
哪种解决⽅案满⾜这些要求？
A. 使⽤ Amazon Athena 运⾏查询以⽣成报告。
B. 在 Cost Explorer 中创建报告并下载报告。
C. 从账单控制⾯板访问账单详情并下载账单。
D. 修改 AWS Budgets 中的成本预算，以便使⽤ Amazon Simple Email Service (Amazon SES) 发出警报。
Question #285
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Service (Amazon SES)。
Topic 1
⼀家公司使⽤ Amazon S3 托管其静态⽹站。该公司希望在其⽹⻚上添加⼀个联系表单。该联系表单将包含动态
服务器端组件，供⽤户输⼊姓名、电⼦邮件地址、电话号码和留⾔。该公司预计每⽉⽹站访问量将少于 100 次。
A. 在 Amazon Elastic Container Service (Amazon ECS) 中托管动态联系表单⻚⾯。设置 Amazon Simple
Email Service (Amazon SES) 以连接到任何第三⽅电⼦邮件提供商。
B. 创建⼀个 Amazon API Gateway 端点，其后端为 AWS Lambda，该后端会调⽤ Amazon Simple Email
C. 通过部署 Amazon Lightsail 将静态⽹⻚转换为动态⽹⻚。使⽤客户端脚本构建联系表单。将该表单与
Amazon WorkMail 集成。
D. 创建⼀个 t2.micro 型 Amazon EC2 实例。部署 LAMP（Linux、Apache、MySQL、PHP/Perl/Python）
架构来托管⽹⻚。使⽤客户端脚本构建联系表单。将表单与 Amazon WorkMail 集成。
https://examlearn.online
[2026/05]
Question #286
Topic 1
⼀家公司拥有⼀个静态⽹站，该⽹站托管在 Amazon CloudFront 上，并以 Amazon S3 为后端存储。该静态⽹
站使⽤数据库作为后端。该公司发现⽹站上的更新⽆法反映其 Git 代码库中的变更。该公司检查了 Git 代码库和
Amazon S3 之间的持续集成和持续交付 (CI/CD) 流⽔线。该公司确认 Webhook 配置正确，并且 CI/CD 流⽔线
发送的消息表明部署成功。
解决⽅案架构师需要实现⼀个解决⽅案，使⽹站上能够显示这些更新。
哪个解决⽅案能够满⾜这些要求？
A. 添加应⽤程序负载均衡器。
B. 将 Amazon ElastiCache for Redis 或 Memcached 添加到 Web 应⽤程序的数据库层。
C. 使 CloudFront 缓存失效。
D. 使⽤ AWS Certificate Manager (ACM) 验证⽹站的 SSL 证书。
Question #287
解决⽅案架构师应该如何设计架构以满⾜这些要求？
Topic 1
⼀家公司希望将⼀个基于 Windows 的应⽤程序从本地迁移到 AWS 云。该应⽤程序包含三个层：应⽤层、业务层
和数据库层（使⽤ Microsoft SQL Server）。该公司希望使⽤ SQL Server 的特定功能，例如原⽣备份和数据质量
服务 (DQS)。此外，该公司还需要在各层之间共享⽂件以进⾏处理。
A. 所有三个层级都托管在 Amazon EC2 实例上。使⽤ Amazon FSx ⽂件⽹关在各层级之间进⾏⽂件共享。
B. 将所有三个层级都托管在 Amazon EC2 实例上。使⽤ Amazon FSx for Windows ⽂件服务器在各层级之
间进⾏⽂件共享。
C. 将应⽤层和业务层托管在 Amazon EC2 实例上。将数据库层托管在 Amazon RDS 上。使⽤ Amazon
Elastic File System (Amazon EFS) 在各层之间共享⽂件。
D. 将应⽤层和业务层托管在 Amazon EC2 实例上。将数据库层托管在 Amazon RDS 上。使⽤预置 IOPS
SSD (io2) Amazon Elastic Block Store (Amazon EBS) 卷在各层之间进⾏⽂件共享。
https://examlearn.online
[2026/05]
Question #288
Topic 1
⼀家公司正在将基于 Linux 的 Web 服务器组迁移到 AWS。这些 Web 服务器需要访问共享⽂件存储中的某些内
容。该公司不得对应⽤程序进⾏任何更改。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 创建⼀个具有对 Web 服务器访问权限的 Amazon S3 标准存储桶。
B. 配置以 Amazon S3 存储桶为源的 Amazon CloudFront 分发。
C. 创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。将 EFS ⽂件系统挂载到所有 Web 服务器
上。
D. 配置通⽤型 SSD (gp3) Amazon Elastic Block Store (Amazon EBS) 卷。将 EBS 卷挂载到所有 Web 服务
器。
Question #289
哪种解决⽅案能够以最安全的⽅式满⾜这些要求？
⼀家公司有⼀个 AWS Lambda 函数，需要读取位于同⼀ AWS 账户中的 Amazon S3 存储桶。
A. 应⽤ S3 存储桶策略，授予对 S3 存储桶的读取权限。
B. 将 IAM ⻆⾊分配给 Lambda 函数。将 IAM 策略分配给该⻆⾊，以授予其对 S3 存储桶的读取权限。
Topic 1
C. 在 Lambda 函数的代码中嵌⼊访问密钥和秘密密钥，以授予对 S3 存储桶进⾏读取访问所需的 IAM 权限。
D. 将 IAM ⻆⾊分配给 Lambda 函数。将 IAM 策略分配给该⻆⾊，以授予其对账户中所有 S3 存储桶的读取
权限。
https://examlearn.online
[2026/05]
Question #290
Topic 1
⼀家公司在多个 Amazon EC2 实例上托管了⼀个 Web 应⽤程序。这些 EC2 实例位于⼀个⾃动扩展组中，可以根
据⽤户需求⾃动扩展。该公司希望在不进⾏⻓期承诺的情况下最⼤限度地节省成本。
为了满⾜这些要求，解决⽅案架构师应该推荐哪种 EC2 实例购买⽅案？
A. 仅限专⽤实例
B. 仅限按需实例
C. 按需实例和竞价实例的混合配置
D. 按需实例和预留实例的混合模式
Question #291
A. 签名 cookie
B. 签名⽹址
C. AWS AppSync
Topic 1
⼀家媒体公司使⽤ Amazon CloudFront 来提供其公开的流媒体视频内容。该公司希望通过控制访问权限来保护
托管在 Amazon S3 中的视频内容。该公司的⼀些⽤户正在使⽤不⽀持 Cookie 的⾃定义 HTTP 客户端。还有⼀
些⽤户⽆法更改他们⽤于访问的硬编码 URL。
哪些服务或⽅法能够以对⽤户影响最⼩的⽅式满⾜这些要求？（选择两项。）
D. JSON Web Token (JWT)
E. AWS Secrets Manager
https://examlearn.online
[2026/05]
Question #292
Topic 1
⼀家公司正在筹备⼀个新的数据平台，该平台将从多个来源接收实时流数据。该公司需要在将数据写⼊ Amazon
S3 之前对其进⾏转换。该公司还需要能够使⽤ SQL 查询转换后的数据。
哪些解决⽅案可以满⾜这些要求？（选择两个。）
A. 使⽤ Amazon Kinesis Data Streams 传输数据。使⽤ Amazon Kinesis Data Analytics 转换数据。使⽤
Amazon Kinesis Data Firehose 将数据写⼊ Amazon S3。使⽤ Amazon Athena 从 Amazon S3 查询转换后
的数据。
B. 使⽤ Amazon Managed Streaming for Apache Kafka (Amazon MSK) 进⾏数据流传输。使⽤ AWS Glue
转换数据并将其写⼊ Amazon S3。使⽤ Amazon Athena 从 Amazon S3 查询转换后的数据。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 导⼊数据。使⽤ Amazon EMR 转换数据并将其写⼊ Amazon
S3。使⽤ Amazon Athena 从 Amazon S3 查询转换后的数据。
D. 使⽤ Amazon Managed Streaming for Apache Kafka (Amazon MSK) 进⾏数据流传输。使⽤ Amazon
Kinesis Data Analytics 转换数据并将其写⼊ Amazon S3。使⽤ Amazon RDS 查询编辑器从 Amazon S3 查
询转换后的数据。
E. 使⽤ Amazon Kinesis Data Streams 传输数据。使⽤ AWS Glue 转换数据。使⽤ Amazon Kinesis Data
Firehose 将数据写⼊ Amazon S3。使⽤ Amazon RDS 查询编辑器从 Amazon S3 查询转换后的数据。
Question #293
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司现有的本地卷备份解决⽅案已达到使⽤寿命。该公司希望使⽤ AWS 作为新的备份解决⽅案的⼀部分，
并希望在数据备份到 AWS 的同时，仍能保持对所有数据的本地访问。该公司还希望确保备份到 AWS 的数据能够
⾃动且安全地传输。
A. 使⽤ AWS Snowball 将数据从本地解决⽅案迁移到 Amazon S3。配置本地系统以挂载 Snowball S3 端
点，从⽽提供对数据的本地访问。
B. 使⽤ AWS Snowball Edge 将数据从本地解决⽅案迁移到 Amazon S3。使⽤ Snowball Edge ⽂件接⼝为
本地系统提供对数据的本地访问。
C. 使⽤ AWS Storage Gateway 并配置缓存卷⽹关。在本地运⾏ Storage Gateway 软件设备，并配置⼀定⽐
例的数据进⾏本地缓存。挂载⽹关存储卷以提供对数据的本地访问。
D. 使⽤ AWS Storage Gateway 并配置存储卷⽹关。在本地运⾏ Storage Gateway 软件设备，并将⽹关存储
卷映射到本地存储。挂载⽹关存储卷以提供对数据的本地访问。
https://examlearn.online
[2026/05]
Question #294
托管在 Amazon EC2 实例上的应⽤程序需要访问 Amazon S3 存储桶。流量不得经过互联⽹。
解决⽅案架构师应如何配置访问权限以满⾜这些要求？
A. 使⽤ Amazon Route 53 创建私有托管区域。
B. 在 VPC 中为 Amazon S3 设置⽹关 VPC 终端节点。
C. 配置 EC2 实例使⽤ NAT ⽹关访问 S3 存储桶。
D. 在 VPC 和 S3 存储桶之间建⽴ AWS 站点到站点 VPN 连接。
Question #295
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
Topic 1
⼀家电商公司在 AWS 云中存储了数 TB 的客户数据。这些数据包含个⼈身份信息 (PII)。该公司希望在三个应⽤
程序中使⽤这些数据。其中只有⼀个应⽤程序需要处理 PII。在其他两个应⽤程序处理数据之前，必须先移除
PII。
A. 将数据存储在 Amazon DynamoDB 表中。创建⼀个代理应⽤层来拦截和处理每个应⽤程序请求的数据。
B. 将数据存储在 Amazon S3 存储桶中。使⽤ S3 Object Lambda 处理和转换数据，然后再将数据返回给请
求应⽤程序。
C. 处理数据并将转换后的数据存储在三个独⽴的 Amazon S3 存储桶中，以便每个应⽤程序拥有⾃⼰的⾃定
义数据集。将每个应⽤程序指向其各⾃的 S3 存储桶。
D. 处理数据并将转换后的数据存储在三个独⽴的 Amazon DynamoDB 表中，以便每个应⽤程序都有⾃⼰的
⾃定义数据集。将每个应⽤程序指向其各⾃的 DynamoDB 表。
https://examlearn.online
[2026/05]
Question #296
Topic 1
开发团队已在开发 VPC 内的 Amazon EC2 实例上部署了⼀个新应⽤程序。解决⽅案架构师需要在同⼀账户中创
建⼀个新的 VPC。新 VPC 将与开发 VPC 建⽴对等连接。开发 VPC 的 CIDR 块为 192.168.0.0/24。解决⽅案架
构师需要为新 VPC 创建⼀个 CIDR 块。该 CIDR 块必须对与开发 VPC 的 VPC 对等连接有效。
满⾜这些要求的最⼩ CIDR 块是多少？
A. 10.0.1.0/32
B. 192.168.0.0/24
C. 192.168.1.0/32
D. 10.0.1.0/24
Question #297
⼀家公司在五个 Amazon EC2 实例上部署了⼀个应⽤程序。应⽤程序负载均衡器 (ALB) 通过⽬标组将流量分配
到各个实例。⼤多数情况下，每个实例的平均 CPU 使⽤率低于 10%，偶尔会飙升⾄ 65%。
哪个解决⽅案能够满⾜这些要求？
Topic 1
解决⽅案架构师需要实施⼀个解决⽅案来⾃动扩展应⽤程序。该解决⽅案必须优化架构成本，并确保应⽤程序在
出现流量⾼峰时拥有⾜够的 CPU 资源。
A. 创建⼀个 Amazon CloudWatch 警报，当 CPUUtilization 指标低于 20% 时，该警报进⼊ ALARM 状态。
创建⼀个 AWS Lambda 函数，CloudWatch 警报会调⽤该函数来终⽌ ALB ⽬标组中的⼀个 EC2 实例。
B. 创建⼀个 EC2 ⾃动扩展组。选择现有的 ALB 作为负载均衡器，选择现有的⽬标组作为⽬标组。设置⼀个
基于 ASGAverageCPUUtilization 指标的⽬标跟踪扩展策略。将最⼩实例数设置为 2，所需容量设置为 3，最
⼤实例数设置为 6，⽬标值设置为 50%。将 EC2 实例添加到⾃动扩展组。
C. 创建⼀个 EC2 ⾃动扩展组。选择现有的 ALB 作为负载均衡器，选择现有的⽬标组作为⽬标组。将最⼩实
例数设置为 2，所需容量设置为 3，最⼤实例数设置为 6。将 EC2 实例添加到⾃动扩展组。
D. 创建两个 Amazon CloudWatch 告警。将第⼀个 CloudWatch 告警配置为在平均 CPU 利⽤率低于 20%
时进⼊ ALARM 状态。将第⼆个 CloudWatch 告警配置为在平均 CPU 利⽤率⾼于 50% 时进⼊ ALARM 状
态。配置告警发布到 Amazon Simple Notification Service (Amazon SNS) 主题以发送电⼦邮件。收到邮件
后，登录系统以减少或增加正在运⾏的 EC2 实例数量。
https://examlearn.online
[2026/05]
Question #298
Topic 1
⼀家公司在应⽤程序负载均衡器 (APP) 后⽅的 Amazon EC2 实例上运⾏关键业务应⽤程序。这些 EC2 实例运⾏
在⾃动扩展组中，并访问 Amazon RDS 数据库实例。
由于 EC2 实例和数据库实例都位于同⼀个可⽤区，因此该设计未通过运维审查。解决⽅案架构师必须更新设计，
使其使⽤第⼆个可⽤区。
哪种解决⽅案能够实现应⽤程序的⾼可⽤性？
A. 在每个可⽤区中配置⼀个⼦⽹。配置⾃动扩展组，将 EC2 实例分布在两个可⽤区中。配置数据库实例，使
其连接到每个⽹络。
B. 配置两个跨越两个可⽤区的⼦⽹。配置⾃动扩展组，将 EC2 实例分布在两个可⽤区中。配置数据库实例，
使其连接到每个⽹络。
C. 在每个可⽤区中配置⼦⽹。配置⾃动扩展组，将 EC2 实例分布在两个可⽤区中。配置数据库实例以⽀持多
可⽤区部署。
D. 配置⼀个跨越两个可⽤区的⼦⽹。配置⾃动扩展组，将 EC2 实例分布在两个可⽤区中。配置数据库实例以
⽀持多可⽤区部署。
Question #299
哪种解决⽅案能够满⾜性能要求？
Topic 1
⼀个研究实验室需要处理⼤约 8 TB 的数据。该实验室要求存储⼦系统的延迟低于毫秒级，吞吐量⾄少为 6
GBps。数百个运⾏ Amazon Linux 的 Amazon EC2 实例将负责分发和处理这些数据。
A. 创建⼀个适⽤于 NetApp ONTAP 的 Amazon FSx ⽂件系统。将每个卷的分层策略设置为“全部”。将原始
数据导⼊⽂件系统。将⽂件系统挂载到 EC2 实例上。
B. 创建⼀个 Amazon S3 存储桶来存储原始数据。创建⼀个使⽤持久性 SSD 存储的 Amazon FSx for Lustre
⽂件系统。选择从 Amazon S3 导⼊数据和向 Amazon S3 导出数据的选项。将该⽂件系统挂载到 EC2 实例
上。
C. 创建⼀个 Amazon S3 存储桶来存储原始数据。创建⼀个使⽤持久性 HDD 存储的 Amazon FSx for Lustre
⽂件系统。选择从 Amazon S3 导⼊数据和向 Amazon S3 导出数据的选项。将该⽂件系统挂载到 EC2 实例
上。
D. 创建⼀个适⽤于 NetApp ONTAP 的 Amazon FSx ⽂件系统。将每个卷的分层策略设置为“⽆”。将原始数
据导⼊⽂件系统。将⽂件系统挂载到 EC2 实例上。
https://examlearn.online
[2026/05]
Question #300
由于硬件容量限制，⼀家公司需要将⼀个传统应⽤程序从本地数据中⼼迁移到 AWS 云。该应⽤程序每周 7 天、
每天 24 ⼩时运⾏，并且其数据库存储空间会随着时间的推移⽽持续增⻓。
解决⽅案架构师应该如何以最具成本效益的⽅式满⾜这些要求？
A. 将应⽤层迁移到 Amazon EC2 Spot 实例。将数据存储层迁移到 Amazon S3。
B. 将应⽤层迁移到 Amazon EC2 预留实例。将数据存储层迁移到 Amazon RDS 按需实例。
C. 将应⽤层迁移到 Amazon EC2 预留实例。将数据存储层迁移到 Amazon Aurora 预留实例。
D. 将应⽤层迁移到 Amazon EC2 按需实例。将数据存储层迁移到 Amazon RDS 预留实例。
Topic 1
https://examlearn.online
[2026/05]
Question #301
Topic 1
某⼤学研究实验室需要将 30 TB 的数据从本地 Windows ⽂件服务器迁移到 Amazon FSx for Windows ⽂件服务
器。该实验室拥有⼀条 1 Gbps 的⽹络链路，⼤学内许多其他部⻔也共享这条链路。
实验室希望部署⼀个数据迁移服务，以最⼤限度地提⾼数据传输性能。但是，实验室需要能够控制该服务使⽤的
带宽，以最⼤程度地减少对其他部⻔的影响。数据迁移必须在未来 5 天内完成。
哪种 AWS 解决⽅案能够满⾜这些要求？
A. AWS 雪锥
B. Amazon FSx ⽂件⽹关
C. AWS 数据同步
D. AWS Transfer 系列
Question #302
Topic 1
⼀家公司希望开发⼀款移动应⽤，使⽤户能够在移动设备上流畅播放慢动作视频。⽬前，该应⽤会捕获视频⽚
段，并以原始格式将其上传到 Amazon S3 存储桶。应⽤会直接从 S3 存储桶中检索这些视频⽚段。然⽽，原始
格式的视频⽂件较⼤，
导致⽤户在移动设备上遇到缓冲和播放问题。该公司希望找到解决⽅案，在最⼤限度提⾼应⽤性能和可扩展性的
同时，最⼤限度地降低运维开销。
以下哪两项解决⽅案组合能够满⾜这些要求？（选择两项。）
A. 部署 Amazon CloudFront 进⾏内容分发和缓存。
B. 使⽤ AWS DataSync 将视频⽂件复制到 AW 的不同区域中的其他 S3 存储桶中。
C. 使⽤ Amazon Elastic Transcoder 将视频⽂件转换为更合适的格式。
D. 在本地区域中部署 Amazon EC2 实例的⾃动密封组，⽤于内容分发和缓存。
E. 部署 Amazon EC2 实例的⾃动扩展组，将视频⽂件转换为更合适的格式。
https://examlearn.online
[2026/05]
Question #303
Topic 1
⼀家公司正在部署⼀个基于 Amazon Elastic Container Service (Amazon ECS) 集群的新应⽤程序，并使⽤
Fargate 启动类型来执⾏ ECS 任务。由于预计应⽤程序上线初期会⾯临⾼流量，该公司正在监控 CPU 和内存使
⽤情况。然⽽，该公司也希望在资源利⽤率下降时降低成本。
解决⽅案架构师应该如何建议？
A. 使⽤ Amazon EC2 ⾃动扩展功能，根据以往的流量模式，按特定周期进⾏扩展。
B. 使⽤ AWS Lambda 函数根据触发 Amazon CloudWatch 警报的指标违规情况来扩展 Amazon ECS。
C. 使⽤ Amazon EC2 Auto Scaling 和简单的扩展策略，在 ECS 指标超出限制触发 Amazon CloudWatch 警
报时进⾏扩展。
D. 使⽤ AWS 应⽤程序⾃动扩展和⽬标跟踪策略，在 ECS 指标违规触发 Amazon CloudWatch 警报时进⾏扩
展。
Question #304
A. 使⽤ AWS DataSync。
Topic 1
⼀家公司最近在另⼀个 AWS 区域创建了⼀个灾难恢复站点。该公司需要定期在两个区域的 NFS ⽂件系统之间来
回传输⼤量数据。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
B. 使⽤ AWS Snowball 设备。
C. 在 Amazon EC2 上设置 SFTP 服务器。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS)。
https://examlearn.online
[2026/05]
Question #305
Topic 1
⼀家公司正在为其托管在 AWS 云上的游戏应⽤程序设计共享存储解决⽅案。该公司需要能够使⽤ SMB 客户端访
问数据。该解决⽅案必须是完全托管的。
哪个 AWS 解决⽅案满⾜这些要求？
A. 创建⼀个 AWS DataSync 任务，将数据共享为可挂载的⽂件系统。将该⽂件系统挂载到应⽤程序服务器。
B. 创建⼀个 Amazon EC2 Windows 实例。在该实例上安装并配置 Windows ⽂件共享⻆⾊。将应⽤程序服务
器连接到该⽂件共享。
C. 创建 Amazon FSx for Windows ⽂件服务器⽂件系统。将该⽂件系统附加到源服务器。将应⽤程序服务器
连接到该⽂件系统。
D. 创建⼀个 Amazon S3 存储桶。为应⽤程序分配⼀个 IAM ⻆⾊，以授予其访问 S3 存储桶的权限。将 S3
存储桶挂载到应⽤程序服务器。
Question #306
哪种解决⽅案符合这些要求？
Topic 1
⼀家公司希望为⼀款对延迟⾮常敏感的应⽤程序运⾏内存数据库，该应⽤程序运⾏在 Amazon EC2 实例上。该应
⽤程序每分钟处理超过 10 万笔交易，需要⾼⽹络吞吐量。解决⽅案架构师需要提供⼀种经济⾼效的⽹络设计⽅
案，以最⼤限度地降低数据传输费⽤。
A. 在同⼀ AWS 区域内的同⼀可⽤区中启动所有 EC2 实例。启动 EC2 实例时，指定带有集群策略的放置组。
B. 在同⼀ AWS 区域内的不同可⽤区中启动所有 EC2 实例。启动 EC2 实例时，指定带有分区策略的放置组。
C. 部署⾃动扩展组，根据⽹络利⽤率⽬标在不同的可⽤区启动 EC2 实例。
D. 部署具有步进式扩展策略的⾃动扩展组，以在不同的可⽤区启动 EC2 实例。
https://examlearn.online
[2026/05]
Question #307
Topic 1
⼀家主要在本地运⾏应⽤服务器的公司决定迁移到 AWS。该公司希望尽可能减少在本地扩展 iSCSI 存储的需求，
并且只希望最近访问的数据保留在本地。
为了满⾜这些要求，该公司应该使⽤哪种 AWS 解决⽅案？
A. Amazon S3 ⽂件⽹关
B. AWS 存储⽹关磁带⽹关
C. AWS Storage Gateway 卷⽹关存储卷
D. AWS Storage Gateway 卷⽹关缓存卷
Question #308
Topic 1
⼀家公司拥有多个使⽤合并计费的 AWS 账户。该公司运⾏多个⾼性能 Amazon RDS for Oracle On-Demand
DB 实例，运⾏时间为 90 天。该公司财务团队可以在合并计费账户以及所有其他 AWS 账户中访问 AWS Trusted
Advisor。
财务团队需要使⽤相应的 AWS 账户来访问 Trusted Advisor 对 RDS 的检查建议。财务团队必须审核相应的
Trusted Advisor 检查建议，以降低 RDS 成本。
财务团队应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 使⽤运⾏ RDS 实例的帐户中的 Trusted Advisor 建议。
B. 使⽤合并账单帐户中的 Trusted Advisor 建议，同时查看所有 RDS 实例检查。
C. 检查 Amazon RDS 预留实例优化的 Trusted Advisor 检查。
D. 检查 Amazon RDS 空闲数据库实例的 Trusted Advisor 检查。
E. 检查 Amazon Redshift 预留节点优化的 Trusted Advisor 检查。
https://examlearn.online
[2026/05]
Question #309
解决⽅案架构师需要优化存储成本。他必须找出所有不再访问或很少访问的 Amazon S3 存储桶。
哪种解决⽅案能够以最⼩的运维开销实现这⼀⽬标？
A. 使⽤ S3 Storage Lens 控制⾯板分析存储桶访问模式，以获取⾼级活动指标。
B. 使⽤ AWS 管理控制台中的 S3 控制⾯板分析存储桶访问模式。
Topic 1
C. 为存储桶启⽤ Amazon CloudWatch BucketSizeBytes 指标。使⽤ Amazon Athena 和这些指标数据分析
存储桶访问模式。
D. 启⽤ AWS CloudTrail 以监控 S3 对象。通过使⽤与 Amazon CloudWatch Logs 集成的 CloudTrail ⽇志来
分析存储桶访问模式。
Question #310
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司向从事⼈⼯智能和机器学习 (AI/ML) 研究的客户销售数据集。这些数据集是存储在美国东部 1 区
Amazon S3 存储桶中的⼤型格式化⽂件。该公司托管了⼀个 Web 应⽤程序，客户可以通过该应⽤程序购买对特
定数据集的访问权限。该 Web 应⽤程序部署在多个 Amazon EC2 实例上，并由应⽤程序负载均衡器
(Application Load Balancer) 进⾏负载均衡。购买完成后，客户会收到⼀个 S3 签名 URL，该 URL 允许他们访
问⽂件。
客户分布在北美和欧洲。该公司希望降低数据传输成本，并保持或提⾼性能。
A. 在现有 S3 存储桶上配置 S3 传输加速。将客户请求定向到 S3 传输加速端点。继续使⽤ S3 签名 URL 进⾏
访问控制。
B. 部署⼀个以现有 S3 存储桶为源的 Amazon CloudFront 分发。将客户请求定向到 CloudFront URL。切换
到 CloudFront 签名 URL 以进⾏访问控制。
C. 在 eu-central-1 区域设置第⼆个 S3 存储桶，并在两个存储桶之间启⽤ S3 跨区域复制。将客户请求定向
到最近的区域。继续使⽤ S3 签名 URL 进⾏访问控制。
D. 修改 Web 应⽤程序，使其能够向最终⽤户流式传输数据集。配置 Web 应⽤程序以从现有的 S3 存储桶读
取数据。直接在应⽤程序中实现访问控制。
https://examlearn.online
[2026/05]
Question #311
Topic 1
⼀家公司正在使⽤ AWS 设计⼀个⽤于处理保险报价的 Web 应⽤程序。⽤户将通过该应⽤程序请求报价。报价必
须按报价类型分类，必须在 24 ⼩时内得到回复，并且不能丢失。该解决⽅案必须最⼤限度地提⾼运营效率并最
⼤限度地减少维护⼯作。
哪个解决⽅案满⾜这些要求？
A. 根据报价类型创建多个 Amazon Kinesis 数据流。配置 Web 应⽤程序以将消息发送到正确的数据流。配置
每个后端应⽤程序服务器组，使其使⽤ Kinesis 客户端库 (KCL) 来汇集来⾃其⾃身数据流的消息。
B. 为每种报价类型创建⼀个 AWS Lambda 函数和⼀个 Amazon Simple Notification Service (Amazon
SNS) 主题。将 Lambda 函数订阅到其关联的 SNS 主题。配置应⽤程序，使其将报价请求发布到相应的 SNS
主题。
C. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。将 Amazon Simple Queue
Service (Amazon SQS) 队列订阅到该 SNS 主题。配置 SNS 消息过滤，以便根据报价类型将消息发布到相应
的 SQS 队列。配置每个后端应⽤程序服务器使⽤其⾃身的 SQS 队列。
D. 根据报价类型创建多个 Amazon Kinesis Data Firehose 数据流，以便将数据流交付到 Amazon
OpenSearch Service 集群。配置应⽤程序将消息发送到正确的数据流。配置每个后端应⽤程序服务器组，使
其能够从 OpenSearch Service 搜索消息并进⾏相应的处理。
Question #312
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
Topic 1
⼀家公司有⼀个应⽤程序运⾏在多个 Amazon EC2 实例上。每个 EC2 实例都附加了多个 Amazon Elastic Block
Store (Amazon EBS) 数据卷。该应⽤程序的 EC2 实例配置和数据需要每晚备份。此外，该应⽤程序还需要能够
在不同的 AWS 区域恢复。
A. 编写⼀个 AWS Lambda 函数，该函数安排每晚对应⽤程序的 EBS 卷进⾏快照，并将快照复制到不同的区
域。
B. 使⽤ AWS Backup 创建备份计划，执⾏每⽇备份。将备份复制到另⼀个区域。将应⽤程序的 EC2 实例添
加为资源。
C. 使⽤ AWS Backup 创建备份计划，执⾏每⽇备份。将备份复制到另⼀个区域。将应⽤程序的 EBS 卷添加
为资源。
D. 编写⼀个 AWS Lambda 函数，该函数安排每晚对应⽤程序的 EBS 卷进⾏快照，并将快照复制到不同的可
⽤区。
https://examlearn.online
[2026/05]
Question #313
Topic 1
⼀家公司正在AWS上构建移动应⽤。该公司希望将⽤户覆盖范围扩⼤到数百万。该公司需要构建⼀个平台，以便
授权⽤户可以在其移动设备上观看该公司的内容。
解决⽅案架构师应该推荐什么⽅案来满⾜这些需求？
A. 将内容发布到公共 Amazon S3 存储桶。使⽤ AWS Key Management Service (AWS KMS) 密钥来流式传
输内容。
B. 在移动应⽤程序和 AWS 环境之间设置 IPsec VPN 以传输内容。
C. 使⽤ Amazon CloudFront。提供已签名的 URL 以流式传输内容。
D. 在移动应⽤程序和 AWS 环境之间设置 AWS 客户端 VPN 以流式传输内容。
Question #314
解决⽅案架构师应该推荐哪种服务？
A. Amazon Aurora MySQL
Topic 1
⼀家公司拥有⼀个本地部署的 MySQL 数据库，供全球销售团队使⽤，访问频率较低。销售团队要求数据库停机
时间尽可能短。数据库管理员希望将此数据库迁移到 AWS，但考虑到未来⽤户数量可能增加，因此没有选择特定
的实例类型。
B. Amazon Aurora Serverless for MySQL
C. 亚⻢逊红移光谱
D. Amazon RDS for MySQL
https://examlearn.online
[2026/05]
Question #315
Topic 1
⼀家公司遭遇安全漏洞攻击，导致其本地数据中⼼的多个应⽤程序受到影响。攻击者利⽤了服务器上运⾏的⾃定
义应⽤程序中的漏洞。该公司⽬前正在将其应⽤程序迁移到 Amazon EC2 实例上运⾏。该公司希望部署⼀种解决
⽅案，能够主动扫描 EC2 实例上的漏洞，并⽣成⼀份包含详细扫描结果的报告。
哪种解决⽅案能够满⾜这些要求？
A. 部署 AWS Shield 扫描 EC2 实例是否存在漏洞。创建⼀个 AWS Lambda 函数，将所有发现的漏洞记录到
AWS CloudTrail。
B. 部署 Amazon Macie 和 AWS Lambda 函数，扫描 EC2 实例是否存在漏洞。将所有发现的漏洞记录到
AWS CloudTrail。
C. 启⽤ Amazon GuardDuty。将 GuardDuty 代理部署到 EC2 实例。配置 AWS Lambda 函数以⾃动⽣成和
分发详细说明调查结果的报告。
Question #316
D. 启⽤ Amazon Inspector。将 Amazon Inspector 代理部署到 EC2 实例。配置 AWS Lambda 函数以⾃动
⽣成和分发详细说明调查结果的报告。
Topic 1
⼀家公司使⽤ Amazon EC2 实例运⾏脚本，轮询并处理 Amazon Simple Queue Service (Amazon SQS) 队列中
的消息。该公司希望在降低运营成本的同时，保持处理不断增⻓的队列消息的能⼒。
解决⽅案架构师应该提出怎样的建议才能满⾜这些要求？
A. 增加 EC2 实例的⼤⼩，以更快地处理消息。
B. 当 EC2 实例利⽤率不⾜时，使⽤ Amazon EventBridge 关闭该 EC2 实例。
C. 将 EC2 实例上的脚本迁移到具有适当运⾏时的 AWS Lambda 函数。
D. 使⽤ AWS Systems Manager Run Command 按需运⾏脚本。
https://examlearn.online
[2026/05]
Question #317
Topic 1
⼀家公司使⽤旧版应⽤程序⽣成 CSV 格式的数据。该旧版应⽤程序将输出数据存储在 Amazon S3 中。该公司正
在部署⼀款新的商⽤现成 (COTS) 应⽤程序，该应⽤程序可以执⾏复杂的 SQL 查询来分析仅存储在 Amazon
Redshift 和 Amazon S3 中的数据。但是，该 COTS 应⽤程序⽆法处理旧版应⽤程序⽣成的 .csv ⽂件。
该公司也⽆法更新旧版应⽤程序以⽣成其他格式的数据。该公司需要实施⼀个解决⽅案，使 COTS 应⽤程序能够
使⽤旧版应⽤程序⽣成的数据。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个按计划运⾏的 AWS Glue 提取、转换和加载 (ETL) 作业。配置 ETL 作业以处理 .csv ⽂件并将处
理后的数据存储在 Amazon Redshift 中。
B. 开发⼀个在 Amazon EC2 实例上运⾏的 Python 脚本，将 .csv ⽂件转换为 .sql ⽂件。通过 cron 定时任务
调⽤该 Python 脚本，将输出⽂件存储到 Amazon S3 中。
C. 创建⼀个 AWS Lambda 函数和⼀个 Amazon DynamoDB 表。使⽤ S3 事件调⽤ Lambda 函数。配置
Lambda 函数执⾏提取、转换和加载 (ETL) 作业，以处理 .csv ⽂件并将处理后的数据存储到 DynamoDB 表
中。
D. 使⽤ Amazon EventBridge 按周计划启动 Amazon EMR 集群。配置 EMR 集群以执⾏提取、转换和加载
(ETL) 作业，处理 .csv ⽂件并将处理后的数据存储在 Amazon Redshift 表中。
Question #318
Topic 1
⼀家公司最近将其整个 IT 环境迁移到了 AWS 云。该公司发现⽤户在未遵循适当的变更控制流程的情况下，配置
了过⼤的 Amazon EC2 实例并修改了安全组规则。解决⽅案架构师必须制定策略来跟踪和审核这些清单和配置变
更。
为了满⾜这些要求，解决⽅案架构师应该采取哪些措施？（选择两项。）
A. 启⽤ AWS CloudTrail 并将其⽤于审计。
B. 对 Amazon EC2 实例使⽤数据⽣命周期策略。
C. 启⽤ AWS Trusted Advisor 并参考安全仪表板。
D. 启⽤ AWS Config 并创建⽤于审计和合规⽬的的规则。
E. 使⽤ AWS CloudFormation 模板恢复先前的资源配置。
https://examlearn.online
[2026/05]
Question #319
Topic 1
⼀家公司在 AWS 云中拥有数百个基于 Linux 的 Amazon EC2 实例。系 统管理员⼀直使⽤共享 SSH 密钥来管理
这些实例。最近⼀次审计后，公司安全团队要求移除所有共享密钥。解决⽅案架构师必须设计⼀个能够安全访问
这些 EC2 实例的⽅案。
哪种⽅案能够在满⾜此要求的同时，将管理开销降⾄最低？
A. 使⽤ AWS Systems Manager Session Manager 连接到 EC2 实例。
B. 使⽤ AWS 安全令牌服务 (AWS STS) 按需⽣成⼀次性 SSH 密钥。
C. 允许对⼀组堡垒机实例进⾏共享 SSH 访问。配置所有其他实例，使其仅允许来⾃堡垒机实例的 SSH 访
问。
D. 使⽤ Amazon Cognito ⾃定义授权器对⽤户进⾏身份验证。调⽤ AWS Lambda 函数⽣成临时 SSH 密钥。
Question #320
Redshift 查询数据。
Topic 1
⼀家公司使⽤⼀组 Amazon EC2 实例从本地数据源提取数据。数据采⽤ JSON 格式，提取速率最⾼可达 1
MB/s。当 EC2 实例重启时，传输中的数据会丢失。该公司的数据科学团队希望近乎实时地查询已提取的数据。
哪种解决⽅案能够提供可扩展的近实时数据查询，并将数据丢失降⾄最低？
A. 将数据发布到 Amazon Kinesis Data Streams，使⽤ Kinesis Data Analytics 查询数据。
B. 将数据发布到 Amazon Kinesis Data Firehose，并将 Amazon Redshift 作为⽬标位置。使⽤ Amazon
C. 将摄取的数据存储在 EC2 实例存储中。将数据发布到 Amazon Kinesis Data Firehose，并将 Amazon S3
设置为⽬标存储。使⽤ Amazon Athena 查询数据。
D. 将摄取的数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷中。将数据发布到 Amazon
ElastiCache for Redis。订阅 Redis 通道以查询数据。
https://examlearn.online
[2026/05]
Question #321
解决⽅案架构师应该如何确保上传到 Amazon S3 存储桶的所有对象都经过加密？
A. 更新存储桶策略，如果 PutObject 没有设置 s3:x-amz-acl 标头，则拒绝该存储桶。
B. 更新存储桶策略，如果 PutObject 没有将 s3:x-amz-acl 标头设置为 private，则拒绝该存储桶。
Topic 1
C. 更新存储桶策略，如果 PutObject 没有将 aws:SecureTransport 标头设置为 true，则拒绝该存储桶。
D. 更新存储桶策略，如果 PutObject 没有设置 x-amz-server-side-encryption 标头，则拒绝该存储桶。
Question #322
⼀位解决⽅案架构师正在为⼀家公司设计⼀个多层应⽤程序。该应⽤程序的⽤户可以通过移动设备上传图⽚。应
⽤程序会为每张图⽚⽣成缩略图，并向⽤户返回⼀条消息，确认图⽚已成功上传。
为了满⾜这些要求，解决⽅案架构师应该怎么做？
Lambda 函数。
Topic 1
缩略图⽣成过程最多可能需要 60 秒，但该公司希望更快地响应⽤户，告知他们已收到原始图⽚。解决⽅案架构
师必须设计应⽤程序，使其能够异步地将请求分发到不同的应⽤程序层。
A. 编写⼀个⾃定义的 AWS Lambda 函数来⽣成缩略图并提醒⽤户。使⽤图像上传过程作为事件源来调⽤该
B. 创建⼀个 AWS Step Functions ⼯作流。配置 Step Functions 来处理应⽤程序层之间的协调，并在缩略图
⽣成完成后提醒⽤户。
C. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 消息队列。当图⽚上传时，将⼀条消息放⼊
SQS 队列以⽣成缩略图。通过应⽤程序消息通知⽤户图⽚已收到。
D. 创建 Amazon Simple Notification Service (Amazon SNS) 通知主题和订阅。使⽤⼀个订阅在应⽤程序上
传图⽚完成后⽣成缩略图。使⽤第⼆个订阅在缩略图⽣成完成后通过推送通知向⽤户的移动应⽤发送消息。
https://examlearn.online
[2026/05]
Question #323
某公司办公楼的每个⼊⼝都安装了⻔禁读卡器。当有⼈刷卡时，读卡器会通过 HTTPS 发送消息，指示是谁试图
进⼊该⼊⼝。
解决⽅案架构师需要设计⼀个系统来处理来⾃传感器的这些消息。该解决⽅案必须具有⾼可⽤性，并且处理结果
必须可供公司安全团队分析。
解决⽅案架构师应该推荐哪种系统架构？
消息并将结果保存到 Amazon DynamoDB 表中。
Topic 1
A. 启动⼀个 Amazon EC2 实例作为 HTTPS 端点并处理消息。配置该 EC2 实例将结果保存到 Amazon S3 存
储桶。
B. 在 Amazon API Gateway 中创建 HTTPS 端点。配置 API Gateway 端点以调⽤ AWS Lambda 函数来处理
C. 使⽤ Amazon Route 53 将传⼊的传感器消息定向到 AWS Lambda 函数。配置 Lambda 函数以处理消息
并将结果保存到 Amazon DynamoDB 表中。
D. 为 Amazon S3 创建⽹关 VPC 端点。配置从设施⽹络到 VPC 的站点到站点 VPN 连接，以便可以通过
VPC 端点将传感器数据直接写⼊ S3 存储桶。
https://examlearn.online
[2026/05]
Question #324
⼀家公司希望为其主要本地⽂件存储卷实施灾难恢复计划。该⽂件存储卷通过互联⽹⼩型计算机系统接⼝ (iSCSI)
设备挂载到本地存储服务器上。该⽂件存储卷存储着数百 TB 的数据。该公司希望确保
最终⽤户能够⽴即从本地系统访问所有⽂件类型，且不会出现延迟。
哪种解决⽅案能够在对公司现有基础架构进⾏最少更改的情况下满⾜这些要求？
A. 在本地部署⼀台 Amazon S3 ⽂件⽹关虚拟机 (VM)。将本地缓存设置为 10 TB。修改现有应⽤程序，使其
通过 NFS 协议访问⽂件。发⽣灾难恢复时，部署⼀个 Amazon EC2 实例并挂载包含⽂件的 S3 存储桶。
B. 配置 AWS Storage Gateway 磁带⽹关。使⽤数据备份解决⽅案将所有现有数据备份到虚拟磁带库。配置
据从虚拟磁带库中的卷恢复到 Amazon Elastic Block Store (Amazon EBS) 卷。
Amazon EC2 实例。
Topic 1
数据备份解决⽅案，使其在初始备份完成后每晚运⾏。要从灾难中恢复，请配置 Amazon EC2 实例，并将数
C. 配置⼀个 AWS Storage Gateway Volume Gateway 缓存卷。将本地缓存设置为 10 TB。使⽤ iSCSI 将
Volume Gateway 缓存卷挂载到现有⽂件服务器，并将所有⽂件复制到该存储卷。配置该存储卷的计划快照。
要从灾难中恢复，请将快照还原到 Amazon Elastic Block Store (Amazon EBS) 卷，并将该 EBS 卷附加到
D. 预置⼀个与现有⽂件存储卷磁盘空间相同的 AWS Storage Gateway Volume Gateway 存储卷。使⽤
iSCSI 将 Volume Gateway 存储卷挂载到现有⽂件服务器，并将所有⽂件复制到该存储卷。配置存储卷的计
划快照。要从灾难中恢复，请将快照还原到 Amazon Elastic Block Store (Amazon EBS) 卷，并将该 EBS 卷
附加到 Amazon EC2 实例。
https://examlearn.online
[2026/05]
Question #325
Topic 1
⼀家公司将 Web 应⽤程序托管在 Amazon S3 存储桶中。该应⽤程序使⽤ Amazon Cognito 作为身份提供程序
来验证⽤户身份，并返回⼀个 JSON Web Token (JWT)，该 JWT 提供对存储在另⼀个 S3 存储桶中的受保护资
源的访问权限。
应⽤程序部署后，⽤户报告错误，并且⽆法访问受保护的内容。解决⽅案架构师必须通过提供适当的权限来解决
此问题，以便⽤户能够访问受保护的内容。
哪个解决⽅案满⾜这些要求？
A. 更新 Amazon Cognito 身份池，使其承担访问受保护内容的适当 IAM ⻆⾊。
B. 更新 S3 ACL，允许应⽤程序访问受保护的内容。
C. 将应⽤程序重新部署到 Amazon S3，以防⽌ S3 存储桶中的最终⼀致性读取影响⽤户访问受保护内容的能
⼒。
D. 更新 Amazon Cognito 池，使其在身份池中使⽤⾃定义属性映射，并授予⽤户访问受保护内容的适当权
限。
Question #326
Topic 1
⼀家图⽚托管公司将其⼤型资产上传到 Amazon S3 标准存储桶。该公司使⽤ S3 API 进⾏并⾏分段上传，如果同
⼀对象被重复上传，则会覆盖已上传的内容。上传后的前 30 天，这些对象会被频繁访问。30 天后，对象的访问
频率会降低，但每个对象的访问模式将不再⼀致。该公司必须在保持存储资产的⾼可⽤性和弹性的同时，优化其
S3 存储成本。
解决⽅案架构师应推荐哪些措施组合来满⾜这些要求？（选择两项。）
A. 30 天后将资产迁移到 S3 智能分层存储。
B. 配置 S3 ⽣命周期策略以清理不完整的分段上传。
C. 配置 S3 ⽣命周期策略以清理过期对象删除标记。
D. 30 天后将资产迁移到 S3 标准-不频繁访问 (S3 标准-IA)。
E. 30 天后将资产迁移到 S3 单区-不频繁访问 (S3 单区-IA)。
https://examlearn.online
[2026/05]
Question #327
Topic 1
解决⽅案架构师需要保护托管 Amazon EC2 实例的 VPC ⽹络。这些 EC2 实例包含⾼度敏感的数据，并在私有⼦
⽹中运⾏。根据公司政策，运⾏在 VPC 中的 EC2 实例只能访问经批准的第三⽅软件仓库，并通过第三⽅提供的
URL 获取软件产品更新。其他互联⽹流量必须被阻⽌。
哪种解决⽅案满⾜这些要求？
A. 更新私有⼦⽹的路由表，将出站流量路由到 AWS ⽹络防⽕墙。配置域列表规则组。
B. 设置 AWS WAF Web ACL。创建⼀组⾃定义规则，根据源 IP 地址和⽬标 IP 地址范围过滤流量请求。
C. 实施严格的⼊站安全组规则。配置出站规则，通过指定 URL，仅允许流量访问互联⽹上已授权的软件存储
库。
D. 在 EC2 实例前⾯配置应⽤程序负载均衡器 (ALB)。将所有出站流量定向到 ALB。在 ALB 的⽬标组中使⽤
基于 URL 的规则监听器，以允许出站访问互联⽹。
Question #328
Topic 1
⼀家公司在 AWS 云上托管了⼀个三层架构的电⼦商务应⽤程序。该公司将⽹站托管在 Amazon S3 上，并将其与
⼀个处理销售请求的 API 集成。该 API 托管在三个 Amazon EC2 实例上，并由应⽤程序负载均衡器 (ALB) 进⾏
负载均衡。该 API 包含静态和动态前端内容，以及异步处理销售请求的后端⼯作进程。
该公司预计在新产品发布活动期间，销售请求数量将出现显著且突然的增⻓。
解决⽅案架构师应该提出哪些建议，以确保所有请求都能成功处理？
A. 添加 Amazon CloudFront 分发以⽤于动态内容。增加 EC2 实例数量以应对流量增⻓。
B. 添加⽤于静态内容的 Amazon CloudFront 分发。将 EC2 实例置于⾃动扩展组中，以便根据⽹络流量启动
新实例。
C. 添加⼀个 Amazon CloudFront 分发⽤于动态内容。在 ALB 前端添加⼀个 Amazon ElastiCache 实例，以
减少 API 需要处理的流量。
D. 添加⽤于静态内容的 Amazon CloudFront 分发。添加 Amazon Simple Queue Service (Amazon SQS)
队列，⽤于接收来⾃⽹站的请求，以便稍后由 EC2 实例进⾏处理。
https://examlearn.online
[2026/05]
Question #329
Topic 1
安全审计发现，Amazon EC2 实例未定期打补丁。解决⽅案架构师需要提供⼀个⽅案，对⼤量 EC2 实例进⾏定
期安全扫描。该⽅案还应按计划定期为 EC2 实例打补丁，并提供每个实例的补丁状态报告。
哪个⽅案能够满⾜这些要求？
A. 设置 Amazon Macie 以扫描 EC2 实例是否存在软件漏洞。在每个 EC2 实例上设置⼀个定时任务，定期修
补实例。
B. 在账户中启⽤ Amazon GuardDuty。配置 GuardDuty 以扫描 EC2 实例是否存在软件漏洞。设置 AWS
Systems Manager Session Manager 以定期修补 EC2 实例。
C. 设置 Amazon Detective 以扫描 EC2 实例是否存在软件漏洞。设置 Amazon EventBridge 定时规则，以
定期修补 EC2 实例。
D. 在账户中启⽤ Amazon Inspector。配置 Amazon Inspector 以扫描 EC2 实例是否存在软件漏洞。设置
AWS Systems Manager Patch Manager 以定期修补 EC2 实例。
Question #330
解决⽅案架构师应该如何满⾜这⼀要求？
⼀家公司计划将数据存储在 Amazon RDS 数据库实例上。该公司必须对静态数据进⾏加密。
A. 在 AWS Key Management Service (AWS KMS) 中创建密钥。为数据库实例启⽤加密。
B. 创建加密密钥。将密钥存储在 AWS Secrets Manager 中。使⽤该密钥加密数据库实例。
C. 在 AWS Certificate Manager (ACM) 中⽣成证书。使⽤该证书在数据库实例上启⽤ SSL/TLS。
D. 在 AWS Identity and Access Management (IAM) 中⽣成证书。使⽤该证书在数据库实例上启⽤
SSL/TLS。
Topic 1
https://examlearn.online
[2026/05]
Question #331
Topic 1
⼀家公司必须在 30 天内将 20 TB 的数据从数据中⼼迁移到 AWS 云。该公司的⽹络带宽限制为 15 Mbps，且利
⽤率不能超过 70%。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 使⽤ AWS Snowball。
B. 使⽤ AWS DataSync。
C. 使⽤安全的 VPN 连接。
D. 使⽤亚⻢逊 S3 传输加速。
Question #332
Topic 1
⼀家公司需要为员⼯提供安全访问机密敏感⽂件的途径。该公司希望确保只有授权⽤户才能访问这些⽂件。⽂件
必须安全地下载到员⼯的设备上。
这些⽂件存储在公司内部的 Windows ⽂件服务器上。然⽽，由于远程使⽤量的增加，⽂件服务器的容量即将耗
尽。
哪种
解决⽅案能够满⾜这些要求？
A. 将⽂件服务器迁移到公有⼦⽹中的 Amazon EC2 实例。配置安全组，将⼊站流量限制在员⼯的 IP 地址范
围内。
B. 将⽂件迁移到 Amazon FSx for Windows ⽂件服务器⽂件系统。将 Amazon FSx ⽂件系统与本地 Active
Directory 集成。配置 AWS 客户端 VPN。
C. 将⽂件迁移到 Amazon S3，并创建私有 VPC 终端节点。创建签名 URL 以允许下载。
D. 将⽂件迁移到 Amazon S3，并创建公共 VPC 终端节点。允许员⼯使⽤ AWS IAM Identity Center（AW S
单点登录）登录。
https://examlearn.online
[2026/05]
Question #333
Topic 1
⼀家公司的应⽤程序运⾏在应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2 实例上。这些实例运⾏在跨多个可
⽤区的 Amazon EC2 ⾃动扩展组中。每⽉第⼀天午夜，当运⾏⽉末财务计算批处理时，应⽤程序的运⾏速度会显
著降低。这会导致 EC2 实例的 CPU 利⽤率⽴即飙升⾄ 100%，从⽽导致应⽤程序中断。
解决⽅案架构师应该提出什么建议，以确保应⽤程序能够处理⼯作负载并避免停机？
A. 在 ALB 前⾯配置 Amazon CloudFront 分发。
B. 根据 CPU 利⽤率配置 EC2 ⾃动扩展简单扩展策略。
C. 根据⽉度计划配置 EC2 ⾃动扩展计划扩展策略。
D. 配置 Amazon ElastiCache，以减轻 EC2 实例的部分⼯作负载。
Question #334
Topic 1
⼀家公司希望让客户能够使⽤本地部署的 Microsoft Active Directory 下载存储在 Amazon S3 中的⽂件。客户的
应⽤程序使⽤ SFTP 客户端下载⽂件。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低，并且⽆需对客户的应⽤程序进⾏任何更改？
A. 为 Amazon S3 设置带有 SFTP 的 AWS Transfer Family。配置集成 Active Directory 身份验证。
B. 设置 AWS 数据库迁移服务 (AWS DMS) 以将本地客户端与 Amazon S3 同步。配置集成 Active Directory
身份验证。
C. 使⽤ AWS IAM Identity Center（AW S 单点登录）设置 AWS DataSync，以在本地位置和 S3 位置之间进
⾏同步。
D. 设置⼀个带有 SFTP 的 Windows Amazon EC2 实例，以便将本地客户端连接到 Amazon S3。集成 AWS
Identity and Access Management (IAM)。
https://examlearn.online
[2026/05]
Question #335
Topic 1
⼀家公司正⾯临需求激增的局⾯。该公司需要从 Amazon 系统映像 (AMI) 中配置⼤型 Amazon EC2 实例。这些
实例将在⾃动扩展组中运⾏。该公司需要⼀个能够最⼤限度减少初始化延迟的解决⽅案来满⾜需求。
哪个解决⽅案符合这些要求？
A. 使⽤ aws ec2 register-image 命令从快照创建 AMI。使⽤ AWS Step Functions 将 AMI 替换到⾃动扩展
组中。
B. 在快照上启⽤ Amazon Elastic Block Store (Amazon EBS) 快速快照恢复。使⽤该快照配置 AMI。将 Auto
Scaling 组中的 AMI 替换为新的 AMI。
C. 在 Amazon Data Lifecycle Manager (Amazon DLM) 中启⽤ AMI 创建并定义⽣命周期规则。创建⼀个
AWS Lambda 函数，⽤于修改 Auto Scaling 组中的 AMI。
D. 使⽤ Amazon EventBridge 调⽤ AWS Backup ⽣命周期策略来配置 AMI。将 Auto Scaling 组容量限制配
置为 EventBridge 中的事件源。
Question #336
解决⽅案架构师应该如何做才能以最⼩的运维⼯作量满⾜此要求？
Topic 1
⼀家公司托管了⼀个多层 Web 应⽤程序，该应⽤程序使⽤ Amazon Aurora MySQL 数据库集群进⾏存储。应⽤
程序层托管在 Amazon EC2 实例上。该公司的 IT 安全准则规定，数据库凭证必须加密，并且每 14 天轮换⼀次。
A. 创建⼀个新的 AWS Key Management Service (AWS KMS) 加密密钥。使⽤ AWS Secrets Manager 创建
⼀个使⽤该 KMS 密钥和相应凭证的新密钥。将该密钥与 Aurora 数据库集群关联。配置 14 天的⾃定义轮换周
期。
B. 在 AWS Systems Manager Parameter Store 中创建两个参数：⼀个⽤于存储⽤户名（字符串类型），另⼀
个⽤于存储密码（SecureString 类型）。为密码参数选择 AWS Key Management Service (AWS KMS) 加
密，并将这些参数加载到应⽤层。实现⼀个 AWS Lambda 函数，每 14 天轮换⼀次密码。
C. 将包含凭证的⽂件存储在 AWS Key Management Service (AWS KMS) 加密的 Amazon Elastic File
System (Amazon EFS) ⽂件系统中。将 EFS ⽂件系统挂载到应⽤层的所有 EC2 实例上。限制对⽂件系统上
该⽂件的访问，以便应⽤程序可以读取该⽂件，并且只有超级⽤户可以修改该⽂件。实现⼀个 AWS Lambda
函数，该函数每 14 天在 Aurora 中轮换⼀次密钥，并将新的凭证写⼊该⽂件。
D. 将包含凭证的⽂件存储在 AWS Key Management Service (AWS KMS) 加密的 Amazon S3 存储桶中，应
⽤程序使⽤该存储桶加载凭证。定期将该⽂件下载到应⽤程序，以确保使⽤正确的凭证。实现⼀个 AWS
Lambda 函数，每 14 天轮换⼀次 Aurora 凭证，并将这些凭证上传到 S3 存储桶中的⽂件中。
https://examlearn.online
[2026/05]
Question #337
Topic 1
⼀家公司在 AWS 上部署了⼀个 Web 应⽤程序。该公司将后端数据库托管在 Amazon RDS for MySQL 上，包含
⼀个主数据库实例和五个只读副本，以满⾜扩展需求。只读副本与主数据库实例之间的延迟不得超过 1 秒。数据
库会定期运⾏计划存储过程。
随着⽹站流量的增加，在⾼峰负载期间，副本会出现额外的延迟。解决⽅案架构师必须尽可能减少复制延迟，同
时还要尽量减少对应⽤程序代码的更改，并尽可能降低持续的运维开销。
哪种解决⽅案能够满⾜这些要求？
A. 将数据库迁移到 Amazon Aurora MySQL。将只读副本替换为 Aurora 副本，并配置 Aurora ⾃动扩展。将
存储过程替换为 Aurora MySQL 原⽣函数。
B. 在数据库前端部署 Amazon ElastiCache for Redis 集群。修改应⽤程序，使其在查询数据库之前先检查缓
存。将存储过程替换为 AWS Lambda 函数。
C. 将数据库迁移到运⾏在 Amazon EC2 实例上的 MySQL 数据库。为所有副本节点选择⼤型、计算优化的
EC2 实例。在 EC2 实例上维护存储过程。
D. 将数据库迁移到 Amazon DynamoDB。配置⼤量读取容量单元 (RCU) 以⽀持所需的吞吐量，并配置按需
容量扩展。将存储过程替换为 DynamoDB 流。
Question #338
计划必须将数据复制到辅助 AWS 区域。
Topic 1
解决⽅案架构师需要为⾼容量软件即服务 (SaaS) 平台制定灾难恢复 (DR) 计划。该平台的所有数据都存储在
Amazon Aurora MySQL 数据库集群中。DR
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ MySQL ⼆进制⽇志复制到辅助区域中的 Aurora 集群。为辅助区域中的 Aurora 集群配置⼀个数据库
实例。
B. 为数据库集群设置 Aurora 全局数据库。设置完成后，从辅助区域中移除数据库实例。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据持续复制到辅助区域中的 Aurora 集群。从辅助区域中移除
数据库实例。
D. 为数据库集群设置 Aurora 全局数据库。在辅助区域中⾄少指定⼀个数据库实例。
https://examlearn.online
[2026/05]
Question #339
Topic 1
⼀家公司有⼀个⾃定义应⽤程序，其中包含嵌⼊式凭证，⽤于从 Amazon RDS MySQL 数据库实例中检索信息。
管理层表示，必须以最⼩的编程⼯作量来提⾼该应⽤程序的安全性。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 使⽤ AWS Key Management Service (AWS KMS) 创建密钥。配置应⽤程序以从 AWS KMS 加载数据库凭
证。启⽤⾃动密钥轮换。
B. 为应⽤程序⽤户在 RDS for MySQL 数据库上创建凭证，并将凭证存储在 AWS Secrets Manager 中。配置
应⽤程序以从 Secrets Manager 加载数据库凭证。创建⼀个 AWS Lambda 函数，⽤于轮换 Secrets
Manager 中的凭证。
C. 为应⽤程序⽤户在 RDS for MySQL 数据库上创建凭证，并将凭证存储在 AWS Secrets Manager 中。配
置应⽤程序以从 Secrets Manager 加载数据库凭证。使⽤ Secrets Manager 为 RDS for MySQL 数据库中的
应⽤程序⽤户设置凭证轮换计划。
D. 为应⽤程序⽤户在 RDS for MySQL 数据库上创建凭证，并将凭证存储在 AWS Systems Manager
for MySQL 数据库中的应⽤程序⽤户设置凭证轮换计划。
Question #340
该公司应该如何解决这个问题？
Parameter Store 中。配置应⽤程序以从 Parameter Store 加载数据库凭证。使⽤ Parameter Store 为 RDS
Topic 1
⼀家媒体公司将其⽹站托管在 AWS 上。该⽹站应⽤程序的架构包括⼀组位于应⽤程序负载均衡器 (ALB) 后⾯的
Amazon EC2 实例，以及⼀个托管在 Amazon Aurora 上的数据库。该公司⽹络安全团队报告称，该应⽤程序存
在 SQL 注⼊漏洞。
A. 在 ALB 前⾯使⽤ AWS WAF。将相应的 Web ACL 与 AWS WAF 关联。
B. 创建⼀个 ALB 监听器规则，以固定响应回复 SQL 注⼊。
C. 订阅 AWS Shield Advanced 以⾃动阻⽌所有 SQL 注⼊尝试。
D. 设置 Amazon Inspector 以⾃动阻⽌所有 SQL 注⼊尝试。
https://examlearn.online
[2026/05]
Question #341
Topic 1
⼀家公司拥有⼀个由 AWS Lake Formation 管理的 Amazon S3 数据湖。该公司希望通过将数据湖中的数据与存
储在 Amazon Aurora MySQL 数据库中的运营数据连接起来，在 Amazon QuickSight 中创建可视化图表。该公
司希望强制执⾏列级授权，以便其市场营销团队只能访问数据库中的部分列。
哪种解决⽅案能够以最⼩的运营开销满⾜这些要求？
A. 使⽤ Amazon EMR 将数据直接从数据库导⼊ QuickSight SPICE 引擎。仅包含必需的列。
B. 使⽤ AWS Glue Studio 将数据从数据库导⼊到 S3 数据湖。为 QuickSight ⽤户附加 IAM 策略，以强制执
⾏列级访问控制。在 QuickSight 中使⽤ Amazon S3 作为数据源。
C. 使⽤ AWS Glue Elastic Views 为 Amazon S3 中的数据库创建物化视图。创建 S3 存储桶策略，以强制
QuickSight ⽤户进⾏列级访问控制。在 QuickSight 中使⽤ Amazon S3 作为数据源。
D. 使⽤ Lake Formation 蓝图将数据从数据库导⼊到 S3 数据湖。使⽤ Lake Formation 为 QuickSight ⽤户
强制执⾏列级访问控制。在 QuickSight 中使⽤ Amazon Athena 作为数据源。
Question #342
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
为 60%。
Topic 1
⼀家交易处理公司每周都会在 Amazon EC2 实例上运⾏脚本化的批处理作业。这些 EC2 实例位于⼀个⾃动扩展
组中。事务数量可能有所不同，但每次运⾏的基准 CPU 利⽤率⾄少为 60%。该公司需要在作业运⾏前 30 分钟
预置容量。
⽬前，⼯程师通过⼿动修改⾃动扩展组的参数来完成这项任务。该公司没有⾜够的资源来分析⾃动扩展组实例数
量的所需容量趋势。因此，该公司需要⼀种⾃动化的⽅法来修改⾃动扩展组的所需容量。
A. 为⾃动扩展组创建动态扩展策略。将该策略配置为基于 CPU 利⽤率指标进⾏扩展。将该指标的⽬标值设置
B. 为⾃动扩展组创建计划扩展策略。设置合适的期望容量、最⼩容量和最⼤容量。将重复周期设置为每周。
将启动时间设置为批处理作业运⾏前 30 分钟。
C. 为⾃动扩展组创建预测性扩展策略。配置该策略以根据预测进⾏扩展。将扩展指标设置为 CPU 利⽤率。将
该指标的⽬标值设置为 60%。在策略中，将实例设置为在作业运⾏前 30 分钟预启动。
D. 创建⼀个 Amazon EventBridge 事件，当 Auto Scaling 组的 CPU 利⽤率指标值达到 60% 时，调⽤ AWS
Lambda 函数。配置 Lambda 函数，将 Auto Scaling 组的期望容量和最⼤容量增加 20%。
https://examlearn.online
[2026/05]
Question #343
Topic 1
⼀位解决⽅案架构师正在为⼀家公司设计灾难恢复 (DR) 架构。该公司有⼀个 MySQL 数据库，运⾏在私有⼦⽹的
Amazon EC2 实例上，并设有定时备份。灾难恢复设计需要涵盖多个 AWS 区域。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将 MySQL 数据库迁移到多个 EC2 实例。在灾备区域配置⼀个备⽤ EC2 实例。启⽤复制功能。
B. 将 MySQL 数据库迁移到 Amazon RDS。使⽤多可⽤区部署。为不同可⽤区中的主数据库实例启⽤读取复
制。
C. 将 MySQL 数据库迁移到 Amazon Aurora 全局数据库。将主数据库集群托管在主区域中。将辅助数据库集
群托管在灾备区域中。
D. 将 MySQL 数据库的计划备份存储在已配置为 S3 跨区域复制 (CRR) 的 Amazon S3 存储桶中。使⽤该数
据备份在灾备区域中恢复数据库。
Question #344
哪种解决⽅案能够以最少的代码更改满⾜这些要求？
Topic 1
⼀家公司有⼀个使⽤ Amazon Simple Queue Service (Amazon SQS) 解析消息的 Java 应⽤程序。该应⽤程序
⽆法解析⼤于 256 KB 的消息。该公司希望实现⼀个解决⽅案，使应⽤程序能够解析最⼤ 50 MB 的消息。
A. 使⽤ Amazon SQS Extended Client Library for Java 在 Amazon S3 中托管⼤于 256 KB 的消息。
B. 使⽤ Amazon EventBridge 从应⽤程序发布⼤型消息，⽽不是使⽤ Amazon SQS。
C. 更改 Amazon SQS 中的限制，以处理⼤于 256 KB 的消息。
D. 将⼤于 256 KB 的消息存储在 Amazon Elastic File System (Amazon EFS) 中。配置 Amazon SQS 在消
息中引⽤此位置。
https://examlearn.online
[2026/05]
Question #345
Topic 1
⼀家公司希望限制对其主要 Web 应⽤程序内容的访问，并利⽤ AWS 提供的授权技术保护内容安全。该公司希望
为不到 100 位⽤户实施⽆服务器架构和身份验证解决⽅案。该解决⽅案需要与主要 Web 应⽤程序集成，并在全
球范围内提供 Web 内容。此外，该解决⽅案还必须能够随着公司⽤户群的增⻓⽽扩展，同时尽可能降低登录延
迟。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ Amazon Cognito 进⾏身份验证。使⽤ Lambda@Edge 进⾏授权。使⽤ Amazon CloudFront 在全球
范围内部署 Web 应⽤程序。
B. 使⽤ AWS Directory Service for Microsoft Active Directory 进⾏身份验证。使⽤ AWS Lambda 进⾏授
权。使⽤应⽤程序负载均衡器在全球范围内部署 Web 应⽤程序。
C. 使⽤ Amazon Cognito 进⾏身份验证。使⽤ AWS Lambda 进⾏授权。使⽤ Amazon S3 Transfer
Acceleration 在全球范围内部署 Web 应⽤程序。
D. 使⽤ AWS Directory Service for Microsoft Active Directory 进⾏身份验证。使⽤ Lambda@Edge 进⾏
授权。使⽤ AWS Elastic Beanstalk 在全球范围内部署 Web 应⽤程序。
Question #346
A. 卷⽹关
B. 磁带⽹关
Topic 1
⼀家公司的数据中⼼⾥有⼀套⽼旧的⽹络附加存储 (NAS) 阵列。该 NAS 阵列向客户端⼯作站提供 SMB 共享和
NFS 共享。该公司不想购买新的 NAS 阵列，也不想承担续订现有 NAS 阵列⽀持合同的费⽤。部分数据访问频
繁，但⼤部分数据处于⾮活动状态。
解决⽅案架构师需要实施⼀个⽅案，将数据迁移到 Amazon S3，使⽤ S3 ⽣命周期策略，并保持客户端⼯作站的
界⾯⻛格⼀致。该解决⽅案架构师已确定 AWS Storage Gateway 作为解决⽅案的⼀部分。
为了满⾜这些要求，解决⽅案架构师应该配置哪种类型的存储⽹关？
C. Amazon FSx ⽂件⽹关
D. Amazon S3 ⽂件⽹关
https://examlearn.online
[2026/05]
Question #347
Topic 1
⼀家公司有⼀个运⾏在 Amazon EC2 实例上的应⽤程序。解决⽅案架构师根据公司当前的需求，将公司标准化为
特定的实例系列和各种实例⼤⼩。
公司希望在未来三年内最⼤限度地节省该应⽤程序的成本。公司需要在未来六个⽉内根据应⽤程序的受欢迎程度
和使⽤情况更改实例系列和⼤⼩。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 计算储蓄计划
B. EC2实例节省计划
C. 区域保留实例
D. 标准保留实例
Question #348
Topic 1
⼀家公司收集⼤量使⽤可穿戴设备的参与者的数据。该公司将数据存储在 Amazon DynamoDB 表中，并使⽤应
⽤程序进⾏数据分析。数据⼯作负载稳定且可预测。该公司希望将 DynamoDB 的使⽤成本控制在或低于其预测
预算。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤预置模式和 DynamoDB 标准版-不频繁访问 (DynamoDB Standard-IA)。为预测的⼯作负载预留容
量。
B. 使⽤配置模式。指定读取容量单位 (RCU) 和写⼊容量单位 (WCU)。
C. 使⽤按需模式。将读取容量单位 (RCU) 和写⼊容量单位 (WCU) 设置得⾜够⾼，以适应⼯作负载的变化。
D. 使⽤按需模式。指定读取容量单元 (RCU) 和写⼊容量单元 (WCU)，并预留容量。
https://examlearn.online
[2026/05]
Question #349
Topic 1
⼀家公司将机密数据存储在位于 ap-southeast-3 区域的 Amazon Aurora PostgreSQL 数据库中。该数据库使⽤
客户管理的 AWS 密钥管理服务 (AWS KMS) 密钥进⾏加密。该公司最近被收购，必须安全地与收购公司位于 ap
southeast-3 区域的 AWS 账户共享数据库备份。
解决⽅案架构师应该如何满⾜这些要求？
A. 创建数据库快照。将快照复制到⼀个新的未加密快照。将新快照共享给收购公司的 AWS 账户。
B. 创建数据库快照。将收购公司的 AWS 账户添加到 KMS 密钥策略中。将快照共享给收购公司的 AWS 账
户。
C. 创建⼀个使⽤不同 AWS 托管 KMS 密钥的数据库快照。将收购公司的 AWS 账户添加到 KMS 密钥别名
中。将该快照共享给收购公司的 AWS 账户。
D. 创建数据库快照。下载数据库快照。将数据库快照上传到 Amazon S3 存储桶。更新 S3 存储桶策略，允许
收购公司的 AWS 账户访问。
Question #350
以下哪两项措施可以满⾜这些要求？
Topic 1
⼀家公司使⽤位于美国东部 1 区域的 100 GB Amazon RDS for Microsoft SQL Server 单可⽤区数据库实例来存
储客户交易信息。该公司需要该数据库实例具备⾼可⽤性和⾃动恢复功能。
此外，该公司每年还需对 RDS 数据库运⾏数次报表。报表处理过程会导致交易记⼊客户账户的时间⽐平时更⻓。
该公司需要⼀个能够提升报表处理性能的解决⽅案。
A. 将数据库实例从单可⽤区数据库实例修改为多可⽤区部署。
B. 对当前数据库实例进⾏快照。将快照还原到另⼀个可⽤区中的新 RDS 部署。
C. 在不同的可⽤区中创建数据库实例的只读副本。将所有报表请求指向该只读副本。
D. 将数据库迁移到 RDS Custom。
E. 使⽤ RDS 代理将报告请求限制在维护窗⼝期间。
https://examlearn.online
[2026/05]
Question #351
Topic 1
⼀家公司正在将其数据管理应⽤程序迁移到 AWS。该公司希望转型为事件驱动架构。该架构需要更加分布式，并
在执⾏⼯作流的不同环节时采⽤⽆服务器理念。此外，该公司还希望最⼤限度地降低运维开销。
哪种解决⽅案能够满⾜这些要求？
A. 在 AWS Glue 中构建⼯作流。使⽤ AWS Glue 调⽤ AWS Lambda 函数来处理⼯作流步骤。
B. 在 AWS Step Functions 中构建⼯作流。将应⽤程序部署到 Amazon EC2 实例上。使⽤ Step Functions
在 EC2 实例上调⽤⼯作流步骤。
C. 在 Amazon EventBridge 中构建⼯作流。使⽤ EventBridge 按计划调⽤ AWS Lambda 函数来处理⼯作流
步骤。
D. 在 AWS Step Functions 中构建⼯作流。使⽤ Step Functions 创建状态机。使⽤该状态机调⽤ AWS
Lambda 函数来处理⼯作流步骤。
Question #352
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在为⼀款在线多⼈游戏设计⽹络。该游戏使⽤UDP⽹络协议，并将部署在⼋个AWS区域中。⽹络架构
需要最⼤限度地减少延迟和丢包，以向最终⽤户提供⾼质量的游戏体验。
A. 在每个区域设置⼀个传输⽹关。在每个传输⽹关之间创建跨区域对等连接。
B. 在每个区域中设置 AWS Global Accelerator，包括 UDP 监听器和终端节点组。
C. 设置启⽤ UDP 的 Amazon CloudFront。在每个区域中配置⼀个源。
D. 在每个区域之间建⽴ VPC 对等互连⽹络。为每个 VPC 启⽤ UDP。
https://examlearn.online
[2026/05]
Question #353
Topic 1
⼀家公司在单个可⽤区内的 Amazon EC2 实例上托管了⼀个三层 Web 应⽤程序。该 Web 应⽤程序使⽤托管在
EC2 实例上的⾃管理 MySQL 数据库，并将数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷中。
MySQL 数据库⽬前使⽤ 1 TB 的预置 IOPS SSD (io2) EBS 卷。该公司预计在流量⾼峰期，读写 IOPS 均为
1,000。
该公司希望在保持两倍 IOPS 容量的同时，最⼤限度地减少中断、稳定性能并降低成本。该公司希望将数据库层
迁移到完全托管、⾼可⽤且容错的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ Amazon RDS for MySQL 数据库实例的多可⽤区部署，并配备 io2 Block Express EBS 卷。
B. 使⽤ Amazon RDS for MySQL 数据库实例的多可⽤区部署，并配备通⽤ SSD (gp2) EBS 卷。
C. 使⽤ Amazon S3 智能分层访问层。
D. 使⽤两个⼤型 EC2 实例以主备模式托管数据库。
Question #354
解决⽅案架构师应该如何满⾜这些要求？
A. 降低 Lambda 并发率。
Topic 1
⼀家公司在 AWS 上托管了⼀个⽆服务器应⽤程序。该应⽤程序使⽤ Amazon API Gateway、AWS Lambda 和
Amazon RDS for PostgreSQL 数据库。该公司注意到，在流量⾼峰期或流量不可预测时，由于数据库连接超时
导致的应⽤程序错误有所增加。该公司需要⼀个解决⽅案，能够在尽可能减少代码更改的情况下降低应⽤程序故
障率。
B. 在 RDS 数据库实例上启⽤ RDS 代理。
C. 调整 RDS 数据库实例类的⼤⼩以接受更多连接。
D. 将数据库迁移到 Amazon DynamoDB，并⽀持按需扩展。
https://examlearn.online
[2026/05]
Question #355
Topic 1
⼀家公司正在将⼀个旧应⽤程序迁移到 AWS。该应⽤程序每⼩时运⾏⼀次批处理作业，并且 CPU 占⽤率很⾼。
在本地服务器上，该批处理作业平均需要 15 分钟才能完成。该服务器有 64 个虚拟 CPU (vCPU) 和 512 GiB 内
存。
哪种解决⽅案能够在 15 分钟内运⾏该批处理作业，且运维开销最⼩？
A. 使⽤ AWS Lambda 进⾏函数式扩展。
B. 将 Amazon Elastic Container Service (Amazon ECS) 与 AWS Fargate 结合使⽤。
C. 将 Amazon Lightsail 与 AWS ⾃动扩展结合使⽤。
D. 在 Amazon EC2 上使⽤ AWS Batch。
Question #356
哪种存储解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司将其数据对象存储在 Amazon S3 标准存储中。解决⽅案架构师发现，30 天后，75% 的数据很少被访
问。该公司需要所有数据保持即时访问，并具备同样的⾼可⽤性和弹性，但同时希望最⼤限度地降低存储成本。
A. 30 天后将数据对象移⾄ S3 Glacier Deep Archive。
B. 30 天后将数据对象移⾄ S3 标准-不频繁访问 (S3 标准-IA)。
C. 30 天后将数据对象移⾄ S3 单区-不频繁访问 (S3 单区-IA)。
D. ⽴即将数据对象移⾄ S3 单区-不频繁访问 (S3 单区-IA)。
https://examlearn.online
[2026/05]
Question #357
Topic 1
⼀家游戏公司正将其公共记分牌从数据中⼼迁移到 AWS 云。该公司使⽤位于应⽤程序负载均衡器后⾯的
Amazon EC2 Windows Server 实例来托管其动态应⽤程序。该公司需要⼀个⾼可⽤性的存储解决⽅案来⽀持该
应⽤程序。该应⽤程序包含静态⽂件和动态服务器端代码。
解决⽅案架构师应采取哪些步骤组合来满⾜这些要求？（选择两项。）
A. 将静态⽂件存储在 Amazon S3 上。使⽤ Amazon CloudFront 在边缘缓存对象。
B. 将静态⽂件存储在 Amazon S3 上。使⽤ Amazon ElastiCache 在边缘缓存对象。
C. 将服务器端代码存储在 Amazon Elastic File System (Amazon EFS) 上。在每个 EC2 实例上挂载 EFS 卷
以共享⽂件。
D. 将服务器端代码存储在 Amazon FSx for Windows ⽂件服务器上。在每个 EC2 实例上挂载 FSx for
Windows ⽂件服务器卷以共享⽂件。
E. 将服务器端代码存储在通⽤型固态硬盘 (gp2) Amazon Elastic Block Store (Amazon EBS) 卷上。将 EBS
卷挂载到每个 EC2 实例上以共享⽂件。
Question #358
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家社交媒体公司将其应⽤程序运⾏在 Amazon EC2 实例上，并部署在应⽤程序负载均衡器 (ALB) 之后。该
ALB 是 Amazon CloudFront 分发的源站。该应⽤程序在 Amazon S3 存储桶中存储了超过 10 亿张图⽚，每秒处
理数千张图⽚。该公司希望动态调整图⽚⼤⼩，并向客户提供合适的格式。
A. 在 EC2 实例上安装外部镜像管理库。使⽤该镜像管理库处理镜像。
B. 创建 CloudFront 源请求策略。使⽤该策略根据请求中的 User-Agent HTTP 标头⾃动调整图像⼤⼩并提供
适当的格式。
C. 使⽤带有外部镜像管理库的 Lambda@Edge 函数。将 Lambda@Edge 函数与提供镜像服务的 CloudFront
⾏为关联起来。
D. 创建 CloudFront 响应头策略。使⽤该策略根据请求中的 User-Agent HTTP 标头⾃动调整图像⼤⼩并提供
适当的格式。
https://examlearn.online
[2026/05]
Question #359
Topic 1
医院需要将患者记录存储在 Amazon S3 存储桶中。医院的合规团队必须确保所有受保护的健康信息 (PHI) 在传
输和存储过程中均经过加密。合规团队还必须管理静态数据的加密密钥。
哪种解决⽅案能够满⾜这些要求？
A. 在 AWS Certificate Manager (ACM) 中创建公共 SSL/TLS 证书。将该证书与 Amazon S3 关联。为每个
S3 存储桶配置默认加密，使⽤基于 AWS KMS 密钥的服务器端加密 (SSE-KMS)。指派合规团队管理 KMS 密
钥。
B. 在 S3 存储桶策略中使⽤ aws:SecureTransport 条件，仅允许通过 HTTPS (TLS) 建⽴加密连接。为每个
S3 存储桶配置默认加密，使⽤服务器端加密和 S3 管理的加密密钥 (SSE-S3)。指定合规团队管理 SSE-S3
密钥。
C. 在 S3 存储桶策略中使⽤ aws:SecureTransport 条件，仅允许通过 HTTPS (TLS) 建⽴加密连接。为每个
S3 存储桶配置默认加密，使⽤基于 AWS KMS 密钥的服务器端加密 (SSE-KMS)。指定合规团队负责管理
KMS 密钥。
D. 在 S3 存储桶策略中使⽤ aws:SecureTransport 条件，仅允许通过 HTTPS (TLS) 建⽴加密连接。使⽤
Amazon Macie 保护存储在 Amazon S3 中的敏感数据。指派合规团队管理 Macie。
Question #360
Topic 1
⼀家公司使⽤ Amazon API Gateway 在同⼀个 VPC 中运⾏⼀个私有⽹关，该⽹关包含两个 REST API。
BuyStock RESTful Web 服务会调⽤ CheckFunds RESTful Web 服务，以确保在购买股票之前有⾜够的资⾦可
⽤。该公司在 VPC 流⽇志中发现，BuyStock RESTful Web 服务是通过互联⽹⽽不是通过 VPC 调⽤
CheckFunds RESTful Web 服务。解决⽅案架构师必须实现⼀个解决⽅案，使这两个 API 能够通过 VPC 进⾏通
信。
哪个解决⽅案能够以最少的代码更改满⾜这些要求？
A. 在 HTTP 标头中添加 X-API-Key 标头以进⾏授权。
B. 使⽤接⼝端点。
C. 使⽤⽹关端点。
D. 在两个 REST API 之间添加 Amazon Simple Queue Service (Amazon SQS) 队列。
https://examlearn.online
[2026/05]
Question #361
Topic 1
⼀家公司在 AWS 上托管了⼀个多⼈游戏应⽤程序。该公司希望该应⽤程序能够以亚毫秒级的延迟读取数据，并
对历史数据执⾏⼀次性查询。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 对于频繁访问的数据，请使⽤ Amazon RDS。定期运⾏⾃定义脚本将数据导出到 Amazon S3 存储桶。
B. 将数据直接存储在 Amazon S3 存储桶中。实施 S3 ⽣命周期策略，将较旧的数据迁移到 S3 Glacier Deep
Archive 进⾏⻓期存储。使⽤ Amazon Athena 对 Amazon S3 中的数据执⾏⼀次性查询。
C. 对于频繁访问的数据，请使⽤配备 DynamoDB Accelerator (DAX) 的 Amazon DynamoDB。使⽤
DynamoDB 表导出功能将数据导出到 Amazon S3 存储桶。使⽤ Amazon Athena 对 Amazon S3 中的数据
执⾏⼀次性查询。
D. 对于频繁访问的数据，请使⽤ Amazon DynamoDB。启⽤ Amazon Kinesis Data Streams 的流式传输功
Question #362
能。使⽤ Amazon Kinesis Data Firehose 从 Kinesis Data Streams 读取数据。将记录存储在 Amazon S3 存
储桶中。
Topic 1
⼀家公司使⽤的⽀付处理系统要求特定⽀付 ID 的消息必须按照发送顺序接收。否则，⽀付处理可能会出错。
解决⽅案架构师应采取哪些措施来满⾜此要求？（选择两项。）
A. 将消息写⼊ Amazon DynamoDB 表，并将付款 ID 作为分区键。
B. 将消息写⼊ Amazon Kinesis 数据流，并将⽀付 ID 作为分区键。
C. 将消息写⼊ Amazon ElastiCache for Memcached 集群，并将⽀付 ID 作为键。
D. 将消息写⼊ Amazon Simple Queue Service (Amazon SQS) 队列。设置消息属性以使⽤付款 ID。
E. 将消息写⼊ Amazon Simple Queue Service (Amazon SQS) FIFO 队列。设置消息组以使⽤付款 ID。
https://examlearn.online
[2026/05]
Question #363
Topic 1
⼀家公司正在构建⼀个游戏系统，该系统需要同时向不同的排⾏榜、匹配和身份验证服务发送独特的事件。该公
司需要⼀个基于 AWS 的事件驱动系统来保证事件的顺序。
哪种解决⽅案能够满⾜这些要求？
A. Amazon EventBridge 事件总线
B. Amazon Simple Notification Service (Amazon SNS) 先进先出 (FIFO) 主题
C. Amazon Simple Notification Service (Amazon SNS) 标准主题
D. Amazon Simple Queue Service (Amazon SQS) 先进先出 (FIFO) 队列
Question #364
⼀家医院正在设计⼀款⽤于收集患者症状的新应⽤程序。医院决定在架构中使⽤ Amazon Simple Queue Service
(Amazon SQS) 和 Amazon Simple Notification Service (Amazon SNS)。
解决⽅案架构师应该采取哪些步骤组合来满⾜这些要求？（选择两项。）
Topic 1
⼀位解决⽅案架构师正在审查基础架构设计。数据必须在静态存储和传输过程中加密。只有医院的授权⼈员才能
访问数据。
A. 在 SQS 组件上启⽤服务器端加密。更新默认密钥策略，将密钥使⽤限制在⼀组授权主体内。
B. 使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥，在 SNS 组件上启⽤服务器端加密。
应⽤密钥策略，将密钥的使⽤限制在⼀组授权主体内。
C. 启⽤ SNS 组件的加密功能。更新默认密钥策略，将密钥使⽤限制在⼀组授权主体内。在主题策略中设置条
件，仅允许通过 TLS 建⽴加密连接。
D. 使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥，在 SQS 组件上启⽤服务器端加密。
应⽤密钥策略，将密钥的使⽤限制在⼀组授权主体内。在队列策略中设置条件，仅允许通过 TLS 建⽴加密连
接。
E. 使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥，在 SQS 组件上启⽤服务器端加密。
应⽤ IAM 策略，将密钥的使⽤限制在⼀组授权主体内。在队列策略中设置条件，仅允许通过 TLS 建⽴加密连
接。
https://examlearn.online
[2026/05]
Question #365
Topic 1
⼀家公司运⾏着⼀个由 Amazon RDS 提供⽀持的 Web 应⽤程序。⼀位新来的数据库管理员不⼩⼼编辑了数据库
表中的信息，导致数据丢失。为了帮助公司从这类事件中恢复，他们希望能够将数据库恢复到过去 30 天内任何
更改发⽣前 5 分钟的状态。
解决⽅案架构师应该在设计中包含哪个功能才能满⾜此要求？
A. 读取副本
B. ⼿动快照
C. ⾃动备份
D. 多可⽤区部署
Question #366
哪种解决⽅案能够以最⼩的运维开销满⾜此要求？
Topic 1
⼀家公司的 Web 应⽤程序由位于 AWS Lambda 函数前端的 Amazon API Gateway API 和 Amazon DynamoDB
数据库组成。Lambda 函数处理业务逻辑，DynamoDB 表存储数据。该应⽤程序使⽤ Amazon Cognito ⽤户池
来识别各个⽤户。解决⽅案架构师需要更新该应⽤程序，以便只有订阅⽤户才能访问⾼级内容。
A. 在 API ⽹关 API 上启⽤ API 缓存和限流。
B. 在 API Gateway API 上设置 AWS WAF。创建⼀条规则来筛选已订阅的⽤户。
C. 对 DynamoDB 表中的⾼级内容应⽤细粒度的 IAM 权限。
D. 实施 API 使⽤计划和 API 密钥，以限制未订阅⽤户的访问权限。
https://examlearn.online
[2026/05]
Question #367
Topic 1
⼀家公司使⽤ Amazon Route 53 的基于延迟的路由功能，将请求路由到其⾯向全球⽤户的基于 UDP 的应⽤程
序。该应⽤程序托管在公司位于美国、亚洲和欧洲的本地数据中⼼的冗余服务器上。公司的合规性要求规定，该
应⽤程序必须托管在公司内部。公司希望提⾼应⽤程序的性能和可⽤性。
解决⽅案架构师应该如何做才能满⾜这些要求？
A. 在三个 AWS 区域中配置三个⽹络负载均衡器 (NLB)，以服务于本地终端节点。使⽤ AWS Global
Accelerator 创建⼀个加速器，并将 NLB 注册为其终端节点。通过指向加速器 DNS 的 CNAME 记录为应⽤程
序提供访问权限。
B. 在三个 AWS 区域中配置三个应⽤程序负载均衡器 (ALB)，以服务于本地终端节点。使⽤ AWS Global
Accelerator 创建⼀个加速器，并将 ALB 注册为其终端节点。通过指向加速器 DNS 的 CNAME 记录为应⽤程
序提供访问权限。
C. 在三个 AWS 区域中配置三个⽹络负载均衡器 (NLB)，以服务于本地终端节点。在 Route 53 中，创建⼀个
指向这三个 NLB 的基于延迟的记录，并将其⽤作 Amazon CloudFront 分发的源。使⽤指向 CloudFront
DNS 的 CNAME 记录为应⽤程序提供访问权限。
Question #368
D. 在三个 AWS 区域中配置三个应⽤程序负载均衡器 (ALB)，以服务于本地终端节点。在 Route 53 中，创建
⼀个指向这三个 ALB 的基于延迟的记录，并将其⽤作 Amazon CloudFront 分发的源。使⽤指向 CloudFront
DNS 的 CNAME 记录来提供对应⽤程序的访问。
Topic 1
解决⽅案架构师希望所有新⽤户都满⾜特定的复杂度要求，并强制要求其身份和访问管理 (IAM) ⽤户密码轮换周
期。
为了实现这⼀⽬标，解决⽅案架构师应该怎么做？
A. 为整个 AWS 账户设置⼀个总体密码策略。
B. 为 AWS 账户中的每个 IAM ⽤户设置密码策略。
C. 使⽤第三⽅供应商软件设置密码要求。
D. 将 Amazon CloudWatch 规则附加到 Create_newuser 事件，以按照适当的要求设置密码。
https://examlearn.online
[2026/05]
Question #369
Topic 1
⼀家公司已将应⽤程序迁移到 Amazon EC2 Linux 实例。其中⼀个 EC2 实例按计划运⾏多个 1 ⼩时的任务。这
些任务由不同的团队编写，且使⽤不同的编程语⾔。该公司担⼼这些任务在单个实例上运⾏时的性能和可扩展性
问题。解决⽅案架构师需要实施⼀个解决⽅案来解决这些问题。
哪个解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 使⽤ AWS Batch 将任务作为作业运⾏。使⽤ Amazon EventBridge（Amazon CloudWatch Events）调
度作业。
B. 将 EC2 实例转换为容器。使⽤ AWS App Runner 按需创建容器，以作业形式运⾏任务。
C. 将任务复制到 AWS Lambda 函数中。使⽤ Amazon EventBridge（Amazon CloudWatch Events）调度
Lambda 函数。
D. 创建运⾏任务的 EC2 实例的 Amazon 系统映像 (AMI)。使⽤该 AMI 创建⾃动扩展组，以运⾏该实例的多
个副本。
Question #370
哪种解决⽅案满⾜这些要求？
Topic 1
⼀家公司在虚拟专⽤⽹络 (VPC) 中运⾏⼀个公共的三层 Web 应⽤程序。该应⽤程序运⾏在跨多个可⽤区的
Amazon EC2 实例上。运⾏在私有⼦⽹中的 EC2 实例需要通过互联⽹与许可证服务器通信。该公司需要⼀个能
够最⼤限度减少运维⼯作的托管解决⽅案。
A. 在公共⼦⽹中配置⼀个 NAT 实例。修改每个私有⼦⽹的路由表，添加⼀条指向该 NAT 实例的默认路由。
B. 在私有⼦⽹中配置 NAT 实例。修改每个私有⼦⽹的路由表，添加⼀条指向 NAT 实例的默认路由。
C. 在公共⼦⽹中配置 NAT ⽹关。修改每个私有⼦⽹的路由表，添加⼀条指向 NAT ⽹关的默认路由。
D. 在私有⼦⽹中配置 NAT ⽹关。修改每个私有⼦⽹的路由表，添加⼀条指向 NAT ⽹关的默认路由。
https://examlearn.online
[2026/05]
Question #371
Topic 1
⼀家公司需要创建⼀个 Amazon Elastic Kubernetes Service (Amazon EKS) 集群来托管⼀个数字媒体流应⽤程
序。该 EKS 集群将使⽤由 Amazon Elastic Block Store (Amazon EBS) 卷⽀持的托管节点组进⾏存储。该公司
必须使⽤存储在 AWS Key Management Service (AWS KMS) 中的客户管理密钥对所有静态数据进⾏加密。
以下哪两项操作组合能够以最⼩的运维开销满⾜此要求？
A. 使⽤ Kubernetes 插件，利⽤客户管理的密钥执⾏数据加密。
B. 创建 EKS 集群后，找到 EBS 卷。使⽤客户管理的密钥启⽤加密。
C. 在将要创建 EKS 集群的 AWS 区域中默认启⽤ EBS 加密。选择客户管理的密钥作为默认密钥。
D. 创建 EKS 集群。创建⼀个 IAM ⻆⾊，该⻆⾊具有授予客户管理密钥权限的策略。将该⻆⾊与 EKS 集群关
联。
E. 将客户管理的密钥作为 Kubernetes Secret 存储在 EKS 集群中。使⽤客户管理的密钥对 EBS 卷进⾏加
密。
Question #372
Topic 1
⼀家公司希望将 Oracle 数据库迁移到 AWS。该数据库包含⼀个单表，其中包含数百万张⾼分辨率地理信息系统
(GIS) 图像，这些图像均由地理代码标识。
当发⽣⾃然灾害时，数万张图像每隔⼏分钟就会更新⼀次。每个地理代码都关联着⼀张图像或⼀⾏数据。该公司
希望找到⼀种在灾害发⽣期间能够保持⾼可⽤性和可扩展性的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将图像和地理编码存储在数据库表中。使⽤运⾏在 Amazon RDS 多可⽤区数据库实例上的 Oracle 数据
库。
B. 将图像存储在 Amazon S3 存储桶中。使⽤ Amazon DynamoDB，以地理代码为键，图像 S3 URL 为值。
C. 将图像和地理代码存储在 Amazon DynamoDB 表中。在⾼负载期间配置 DynamoDB 加速器 (DAX)。
D. 将图像存储在 Amazon S3 存储桶中。将地理编码和图像 S3 URL 存储在数据库表中。使⽤运⾏在
Amazon RDS 多可⽤区数据库实例上的 Oracle 数据库。
https://examlearn.online
[2026/05]
Question #373
Topic 1
⼀家公司开发了⼀款应⽤程序，⽤于收集汽⻋物联⽹传感器的数据。这些数据通过 Amazon Kinesis Data
Firehose 流式传输并存储在 Amazon S3 中。每年，该应⽤程序会产⽣数万亿个 S3 对象。每天早上，该公司使
⽤过去 30 天的数据重新训练⼀套机器学习 (ML) 模型。
每年四次，该公司使⽤过去 12 个⽉的数据进⾏分析并训练其他 ML 模型。数据必须以最⼩延迟可⽤⻓达⼀年。⼀
年后，数据必须保留⽤于归档。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ S3 智能分层存储类。创建 S3 ⽣命周期策略，将对象在 1 年后迁移到 S3 Glacier 深度归档。
B. 使⽤ S3 智能分层存储类。配置 S3 智能分层，使其在 1 年后⾃动将对象移动到 S3 Glacier 深度归档。
C. 使⽤ S3 标准-不频繁访问 (S3 Standard-IA) 存储类。创建 S3 ⽣命周期策略，将对象在 1 年后迁移到 S3
Glacier 深度归档。
D. 使⽤ S3 标准存储类。创建 S3 ⽣命周期策略，将对象在 30 天后转换为 S3 标准-不频繁访问 (S3
Standard-IA)，然后在 1 年后转换为 S3 Glacier 深度归档。
Question #374
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在美国东部1区（us-east-1）的三个独⽴虚拟私有云（VPC）中运⾏多个业务应⽤程序。这些应⽤程序
必须能够在不同VPC之间通信。此外，这些应⽤程序还必须能够每天持续地向运⾏在单个本地数据中⼼的对延迟
敏感的应⽤程序发送数百GB的数据。
解决⽅案架构师需要设计⼀个能够最⼤限度提⾼成本效益的⽹络连接解决⽅ 案。
A. 配置从数据中⼼到 AWS 的三条 AWS 站点到站点 VPN 连接。为每个 VPC 配置⼀条 VPN 连接以建⽴连
接。
B. 在每个 VPC 中启动第三⽅虚拟⽹络设备。在数据中⼼和每个虚拟设备之间建⽴ IPsec VPN 隧道。
C. 从数据中⼼到 us-east-1 的 Direct Connect ⽹关建⽴三个 AWS Direct Connect 连接。通过配置每个
VPC 使⽤其中⼀个 Direct Connect 连接来建⽴连接。
D. 从数据中⼼到 AWS 设置⼀条 AWS Direct Connect 连接。创建⼀个传输⽹关，并将每个 VPC 连接到该传
输⽹关。建⽴ Direct Connect 连接和传输⽹关之间的连通性。
https://examlearn.online
[2026/05]
Question #375
Topic 1
⼀家电商公司正在构建⼀个分布式应⽤程序，该应⽤程序涉及多个⽆服务器函数和 AWS 服务，⽤于完成订单处
理任务。这些任务需要⼈⼯审批。解决⽅案架构师需要为该订单处理应⽤程序设计⼀个架构。该解决⽅案必须能
够将多个 AWS Lambda 函数组合成响应迅速的⽆服务器应⽤程序。此外，该解决⽅案还必须能够协调运⾏在
Amazon EC2 实例、容器或本地服务器上的数据和服务。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ AWS Step Functions 构建应⽤程序。
B. 将所有应⽤程序组件集成到 AWS Glue 作业中。
C. 使⽤ Amazon Simple Queue Service (Amazon SQS) 构建应⽤程序。
D. 使⽤ AWS Lambda 函数和 Amazon EventBridge 事件来构建应⽤程序。
Question #376
Topic 1
⼀家公司部署了⼀个 Amazon RDS for MySQL 数据库实例。⼤部分数据库连接来⾃⽆服务器应⽤程序。应⽤程
序对数据库的流量会随机出现显著变化。在⾼需求时段，⽤户反映他们的应⽤程序会遇到数据库连接被拒绝的错
误。
哪种解决⽅案能够以最⼩的运维开销解决此问题？
A. 在 RDS Proxy 中创建代理。配置⽤户应⽤程序以通过 RDS Proxy 使⽤数据库实例。
B. 在⽤户应⽤程序和数据库实例之间部署 Amazon ElastiCache for Memcached。
C. 将数据库实例迁移到具有更⾼ I/O 容量的不同实例类。配置⽤户应⽤程序以使⽤新的数据库实例。
D. 为数据库实例配置多可⽤区 (Multi-AZ)。配置⽤户应⽤程序以在数据库实例之间切换。
https://examlearn.online
[2026/05]
Question #377
Topic 1
⼀家公司最近部署了⼀个新的审计系统，⽤于集中管理 Amazon EC2 实例的操作系统版本、补丁和已安装软件等
信息。解决⽅案架构师必须确保所有通过 EC2 ⾃动扩展组配置的实例在启动和终⽌后都能⽴即向审计系统成功发
送报告。
哪种解决⽅案能最有效地实现这些⽬标？
A. 使⽤计划的 AWS Lambda 函数，并在所有 EC2 实例上远程运⾏脚本，将数据发送到审计系统。
B. 使⽤ EC2 ⾃动扩展⽣命周期钩⼦运⾏⾃定义脚本，在实例启动和终⽌时向审计系统发送数据。
C. 使⽤ EC2 ⾃动扩展启动配置，通过⽤户数据运⾏⾃定义脚本，以便在实例启动和终⽌时将数据发送到审计
系统。
D. 在实例操作系统上运⾏⾃定义脚本，将数据发送到审计系统。配置该脚本，使其在实例启动和终⽌时由
EC2 ⾃动扩展组调⽤。
Question #378
解决⽅案架构师应该推荐哪种⽅案？
Topic 1
⼀家公司正在开发⼀款实时多⼈游戏，该游戏使⽤UDP协议在客户端和服务器之间进⾏通信，并采⽤⾃动扩展机
制。预计⽩天会出现流量⾼峰，因此游戏服务器平台必须能够相应地进⾏调整。开发⼈员希望将玩家分数和其他
⾮关系型数据存储在⼀个⽆需⼈⼯⼲预即可扩展的数据库解决⽅案中。
A. 使⽤ Amazon Route 53 进⾏流量分发，使⽤ Amazon Aurora Serverless 进⾏数据存储。
B. 使⽤⽹络负载均衡器进⾏流量分配，并使⽤ Amazon DynamoDB 按需存储数据。
C. 使⽤⽹络负载均衡器进⾏流量分配，并使⽤ Amazon Aurora 全球数据库进⾏数据存储。
D. 使⽤应⽤程序负载均衡器进⾏流量分配，并使⽤ Amazon DynamoDB 全局表进⾏数据存储。
https://examlearn.online
[2026/05]
Question #379
Topic 1
⼀家公司托管了⼀个前端应⽤程序，该应⽤程序使⽤与 AWS Lambda 集成的 Amazon API Gateway API 后端。
当 API 收到请求时，Lambda 函数会加载多个库。然后，Lambda 函数连接到 Amazon RDS 数据库，处理数
据，并将数据返回给前端应⽤程序。该公司希望确保所有⽤户的响应延迟尽可能低，同时尽可能减少对公司运营
的更改。
哪种解决⽅案能够满⾜这些要求？
A. 建⽴前端应⽤程序与数据库之间的连接，绕过 API 以加快查询速度。
B. 为处理请求的 Lambda 函数配置预置并发。
C. 将查询结果缓存到 Amazon S3 中，以便更快地检索类似数据集。
D. 增加数据库的⼤⼩，以增加 Lambda ⼀次可以建⽴的连接数。
Question #380
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在将其本地⼯作负载迁移到 AWS 云。该公司⽬前已使⽤多个 Amazon EC2 实例和 Amazon RDS 数
据库实例。该公司希望找到⼀种解决⽅案，能够在⾮⼯作时间⾃动启动和停⽌这些 EC2 实例和数据库实例。该解
决⽅案必须最⼤限度地降低成本和基础设施维护。
A. 使⽤弹性调整⼤⼩功能扩展 EC2 实例。在⾮⼯作时间将数据库实例缩减⾄零。
B. 在 AWS Marketplace 上寻找合作伙伴解决⽅案，这些解决⽅案可以按计划⾃动启动和停⽌ EC2 实例和数
据库实例。
C. 启动另⼀个 EC2 实例。配置 crontab 计划任务，以按计划运⾏ shell 脚本来启动和停⽌现有的 EC2 实例
和数据库实例。
D. 创建⼀个 AWS Lambda 函数，⽤于启动和停⽌ EC2 实例和数据库实例。配置 Amazon EventBridge 以按
计划调⽤该 Lambda 函数。
https://examlearn.online
[2026/05]
Question #381
Topic 1
⼀家公司托管着⼀个三层架构的 Web 应⽤程序，其中包含⼀个 PostgreSQL 数据库。该数据库存储⽂档的元数
据。公司通过搜索元数据中的关键词来检索⽂档，并每⽉⽣成⼀份报告。这些⽂档存储在 Amazon S3 中。⽂档
通常只编写⼀次，但会频繁更新。
使⽤关系查询⽣成报告需要⼏个⼩时。报告⽣成过程不得阻⽌任何⽂档修改或新⽂档的添加。解决⽅案架构师需
要实施⼀个解决⽅案来加快报告⽣成速度。
哪个解决⽅案能够在对应⽤程序代码进⾏最少更改的情况下满⾜这些要求？
A. 设置⼀个新的 Amazon DocumentDB（兼容 MongoDB）集群，其中包含⼀个只读副本。扩展只读副本以
⽣成报告。
B. 设置⼀个新的 Amazon Aurora PostgreSQL 数据库集群，其中包含⼀个 Aurora 副本。向 Aurora 副本发
出查询以⽣成报告。
C. 设置⼀个新的 Amazon RDS for PostgreSQL 多可⽤区数据库实例。配置报表模块以查询辅助 RDS 节点，
使报表模块不会影响主节点。
Question #382
D. 创建⼀个新的 Amazon DynamoDB 表来存储⽂档。使⽤固定的写⼊容量来⽀持新⽂档的添加。⾃动扩展
读取容量以⽀持报表⽣成。
Topic 1
⼀家公司在 AWS 上部署了⼀个三层应⽤程序，⽤于接收来⾃⽤户设备的传感器数据。流量先经过⽹络负载均衡
器 (NLB)，然后到达 Web 层的 Amazon EC2 实例，最后到达应⽤层的 EC2 实例。应⽤层会调⽤数据库。
解决⽅案架构师应该如何提⾼传输中数据的安全性？
A. 配置 TLS 监听器。将服务器证书部署到 NLB 上。
B. 配置 AWS Shield Advanced。在 NLB 上启⽤ AWS WAF。
C. 将负载均衡器更改为应⽤程序负载均衡器 (ALB)。在 ALB 上启⽤ AWS WAF。
D. 使⽤ AWS Key Management Service (AWS KMS) 对 EC2 实例上的 Amazon Elastic Block Store
(Amazon EBS) 卷进⾏加密。
https://examlearn.online
[2026/05]
Question #383
Topic 1
⼀家公司计划将其本地数据中⼼的商⽤现成应⽤程序迁移到 AWS。该软件采⽤基于插槽和核⼼的软件许可模式，
具有可预测的容量和正常运⾏时间要求。该公司希望使⽤今年早些时候购买的现有许可证。
哪种 Amazon EC2 定价⽅案最具成本效益？
A. 专属预留主机
B. 专属按需主持⼈
C. 专⽤预留实例
D. 专⽤按需实例
Question #384
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
(S3 标准-IA)。
Topic 1
⼀家公司在多个可⽤区运⾏于 Amazon EC2 Linux 实例上的应⽤程序。该应⽤程序需要⼀个⾼可⽤性且符合
POSIX 标准的存储层。该存储层必须提供最⼤程度的数据持久性，并且能够在各个 EC2 实例之间共享。存储层
中的数据在前 30 天内会被频繁访问，之后访问频率会降低。
A. 使⽤ Amazon S3 标准存储类。创建 S3 ⽣命周期策略，将不常⽤的数据迁移到 S3 Glacier。
B. 使⽤ Amazon S3 标准存储类。创建 S3 ⽣命周期策略，将不经常访问的数据移⾄ S3 标准-不经常访问
C. 使⽤ Amazon Elastic File System (Amazon EFS) 标准存储类。创建⽣命周期管理策略，将不经常访问的
数据迁移到 EFS Standard-Infrequent Access (EFS Standard-IA)。
D. 使⽤ Amazon Elastic File System (Amazon EFS) One Zone 存储类。创建⽣命周期管理策略，将不经常
访问的数据移动到 EFS One Zone-Infrequent Access (EFS One Zone-IA)。
https://examlearn.online
[2026/05]
Question #385
Topic 1
解决⽅案架构师正在创建⼀个新的 VPC 设计。负载均衡器有两个公有⼦⽹，Web 服务器有两个私有⼦⽹，
MySQL 也有两个私有⼦⽹。Web 服务器仅使⽤ HTTPS。解决⽅案架构师已经为负载均衡器创建了⼀个安全组，
允许来⾃ 0.0.0.0/0 的 443 端⼝访问。公司策略要求每个资源都拥有执⾏其任务所需的最⼩访问权限。
为了满⾜这些要求，解决⽅案架构师应该使⽤哪种额外的配置策略？
A. 为 Web 服务器创建⼀个安全组，并允许来⾃ 0.0.0.0/0 的端⼝ 443。为 MySQL 服务器创建⼀个安全组，
并允许来⾃ Web 服务器安全组的端⼝ 3306。
B. 为 Web 服务器创建⽹络 ACL，并允许来⾃ 0.0.0.0/0 的端⼝ 443。为 MySQL 服务器创建⽹络 ACL，并允
许来⾃ Web 服务器安全组的端⼝ 3306。
C. 为 Web 服务器创建⼀个安全组，并允许负载均衡器通过 443 端⼝访问 MySQL 服务器。为 MySQL 服务
器创建⼀个安全组，并允许 Web 服务器安全组通过 3306 端⼝访问 MySQL 服务器。
D. 为 Web 服务器创建⽹络 ACL，并允许负载均衡器访问 443 端⼝。为 MySQL 服务器创建⽹络 ACL，并允
许 Web 服务器安全组访问 3306 端⼝。
Question #386
应该采取什么措施来提⾼后端的性能？
Topic 1
⼀家电商公司在 AWS 上运⾏⼀个多层应⽤程序。前端和后端都运⾏在 Amazon EC2 上，数据库运⾏在 Amazon
RDS for MySQL 上。后端与 RDS 实例通信。频繁地从数据库返回相同的数据集导致性能下降。
A. 实现 Amazon SNS 来存储数据库调⽤。
B. 实现 Amazon ElastiCache 来缓存⼤型数据集。
C. 实现 RDS for MySQL 只读副本以缓存数据库调⽤。
D. 实现 Amazon Kinesis Data Firehose，以流式传输对数据库的调⽤。
https://examlearn.online
[2026/05]
Question #387
Topic 1
⼀位新员⼯加⼊公司担任部署⼯程师。该部署⼯程师将使⽤ AWS CloudFormation 模板创建多个 AWS 资源。解
决⽅案架构师希望该部署⼯程师在执⾏作业活动时遵循最⼩权限原则。
为了实现此⽬标，解决⽅案架构师应该采取哪些操作组合？（选择两项。）
A. 让部署⼯程师使⽤ AWS 账户根⽤户凭证来执⾏ AWS CloudFormation 堆栈操作。
B. 为部署⼯程师创建⼀个新的 IAM ⽤户，并将该 IAM ⽤户添加到附加了 PowerUsers IAM 策略的组中。
C. 为部署⼯程师创建⼀个新的 IAM ⽤户，并将该 IAM ⽤户添加到附加了 AdministratorAccess IAM 策略的
组中。
D. 为部署⼯程师创建⼀个新的 IAM ⽤户，并将该 IAM ⽤户添加到仅允许 AWS CloudFormation 操作的 IAM
策略组中。
E. 为部署⼯程师创建⼀个 IAM ⻆⾊，以明确定义 AWS CloudFormation 堆栈的特定权限，并使⽤该 IAM ⻆
⾊启动堆栈。
Question #388
Topic 1
⼀家公司正在 VPC 中部署⼀个两层 Web 应⽤程序。Web 层使⽤⼀个 Amazon EC2 Auto Scaling 组，该组包含
跨越多个可⽤区的公有⼦⽹。数据库层由⼀个位于独⽴私有⼦⽹中的 Amazon RDS for MySQL 数据库实例组
成。Web 层需要访问数据库以检索产品信息。但
Web 应⽤程序⽆法正常⼯作，并报告⽆法连接到数据库。经确认，数据库已启动并正在运⾏。⽹络 ACL、安全组
和路由表的所有配置仍处于默认状态。
解决⽅案架构师应该建议如何修复此应⽤程序？
A. 在私有⼦⽹的⽹络 ACL 中添加⼀条明确的规则，以允许来⾃ Web 层 EC2 实例的流量。
B. 在 VPC 路由表中添加⼀条路由，以允许 Web 层 EC2 实例与数据库层之间的流量。
C. 将 Web 层的 EC2 实例和数据库层的 RDS 实例部署到两个独⽴的 VPC 中，并配置 VPC 对等连接。
D. 向数据库层 RDS 实例的安全组添加⼊站规则，以允许来⾃ Web 层安全组的流量。
https://examlearn.online
[2026/05]
Question #389
Topic 1
⼀家公司拥有⼀个庞⼤的在线⼴告业务数据集，该数据集存储在单个可⽤区内的 Amazon RDS for MySQL 数据
库实例中。该公司希望业务报表查询的运⾏不会影响⽣产数据库实例的写⼊操作。
哪种解决⽅案满⾜这些要求？
A. 部署 RDS 只读副本以处理业务报告查询。
B. 将数据库实例横向扩展，⽅法是将其放置在弹性负载均衡器后⾯。
C. 将数据库实例扩展到更⼤的实例类型，以处理写⼊操作和查询。
D. 在多个可⽤区部署数据库实例，以处理业务报告查询。
Question #390
哪些解决⽅案可以满⾜这些要求？（选择两个。）
Topic 1
⼀家公司在 Amazon EC2 实例集群上托管了⼀个三层架构的电⼦商务应⽤程序。这些实例运⾏在应⽤程序负载均
衡器 (ALB) 后⾯的⾃动扩展组中。所有电⼦商务数据都存储在 Amazon RDS for MariaDB 多可⽤区数据库实例
中。
该公司希望优化交易期间的客户会话管理。应⽤程序必须持久存储会话数据。
A. 在 ALB 上启⽤粘性会话功能（会话关联）。
B. 使⽤ Amazon DynamoDB 表存储客户会话信息。
C. 部署 Amazon Cognito ⽤户池来管理⽤户会话信息。
D. 部署 Amazon ElastiCache for Redis 集群来存储客户会话信息。
E. 在应⽤程序中使⽤ AWS Systems Manager Application Manager 来管理⽤户会话信息。
https://examlearn.online
[2026/05]
Question #391
Topic 1
⼀家公司需要为其三层⽆状态 Web 应⽤程序制定备份策略。该 Web 应⽤程序运⾏在 Amazon EC2 实例上，这
些实例位于⼀个⾃动扩展组中，并配置了动态扩展策略以响应扩展事件。数据库层运⾏在 Amazon RDS for
PostgreSQL 上。该 Web 应⽤程序不需要在 EC2 实例上存储临时本地存储。公司的恢复点⽬标 (RPO) 为 2 ⼩
时。
备份策略必须最⼤限度地提⾼可扩展性并优化此环境的资源利⽤率。
哪种解决⽅案能够满⾜这些要求？
A. 每 2 ⼩时对 EC2 实例和数据库的 Amazon Elastic Block Store (Amazon EBS) 卷进⾏快照，以满⾜
RPO。
B. 配置快照⽣命周期策略，以创建 Amazon Elastic Block Store (Amazon EBS) 快照。在 Amazon RDS 中
启⽤⾃动备份，以满⾜恢复点⽬标 (RPO)。
C. 保留 Web 层和应⽤层的最新 Amazon 系统映像 (AMI)。在 Amazon RDS 中启⽤⾃动备份，并使⽤时间点
恢复来满⾜ RPO。
D. 每 2 ⼩时对 EC2 实例的 Amazon Elastic Block Store (Amazon EBS) 卷进⾏快照。在 Amazon RDS 中启
⽤⾃动备份，并使⽤时间点恢复来满⾜ RPO。
Question #392
程序必须安全可靠，并且能够被拥有动态 IP 地址的全球客户访问。
解决⽅案架构师应该如何配置安全组以满⾜这些要求？
Topic 1
⼀家公司希望在 AWS 上部署⼀个新的公共 Web 应⽤程序。该应⽤程序包含⼀个使⽤ Amazon EC2 实例的 Web
服务器层，以及⼀个使⽤ Amazon RDS for MySQL 数据库实例的数据库层。该应⽤
A. 配置 Web 服务器的安全组，允许来⾃ 0.0.0.0/0 的 443 端⼝⼊站流量。配置数据库实例的安全组，允许来
⾃ Web 服务器安全组的 3306 端⼝⼊站流量。
B. 配置 Web 服务器的安全组，允许来⾃客户 IP 地址的 443 端⼝⼊站流量。配置数据库实例的安全组，允许
来⾃ Web 服务器安全组的 3306 端⼝⼊站流量。
C. 配置 Web 服务器的安全组，允许来⾃客户 IP 地址的 443 端⼝⼊站流量。配置数据库实例的安全组，允许
来⾃客户 IP 地址的 3306 端⼝⼊站流量。
D. 配置 Web 服务器的安全组，允许来⾃ 0.0.0.0/0 的 443 端⼝⼊站流量。配置数据库实例的安全组，允许来
⾃ 0.0.0.0/0 的 3306 端⼝⼊站流量。
https://examlearn.online
[2026/05]
Question #393
Topic 1
⼀家⽀付处理公司会录制与客户的所有语⾳通信，并将⾳频⽂件存储在 Amazon S3 存储桶中。该公司需要从这
些⾳频⽂件中提取⽂本。该公司必须从⽂本中删除所有属于客户的个⼈身份信息 (PII)。
解决⽅案架构师应该如何满⾜这些要求？
A. 使⽤ Amazon Kinesis Video Streams 处理⾳频⽂件。使⽤ AWS Lambda 函数扫描已知的个⼈身份信息
(PII) 模式。
B. 当⾳频⽂件上传到 S3 存储桶时，调⽤ AWS Lambda 函数启动 Amazon Textract 任务来分析通话录⾳。
C. 配置⼀个启⽤个⼈身份信息 (PII) 脱敏功能的 Amazon Transcribe 转录作业。当⾳频⽂件上传到 S3 存储
桶时，调⽤ AWS Lambda 函数启动转录作业。将输出结果存储在单独的 S3 存储桶中。
D. 创建⼀个 Amazon Connect 联系⼈流程，⽤于接收已启⽤转录功能的⾳频⽂件。嵌⼊⼀个 AWS Lambda
函数来扫描已知的个⼈身份信息 (PII) 模式。使⽤ Amazon EventBridge 在⾳频⽂件上传到 S3 存储桶时启动
联系⼈流程。
Question #394
Topic 1
⼀家公司在 AWS 云上运⾏⼀个多层电⼦商务 Web 应⽤程序。该应⽤程序运⾏在 Amazon EC2 实例上，并使⽤
Amazon RDS for MySQL 多可⽤区数据库实例。Amazon RDS 配置了最新⼀代数据库实例，并在通⽤型 SSD
(gp3) Amazon Elastic Block Store (Amazon EBS) 卷中拥有 2,000 GB 的存储空间。在⾼需求期间，数据库性
能会影响应⽤程序。数据库
管理员分析了 Amazon CloudWatch Logs 中的⽇志，发现当读写 IOPS 超过 20,000 时，应⽤程序性能总是会下
降。
解决⽅案架构师应该如何改进应⽤程序性能？
A. 将⾳量调节器更换为磁性⾳量调节器。
B. 增加 gp3 卷上的 IOPS 数量。
C. 将卷替换为已配置 IOPS SSD (io2) 卷。
D. 将 2,000 GB 的 gp3 卷替换为两个 1,000 GB 的 gp3 卷。
https://examlearn.online
[2026/05]
Question #395
Topic 1
上周，⼀位 IAM ⽤户在公司 AWS 账户中进⾏⽣产部署期间，对其账户中的资源进⾏了多项配置更改。解决⽅案
架构师发现其中⼏条安全组规则配置不正确。该解决⽅案架构师希望确认是哪位 IAM ⽤户进⾏了这些更改。
解决⽅案架构师应该使⽤哪个服务来查找所需信息？
A. Amazon GuardDuty
B. 亚⻢逊督察
C. AWS CloudTrail
D. AWS 配置
Question #396
⼀家公司在 AWS 上部署了⾃托管 DNS 服务。该解决⽅案包含以下内容：
• 位于不同 AWS 区域的 Amazon EC2 实例
• AWS Global Accelerator 中标准加速器的端点。
该公司希望保护该解决⽅案免受 DDoS 攻击。
解决⽅案架构师应该如何满⾜此要求？
A. 订阅 AWS Shield Advanced。将加速器添加为要保护的资源。
B. 订阅 AWS Shield Advanced 服务。将 EC2 实例添加为要保护的资源。
C. 创建⼀个包含基于速率规则的 AWS WAF Web ACL。将该 Web ACL 与加速器关联。
D. 创建⼀个包含基于速率规则的 AWS WAF Web ACL。将该 Web ACL 与 EC2 实例关联。
Topic 1
https://examlearn.online
[2026/05]
Question #397
Topic 1
⼀家电商公司需要运⾏⼀个每⽇定时任务，⽤于汇总和筛选销售记录以进⾏分析。该公司将销售记录存储在
Amazon S3 存储桶中。每个对象的⼤⼩上限为 10 GB。根据销售事件的数量，该任务可能需要⻓达⼀个⼩时才能
完成。该任务的 CPU 和内存使⽤量是恒定的，并且事先已知。
解决⽅案架构师需要最⼤限度地减少运⾏该任务所需的运维⼯作量。
哪种解决⽅案满⾜这些要求？
A. 创建⼀个包含 Amazon EventBridge 通知的 AWS Lambda 函数。安排 EventBridge 事件每天运⾏⼀次。
B. 创建⼀个 AWS Lambda 函数。创建⼀个 Amazon API Gateway HTTP API，并将该 API 与函数集成。创
建⼀个 Amazon EventBridge 定时事件，该事件调⽤ API 并触发函数。
C. 创建⼀个 Amazon Elastic Container Service (Amazon ECS) 集群，启动类型为 AWS Fargate。创建⼀个
Amazon EventBridge 计划事件，该事件会在集群上启动⼀个 ECS 任务来运⾏作业。
D. 创建⼀个 Amazon Elastic Container Service (Amazon ECS) 集群，启动类型为 Amazon EC2，并创建⼀
个包含⾄少⼀个 EC2 实例的⾃动扩展组。创建⼀个 Amazon EventBridge 计划事件，该事件会在集群上启动
⼀个 ECS 任务来运⾏作业。
Question #398
Topic 1
⼀家公司需要将 600 TB 的数据从其本地⽹络附加存储 (NAS) 系统迁移到 AWS 云。数据传输必须在两周内完
成。数据敏感，传输过程中必须加密。该公司的互联⽹连接上传速度可达 100 Mbps。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ Amazon S3 分段上传功能通过 HTTPS 传输⽂件。
B. 在本地 NAS 系统和最近的 AWS 区域之间创建 VPN 连接。通过 VPN 连接传输数据。
C. 使⽤ AWS Snow 系列控制台订购多个 AWS Snowball Edge Storage Optimized 设备。使⽤这些设备将数
据传输到 Amazon S3。
D. 在公司所在地和最近的 AWS 区域之间建⽴ 10 Gbps 的 AWS Direct Connect 连接。通过 VPN 连接将数
据传输到该区域，并将数据存储在 Amazon S3 中。
https://examlearn.online
[2026/05]
Question #399
Topic 1
⼀家⾦融公司在 AWS 上托管了⼀个 Web 应⽤程序。该应⽤程序使⽤ Amazon API Gateway 区域 API 端点，使
⽤户能够获取最新的股票价格。该公司的安全团队注意到 API 请求数量有所增加。安全团队担⼼ HTTP 洪⽔攻击
可能会导致应⽤程序离线。
解决⽅案架构师必须设计⼀个解决⽅案来保护应⽤程序免受此类攻击。
哪个解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 在 API Gateway 区域 API 端点前⾯创建 Amazon CloudFront 分发，最⼤ TTL 为 24 ⼩时。
B. 创建⼀个区域性 AWS WAF Web ACL，并添加基于速率的规则。将该 Web ACL 与 API ⽹关阶段关联。
C. 使⽤ Amazon CloudWatch 指标监控计数指标，并在达到预定义速率时向安全团队发出警报。
D. 在 API Gateway 区域 API 端点前创建 Amazon CloudFront 分发，并部署 Lambda@Edge 函数。创建⼀
个 AWS Lambda 函数，⽤于阻⽌来⾃超出预定义速率的 IP 地址的请求。
Question #400
Topic 1
⼀家⽓象初创公司拥有⼀个定制的Web应⽤程序，⽤于在线向⽤户销售天⽓数据。该公司使⽤Amazon
DynamoDB存储数据，并希望构建⼀项新服务，以便在每次记录到新的天⽓事件时，向四个内部团队的经理发送
警报。该公司不希望这项新服务影响现有应⽤程序的性能。
解决⽅案架构师应该如何做才能在尽可能减少运维开销的情况下满⾜这些要求？
A. 使⽤ DynamoDB 事务将新的事件数据写⼊表。配置事务以通知内部团队。
B. 让当前应⽤程序向四个 Amazon Simple Notification Service (Amazon SNS) 主题发布消息。每个团队订
阅⼀个主题。
C. 在表上启⽤ Amazon DynamoDB Streams。使⽤触发器将数据写⼊单个 Amazon Simple Notification
Service (Amazon SNS) 主题，供团队订阅。
D. 为每条记录添加⾃定义属性以标记新项⽬。编写⼀个定时任务，每分钟扫描⼀次表，查找新增项⽬，并通
知 Amazon Simple Queue Service (Amazon SQS) 队列，供团队订阅。
https://examlearn.online
[2026/05]
Question #401
Topic 1
⼀家公司希望利⽤ AWS 云平台，使其现有应⽤程序具备⾼可⽤性和弹性。该应⽤程序的当前版本部署在公司⾃
身的数据中⼼。最近，由于意外断电导致数据库服务器崩溃，该应⽤程序遭遇了数据丢失。
公司需要⼀个能够避免单点故障的解决⽅案，并且该⽅案必须能够使应⽤程序扩展以满⾜⽤户需求。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤跨多个可⽤区的⾃动扩展组中的 Amazon EC2 实例部署应⽤程序服务器。使⽤多可⽤区配置的
Amazon RDS 数据库实例。
B. 在单个可⽤区内的⾃动扩展组中使⽤ Amazon EC2 实例部署应⽤程序服务器。将数据库部署在 EC2 实例
上。启⽤ EC2 ⾃动恢复。
C. 使⽤跨多个可⽤区的⾃动扩展组中的 Amazon EC2 实例部署应⽤程序服务器。在单个可⽤区中使⽤带有只
读副本的 Amazon RDS 数据库实例。如果主数据库实例发⽣故障，则将只读副本提升为替换主数据库实例。
D. 使⽤跨多个可⽤区的 Auto Scaling 组中的 Amazon EC2 实例部署应⽤程序服务器。将主数据库服务器和
辅助数据库服务器部署在跨多个可⽤区的 EC2 实例上。使⽤ Amazon Elastic Block Store (Amazon EBS) 多
实例附加功能在实例之间创建共享存储。
Question #402
解决⽅案架构师应该如何解决此问题？
Topic 1
⼀家公司需要摄取和处理其应⽤程序⽣成的⼤量流数据。该应⽤程序运⾏在 Amazon EC2 实例上，并将数据发送
到 Amazon Kinesis Data Streams，后者采⽤默认配置。每隔⼀天，该应⽤程序会消耗数据并将其写⼊ Amazon
S3 存储桶以进⾏商业智能 (BI) 处理。该公司发现 Amazon S3 并未接收到应⽤程序发送到 Kinesis Data
Streams 的所有数据。
A. 通过修改数据保留期来更新 Kinesis 数据流的默认设置。
B. 更新应⽤程序，使其使⽤ Kinesis Producer Library (KPL) 将数据发送到 Kinesis Data Streams。
C. 更新 Kinesis 分⽚的数量，以处理发送到 Kinesis 数据流的数据吞吐量。
D. 在 S3 存储桶中启⽤ S3 版本控制，以保留 S3 存储桶中每个对象的每个版本。
https://examlearn.online
[2026/05]
Question #403
Topic 1
开发⼈员有⼀个应⽤程序，该应⽤程序使⽤ AWS Lambda 函数将⽂件上传到 Amazon S3，并且需要执⾏此任务
所需的权限。开发⼈员已经拥有⼀个具有 Amazon S3 所需有效 IAM 凭证的 IAM ⽤户。
解决⽅案架构师应该如何授予这些权限？
A. 在 Lambda 函数的资源策略中添加所需的 IAM 权限。
B. 使⽤ Lambda 函数中现有的 IAM 凭证创建签名请求。
C. 创建⼀个新的 IAM ⽤户，并在 Lambda 函数中使⽤现有的 IAM 凭证。
D. 创建⼀个具有所需权限的 IAM 执⾏⻆⾊，并将该 IAM ⻆⾊附加到 Lambda 函数。
Question #404
解决⽅案架构师应该如何改进此应⽤程序的架构？
Topic 1
⼀家公司部署了⼀个⽆服务器应⽤程序，当新⽂档上传到 Amazon S3 存储桶时，该应⽤程序会调⽤⼀个 AWS
Lambda 函数。该应⽤程序使⽤ Lambda 函数来处理这些⽂档。在最近⼀次市场营销活动之后，该公司发现该应
⽤程序未能处理许多⽂档。
A. 将 Lambda 函数的运⾏时超时值设置为 15 分钟。
B. 配置 S3 存储桶复制策略。将⽂档暂存在 S3 存储桶中，以便稍后处理。
C. 部署⼀个额外的 Lambda 函数。在两个 Lambda 函数之间进⾏⽂档处理负载均衡。
D. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。将请求发送到该队列。将该队列配置为
Lambda 的事件源。
https://examlearn.online
[2026/05]
Question #405
Topic 1
⼀位解决⽅案架构师正在设计软件演示环境的架构。该环境将运⾏在 Amazon EC2 实例上，这些实例位于⾃动扩
展组 (Auto Scaling group) 中，并由应⽤程序负载均衡器 (ALB) 管理。系统在⼯作时间内流量将显著增加，但周
末⽆需运⾏。
为了确保系统能够扩展以满⾜需求，解决⽅案架构师应该采取哪些措施组合？（选择两项。）
A. 使⽤ AWS Auto Scaling 根据请求速率调整 ALB 容量。
B. 使⽤ AWS Auto Scaling 扩展 VPC 互联⽹⽹关的容量。
C. 在多个 AWS 区域中启动 EC2 实例，以将负载分散到各个区域。
D. 使⽤⽬标跟踪扩展策略，根据实例 CPU 利⽤率扩展⾃动扩展组。
E. 使⽤计划扩展功能，将⾃动扩展组的最⼩容量、最⼤容量和期望容量在周末设置为零。在⼀周开始时恢复
为默认值。
Question #406
Topic 1
⼀位解决⽅案架构师正在设计⼀个包含公有⼦⽹和数据库⼦⽹的两层架构。公有⼦⽹中的 Web 服务器必须通过
443 端⼝向互联⽹开放。数据库⼦⽹中的 Amazon RDS for MySQL 数据库实例必须仅可通过 3306 端⼝由 Web
服务器访问。
为了满⾜这些要求，解决⽅案架构师应该采取哪些步骤组合？（选择两项。）
A. 为公⽹⼦⽹创建⽹络 ACL。添加⼀条规则，拒绝出站流量到 0.0.0.0/0 的 3306 端⼝。
B. 为数据库实例创建⼀个安全组。添加⼀条规则，允许来⾃公共⼦⽹ CIDR 块的 3306 端⼝流量。
C. 为公⽹⼦⽹中的 Web 服务器创建⼀个安全组。添加⼀条规则，允许来⾃ 0.0.0.0/0 的 443 端⼝流量。
D. 为数据库实例创建⼀个安全组。添加⼀条规则，允许来⾃ Web 服务器安全组的流量通过 3306 端⼝。
E. 为数据库实例创建⼀个安全组。添加⼀条规则，拒绝除来⾃ Web 服务器安全组的流量之外的所有流量，端
⼝为 3306。
https://examlearn.online
[2026/05]
Question #407
Topic 1
⼀家公司正在为其托管在 AWS 云上的游戏应⽤程序部署共享存储解决⽅案。该公司需要能够使⽤ Lustre 客户端
访问数据。该解决⽅案必须是完全托管的。
哪种解决⽅案符合这些要求？
A. 创建⼀个 AWS DataSync 任务，将数据共享为可挂载的⽂件系统。将该⽂件系统挂载到应⽤程序服务器。
B. 创建 AWS Storage Gateway ⽂件⽹关。创建使⽤所需客户端协议的⽂件共享。将应⽤程序服务器连接到
该⽂件共享。
C. 创建⼀个 Amazon Elastic File System (Amazon EFS) ⽂件系统，并将其配置为⽀持 Lustre。将该⽂件系
统附加到源服务器。将应⽤程序服务器连接到该⽂件系统。
D. 创建⼀个 Amazon FSx for Lustre ⽂件系统。将该⽂件系统连接到源服务器。将应⽤服务器连接到该⽂件
系统。
Question #408
哪个解决⽅案能够满⾜这些要求？
调⽤ AWS Lambda 函数来处理数据。
Topic 1
⼀家公司运⾏⼀个应⽤程序，该应⽤程序从数千台地理位置分散的远程设备接收数据，这些设备使⽤ UDP 协议。
该应⽤程序会⽴即处理数据，并在必要时向设备发送消息。数据不会被存储。
该公司需要⼀个解决⽅案，以最⼤限度地降低设备数据传输的延迟。该解决⽅案还必须能够快速故障转移到另⼀
个 AWS 区域。
A. 配置 Amazon Route 53 故障转移路由策略。在两个区域中分别创建⽹络负载均衡器 (NLB)。配置 NLB 以
B. 使⽤ AWS 全球加速器。在两个区域中分别创建⼀个⽹络负载均衡器 (NLB) 作为终端节点。创建⼀个启动
类型为 Fargate 的 Amazon Elastic Container Service (Amazon ECS) 集群。在该集群上创建⼀个 ECS 服
务。将该 ECS 服务设置为 NLB 的⽬标。在 Amazon ECS 中处理数据。
C. 使⽤ AWS 全球加速器。在两个区域中分别创建⼀个应⽤程序负载均衡器 (ALB) 作为终端节点。创建⼀个
启动类型为 Fargate 的 Amazon Elastic Container Service (Amazon ECS) 集群。在该集群上创建⼀个 ECS
服务。将该 ECS 服务设置为 ALB 的⽬标。在 Amazon ECS 中处理数据。
D. 配置 Amazon Route 53 故障转移路由策略。在两个区域中分别创建⼀个应⽤程序负载均衡器 (ALB)。创建
⼀个启动类型为 Fargate 的 Amazon Elastic Container Service (Amazon ECS) 集群。在该集群上创建⼀个
ECS 服务。将该 ECS 服务设置为 ALB 的⽬标。在 Amazon ECS 中处理数据。
https://examlearn.online
[2026/05]
Question #409
Topic 1
解决⽅案架构师需要将⼀个 Windows Internet Information Services (IIS) Web 应⽤程序迁移到 AWS。该应⽤
程序⽬前依赖于⽤户本地⽹络附加存储 (NAS) 中托管的⽂件共享。解决⽅案架构师建议将 IIS Web 服务器迁移到
连接到该存储解决⽅案的多个可⽤区中的 Amazon EC2 实例，并配置⼀个连接到这些实例的弹性负载均衡器。
哪种⽅案能够最有效地替代本地⽂件共享，并具有最⾼的弹性和持久性？
A. 将⽂件共享迁移到 Amazon RDS。
B. 将⽂件共享迁移到 AWS Storage Gateway。
C. 将⽂件共享迁移到 Amazon FSx for Windows ⽂件服务器。
D. 将⽂件共享迁移到 Amazon Elastic File System (Amazon EFS)。
Question #410
哪种解决⽅案能够满⾜此要求？
Topic 1
⼀家公司正在 Amazon EC2 实例上部署⼀个新应⽤程序。该应⽤程序会将数据写⼊ Amazon Elastic Block Store
(Amazon EBS) 卷。该公司需要确保写⼊ EBS 卷的所有数据在静态存储时都经过加密。
A. 创建⼀个指定 EBS 加密的 IAM ⻆⾊。将该⻆⾊附加到 EC2 实例。
B. 将 EBS 卷创建为加密卷。将 EBS 卷附加到 EC2 实例。
C. 创建⼀个密钥为“加密”且值为“True”的 EC2 实例标签。标记所有需要在 EBS 级别进⾏加密的实例。
D. 创建⼀个 AWS Key Management Service (AWS KMS) 密钥策略，强制账户中的 EBS 加密。确保该密钥
策略处于激活状态。
https://examlearn.online
[2026/05]
Question #411
Topic 1
⼀家公司拥有⼀个使⽤模式不稳定的Web应⽤程序。每⽉初使⽤量较⼤，每周初使⽤量中等，⽽⼀周内的使⽤量
则难以预测。该应⽤程序由⼀个Web服务器和⼀个运⾏在数据中⼼内的MySQL数据库服务器组成。该公司希望将
该应⽤程序迁移到AWS云平台，因此需要选择⼀个经济⾼效且⽆需修改数据库的数据库平台。
哪种解决⽅案能够满⾜这些要求？
A. Amazon DynamoDB
B. Amazon RDS for MySQL
C. 兼容 MySQL 的 Amazon Aurora Serverless
D. MySQL 部署在 Amazon EC2 的⾃动扩展组中
Question #412
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家图⽚托管公司将其对象存储在 Amazon S3 存储桶中。该公司希望避免 S3 存储桶中的对象意外暴露给公
众。整个 AWS 账户中的所有 S3 对象都需要保持私有状态。
A. 使⽤ Amazon GuardDuty 监控 S3 存储桶策略。创建⼀个⾃动修复操作规则，该规则使⽤ AWS Lambda
函数来修复任何使对象公开的更改。
B. 使⽤ AWS Trusted Advisor 查找可公开访问的 S3 存储桶。在 Trusted Advisor 中配置电⼦邮件通知，以
便在检测到更改时收到通知。如果 S3 存储桶策略允许公开访问，请⼿动更改该策略。
C. 使⽤ AWS 资源访问管理器查找可公开访问的 S3 存储桶。使⽤ Amazon Simple Notification Service
(Amazon SNS) 在检测到更改时调⽤ AWS Lambda 函数。部署⼀个 Lambda 函数，以编程⽅式修复此更
改。
D. 在账户级别使⽤ S3 阻⽌公共访问功能。使⽤ AWS Organizations 创建服务控制策略 (SCP)，以防⽌ IAM
⽤户更改此设置。将此 SCP 应⽤到账户。
https://examlearn.online
[2026/05]
Question #413
Topic 1
⼀家电商公司正⾯临⽤户流量激增的困境。该公司的⽹店部署在亚⻢逊 EC2 实例上，采⽤两层架构，包含 Web
层和独⽴的数据库层。随着流量的增⻓，该公司发现这种架构导致营销邮件和订单确认邮件的发送出现严重延
迟。该公司希望减少解决复杂邮件发送问题所花费的时间，并最⼤限度地降低运营成本。
解决⽅案架构师应该如何满⾜这些需求？
A. 使⽤专⻔⽤于电⼦邮件处理的 EC2 实例创建⼀个单独的应⽤程序层。
B. 配置 Web 实例通过 Amazon Simple Email Service (Amazon SES) 发送电⼦邮件。
C. 配置 Web 实例通过 Amazon Simple Notification Service (Amazon SNS) 发送电⼦邮件。
D. 使⽤专⽤于电⼦邮件处理的 EC2 实例创建⼀个单独的应⽤层。将这些实例放置在⾃动扩展组中。
Question #414
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
Topic 1
⼀家公司拥有⼀个每天⽣成数百份报告的业务系统。该系统将这些报告以 CSV 格式保存到⽹络共享位置。该公司
需要将这些数据近乎实时地存储到 AWS 云中以进⾏分析。
A. 使⽤ AWS DataSync 将⽂件传输到 Amazon S3。创建⼀个计划任务，使其在每天结束时运⾏。
B. 创建 Amazon S3 ⽂件⽹关。更新业务系统，使其使⽤来⾃ S3 ⽂件⽹关的新⽹络共享。
C. 使⽤ AWS DataSync 将⽂件传输到 Amazon S3。创建⼀个在⾃动化⼯作流中使⽤ DataSync API 的应⽤
程序。
D. 部署⼀个⽤于 SFTP 的 AWS Transfer 端点。创建⼀个脚本，⽤于检查⽹络共享上是否有新⽂件，并使⽤
SFTP 上传这些新⽂件。
https://examlearn.online
[2026/05]
Question #415
Topic 1
⼀家公司在 Amazon S3 Standard 中存储了 PB 级的数据。这些数据存储在多个 S3 存储桶中，访问频率各不相
同。该公司并不了解所有数据的访问模式。为了优化 S3 的使⽤成本，该公司需要为每个 S3 存储桶实施相应的解
决⽅案。
哪种解决⽅案能够以最⾼的运营效率满⾜这些要求？
A. 创建⼀个 S3 ⽣命周期配置，其中包含⼀条规则，⽤于将 S3 存储桶中的对象转换为 S3 智能分层。
B. 使⽤ S3 存储类别分析⼯具确定 S3 存储桶中每个对象的正确存储层。将每个对象移动到已确定的存储层。
C. 创建⼀个 S3 ⽣命周期配置，其中包含⼀条规则，⽤于将 S3 存储桶中的对象转换为 S3 Glacier 即时检
索。
D. 创建⼀个 S3 ⽣命周期配置，其中包含⼀条规则，⽤于将 S3 存储桶中的对象转换为 S3 单区 - 不频繁访问
(S3 单区 - IA)。
Question #416
A. 配置 Amazon Redshift 集群。
Topic 1
⼀家快速发展的全球电⼦商务公司将其 Web 应⽤程序托管在 AWS 上。该 Web 应⽤程序包含静态内容和动态内
容。⽹站将在线交易处理 (OLTP) 数据存储在 Amazon RDS 数据库中。⽹站⽤户遇到⻚⾯加载缓慢的问题。
解决⽅案架构师应采取哪些措施组合来解决此问题？（选择两项。）
B. 设置 Amazon CloudFront 分发。
C. 将动态 Web 内容托管在 Amazon S3 上。
D. 为 RDS 数据库实例创建只读副本。
E. 为 RDS 数据库实例配置多可⽤区部署。
https://examlearn.online
[2026/05]
Question #417
Topic 1
⼀家公司使⽤ Amazon EC2 实例和 AWS Lambda 函数来运⾏其应⽤程序。该公司在其 AWS 账户中拥有包含公
有⼦⽹和私有⼦⽹的 VPC。EC2 实例运⾏在其中⼀个 VPC 的私有⼦⽹中。Lambda 函数需要直接访问 EC2 实例
的⽹络才能使应⽤程序正常运⾏。
该应⽤程序⾄少运⾏⼀年。该公司预计在此期间应⽤程序使⽤的 Lambda 函数数量将会增加。该公司希望最⼤限
度地节省所有应⽤程序资源，并保持服务之间的⽹络延迟较低。
哪种解决⽅案能够满⾜这些要求？
A. 购买 EC2 实例节省计划，优化 Lambda 函数的持续时间、内存使⽤量和调⽤次数。将 Lambda 函数连接
到包含 EC2 实例的私有⼦⽹。
B. 购买 EC2 实例节省计划，优化 Lambda 函数的持续时间和内存使⽤量、调⽤次数以及传输的数据量。将
Lambda 函数连接到 EC2 实例运⾏所在的同⼀ VPC 中的公共⼦⽹。
C. 购买计算节省计划。优化 Lambda 函数的执⾏时间和内存使⽤量、调⽤次数以及数据传输量。将 Lambda
函数连接到包含 EC2 实例的私有⼦⽹。
D. 购买计算节省计划。优化 Lambda 函数的执⾏时间和内存使⽤量、调⽤次数以及数据传输量。将 Lambda
函数保留在 Lambda 服务 VPC 中。
Question #418
Topic 1
解决⽅案架构师需要允许团队成员访问两个不同 AWS 账户中的 Amazon S3 存储桶：⼀个开发账户和⼀个⽣产账
户。⽬前，团队可以通过使⽤分配给具有相应权限的 IAM 组的唯⼀ IAM ⽤户来访问开发账户中的 S3 存储桶。
解决⽅案架构师在⽣产账户中创建了⼀个 IAM ⻆⾊。该⻆⾊具有⼀条策略，授予其访问⽣产账户中某个 S3 存储
桶的权限。
哪种解决⽅案既能满⾜这些要求，⼜能遵循最⼩权限原则？
A. 将管理员访问策略附加到开发帐户⽤户。
B. 将开发帐户作为主体添加到⽣产帐户⻆⾊的信任策略中。
C. 关闭⽣产帐户中 S3 存储桶的 S3 阻⽌公共访问功能。
D. 在⽣产帐户中为每个团队成员创建⼀个具有唯⼀凭据的⽤户。
https://examlearn.online
[2026/05]
Question #419
Topic 1
⼀家公司使⽤启⽤了所有功能的 AWS Organizations，并在 ap-southeast-2 区域运⾏多个 Amazon EC2 ⼯作负
载。该公司拥有⼀项服务控制策略 (SCP)，该策略禁⽌在任何其他区域创建任何资源。⼀项安全策略要求该公司
对所有静态数据进⾏加密。
审计发现，员⼯为 EC2 实例创建了 Amazon Elastic Block Store (Amazon EBS) 卷，但未对这些卷进⾏加密。
该公司希望任何 IAM ⽤户或 root ⽤户在 ap-southeast-2 区域启动的任何新 EC2 实例都使⽤加密的 EBS 卷。该
公司希望找到⼀种对创建 EBS 卷的员⼯影响最⼩的解决⽅案。
以下哪两项措施组合可以满⾜这些要求？
A. 在 Amazon EC2 控制台中，选择 EBS 加密账户属性并定义默认加密密钥。
B. 创建 IAM 权限边界。将权限边界附加到根组织单元 (OU)。定义该边界，当 ec2:Encrypted 条件等于 false
时，拒绝 ec2:CreateVolume 操作。
C. 创建 SCP。将 SCP 附加到根组织单元 (OU)。定义 SCP，使其在 ec2:Encrypted 条件等于 false 时拒绝
ec2:CreateVolume 操作。
D. 更新每个帐户的 IAM 策略，当 ec2:Encrypted 条件等于 false 时，拒绝 ec2:CreateVolume 操作。
E. 在组织管理帐户中，指定默认 EBS 卷加密设置。
Question #420
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望使⽤ Amazon RDS for PostgreSQL 数据库集群来简化⽣产数据库⼯作负载中耗时的数据库管理任
务。该公司希望确保其数据库具有⾼可⽤性，并在⼤多数情况下提供 40 秒以内的⾃动故障转移⽀持。该公司还
希望将读取操作从主实例卸载，并尽可能降低成本。
A. 使⽤ Amazon RDS 多可⽤区数据库实例部署。创建⼀个只读副本，并将读取⼯作负载指向该只读副本。
B. 使⽤ Amazon RDS 多可⽤区数据库部署 创建两个只读副本，并将读取⼯作负载指向这两个只读副本。
C. 使⽤ Amazon RDS 多可⽤区数据库实例部署。将读取⼯作负载指向多可⽤区对中的辅助实例。
D. 使⽤ Amazon RDS 多可⽤区数据库集群部署，将读取⼯作负载指向读取器端点。
https://examlearn.online
[2026/05]
Question #421
⼀家公司运⾏着⼀个⾼可⽤性的 SFTP 服务。该 SFTP 服务使⽤两个 Amazon EC2 Linux 实例，并配置了弹性 IP
地址，以接收来⾃互联⽹上可信 IP 源的流量。SFTP 服务由连接到这些实例的共享存储提供⽀持。⽤户帐户在
SFTP 服务器上以 Linux ⽤户身份创建和管理。
该公司希望采⽤⼀种⽆服务器⽅案，该⽅案能够提供⾼ IOPS 性能和⾼度可配置的安全性，并且能够保持对⽤户
权限的控制。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个加密的 Amazon Elastic Block Store (Amazon EBS) 卷。创建⼀个 AWS Transfer Family SFTP
⽤户对 SFTP 服务的访问权限。
SFTP 服务的访问权限。
Topic 1
服务，并配置⼀个仅允许受信任 IP 地址访问的公共终端节点。将 EBS 卷附加到该 SFTP 服务终端节点。授予
B. 创建⼀个加密的 Amazon Elastic File System (Amazon EFS) 卷。创建⼀个具有弹性 IP 地址和可⾯向
Internet 访问的 VPC 终端节点的 AWS Transfer Family SFTP 服务。将⼀个安全组附加到该终端节点，仅允
许受信任的 IP 地址访问。将 EFS 卷附加到 SFTP 服务终端节点。授予⽤户对 SFTP 服务的访问权限。
C. 创建⼀个启⽤默认加密的 Amazon S3 存储桶。创建⼀个 AWS Transfer Family SFTP 服务，并为其配置
⼀个仅允许受信任 IP 地址访问的公共终端节点。将 S3 存储桶连接到该 SFTP 服务终端节点。授予⽤户对
D. 创建⼀个启⽤默认加密的 Amazon S3 存储桶。创建⼀个 AWS Transfer Family SFTP 服务，该服务具有⼀
个 VPC 终端节点，该终端节点在私有⼦⽹中具有内部访问权限。添加⼀个安全组，该安全组仅允许受信任的
IP 地址访问。将 S3 存储桶连接到 SFTP 服务终端节点。授予⽤户对 SFTP 服务的访问权限。
https://examlearn.online
[2026/05]
Question #422
⼀家公司正在 AWS 上开发新的机器学习 (ML) 模型解决⽅案。这些模型以独⽴微服务的形式开发，在启动时从
Amazon S3 获取约 1 GB 的模型数据并将其加载到内存中。⽤户通过异步 API 访问这些模型。⽤户可以发送单个
请求或⼀批请求，并指定结果的发送位置。
该公司向数百名⽤户提供这些模型。模型的使⽤模式不规则。有些模型可能数天甚⾄数周都未使⽤。⽽另⼀些模
型则可能⼀次性接收数千个请求。
为了满⾜这些需求，解决⽅案架构师应该推荐哪种设计⽅案？
A. 将来⾃ API 的请求定向到⽹络负载均衡器 (NLB)。将模型部署为由 NLB 调⽤的 AWS Lambda 函数。
Mesh 根据 SQS 队列⼤⼩扩展 ECS 集群实例。
CPU (vCPU) 数量。
B. 将 API 请求定向到应⽤程序负载均衡器 (ALB)。将模型部署为 Amazon Elastic Container Service
Topic 1
(Amazon ECS) 服务，并从 Amazon Simple Queue Service (Amazon SQS) 队列读取数据。使⽤ AWS App
C. 将来⾃ API 的请求定向到 Amazon Simple Queue Service (Amazon SQS) 队列。将模型部署为 AWS
Lambda 函数，并由 SQS 事件调⽤。使⽤ AWS Auto Scaling 根据 SQS 队列⼤⼩增加 Lambda 函数的虚拟
D. 将来⾃ API 的请求定向到 Amazon Simple Queue Service (Amazon SQS) 队列。将模型部署为 Amazon
Elastic Container Service (Amazon ECS) 服务，并从队列中读取数据。根据队列⼤⼩，为集群和服务副本启
⽤ Amazon ECS 上的 AWS Auto Scaling。
https://examlearn.online
[2026/05]
Question #423
解决⽅案架构师希望使⽤以下 JSON ⽂本作为基于身份的策略来授予特定权限：
解决⽅案架构师可以将此策略附加到哪些 IAM 主体？（选择两个。）
A. ⻆⾊
B. 组
C. 组织
D. Amazon Elastic Container Service (Amazon ECS) 资源
E. Amazon EC2 资源
Question #424
Topic 1
Topic 1
⼀家公司在 Amazon EC2 按需实例上运⾏⼀个⾃定义应⽤程序。该应⽤程序的前端节点需要 24 ⼩时全天候运
⾏，后端节点则只需根据⼯作负载短时间运⾏。后端节点的数量会随时间变化。
该公司需要根据⼯作负载进⾏横向扩展，增加实例数量。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 前端节点使⽤预留实例，后端节点使⽤ AWS Fargate。
B. 前端节点使⽤预留实例，后端节点使⽤竞价型实例。
C. 前端节点使⽤竞价型实例，后端节点使⽤预留实例。
D. 前端节点使⽤竞价型实例，后端节点使⽤ AWS Fargate。
https://examlearn.online
[2026/05]
Question #425
Topic 1
⼀家公司使⽤⾼容量块存储来运⾏其本地⼯作负载。该公司每⽇峰值每秒输⼊/输出事务数不超过 15,000 IOPS。
该公司希望将⼯作负载迁移到 Amazon EC2，并配置与存储容量⽆关的磁盘性能。
哪种 Amazon Elastic Block Store (Amazon EBS) 卷类型能够以最具成本效益的⽅式满⾜这些要求？
A. GP2 容量类型
B. io2 体积类型
C. GP3 卷类型
D. io1 卷类型
Question #426
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司需要存储其医疗保健应⽤程序的数据。该应⽤程序的数据经常变更。⼀项新法规要求对所有存储的数据
进⾏审计访问。
该公司将该应⽤程序托管在本地基础设施上，但该基础设施的存储容量即将耗尽。解决⽅案架构师必须在满⾜新
法规要求的前提下，安全地将现有数据迁移到 AWS。
A. 使⽤ AWS DataSync 将现有数据迁移到 Amazon S3。使⽤ AWS CloudTrail 记录数据事件。
B. 使⽤ AWS Snowcone 将现有数据迁移到 Amazon S3。使⽤ AWS CloudTrail 记录管理事件。
C. 使⽤ Amazon S3 Transfer Acceleration 将现有数据迁移到 Amazon S3。使⽤ AWS CloudTrail 记录数据
事件。
D. 使⽤ AWS Storage Gateway 将现有数据迁移到 Amazon S3。使⽤ AWS CloudTrail 记录管理事件。
https://examlearn.online
[2026/05]
Question #427
Topic 1
⼀位解决⽅案架构师正在实现⼀个使⽤ MySQL 数据库的复杂 Java 应⽤程序。该 Java 应⽤程序必须部署在
Apache Tomcat 上，并且必须具备⾼可⽤性。
为了满⾜这些要求，解决⽅案架构师应该怎么做？
A. 将应⽤程序部署到 AWS Lambda。配置 Amazon API Gateway API 以连接到 Lambda 函数。
B. 使⽤ AWS Elastic Beanstalk 部署应⽤程序。配置负载均衡环境和滚动部署策略。
C. 将数据库迁移到 Amazon ElastiCache。配置 ElastiCache 安全组，允许应⽤程序访问。
D. 启动⼀个 Amazon EC2 实例。在 EC2 实例上安装 MySQL 服务器。在服务器上配置应⽤程序。创建
AMI。使⽤该 AMI 创建包含⾃动扩展组的启动模板。
Question #428
哪种解决⽅案能以最安全的⽅式为 Lambda 函数提供对 DynamoDB 表的访问权限？
⽤户没有对 Lambda 函数配置的读写权限。
Topic 1
⼀个⽆服务器应⽤程序使⽤了 Amazon API Gateway、AWS Lambda 和 Amazon DynamoDB。Lambda 函数需
要对 DynamoDB 表进⾏读写操作的权限。
A. 创建⼀个具有 Lambda 函数编程访问权限的 IAM ⽤户。为该⽤户附加⼀个策略，允许其对 DynamoDB 表
进⾏读写操作。将 access_key_id 和 secret_access_key 参数存储到 Lambda 环境变量中。确保其他 AWS
B. 创建⼀个包含 Lambda 作为受信任服务的 IAM ⻆⾊。为该⻆⾊附加⼀个策略，允许其对 DynamoDB 表进
⾏读写访问。更新 Lambda 函数的配置，使其使⽤新⻆⾊作为执⾏⻆⾊。
C. 创建⼀个具有 Lambda 函数编程访问权限的 IAM ⽤户。为该⽤户附加⼀个策略，允许其对 DynamoDB 表
进⾏读写访问。将 access_key_id 和 secret_access_key 参数作为安全字符串参数存储在 AWS Systems
Manager Parameter Store 中。更新 Lambda 函数代码，使其在连接到 DynamoDB 表之前检索这些安全字
符串参数。
D. 创建⼀个包含 DynamoDB 作为受信任服务的 IAM ⻆⾊。为该⻆⾊附加⼀个策略，允许 Lambda 函数对其
进⾏读写访问。更新 Lambda 函数的代码，使其以执⾏⻆⾊的身份附加到该新⻆⾊。
https://examlearn.online
[2026/05]
Question #429
以下 IAM 策略已附加到 IAM 组。这是应⽤于该组的唯⼀策略。
Topic 1
该策略对组成员的有效 IAM 权限是什么？
A. 组成员被允许在美国东部1区内执⾏任何Amazon EC2操作。允许权限之后的语句⽆效。
B. 除⾮使⽤多因素身份验证 (MFA) 登录，否则组成员将被拒绝在美国东部 1 区域内的任何 Amazon EC2 权
限。
C. 启⽤多重身份验证 (MFA) 登录后，组成员拥有对所有区域的 ec2:StopInstances 和
ec2:TerminateInstances 权限。组成员还可以执⾏任何其他 Amazon EC2 操作。
D. 组成员仅在启⽤多重身份验证 (MFA) 登录后，才被允许对 us-east-1 区域执⾏ ec2:StopInstances 和
ec2:TerminateInstances 操作。组成员可以对 us-east-1 区域内的 Amazon EC2 执⾏任何其他操作。
https://examlearn.online
[2026/05]
Question #430
Topic 1
⼀家制造公司拥有机器传感器，这些传感器会将 .csv ⽂件上传到 Amazon S3 存储桶。这些 .csv ⽂件必须转换
为图像，并尽快⽤于⾃动⽣成图形报告。
图像会在⼀个⽉后失效，但 .csv ⽂件必须保留，以便每年两次训练机器学习 (ML) 模型。ML 模型的训练和审核
需要提前数周进⾏计划。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 启动⼀个 Amazon EC2 Spot 实例，该实例每⼩时下载 .csv ⽂件，⽣成图像⽂件，并将图像上传到 S3 存
储桶。
B. 设计⼀个 AWS Lambda 函数，将 .csv ⽂件转换为图像并将图像存储在 S3 存储桶中。当上传 .csv ⽂件时
调⽤该 Lambda 函数。
C. 为 S3 存储桶中的 .csv ⽂件和图像⽂件创建 S3 ⽣命周期规则。.csv ⽂件上传 1 天后从 S3 标准存储迁移
到 S3 Glacier 存储。图像⽂件在 30 天后过期。
D. 为 S3 存储桶中的 .csv ⽂件和图像⽂件创建 S3 ⽣命周期规则。.csv ⽂件上传 1 天后从 S3 标准存储转换
为 S3 单区域低频访问 (S3 One Zone-IA)。图像⽂件在 30 天后过期。
Question #431
解决⽅案架构师应该如何满⾜这些需求？
E. 为 S3 存储桶中的 .csv ⽂件和图像⽂件创建 S3 ⽣命周期规则。.csv ⽂件上传 1 天后，将其从 S3 标准存
储转换为 S3 标准-不频繁访问 (S3 Standard-IA)。将图像⽂件保留在低冗余存储 (RRS) 中。
Topic 1
⼀家公司开发了⼀款新的视频游戏，并将其作为 Web 应⽤程序运⾏。该应⽤程序采⽤三层架构，部署在 VPC
中，数据库层使⽤ Amazon RDS for MySQL。多名玩家将同时在线竞技。游戏开发者希望近乎实时地显示前⼗名
排⾏榜，并提供暂停和恢复游戏的功能，同时保留当前分数。
A. 设置 Amazon ElastiCache for Memcached 集群来缓存分数，以便 Web 应⽤程序显示。
B. 设置 Amazon ElastiCache for Redis 集群来计算和缓存分数，以便 Web 应⽤程序显示。
C. 在 Web 应⽤程序前⾯放置 Amazon CloudFront 分发，以缓存应⽤程序部分中的记分板。
D. 在 Amazon RDS 上为 MySQL 创建⼀个只读副本，以运⾏查询来计算记分板并向 Web 应⽤程序提供读取
流量。
https://examlearn.online
[2026/05]
Question #432
Topic 1
⼀家电商公司希望利⽤机器学习 (ML) 算法构建和训练模型。该公司将使⽤这些模型来可视化复杂场景并检测客
户数据中的趋势。架构团队希望将 ML 模型与报表平台集成，以便分析增强后的数据，并将这些数据直接⽤于其
商业智能仪表板。
哪种解决⽅案能够以最低的运营成本满⾜这些需求？
A. 使⽤ AWS Glue 创建机器学习转换，以构建和训练模型。使⽤ Amazon OpenSearch Service 可视化数
据。
B. 使⽤ Amazon SageMaker 构建和训练模型。使⽤ Amazon QuickSight 可视化数据。
C. 使⽤ AWS Marketplace 中预构建的 ML Amazon Machine Image (AMI) 来构建和训练模型。使⽤
Amazon OpenSearch Service 来可视化数据。
D. 使⽤ Amazon QuickSight 通过计算字段构建和训练模型。使⽤ Amazon QuickSight 可视化数据。
Question #433
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在多个 AWS 账户中运⾏其⽣产环境和⾮⽣产环境⼯作负载。这些账户位于 AWS Organizations 的同⼀
个组织中。该公司需要设计⼀个解决⽅案来防⽌成本使⽤标签被修改。
A. 创建⾃定义 AWS Config 规则，防⽌除授权主体之外的任何⼈修改标签。
B. 在 AWS CloudTrail 中创建⾃定义跟踪以防⽌标签被修改。
C. 创建服务控制策略 (SCP)，以防⽌除授权主体之外的任何⼈修改标签。
D. 创建⾃定义 Amazon CloudWatch ⽇志以防⽌标签被修改。
https://examlearn.online
[2026/05]
Question #434
Topic 1
⼀家公司将其应⽤程序托管在 AWS 云上。该应⽤程序运⾏在 Amazon EC2 实例上，位于⾃动扩展组的弹性负载
均衡器 (ELB) 之后，并使⽤ Amazon DynamoDB 表。该公司希望确保该应⽤程序能够以最⼩的停机时间迁移到
另⼀个 AWS 区域。
解决⽅案架构师应该如何做才能在最⼤程度减少停机时间的情况下满⾜这些要求？
A. 在灾难恢复区域中创建⾃动扩展组和负载均衡器。将 DynamoDB 表配置为全局表。配置 DNS 故障转移，
使其指向新的灾难恢复区域的负载均衡器。
B. 创建⼀个 AWS CloudFormation 模板，⽤于创建 EC2 实例、负载均衡器和 DynamoDB 表，以便在需要时
启动。配置 DNS 故障转移，使其指向新的灾难恢复区域的负载均衡器。
C. 创建⼀个 AWS CloudFormation 模板，⽤于创建 EC2 实例和负载均衡器，以便在需要时启动。将
DynamoDB 表配置为全局表。配置 DNS 故障转移，使其指向新的灾难恢复区域的负载均衡器。
D. 在灾难恢复区域中创建⾃动扩展组和负载均衡器。将 DynamoDB 表配置为全局表。创建 Amazon
CloudWatch 警报以触发 AWS Lambda 函数，该函数更新指向灾难恢复负载均衡器的 Amazon Route 53。
Question #435
哪种解决⽅案能够以最具成本效益的⽅式迁移该数据库？
Topic 1
⼀家公司需要在两周内将⼀个 MySQL 数据库从其本地数据中⼼迁移到 AWS。该数据库⼤⼩为 20 TB。该公司希
望尽可能减少停机时间。
A. 订购⼀台 AWS Snowball Edge 存储优化设备。使⽤ AWS 数据库迁移服务 (AWS DMS) 和 AWS 架构转换
⼯具 (AWS SCT) 迁移数据库，并复制正在进⾏的更改。将 Snowball Edge 设备发送⾄ AWS 以完成迁移并继
续进⾏复制。
B. 订购⼀辆 AWS 雪地摩托⻋。使⽤ AWS 数据库迁移服务 (AWS DMS) 和 AWS 架构转换⼯具 (AWS SCT)
迁移包含持续变更的数据库。将雪地摩托⻋送回 AWS 以完成迁移并继续进⾏复制。
C. 订购⼀台配备 GPU 的 AWS Snowball Edge Compute Optimized 设备。使⽤ AWS Database Migration
Service (AWS DMS) 和 AWS Schema Conversion Tool (AWS SCT) 迁移包含持续变更的数据库。将
Snowball 设备发送⾄ AWS 以完成迁移并继续进⾏复制。
D. 订购⼀条 1 GB 专⽤ AWS Direct Connect 连接，以建⽴与数据中⼼的连接。使⽤ AWS 数据库迁移服务
(AWS DMS) 和 AWS 模式转换⼯具 (AWS SCT) 迁移数据库，并复制正在进⾏的更改。
https://examlearn.online
[2026/05]
Question #436
Topic 1
⼀家公司将其本地 PostgreSQL 数据库迁移到了 Amazon RDS for PostgreSQL 数据库实例。该公司成功发布了
⼀款新产品，数据库负载随之增加。该公司希望在不增加基础设施的情况下应对更⼤的负载。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 购买⾜够多的预留数据库实例来满⾜全部⼯作负载的需求。增加 Amazon RDS for PostgreSQL 数据库实
例的容量。
B. 将 Amazon RDS for PostgreSQL 数据库实例设为多可⽤区数据库实例。
C. 为全部⼯作负载购买预留数据库实例。添加另⼀个 Amazon RDS for PostgreSQL 数据库实例。
D. 将 Amazon RDS for PostgreSQL 数据库实例设为按需数据库实例。
Question #437
解决⽅案架构师应该提出什么建议？
Topic 1
⼀家公司在 Amazon EC2 实例上运营⼀个电⼦商务⽹站，该⽹站位于⾃动扩展组的应⽤负载均衡器 (ALB) 之
后。该⽹站⽬前⾯临性能问题，原因是来⾃ IP 地址不断变化的⾮法外部系统的请求速率过⾼。安全团队担⼼⽹站
可能遭受 DDoS 攻击。该公司必须以尽可能减少对合法⽤户影响的⽅式阻⽌这些⾮法传⼊请求。
A. 部署 Amazon Inspector 并将其与 ALB 关联。
B. 部署 AWS WAF，将其与 ALB 关联，并配置速率限制规则。
C. 将规则部署到与 ALB 关联的⽹络 ACL 中，以阻⽌传⼊流量。
D. 部署 Amazon GuardDuty 并在配置 GuardDuty 时启⽤速率限制保护。
https://examlearn.online
[2026/05]
Question #438
Topic 1
⼀家公司希望与外部审计师共享会计数据。数据存储在位于私有⼦⽹中的 Amazon RDS 数据库实例中。审计师拥
有⾃⼰的 AWS 账户，并且需要数据库的独⽴副本。
公司与审计师共享数据库最安全的⽅式是什么？
A. 创建数据库的只读副本。配置 IAM 标准数据库身份验证，以授予审计员访问权限。
B. 将数据库内容导出为⽂本⽂件。将⽂件存储在 Amazon S3 存储桶中。为审计员创建⼀个新的 IAM ⽤户。
授予该⽤户对 S3 存储桶的访问权限。
C. 将数据库快照复制到 Amazon S3 存储桶。创建⼀个 IAM ⽤户。将该⽤户的密钥共享给审计员，以授予其
对 S3 存储桶中对象的访问权限。
D. 创建数据库的加密快照。与审计员共享该快照。允许访问 AWS Key Management Service (AWS KMS) 加
密密钥。
Question #439
哪种解决⽅案能够以最⼩的运维开销解决此问题？
Topic 1
解决⽅案架构师配置了⼀个 IP 地址范围较⼩的 VPC。随着 VPC 中 Amazon EC2 实例数量的增加，IP 地址数量
不⾜以满⾜未来⼯作负载的需求。
A. 添加⼀个额外的 IPv4 CIDR 块，以增加 IP 地址数量并在 VPC 中创建额外的⼦⽹。使⽤新的 CIDR 在新⼦
⽹中创建新资源。
B. 创建第⼆个 VPC，并添加额外的⼦⽹。使⽤对等连接将第⼆个 VPC 与第⼀个 VPC 连接起来。更新路由，
并在第⼆个 VPC 的⼦⽹中创建新资源。
C. 使⽤ AWS Transit Gateway 添加传输⽹关，并将第⼆个 VPC 与第⼀个 VPC 连接起来。更新传输⽹关和
VPC 的路由。在第⼆个 VPC 的⼦⽹中创建新资源。
D. 创建第⼆个 VPC。使⽤ Amazon EC2 上的 VPN 托管解决⽅案和虚拟专⽤⽹关，在第⼀个 VPC 和第⼆个
VPC 之间创建站点到站点 VPN 连接。将 VPC 之间的路由更新为通过 VPN 的流量。在第⼆个 VPC 的⼦⽹中
创建新资源。
https://examlearn.online
[2026/05]
Question #440
Topic 1
⼀家公司在应⽤程序测试期间使⽤了 Amazon RDS for MySQL 数据库实例。在测试周期结束终⽌数据库实例之
前，解决⽅案架构师创建了两个备份。第⼀个备份是使⽤ mysqldump ⼯具创建数据库转储。第⼆个备份是在
RDS 终⽌时启⽤最终数据库快照选项创建的。
该公司现在计划进⾏新的测试周期，并希望从最新的备份创建⼀个新的数据库实例。该公司已选择 Amazon
Aurora 的 MySQL 兼容版本来托管该数据库实例。
哪些解决⽅案可以创建新的数据库实例？（选择两个。）
A. 将 RDS 快照直接导⼊ Aurora。
B. 将 RDS 快照上传到 Amazon S3。然后将 RDS 快照导⼊到 Aurora。
C. 将数据库转储⽂件上传到 Amazon S3。然后将数据库转储⽂件导⼊到 Aurora 中。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将 RDS 快照导⼊ Aurora。
E. 将数据库转储上传到 Amazon S3。然后使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据库转储导⼊到
Aurora。
Question #441
Topic 1
⼀家公司在 Amazon Linux Amazon EC2 实例上托管了⼀个多层 Web 应⽤程序，这些实例位于应⽤程序负载均
衡器 (APP) 之后。这些实例运⾏在跨多个可⽤区的⾃动扩展组中。该公司发现，当应⽤程序的最终⽤户访问⼤量
静态 Web 内容时，⾃动扩展组会启动更多按需实例。该公司希望优化成本。
解决⽅案架构师应该如何以最具成本效益的⽅式重新设计该应⽤程序？
A. 更新⾃动扩展组，使其使⽤预留实例⽽不是按需实例。
B. 更新⾃动扩展组，使其通过启动竞价型实例⽽不是按需实例来进⾏扩展。
C. 创建 Amazon CloudFront 分发，以托管来⾃ Amazon S3 存储桶的静态 Web 内容。
D. 在 Amazon API Gateway API 后⾯创建⼀个 AWS Lambda 函数来托管静态⽹站内容。
https://examlearn.online
[2026/05]
Question #442
Topic 1
⼀家公司在多个 AWS 账户中存储了数 PB 的数据。该公司使⽤ AWS Lake Formation 来管理其数据湖。该公司
的数据科学团队希望安全地与公司⼯程团队共享其账户中的特定数据，⽤于分析⽬的。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 将所需数据复制到公共帐户。在该帐户中创建 IAM 访问⻆⾊。通过指定权限策略授予访问权限，该策略将
⼯程团队帐户中的⽤户列为受信任实体。
B. 在存储数据的每个帐户中使⽤ Lake Formation 权限授予命令，以允许所需的⼯程团队⽤户访问数据。
C. 使⽤ AWS Data Exchange 将所需数据私下发布到所需的⼯程团队帐户。
D. 使⽤基于 Lake Formation 标签的访问控制来授权和授予⼯程团队帐户访问所需数据的跨帐户权限。
Question #443
解决⽅案架构师应该如何实现这⼀⽬标？
Topic 1
⼀家公司希望在 AWS 上托管⼀个可扩展的 Web 应⽤程序。该应⽤程序将供来⾃世界各地不同地区的⽤户访问。
⽤户可以下载和上传⾼达 GB ⼤⼩的独⽴数据。开发团队希望找到⼀种经济⾼效的解决⽅案，以最⼤限度地减少
上传和下载延迟并提⾼性能。
A. 使⽤ Amazon S3 和传输加速功能来托管应⽤程序。
B. 使⽤带有 CacheControl 标头的 Amazon S3 来托管应⽤程序。
C. 使⽤ Amazon EC2 和 Auto Scaling 以及 Amazon CloudFront 来托管应⽤程序。
D. 使⽤ Amazon EC2 和 Auto Scaling 以及 Amazon ElastiCache 来托管应⽤程序。
https://examlearn.online
[2026/05]
Question #444
Topic 1
⼀家公司聘请了⼀位解决⽅案架构师为其应⽤程序设计可靠的架构。该应⽤程序包含⼀个 Amazon RDS 数据库实
例和两个⼿动配置的运⾏ Web 服务器的 Amazon EC2 实例。这些 EC2 实例位于同⼀个可⽤区。
最近，⼀名员⼯删除了数据库实例，导致应⽤程序瘫痪了 24 ⼩时。该公司⾮常关注其环境的整体可靠性。
解决⽅案架构师应该如何做才能最⼤限度地提⾼应⽤程序基础设施的可靠性？
A. 删除⼀个 EC2 实例，并在另⼀个 EC2 实例上启⽤终⽌保护。将数据库实例更新为多可⽤区 (Multi-AZ) 实
例，并启⽤删除保护。
B. 将数据库实例更新为多可⽤区实例，并启⽤删除保护。将 EC2 实例置于应⽤程序负载均衡器之后，并在跨
多个可⽤区的 EC2 ⾃动扩展组中运⾏它们。
C. 创建⼀个额外的数据库实例，以及⼀个 Amazon API Gateway 和⼀个 AWS Lambda 函数。配置应⽤程序
通过 API Gateway 调⽤ Lambda 函数。让 Lambda 函数将数据写⼊这两个数据库实例。
D. 将 EC2 实例放置在包含多个⼦⽹且位于多个可⽤区的 EC2 ⾃动扩展组中。使⽤竞价型实例⽽⾮按需实
例。设置 Amazon CloudWatch 警报以监控实例的运⾏状况。将数据库实例更新为多可⽤区实例，并启⽤删
除保护。
Question #445
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在其企业数据中⼼的⼤型⽹络附加存储 (NAS) 系统中存储了 700 TB 的数据。该公司采⽤混合云环境，
并使⽤ 10 Gbps 的 AWS Direct Connect 连接。
监管机构审计后，该公司有 90 天的时间将数据迁移到云端。该公司需要⾼效且⽆中断地完成数据迁移，并且在
迁移期间仍能访问和更新数据。
A. 在企业数据中⼼创建 AWS DataSync 代理。创建数据传输任务，启动向 Amazon S3 存储桶的传输。
B. 将数据备份到 AWS Snowball Edge Storage Optimized 设备。将设备运送到 AWS 数据中⼼。在本地⽂件
系统上挂载⽬标 Amazon S3 存储桶。
C. 使⽤ rsync 通过 Direct Connect 连接将数据直接从本地存储复制到指定的 Amazon S3 存储桶。
D. 将数据备份到磁带上。将磁带运送到 AWS 数据中⼼。在本地⽂件系统上挂载⽬标 Amazon S3 存储桶。
https://examlearn.online
[2026/05]
Question #446
Topic 1
⼀家公司将数据以 PDF 格式存储在 Amazon S3 存储桶中。该公司必须遵守法律规定，将所有新增和现有数据在
Amazon S3 中保留 7 年。
哪种解决⽅案能够以最低的运营成本满⾜这些要求？
A. 为 S3 存储桶启⽤ S3 版本控制功能。配置 S3 ⽣命周期，使其在 7 年后删除数据。为所有 S3 对象配置多
重身份验证 (MFA) 删除。
B. 为 S3 存储桶启⽤ S3 对象锁定，并启⽤治理保留模式。将保留期限设置为 7 年后到期。重新复制所有现有
对象，以使现有数据符合规范。
C. 为 S3 存储桶启⽤ S3 对象锁定，并设置合规性保留模式。将保留期限设置为 7 年后到期。重新复制所有现
有对象，以使现有数据符合合规性要求。
D. 为 S3 存储桶启⽤ S3 对象锁定，并设置合规性保留模式。将保留期限设置为 7 年后到期。使⽤ S3 批量操
作使现有数据符合合规性要求。
Question #447
解决⽅案架构师应该如何将流量路由到多个区域？
Topic 1
⼀家公司有⼀个⽆状态 Web 应⽤程序，该应⽤程序运⾏在 AWS Lambda 函数上，并通过 Amazon API Gateway
调⽤。该公司希望将该应⽤程序部署到多个 AWS 区域，以实现区域故障转移功能。
A. 为每个区域创建 Amazon Route 53 健康检查。使⽤双活故障转移配置。
B. 为每个区域创建⼀个源站点，并创建⼀个 Amazon CloudFront 分发。使⽤ CloudFront 健康检查来路由流
量。
C. 创建传输⽹关。将传输⽹关连接到每个区域的 API ⽹关端点。配置传输⽹关以路由请求。
D. 在主区域中创建应⽤程序负载均衡器。将⽬标组设置为指向每个区域中的 API ⽹关端点主机名。
https://examlearn.online
[2026/05]
Question #448
Topic 1
⼀家公司有两个虚拟私有云 (VPC)，分别名为管理 VPC 和⽣产 VPC。管理 VPC 通过客户⽹关使⽤ VPN 连接到
数据中⼼中的单个设备。⽣产 VPC 使⽤虚拟专⽤⽹关，并附加了两个 AWS Direct Connect 连接。管理 VPC 和
⽣产 VPC 都使⽤同⼀个 VPC 对等连接来实现应⽤程序之间的通信。
解决⽅案架构师应该如何降低此架构中单点故障的⻛险？
A. 在管理 VPC 和⽣产 VPC 之间添加⼀组 VPN。
B. 添加第⼆个虚拟专⽤⽹关并将其附加到管理 VPC。
C. 从第⼆个客户⽹关设备向管理 VPC 添加第⼆组 VPN。
D. 在管理 VPC 和⽣产 VPC 之间添加第⼆个 VPC 对等连接。
Question #449
Topic 1
⼀家公司⽬前在Oracle数据库上运⾏其应⽤程序。由于数据库、备份管理和数据中⼼维护⽅⾯的资源有限，该公
司计划快速迁移到AWS。该应⽤程序使⽤了需要特权访问的第三⽅数据库功能。
哪种解决⽅案能够以最具成本效益的⽅式帮助该公司将数据库迁移到AWS？
A. 将数据库迁移到 Amazon RDS for Oracle。⽤云服务替换第三⽅功能。
B. 将数据库迁移到 Amazon RDS Custom for Oracle。⾃定义数据库设置以⽀持第三⽅功能。
C. 将数据库迁移到 Amazon EC2 Amazon Machine Image (AMI) for Oracle。⾃定义数据库设置以⽀持第三
⽅功能。
D. 将数据库迁移到 Amazon RDS for PostgreSQL，⽅法是重写应⽤程序代码以消除对 Oracle APEX 的依
赖。
https://examlearn.online
[2026/05]
Question #450
⼀家公司有⼀个三层架构的Web应⽤程序，⽬前运⾏在单个服务器上。该公司希望将该应⽤程序迁移到AWS云平
台。同时，该公司还希望该应⽤程序符合AWS良好架构框架，并遵循AWS推荐的安全性、可扩展性和弹性⽅⾯的
最佳实践。
以下哪三项解决⽅案组合能够满⾜这些要求？（选择三项。）
A. 在两个可⽤区之间创建 VPC，并使⽤应⽤程序的现有架构。将应⽤程序及其现有架构托管在每个可⽤区私
Topic 1
有⼦⽹的 Amazon EC2 实例上，并配置 EC2 ⾃动扩展组。使⽤安全组和⽹络访问控制列表 (ACL) 保护 EC2
实例。
B. 设置安全组和⽹络访问控制列表（⽹络 ACL）以控制对数据库层的访问。在私有⼦⽹中设置单个 Amazon
RDS 数据库。
C. 在两个可⽤区之间创建 VPC。重构应⽤程序，使其托管 Web 层、应⽤层和数据库层。将每⼀层托管在各
⾃的私有⼦⽹中，并为 Web 层和应⽤层使⽤⾃动扩展组。
D. 使⽤单个 Amazon RDS 数据库。仅允许应⽤层安全组访问数据库。
E. 在 Web 层前端使⽤弹性负载均衡器。通过使⽤包含对每⼀层安全组的引⽤的安全组来控制访问。
F. 在私有⼦⽹中使⽤ Amazon RDS 数据库多可⽤区集群部署。仅允许应⽤层安全组访问数据库。
https://examlearn.online
[2026/05]
Question #451
⼀家公司正在将其应⽤程序和数据库迁移到 AWS 云。该公司将使⽤ Amazon Elastic Container Service
(Amazon ECS)、AWS Direct Connect 和 Amazon RDS。
哪些活动将由该公司的运维团队管理？（选择三项。）
A. Amazon RDS 基础设施层、操作系统和平台的管理
B. 创建 Amazon RDS 数据库实例并配置计划维护窗⼝
C. 在 Amazon ECS 上配置其他软件组件，⽤于监控、补丁管理、⽇志管理和主机⼊侵检测
D. 为 Amazon RDS 数据库的所有次要和主要版本安装补丁
E. 确保数据中⼼内 Amazon RDS 基础设施的物理安全
F. 对通过直连传输的数据进⾏加密
Question #452
哪种解决⽅案能够满⾜这些要求？
Topic 1
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个基于 Java 的作业。该作业每⼩时运⾏⼀次，每次运⾏耗时 10 秒。作
业按计划间隔运⾏，并消耗 1 GB 内存。除了作业会短暂占⽤全部可⽤ CPU 的⾼峰期外，实例的 CPU 利⽤率通
常很低。该公司希望优化运⾏该作业的成本。
A. 使⽤ AWS App2Container (A2C) 将作业容器化。在 AWS Fargate 上以 Amazon Elastic Container
Service (Amazon ECS) 任务的形式运⾏该作业，分配 0.5 个虚拟 CPU (vCPU) 和 1 GB 内存。
B. 将代码复制到具有 1 GB 内存的 AWS Lambda 函数中。创建 Amazon EventBridge 计划规则，使代码每⼩
时运⾏⼀次。
C. 使⽤ AWS App2Container (A2C) 将作业容器化。将容器安装到现有的 Amazon 系统映像 (AMI) 中。确保
任务完成后，调度程序会停⽌容器。
D. 配置现有计划，以便在作业完成后停⽌ EC2 实例，并在下⼀个作业开始时重新启动 EC2 实例。
https://examlearn.online
[2026/05]
Question #453
Topic 1
⼀家公司希望为 Amazon EC2 数据和多个 Amazon S3 存储桶实施备份策略。由于监管要求，该公司必须将备份
⽂件保留特定时间段。在保留期内，该公司不得更改这些⽂件。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Backup 创建⼀个具有治理模式保险库锁的备份保险库。创建所需的备份计划。
B. 使⽤ Amazon Data Lifecycle Manager 创建所需的⾃动快照策略。
C. 使⽤ Amazon S3 ⽂件⽹关创建备份。配置相应的 S3 ⽣命周期管理。
D. 使⽤ AWS Backup 创建⼀个具有合规模式保险库锁的备份保险库。创建所需的备份计划。
Question #454
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
Topic 1
⼀家公司在多个 AWS 区域和账户中拥有资源。⼀位新聘的解决⽅案架构师发现，前任员⼯没有提供资源清单的
详细信息。该解决⽅案架构师需要构建并映射所有账户中各种⼯作负载之间的关系。
A. 使⽤ AWS Systems Manager Inventory 从详细视图报告⽣成地图视图。
B. 使⽤ AWS Step Functions 收集⼯作负载详细信息。⼿动构建⼯作负载的架构图。
C. 使⽤ AWS 上的⼯作负载发现功能⽣成⼯作负载的架构图。
D. 使⽤ AWS X-Ray 查看⼯作负载详情。构建包含关系的架构图。
https://examlearn.online
[2026/05]
Question #455
Topic 1
⼀家公司使⽤ AWS Organizations。该公司希望为其部分 AWS 账户设置不同的预算。该公司希望在特定时期
内，当分配的预算达到阈值时，能够收到警报并⾃动阻⽌在 AWS 账户上配置额外的资源。
以下哪些解决⽅案组合可以满⾜这些要求？（选择三个。）
A. 使⽤ AWS Budgets 创建预算。在所需 AWS 账户的“成本和使⽤情况报告”部分下设置预算⾦额。
B. 使⽤ AWS Budgets 创建预算。在所需 AWS 账户的账单控制⾯板下设置预算⾦额。
C. 为 AWS Budgets 创建⼀个 IAM ⽤户，以便运⾏预算操作并具有所需的权限。
D. 为 AWS Budgets 创建⼀个 IAM ⻆⾊，使其能够运⾏预算操作并具有所需的权限。
E. 添加警报，在每个账户达到预算阈值时通知公司。添加预算操作，选择使⽤相应配置规则创建的 IAM 身
份，以防⽌配置额外资源。
F. 添加警报，在每个账户达到预算阈值时通知公司。添加预算操作，选择使⽤相应服务控制策略 (SCP) 创建
的身份和访问管理 (IAM) 身份，以防⽌配置额外资源。
Question #456
Topic 1
⼀家公司在⼀个 AWS 区域中的 Amazon EC2 实例上运⾏应⽤程序。该公司希望将这些 EC2 实例备份到另⼀个
区域。此外，该公司还希望在第⼆个区域中配置 EC2 资源，并从⼀个 AWS 账户集中管理这些 EC2 实例。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建⼀个灾难恢复 (DR) 计划，在第⼆个区域中使⽤数量相近的 EC2 实例。配置数据复制。
B. 创建 EC2 实例的 Amazon Elastic Block Store (Amazon EBS) 时间点快照。定期将快照复制到第⼆个区
域。
C. 使⽤ AWS Backup 创建备份计划。为 EC2 实例配置跨区域备份到第⼆个区域。
D. 在第⼆个区域中部署数量相近的 EC2 实例。使⽤ AWS DataSync 将数据从源区域传输到第⼆个区域。
https://examlearn.online
[2026/05]
Question #457
Topic 1
⼀家使⽤ AWS 的公司正在构建⼀个应⽤程序，⽤于向产品制造商传输数据。该公司拥有⾃⼰的身份提供商
(IdP)。该公司希望 IdP 在⽤户使⽤该应⽤程序传输数据时对其进⾏身份验证。该公司必须使⽤适⽤性声明 2
(AS2) 协议。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS DataSync 传输数据。创建⽤于身份提供商 (IdP) 身份验证的 AWS Lambda 函数。
B. 使⽤ Amazon AppFlow 流传输数据。创建⼀个⽤于身份提供商 (IdP) 身份验证的 Amazon Elastic
Container Service (Amazon ECS) 任务。
C. 使⽤ AWS Transfer 系列传输数据。创建⽤于身份提供商 (IdP) 身份验证的 AWS Lambda 函数。
D. 使⽤ AWS Storage Gateway 传输数据。创建 Amazon Cognito 身份池⽤于身份提供商 (IdP) 身份验证。
Question #458
A. Amazon EC2
B. AWS Lambda
C. Amazon RDS
Topic 1
⼀位解决⽅案架构师正在使⽤ Amazon API Gateway 设计⼀个⽤于现⾦返还服务的 REST API。该应⽤程序需要
1 GB 内存和 2 GB 存储空间⽤于计算。应⽤程序要求数据采⽤关系型格式。
以下哪两项 AWS 服务组合能够以最少的管理⼯作量满⾜这些要求？
D. Amazon DynamoDB
E. Amazon Elastic Kubernetes Services (Amazon EKS)
https://examlearn.online
[2026/05]
Question #459
Topic 1
⼀家公司使⽤ AWS Organizations 在多个 AWS 账户中运⾏⼯作负载。当公司创建标签时，标签策略会将部⻔标
签添加到 AWS 资源。
会计团队需要确定 Amazon EC2 的使⽤⽀出。会计团队必须确定哪些部⻔负责这些成本，⽽⽆需考虑 AWS 账
户。会计团队可以访问组织内所有 AWS 账户的 AWS Cost Explorer，并且需要访问 Cost Explorer 中的所有报
告。
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
A. 在“组织”管理帐户计费控制台中，激活⼀个名为“部⻔”的⽤户⾃定义成本分配标签。在“成本资源管理器”中
创建⼀个成本报告，按标签名称分组，并按 EC2 进⾏筛选。
B. 在组织管理帐户结算控制台中，激活⼀个名为“部⻔”的 AWS 定义成本分配标签。在成本资源管理器中创建
⼀个成本报告，按标签名称分组，并按 EC2 实例筛选。
C. 在“组织”成员帐户计费控制台中，激活⼀个名为“部⻔”的⽤户⾃定义成本分配标签。在“成本资源管理器”中
创建⼀个成本报告，按标签名称分组，并按 EC2 进⾏筛选。
D. 在组织成员账户的结算控制台中，激活⼀个名为“部⻔”的 AWS 定义成本分配标签。在成本资源管理器中创
建⼀个成本报告，按标签名称分组，并按 EC2 实例筛选。
Question #460
Topic 1
⼀家公司希望在其软件即服务 (SaaS) 应⽤ Salesforce 账户和 Amazon S3 之间安全地交换数据。该公司必须使
⽤ AWS Key Management Service (AWS KMS) 客户管理密钥 (CMK) 对静态数据进⾏加密，并对传输中的数据
进⾏加密。该公司已为 Salesforce 账户启⽤ API 访问权限。
A. 创建 AWS Lambda 函数，将数据从 Salesforce 安全地传输到 Amazon S3。
B. 创建⼀个 AWS Step Functions ⼯作流。定义将数据从 Salesforce 安全地传输到 Amazon S3 的任务。
C. 创建 Amazon AppFlow 流，以将数据从 Salesforce 安全地传输到 Amazon S3。
D. 为 Salesforce 创建⼀个⾃定义连接器，以便将数据从 Salesforce 安全地传输到 Amazon S3。
https://examlearn.online
[2026/05]
Question #461
Topic 1
⼀家公司正在单个 AWS 区域内开发⼀款移动游戏应⽤。该应⽤运⾏在⾃动扩展组中的多个 Amazon EC2 实例
上。公司将应⽤数据存储在 Amazon DynamoDB 中。应⽤通过 TCP 和 UDP 协议在⽤户和服务器之间进⾏通
信。该应⽤将在全球范围内使⽤。公司希望确保所有⽤户都能获得尽可能低的延迟。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Global Accelerator 创建加速器。在加速器终端节点后创建⼀个应⽤程序负载均衡器 (ALB)，该
ALB 使⽤ Global Accelerator 集成并监听 TCP 和 UDP 端⼝。更新⾃动扩展组，以在 ALB 上注册实例。
B. 使⽤ AWS Global Accelerator 创建加速器。在加速器终端节点后创建⼀个⽹络负载均衡器 (NLB)，该
NLB 使⽤ Global Accelerator 集成并监听 TCP 和 UDP 端⼝。更新 Auto Scaling 组，将实例注册到 NLB。
C. 创建⼀个 Amazon CloudFront 内容分发⽹络 (CDN) 终端节点。在该终端节点后创建⼀个⽹络负载均衡器
(NLB)，并监听 TCP 和 UDP 端⼝。更新⾃动扩展组，将实例注册到 NLB。更新 CloudFront，将 NLB ⽤作
源服务器。
D. 创建⼀个 Amazon CloudFront 内容分发⽹络 (CDN) 终端节点。在该终端节点后创建⼀个应⽤程序负载均
衡器 (ALB)，并监听 TCP 和 UDP 端⼝。更新⾃动扩展组，将实例注册到 ALB。更新 CloudFront，将 ALB
⽤作源服务器。
Question #462
指令。将数据库端点订阅到 SNS 主题。
Topic 1
⼀家公司有⼀个⽤于处理客户订单的应⽤程序。该公司将该应⽤程序托管在 Amazon EC2 实例上，并将订单保存
到 Amazon Aurora 数据库中。有时，当流量⾼峰期，⼯作负载⽆法⾜够快地处理订单。
解决⽅案架构师应该如何做才能以最快的速度可靠地将订单写⼊数据库？
A. 当流量⾼峰期，增加 EC2 实例的实例⼤⼩。向 Amazon Simple Notification Service (Amazon SNS) 写⼊
B. 将订单写⼊ Amazon Simple Queue Service (Amazon SQS) 队列。使⽤位于应⽤程序负载均衡器后⾯的
⾃动扩展组中的 EC2 实例，从 SQS 队列读取订单并将订单处理到数据库中。
C. 将指令写⼊ Amazon Simple Notification Service (Amazon SNS)。将数据库端点订阅到 SNS 主题。使⽤
位于应⽤程序负载均衡器后⾯的 Auto Scaling 组中的 EC2 实例从 SNS 主题读取数据。
D. 当 EC2 实例达到 CPU 阈值限制时，将订单写⼊ Amazon Simple Queue Service (Amazon SQS) 队列。
使⽤应⽤程序负载均衡器 (Application Load Balancer) 后⾯的 Auto Scaling 组中的 EC2 实例的计划扩展功
能，从 SQS 队列读取订单并将订单处理到数据库中。
https://examlearn.online
[2026/05]
Question #463
Topic 1
⼀家物联⽹公司即将推出⼀款内置传感器的床垫，⽤于收集⽤户睡眠数据。这些传感器会将数据发送到亚⻢逊S3
存储桶。每张床垫每晚⼤约会收集2MB的数据。该公司需要处理并汇总每张床垫的数据，且结果必须尽快提供。
数据处理需要1GB内存，并将在30秒内完成。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将 AWS Glue 与 Scala 作业⼀起使⽤
B. 将 Amazon EMR 与 Apache Spark 脚本结合使⽤
C. 将 AWS Lambda 与 Python 脚本结合使⽤
D. 将 AWS Glue 与 PySpark 作业⼀起使⽤
Question #464
哪种解决⽅案符合这些要求？
Topic 1
⼀家公司托管了⼀个在线购物应⽤程序，该应⽤程序将所有订单存储在 Amazon RDS for PostgreSQL 单可⽤区
数据库实例中。管理层希望消除单点故障，并要求解决⽅案架构师推荐⼀种⽆需更改应⽤程序代码即可最⼤限度
减少数据库停机时间的⽅案。
A. 通过修改数据库实例并指定 Multi-AZ 选项，将现有数据库实例转换为 Multi-AZ 部署。
B. 创建⼀个新的 RDS 多可⽤区部署。对当前 RDS 实例进⾏快照，并使⽤该快照还原新的多可⽤区部署。
C. 在另⼀个可⽤区中创建 PostgreSQL 数据库的只读副本。使⽤ Amazon Route 53 加权记录集将请求分配
到各个数据库。
D. 将 RDS for PostgreSQL 数据库放置在 Amazon EC2 Auto Scaling 组中，最⼩组⼤⼩为 2。使⽤ Amazon
Route 53 加权记录集将请求分配到各个实例。
https://examlearn.online
[2026/05]
Question #465
Topic 1
⼀家公司正在开发⼀款应⽤程序以满⾜客户需求。该公司希望将该应⽤程序部署在同⼀可⽤区内的多个基于
Amazon EC2 Nitro 的实例上。此外，该公司还希望该应⽤程序能够同时写⼊多个基于 EC2 Nitro 的实例中的多
个块存储卷，以提⾼应⽤程序的可⽤性。
哪种解决⽅案能够满⾜这些要求？
A. 将通⽤型 SSD (gp3) EBS 卷与 Amazon Elastic Block Store (Amazon EBS) 多连接功能结合使⽤
B. 将吞吐量优化型 HDD (st1) EBS 卷与 Amazon Elastic Block Store (Amazon EBS) 多连接结合使⽤
C. 将预置 IOPS SSD (io2) EBS 卷与 Amazon Elastic Block Store (Amazon EBS) 多连接结合使⽤
D. 将通⽤型 SSD (gp2) EBS 卷与 Amazon Elastic Block Store (Amazon EBS) 多连接功能结合使⽤
Question #466
⼀家公司设计了⼀个⽆状态的两层应⽤程序，该应⽤程序使⽤位于单个可⽤区的 Amazon EC2 实例和 Amazon
RDS 多可⽤区数据库实例。新公司管理层希望确保该应⽤程序具有⾼可⽤性。
解决⽅案架构师应该如何满⾜这⼀要求？
A. 配置应⽤程序以使⽤多可⽤区 EC2 ⾃动扩展，并创建应⽤程序负载均衡器。
B. 配置应⽤程序，使其对 EC2 实例进⾏快照并将其发送到不同的 AWS 区域。
Question #467
C. 配置应⽤程序以使⽤ Amazon Route 53 基于延迟的路由将请求传递给应⽤程序。
D. 配置 Amazon Route 53 规则以处理传⼊请求并创建多可⽤区应⽤程序负载均衡器
Topic 1
Topic 1
⼀家公司使⽤ AWS Organizations。其⼀个成员账户购买了计算资源节省计划。由于该成员账户内的⼯作负载发
⽣变化，该账户⽆法再享受计算资源节省计划承诺的全部优惠。该公司⽬前使⽤的计算能⼒不⾜其购买计算能⼒
的 50%。
A. 在购买了计算储蓄计划的会员帐户的帐户控制台的“账单⾸选项”部分中启⽤折扣共享。
B. 在公司组织管理帐户的帐户控制台的“账单⾸选项”部分启⽤折扣共享。
C. 将其他 AWS 账户中的额外计算⼯作负载迁移到具有计算节省计划的账户。
D. 在预留实例市场出售多余的储蓄计划承诺。
https://examlearn.online
[2026/05]
Question #468
Topic 1
⼀家公司正在开发⼀个微服务应⽤程序，该程序将为客户提供搜索⽬录。该公司必须使⽤ REST API 向⽤户展示
应⽤程序的前端。这些 REST API 必须访问该公司托管在私有 VPC ⼦⽹容器中的后端服务。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon API Gateway 设计 WebSocket API。将应⽤程序托管在 Amazon Elastic Container
Service (Amazon ECS) 的私有⼦⽹中。为 API Gateway 创建⼀个私有 VPC 链接以访问 Amazon ECS。
B. 使⽤ Amazon API Gateway 设计 REST API。将应⽤程序托管在 Amazon Elastic Container Service
(Amazon ECS) 的私有⼦⽹中。为 API Gateway 创建⼀个私有 VPC 链接以访问 Amazon ECS。
C. 使⽤ Amazon API Gateway 设计 WebSocket API。将应⽤程序托管在 Amazon Elastic Container
Service (Amazon ECS) 的私有⼦⽹中。创建⼀个安全组，允许 API Gateway 访问 Amazon ECS。
D. 使⽤ Amazon API Gateway 设计 REST API。将应⽤程序托管在 Amazon Elastic Container Service
(Amazon ECS) 的私有⼦⽹中。创建⼀个安全组，允许 API Gateway 访问 Amazon ECS。
Question #469
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司将收集到的原始数据存储在 Amazon S3 存储桶中。这些数据⽤于代表公司客户进⾏多种类型的分析。
所请求的分析类型决定了对 S3 对象的访问模式。
该公司⽆法预测或控制这种访问模式。该公司希望降低其 S3 成本。
A. 使⽤ S3 复制将不经常访问的对象迁移到 S3 标准版 - 不经常访问 (S3 标准版-IA)
B. 使⽤ S3 ⽣命周期规则将对象从 S3 标准版转换为标准版-不频繁访问版 (S3 标准版-IA)
C. 使⽤ S3 ⽣命周期规则将对象从 S3 标准版迁移到 S3 智能分层版
D. 使⽤ S3 清单识别并迁移尚未被访问的 S3 标准存储对象到 S3 智能分层存储对象。
https://examlearn.online
[2026/05]
Question #470
Topic 1
⼀家公司在拥有 IPv6 地址的 Amazon EC2 实例上托管了⼀些应⽤程序。这些应⽤程序必须通过互联⽹与其他外
部应⽤程序进⾏通信。但是，该公司的安全策略规定任何外部服务都不能主动连接到 EC2 实例。
解决⽅案架构师应该如何建议来解决这个问题？
A. 创建⼀个 NAT ⽹关，并将其设置为⼦⽹路由表的⽬标地址。
B. 创建⼀个互联⽹⽹关，并将其设置为⼦⽹路由表的⽬标地址。
C. 创建⼀个虚拟专⽤⽹关，并将其设置为⼦⽹路由表的⽬标地址。
D. 创建⼀个仅允许出站流量的互联⽹⽹关，并将其设置为⼦⽹路由表的⽬标地址。
Question #471
哪种解决⽅案能够满⾜这些要求？
A. 为 S3 存储桶启⽤ S3 智能分层
Topic 1
⼀家公司正在开发⼀个运⾏在 VPC 容器中的应⽤程序。该应⽤程序将数据存储在 Amazon S3 存储桶中并进⾏访
问。在开发阶段，该应⽤程序每天将在 Amazon S3 中存储和访问 1 TB 的数据。该公司希望最⼤限度地降低成
本，并尽可能避免流量通过互联⽹传输。
B. 为 S3 存储桶启⽤ S3 传输加速
C. 为 Amazon S3 创建⽹关 VPC 终端节点。将此终端节点与 VPC 中的所有路由表关联。
D. 在 VPC 中为 Amazon S3 创建接⼝终端节点。将此终端节点与 VPC 中的所有路由表关联。
https://examlearn.online
[2026/05]
Question #472
Topic 1
⼀家公司拥有⼀款移动聊天应⽤，其数据存储在 Amazon DynamoDB 上。⽤户希望尽可能低延迟地阅读新消
息。解决⽅案架构师需要设计⼀个对应⽤改动最⼩的最佳解决⽅案。
解决⽅案架构师应该选择哪种⽅法？
A. 为新的消息表配置 Amazon DynamoDB Accelerator (DAX)。更新代码以使⽤ DAX 端点。
B. 添加 DynamoDB 只读副本以处理增加的读取负载。更新应⽤程序，使其指向只读副本的读取端点。
C. 将 DynamoDB 中新消息表的读取容量单位数量增加⼀倍。继续使⽤现有的 DynamoDB 端点。
D. 向应⽤程序堆栈添加 Amazon ElastiCache for Redis 缓存。更新应⽤程序，使其指向 Redis 缓存端点，⽽
不是 DynamoDB。
Question #473
Topic 1
⼀家公司在应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2 实例上托管了⼀个⽹站。该⽹站提供静态内容。随
着⽹站流量的增⻓，该公司担⼼成本可能会增加。
A. 创建 Amazon CloudFront 分发，以在边缘位置缓存状态⽂件
B. 创建⼀个 Amazon ElastiCache 集群。将 ALB 连接到 ElastiCache 集群以提供缓存⽂件服务。
C. 创建⼀个 AWS WAF Web ACL 并将其与 ALB 关联。向 Web ACL 添加⼀条规则以缓存静态⽂件。
D. 在另⼀个 AWS 区域中创建第⼆个 ALB。将⽤户流量路由到最近的区域，以最⼤限度地降低数据传输成
本。
https://examlearn.online
[2026/05]
Question #474
Topic 1
⼀家公司在多个 AWS 区域中拥有多个 VPC，⽤于⽀持和运⾏与其他区域中的⼯作负载隔离的⼯作负载。由于最
近⼀项应⽤程序的上线需求，该公司的 VPC 必须与所有区域中的所有其他 VPC 通信。
哪种解决⽅案能够以最少的管理⼯作量满⾜这些要求？
A. 使⽤ VPC 对等连接管理单个区域内的 VPC 通信。使⽤跨区域的 VPC 对等连接管理 VPC 通信。
B. 使⽤跨区域的 AWS Direct Connect ⽹关连接跨区域的 VPC 并管理 VPC 通信。
C. 使⽤ AWS Transit Gateway 管理单个区域中的 VPC 通信，并使⽤ Transit Gateway 跨区域的对等连接来
管理 VPC 通信。
D. 使⽤ AWS PrivateLink 跨区域连接 VPC 并管理 VPC 通信
Question #475
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在设计⼀个容器化应⽤程序，该应⽤程序将使⽤ Amazon Elastic Container Service (Amazon
ECS)。该应⽤程序需要访问⼀个⾼度持久的共享⽂件系统，并且能够在 8 ⼩时恢复点⽬标 (RPO) 内将数据恢复
到另⼀个 AWS 区域。该⽂件系统需要在每个区域内的每个可⽤区中提供⼀个挂载⽬标。
解决⽅案架构师希望使⽤ AWS Backup 来管理到另⼀个区域的复制。
A. 采⽤多可⽤区部署的 Amazon FSx for Windows ⽂件服务器
B. 适⽤于 NetApp ONTAP 的 Amazon FSx 多可⽤区部署
C. 亚⻢逊弹性⽂件系统 (Amazon EFS) 标准存储类
D. Amazon FSx for OpenZFS
https://examlearn.online
[2026/05]
Question #476
⼀家公司预计近期将快速增⻓。解决⽅案架构师需要在 AWS 上配置现有⽤户并授予新⽤户权限。该解决⽅案架
构师决定创建 IAM 组。他将根据部⻔将新⽤户添加到相应的 IAM 组中。
以下哪项操作是授予新⽤户权限的最安全⽅式？
A. 应⽤服务控制策略 (SCP) 来管理访问权限
B. 创建权限最⼩的 IAM ⻆⾊。将这些⻆⾊附加到 IAM 组。
C. 创建⼀条授予最⼩权限原则的 IAM 策略。将该策略附加到 IAM 组。
D. 创建 IAM ⻆⾊。将这些⻆⾊与权限边界关联，该权限边界定义了最⼤权限。
Topic 1
https://examlearn.online
[2026/05]
Question #477
Topic 1
⼀个组需要拥有列出 Amazon S3 存储桶和从中删除对象的权限。管理员创建了以下 IAM 策略来授予对该存储桶
的访问权限，并将该策略应⽤到了该组。但该组仍然⽆法删除存储桶中的对象。公司遵循最⼩权限原则。
解决⽅案架构师应该在策略中添加哪条语句来纠正存储桶访问权限问题？
A. 
B. 
https://examlearn.online
[2026/05]
C. 
D. 
Question #478
哪种解决⽅案能够以最安全的⽅式满⾜这些要求？
Topic 1
⼀家律师事务所需要向公众共享信息。这些信息包含数百个必须公开可读的⽂件。在指定的未来⽇期之前，任何
⼈不得修改或删除这些⽂件。
A. 将所有⽂件上传到配置为静态⽹站托管的 Amazon S3 存储桶。在指定⽇期之前，授予任何访问该 S3 存储
桶的 AWS 主体只读 IAM 权限。
B. 创建⼀个新的 Amazon S3 存储桶，并启⽤ S3 版本控制。使⽤ S3 对象锁定，并根据指定⽇期设置保留期
限。将 S3 存储桶配置为静态⽹站托管。设置 S3 存储桶策略，允许对对象进⾏只读访问。
C. 创建⼀个新的 Amazon S3 存储桶，并启⽤ S3 版本控制。配置⼀个事件触发器，以便在对象被修改或删除
时运⾏ AWS Lambda 函数。配置该 Lambda 函数，使其将修改后的对象替换为私有 S3 存储桶中的原始版
本。
D. 将所有⽂件上传到配置为静态⽹站托管的 Amazon S3 存储桶。选择包含⽂件的⽂件夹。使⽤ S3 对象锁
定，并根据指定⽇期设置保留期限。授予所有访问该 S3 存储桶的 AWS 主体只读 IAM 权限。
https://examlearn.online
[2026/05]
Question #479
Topic 1
⼀家公司正在为其新⽹站构建基础设施原型，⽅法是⼿动配置必要的基础设施。该基础设施包括⼀个⾃动扩展
组、⼀个应⽤程序负载均衡器和⼀个 Amazon RDS 数据库。在配置经过全⾯验证后，该公司希望能够以⾃动化的
⽅式⽴即将该基础设施部署到两个可⽤区，⽤于开发和⽣产环境。
解决⽅案架构师应该提出怎样的建议来满⾜这些需求？
A. 使⽤ AWS Systems Manager 在两个可⽤区中复制和配置原型基础设施
B. 以原型基础设施为指导，将基础设施定义为模板。使⽤ AWS CloudFormation 部署基础设施。
C. 使⽤ AWS Config 记录原型基础设施中使⽤的资源清单。使⽤ AWS Config 将原型基础设施部署到两个可
⽤区。
D. 使⽤ AWS Elastic Beanstalk 并将其配置为使⽤对原型基础设施的⾃动引⽤，以便在两个可⽤区中⾃动部
署新环境。
Question #480
B. VPC 端点
Topic 1
⼀个业务应⽤程序托管在 Amazon EC2 上，并使⽤ Amazon S3 进⾏加密对象存储。⾸席信息安全官已指示，这
两个服务之间的任何应⽤程序流量都不得通过公共互联⽹传输。
解决⽅案架构师应使⽤哪项功能来满⾜合规性要求？
A. AWS 密钥管理服务 (AWS KMS)
C. 私有⼦⽹
D. 虚拟专⽤⽹关
https://examlearn.online
[2026/05]
Question #481
Topic 1
⼀家公司在 AWS 云上托管了⼀个三层 Web 应⽤程序。数据库层由⼀个多可⽤区 Amazon RDS for MySQL 服务
器构成，缓存层由 Amazon ElastiCache 构成。该公司希望采⽤⼀种缓存策略，当客户向数据库添加商品时，缓
存中的数据能够相应更新。缓存中的数据必须始终与数据库中的数据保持⼀致。
哪种解决⽅案能够满⾜这些要求？
A. 实现延迟加载缓存策略
B. 实现直写式缓存策略
C. 实现添加 TTL 缓存策略
D. 实施 AWS AppConfig 缓存策略
Question #482
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司希望将 100 GB 的历史数据从本地迁移到 Amazon S3 存储桶。该公司本地拥有 100 Mbps 的互联⽹连
接。该公司需要对传输到 S3 存储桶的数据进⾏加密。该公司会将新数据直接存储在 Amazon S3 中。
A. 使⽤ AWS CLI 中的 s3 sync 命令将数据直接移动到 S3 存储桶。
B. 使⽤ AWS DataSync 将数据从本地位置迁移到 S3 存储桶
C. 使⽤ AWS Snowball 将数据迁移到 S3 存储桶
D. 从本地位置到 AWS 设置 IPsec VPN。使⽤ AWS CLI 中的 s3 cp 命令将数据直接移动到 S3 存储桶。
https://examlearn.online
[2026/05]
Question #483
Topic 1
⼀家公司将⼀个基于 .NET 6 Framework 的 Windows 作业容器化，并部署在 Windows 容器中。该公司希望在
AWS 云上运⾏该作业。该作业每 10 分钟运⾏⼀次，每次运⾏时间在 1 分钟到 3 分钟之间。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 基于作业的容器镜像创建 AWS Lambda 函数。配置 Amazon EventBridge 每 10 分钟调⽤⼀次该函数。
B. 使⽤ AWS Batch 创建⼀个使⽤ AWS Fargate 资源的作业。配置作业调度，使其每 10 分钟运⾏⼀次。
C. 使⽤ AWS Fargate 上的 Amazon Elastic Container Service (Amazon ECS) 运⾏作业。根据作业的容器
镜像创建⼀个计划任务，每 10 分钟运⾏⼀次。
D. 使⽤ AWS Fargate 上的 Amazon Elastic Container Service (Amazon ECS) 运⾏作业。基于作业的容器
镜像创建⼀个独⽴任务。使⽤ Windows 任务计划程序每
10 分钟运⾏⼀次作业。
Question #484
为了满⾜这些要求，解决⽅案架构师应该推荐哪些操作组合？（选择两项。）
Cognito 身份验证。
Directory Service。
Service。
Topic 1
⼀家公司希望将多个独⽴的 AWS 账户迁移到整合的多账户架构。该公司计划为不同的业务部⻔创建多个新的
AWS 账户。该公司需要使⽤集中式企业⽬录服务来验证对这些 AWS 账户的访问权限。
A. 在 AWS Organizations 中创建⼀个新的组织，并启⽤所有功能。在该组织中创建新的 AWS 账户。
B. 设置 Amazon Cognito 身份池。配置 AWS IAM Identity Center（AW S 单点登录）以接受 Amazon
C. 配置服务控制策略 (SCP) 以管理 AWS 账户。将 AWS IAM 身份中⼼（AWS 单点登录）添加到 AWS
D. 在 AWS Organizations 中创建⼀个新组织。配置该组织的身份验证机制，使其直接使⽤ AWS Directory
E. 在组织内设置 AWS IAM 身份中⼼（AWS 单点登录）。配置 IAM 身份中⼼，并将其与公司企业⽬录服务集
成。
https://examlearn.online
[2026/05]
Question #485
Topic 1
⼀家公司正在寻找⼀种解决⽅案，可以将旧新闻视频存档存储在 AWS 中。该公司需要尽可能降低成本，并且很
少需要恢复这些⽂件。当需要这些⽂件时，必须在五分钟内可⽤。
哪种解决⽅案最具成本效益？
A. 将视频存档存储在 Amazon S3 Glacier 中，并使⽤加急检索。
B. 将视频存档存储在 Amazon S3 Glacier 中，并使⽤标准检索。
C. 将视频存档存储在 Amazon S3 标准-不频繁访问 (S3 标准-IA) 中。
D. 将视频存档存储在 Amazon S3 One Zone-Infrequent Access (S3 One Zone-IA) 中。
Question #486
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在 AWS 上构建⼀个三层应⽤程序。表示层将提供静态⽹站服务；逻辑层是⼀个容器化应⽤程序，⽤
于将数据存储在关系数据库中。该公司希望简化部署并降低运营成本。
A. 使⽤ Amazon S3 托管静态内容。使⽤ Amazon Elastic Container Service (Amazon ECS) 和 AWS
Fargate 来获取计算能⼒。使⽤托管的 Amazon RDS 集群作为数据库。
B. 使⽤ Amazon CloudFront 托管静态内容。使⽤ Amazon Elastic Container Service (Amazon ECS) 和
Amazon EC2 获取计算能⼒。使⽤托管的 Amazon RDS 集群作为数据库。
C. 使⽤ Amazon S3 托管静态内容。使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 AWS
Fargate 来获取计算能⼒。使⽤托管的 Amazon RDS 集群作为数据库。
D. 使⽤ Amazon EC2 预留实例托管静态内容。将 Amazon Elastic Kubernetes Service (Amazon EKS) 与
Amazon EC2 结合使⽤，以获得强⼤的计算能⼒。使⽤托管的 Amazon RDS 集群作为数据库。
https://examlearn.online
[2026/05]
Question #487
Topic 1
⼀家公司正在为其应⽤程序寻找存储解决⽅案。该解决⽅案必须具备⾼可⽤性和可扩展性。此外，该解决⽅案还
必须能够作为⽂件系统运⾏，并可通过原⽣协议被 AWS 和本地的多个 Linux 实例挂载，且没有最⼩容量要求。
该公司已为其本地⽹络到 VPC 的访问设置了站点到站点 VPN。
哪种存储解决⽅案能够满⾜这些要求？
A. Amazon FSx 多可⽤区部署
B. Amazon Elastic Block Store (Amazon EBS) 多连接卷
C. 具有多个挂载⽬标的 Amazon Elastic File System (Amazon EFS)
D. 具有单个挂载⽬标和多个访问点的亚⻢逊弹性⽂件系统 (Amazon EFS)
Question #488
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家成⽴四年的媒体公司正在使⽤ AWS Organizations 的所有功能来管理其 AWS 账户。据该公司财务团队称，
成员账户的账单信息不得对任何⼈开放，包括成员账户的根⽤户。
A. 将所有财务团队⽤户添加到 IAM 组。将名为“Billing”的 AWS 托管策略附加到该组。
B. 附加基于身份的策略，拒绝所有⽤户（包括 root ⽤户）访问账单信息。
C. 创建服务控制策略 (SCP) 以拒绝访问计费信息。将 SCP 附加到根组织单元 (OU)。
D. 将“组织的所有功能”功能集转换为“组织合并计费”功能集。
https://examlearn.online
[2026/05]
Question #489
Topic 1
⼀家电商公司在 AWS 云上运⾏⼀个应⽤程序，该应⽤程序与本地仓库解决⽅案集成。该公司使⽤ Amazon
Simple Notification Service (Amazon SNS) 将订单消息发送到本地 HTTPS 端点，以便仓库应⽤程序可以处理
订单。本地数据中⼼团队检测到部分订单消息未被接收。
解决⽅案架构师需要保留未送达的消息，并对其进⾏最多 14 天的分析。
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
A. 配置 Amazon SNS 死信队列，该队列具有 Amazon Kinesis Data Stream ⽬标，保留期为 14 天。
B. 在应⽤程序和 Amazon SNS 之间添加⼀个保留期为 14 天的 Amazon Simple Queue Service (Amazon
SQS) 队列。
C. 配置 Amazon SNS 死信队列，⽬标为 Amazon Simple Queue Service (Amazon SQS)，保留期为 14
天。
D. 配置 Amazon SNS 死信队列，该队列具有 Amazon DynamoDB ⽬标，并将 TTL 属性设置为保留期 14
天。
Question #490
哪种解决⽅案满⾜这些要求？
Topic 1
⼀家游戏公司使⽤ Amazon DynamoDB 存储⽤户信息，例如地理位置、玩家数据和排⾏榜。该公司需要配置持
续备份到 Amazon S3 存储桶，并尽可能减少代码量。备份不得影响应⽤程序的可⽤性，也不得影响为该表定义
的读取容量单位 (RCU)。
A. 使⽤ Amazon EMR 集群。创建⼀个 Apache Hive 作业，将数据备份到 Amazon S3。
B. 将数据直接从 DynamoDB 导出到 Amazon S3，并启⽤持续备份。为该表启⽤时间点恢复。
C. 配置 Amazon DynamoDB Streams。创建⼀个 AWS Lambda 函数来使⽤该流并将数据导出到 Amazon
S3 存储桶。
D. 创建⼀个 AWS Lambda 函数，定期将数据库表中的数据导出到 Amazon S3。启⽤该表的时点恢复功能。
https://examlearn.online
[2026/05]
Question #491
Topic 1
⼀位解决⽅案架构师正在为⼀家银⾏设计⼀个异步应⽤程序，⽤于处理信⽤卡数据验证请求。该应⽤程序必须安
全可靠，并且能够⾄少处理每个请求⼀次。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ AWS Lambda 事件源映射。将 Amazon Simple Queue Service (Amazon SQS) 标准队列设置为事件
源。使⽤ AWS Key Management Service (SSE-KMS) 进⾏加密。为 Lambda 执⾏⻆⾊添加 kms:Decrypt
权限。
B. 使⽤ AWS Lambda 事件源映射。使⽤ Amazon Simple Queue Service (Amazon SQS) FIFO 队列作为事
件源。使⽤ SQS 托管加密密钥 (SSE-SQS) 进⾏加密。为 Lambda 函数添 加加密密钥调⽤权限。
C. 使⽤ AWS Lambda 事件源映射。将 Amazon Simple Queue Service (Amazon SQS) FIFO 队列设置为事
件源。使⽤ AWS KMS 密钥 (SSE-KMS)。为 Lambda 执⾏⻆⾊添加 kms:Decrypt 权限。
D. 使⽤ AWS Lambda 事件源映射。将 Amazon Simple Queue Service (Amazon SQS) 标准队列设置为事
件源。使⽤ AWS KMS 密钥 (SSE-KMS) 进⾏加密。为 Lambda 函数添 加加密密钥调⽤权限。
Question #492
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
来配置 EC2 实例。
Topic 1
⼀家公司拥有多个⽤于开发⼯作的 AWS 账户。部分员⼯经常使⽤过⼤的 Amazon EC2 实例，导致公司开发账户
的年度预算超⽀。公司希望集中限制这些账户中 AWS 资源的创建。
A. 开发使⽤已批准的 EC2 创建流程的 AWS Systems Manager 模板。使⽤已批准的 Systems Manager 模板
B. 使⽤ AWS Organizations 将账户组织成组织单元 (OU)。定义并附加服务控制策略 (SCP) 以控制 EC2 实例
类型的使⽤。
C. 配置⼀条 Amazon EventBridge 规则，以便在创建 EC2 实例时调⽤ AWS Lambda 函数。停⽌不允许的
EC2 实例类型。
D. 为员⼯配置 AWS Service Catalog 产品，以便他们创建允许的 EC2 实例类型。确保员⼯只能通过 Service
Catalog 产品部署 EC2 实例。
https://examlearn.online
[2026/05]
Question #493
⼀家公司希望利⽤⼈⼯智能 (AI) 来评估其客户服务电话的质量。该公司⽬前处理四种不同语⾔的电话，包括英
语。未来，该公司还将提供更多语⾔选择。该公司⽬前没有⾜够的资源来定期维护机器学习 (ML) 模型。
该公司需要根据客户服务电话录⾳⽣成书⾯情感分析报告。客户服务电话录⾳⽂本必须翻译成英⽂。请问
以下哪些步骤组合能够满⾜这些要求？（选择三个。）
A. 使⽤ Amazon Comprehend 将⾳频录⾳翻译成英语。
B. 使⽤ Amazon Lex 创建书⾯情感分析报告。
C. 使⽤ Amazon Polly 将⾳频录⾳转换为⽂本。
D. 使⽤ Amazon Transcribe 将任何语⾔的⾳频录⾳转换为⽂本。
E. 使⽤亚⻢逊翻译将任何语⾔的⽂本翻译成英语。
F. 使⽤ Amazon Comprehend 创建情感分析报告。
Topic 1
https://examlearn.online
[2026/05]
Question #494
Topic 1
⼀家公司使⽤ Amazon EC2 实例托管其内部系统。在部署操作过程中，管理员尝试使⽤ AWS CLI 终⽌⼀个 EC2
实例。但是，管理员收到 403（访问被拒绝）错误消息。
管理员使⽤的 IAM ⻆⾊附加了以下 IAM 策略：
导致请求失败的原因是什么？
A. EC2 实例具有基于资源的策略，其中包含拒绝语句。
B. 保单声明中未明确指定委托⼈。
C. “操作”字段未授予终⽌ EC2 实例所需的操作权限。
D. 终⽌ EC2 实例的请求并⾮来⾃ CIDR 块 192.0.2.0/24 或 203.0.113.0/24。
https://examlearn.online
[2026/05]
Question #495
Topic 1
⼀家公司正在进⾏内部审计。该公司希望确保与其 AWS Lake Formation 数据湖关联的 Amazon S3 存储桶中的
数据不包含敏感的客户或员⼯数据。该公司希望发现个⼈身份信息 (PII) 或财务信息，包括护照号码和信⽤卡号
码。
哪种解决⽅案能够满⾜这些要求？
A. 在账户上配置 AWS Audit Manager。选择⽀付卡⾏业数据安全标准 (PCI DSS) 进⾏审计。
B. 在 S3 存储桶上配置 Amazon S3 清单 配置 Amazon Athena 查询清单。
C. 配置 Amazon Macie 以运⾏数据发现作业，该作业使⽤托管标识符来识别所需的数据类型。
D. 使⽤ Amazon S3 Select 对 S3 存储桶运⾏报告。
Question #496
Topic 1
⼀家公司使⽤本地服务器托管其应⽤程序。该公司⽬前⾯临存储容量不⾜的问题。这些应⽤程序同时使⽤了块存
储和NFS存储。该公司需要⼀个⾼性能的解决⽅案，该⽅案⽀持本地缓存，且⽆需重新设计其现有应⽤程序。
解决⽅案架构师应采取哪些措施组合来满⾜这些要求？（选择两项。）
A. 将 Amazon S3 作为⽂件系统挂载到本地服务器。
B. 部署 AWS Storage Gateway ⽂件⽹关来替换 NFS 存储。
C. 部署 AWS Snowball Edge 以在本地服务器上配置 NFS 挂载点。
D. 部署 AWS Storage Gateway 卷⽹关来替换块存储。
E. 部署 Amazon Elastic File System (Amazon EFS) 卷并将其挂载到本地服务器。
https://examlearn.online
[2026/05]
Question #497
Topic 1
⼀家公司拥有⼀项服务，该服务会从同⼀ AWS 区域中的 Amazon S3 存储桶读取和写⼊⼤量数据。该服务部署在
VPC 私有⼦⽹内的 Amazon EC2 实例上。该服务通过公有⼦⽹中的 NAT ⽹关与 Amazon S3 通信。然⽽，该公
司希望找到⼀种能够降低数据输出成本的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在公有⼦⽹中配置⼀个专⽤的 EC2 NAT 实例。配置私有⼦⽹的路由表，使该实例的弹性⽹络接⼝成为所有
S3 流量的⽬标地址。
B. 在私有⼦⽹中配置⼀个专⽤的 EC2 NAT 实例。配置公有⼦⽹的路由表，使所有 S3 流量都使⽤该实例的弹
性⽹络接⼝作为⽬标地址。
C. 配置 VPC ⽹关端点。配置私有⼦⽹的路由表，使所有 S3 流量都使⽤该⽹关端点作为路由。
D. 配置第⼆个 NAT ⽹关。配置私有⼦⽹的路由表，使所有 S3 流量都使⽤此 NAT ⽹关作为⽬标。
Question #498
Topic 1
⼀家公司使⽤ Amazon S3 将⾼分辨率图⽚存储在 S3 存储桶中。为了尽量减少应⽤程序的变更，该公司将图⽚
存储为 S3 对象的最新版本。该公司只需要保留图⽚的最新两个版本。
该公司希望降低成本，并且已将 S3 存储桶视为⼀项主要⽀出。
哪种解决⽅案能够在运营开销最⼩的情况下降低 S3 成本？
A. 使⽤ S3 ⽣命周期删除过期的对象版本，并保留最新的两个版本。
B. 使⽤ AWS Lambda 函数检查旧版本，并删除除最新两个版本之外的所有版本。
C. 使⽤ S3 批量操作删除⾮当前对象版本，仅保留最近的两个版本。
D. 停⽤ S3 存储桶的版本控制，并保留最近的两个版本。
https://examlearn.online
[2026/05]
Question #499
Topic 1
⼀家公司需要尽可能降低其 1 Gbps AWS Direct Connect 连接的成本。该公司的平均连接利⽤率低于 10%。解
决⽅案架构师必须推荐⼀种既能降低成本⼜不影响安全性的⽅案。
哪种⽅案能够满⾜这些要求？
A. 设置⼀个新的 1 Gbps Direct Connect 连接。将该连接共享给另⼀个 AWS 账户。
B. 在 AWS 管理控制台中设置⼀个新的 200 Mbps Direct Connect 连接。
C. 联系 AWS Direct Connect 合作伙伴订购 1 Gbps 连接。将该连接与其他 AWS 账户共享。
D. 联系 AWS Direct Connect 合作伙伴，为现有 AWS 账户订购 200 Mbps 托管连接。
Question #500
⼀家公司在本地部署了多台 Windows ⽂件服务器。该公司希望将其⽂件迁移并整合到 Amazon FSx for
Windows ⽂件服务器⽂件系统中。必须保留⽂件权限，以确保访问权限不变。
哪些解决⽅案能够满⾜这些要求？（选择两项。）
Topic 1
A. 在本地部署 AWS DataSync 代理。安排 DataSync 任务将数据传输到 FSx for Windows ⽂件服务器⽂件
系统。
B. 使⽤ AWS CLI 将每个⽂件服务器上的共享⽂件复制到 Amazon S3 存储桶中。安排 AWS DataSync 任务
将数据传输到 FSx for Windows ⽂件服务器⽂件系统。
C. 从每台⽂件服务器中移除硬盘驱动器。将硬盘驱动器运送⾄ AWS 以便导⼊到 Amazon S3。安排 AWS
DataSync 任务将数据传输到 FSx for Windows ⽂件服务器⽂件系统。
D. 订购⼀台 AWS Snowcone 设备。将设备连接到本地⽹络。在设备上启动 AWS DataSync 代理。安排
DataSync 任务，将数据传输到 FSx for Windows ⽂件服务器⽂件系统。
E. 订购⼀台 AWS Snowball Edge Storage Optimized 设备。将设备连接到本地⽹络。使⽤ AWS CLI 将数据
复制到该设备。将设备寄回 AWS 以便导⼊到 Amazon S3。安排 AWS DataSync 任务将数据传输到 FSx for
Windows ⽂件服务器⽂件系统。
https://examlearn.online
[2026/05]
Question #501
Topic 1
⼀家公司希望将客户⽀付数据导⼊其位于 Amazon S3 的数据湖中。该公司平均每分钟都会收到⽀付数据。该公
司希望实时分析这些⽀付数据，然后将数据导⼊数据湖。
哪种解决⽅案能够以最⾼的运营效率满⾜这些要求？
A. 使⽤ Amazon Kinesis Data Streams 摄取数据。使⽤ AWS Lambda 实时分析数据。
B. 使⽤ AWS Glue 导⼊数据。使⽤ Amazon Kinesis Data Analytics 实时分析数据。
C. 使⽤ Amazon Kinesis Data Firehose 摄取数据。使⽤ Amazon Kinesis Data Analytics 实时分析数据。
D. 使⽤ Amazon API Gateway 摄取数据。使⽤ AWS Lambda 实时分析数据。
Question #502
Topic 1
⼀家公司运营着⼀个⽹站，该⽹站使⽤基于 Amazon EC2 的内容管理系统 (CMS)。该 CMS 运⾏在单个 EC2 实
例上，并使⽤ Amazon Aurora MySQL 多可⽤区数据库实例作为数据层。⽹站图⽚存储在挂载于该 EC2 实例内
部的 Amazon Elastic Block Store (Amazon EBS) 卷上。
解决⽅案架构师应采取哪些措施组合来提⾼⽹站的性能和弹性？（选择两项。）
A. 将⽹站图⽚移动到挂载到每个 EC2 实例上的 Amazon S3 存储桶中。
B. 通过主 EC2 实例上的 NFS 共享来共享⽹站图⽚。将此共享挂载到其他 EC2 实例上。
C. 将⽹站图像移动到挂载到每个 EC2 实例上的 Amazon Elastic File System (Amazon EFS) ⽂件系统上。
D. 从现有 EC2 实例创建 Amazon 系统映像 (AMI)。使⽤该 AMI 在应⽤程序负载均衡器后⽅配置新实例，作
为⾃动扩展组的⼀部分。配置⾃动扩展组以⾄少维护两个实例。在 AWS Global Accelerator 中为⽹站配置加
速器。
E. 从现有 EC2 实例创建 Amazon 系统映像 (AMI)。使⽤该 AMI 在应⽤程序负载均衡器后⽅配置新实例，作
为⾃动扩展组的⼀部分。配置⾃动扩展组以⾄少维护两个实例。为⽹站配置 Amazon CloudFront 分发。
https://examlearn.online
[2026/05]
Question #503
Topic 1
⼀家公司运营着⼀项基础设施监控服务。该公司正在开发⼀项新功能，该功能将使该服务能够监控客户 AWS 账
户中的数据。这项新功能将调⽤客户账户中的 AWS API 来描述 Amazon EC2 实例并读取 Amazon CloudWatch
指标。
该公司应该如何以最安全的⽅式获取客户账户的访问权限？
A. 确保客户在其帐户中创建具有只读 EC2 和 CloudWatch 权限的 IAM ⻆⾊，并建⽴对公司帐户的信任策
略。
B. 创建⼀个⽆服务器 API，实现令牌⾃动售货机，为具有只读 EC2 和 CloudWatch 权限的⻆⾊提供临时
AWS 凭证。
C. 确保客户在其账户中创建⼀个具有只读 EC2 和 CloudWatch 权限的 IAM ⽤户。将客户的访问密钥和私钥
加密并存储在密钥管理系统中。
D. 确保客户在其账户中创建⼀个 Amazon Cognito ⽤户，并使⽤具有只读 EC2 和 CloudWatch 权限的 IAM
⻆⾊。将 Amazon Cognito ⽤户和密码加密并存储在密钥管理系统中。
Question #504
连接这些 VPC 的最⾼效⽅案是什么？
Topic 1
⼀家公司需要连接位于美国东部 1 区、跨越数百个 AWS 账户的多个 VPC。该公司的⽹络团队拥有⾃⼰的 AWS
账户来管理云⽹络。
A. 建⽴各 VPC 之间的 VPC 对等连接。更新各关联⼦⽹的路由表。
B. 在每个 VPC 中配置 NAT ⽹关和互联⽹⽹关，以便通过互联⽹连接各个 VPC。
C. 在⽹络团队的 AWS 账户中创建 AWS Transit Gateway。配置来⾃每个 VPC 的静态路由。
D. 在每个 VPC 中部署 VPN ⽹关。在⽹络团队的 AWS 账户中创建⼀个传输 VPC，⽤于连接到每个 VPC。
https://examlearn.online
[2026/05]
Question #505
Topic 1
⼀家公司使⽤ Amazon EC2 实例运⾏夜间批处理作业来处理数据。这些 EC2 实例运⾏在⼀个采⽤按需计费的⾃
动扩展组中。如果⼀个作业在⼀个实例上失败，另⼀个实例将重新处理该作业。批处理作业每天在当地时间凌晨
12:00 ⾄早上 6:00 之间运⾏。
哪种解决⽅案能够以最具成本效益的⽅式提供满⾜这些要求的 EC2 实例？
A. 购买 Amazon EC2 的 1 年期储蓄计划，该计划涵盖批处理作业使⽤的⾃动扩展组的实例系列。
B. 为批处理作业使⽤的⾃动扩展组中的特定实例类型和操作系统购买 1 年的预留实例。
C. 为⾃动扩展组创建⼀个新的启动模板。将实例设置为竞价型实例。设置基于 CPU 使⽤率的横向扩展策略。
D. 为⾃动扩展组创建⼀个新的启动模板。增加实例⼤⼩。设置基于 CPU 使⽤率的横向扩展策略。
Question #506
哪种解决⽅案能够以最佳的可扩展性满⾜这些要求？
Topic 1
⼀家社交媒体公司正在为其⽹站开发⼀项新功能，允许⽤户上传照⽚。该公司预计在⼤型活动期间，⽤户上传照
⽚的需求将显著增⻓，因此必须确保⽹站能够处理来⾃⽤户的⼤量上传流量。
A. 将⽤户浏览器中的⽂件上传到应⽤程序服务器。将⽂件传输到 Amazon S3 存储桶。
B. 配置 AWS Storage Gateway ⽂件⽹关。⽤户可以直接从浏览器将⽂件上传到⽂件⽹关。
C. 在应⽤程序中⽣成 Amazon S3 预签名 URL。直接从⽤户的浏览器将⽂件上传到 S3 存储桶。
D. 配置 Amazon Elastic File System (Amazon EFS) ⽂件系统。允许⽤户直接从浏览器将⽂件上传到该⽂件
系统。
https://examlearn.online
[2026/05]
Question #507
⼀家公司拥有⼀个⽤于旅⾏票务的 Web 应⽤程序。该应⽤程序基于⼀个运⾏在北美单个数据中⼼的数据库。该公
司希望扩展该应⽤程序，以服务全球⽤户。该公司需要将该应⽤程序部署到多个 AWS 区域。预订数据库更新的
平均延迟必须⼩于 1 秒。
该公司希望在多个区域独⽴部署其 Web 平台。但是，该公司必须维护⼀个全球⼀致的主预订数据库。
解决⽅案架构师应该推荐哪种解决⽅案来满⾜这些要求？
Topic 1
A. 将应⽤程序转换为使⽤ Amazon DynamoDB。使⽤全局表作为中⼼预订表。在每个区域部署中使⽤正确的
区域端点。
B. 将数据库迁移到 Amazon Aurora MySQL 数据库。在每个区域部署 Aurora 只读副本。在每个区域部署中
使⽤正确的区域终端节点来访问数据库。
C. 将数据库迁移到 Amazon RDS for MySQL 数据库。在每个区域中部署 MySQL 只读副本。在每个区域部署
中使⽤正确的区域终端节点来访问数据库。
D. 将应⽤程序迁移到 Amazon Aurora ⽆服务器数据库。在每个区域部署数据库实例。在每个区域部署中使⽤
正确的区域终端节点访问数据库。使⽤ AWS Lambda 函数处理每个区域中的事件流以同步数据库。
https://examlearn.online
[2026/05]
Question #508
Topic 1
⼀家公司已将多个 Microsoft Windows Server ⼯作负载迁移到运⾏于 us-west-1 区域的 Amazon EC2 实例。该
公司会根据需要⼿动备份这些⼯作负载以创建镜像。
如果 us-west-1 区域发⽣⾃然灾害，该公司希望能够快速地在 us-west-2 区域恢复⼯作负载。该公司希望 EC2
实例上的数据丢失时间不超过 24 ⼩时。此外，该公司还希望实现 EC2 实例备份的⾃动化。
哪些解决⽅案能够以最少的管理⼯作量满⾜这些要求？（选择两个。）
A. 创建⼀个基于 Amazon EC2 的 Amazon 系统映像 (AMI) ⽣命周期策略，以根据标签创建备份。将备份计
划为每天运⾏两次。按需复制映像。
B. 创建⼀个基于 Amazon EC2 的 Amazon 系统映像 (AMI) ⽣命周期策略，以根据标签创建备份。将备份计
划为每天运⾏两次。将备份配置到 us-west-2 区域。
C. 使⽤ AWS Backup 在 us-west-1 和 us-west-2 中创建备份存储库。根据标签值为 EC2 实例创建备份计
划。创建⼀个 AWS Lambda 函数，作为计划任务运⾏，将备份数据复制到 us-west-2。
D. 使⽤ AWS Backup 创建备份库。使⽤ AWS Backup 根据标签值为 EC2 实例创建备份计划。将副本⽬标位
置定义为 us-west-2。指定备份计划为每天运⾏两次。
E. 使⽤ AWS Backup 创建备份库。使⽤ AWS Backup 根据标签值为 EC2 实例创建备份计划。指定备份计划
为每天运⾏两次。按需复制到 us-west-2 分区。
Question #509
Topic 1
⼀家公司运⾏着⼀个两层架构的图像处理应⽤程序。该应⽤程序使⽤两个可⽤区，每个可⽤区包含⼀个公有⼦⽹
和⼀个私有⼦⽹。Web 层使⽤应⽤程序负载均衡器 (ALB) 来处理公有⼦⽹，⽽应⽤程序层则使⽤ Amazon EC2
实例来处理私有⼦⽹。
⽤户反映应⽤程序运⾏速度低于预期。对 Web 服务器⽇志⽂件的安全审计显示，该应⽤程序正从少数 IP 地址接
收数百万个⾮法请求。解决⽅案架构师需要在公司寻找更⻓久的解决⽅案的同时，解决当前的性能问题。
为了满⾜这⼀需求，解决⽅案架构师应该提出怎样的建议？
A. 修改 Web 层的⼊站安全组。添加⼀条拒绝规则，阻⽌正在消耗资源的 IP 地址。
B. 修改 Web 层⼦⽹的⽹络 ACL。添加⼀条⼊站拒绝规则，阻⽌正在消耗资源的 IP 地址访问。
C. 修改应⽤层的⼊站安全组。添加⼀条拒绝规则，阻⽌消耗资源的 IP 地址访问。
D. 修改应⽤层⼦⽹的⽹络访问控制列表 (ACL)。添加⼀条⼊站拒绝规则，阻⽌消耗资源的 IP 地址访问。
https://examlearn.online
[2026/05]
Question #510
Topic 1
⼀家全球营销公司在 ap-southeast-2 区域和 eu-west-1 区域运⾏应⽤程序。运⾏在 eu-west-1 区域 VPC 中的
应⽤程序需要与运⾏在 ap-southeast-2 区域 VPC 中的数据库进⾏安全通信。
哪种⽹络设计能够满⾜这些要求？
A. 在 eu-west-1 VPC 和 ap-southeast-2 VPC 之间创建 VPC 对等连接。在 eu-west-1 应⽤程序安全组中创
建⼊站规则，允许来⾃ ap-southeast-2 安全组中数据库服务器 IP 地址的流量。
B. 在 ap-southeast-2 VPC 和 eu-west-1 VPC 之间配置 VPC 对等连接。更新⼦⽹路由表。在 ap
southeast-2 数据库安全组中创建⼀条⼊站规则，该规则引⽤ eu-west-1 中应⽤服务器的安全组 ID。
C. 配置 ap-southeast-2 VPC 和 eu-west-1 VPC 之间的 VPC 对等连接，并更新⼦⽹路由表。在 ap
southeast-2 数据库安全组中创建⼀条⼊站规则，允许来⾃ eu-west-1 应⽤服务器 IP 地址的流量。
D. 在 eu-west-1 VPC 和 ap-southeast-2 VPC 之间建⽴对等连接，并创建⼀个传输⽹关。传输⽹关正确建⽴
对等连接并配置路由后，在数据库安全组中创建⼀个⼊站规则，该规则引⽤ eu-west-1 中应⽤服务器的安全
组 ID。
Question #511
Topic 1
⼀家公司正在开发⼀款使⽤ PostgreSQL 数据库模式的软件。该公司需要为开发⼈员配置多个开发环境和数据
库。平均⽽⾔，每个开发环境每天使⽤ 8 ⼩时⼯作⽇的⼀半时间。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 为每个开发环境配置其⾃身的 Amazon Aurora PostgreSQL 数据库
B. 为每个开发环境配置其⾃身的 Amazon RDS for PostgreSQL 单可⽤区数据库实例
C. 为每个开发环境配置其⾃身的 Amazon Aurora On-Demand PostgreSQL 兼容数据库
D. 使⽤ Amazon S3 ObjectSelect 为每个开发环境配置其⾃身的 Amazon S3 存储桶。
https://examlearn.online
[2026/05]
Question #512
Topic 1
⼀家公司使⽤ AWS Organizations，并按账户标记资源。该公司还使⽤ AWS Backup 来备份其 AWS 基础设施资
源。该公司需要备份所有 AWS 资源。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ AWS Config 识别所有未标记的资源。以编程⽅式标记已识别的资源。在备份计划中使⽤标签。
B. 使⽤ AWS Config 识别所有未运⾏的资源，并将这些资源添加到备份库中。
C. 要求所有 AWS 账户所有者审查其资源，以确定需要备份的资源。
D. 使⽤ Amazon Inspector 识别所有不合规的资源。
Question #513
解决⽅案架构师应该如何满⾜这些要求？
在 Amazon S3 存储桶中。
Topic 1
⼀家社交媒体公司希望允许⽤户在其托管于 AWS 云的应⽤程序中上传图⽚。该公司需要⼀个能够⾃动调整图⽚
⼤⼩的解决⽅案，以便图⽚能够在多种设备上显示。该应⽤程序全天都会遇到不可预测的流量模式。该公司正在
寻求⼀种⾼可⽤性且可扩展性极强的解决⽅案。
A. 创建⼀个托管在 Amazon S3 上的静态⽹站，该⽹站调⽤ AWS Lambda 函数来调整图像⼤⼩并将图像存储
B. 创建⼀个托管在 Amazon CloudFront 上的静态⽹站，该⽹站调⽤ AWS Step Functions 来调整图像⼤⼩
并将图像存储在 Amazon RDS 数据库中。
C. 创建⼀个动态⽹站，托管在运⾏于 Amazon EC2 实例上的 Web 服务器上。配置⼀个在 EC2 实例上运⾏的
进程，⽤于调整图像⼤⼩并将图像存储在 Amazon S3 存储桶中。
D. 创建⼀个动态⽹站，托管在可⾃动扩展的 Amazon Elastic Container Service (Amazon ECS) 集群上，该
⽹站会在 Amazon Simple Queue Service (Amazon SQS) 中创建⼀个调整⼤⼩作业。设置⼀个在 Amazon
EC2 实例上运⾏的图像调整⼤⼩程序来处理这些调整⼤⼩作业。
https://examlearn.online
[2026/05]
Question #514
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏微服务应⽤程序。为了提⾼可扩展性，该公司希望将该应⽤程序迁移到
Amazon Elastic Kubernetes Service (Amazon EKS) 集群。为了确保安全合规性，该公司必须配置 Amazon
EKS 控制平⾯，将端点私有访问权限设置为 true，将端点公共访问权限设置为 false。此外，该公司还必须将数
据平⾯放置在私有⼦⽹中。然⽽，该公司收到错误通知，提示节点⽆法加⼊集群。请问
哪种解决⽅案能够使节点加⼊集群？
A. 在 AWS Identity and Access Management (IAM) 中授予 AmazonEKSNodeRole IAM ⻆⾊所需的权限。
B. 创建接⼝ VPC 端点，允许节点访问控制平⾯。
C. 在公共⼦⽹中重新创建节点。限制 EC2 节点的安全组。
D. 允许节点安全组中的出站流量。
Question #515
B. ⽀持客户端和服务器端加密
⼀家公司正在将本地应⽤程序迁移到 AWS。该公司希望使⽤ Amazon Redshift 作为解决⽅案。
在这种情况下，哪些⽤例适合使⽤ Amazon Redshift？（选择三个。）
A. ⽀持数据 API，以便传统应⽤、容器化应⽤和事件驱动型应⽤访问数据。
C. 在指定时间段以及应⽤程序不活动时构建分析⼯作负载
D. 缓存数据以减轻后端数据库的压⼒
E. 全球扩展，以⽀持PB级数据和每分钟数千万次请求
F. 使⽤ AWS 管理控制台创建集群的辅助副本
Topic 1
https://examlearn.online
[2026/05]
Question #516
Topic 1
⼀家公司向客户提供 API 接⼝，以便客户检索其财务信息。该公司预计在⼀年中的⾼峰期，API 请求量会⼤幅增
加。
为了确保客户满意度，该公司要求 API 能够稳定响应并保持低延迟。该公司需要为 API 提供计算主机。
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 使⽤应⽤程序负载均衡器和 Amazon Elastic Container Service (Amazon ECS)。
B. 使⽤预置并发的 Amazon API Gateway 和 AWS Lambda 函数。
C. 使⽤应⽤程序负载均衡器和 Amazon Elastic Kubernetes Service (Amazon EKS) 集群。
D. 使⽤预留并发数的 Amazon API Gateway 和 AWS Lambda 函数。
Question #517
哪种解决⽅案能够以最⾼的运⾏效率满⾜此要求？
Topic 1
⼀家公司希望将所有 AWS Systems Manager Session Manager ⽇志发送到 Amazon S3 存储桶进⾏存档。
A. 在系统管理器控制台中启⽤ S3 ⽇志记录。选择⼀个 S3 存储桶来发送会话数据。
B. 安装 Amazon CloudWatch 代理。将所有⽇志推送到 CloudWatch ⽇志组。将⽇志从该组导出到 S3 存储
桶以进⾏归档。
C. 创建⼀个 Systems Manager ⽂档，将所有服务器⽇志上传到中央 S3 存储桶。使⽤ Amazon EventBridge
每天对账户中的所有服务器运⾏该 Systems Manager ⽂档。
D. 安装 Amazon CloudWatch 代理。将所有⽇志推送到 CloudWatch ⽇志组。创建⼀个 CloudWatch ⽇志
订阅，将所有传⼊的⽇志事件推送到 Amazon Kinesis Data Firehose 传输流。将 Amazon S3 设置为⽬标位
置。
https://examlearn.online
[2026/05]
Question #518
Topic 1
⼀个应⽤程序使⽤ Amazon RDS MySQL 数据库实例。RDS 数据库的磁盘空间即将耗尽。解决⽅案架构师希望在
不中断服务的情况下增加磁盘空间。
哪种解决⽅案能够以最少的投⼊满⾜这些要求？
A. 在 RDS 中启⽤存储⾃动扩缩容
B. 增加 RDS 数据库实例⼤⼩
C. 将 RDS 数据库实例存储类型更改为“预置 IOPS”。
D. 备份 RDS 数据库，增加存储容量，恢复数据库，并停⽌之前的实例
Question #519
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家咨询公司为全球客户提供专业服务。该公司提供解决⽅案和⼯具，帮助客户加快在 AWS 上收集和分析数据
的速度。该公司需要集中管理和部署⼀套通⽤的解决⽅案和⼯具，供客户⾃助使⽤。
A. 为客户创建 AWS CloudFormation 模板。
B. 为客户创建 AWS 服务⽬录产品。
C. 为客户创建 AWS Systems Manager 模板。
D. 为客户创建 AWS 配置项。
https://examlearn.online
[2026/05]
Question #520
Topic 1
⼀家公司正在设计⼀款新的 Web 应⽤程序，该应⽤程序将在 Amazon EC2 实例上运⾏。该应⽤程序将使⽤
Amazon DynamoDB 作为后端数据存储。应⽤程序流量不可预测。该公司预计应⽤程序对数据库的读写吞吐量将
处于中等到较⾼⽔平。该公司需要根据应⽤程序流量进⾏扩展。
哪种 DynamoDB 表配置能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ DynamoDB 标准表类配置 DynamoDB 的预置读写权限。将 DynamoDB ⾃动扩展设置为最⼤预定义
容量。
B. 使⽤ DynamoDB 标准表类将 DynamoDB 配置为按需模式。
C. 使⽤ DynamoDB 标准不频繁访问 (DynamoDB Standard-IA) 表类配置 DynamoDB 的预置读写权限。将
DynamoDB ⾃动扩展设置为最⼤预定义容量。
D. 使⽤ DynamoDB 标准不频繁访问 (DynamoDB Standard-IA) 表类，将 DynamoDB 配置为按需模式。
Question #521
哪种身份验证选项能够最安全地满⾜这些要求？
Topic 1
⼀家零售公司旗下拥有多个业务部⻔。每个业务部⻔的 IT 团队都管理着各⾃的 AWS 账户。每个团队账户都⾪属
于 AWS Organizations 中的⼀个组织。每个团队在其⾃身 AWS 账户中的 Amazon DynamoDB 表中监控产品库
存⽔平。
该公司正在将⼀个中央库存报告应⽤程序部署到共享的 AWS 账户中。该应⽤程序必须能够读取所有团队
DynamoDB 表中的条⽬。
A. 在清单应⽤程序账户中将 DynamoDB 与 AWS Secrets Manager 集成。配置应⽤程序以使⽤ Secrets
Manager 中的正确密钥进⾏身份验证并读取 DynamoDB 表。设置密钥轮换周期为每 30 天⼀次。
B. 在每个企业帐户中，创建⼀个具有编程访问权限的 IAM ⽤户。配置应⽤程序以使⽤正确的 IAM ⽤户访问密
钥 ID 和秘密访问密钥进⾏身份验证并读取 DynamoDB 表。每 30 天⼿动轮换⼀次 IAM 访问密钥。
C. 在每个业务帐户中，创建⼀个名为 BU_ROLE 的 IAM ⻆⾊，并为其配置策略，授予其访问 DynamoDB 表
的权限，以及信任策略，以信任库存应⽤程序帐户中的特定⻆⾊。在库存帐户中，创建⼀个名为 APP_ROLE
的⻆⾊，允许其访问 STS AssumeRole API 操作。配置应⽤程序以使⽤ APP_ROLE 并承担跨帐户⻆⾊
BU_ROLE 来读取 DynamoDB 表。
D. 将 DynamoDB 与 AWS Certificate Manager (ACM) 集成。⽣成身份证书以验证 DynamoDB 的身份。配
置应⽤程序以使⽤正确的证书进⾏身份验证并读取 DynamoDB 表。
https://examlearn.online
[2026/05]
Question #522
Topic 1
⼀家公司使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 运⾏容器应⽤程序。该公司的⼯作负载在⼀
天中并不稳定。该公司希望 Amazon EKS 能够根据⼯作负载进⾏横向扩展和缩减。
以下哪两项措施组合能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ AWS Lambda 函数调整 EKS 集群的⼤⼩。
B. 使⽤ Kubernetes Metrics Server 激活⽔平 Pod ⾃动扩缩容。
C. 使⽤ Kubernetes 集群⾃动扩缩器来管理集群中的节点数。
D. 使⽤ Amazon API Gateway 并将其连接到 Amazon EKS。
E. 使⽤ AWS App Mesh 观察⽹络活动。
Question #523
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
A. AWS AppSync 管道解析器
Topic 1
⼀家公司运⾏着⼀个基于微服务的⽆服务器 Web 应⽤程序。该应⽤程序必须能够从多个 Amazon DynamoDB 表
中检索数据。解决⽅案架构师需要使应⽤程序能够在不影响其基本性能的前提下检索数据。
B. Amazon CloudFront 与 Lambda@Edge 函数
C. 边缘优化的 Amazon API Gateway 与 AWS Lambda 函数
D. 使⽤ DynamoDB 连接器的 Amazon Athena 联合查询
https://examlearn.online
[2026/05]
Question #524
⼀家公司希望分析并排查与 IAM 权限相关的“访问被拒绝”错误和“未授权”错误。该公司已启⽤ AWS
CloudTrail。
哪种解决⽅案能够以最少的投⼊满⾜这些要求？
A. 使⽤ AWS Glue 并编写⾃定义脚本来查询 CloudTrail ⽇志中的错误。
B. 使⽤ AWS Batch 并编写⾃定义脚本来查询 CloudTrail ⽇志中的错误。
C. 使⽤ Amazon Athena 查询搜索 CloudTrail ⽇志，以识别错误。
D. 使⽤ Amazon QuickSight 搜索 CloudTrail ⽇志。创建仪表板以识别错误。
Question #525
Topic 1
Topic 1
⼀家公司希望将其现有的 AWS 使⽤成本添加到运营成本仪表板中。解决⽅案架构师需要推荐⼀种解决⽅案，使
该公司能够以编程⽅式访问其使⽤成本。该公司必须能够访问当年的成本数据并预测未来 12 个⽉的成本。
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 使⽤ AWS Cost Explorer API 的分⻚功能访问与使⽤成本相关的数据。
B. 使⽤可下载的 AWS Cost Explorer 报告 .csv ⽂件访问与使⽤成本相关的数据。
C. 配置 AWS Budgets 操作，通过 FTP 将使⽤成本数据发送给公司。
D. 创建 AWS Budgets 报告，⽤于收集使⽤成本数据。通过 SMTP 将数据发送给公司。
https://examlearn.online
[2026/05]
Question #526
Topic 1
解决⽅案架构师正在评估应⽤程序的弹性。他注意到，数据库管理员最近在⼀次扩展演练中，对应⽤程序的
Amazon Aurora PostgreSQL 数据库写⼊实例进⾏了故障转移。这次故障转移导致应⽤程序停机 3 分钟。
哪种解决⽅案能够在最⼤限度减少扩展演练停机时间的同时，将运维开销降⾄最低？
A. 在集群中创建更多 Aurora PostgreSQL 只读副本，以处理故障转移期间的负载。
B. 在同⼀ AWS 区域中设置辅助 Aurora PostgreSQL 集群。故障转移期间，更新应⽤程序以使⽤辅助集群的
写⼊端点。
C. 创建⼀个 Amazon ElastiCache for Memcached 集群来处理故障转移期间的负载。
D. 为数据库设置 Amazon RDS 代理。更新应⽤程序以使⽤代理终端节点。
Question #527
该公司希望进⾏全球扩张，并确保其应⽤程序的停机时间最短。
哪种解决⽅案能够提供最⾼的容错能⼒？
Topic 1
⼀家公司拥有⼀个区域性订阅式流媒体服务，该服务运⾏在单个 AWS 区域内。其架构由运⾏在 Amazon EC2 实
例上的 Web 服务器和应⽤服务器组成。这些 EC2 实例位于弹性负载均衡器 (ELB) 后的⾃动扩展组中。该架构还
包含⼀个跨多个可⽤区的 Amazon Aurora 全球数据库集群。
A. 扩展 Web 层和应⽤层的⾃动扩展组，以便在第⼆个区域的可⽤区中部署实例。使⽤ Aurora 全局数据库，
将数据库部署在主区域和第⼆个区域中。使⽤ Amazon Route 53 健康检查，并配置故障转移路由策略，将流
量转移到第⼆个区域。
B. 将 Web 层和应⽤层部署到第⼆个区域。在第⼆个区域添加⼀个跨区域的 Aurora PostgreSQL 副本。使⽤
Amazon Route 53 运⾏状况检查，并配置故障转移路由策略到第⼆个区域。根据需要将辅助副本提升为主副
本。
C. 将 Web 层和应⽤层部署到第⼆个区域。在第⼆个区域中创建 Aurora PostgreSQL 数据库。使⽤ AWS 数
据库迁移服务 (AWS DMS) 将主数据库复制到第⼆个区域。使⽤ Amazon Route 53 运⾏状况检查，并配置故
障转移路由策略以将流量路由到第⼆个区域。
D. 将 Web 层和应⽤层部署到第⼆个区域。使⽤ Amazon Aurora 全局数据库在主区域和第⼆个区域中部署数
据库。使⽤ Amazon Route 53 运⾏状况检查，并配置故障转移路由策略到第⼆个区域。根据需要将辅助区域
提升为主区域。
https://examlearn.online
[2026/05]
Question #528
Topic 1
⼀家数据分析公司希望将其批处理系统迁移到 AWS。该公司每天会定期通过 FTP 接收数千个⼩型数据⽂件。本
地部署的批处理作业会在夜间处理这些数据⽂件。然⽽，该批处理作业需要数⼩时才能完成。
该公司希望 AWS 解决⽅案能够尽快处理传⼊的数据⽂件，并且尽可能减少对发送⽂件的 FTP 客户端的更改。该
解决⽅案必须在⽂件处理成功后删除传⼊的数据⽂件。每个⽂件的处理时间需要 3-8 分钟。
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
A. 使⽤运⾏ FTP 服务器的 Amazon EC2 实例，将传⼊的⽂件作为对象存储在 Amazon S3 Glacier Flexible
Retrieval 中。在 AWS Batch 中配置作业队列。使⽤ Amazon EventBridge 规则调⽤该作业，每晚从 S3
Glacier Flexible Retrieval 处理对象。作业处理完对象后，删除这些对象。
B. 使⽤运⾏ FTP 服务器的 Amazon EC2 实例，将传⼊的⽂件存储在 Amazon Elastic Block Store (Amazon
EBS) 卷上。在 AWS Batch 中配置作业队列。使⽤ Amazon EventBridge 规则调⽤该作业，每晚从 EBS 卷处
理⽂件。作业处理完⽂件后，删除这些⽂件。
C. 使⽤ AWS Transfer Family 创建 FTP 服务器，将传⼊的⽂件存储在 Amazon Elastic Block Store
(Amazon EBS) 卷上。在 AWS Batch 中配置作业队列。当每个⽂件到达时，使⽤ Amazon S3 事件通知来调
⽤ AWS Batch 中的作业。作业处理完⽂件后，删除这些⽂件。
Question #529
哪种解决⽅案能够满⾜这些要求？
D. 使⽤ AWS Transfer Family 创建 FTP 服务器，将传⼊的⽂件存储到 Amazon S3 Standard 中。创建⼀个
AWS Lambda 函数来处理这些⽂件，并在处理完成后删除它们。使⽤ S3 事件通知在⽂件到达时调⽤
Lambda 函数。
Topic 1
⼀家公司正在将其⼯作负载迁移到 AWS。该公司数据库中包含交易数据和敏感数据。该公司希望使⽤ AWS 云解
决⽅案来提⾼数据库的安全性并降低运维开销。
A. 将数据库迁移到 Amazon EC2。使⽤ AWS Key Management Service (AWS KMS) AWS 托管密钥进⾏加
密。
B. 将数据库迁移到 Amazon RDS 配置静态加密。
C. 将数据迁移到 Amazon S3，使⽤ Amazon Macie 进⾏数据安全和保护
D. 将数据库迁移到 Amazon RDS。使⽤ Amazon CloudWatch Logs 来保障数据安全和保护。
https://examlearn.online
[2026/05]
Question #530
Topic 1
⼀家公司拥有⼀款⽀持 TCP 和 UDP 多⼈游戏的在线游戏应⽤。该公司使⽤ Amazon Route 53 将应⽤流量指向
位于不同 AWS 区域的多个⽹络负载均衡器 (NLB)。为了应对⽤户增⻓，该公司需要提升在线游戏的应⽤性能并
降低延迟。
哪种解决⽅案能够满⾜这些需求？
A. 在 NLB 前⾯添加 Amazon CloudFront 分发。增加 Cache-Control max-age 参数。
B. 将⽹络负载均衡器 (NLB) 替换为应⽤负载均衡器 (ALB)。配置 Route 53 使⽤基于延迟的路由。
C. 在 NLB 前⾯添加 AWS Global Accelerator。配置 Global Accelerator 端点以使⽤正确的监听器端⼝。
D. 在 NLB 后⾯添加 Amazon API Gateway 端点。启⽤ API 缓存。针对不同阶段重写⽅法缓存。
Question #531
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
Topic 1
⼀家公司需要集成第三⽅数据源。当有新数据可供使⽤时，数据源会发送 Webhook 通知外部服务。开发⼈员编
写了⼀个 AWS Lambda 函数，⽤于在公司收到 Webhook 回调时检索数据。开发⼈员必须使第三⽅能够调⽤此
Lambda 函数。
A. 为 Lambda 函数创建函数 URL。将 Lambda 函数 URL 提供给第三⽅以⽤于 webhook。
B. 在 Lambda 函数前⾯部署应⽤程序负载均衡器 (ALB)。将 ALB URL 提供给第三⽅以⽤于 webhook。
C. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。将该主题附加到 Lambda 函数。将
SNS 主题的公共主机名提供给第三⽅，以便进⾏ Webhook 通信。
D. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。将该队列附加到 Lambda 函数。将 SQS
队列的公共主机名提供给第三⽅，以便进⾏ Webhook 连接。
https://examlearn.online
[2026/05]
Question #532
Topic 1
⼀家公司在 AWS 区域内运⾏着⼀个⼯作负载。客户通过 Amazon API Gateway REST API 连接并访问该⼯作负
载。该公司使⽤ Amazon Route 53 作为其 DNS 提供商。该公司希望为所有客户提供独⽴且安全的 URL。
以下哪三项步骤组合能够以最⾼的运营效率满⾜这些要求？（选择三项。）
A. 在域名注册商处注册所需的域名。在 Route 53 托管区域中创建通配符⾃定义域名，并在指向 API ⽹关端
点的区域中进⾏记录。
B. 请求与 AWS Certificate Manager (ACM) 中不同区域的域匹配的通配符证书。
C. 根据 Route 53 的要求，为每个客户创建托管区域。创建指向 API ⽹关端点的区域记录。
D. 在同⼀区域的 AWS Certificate Manager (ACM) 中，请求与⾃定义域名匹配的通配符证书。
E. 在 API ⽹关中为每个客户创建多个 API 端点。
F. 在 API Gateway 中为 REST API 创建⾃定义域名。从 AWS Certificate Manager (ACM) 导⼊证书。
Question #533
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司将数据存储在 Amazon S3 中。根据相关规定，数据不得包含个⼈身份信息 (PII)。该公司最近发现 S3
存储桶中存在⼀些包含 PII 的对象。该公司需要⾃动检测 S3 存储桶中的 PII，并通知其安全团队。
A. 使⽤ Amazon Macie。创建 Amazon EventBridge 规则，从 Macie 的发现结果中筛选出 SensitiveData 事
件类型，并向安全团队发送 Amazon Simple Notification Service (Amazon SNS) 通知。
B. 使⽤ Amazon GuardDuty。创建 Amazon EventBridge 规则，从 GuardDuty 的发现结果中筛选出
CRITICAL 事件类型，并向安全团队发送 Amazon Simple Notification Service (Amazon SNS) 通知。
C. 使⽤ Amazon Macie。创建 Amazon EventBridge 规则，从 Macie 的发现结果中筛选出
SensitiveData:S3Object/Personal 事件类型，并向安全团队发送 Amazon Simple Queue Service (Amazon
SQS) 通知。
D. 使⽤ Amazon GuardDuty。创建 Amazon EventBridge 规则，从 GuardDuty 的发现结果中筛选出
CRITICAL 事件类型，并向安全团队发送 Amazon Simple Queue Service (Amazon SQS) 通知。
https://examlearn.online
[2026/05]
Question #534
Topic 1
⼀家公司希望为其多个 AWS 账户构建⽇志解决⽅案。该公司⽬前将所有账户的⽇志存储在⼀个集中式账户中。
该公司已在该集中式账户中创建了⼀个 Amazon S3 存储桶，⽤于存储 VPC 流⽇志和 AWS CloudTrail ⽇志。所
有⽇志必须保持⾼可⽤性 30 天，以便进⾏频繁分析；之后再保留 60 天⽤于备份；并在创建 90 天后删除。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在对象创建 30 天后将其迁移到 S3 标准存储类。编写⼀个过期操作，指示 Amazon S3 在 90 天后删除对
象。
B. 在对象创建 30 天后，将其迁移到 S3 标准-不频繁访问 (S3 Standard-IA) 存储类。90 天后，将所有对象
迁移到 S3 Glacier 灵活检索存储类。编写⼀个过期操作，指示 Amazon S3 在 90 天后删除对象。
C. 在对象创建 30 天后，将其迁移到 S3 Glacier 灵活检索存储类。编写⼀个过期操作，指示 Amazon S3 在
90 天后删除对象。
D. 在对象创建 30 天后，将其迁移到 S3 单区域低频访问 (S3 One Zone-IA) 存储类。90 天后，将所有对象
迁移到 S3 Glacier 灵活检索存储类。编写⼀个过期操作，指示 Amazon S3 在 90 天后删除对象。
Question #535
哪种解决⽅案能够满⾜这些要求？
换和存储 Amazon EKS 中的所有密钥。
KMS 密钥加密。
Topic 1
⼀家公司正在为其⼯作负载构建 Amazon Elastic Kubernetes Service (Amazon EKS) 集群。存储在 Amazon
EKS 中的所有密钥都必须在 Kubernetes etcd 键值存储中进⾏加密。
A. 创建⼀个新的 AWS Key Management Service (AWS KMS) 密钥。使⽤ AWS Secrets Manager 管理、轮
B. 创建新的 AWS Key Management Service (AWS KMS) 密钥。在 Amazon EKS 集群上启⽤ Amazon EKS
C. 使⽤默认选项创建 Amazon EKS 集群。使⽤ Amazon Elastic Block Store (Amazon EBS) 容器存储接⼝
(CSI) 驱动程序作为附加组件。
D. 创建别名为 /aws/ebs 的新 AWS Key Management Service (AWS KMS) 密钥。为该账户启⽤默认的
Amazon Elastic Block Store (Amazon EBS) 卷加密。
https://examlearn.online
[2026/05]
Question #536
Topic 1
⼀家公司希望为数据科学家提供对公司⽣产环境 Amazon RDS for PostgreSQL 数据库的近实时只读访问权限。
该数据库⽬前配置为单可⽤区 (Single-AZ) 数据库。数据科学家使⽤复杂的查询，但这些查询不会影响⽣产数据
库。该公司需要⼀个⾼可⽤性的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在维护窗⼝期内扩展现有⽣产数据库，为数据科学家提供⾜够的处理能⼒。
B. 将部署环境从单可⽤区 (Single-AZ) 更改为多可⽤区 (Multi-AZ) 实例部署，并配备⼀个容量更⼤的备⽤实
例。为数据科学家提供对该备⽤实例的访问权限。
C. 将部署环境从单可⽤区 (Single-AZ) 更改为多可⽤区 (Multi-AZ)。为数据科学家提供两个额外的只读副
本。
D. 将部署环境从单可⽤区 (Single-AZ) 改为多可⽤区 (Multi-AZ) 集群部署，并配备两个可读备⽤实例。为数
据科学家提供读取端点。
Question #537
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 AWS 云上运⾏⼀个三层 Web 应⽤程序，该应⽤程序跨三个可⽤区运⾏。该应⽤程序架构包含⼀个应
⽤程序负载均衡器、⼀个⽤于托管⽤户会话状态的 Amazon EC2 Web 服务器以及⼀个运⾏在 EC2 实例上的
MySQL 数据库。该公司预计应⽤程序流量会突然增加。该公司希望能够扩展以满⾜未来的应⽤程序容量需求，并
确保在所有三个可⽤区中都具有⾼可⽤性。
A. 将 MySQL 数据库迁移到 Amazon RDS for MySQL，并部署多可⽤区数据库集群。使⽤ Amazon
ElastiCache for Redis 的⾼可⽤性功能来存储会话数据并缓存读取操作。将 Web 服务器迁移到位于三个可⽤
区的⾃动扩展组。
B. 将 MySQL 数据库迁移到 Amazon RDS for MySQL，并部署多可⽤区数据库集群。使⽤ Amazon
ElastiCache for Memcached 的⾼可⽤性功能来存储会话数据和缓存读取操作。将 Web 服务器迁移到位于三
个可⽤区的⾃动扩展组。
C. 将 MySQL 数据库迁移到 Amazon DynamoDB。使⽤ DynamoDB Accelerator (DAX) 缓存读取操作。将
会话数据存储在 DynamoDB 中。将 Web 服务器迁移到位于三个可⽤区的⾃动扩展组。
D. 将 MySQL 数据库迁移到位于单个可⽤区的 Amazon RDS for MySQL。使⽤⾼可⽤性的 Amazon
ElastiCache for Redis 来存储会话数据并缓存读取操作。将 Web 服务器迁移到位于三个可⽤区的 Auto
Scaling 组。
https://examlearn.online
[2026/05]
Question #538
Topic 1
⼀家全球视频流媒体公司使⽤ Amazon CloudFront 作为内容分发⽹络 (CDN)。该公司希望分阶段在多个国家/地
区推出内容。该公司需要确保内容发布国家/地区以外的⽤户⽆法观看这些内容。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤允许列表为 CloudFront 中的内容添加地理位置限制。设置⾃定义错误消息。
B. 为受限内容设置新的 URL。使⽤签名 URL 和 cookie 进⾏授权访问。设置⾃定义错误消息。
C. 对公司分发的内容数据进⾏加密。设置⾃定义错误消息。
D. 为受限内容创建新的 URL。为已签名的 URL 设置限时访问策略。
Question #539
哪种解决⽅案能够满⾜这些要求？
主动/主动设置。
Topic 1
⼀家公司希望利⽤ AWS 云来改进其本地灾难恢复 (DR) 配置。该公司的核⼼⽣产业务应⽤程序使⽤ Microsoft
SQL Server Standard，该数据库运⾏在虚拟机 (VM) 上。该应⽤程序的恢复点⽬标 (RPO) 为 30 秒或更短，恢
复时间⽬标 (RTO) 为 60 分钟。灾难恢复解决⽅案需要尽可能降低成本。
A. 使⽤ Microsoft SQL Server Enterprise 和 Always On 可⽤性组，在本地服务器和 AWS 之间配置多站点
B. 在 AWS 上为 SQL Server 数据库配置热备 Amazon RDS。配置 AWS 数据库迁移服务 (AWS DMS) 以使⽤
变更数据捕获 (CDC)。
C. 使⽤配置为将磁盘更改复制到 AWS 的 AWS Elastic Disaster Recovery 作为指示灯。
D. 使⽤第三⽅备份软件每晚进⾏备份。将另⼀组备份存储在 Amazon S3 中。
https://examlearn.online
[2026/05]
Question #540
Topic 1
⼀家公司拥有⼀个本地服务器，该服务器使⽤ Oracle 数据库来处理和存储客户信息。该公司希望使⽤ AWS 数据
库服务来提⾼可⽤性并提升应⽤程序性能。此外，该公司还希望将报表功能从其主数据库系统卸载。
哪种解决⽅案能够以最⾼效的⽅式满⾜这些需求？
A. 使⽤ AWS 数据库迁移服务 (AWS DMS) 在多个 AWS 区域中创建 Amazon RDS 数据库实例。将报表功能
指向与主数据库实例不同的独⽴数据库实例。
B. 使⽤ Amazon RDS 在单可⽤区部署中创建 Oracle 数据库。在与主数据库实例相同的可⽤区中创建只读副
本。将报表功能定向到该只读副本。
C. 使⽤部署在多可⽤区集群中的 Amazon RDS 创建 Oracle 数据库。指示报表功能使⽤集群部署中的读取器
实例。
D. 使⽤部署在多可⽤区实例环境中的 Amazon RDS 创建 Amazon Aurora 数据库。将报表功能定向到读取器
实例。
Question #541
以下哪三项措施组合能够以最具成本效益的⽅式满⾜这些要求？（选择三项。）
Lambda 函数。
Topic 1
⼀家公司想在 AWS 上构建⼀个 Web 应⽤程序。客户对⽹站的访问请求不可预测，并且可能⻓时间处于空闲状
态。只有⽀付了订阅费的客户才能登录并使⽤该 Web 应⽤程序。
A. 创建⼀个 AWS Lambda 函数，⽤于从 Amazon DynamoDB 中检索⽤户信息。创建⼀个 Amazon API
Gateway 端点，⽤于接收 RESTful API 请求。将 API 调⽤发送到 Lambda 函数。
B. 在应⽤程序负载均衡器后创建⼀个 Amazon Elastic Container Service (Amazon ECS) 服务，⽤于从
Amazon RDS 检索⽤户信息。创建⼀个 Amazon API Gateway 端点以接收 RESTful API。将 API 调⽤发送到
C. 创建⼀个 Amazon Cognito ⽤户池来验证⽤户身份。
D. 创建 Amazon Cognito 身份池以验证⽤户身份。
E. 使⽤ AWS Amplify 提供前端 Web 内容，包括 HTML、CSS 和 JS。使⽤集成的 Amazon CloudFront 配
置。
F. 使⽤ Amazon S3 静态⽹站托管服务，并配合 PHP、CSS 和 JS 使⽤ Amazon CloudFront 来提供前端⽹站
内容。
https://examlearn.online
[2026/05]
Question #542
Topic 1
⼀家媒体公司使⽤ Amazon CloudFront 分发通过互联⽹提供内容。该公司希望只有⾼级客户才能访问媒体流和
⽂件内容。该公司将所有内容存储在 Amazon S3 存储桶中。该公司还根据客户的特定需求提供按需内容，例如
电影租赁或⾳乐下载。
哪种解决⽅案能够满⾜这些要求？
A. 为⾼级客户⽣成并提供 S3 签名 cookie。
B. 为⾼级客户⽣成并提供 CloudFront 签名 URL。
C. 使⽤源访问控制 (OAC) 来限制⾮⾼级客户的访问。
D. ⽣成并激活字段级加密，以阻⽌⾮⾼级客户。
Question #543
以下哪两项措施可以满⾜这些要求？（选择两项。）
Savings Plan。
Topic 1
⼀家公司在多个独⽴的 AWS 账户中运⾏ Amazon EC2 实例。该公司最近购买了 Savings Plan 计划。由于公司
业务需求的变化，该公司已停⽤了⼤量 EC2 实例。该公司希望将其 Savings Plan 折扣⽤于其他 AWS 账户。
A. 从 管理账户的 AWS 账户管理控制台中，在账单⾸选项部分启⽤折扣共享。
B. 在购买现有储蓄计划的账户的 AWS 账户管理控制台中，从账单⾸选项部分启⽤折扣共享。包含所有账户。
C. 从 AWS Organizations 管理账户，使⽤ AWS Resource Access Manager (AWS RAM) 与其他账户共享
D. 在新的付款⼈账户中，于 AWS Organizations 中创建⼀个组织。从管理账户邀请其他 AWS 账户加⼊该组
织。
E. 在现有 AWS 账户中，使⽤现有的 EC2 实例和 Savings Plan，在 AWS Organizations 中创建⼀个组织。
通过管理账户邀请其他 AWS 账户加⼊该组织。
https://examlearn.online
[2026/05]
Question #544
Topic 1
⼀家零售公司使⽤区域性的亚⻢逊 API Gateway API 作为其公共 REST API。该 API Gateway 端点是⼀个⾃定义
域名，指向亚⻢逊 Route 53 别名记录。解决⽅案架构师需要创建⼀个⽅案，以尽可能减少对客户的影响和数据
丢失，从⽽发布新版本的 API。
哪个⽅案能够满⾜这些要求？
A. 为 API ⽹关创建⾦丝雀发布部署阶段。部署最新 API 版本。将适当⽐例的流量导向⾦丝雀阶段。API 验证
通过后，将⾦丝雀阶段升级到⽣产阶段。
B. 使⽤ OpenAPI YAML ⽂件格式的新版 API 创建⼀个新的 API ⽹关端点。在 API ⽹关中使⽤合并模式的导
⼊更新操作将新版 API 导⼊到 API 中。将新版 API 部署到⽣产环境。
C. 创建⼀个新的 API ⽹关端点，使⽤ OpenAPI JSON ⽂件格式的新版本 API。在 API ⽹关中使⽤覆盖模式的
导⼊更新操作，将新版本的 API 部署到⽣产环境。
D. 创建⼀个新的 API ⽹关端点，并使⽤新版本的 API 定义。为新的 API ⽹关 API 创建⾃定义域名。将 Route
53 别名记录指向新的 API ⽹关 API ⾃定义域名。
Question #545
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望在主⽹站⽆法访问时，将⽤户引导⾄备⽤静态错误⻚⾯。主⽹站的 DNS 记录托管在 Amazon
Route 53 上。该域名指向应⽤程序负载均衡器 (ALB)。该公司需要⼀个能够最⼤限度减少变更和基础设施开销的
解决⽅案。
A. 更新 Route 53 记录，使⽤延迟路由策略。在记录中添加⼀个托管在 Amazon S3 存储桶中的静态错误⻚
⾯，以便将流量发送到响应速度最快的终端节点。
B. 设置 Route 53 主备故障转移配置。当 Route 53 健康检查确定 ALB 端点不健康时，将流量定向到托管在
Amazon S3 存储桶中的静态错误⻚⾯。
C. 设置 Route 53 主动-主动配置，将 ALB 和托管静态错误⻚⾯的 Amazon EC2 实例作为终端节点。配置
Route 53，使其仅在 ALB 的运⾏状况检查失败时才向该实例发送请求。
D. 更新 Route 53 记录，使⽤多值应答路由策略。创建健康检查。如果健康检查通过，则将流量定向到⽹站。
如果健康检查未通过，则将流量定向到托管在 Amazon S3 上的静态错误⻚⾯。
https://examlearn.online
[2026/05]
Question #546
Topic 1
最近对⼀家公司IT⽀出进⾏的分析凸显了降低备份成本的必要性。该公司⾸席信息官希望简化本地备份基础设
施，并通过取消使⽤物理备份磁带来降低成本。该公司必须保留对本地备份应⽤程序和⼯作流程的现有投资。
解决⽅案架构师应该提出什么建议？
A. 设置 AWS Storage Gateway 以使⽤ NFS 接⼝与备份应⽤程序连接。
B. 设置 Amazon EFS ⽂件系统，使其通过 NFS 接⼝与备份应⽤程序连接。
C. 设置⼀个 Amazon EFS ⽂件系统，该⽂件系统使⽤ iSCSI 接⼝与备份应⽤程序连接。
D. 设置 AWS Storage Gateway 以使⽤ iSCSI 虚拟磁带库 (VTL) 接⼝与备份应⽤程序连接。
Question #547
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
Topic 1
⼀家公司在不同地点部署了数据采集传感器。这些数据采集传感器会向公司传输⼤量数据。该公司希望在 AWS
上构建⼀个平台，⽤于接收和处理海量流数据。该解决⽅案必须具有可扩展性，并⽀持近实时数据采集。公司还
必须将数据存储在 Amazon S3 中，以便⽇后⽣成报告。
A. 使⽤ Amazon Kinesis Data Firehose 将流式数据传输到 Amazon S3。
B. 使⽤ AWS Glue 将流式数据传输到 Amazon S3。
C. 使⽤ AWS Lambda 传递流数据并将数据存储到 Amazon S3。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将流式数据传输到 Amazon S3。
https://examlearn.online
[2026/05]
Question #548
Topic 1
⼀家公司为其财务、数据分析和开发部⻔分别开设了独⽴的 AWS 账户。出于成本和安全⽅⾯的考虑，该公司希
望控制每个 AWS 账户可以使⽤的服务。
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 使⽤ AWS Systems Manager 模板来控制每个部⻔可以使⽤哪些 AWS 服务。
B. 在 AWS Organizations 中为每个部⻔创建组织单元 (OU)。将服务控制策略 (SCP) 附加到 OU。
C. 使⽤ AWS CloudFormation ⾃动配置每个部⻔可以使⽤的 AWS 服务。
D. 在 AWS 账户的 AWS 服务⽬录中设置产品列表，以管理和控制特定 AWS 服务的使⽤。
Question #549
解决⽅案架构师应该如何做才能满⾜这些要求？
Topic 1
⼀家公司为其电⼦商务⽹站创建了⼀个多层应⽤程序。该⽹站使⽤位于公有⼦⽹中的应⽤程序负载均衡器、位于
公有⼦⽹中的 Web 层以及托管在私有⼦⽹ Amazon EC2 实例上的 MySQL 集群。MySQL 数据库需要检索由第
三⽅提供商托管在互联⽹上的产品⽬录和定价信息。解决⽅案架构师必须制定⼀个策略，在不增加运营开销的情
况下最⼤限度地提⾼安全性。
A. 在 VPC 中部署 NAT 实例。将所有基于互联⽹的流量路由到 NAT 实例。
B. 在公有⼦⽹中部署 NAT ⽹关。修改私有⼦⽹路由表，将所有出境互联⽹的流量导向 NAT ⽹关。
C. 配置互联⽹⽹关并将其连接到 VP。修改私有⼦⽹路由表，将出站互联⽹流量定向到互联⽹⽹关。
D. 配置虚拟专⽤⽹关并将其附加到 VPC。修改私有⼦⽹路由表，将出站互联⽹流量定向到虚拟专⽤⽹关。
https://examlearn.online
[2026/05]
Question #550
Topic 1
⼀家公司使⽤ AWS Key Management Service (AWS KMS) 密钥来加密 AWS Lambda 环境变量。解决⽅案架构
师需要确保已具备解密和使⽤这些环境变量所需的权限。
解决⽅案架构师必须采取哪些步骤来实现正确的权限？（选择两项。）
A. 在 Lambda 资源策略中添加 AWS KMS 权限。
B. 在 Lambda 执⾏⻆⾊中添加 AWS KMS 权限。
C. 在 Lambda 函数策略中添加 AWS KMS 权限。
D. 在 AWS KMS 密钥策略中允许 Lambda 执⾏⻆⾊。
E. 在 AWS KMS 密钥策略中允许 Lambda 资源策略。
Question #551
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Glacier。
Topic 1
⼀家公司有⼀个财务应⽤程序，⽤于⽣成报表。这些报表平均⼤⼩为 50 KB，存储在 Amazon S3 中。报表在上
线后的第⼀周内会被频繁访问，并且需要保存数年。报表必须在 6 ⼩时内可检索。
A. 使⽤ S3 标准版。使⽤ S3 ⽣命周期规则，在 7 天后将报告迁移到 S3 Glacier。
B. 使⽤ S3 标准。使⽤ S3 ⽣命周期规则，在 7 天后将报表转换为 S3 标准 - 不频繁访问 (S3 标准-IA)。
C. 使⽤ S3 智能分层。配置 S3 智能分层，将报表迁移到 S3 标准-不频繁访问 (S3 Standard-IA) 和 S3
D. 使⽤ S3 标准版。使⽤ S3 ⽣命周期规则，在 7 天后将报告迁移到 S3 Glacier 深度存档。
https://examlearn.online
[2026/05]
Question #552
Topic 1
⼀家公司需要优化其 Amazon EC2 实例的成本。该公司还需要每 2-3 个⽉更换⼀次 EC2 实例的类型和系列。
为了满⾜这些要求，该公司应该怎么做？
A. 购买部分预付预留实例，期限为 3 年。
B. 购买为期 1 年的⽆需预付计算节省计划。
C. 购买所有预付预留实例，期限为 1 年。
D. 购买为期 1 年的全额预付 EC2 实例节省计划。
Question #553
解决⽅案架构师需要审查公司的 Amazon S3 存储桶，以发现个⼈身份信息 (PII)。该公司将 PII 数据存储在 us
east-1 区域和 us-west-2 区域。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 在每个区域中配置 Amazon Macie。创建⼀个作业来分析 Amazon S3 中的数据。
B. 为所有区域配置 AWS Security Hub。创建 AWS Config 规则以分析 Amazon S3 中的数据。
C. 配置 Amazon Inspector 以分析 Amazon S3 中的数据。
D. 配置 Amazon GuardDuty 分析 Amazon S3 中的数据。
Question #554
Topic 1
Topic 1
⼀家公司的 SAP 应⽤使⽤本地部署的 SQL Server 数据库作为后端。该公司希望将本地应⽤和数据库服务器迁移
到 AWS。该公司需要⼀个能够满⾜其 SAP 数据库⾼要求的实例类型。本地性能数据显示，SAP 应⽤和数据库的
内存利⽤率都很⾼。
哪种解决⽅案能够满⾜这些要求？
A. 应⽤程序使⽤计算优化型实例系列，数据库使⽤内存优化型实例系列。
B. 对应⽤程序和数据库都使⽤存储优化型实例系列。
C. 对应⽤程序和数据库都使⽤内存优化实例系列。
D. 应⽤程序使⽤⾼性能计算 (HPC) 优化实例系列。数据库使⽤内存优化实例系列。
https://examlearn.online
[2026/05]
Question #555
Topic 1
⼀家公司在包含公有⼦⽹和私有⼦⽹的虚拟私有云 (VPC) 中运⾏⼀个应⽤程序。该 VPC 跨越多个可⽤区。该应
⽤程序运⾏在私有⼦⽹中的 Amazon EC2 实例上。该应⽤程序使⽤ Amazon Simple Queue Service (Amazon
SQS) 队列。
解决⽅案架构师需要设计⼀个安全的解决⽅案，以在 EC2 实例和 SQS 队列之间建⽴连接。
哪个解决⽅案能够满⾜这些要求？
A. 为 Amazon SQS 实现⼀个接⼝ VPC 终端节点。配置该终端节点以使⽤私有⼦⽹。向该终端节点添加⼀个
安全组，该安全组包含⼀条⼊站访问规则，允许来⾃私有⼦⽹中 EC2 实例的流量。
B. 为 Amazon SQS 实现接⼝ VPC 终端节点。配置该终端节点以使⽤公有⼦⽹。将允许私有⼦⽹中的 EC2 实
例访问的 VPC 终端节点策略附加到该接⼝终端节点。
C. 为 Amazon SQS 实现接⼝ VPC 终端节点。配置该终端节点以使⽤公有⼦⽹。将 Amazon SQS 访问策略
附加到该接⼝ VPC 终端节点，该策略仅允许来⾃指定 VPC 终端节点的请求。
D. 为 Amazon SQS 实现⽹关终端节点。向私有⼦⽹添加 NAT ⽹关。将允许访问 SQS 队列的 IAM ⻆⾊附加
到 EC2 实例。
Question #556
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀位解决⽅案架构师正在使⽤ AWS CloudFormation 模板部署⼀个三层 Web 应⽤程序。该 Web 应⽤程序包含
⼀个 Web 层和⼀个应⽤层，应⽤层⽤于在 Amazon DynamoDB 表中存储和检索⽤户数据。Web 层和应⽤层托
管在 Amazon EC2 实例上，数据库层不对外公开。应⽤层 EC2 实例需要访问 DynamoDB 表，但不能在模板中
公开 API 凭证。
A. 创建⼀个 IAM ⻆⾊来读取 DynamoDB 表。通过引⽤实例配置⽂件将该⻆⾊与应⽤程序实例关联起来。
B. 创建⼀个具有读写 DynamoDB 表所需权限的 IAM ⻆⾊。将该⻆⾊添加到 EC2 实例配置⽂件，并将该实例
配置⽂件与应⽤程序实例关联。
C. 使⽤ AWS CloudFormation 模板中的参数部分，让⽤户从已创建的 IAM ⽤户输⼊访问密钥和秘密密钥，
该 IAM ⽤户具有从 DynamoDB 表读取和写⼊所需的权限。
D. 在 AWS CloudFormation 模板中创建⼀个具有读写 DynamoDB 表所需权限的 IAM ⽤户。使⽤ GetAtt 函
数检索访问密钥和秘密密钥，并通过⽤户数据将它们传递给应⽤程序实例。
https://examlearn.online
[2026/05]
Question #557
Topic 1
⼀位解决⽅案架构师负责管理⼀个分析应⽤程序。该应⽤程序将⼤量半结构化数据存储在 Amazon S3 存储桶
中。这位解决⽅案架构师希望使⽤并⾏数据处理来加快数据处理速度。此外，他还希望利⽤存储在 Amazon
Redshift 数据库中的信息来丰富数据。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon Athena 处理 S3 数据。使⽤ AWS Glue 和 Amazon Redshift 数据来丰富 S3 数据。
B. 使⽤ Amazon EMR 处理 S3 数据。将 Amazon EMR 与 Amazon Redshift 数据结合使⽤，以丰富 S3 数
据。
C. 使⽤ Amazon EMR 处理 S3 数据。使⽤ Amazon Kinesis Data Streams 将 S3 数据迁移到 Amazon
Redshift，以便对数据进⾏丰富化。
D. 使⽤ AWS Glue 处理 S3 数据。使⽤ AWS Lake Formation 和 Amazon Redshift 数据来丰富 S3 数据。
Question #558
连接这两个 VPC 最具成本效益的解决⽅案是什么？
Topic 1
⼀家公司在同⼀个 AWS 账户的 us-west-2 区域内有两个 VPC。该公司需要允许这两个 VPC 之间进⾏⽹络流量
通信。预计每⽉这两个 VPC 之间将有⼤约 500 GB 的数据传输。
A. 部署 AWS Transit Gateway 连接 VPC。更新每个 VPC 的路由表，使 VPC 间通信使⽤ Transit Gateway。
B. 在 VPC 之间建⽴ AWS 站点到站点 VPN 隧道。更新每个 VPC 的路由表，以使⽤ VPN 隧道进⾏ VPC 间通
信。
C. 在 VPC 之间建⽴ VPC 对等连接。更新每个 VPC 的路由表，使 VPC 对等连接⽤于 VPC 间的通信。
D. 在 VPC 之间建⽴ 1 GB 的 AWS Direct Connect 连接。更新每个 VPC 的路由表，以使⽤ Direct Connect
连接进⾏ VPC 间通信。
https://examlearn.online
[2026/05]
Question #559
Topic 1
⼀家公司在 AWS 上为不同的产品线托管了多个应⽤程序。这些应⽤程序使⽤不同的计算资源，包括 Amazon
EC2 实例和应⽤程序负载均衡器。这些应⽤程序运⾏在 AWS Organizations 中同⼀组织下的不同 AWS 账户中，
这些账户分布在多个 AWS 区域。每个产品线的团队都在各⾃的账户中标记了每个计算资源。
该公司希望通过 Organizations 中的合并账单功能了解每个产品线的更多成本详情。
以下哪两项步骤组合可以满⾜这些要求？（选择两项。）
A. 在 AWS 账单控制台中选择特定的 AWS ⽣成的标签。
B. 在 AWS 账单控制台中选择⼀个特定的⽤户定义标签。
C. 在 AWS 资源组控制台中选择⼀个特定的⽤户定义标签。
D. 从每个 AWS 账户激活所选标签。
E. 从组织管理帐户激活所选标签。
Question #560
哪个解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司的解决⽅案架构师正在设计⼀个使⽤ AWS Organizations 的 AWS 多账户解决⽅案。该架构师已将公司
账户组织成组织单元 (OU)。
他需要⼀个解决⽅案来识别 OU 层级结构的任何变更，并将所有变更通知公司的运维团队。
A. 使⽤ AWS Control Tower 配置 AWS 账户。使⽤账户漂移通知来识别 OU 层次结构的变化。
B. 使⽤ AWS Control Tower 配置 AWS 账户。使⽤ AWS Config 聚合规则来识别 OU 层次结构的更改。
C. 使⽤ AWS Service Catalog 在 Organizations 中创建账户。使⽤ AWS CloudTrail 组织跟踪来识别 OU 层
次结构的更改。
D. 使⽤ AWS CloudFormation 模板在组织中创建账户。对堆栈使⽤漂移检测操作来识别 OU 层次结构的更
改。
https://examlearn.online
[2026/05]
Question #561
Topic 1
⼀家公司的⽹站每天处理数百万个请求，⽽且请求数量还在持续增⻓。解决⽅案架构师需要提⾼该 Web 应⽤程序
的响应速度。该架构师确定，应⽤程序需要降低从 Amazon DynamoDB 表中检索产品详细信息时的延迟。
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 设置 DynamoDB Accelerator (DAX) 集群。将所有读取请求路由到 DAX。
B. 在 DynamoDB 表和 Web 应⽤程序之间配置 Amazon ElastiCache for Redis。将所有读取请求路由到
Redis。
C. 在 DynamoDB 表和 Web 应⽤程序之间配置 Amazon ElastiCache for Memcached。将所有读取请求路
由到 Memcached。
D. 在表上设置 Amazon DynamoDB Streams，并让 AWS Lambda 从表中读取数据并填充 Amazon
ElastiCache。将所有读取请求路由到 ElastiCache。
Question #562
A. 为端点创建路由表条⽬。
Topic 1
解决⽅案架构师需要确保从 VPC 中的 Amazon EC2 实例对 Amazon DynamoDB 的 API 调⽤不会通过互联⽹传
输。
为了满⾜此要求，解决⽅案架构师应该采取哪些步骤组合？（选择两项。）
B. 为 DynamoDB 创建⽹关端点。
C. 为 Amazon EC2 创建接⼝端点。
D. 为 VPC 的每个⼦⽹中的端点创建弹性⽹络接⼝。
E. 在端点的安全组中创建安全组条⽬以提供访问权限。
https://examlearn.online
[2026/05]
Question #563
Topic 1
⼀家公司同时在 Amazon Elastic Kubernetes Service (Amazon EKS) 集群和本地 Kubernetes 集群上运⾏其应
⽤程序。该公司希望从⼀个中⼼位置查看所有集群和⼯作负载。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ Amazon CloudWatch Container Insights 收集和分组集群信息。
B. 使⽤ Amazon EKS Connector 注册并连接所有 Kubernetes 集群。
C. 使⽤ AWS Systems Manager 收集和查看集群信息。
D. 使⽤ Amazon EKS Anywhere 作为主集群，通过原⽣ Kubernetes 命令查看其他集群。
Question #564
哪种解决⽅案能够满⾜这些要求？
⽤ IAM 实例⻆⾊限制访问权限。
Topic 1
⼀家公司正在开发⼀款电⼦商务应⽤，需要存储敏感的客户信息。该公司需要让客户能够在⽹站上完成购买交
易。同时，该公司还需要确保敏感的客户数据受到保护，即使是数据库管理员也⽆法访问这些数据。
A. 将敏感数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷中。使⽤ EBS 加密对数据进⾏加密。使
B. 将敏感数据存储在 Amazon RDS for MySQL 中。使⽤ AWS Key Management Service (AWS KMS) 客户
端加密对数据进⾏加密。
C. 将敏感数据存储在 Amazon S3 中。使⽤ AWS Key Management Service (AWS KMS) 服务器端加密对数
据进⾏加密。使⽤ S3 存储桶策略限制访问。
D. 将敏感数据存储在 Amazon FSx for Windows Server 中。在应⽤程序服务器上挂载⽂件共享。使⽤
Windows ⽂件权限限制访问。
https://examlearn.online
[2026/05]
Question #565
Topic 1
⼀家公司拥有⼀个本地部署的 MySQL 数据库，⽤于处理事务数据。该公司正在将该数据库迁移到 AWS 云平
台。迁移后的数据库必须与公司使⽤该数据库的应⽤程序保持兼容性，并且还必须在需求⾼峰期⾃动扩展。
哪种迁移⽅案能够满⾜这些要求？
A. 使⽤ MySQL 原⽣⼯具将数据库迁移到 Amazon RDS for MySQL。配置弹性存储扩展。
B. 使⽤ mysqldump ⼯具将数据库迁移到 Amazon Redshift。为 Amazon Redshift 集群启⽤⾃动扩展功能。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据库迁移到 Amazon Aurora。启⽤ Aurora ⾃动扩展。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据库迁移到 Amazon DynamoDB。配置⾃动扩展策略。
Question #566
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司在跨两个可⽤区的 VPC 中运⾏多个 Amazon EC2 Linux 实例。这些实例托管使⽤分层⽬录结构的应⽤
程序。这些应⽤程序需要快速且并发地读写共享存储。
A. 创建⼀个 Amazon S3 存储桶。允许 VPC 中的所有 EC2 实例访问该存储桶。
B. 创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。从每个 EC2 实例挂载 EFS ⽂件系统。
C. 在已配置 IOPS SSD (io2) Amazon Elastic Block Store (Amazon EBS) 卷上创建⽂件系统。将 EBS 卷附
加到所有 EC2 实例。
D. 在附加到每个 EC2 实例的 Amazon Elastic Block Store (Amazon EBS) 卷上创建⽂件系统。在不同的
EC2 实例之间同步 EBS 卷。
https://examlearn.online
[2026/05]
Question #567
Topic 1
⼀位解决⽅案架构师正在设计⼀个⼯作负载，⽤于存储建筑物内企业租户的每⼩时能耗数据。传感器将通过
HTTP 请求向数据库发送数据，数据库将汇总每个租户的能耗。解决⽅案架构师必须尽可能使⽤托管服务。随着
解决⽅案架构师添加独⽴组件，该⼯作负载未来将获得更多功能。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ Amazon API Gateway 和 AWS Lambda 函数接收来⾃传感器的数据，处理数据，并将数据存储在
Amazon DynamoDB 表中。
B. 使⽤由 Amazon EC2 实例⾃动扩展组⽀持的弹性负载均衡器来接收和处理来⾃传感器的数据。使⽤
Amazon S3 存储桶来存储处理后的数据。
C. 使⽤ Amazon API Gateway 和 AWS Lambda 函数接收来⾃传感器的数据，处理数据，并将数据存储在
Amazon EC2 实例上的 Microsoft SQL Server Express 数据库中。
D. 使⽤由 Amazon EC2 实例⾃动扩展组⽀持的弹性负载均衡器来接收和处理来⾃传感器的数据。使⽤
Amazon Elastic File System (Amazon EFS) 共享⽂件系统来存储处理后的数据。
Question #568
Topic 1
⼀位解决⽅案架构师正在为⼀款⽤于存储和查看⼯程图纸的全新 Web 应⽤程序设计存储架构。所有应⽤程序组件
都将部署在 AWS 基础设施上。
该应⽤程序设计必须⽀持缓存，以最⼤限度地减少⽤户等待⼯程图纸加载的时间。该应⽤程序必须能够存储 PB
级的数据。
解决⽅案架构师应该使⽤哪种存储和缓存组合？
A. Amazon S3 与 Amazon CloudFront
B. Amazon S3 Glacier 搭配 Amazon ElastiCache
C. Amazon Elastic Block Store (Amazon EBS) 卷与 Amazon CloudFront
D. AWS Storage Gateway 与 Amazon ElastiCache
https://examlearn.online
[2026/05]
Question #569
Topic 1
Amazon EventBridge 规则针对第三⽅ API。该第三⽅ API 尚未收到任何⼊站流量。解决⽅案架构师需要确定规
则条件是否满⾜，以及规则的⽬标是否被调⽤。
哪种解决⽅案能够满⾜这些要求？
A. 检查 Amazon CloudWatch 中 AWS/Events 命名空间的指标。
B. 查看 Amazon Simple Queue Service (Amazon SQS) 死信队列中的事件。
C. 检查 Amazon CloudWatch Logs 中的事件。
D. 在 AWS CloudTrail 中查看 EventBridge 事件的跟踪记录。
Question #570
Topic 1
⼀家公司每周五晚上都会运⾏⼀个⼤型⼯作负载。该⼯作负载运⾏在位于美国东部 1 区两个可⽤区的 Amazon
EC2 实例上。通常情况下，该公司最多只能同时运⾏两个实例。但是，为了应对每周五定期增加的⼯作负载，该
公司希望将实例数量扩展到六个。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 在 Amazon EventBridge 中创建提醒，以便扩展实例。
B. 创建⼀个具有计划操作的⾃动扩展组。
C. 创建⼀个使⽤⼿动缩放的⾃动缩放组。
D. 创建⼀个使⽤⾃动缩放的⾃动缩放组。
https://examlearn.online
[2026/05]
Question #571
Topic 1
⼀家公司正在开发⼀个 REST API。该公司对 TLS 的使⽤有严格的要求，要求 API 端点使⽤ TLSv1.3，并且要求
使⽤指定的第三⽅公共证书颁发机构 (CA) 来签署 TLS 证书。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤本地计算机创建由第三⽅ C 签名的证书。将该证书导⼊ AWS Certificate Manager (ACM)。在
Amazon API Gateway 中创建⼀个带有⾃定义域名的 HTTP API。配置该⾃定义域名以使⽤该证书。
B. 在 AWS Certificate Manager (ACM) 中创建由第三⽅ CA 签名的证书。在 Amazon API Gateway 中创建
⼀个带有⾃定义域名的 HTTP API。配置该⾃定义域名以使⽤该证书。
C. 使⽤ AWS Certificate Manager (ACM) 创建由第三⽅ CA 签名的证书。将该证书导⼊ AWS Certificate
Manager (ACM)。创建⼀个 AWS Lambda 函数，并为其分配⼀个 Lambda 函数 URL。配置该 Lambda 函数
URL 以使⽤该证书。
D. 在 AWS Certificate Manager (ACM) 中创建由第三⽅ CA 签名的证书。创建 AWS Lambda 函数并分配
Lambda 函数 URL。配置 Lambda 函数 URL 以使⽤该证书。
Question #572
Topic 1
⼀家公司在 AWS 上运⾏⼀个应⽤程序。该应⽤程序的使⽤量不稳定。该应⽤程序使⽤ AWS Direct Connect 连
接到本地 MySQL 兼容数据库。本地数据库始终⾄少占⽤ 2 GiB 内存。
该公司希望将本地数据库迁移到托管的 AWS 服务。该公司希望使⽤⾃动扩展功能来应对意外的⼯作负载增⻓。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 配置具有默认读取和写⼊容量设置的 Amazon DynamoDB 数据库。
B. 提供容量⾄少为 1 个 Aurora 容量单位 (ACU) 的 Amazon Aurora 数据库。
C. 提供容量⾄少为 1 个 Aurora 容量单位 (ACU) 的 Amazon Aurora Serverless v2 数据库。
D. 为 MySQL 数据库配置 2 GiB 内存。
https://examlearn.online
[2026/05]
Question #573
Topic 1
⼀家公司希望在 AWS Lambda 中使⽤事件驱动编程模型。该公司希望降低运⾏在 Java 11 上的 Lambda 函数的
启动延迟。该公司对应⽤程序的延迟没有严格的要求。该公司希望在函数扩展时减少冷启动和异常延迟。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置 Lambda 预置并发。
B. 增加 Lambda 函数的超时时间。
C. 增加 Lambda 函数的内存。
D. 配置 Lambda SnapStart。
Question #574
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家⾦融服务公司推出了⼀款使⽤ Amazon RDS for MySQL 数据库的新应⽤程序。该公司使⽤该应⽤程序跟踪
股票市场趋势。该公司每周只需运⾏该应⽤程序 2 ⼩时。该公司需要优化数据库运⾏成本。
A. 将现有的 RDS for MySQL 数据库迁移到 Aurora Serverless v2 MySQL 数据库集群。
B. 将现有的 RDS for MySQL 数据库迁移到 Aurora MySQL 数据库集群。
C. 将现有的 RDS for MySQL 数据库迁移到运⾏ MySQL 的 Amazon EC2 实例。为该 EC2 实例购买实例预
留。
D. 将现有的 RDS for MySQL 数据库迁移到使⽤ MySQL 容器镜像运⾏任务的 Amazon Elastic Container
Service (Amazon ECS) 集群。
https://examlearn.online
[2026/05]
Question #575
Topic 1
⼀家公司将其应⽤程序部署在 AWS 区域的 Amazon Elastic Kubernetes Service (Amazon EKS) 上，并通过应
⽤程序负载均衡器进⾏管理。该应⽤程序需要将数据存储在 PostgreSQL 数据库引擎中。该公司希望数据库中的
数据具有⾼可⽤性，并且需要提⾼读取⼯作负载的容量。
哪种解决⽅案能够以最⾼的运维效率满⾜这些要求？
A. 创建⼀个配置了全局表的 Amazon DynamoDB 数据库表。
B. 创建具有多可⽤区部署的 Amazon RDS 数据库。
C. 创建具有多可⽤区数据库集群部署的 Amazon RDS 数据库。
D. 创建⼀个配置了跨区域只读副本的 Amazon RDS 数据库。
Question #576
A. 私有端点
B. 区域终点
Topic 1
⼀家公司正在使⽤ Amazon API Gateway 和 AWS Lambda 在 AWS 上构建⼀个 RESTful ⽆服务器 Web 应⽤程
序。该 Web 应⽤程序的⽤户分布在不同的地理位置，公司希望降低 API 请求对这些⽤户的延迟。
解决⽅案架构师应该使⽤哪种类型的端点来满⾜这些要求？
C. VPC 端点接⼝
D. 边缘优化端点
https://examlearn.online
[2026/05]
Question #577
Topic 1
⼀家公司使⽤ Amazon CloudFront 分发为其⽹站提供内容⻚⾯。该公司需要确保客户端在访问其⽹站时使⽤
TLS 证书。该公司希望实现 TLS 证书的⾃动创建和续订。
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
A. 使⽤ CloudFront 安全策略创建证书。
B. 使⽤ CloudFront 源访问控制 (OAC) 创建证书。
C. 使⽤ AWS Certificate Manager (ACM) 创建证书。对域名启⽤ DNS 验证。
D. 使⽤ AWS Certificate Manager (ACM) 创建证书。对域名启⽤电⼦邮件验证。
Question #578
⼀家公司部署了⼀个使⽤ Amazon DynamoDB 作为数据库层的⽆服务器应⽤程序。该应⽤程序的⽤户数量⼤幅
增⻓。该公司希望将数据库响应时间从毫秒级提升到微秒级，并对数据库请求进⾏缓存。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 使⽤ DynamoDB Accelerator (DAX)。
B. 将数据库迁移到 Amazon Redshift。
C. 将数据库迁移到 Amazon RDS。
D. 使⽤ Amazon ElastiCache for Redis。
Question #579
Topic 1
Topic 1
⼀家公司运⾏⼀个使⽤ Amazon RDS for PostgreSQL 的应⽤程序。该应⽤程序仅在⼯作⽇的办公时间内有流
量。该公司希望根据这种使⽤情况优化成本并降低运营开销。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS 上的实例调度器配置启动和停⽌计划。
B. 关闭⾃动备份。每周⼿动创建数据库快照。
C. 创建⼀个⾃定义 AWS Lambda 函数，根据最低 CPU 利⽤率启动和停⽌数据库。
D. 购买所有预付预留的数据库实例。
https://examlearn.online
[2026/05]
Question #580
Topic 1
⼀家公司使⽤本地存储运⾏对延迟敏感的应⽤程序。该公司采⽤直接迁移的⽅式将该应⽤程序迁移到 AWS 云。
该公司不希望更改应⽤程序架构。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置⼀个包含 Amazon EC2 实例的⾃动扩展组。使⽤ Amazon FSx for Lustre ⽂件系统来运⾏应⽤程序。
B. 将应⽤程序托管在 Amazon EC2 实例上。使⽤ Amazon Elastic Block Store (Amazon EBS) GP2 卷来运
⾏应⽤程序。
C. 配置⼀个包含 Amazon EC2 实例的⾃动扩展组。使⽤ Amazon FSx for OpenZFS ⽂件系统来运⾏应⽤程
序。
D. 将应⽤程序托管在 Amazon EC2 实例上。使⽤ Amazon Elastic Block Store (Amazon EBS) GP3 卷来运
⾏应⽤程序。
Question #581
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个有状态的⽣产应⽤程序。该应⽤程序需要⾄少两个 EC2 实例始终保持
运⾏。
解决⽅案架构师需要为该应⽤程序设计⼀个⾼可⽤性和容错架构。解决⽅案架构师创建了⼀个 EC2 实例的⾃动扩
展组。
为了满⾜这些要求，解决⽅案架构师还应该采取哪些额外步骤？
A. 将⾃动扩展组的最⼩容量设置为 2。在⼀个可⽤区部署⼀个按需实例，在另⼀个可⽤区部署⼀个按需实
例。
B. 将⾃动扩展组的最⼩容量设置为 4。在⼀个可⽤区部署两个按需实例，在另⼀个可⽤区部署两个按需实
例。
C. 将⾃动扩展组的最⼩容量设置为 2。在⼀个可⽤区中部署四个竞价型实例。
D. 将⾃动扩展组的最⼩容量设置为 4。在⼀个可⽤区部署两个按需实例，在另⼀个可⽤区部署两个竞价型实
例。
https://examlearn.online
[2026/05]
Question #582
Topic 1
⼀家电商公司使⽤ Amazon Route 53 作为其 DNS 提供商。该公司将其⽹站托管在本地和 AWS 云端。该公司的
本地数据中⼼位于 us-west-1 区域附近。该公司使⽤ eu-central-1 区域托管其⽹站。该公司希望尽可能缩短⽹站
加载时间。
哪种解决⽅案能够满⾜这些要求？
A. 设置地理位置路由策略。将靠近 us-west-1 的流量发送到本地数据中⼼。将靠近 eu-central-1 的流量发送
到 eu-central-1。
B. 设置⼀个简单的路由策略，将所有靠近 eu-central-1 的流量路由到 eu-central-1，并将所有靠近本地数据
中⼼的流量路由到本地数据中⼼。
C. 设置延迟路由策略。将该策略与 us-west-1 关联。
D. 设置加权路由策略。将流量平均分配到 eu-central-1 和本地数据中⼼。
Question #583
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Glacier Flexible Retrieval。
Topic 1
⼀家公司在物理磁带上存储了 5 PB 的归档数据。出于合规性要求，该公司需要将磁带上的数据再保存 10 年。该
公司计划在未来 6 个⽉内迁移到 AWS。存储磁带的数据中⼼拥有 1 Gbps 的上⾏互联⽹连接。
A. 从 本地磁带读取数据。将数据暂存在本地 NFS 存储中。使⽤ AWS DataSync 将数据迁移到 Amazon S3
B. 使⽤本地备份应⽤程序从磁带读取数据，并直接写⼊ Amazon S3 Glacier Deep Archive。
C. 订购多台配备磁带⽹关的 AWS Snowball 设备。将物理磁带复制到 Snowball 中的虚拟磁带。将 Snowball
设备运送⾄ AWS。创建⽣命周期策略，将磁带迁移到 Amazon S3 Glacier Deep Archive。
D. 配置本地磁带⽹关。在 AWS 云中创建虚拟磁带。使⽤备份软件将物理磁带复制到虚拟磁带。
https://examlearn.online
[2026/05]
Question #584
Topic 1
⼀家公司正在部署⼀个并⾏处理⼤量数据的应⽤程序。该公司计划使⽤ Amazon EC2 实例来处理该⼯作负载。⽹
络架构必须可配置，以防⽌多个节点共享相同的底层硬件。
哪种⽹络解决⽅案满⾜这些要求？
A. 在分散放置组中运⾏ EC2 实例。
B. 将 EC2 实例分组到不同的账户中。
C. 配置具有专⽤租户的 EC2 实例。
D. 配置 EC2 实例为共享租户。
Question #585
哪种解决⽅案能够满⾜这些要求？
Topic 1
解决⽅案架构师正在设计灾难恢复 (DR) 策略，以在故障转移的 AWS 区域中提供 Amazon EC2 容量。业务需求
指出，DR 策略必须满⾜故障转移区域的容量要求。
A. 在故障转移区域中购买按需实例。
B. 在故障转移区域购买 EC2 节省计划。
C. 在故障转移区域中购买区域预留实例。
D. 在故障转移区域中购买容量预留。
https://examlearn.online
[2026/05]
Question #586
Topic 1
⼀家公司在 AWS Organizations 中拥有五个组织单元 (OU)。每个 OU 对应该公司旗下的五个业务部⻔。该公司
的研发 (R&D) 业务部⻔即将从公司分离出来，需要建⽴⾃⼰的组织。解决⽅案架构师为此创建了⼀个新的管理帐
户。
接下来，解决⽅案架构师应该在新管理帐户中执⾏哪些操作？
A. 在过渡期间，让研发 AWS 账户同时属于这两个组织。
B. 在研发 AWS 账户离开原组织后，邀请研发 AWS 账户加⼊新组织。
C. 在新组织中创建⼀个新的研发 AWS 账户。将资源从之前的研发 AWS 账户迁移到新的研发 AWS 账户。
D. 将研发部⻔的 AWS 账户加⼊新组织。将新的管理账户设为原组织的成员。
Question #587
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在设计⼀个解决⽅案，⽤于捕获不同 Web 应⽤程序中的客户活动，以便进⾏分析和预测。Web 应⽤
程序中的客户活动难以预测，并且可能突然增加。该公司需要⼀个能够与其他 Web 应⽤程序集成的解决⽅案。出
于安全考虑，该解决⽅案必须包含授权步骤。
A. 在 Amazon Elastic Container Service (Amazon ECS) 容器实例前配置⽹关负载均衡器 (GWLB)，该容器
实例将公司接收的信息存储在 Amazon Elastic File System (Amazon EFS) ⽂件系统中。授权在 GWLB 处解
析。
B. 在 Amazon Kinesis 数据流前端配置 Amazon API Gateway 端点，该数据流将公司接收到的信息存储在
Amazon S3 存储桶中。使⽤ AWS Lambda 函数解决授权问题。
C. 在 Amazon Kinesis Data Firehose 前端配置 Amazon API Gateway 端点，该端点将公司接收到的信息存
储在 Amazon S3 存储桶中。使⽤ API Gateway Lambda 授权器来解决授权问题。
D. 在 Amazon Elastic Container Service (Amazon ECS) 容器实例前配置⽹关负载均衡器 (GWLB)，该容器
实例⽤于存储公司从 Amazon Elastic File System (Amazon EFS) ⽂件系统接收的信息。使⽤ AWS Lambda
函数解决授权问题。
https://examlearn.online
[2026/05]
Question #588
Topic 1
⼀家电商公司希望为其运⾏ Microsoft SQL Server 企业版的 Amazon RDS 数据库实例寻找灾难恢复解决⽅案。
该公司⽬前的恢复点⽬标 (RPO) 和恢复时间⽬标 (RTO) 均为 24 ⼩时。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建跨区域的只读副本，并将只读副本提升为主实例。
B. 使⽤ AWS 数据库迁移服务 (AWS DMS) 创建 RDS 跨区域复制。
C. 每 24 ⼩时使⽤跨区域复制将本地备份复制到 Amazon S3 存储桶。
D. 每 24 ⼩时将⾃动快照复制到另⼀个区域。
Question #589
哪种解决⽅案能够满⾜这些要求？
for Memcached 存储会话状态。
Topic 1
⼀家公司在启⽤了会话保持功能的 Amazon EC2 实例上运⾏⼀个 Web 应⽤程序，该实例位于⾃动扩展组 (Auto
Scaling group) 中，并由应⽤程序负载均衡器 (Application Load Balancer) 管理。⽬前，Web 服务器托管⽤户
会话状态。该公司希望确保⾼可⽤性，并在 Web 服务器发⽣故障时避免⽤户会话状态丢失。
A. 使⽤ Amazon ElastiCache for Memcached 实例存储会话数据。更新应⽤程序，使其使⽤ ElastiCache
B. 使⽤ Amazon ElastiCache for Redis 存储会话状态。更新应⽤程序，使其使⽤ ElastiCache for Redis 存
储会话状态。
C. 使⽤ AWS Storage Gateway 缓存卷存储会话数据。更新应⽤程序，使其使⽤ AWS Storage Gateway 缓
存卷来存储会话状态。
D. 使⽤ Amazon RDS 存储会话状态。更新应⽤程序以使⽤ Amazon RDS 存储会话状态。
https://examlearn.online
[2026/05]
Question #590
Topic 1
⼀家公司将其内部数据中⼼的 MySQL 数据库迁移到了 Amazon RDS for MySQL 数据库实例。该公司根据公司
平均每⽇⼯作负载调整了 RDS 数据库实例的容量。每⽉⼀次，当公司运⾏报表查询时，数据库性能会下降。该公
司希望能够运⾏报表并保持⽇常⼯作负载的性能。
哪种解决⽅案能够满⾜这些要求？
A. 创建数据库的只读副本。将查询直接发送到该只读副本。
B. 创建数据库备份。将备份恢复到另⼀个数据库实例。将查询定向到新数据库。
C. 将数据导出到 Amazon S3。使⽤ Amazon Athena 查询 S3 存储桶。
D. 调整数据库实例⼤⼩以适应额外的⼯作负载。
Question #591
Topic 1
⼀家公司使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 运⾏容器应⽤程序。该应⽤程序包含⽤于管
理客户和处理订单的微服务。该公司需要将传⼊的请求路由到相应的微服务。
哪种解决⽅案能够以最具成本效益的⽅式满⾜此需求？
A. 使⽤ AWS 负载均衡控制器来配置⽹络负载均衡器。
B. 使⽤ AWS 负载均衡控制器来配置应⽤程序负载均衡器。
C. 使⽤ AWS Lambda 函数将请求连接到 Amazon EKS。
D. 使⽤ Amazon API Gateway 将请求连接到 Amazon EKS。
https://examlearn.online
[2026/05]
Question #592
Topic 1
⼀家公司使⽤ AWS 并出售受版权保护图像的访问权限。该公司的全球客户群需要能够快速访问这些图像。该公
司必须禁⽌特定国家/地区的⽤户访问。该公司希望尽可能降低成本。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon S3 存储图像。启⽤多重身份验证 (MFA) 和公共存储桶访问权限。向客户提供 S3 存储桶的
链接。
B. 使⽤ Amazon S3 存储图像。为每个客户创建⼀个 IAM ⽤户。将这些⽤户添加到具有访问 S3 存储桶权限
的组中。
C. 使⽤部署在应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2 实例来存储镜像。仅在公司提供服务的国家/
地区部署这些实例。向客户提供其所在国家/地区实例的 ALB 链接。
D. 使⽤ Amazon S3 存储图像。使⽤ Amazon CloudFront 分发图像，并设置地域限制。为每个客户提供⼀个
签名 URL，以便他们访问 CloudFront 中的数据。
Question #593
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀位解决⽅案架构师正在设计⼀个基于 Amazon ElastiCache for Redis 的⾼可⽤性解决⽅案。该架构师需要确保
故障不会导致本地和 AWS 区域内的性能下降或数据丢失。该解决⽅案需要在节点级别和区域级别都提供⾼可⽤
性。
A. 使⽤包含多个节点的分⽚的多可⽤区 Redis 复制组。
B. 使⽤包含多个节点的 Redis 分⽚，并启⽤ Redis 仅追加⽂件 (AOF)。
C. 使⽤具有多个只读副本的多可⽤区 Redis 集群，复制组中有多个只读副本。
D. 使⽤包含多个节点的 Redis 分⽚，并启⽤⾃动扩展功能。
https://examlearn.online
[2026/05]
Question #594
Topic 1
⼀家公司计划将其应⽤程序迁移到 AWS，并使⽤ Amazon EC2 按需实例。在迁移测试阶段，技术团队发现应⽤
程序启动和加载内存以达到完全运⾏状态所需的时间过⻓。在下⼀测试阶段，
哪种解决⽅案可以缩短应⽤程序的启动时间？
A. 启动两个或多个 EC2 按需实例。启⽤⾃动扩展功能，并在下⼀个测试阶段使 EC2 按需实例可⽤。
B. 启动 EC2 Spot 实例来⽀持应⽤程序，并扩展应⽤程序，以便在下⼀个测试阶段可⽤。
C. 启动启⽤休眠功能的 EC2 按需实例。在下⼀测试阶段配置 EC2 ⾃动扩展热池。
D. 启动带有容量预留的 EC2 按需实例。在下⼀测试阶段启动更多 EC2 实例。
Question #595
Topic 1
⼀家公司的应⽤程序运⾏在 Amazon EC2 实例的⾃动扩展组中。该公司注意到，其应⽤程序会在⼀周中的某些随
机⽇期出现流量突然激增的情况。该公司希望在流量激增期间保持应⽤程序的性能。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤⼿动缩放来更改⾃动缩放组的⼤⼩。
B. 使⽤预测缩放来改变⾃动缩放组的⼤⼩。
C. 使⽤动态缩放来改变⾃动缩放组的⼤⼩。
D. 使⽤计划缩放来更改⾃动缩放组的⼤⼩。
https://examlearn.online
[2026/05]
Question #596
Topic 1
⼀个电商应⽤使⽤运⾏在 Amazon EC2 实例上的 PostgreSQL 数据库。在每⽉⼀次的促销活动期间，数据库使⽤
量激增，导致应⽤出现数据库连接问题。后续每⽉促销活动的流量难以预测，影响了销售预测。公司需要在流量
出现不可预测的增⻓时保持性能稳定。
哪种解决⽅案能够以最具成本效益的⽅式解决此问题？
A. 将 PostgreSQL 数据库迁移到 Amazon Aurora Serverless v2。
B. 为 EC2 实例上的 PostgreSQL 数据库启⽤⾃动扩展，以适应不断增⻓的使⽤量。
C. 将 PostgreSQL 数据库迁移到 Amazon RDS for PostgreSQL，并选择更⼤的实例类型。
D. 将 PostgreSQL 数据库迁移到 Amazon Redshift 以适应不断增⻓的使⽤量。
Question #597
哪种解决⽅案能够满⾜这些要求？
A. 提⾼ API ⽹关限速限制。
Topic 1
⼀家公司使⽤ Amazon API Gateway 和 AWS Lambda 在 AWS 上托管了⼀个内部⽆服务器应⽤程序。该公司员
⼯反映，每天启动该应⽤程序时都会遇到⾼延迟问题。该公司希望降低延迟。
B. 在员⼯每天开始使⽤该应⽤程序之前，设置计划扩展以增加 Lambda 预置的并发量。
C. 创建⼀个 Amazon CloudWatch 警报，以便在每天开始时启动 Lambda 函数作为警报的⽬标。
D. 增加 Lambda 函数内存。
https://examlearn.online
[2026/05]
Question #598
Topic 1
⼀家研究公司使⽤本地设备⽣成⽤于分析的数据。该公司希望使⽤ AWS 云来分析这些数据。这些设备⽣成 .csv
⽂件，并⽀持将数据写⼊ SMB ⽂件共享。公司分析师必须能够使⽤ SQL 命令查询数据。分析师将在⼀天中定期
运⾏查询。
以下哪三项步骤组合能够以最具成本效益的⽅式满⾜这些要求？（选择三项。）
A. 在本地部署 AWS Storage Gateway，采⽤ Amazon S3 ⽂件⽹关模式。
B. 在 Amazon FSx ⽂件⽹关中部署本地 AWS Storage Gateway。
C. 设置 AWS Glue 爬⾍程序，根据 Amazon S3 中的数据创建表。
D. 使⽤ EMR ⽂件系统 (EMRFS) 设置 Amazon EMR 集群，以查询 Amazon S3 中的数据。向分析师提供访
问权限。
E. 设置 Amazon Redshift 集群以查询 Amazon S3 中的数据。向分析师提供访问权限。
F. 设置 Amazon Athena 以查询 Amazon S3 中的数据。向分析师提供访问权限。
Question #599
哪些活动属于公司运维团队的职责范围？（选择三项。）
Topic 1
⼀家公司希望使⽤ Amazon Elastic Container Service (Amazon ECS) 集群和 Amazon RDS 数据库实例来构建
和运⾏⽀付处理应⽤程序。出于合规性考虑，该公司将在其本地数据中⼼运⾏该应⽤程序。
解决⽅案架构师希望将 AWS Outposts 作为解决⽅案的⼀部分。该解决⽅案架构师正在与公司的运维团队合作构
建该应⽤程序。
A. 为前哨站机架提供可靠的电源和⽹络连接
B. 管理 Outposts 上运⾏的虚拟化管理程序、存储系统和 AWS 服务
C. 数据中⼼环境的物理安全和访问控制
D. 前哨站基础设施的可⽤性，包括前哨站机架内的电源、服务器和⽹络设备。
E. 前哨站组件的物理维护
F. 为 Amazon ECS 集群提供额外容量，以缓解服务器故障和维护事件
https://examlearn.online
[2026/05]
Question #600
⼀家公司计划将⼀个基于 TCP 的应⽤程序迁移到其虚拟专⽤⽹络 (VPC) 中。该应⽤程序⽬前可通过公司数据中
⼼内的硬件设备，使⽤⾮标准 TCP 端⼝进⾏公开访问。该公共端点每秒可处理⾼达 300 万个请求，且延迟极
低。该公司要求 AWS 中的新公共端点也达到相同的性能⽔平。
解决⽅案架构师应该提出怎样的建议才能满⾜这⼀要求？
A. 部署⽹络负载均衡器（NLB）。将NLB配置为可通过应⽤程序所需的TCP端⼝公开访问。
B. 部署应⽤程序负载均衡器 (ALB)。将 ALB 配置为可通过应⽤程序所需的 TCP 端⼝公开访问。
Topic 1
C. 部署⼀个监听应⽤程序所需 TCP 端⼝的 Amazon CloudFront 分发。使⽤应⽤程序负载均衡器作为源服务
器。
D. 部署⼀个配置了应⽤程序所需 TCP 端⼝的 Amazon API Gateway API。配置具有预置并发能⼒的 AWS
Lambda 函数来处理请求。
https://examlearn.online
[2026/05]
Question #601
Topic 1
⼀家公司的关键数据库运⾏在 Amazon RDS for PostgreSQL 数据库实例上。该公司希望迁移到 Amazon Aurora
PostgreSQL，并尽可能减少停机时间和数据丢失。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 为 RDS for PostgreSQL 数据库实例创建数据库快照，以填充新的 Aurora PostgreSQL 数据库集群。
B. 为 RDS for PostgreSQL 数据库实例创建 Aurora 只读副本。将 Aurora 只读副本提升到新的 Aurora
PostgreSQL 数据库集群。
C. 使⽤从 Amazon S3 导⼊数据将数据库迁移到 Aurora PostgreSQL 数据库集群。
D. 使⽤ pg_dump ⼯具备份 RDS for PostgreSQL 数据库。将备份恢复到新的 Aurora PostgreSQL 数据库集
群。
Question #602
解决⽅案架构师应该如何做才能以最⼩的努⼒满⾜这⼀要求？
新的 EC2 实例。
加 EBS 存储。
Topic 1
⼀家公司的基础设施由数百个使⽤ Amazon Elastic Block Store (Amazon EBS) 存储的 Amazon EC2 实例组
成。解决⽅案架构师必须确保每个 EC2 实例在灾难发⽣后都能恢复。
A. 对附加到每个 EC2 实例的 EBS 存储进⾏快照。创建 AWS CloudFormation 模板，以便从 EBS 存储启动
B. 对附加到每个 EC2 实例的 EBS 存储进⾏快照。使⽤ AWS Elastic Beanstalk 根据 EC2 模板设置环境并附
C. 使⽤ AWS Backup 为整个 EC2 实例组设置备份计划。使⽤ AWS Backup API 或 AWS CLI 可以加快多个
EC2 实例的恢复过程。
D. 创建⼀个 AWS Lambda 函数，⽤于对附加到每个 EC2 实例的 EBS 存储进⾏快照，并复制 Amazon 系统
映像 (AMI)。创建另⼀个 Lambda 函数，⽤于使⽤复制的 AMI 执⾏恢复操作，并将 EBS 存储附加到实例。
https://examlearn.online
[2026/05]
Question #603
Topic 1
⼀家公司最近迁移到了 AWS 云平台。该公司需要⼀个⽆服务器解决⽅案，⽤于⼤规模并⾏按需处理半结构化数
据集。该数据集包含⽇志、媒体⽂件、销售交易记录和物联⽹传感器数据，存储在 Amazon S3 中。该公司希望
该解决⽅案能够并⾏处理数据集中的数千个条⽬。
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
A. 使⽤ AWS Step Functions 的内联模式映射状态来并⾏处理数据。
B. 使⽤ AWS Step Functions 的分布式模式映射状态来并⾏处理数据。
C. 使⽤ AWS Glue 并⾏处理数据。
D. 使⽤多个 AWS Lambda 函数并⾏处理数据。
Question #604
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司将在 6 周内将 10 PB 的数据迁移到 Amazon S3。其现有数据中⼼拥有 500 Mbps 的互联⽹上⾏链路带
宽。其他本地应⽤程序也共享该上⾏链路。该公司可以使⽤ 80% 的互联⽹带宽来完成此次⼀次性迁移任务。
A. 配置 AWS DataSync 将数据迁移到 Amazon S3 并⾃动验证数据。
B. 使⽤ rsync 将数据直接传输到 Amazon S3。
C. 使⽤ AWS CLI 和多个复制进程将数据直接发送到 Amazon S3。
D. 订购多个 AWS Snowball 设备。将数据复制到这些设备。将这些设备发送给 AWS，以便将数据复制到
Amazon S3。
https://examlearn.online
[2026/05]
Question #605
Topic 1
⼀家公司拥有多台本地部署的互联⽹⼩型计算机系统接⼝ (ISCSI) ⽹络存储服务器。该公司希望通过迁移到 AWS
云来减少这些服务器的数量。解决⽅案架构师必须确保对常⽤数据的低延迟访问，并尽可能减少对本地服务器的
依赖，同时尽可能减少基础设施变更。
哪种解决⽅案能够满⾜这些要求？
A. 部署 Amazon S3 ⽂件⽹关。
B. 部署 Amazon Elastic Block Store (Amazon EBS) 存储，并将备份备份到 Amazon S3。
C. 部署⼀个配置了存储卷的 AWS Storage Gateway 卷⽹关。
D. 部署⼀个配置了缓存卷的 AWS Storage Gateway 卷⽹关。
Question #606
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀位解决⽅案架构师正在设计⼀个应⽤程序，允许业务⽤户将对象上传到 Amazon S3。该解决⽅案需要最⼤限度
地提⾼对象的持久性。对象还必须能够随时访问，且访问时间不受限制。⽤户会在对象上传后的前 30 天内频繁
访问，但访问超过 30 天的对象的可能性会⼤⼤降低。
A. 将所有对象存储在 S3 Standard 中，并设置 S3 ⽣命周期规则，在 30 天后将对象迁移到 S3 Glacier。
B. 将所有对象存储在 S3 标准中，并设置 S3 ⽣命周期规则，在 30 天后将对象转换为 S3 标准-不频繁访问
(S3 标准-IA)。
C. 将所有对象存储在 S3 标准存储中，并设置 S3 ⽣命周期规则，在 30 天后将对象转换为 S3 单区 - 不频繁
访问 (S3 单区 - IA)。
D. 将所有对象存储在 S3 智能分层中，并设置 S3 ⽣命周期规则，在 30 天后将对象转换为 S3 标准-不频繁访
问 (S3 Standard-IA)。
https://examlearn.online
[2026/05]
Question #607
Topic 1
⼀家公司已将其两层应⽤程序从本地数据中⼼迁移到 AWS 云。数据层是 Amazon RDS for Oracle 的多可⽤区部
署，配备 12 TB 通⽤型 SSD Amazon Elastic Block Store (Amazon EBS) 存储。该应⽤程序旨在处理数据库中
的⽂档，并将⽂档存储为平均⼤⼩为 6 MB 的⼆进制⼤对象 (BLOB)。
随着时间的推移，数据库⼤⼩不断增⻓，导致性能下降和存储成本上升。该公司必须提⾼数据库性能，并需要⼀
个⾼可⽤性和⾼弹性的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 减⼩ RDS 数据库实例⼤⼩。将存储容量增加到 24 TiB。将存储类型更改为磁性存储。
B. 增加 RDS 数据库实例⼤⼩。将存储容量增加到 24 Ti。将存储类型更改为预置 IOPS。
C. 创建⼀个 Amazon S3 存储桶。更新应⽤程序，将⽂档存储在 S3 存储桶中。将对象元数据存储在现有数据
库中。
D. 创建 Amazon DynamoDB 表。更新应⽤程序以使⽤ DynamoDB。使⽤ AWS 数据库迁移服务 (AWS
DMS) 将数据从 Oracle 数据库迁移到 DynamoDB。
Question #608
解决⽅案架构师应该如何满⾜这些要求？
含已注册的 IP 地址。
册的 IP 地址。
Topic 1
⼀家公司拥有⼀款应⽤程序，服务于遍布全球 20,000 多个零售⻔店的客户。该应⽤程序包含后端 Web 服务，这
些服务通过 HTTPS 协议在 443 端⼝上公开。该应⽤程序托管在 Amazon EC2 实例上，并由应⽤程序负载均衡
器 (ALB) 提供⽀持。各零售⻔店通过公共互联⽹与该 Web 应⽤程序通信。该公司允许每个零售⻔店注册其本地
ISP 分配的 IP 地址。
该公司的安全团队建议通过限制访问权限，仅允许零售⻔店注册的 IP 地址访问应⽤程序端点，从⽽提⾼安全性。
A. 将 AWS WAF Web ACL 与 ALB 关联。在 ALB 上使⽤ IP 规则集过滤流量。更新规则中的 IP 地址，使其包
B. 部署 AWS Firewall Manager 来管理 AL 配置防⽕墙规则以限制流向 AL 的流量 修改防⽕墙规则以包含已注
C. 将 IP 地址存储在 Amazon DynamoDB 表中。在 ALB 上配置 AWS Lambda 授权函数，以验证传⼊请求是
否来⾃已注册的 IP 地址。
D. 在包含 ALB 公⽹接⼝的⼦⽹上配置⽹络 ACL。使⽤每个已注册 IP 地址的条⽬更新⽹络 ACL 的⼊⼝规则。
https://examlearn.online
[2026/05]
Question #609
Topic 1
⼀家公司正在使⽤ AWS Lake Formation 在 AWS 上构建数据分析平台。该平台将从 Amazon S3 和 Amazon
RDS 等不同来源提取数据。该公司需要⼀个安全的解决⽅案来防⽌访问包含敏感信息的数据部分。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 创建⼀个 IAM ⻆⾊，该⻆⾊包含访问 Lake Formation 表的权限。
B. 创建数据筛选器以实现⾏级安全性和单元格级安全性。
C. 创建⼀个 AWS Lambda 函数，在 Lake Formation 摄取数据之前删除敏感信息。
D. 创建⼀个 AWS Lambda 函数，定期查询并从 Lake Formation 表中删除敏感信息。
Question #610
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司部署了运⾏在 VPC 中的 Amazon EC2 实例。这些 EC2 实例将源数据加载到 Amazon S3 存储桶中，以
便将来进⾏处理。根据合规性法规，这些数据不得通过公共互联⽹传输。公司本地数据中⼼的服务器将使⽤运⾏
在 EC2 实例上的应⽤程序的输出。
A. 为 Amazon EC2 部署接⼝ VPC 端点。在公司和 VPC 之间创建 AWS 站点到站点 VPN 连接。
B. 为 Amazon S3 部署⽹关 VPC 终端节点。在本地⽹络和 VPC 之间建⽴ AWS Direct Connect 连接。
C. 从 VPC 到 S3 存储桶建⽴ AWS Transit Gateway 连接。在公司和 VPC 之间创建 AWS Site-to-Site VPN
连接。
D. 设置具有通往 NAT ⽹关路由的代理 EC2 实例。配置代理 EC2 实例以获取 S3 数据并提供给应⽤程序实
例。
https://examlearn.online
[2026/05]
Question #611
Topic 1
⼀家公司有⼀个基于 REST 接⼝的应⽤程序，可以近乎实时地从第三⽅供应商接收数据。接收到数据后，应⽤程
序会对其进⾏处理并存储以供进⼀步分析。该应⽤程序运⾏在 Amazon EC2 实例上。第三⽅
供应商在向该应⽤程序发送数据时经常收到 503 服务不可⽤错误。当数据量激增时，计算能⼒达到其最⼤限制，
应⽤程序⽆法处理所有请求。
解决⽅案架构师应该推荐哪种设计⽅案以提供更具可扩展性的解决⽅案？
A. 使⽤ Amazon Kinesis Data Streams 摄取数据。使⽤ AWS Lambda 函数处理数据。
B. 在现有应⽤程序之上使⽤ Amazon API Gateway。为第三⽅供应商创建带有配额限制的使⽤计划。
C. 使⽤ Amazon Simple Notification Service (Amazon SNS) 来接收数据。将 EC2 实例放在应⽤程序负载
均衡器后⾯的⾃动扩展组中。
D. 将应⽤程序重新打包为容器。使⽤ Amazon Elastic Container Service (Amazon ECS) 部署应⽤程序，启
动类型选择 EC2，并使⽤⾃动扩展组。
Question #612
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司有⼀个应⽤程序运⾏在私有⼦⽹中的 Amazon EC2 实例上。该应⽤程序需要处理来⾃ Amazon S3 存储
桶的敏感信息。该应⽤程序不得使⽤互联⽹连接到 S3 存储桶。
A. 配置互联⽹⽹关。更新 S3 存储桶策略，允许通过互联⽹⽹关访问。更新应⽤程序以使⽤新的互联⽹⽹关。
B. 配置 VPN 连接。更新 S3 存储桶策略，允许通过 VPN 连接访问。更新应⽤程序以使⽤新的 VPN 连接。
C. 配置 NAT ⽹关。更新 S3 存储桶策略，允许通过 NAT ⽹关访问。更新应⽤程序，使其使⽤新的 NAT ⽹
关。
D. 配置 VPC 端点。更新 S3 存储桶策略，允许从 VPC 端点访问。更新应⽤程序以使⽤新的 VPC 端点。
https://examlearn.online
[2026/05]
Question #613
Topic 1
⼀家公司使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 运⾏容器应⽤程序。EKS 集群将敏感信息存
储在 Kubernetes Secrets 对象中。该公司希望确保这些信息已加密。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤容器应⽤程序通过 AWS Key Management Service (AWS KMS) 对信息进⾏加密。
B. 使⽤ AWS Key Management Service (AWS KMS) 在 EKS 集群中启⽤密钥加密。
C. 实现 AWS Lambda 函数，使⽤ AWS Key Management Service (AWS KMS) 对信息进⾏加密。
D. 使⽤ AWS Systems Manager Parameter Store 通过 AWS Key Management Service (AWS KMS) 对信
息进⾏加密。
Question #614
⼀家公司正在设计⼀个新的多层 Web 应⽤程序，该应⽤程序包含以下组件：
哪种解决⽅案能够满⾜这些要求？
• 运⾏在 Amazon EC2 实例上的 Web 服务器和应⽤程序服务器（作为 Auto Scaling 组的⼀部分）
；• ⽤于数据存储的 Amazon RDS 数据库实例。
解决⽅案架构师需要限制对应⽤程序服务器的访问，以便只有 Web 服务器才能访问它们。
Topic 1
A. 在应⽤服务器前端部署 AWS PrivateLink。配置⽹络访问控制列表 (ACL)，仅允许 Web 服务器访问应⽤服
务器。
B. 在应⽤服务器前端部署 VPC 端点。配置安全组，仅允许 Web 服务器访问应⽤服务器。
C. 部署⽹络负载均衡器，⽬标组包含应⽤服务器的⾃动扩展组。配置⽹络访问控制列表 (ACL)，仅允许 Web
服务器访问应⽤服务器。
D. 部署⼀个应⽤程序负载均衡器，其⽬标组包含应⽤程序服务器的⾃动扩展组。配置安全组，仅允许 Web 服
务器访问应⽤程序服务器。
https://examlearn.online
[2026/05]
Question #615
Topic 1
⼀家公司在 Amazon Elastic Kubernetes Service (Amazon EKS) 上运⾏⼀个关键的⾯向客户的应⽤程序。该应
⽤程序采⽤微服务架构。该公司需要实现⼀个解决⽅案，将应⽤程序的指标和⽇志集中收集、聚合和汇总到⼀个
统⼀的位置。
哪个解决⽅案满⾜这些要求？
A. 在现有 EKS 集群中运⾏ Amazon CloudWatch 代理。在 CloudWatch 控制台中查看指标和⽇志。
B. 在现有 EKS 集群中运⾏ AWS App Mesh。在 App Mesh 控制台中查看指标和⽇志。
C. 配置 AWS CloudTrail 以捕获数据事件。使⽤ Amazon OpenSearch Service 查询 CloudTrail。
D. 在现有 EKS 集群中配置 Amazon CloudWatch Container Insights。在 CloudWatch 控制台中查看指标和
⽇志。
Question #616
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司已将其最新产品部署在 AWS 上。该产品运⾏在⽹络负载均衡器 (NLB) 后⾯的⾃动扩展组中。该公司将
产品对象存储在 Amazon S3 存储桶中。
该公司最近遭受了针对其系统的恶意攻击。该公司需要⼀个解决⽅案，能够持续监控 AWS 账户、⼯作负载以及
对 S3 存储桶的访问模式中的恶意活动。该解决⽅案还必须报告可疑活动，并在仪表板上显示相关信息。
A. 配置 Amazon Macie 以监控并将结果报告给 AWS Config。
B. 配置 Amazon Inspector 以监控并将发现结果报告给 AWS CloudTrail。
C. 配置 Amazon GuardDuty 以监控并将发现结果报告给 AWS Security Hub。
D. 配置 AWS Config 以监控并将结果报告给 Amazon EventBridge。
https://examlearn.online
[2026/05]
Question #617
Topic 1
⼀家公司希望将本地数据中⼼迁移到 AWS。该数据中⼼托管着⼀台存储服务器，该服务器使⽤基于 NFS 的⽂件
系统存储数据。该存储服务器存储了 200 GB 的数据。该公司需要在不中断现有服务的情况下迁移数据。AWS 中
的多个资源必须能够使⽤ NFS 协议访问这些数据。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 为 Lustre ⽂件系统创建 Amazon FSx。
B. 创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。
C. 创建⼀个 Amazon S3 存储桶来接收数据。
D. ⼿动使⽤操作系统复制命令将数据推送到 AWS ⽬标位置。
E. 在本地数据中⼼安装 AWS DataSync 代理。在本地位置和 AWS 之间使⽤ DataSync 任务。
Question #618
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望在其位于美国东部 1 区（us-east-1）的 Amazon EC2 实例上使⽤ Amazon FSx for Windows ⽂件
服务器，这些实例挂载了⼀个 SMB ⽂件共享卷。该公司针对计划内系统维护或计划外服务中断设定了 5 分钟的
恢复点⽬标 (RPO)。该公司需要将⽂件系统复制到美国⻄部 2 区（us-west-2）。复制的数据在 5 年内不得被任
何⽤户删除。
A. 在 us-east-1 区域创建⼀个 FSx for Windows ⽂件服务器⽂件系统，部署类型为 Single-AZ 2。使⽤ AWS
Backup 创建每⽇备份计划，其中包含⼀条备份规则，将备份复制到 us-west-2 区域。在 us-west-2 区域配
置 AWS Backup Vault Lock 的合规模式，并设置⽬标存储库的最⼩期限为 5 年。
B. 在 us-east-1 区域创建⼀个 FSx for Windows ⽂件服务器⽂件系统，并采⽤多可⽤区部署类型。使⽤
AWS Backup 创建每⽇备份计划，其中包含⼀条备份规则，将备份复制到 us-west-2 区域。在 us-west-2 区
域配置 AWS Backup Vault Lock 的治理模式，并指定⼀个⽬标存储库。配置最短期限为 5 年。
C. 在 us-east-1 区域创建⼀个 FSx for Windows ⽂件服务器⽂件系统，并采⽤多可⽤区部署类型。使⽤
AWS Backup 创建每⽇备份计划，其中包含⼀条备份规则，将备份复制到 us-west-2 区域。在 us-west-2 区
域为⽬标存储库配置 AWS Backup Vault Lock 的合规模式。配置最短期限为 5 年。
D. 在 us-east-1 区域创建⼀个 FSx for Windows ⽂件服务器⽂件系统，部署类型为 Single-AZ 2。使⽤ AWS
Backup 创建每⽇备份计划，其中包含⼀条备份规则，将备份复制到 us-west-2 区域。在 us-west-2 区域配
置 AWS Backup Vault Lock 的治理模式，⽬标存储库设置为 Vault Lock。配置最短期限为 5 年。
https://examlearn.online
[2026/05]
Question #619
Topic 1
⼀位解决⽅案架构师正在为⼀家公司设计安全解决⽅案，该公司希望通过 AWS Organizations 为开发⼈员提供独
⽴的 AWS 账户，同时还要保持标准的安全控制。由于每个开发⼈员都将拥有对其⾃身账户的 AWS 账户根⽤户级
别的访问权限，因此解决⽅案架构师希望确保应⽤于新开发⼈员账户的强制性 AWS CloudTrail 配置不会被修
改。
以下哪项操作满⾜这些要求？
A. 创建⼀个 IAM 策略，禁⽌对 CloudTrail 进⾏更改，并将其附加到 root ⽤户。
B. 在启⽤了组织跟踪选项的开发者帐户中，在 CloudTrail 中创建新跟踪。
C. 创建⼀个服务控制策略 (SCP)，禁⽌对 CloudTrail 进⾏更改，并将其附加到开发⼈员帐户。
D. 为 CloudTrail 创建⼀个服务相关⻆⾊，并设置策略条件，仅允许从管理账户中的 Amazon 资源名称 (ARN)
进⾏更改。
Question #620
A. 实例存储卷
Topic 1
⼀家公司计划在 AWS 云上部署⼀个业务关键型应⽤程序。该应⽤程序需要持久存储以及稳定、低延迟的性能。
解决⽅案架构师应该推荐哪种类型的存储来满⾜这些要求？
B. Amazon ElastiCache for Memcached 集群
C. 已配置 IOPS SSD Amazon Elastic Block Store (Amazon EBS) 卷
D. 吞吐量优化型硬盘 Amazon Elastic Block Store (Amazon EBS) 卷
https://examlearn.online
[2026/05]
Question #621
Topic 1
⼀家在线照⽚分享公司将其照⽚存储在位于 us-west-1 区域的 Amazon S3 存储桶中。该公司需要将所有新照⽚
的副本存储在 us-east-1 区域。
哪种解决⽅案能够以最⼩的运维⼯作量满⾜此要求？
A. 在 us-east-1 区域创建第⼆个 S3 存储桶。使⽤ S3 跨区域复制将照⽚从现有 S3 存储桶复制到第⼆个 S3
存储桶。
B. 为现有的 S3 存储桶创建跨域资源共享 (CORS) 配置。在 CORS 规则的 AllowedOrigin 元素中指定 us
east-1。
C. 在 us-east-1 区域（跨越多个可⽤区）创建第⼆个 S3 存储桶。创建 S3 ⽣命周期规则，将照⽚保存到第⼆
个 S3 存储桶中。
D. 在 us-east-1 区域创建第⼆个 S3 存储桶。配置 S3 对象创建和更新事件的通知，以调⽤ AWS Lambda 函
数将照⽚从现有 S3 存储桶复制到第⼆个 S3 存储桶。
Question #622
Topic 1
⼀家公司正在为其⽤户开发⼀款新的 Web 应⽤程序。该应⽤程序由⼀个静态单⻚和⼀个持久数据库层组成。每天
早上 4 ⼩时内，该应⽤程序的访问量将达到数百万，⽽其余时间则只有⼏千名⽤户。公司的数据架构师要求能够
快速扩展其数据模式。
哪些解决⽅案能够满⾜这些要求并提供最佳的可扩展性？（选择两个。）
A. 部署 Amazon DynamoDB 作为数据库解决⽅案。按需配置容量。
B. 部署 Amazon Aurora 作为数据库解决⽅案。选择⽆服务器数据库引擎模式。
C. 部署 Amazon DynamoDB 作为数据库解决⽅案。确保已启⽤ DynamoDB ⾃动扩展。
D. 将静态内容部署到 Amazon S3 存储桶中。配置⼀个以 S3 存储桶为源的 Amazon CloudFront 分发。
E. 将静态内容的 Web 服务器部署到⾃动扩展组中的 Amazon EC2 实例集群上。配置这些实例定期从
Amazon Elastic File System (Amazon EFS) 卷刷新内容。
https://examlearn.online
[2026/05]
Question #623
Topic 1
⼀家公司使⽤ Amazon API Gateway 来管理其 REST API，供第三⽅服务提供商访问。该公司必须保护 REST
API 免受 SQL 注⼊和跨站脚本攻击。
满⾜这些要求的最⾼效解决⽅案是什么？
A. 配置 AWS Shield。
B. 配置 AWS WAF。
C. 使⽤ Amazon CloudFront 分发设置 API ⽹关。在 CloudFront 中配置 AWS Shield。
D. 设置 API Gateway 并部署 Amazon CloudFront。在 CloudFront 中配置 AWS WAF。
Question #624
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司希望为⽤户提供对 AWS 资源的访问权限。该公司拥有 1500 名⽤户，并通过企业⽹络上的 Active
Directory ⽤户组管理他们对本地资源的访问。但是，该公司不希望⽤户为了访问这些资源⽽维护另⼀个身份。解
决⽅案架构师必须在管理⽤户对 AWS 资源的访问的同时，保留对本地资源的访问。
A. 为公司中的每个⽤户创建⼀个 IAM ⽤户。将相应的策略附加到每个⽤户。
B. 将 Amazon Cognito 与 Active Directory ⽤户池结合使⽤。创建⻆⾊并附加相应的策略。
C. 定义跨账户⻆⾊并附加相应的策略。将这些⻆⾊映射到 Active Directory 组。
D. 配置基于安全断⾔标记语⾔ (SAML) 2.0 的联合身份验证。创建附加了相应策略的⻆⾊，并将这些⻆⾊映射
到 Active Directory 组。
https://examlearn.online
[2026/05]
Question #625
Topic 1
⼀家公司在其⽹站后部署了多个应⽤负载均衡器。该公司对其内容在全球范围内拥有不同的分发权限。解决⽅案
架构师需要确保⽤户能够访问到正确的内容，同时⼜不违反分发权限。
为了满⾜这些要求，解决⽅案架构师应该选择哪种配置？
A. 将 Amazon CloudFront 与 AWS WAF 配置在⼀起。
B. 配置应⽤程序负载均衡器与 AWS WAF 集成
C. 使⽤地理位置策略配置 Amazon Route 53
D. 配置 Amazon Route 53 的地理位置路由策略
Question #626
⼀家公司将数据存储在本地。数据量不断增⻓，已超出公司现有容量。
哪个解决⽅案能够满⾜这些要求？
Topic 1
该公司希望将数据从本地迁移到 Amazon S3 存储桶。该公司需要⼀个解决⽅案，能够在迁移后⾃动验证数据的
完整性。
A. 订购⼀台 AWS Snowball Edge 设备。配置 Snowball Edge 设备以执⾏到 S3 存储桶的在线数据传输。
B. 在本地部署 AWS DataSync 代理。配置 DataSync 代理以执⾏在线数据传输到 S3 存储桶的操作。
C. 在本地创建 Amazon S3 ⽂件⽹关。配置 S3 ⽂件⽹关以执⾏到 S3 存储桶的在线数据传输。
D. 在本地的 Amazon S3 Transfer Acceleration 中配置加速器。配置加速器以执⾏到 S3 存储桶的在线数据
传输。
https://examlearn.online
[2026/05]
Question #627
Topic 1
⼀家公司希望将两台 DNS 服务器迁移到 AWS。这两台服务器共托管约 200 个区域，平均每天接收 100 万个请
求。该公司希望在最⼤限度提⾼可⽤性的同时，最⼤限度降低与管理这两台服务器相关的运维开销。
解决⽅案架构师应该提出怎样的建议才能满⾜这些要求？
A. 在 Amazon Route 53 控制台中创建 200 个新的托管区域，并导⼊区域⽂件。
B. 启动单个⼤型 Amazon EC2 实例，导⼊区域图块。配置 Amazon CloudWatch 警报和通知，以便在出现任
何停机情况时向公司发出警报。
C. 使⽤ AWS 服务器迁移服务 (AWS SMS) 将服务器迁移到 AWS。配置 Amazon CloudWatch 警报和通知，
以便在出现任何停机情况时向公司发出警报。
D. 在跨两个可⽤区的⾃动扩展组中启动⼀个 Amazon EC2 实例。导⼊区域⽂件。将⾃动扩展组的期望容量设
置为 1，最⼤容量设置为 3。配置扩展警报，使其根据 CPU 利⽤率进⾏扩展。
Question #628
Topic 1
⼀家全球性公司在 AWS Organizations 的多个 AWS 账户中运⾏其应⽤程序。该公司的应⽤程序使⽤分段上传将
数据上传到跨 AWS 区域的多个 Amazon S3 存储桶。出于成本合规性考虑，该公司希望报告未完成的分段上传。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 配置 AWS Config，添加⼀条规则来报告不完整的多部分上传对象计数。
B. 创建服务控制策略 (SCP) 以报告不完整的多部分上传对象计数。
C. 配置 S3 Storage Lens 报告不完整的多部分上传对象计数。
D. 创建⼀个 S3 多区域访问点，⽤于报告不完整的多部分上传对象计数。
https://examlearn.online
[2026/05]
Question #629
Topic 1
⼀家公司在 Amazon RDS for MySQL 上运⾏⽣产数据库。出于安全合规性考虑，该公司希望升级数据库版本。
由于数据库包含关键数据，该公司希望找到⼀种快速升级并测试功能且不丢失任何数据的解决⽅案。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建 RDS ⼿动快照。升级到新版本的 Amazon RDS for MySQL。
B. 使⽤原⽣备份和恢复功能。将数据恢复到升级后的新版 Amazon RDS for MySQL。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据复制到升级后的新版 Amazon RDS for MySQL。
D. 使⽤ Amazon RDS 蓝绿部署来部署和测试⽣产变更。
Question #630
解决⽅案架构师应该如何以最具成本效益的⽅式解决这个问题？
Fargate 任务。
Topic 1
⼀位解决⽅案架构师正在创建⼀个数据处理作业，该作业每天运⾏⼀次，耗时最多可达 2 ⼩时。如果作业被中
断，则必须从头开始。
A. 创建⼀个脚本，该脚本在 Amazon EC2 预留实例上本地运⾏，并由 cron 作业触发。
B. 创建⼀个由 Amazon EventBridge 计划事件触发的 AWS Lambda 函数。
C. 使⽤由 Amazon EventBridge 计划事件触发的 Amazon Elastic Container Service (Amazon ECS)
D. 使⽤由 Amazon EventBridge 计划事件触发的 Amazon Elastic Container Service (Amazon ECS) 任务，
该任务运⾏在 Amazon EC2 上。
https://examlearn.online
[2026/05]
Question #631
Topic 1
⼀家社交媒体公司希望将其⽤户资料、关系和互动数据库存储在 AWS 云中。该公司需要⼀个应⽤程序来监控数
据库的任何更改。该应⽤程序需要分析数据实体之间的关系，并向⽤户提供建议。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ Amazon Neptune 存储信息。使⽤ Amazon Kinesis Data Streams 处理数据库中的更改。
B. 使⽤ Amazon Neptune 存储信息。使⽤ Neptune Streams 处理数据库中的更改。
C. 使⽤亚⻢逊量⼦账本数据库（Amazon QLDB）存储信息。使⽤亚⻢逊 Kinesis 数据流处理数据库中的更
改。
D. 使⽤亚⻢逊量⼦账本数据库（Amazon QLDB）存储信息。使⽤ Neptune Streams 处理数据库中的更改。
Question #632
Topic 1
⼀家公司正在开发⼀款新的应⽤程序，该应⽤程序将存储⼤量数据。这些数据将每⼩时进⾏分析，并由部署在多
个可⽤区的多个 Amazon EC2 Linux 实例进⾏修改。未来 6 个⽉内，所需的存储空间将持续增⻓。
解决⽅案架构师应该推荐哪种存储解决⽅案来满⾜这些需求？
A. 将数据存储在 Amazon S3 Glacier 中。更新 S3 Glacier 存储库策略，以允许访问应⽤程序实例。
B. 将数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷中。将 EBS 卷挂载到应⽤程序实例上。
C. 将数据存储在 Amazon Elastic File System (Amazon EFS) ⽂件系统中。将该⽂件系统挂载到应⽤程序实
例上。
D. 将数据存储在应⽤程序实例之间共享的 Amazon Elastic Block Store (Amazon EBS) 预置 IOPS 卷中。
https://examlearn.online
[2026/05]
Question #633
Topic 1
⼀家公司管理着⼀个应⽤程序，该应⽤程序将数据存储在 Amazon RDS for PostgreSQL 多可⽤区数据库实例
上。流量增加导致了性能问题。该公司确定数据库查询是性能缓慢的主要原因。
解决⽅案架构师应该如何改进应⽤程序的性能？
A. 从 多可⽤区备⽤副本提供读取流量。
B. 配置数据库实例以使⽤传输加速。
C. 从源数据库实例创建只读副本。从只读副本提供读取流量服务。
D. 在应⽤程序和 Amazon RDS 之间使⽤ Amazon Kinesis Data Firehose 来提⾼数据库请求的并发性。
Question #634
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司每天从各种机器收集 10 GB 的遥测数据。该公司将数据存储在源数据账户的 Amazon S3 存储桶中。
该公司聘请了多家咨询机构使⽤这些数据进⾏分析。每家机构的分析师都需要对数据拥有读取权限。该公司必须
选择⼀种能够最⼤限度提⾼安全性和运营效率的解决⽅案，才能共享源数据账户中的数据。
A. 配置 S3 全局表，为每个机构复制数据。
B. 将 S3 存储桶在限定时间内公开。仅通知相关机构。
C. 为机构拥有的帐户配置 S3 存储桶的跨帐户访问权限。
D. 为源数据帐户中的每位分析师设置⼀个 IAM ⽤户。授予每个⽤户对 S3 存储桶的访问权限。
https://examlearn.online
[2026/05]
Question #635
Topic 1
⼀家公司在其主 AWS 区域中使⽤ Amazon FSx for NetApp ONTAP 来存储 CIFS 和 NFS ⽂件共享。运⾏在
Amazon EC2 实例上的应⽤程序会访问这些⽂件共享。该公司需要在辅助区域中部署存储灾难恢复 (DR) 解决⽅
案。辅助区域中复制的数据需要使⽤与主区域相同的协议进⾏访问。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个 AWS Lambda 函数，将数据复制到 Amazon S3 存储桶。将该 S3 存储桶复制到辅助区域。
B. 使⽤ AWS Backup 创建 FSx for ONTAP 卷的备份。将卷复制到辅助区域。从备份创建新的 FSx for
ONTAP 实例。
C. 在辅助区域中创建 FSx for ONTAP 实例。使⽤ NetApp SnapMirror 将数据从主区域复制到辅助区域。
D. 创建 Amazon Elastic File System (Amazon EFS) 卷。将当前数据迁移到该卷。将该卷复制到辅助区域。
Question #636
ECS) 中处理该事件。
Topic 1
⼀个开发团队正在创建⼀个基于事件的应⽤程序，该应⽤程序使⽤ AWS Lambda 函数。当⽂件添加到 Amazon
S3 存储桶时，将⽣成事件。⽬前，该开发团队已将 Amazon Simple Notification Service (Amazon SNS) 配置
为来⾃ Amazon S3 的事件⽬标。
解决⽅案架构师应该如何以可扩展的⽅式处理来⾃ Amazon S3 的事件？
A. 创建⼀个 SNS 订阅，在 Lambda 中运⾏事件之前，在 Amazon Elastic Container Service (Amazon
B. 创建⼀个 SNS 订阅，在 Lambda 函数运⾏事件之前，先在 Amazon Elastic Kubernetes Service
(Amazon EKS) 中处理该事件。
C. 创建⼀个 SNS 订阅，将事件发送到 Amazon Simple Queue Service (Amazon SQS)。配置 SOS 队列以
触发 Lambda 函数。
D. 创建⼀个 SNS 订阅，将事件发送到 AWS 服务器迁移服务 (AWS SMS)。配置 Lambda 函数以轮询 SMS
事件。
https://examlearn.online
[2026/05]
Question #637
Topic 1
⼀位解决⽅案架构师正在设计⼀项基于 Amazon API Gateway 的新服务。该服务的请求模式不可预测，请求量可
能突然从每秒 0 个请求飙升⾄每秒 500 多个。⽬前需要持久化到后端数据库中的数据总量⼩于 1 GB，但未来增
⻓不可预测。数据可以通过简单的键值对请求进⾏查询。
以下哪两项 AWS 服务组合能够满⾜这些要求？
A. AWS Fargate
B. AWS Lambda
C. Amazon DynamoDB
D. Amazon EC2 ⾃动扩展
E. 兼容 MySQL 的 Amazon Aurora
Question #638
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司收集研究数据并与全球各地的员⼯共享。该公司希望将数据收集并存储在 Amazon S3 存储桶中，并在
AWS 云平台上进⾏处理。该公司将与员⼯共享这些数据。该公司需要⼀个安全可靠且运营成本最低的 AWS 云解
决⽅案。
A. 使⽤ AWS Lambda 函数创建 S3 预签名 URL。指导员⼯使⽤该 URL。
B. 为每位员⼯创建⼀个 IAM ⽤户。为每位员⼯创建⼀个 IAM 策略，以允许其访问 S3。指导员⼯使⽤ AWS
管理控制台。
C. 创建 S3 ⽂件⽹关。创建⽤于上传的共享⽂件夹和⽤于下载的共享⽂件夹。允许员⼯在其本地计算机上挂
载这些共享⽂件夹以使⽤ S3 ⽂件⽹关。
D. 配置 AWS Transfer Family SFTP 端点。选择⾃定义身份提供程序选项。使⽤ AWS Secrets Manager 管
理⽤户凭证。指导员⼯使⽤ Transfer Family。
https://examlearn.online
[2026/05]
Question #639
Topic 1
⼀家公司正在开发⼀款新的家具库存应⽤程序。该公司已将该应⽤程序部署在跨多个可⽤区的 Amazon EC2 实例
集群上。这些 EC2 实例运⾏在其 VPC 中的应⽤程序负载均衡器 (ALB) 之后。
解决⽅案架构师观察到，传⼊流量似乎偏向于某个特定的 EC2 实例，导致部分请求出现延迟。
解决⽅案架构师应该如何解决这个问题？
A. 在应⽤负载均衡器 (ALB) 上禁⽤会话亲和性（粘性会话）。
B. 将 ALB 替换为⽹络负载均衡器
C. 增加每个可⽤区中的 EC2 实例数量
D. 调整ALB⽬标⼈群的健康检查频率
Question #640
以下哪些操作组合可以实现此⽬的？（选择两项。）
Topic 1
⼀家公司有⼀个应⽤程序⼯作流，该⼯作流使⽤ AWS Lambda 函数从 Amazon S3 下载并解密⽂件。这些⽂件使
⽤ AWS Key Management Service (AWS KMS) 密钥进⾏加密。解决⽅案架构师需要设计⼀个解决⽅案，以确保
正确设置所需的权限。
A. 将 kms:decrypt 权限附加到 Lambda 函数的资源策略中
B. 在 KMS 密钥策略中授予 Lambda IAM ⻆⾊解密权限
C. 在 KMS 密钥的策略中授予 Lambda 资源策略的解密权限。
D. 创建具有 kms:decrypt 权限的新 IAM 策略，并将该策略附加到 Lambda 函数。
E. 创建⼀个具有 kms:decrypt 权限的新 IAM ⻆⾊，并将执⾏⻆⾊附加到 Lambda 函数。
https://examlearn.online
[2026/05]
Question #641
Topic 1
⼀家公司希望监控其 AWS 成本以进⾏财务审查。云运维团队正在 AWS Organizations 管理账户中设计⼀个架
构，⽤于查询所有成员账户的 AWS 成本和使⽤情况报告。该团队必须每⽉运⾏⼀次此查询，并提供详细的账单
分析。
哪种解决⽅案能够以最具可扩展性和成本效益的⽅式满⾜这些要求？
A. 在管理账户中启⽤成本和使⽤情况报告。将报告发送⾄ Amazon Kinesis。使⽤ Amazon EMR 进⾏分析。
B. 在管理账户中启⽤成本和使⽤情况报告。将报告发送到 Amazon S3，并使⽤ Amazon Athena 进⾏分析。
C. 为成员账户启⽤成本和使⽤情况报告。将报告发送到 Amazon S3，并使⽤ Amazon Redshift 进⾏分析。
D. 为成员账户启⽤成本和使⽤情况报告。将报告发送⾄ Amazon Kinesis。使⽤ Amazon QuickSight 进⾏分
析。
Question #642
解决⽅案架构师应该如何做才能满⾜这些要求？
Topic 1
⼀家公司希望在 AWS 云中属于⾃动扩展组的 Amazon EC2 实例上运⾏⼀个游戏应⽤程序。该应⽤程序将使⽤
UDP 数据包传输数据。该公司希望确保应⽤程序能够随着流量的增减⽽横向扩展或缩减。
A. 将⽹络负载均衡器连接到⾃动伸缩组。
B. 将应⽤程序负载均衡器附加到⾃动扩展组。
C. 部署具有加权策略的 Amazon Route 53 记录集，以便适当地路由流量。
D. 部署⼀个 NAT 实例，该实例配置了端⼝转发到⾃动扩展组中的 EC2 实例。
https://examlearn.online
[2026/05]
Question #643
Topic 1
⼀家公司在 AWS 上为其不同品牌运⾏多个⽹站。每个⽹站每天都会⽣成数⼗ GB 的⽹络流量⽇志。解决⽅案架
构师需要设计⼀个可扩展的解决⽅案，使公司开发⼈员能够分析公司所有⽹站的流量模式。开发⼈员将按需进⾏
此分析，每周⼀次，持续数⽉。该解决⽅案必须⽀持使⽤标准 SQL 进⾏查询。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将⽇志存储在 Amazon S3 中。使⽤ Amazon Athena 进⾏分析。
B. 将⽇志存储在 Amazon RDS 中。使⽤数据库客户端进⾏分析。
C. 将⽇志存储在 Amazon OpenSearch Service 中。使⽤ OpenSearch Service 进⾏分析。
D. 将⽇志存储在 Amazon EMR 集群中。使⽤受⽀持的开源框架进⾏基于 SQL 的分析。
Question #644
以下哪两项措施可以满⾜这些要求？
*.example.com 请求通配符证书。
Topic 1
⼀家国际公司为其运营的每个国家/地区都设置了⼀个⼦域名。这些⼦域名的格式分别为 example.com、
country1.example.com 和 country2.example.com。该公司的⼯作负载位于应⽤负载均衡器之后。该公司希望
对传输中的⽹站数据进⾏加密。
A. 使⽤ AWS Certificate Manager (ACM) 控制台为顶级域名 example.com 请求公共证书，并为
B. 使⽤ AWS Certificate Manager (ACM) 控制台为顶级域名 example.com 请求私有证书，并为
*.example.com 请求通配符证书。
C. 使⽤ AWS Certificate Manager (ACM) 控制台为顶级域名 example.com 请求公共证书和私有证书。
D. 通过电⼦邮件地址验证域名所有权。切换到 DNS 验证，⽅法是向 DNS 提供商添加所需的 DNS 记录。
E. 通过向 DNS 提供商添加所需的 DNS 记录来验证域名的所有权。
https://examlearn.online
[2026/05]
Question #645
Topic 1
⼀家公司需要在其本地密钥管理器中使⽤加密密钥。由于监管和合规性要求，该密钥管理器位于 AWS 云之外。
该公司希望使⽤保存在 AWS 云之外且⽀持来⾃不同供应商的各种外部密钥管理器的加密密钥来管理加密和解
密。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 使⽤由 CloudHSM 集群⽀持的 AWS CloudHSM 密钥存储。
B. 使⽤由外部密钥管理器⽀持的 AWS Key Management Service (AWS KMS) 外部密钥存储。
C. 使⽤默认的 AWS Key Management Service (AWS KMS) 托管密钥库。
D. 使⽤由 AWS CloudHSM 集群⽀持的⾃定义密钥库。
Question #646
哪种解决⽅案能够满⾜这些要求？
Topic 1
解决⽅案架构师需要在 AWS 云中托管⾼性能计算 (HPC) ⼯作负载。该⼯作负载将在数百个 Amazon EC2 实例
上运⾏，并需要并⾏访问共享⽂件系统以实现⼤型数据集的分布式处理。数据集将同时在多个实例上被访问。该
⼯作负载要求访问延迟在 1 毫秒以内。处理完成后，⼯程师需要访问数据集进⾏⼿动后处理。
A. 使⽤ Amazon Elastic File System (Amazon EFS) 作为共享⽂件系统。从 Amazon EFS 访问数据集。
B. 挂载⼀个 Amazon S3 存储桶作为共享⽂件系统。直接从 S3 存储桶执⾏后处理。
C. 使⽤ Amazon FSx for Lustre 作为共享⽂件系统。将该⽂件系统链接到 Amazon S3 存储桶以进⾏后处
理。
D. 配置 AWS Resource Access Manager 以共享 Amazon S3 存储桶，以便将其挂载到所有实例进⾏处理和
后处理。
https://examlearn.online
[2026/05]
Question #647
Topic 1
⼀家游戏公司正在构建⼀个具备 VoIP 功能的应⽤程序。该应⽤程序将为全球⽤户提供服务。该应⽤程序需要具备
⾼可⽤性，并能在 AWS 不同区域之间实现⾃动故障转移。该公司希望在不依赖⽤户设备上的 IP 地址缓存的情况
下，最⼤限度地降低⽤户延迟。
解决⽅案架构师应该如何满⾜这些要求？
A. 使⽤带有健康检查功能的 AWS Global Accelerator。
B. 使⽤ Amazon Route 53 和地理位置路由策略。
C. 创建⼀个包含多个源的 Amazon CloudFront 分发。
D. 创建⼀个使⽤基于路径路由的应⽤程序负载均衡器。
Question #648
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家天⽓预报公司需要处理数百GB的数据，且延迟必须低于毫秒级。该公司在其数据中⼼拥有⾼性能计算 (HPC)
环境，并希望扩展其预报能⼒。
解决⽅案架构师必须找到⼀种⾼可⽤性的云存储解决⽅案，该⽅案能够处理持续的⼤量吞吐量。存储在该解决⽅
案中的⽂件应可供数千个计算实例访问，这些实例将同时访问和处理整个数据集。
A. 使⽤ Amazon FSx 作为 Lustre 临时⽂件系统。
B. 使⽤ Amazon FSx 实现 Lustre 持久⽂件系统。
C. 使⽤ Amazon Elastic File System (Amazon EFS) 的突发吞吐量模式。
D. 使⽤ Amazon Elastic File System (Amazon EFS) 的预置吞吐量模式。
https://examlearn.online
[2026/05]
Question #649
Topic 1
⼀家电商公司在本地运⾏ PostgreSQL 数据库。该数据库使⽤⾼ IOPS 的 Amazon Elastic Block Store (Amazon
EBS) 块存储来存储数据。每⽇峰值 I/O 事务/秒不超过 15,000 IOPS。该公司希望将数据库迁移到 Amazon RDS
for PostgreSQL，并实现与磁盘存储容量⽆关的磁盘 IOPS 性能。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置通⽤ SSD (gp2) EBS 卷存储类型，并提供 15,000 IOPS。
B. 配置已配置 IOPS SSD (io1) EBS 卷存储类型，并配置 15,000 IOPS。
C. 配置通⽤ SSD (gp3) EBS 卷存储类型，并提供 15,000 IOPS。
D. 配置 EBS 磁卷类型以实现最⼤ IOPS。
Question #650
Topic 1
⼀家公司希望将其本地部署的 Microsoft SQL Server 企业版数据库迁移到 AWS。该公司的在线应⽤程序使⽤该
数据库处理交易。数据分析团队也使⽤同⼀个⽣产数据库来运⾏分析报告。该公司希望尽可能地迁移到托管服
务，以降低运营成本。
哪种解决⽅案能够以最低的运营成本满⾜这些要求？
A. 将 Microsoft SOL 服务器迁移到 Amazon RDS。使⽤只读副本进⾏报告。
B. 迁移到 Amazon EC2 上的 Microsoft SQL Server。使⽤ Always On 只读副本进⾏报表⽣成。
C. 迁移到 Amazon DynamoDB。使⽤ DynamoDB 按需副本进⾏报表⽣成。
D. 迁移到 Amazon Aurora MySQL。使⽤ Aurora 只读副本进⾏报表⽣成。
https://examlearn.online
[2026/05]
Question #651
Topic 1
⼀家公司在 Amazon S3 存储桶中存储⼤量图像⽂件。这些图像需要在前 180 天内随时可⽤。接下来的 180 天
内，图像访问频率较低。360 天后，图像需要归档，但必须能够应要求⽴即访问。5 年后，只有审计⼈员才能访
问这些图像。审计⼈员必须能够在 12 ⼩时内检索到这些图像。在此过程中，图像不能丢失。
开发⼈员将在前 180 天内使⽤ S3 标准存储。开发⼈员需要配置 S3 ⽣命周期规则。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 180 天后将对象迁移到 S3 单区-不频繁访问 (S3 One Zone-IA)，360 天后迁移到 S3 Glacier 即时检索，
5 年后迁移到 S3 Glacier 深度存档。
B. 180 天后将对象迁移到 S3 单区-不频繁访问 (S3 单区-IA)，360 天后迁移到 S3 Glacier 灵活检索，5 年后
迁移到 S3 Glacier 深度存档。
C. 180 天后将对象迁移到 S3 标准-不频繁访问 (S3 标准-IA)，360 天后迁移到 S3 Glacier 即时检索，5 年后
迁移到 S3 Glacier 深度存档。
D. 180 天后将对象迁移到 S3 标准-不频繁访问 (S3 标准-IA)，360 天后迁移到 S3 Glacier 灵活检索，5 年后
迁移到 S3 Glacier 深度存档。
Question #652
Topic 1
⼀家公司每天运⾏ 6 ⼩时的⼤型数据⼯作负载。该公司在处理过程中不能丢失任何数据。解决⽅案架构师正在设
计⼀个 Amazon EMR 集群配置来⽀持这项关键数据⼯作负载。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置⼀个⻓期运⾏的集群，其中主节点和核⼼节点运⾏在按需实例上，任务节点运⾏在竞价实例上。
B. 配置⼀个临时集群，其中主节点和核⼼节点运⾏在按需实例上，任务节点运⾏在竞价实例上。
C. 配置⼀个临时集群，其中主节点运⾏在按需实例上，核⼼节点和任务节点运⾏在竞价实例上。
D. 配置⼀个⻓期运⾏的集群，其中主节点运⾏在按需实例上，核⼼节点运⾏在竞价型实例上，任务节点运⾏
在竞价型实例上。
https://examlearn.online
[2026/05]
Question #653
⼀家公司维护着⼀个 Amazon RDS 数据库，该数据库将⽤户映射到成本中⼼。该公司在 AWS Organizations 的
⼀个组织中拥有账户。该公司需要⼀个解决⽅案，⽤于标记在该组织中特定 AWS 账户中创建的所有资源。该解
决⽅案必须使⽤创建该资源的⽤户的成本中⼼ ID 来标记每个资源。
哪个解决⽅案能够满⾜这些要求？
Topic 1
A. 将指定的 AWS 账户从管理账户移动到 Organizations 中的新组织单元 (OU)。创建服务控制策略 (SCP)，
要求所有现有资源在创建之前必须具有正确的成本中⼼标签。将此 SCP 应⽤到新的 OU。
B. 创建⼀个 AWS Lambda 函数，该函数在从 RDS 数据库查找相应的成本中⼼后，⽤于标记资源。配置⼀条
Amazon EventBridge 规则，使其响应 AWS CloudTrail 事件来调⽤该 Lambda 函数。
C. 创建⼀个 AWS CloudFormation 堆栈来部署 AWS Lambda 函数。配置 Lambda 函数，使其从 RDS 数据
库中查找相应的成本中⼼并标记资源。创建⼀个 Amazon EventBridge 计划规则来调⽤ CloudFormation 堆
栈。
D. 创建⼀个 AWS Lambda 函数，⽤于为资源添加默认值标签。配置⼀条 Amazon EventBridge 规则，使其
响应 AWS CloudTrail 事件，并在资源缺少成本中⼼标签时调⽤该 Lambda 函数。
https://examlearn.online
[2026/05]
Question #654
Topic 1
⼀家公司最近将其 Web 应⽤程序迁移到了 AWS 云。该公司使⽤ Amazon EC2 实例运⾏多个进程来托管该应⽤
程序。这些进程包括⼀个提供静态内容的 Apache Web 服务器。Apache Web 服务器向⼀个使⽤本地 Redis 服
务器管理⽤户会话的 PHP 应⽤程序发出请求。
该公司希望重新设计架构，以实现⾼可⽤性并使⽤ AWS 托管解决⽅案。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Elastic Beanstalk 托管静态内容和 PHP 应⽤程序。配置 Elastic Beanstalk 将其 EC2 实例部署
到公共⼦⽹中。分配⼀个公共 IP 地址。
B. 使⽤ AWS Lambda 托管静态内容和 PHP 应⽤程序。使⽤ Amazon API Gateway REST API 将请求代理到
Lambda 函数。设置 API Gateway 的 CORS 配置，使其响应域名。配置 Amazon ElastiCache for Redis 以
处理会话信息。
C. 将后端代码保留在 EC2 实例上。创建⼀个启⽤多可⽤区 (Multi-AZ) 的 Amazon ElastiCache for Redis 集
群。将 ElastiCache for Redis 集群配置为集群模式。将前端资源复制到 Amazon S3。配置后端代码以引⽤
EC2 实例。
D. 配置 Amazon CloudFront 分发，并将其指向⽤于托管静态内容的 S3 存储桶的 Amazon S3 端点。配置应
⽤程序负载均衡器，使其指向运⾏ PHP 应⽤程序 AWS Fargate 任务的 Amazon Elastic Container Service
(Amazon ECS) 服务。配置 PHP 应⽤程序以使⽤运⾏在多个可⽤区中的 Amazon ElastiCache for Redis 集
群。
Question #655
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⼀个 Web 应⽤程序，该实例位于⼀个具有⽬标组的 Auto Scaling 组中。该
公司将该应⽤程序设计为⽀持会话亲和性（粘性会话），以提供更好的⽤户体验。
该应⽤程序必须作为终端节点通过互联⽹公开访问。为了增强安全性，必须在终端节点上应⽤ Web 应⽤防⽕墙
(WAF)。必须在终端节点上配置会话亲和性（粘性会话）。
以下哪两项步骤组合可以满⾜这些要求？（选择两项。）
A. 创建公共⽹络负载均衡器。指定应⽤程序⽬标组。
B. 创建⽹关负载均衡器。指定应⽤程序⽬标组。
C. 创建公共应⽤程序负载均衡器。指定应⽤程序⽬标组。
D. 创建第⼆个⽬标组。向 EC2 实例添加弹性 IP 地址。
E. 在 AWS WAF 中创建 Web ACL。将 Web ACL 与端点关联。
https://examlearn.online
[2026/05]
Question #656
Topic 1
⼀家公司运营⼀个⽹站，⽤于存储历史事件的图⽚。⽹站⽤户需要能够根据图⽚中事件发⽣的年份进⾏搜索和查
看。平均⽽⾔，⽤户每年只会请求每张图⽚⼀到两次。该公司需要⼀个⾼可⽤性的解决⽅案来存储图⽚并将其交
付给⽤户。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将图像存储在 Amazon Elastic Block Store (Amazon EBS) 中。使⽤运⾏在 Amazon EC2 上的 Web 服务
器。
B. 将图像存储在 Amazon Elastic File System (Amazon EFS) 中。使⽤运⾏在 Amazon EC2 上的 Web 服务
器。
C. 将图⽚存储在 Amazon S3 Standard 中。使⽤ S3 Standard 通过静态⽹站直接提供图⽚。
D. 将图像存储在 Amazon S3 标准版（不频繁访问）（S3 Standard-IA）中。使⽤ S3 Standard-IA 通过静态
⽹站直接提供图像。
Question #657
解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司在 AWS Organizations 中拥有多个 AWS 账户，供不同的业务部⻔使⽤。该公司在全球各地设有多个办
事处。该公司需要更新安全组规则，以允许新的办事处使⽤ CIDR 范围，或移除组织内旧的 CIDR 范围。该公司
希望集中管理安全组规则，以最⼤限度地减少更新 CIDR 范围所需的管理开销。哪种
A. 在组织的管理帐户中创建 VPC 安全组。当需要更新 CIDR 范围时，更新安全组。
B. 创建⼀个由 VPC 客户管理的前缀列表，其中包含 CIDR 列表。使⽤ AWS Resource Access Manager
(AWS RAM) 在组织内共享此前缀列表。在组织内的安全组中使⽤此前缀列表。
C. 创建 AWS 托管前缀列表。使⽤ AWS Security Hub 策略强制整个组织更新安全组。使⽤ AWS Lambda 函
数在 CIDR 范围更改时⾃动更新前缀列表。
D. 在中央管理 AWS 账户中创建安全组。为整个组织创建 AWS 防⽕墙管理器通⽤安全组策略。将先前创建的
安全组选为该策略中的主要组。
https://examlearn.online
[2026/05]
Question #658
Topic 1
⼀家公司使⽤本地⽹络附加存储 (NAS) 系统为其⾼性能计算 (HPC) ⼯作负载提供⽂件共享。该公司希望将其对
延迟敏感的 HPC ⼯作负载及其存储迁移到 AWS 云。该公司必须能够从⽂件系统提供 NFS 和 SMB 多协议访问。
哪种解决⽅案能够以最低的延迟满⾜这些要求？（选择两个。）
A. 将计算优化型 EC2 实例部署到集群放置组中。
B. 将计算优化型 EC2 实例部署到分区放置组中。
C. 将 EC2 实例连接到 Amazon FSx for Lustre ⽂件系统。
D. 将 EC2 实例连接到 Amazon FSx for OpenZFS ⽂件系统。
E. 将 EC2 实例连接到 Amazon FSx for NetApp ONTAP ⽂件系统。
Question #659
Topic 1
⼀家公司正在迁移其数据中⼼，并希望在两周内将 50 TB 的数据安全地迁移到 AWS。现有数据中⼼与 AWS 之间
通过站点到站点 VPN 连接，⽬前 VPN 使⽤率已达 90%。
解决⽅案架构师应该使⽤哪项 AWS 服务来满⾜这些要求？
A. 使⽤ VPC 端点的 AWS DataSync
B. AWS Direct Connect
C. AWS Snowball 边缘存储优化
D. AWS 存储⽹关
https://examlearn.online
[2026/05]
Question #660
Topic 1
⼀家公司在 Amazon EC2 按需实例的⾃动扩展组中托管了⼀个应⽤程序。该应⽤程序的⾼峰时段每天固定。⽤户
反映，在⾼峰时段开始时应⽤程序性能缓慢。⾼峰时段开始 2-3 ⼩时后，应⽤程序运⾏恢复正常。该公司希望确
保应⽤程序在⾼峰时段开始时也能正常运⾏。
哪种解决⽅案能够满⾜这些要求？
A. 配置应⽤程序负载均衡器，以便将流量正确分配到各个实例。
B. 为⾃动扩展组配置动态扩展策略，以根据内存利⽤率启动新实例。
C. 为⾃动扩展组配置动态扩展策略，以根据 CPU 利⽤率启动新实例。
D. 为⾃动扩展组配置计划扩展策略，以便在⾼峰时段之前启动新实例。
Question #661
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司在 AWS 上运⾏连接到其 Amazon RDS 数据库的应⽤程序。这些应⽤程序在周末和⼀年中的⾼峰期需要
扩展。该公司希望更有效地扩展连接到该数据库的应⽤程序所需的数据库。
A. 使⽤带有连接池的 Amazon DynamoDB，并为数据库配置⽬标组。更改应⽤程序以使⽤ DynamoDB 端
点。
B. 使⽤ Amazon RDS Proxy 并为数据库设置⽬标组。更改应⽤程序以使⽤ RDS Proxy 终端节点。
C. 使⽤运⾏在 Amazon EC2 上的⾃定义代理作为数据库的中介。修改应⽤程序以使⽤该⾃定义代理终端节
点。
D. 使⽤ AWS Lambda 函数为数据库提供连接池，并配置⽬标组。修改应⽤程序以使⽤该 Lambda 函数。
https://examlearn.online
[2026/05]
Question #662
Topic 1
⼀家公司使⽤ AWS Cost Explorer 来监控其 AWS 成本。该公司注意到 Amazon Elastic Block Store (Amazon
EBS) 的存储和快照成本每⽉都在增加。然⽽，该公司并没有每⽉购买额外的 EBS 存储空间。该公司希望在当前
存储使⽤量下优化每⽉成本。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 使⽤ Amazon CloudWatch Logs 中的⽇志监控 Amazon EBS 的存储利⽤率。使⽤ Amazon EBS Elastic
Volumes 来减⼩ EBS 卷的⼤⼩。
B. 使⽤⾃定义脚本监控空间使⽤情况。使⽤ Amazon EBS 弹性卷来减⼩ EBS 卷的⼤⼩。
C. 删除所有过期和未使⽤的快照，以降低快照成本。
D. 删除所有⾮必要的快照。使⽤ Amazon 数据⽣命周期管理器，根据公司的快照策略要求创建和管理快照。
Question #663
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在 AWS 上开发⼀款新应⽤。该应⽤包含⼀个 Amazon Elastic Container Service (Amazon ECS) 集
群、⼀个存放应⽤资源的 Amazon S3 存储桶，以及⼀个存放应⽤数据集的 Amazon RDS for MySQL 数据库。
该数据集包含敏感信息。该公司希望确保只有 ECS 集群才能访问 RDS for MySQL 数据库和 S3 存储桶中的数
据。
A. 创建⼀个新的 AWS Key Management Service (AWS KMS) 客户管理密钥，⽤于加密 S3 存储桶和 RDS
for MySQL 数据库。确保 KMS 密钥策略包含 ECS 任务执⾏⻆⾊的加密和解密权限。
B. 创建⼀个由 AWS Key Management Service (AWS KMS) 管理的密钥，⽤于加密 S3 存储桶和 RDS for
MySQL 数据库。确保 S3 存储桶策略中指定 ECS 任务执⾏⻆⾊为⽤户。
C. 创建 S3 存储桶策略，将存储桶访问权限限制为 ECS 任务执⾏⻆⾊。为 Amazon RDS for MySQL 创建
VPC 终端节点。更新 RDS for MySQL 安全组，仅允许 ECS 集群在其上⽣成任务的⼦⽹进⾏访问。
D. 为 Amazon RDS for MySQL 创建 VPC 端点。更新 RDS for MySQL 安全组，仅允许 ECS 集群在其上⽣成
任务的⼦⽹进⾏访问。为 Amazon S3 创建 VPC 端点。更新 S3 存储桶策略，仅允许从 S3 VPC 端点进⾏访
问。
https://examlearn.online
[2026/05]
Question #664
Topic 1
⼀家公司有⼀个运⾏在本地的 Web 应⽤程序。该应⽤程序在⾼峰时段会出现延迟问题，每⽉发⽣两次。每次延迟
问题发⽣时，应⽤程序的 CPU 利⽤率会⽴即飙升⾄正常⽔平的 10 倍。
该公司希望将应⽤程序迁移到 AWS 以改善延迟，并希望在应⽤程序需求增加时⾃动扩展其规模。该公司计划使
⽤ AWS Elastic Beanstalk 进⾏应⽤程序部署。请问
哪种解决⽅案能够满⾜这些要求？
A. 配置 Elastic Beanstalk 环境，以在⽆限制模式下使⽤突发性能实例。配置环境以根据请求进⾏扩展。
B. 配置 Elastic Beanstalk 环境以使⽤计算优化实例。配置环境以根据请求进⾏扩展。
C. 配置 Elastic Beanstalk 环境以使⽤计算优化实例。配置环境以按计划进⾏扩展。
D. 配置 Elastic Beanstalk 环境，以在⽆限制模式下使⽤突发性能实例。配置环境以根据预测指标进⾏扩展。
Question #665
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司拥有遍布全球的客户。该公司希望利⽤⾃动化技术来保护其系统和⽹络基础设施。该公司的安全团队必
须能够跟踪和审计基础设施的所有增量变更。
A. 使⽤ AWS Organizations 设置基础设施。使⽤ AWS Config 跟踪变更。
B. 使⽤ AWS CloudFormation 设置基础设施。使⽤ AWS Config 跟踪变更。
C. 使⽤ AWS Organizations 设置基础设施。使⽤ AWS Service Catalog 跟踪变更。
D. 使⽤ AWS CloudFormation 设置基础设施。使⽤ AWS Service Catalog 跟踪变更。
https://examlearn.online
[2026/05]
Question #666
Topic 1
⼀家初创公司在亚⻢逊 EC2 实例上托管了⼀个⾯向客户的⽹站。该⽹站包含⼀个⽆状态的 Python 应⽤程序和⼀
个 MySQL 数据库。该⽹站的流量很⼩。公司担⼼实例的可靠性，需要迁移到⾼可⽤性架构。公司⽆法修改应⽤
程序代码。
解决⽅案架构师应该采取哪些措施组合来实现⽹站的⾼可⽤性？（选择两项。）
A. 在每个使⽤的可⽤区中配置⼀个互联⽹⽹关。
B. 将数据库迁移到 Amazon RDS for MySQL 多可⽤区数据库实例。
C. 将数据库迁移到 Amazon DynamoDB，并启⽤ DynamoDB ⾃动扩展。
D. 使⽤ AWS DataSync 在多个 EC2 实例之间同步数据库数据。
E. 创建⼀个应⽤程序负载均衡器，将流量分配到分布在两个可⽤区中的 EC2 实例的⾃动扩展组。
Question #667
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在进⾏⼀项为期多年的迁移项⽬，将其数据和应⽤程序迁移到 AWS。该公司希望能够从其 AWS 区域
和本地位置安全地访问 Amazon S3 上的数据。数据不得通过互联⽹传输。该公司已在其 AWS 区域和本地位置之
间建⽴了 AWS Direct Connect 连接。
A. 为 Amazon S3 创建⽹关终端节点。使⽤⽹关终端节点安全地访问来⾃区域和本地位置的数据。
B. 在 AWS Transit Gateway 中创建⼀个⽹关，以便从区域和本地位置安全地访问 Amazon S3。
C. 为 Amazon S3 创建接⼝端点。使⽤接⼝端点安全地访问来⾃区域和本地位置的数据。
D. 使⽤ AWS Key Management Service (AWS KMS) 密钥从区域和本地位置安全地访问数据。
https://examlearn.online
[2026/05]
Question #668
Topic 1
⼀家公司在 AWS Organizations 中创建了⼀个新的组织。该组织拥有多个账户，供公司各个开发团队使⽤。开发
团队成员使⽤ AWS IAM Identity Center（AW S 单点登录）访问这些账户。对于公司的每个应⽤程序，开发团队
必须使⽤预定义的应⽤程序名称来标记创建的资源。
解决⽅案架构师需要设计⼀个解决⽅案，使开发团队只有在应⽤程序名称标签具有已批准的值时才能创建资源。
哪个解决⽅案能够满⾜这些要求？
A. 创建⼀个 IAM 组，该组具有条件允许策略，要求在创建资源时指定应⽤程序名称标签。
B. 创建⼀个跨账户⻆⾊，该⻆⾊对任何具有应⽤程序名称标签的资源都具有拒绝策略。
C. 在 AWS 资源组中创建⼀个资源组，以验证标签是否已应⽤于所有账户中的所有资源。
D. 在“组织”中创建⼀个标签策略，其中包含允许的应⽤程序名称列表。
Question #669
Topic 1
⼀家公司使⽤ Amazon RDS for PostgreSQL 运⾏其数据库。该公司希望找到⼀种安全的解决⽅案来管理主⽤户
密码，每 30 天轮换⼀次密码。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 使⽤ Amazon EventBridge 安排⾃定义 AWS Lambda 函数每 30 天轮换⼀次密码。
B. 使⽤ AWS CLI 中的 modify-db-instance 命令更改密码。
C. 将 AWS Secrets Manager 与 Amazon RDS for PostgreSQL 集成，以实现密码轮换⾃动化。
D. 将 AWS Systems Manager Parameter Store 与 Amazon RDS for PostgreSQL 集成，以实现密码轮换⾃
动化。
https://examlearn.online
[2026/05]
Question #670
Topic 1
⼀家公司每周对⼀个使⽤ Amazon DynamoDB 表的应⽤程序进⾏测试，每次测试持续 4 ⼩时。该公司知道在测
试期间，该应⽤程序每秒对该表执⾏多少次读写操作。该公司⽬前没有将 DynamoDB ⽤于任何其他⽤例。解决
⽅案架构师需要优化该表的成本。
哪种解决⽅案能够满⾜这些要求？
A. 选择按需模式。相应地更新读取和写⼊容量单位。
B. 选择预置模式。相应地更新读取和写⼊容量单位。
C. 购买 DynamoDB 预留容量，期限为 1 年。
D. 购买 DynamoDB 预留容量，期限为 3 年。
Question #671
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏其应⽤程序。该公司定期对其 AWS 成本进⾏财务评估。该公司最近发现了
⼀些异常⽀出。
该公司需要⼀个解决⽅案来防⽌这些异常⽀出。该解决⽅案必须能够监控成本，并在出现异常⽀出时通知相关利
益⽅。
A. 使⽤ AWS Budgets 模板创建零⽀出预算。
B. 在 AWS 计费和成本管理控制台中创建 AWS 成本异常检测监控器。
C. 创建 AWS 定价计算器，估算当前正在运⾏的⼯作负载的定价详情。
D. 使⽤ Amazon CloudWatch 监控成本并识别异常⽀出。
https://examlearn.online
[2026/05]
Question #672
Topic 1
⼀家营销公司在亚⻢逊S3中收到来⾃营销活动的⼤量新的点击流数据。该公司需要快速分析亚⻢逊S3中的点击流
数据，然后确定是否需要在数据管道中进⼀步处理这些数据。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 在 Spark ⽬录中创建外部表。在 AWS Glue 中配置作业以查询数据。
B. 配置 AWS Glue 爬⾍程序来爬取数据。配置 Amazon Athena 来查询数据。
C. 在 Hive 元数据存储中创建外部表。在 Amazon EMR 中配置 Spark 作业以查询数据。
D. 配置 AWS Glue 爬⾍程序来抓取数据。配置 Amazon Kinesis Data Analytics 以使⽤ SQL 查询数据。
Question #673
哪种解决⽅案能够满⾜这些要求？
Glacier 深度归档。
Topic 1
⼀家公司在其数据中⼼运⾏着⼀台 SMB ⽂件服务器。该⽂件服务器存储着公司经常访问的⼤⽂件，这些⽂件会
在创建⽇期后的 7 天内保留。7 天后，公司需要能够在 24 ⼩时内访问这些⽂件。
A. 使⽤ AWS DataSync 将 SMB ⽂件服务器上超过 7 天的数据复制到 AWS。
B. 创建 Amazon S3 ⽂件⽹关以增加公司存储空间。创建 S3 ⽣命周期策略，以便在 7 天后将数据迁移到 S3
C. 创建 Amazon FSx ⽂件⽹关以增加公司存储空间。创建 Amazon S3 ⽣命周期策略，以便在 7 天后迁移数
据。
D. 为每个⽤户配置对 Amazon S3 的访问权限。创建 S3 ⽣命周期策略，以便在 7 天后将数据迁移到 S3
Glacier 灵活检索。
https://examlearn.online
[2026/05]
Question #674
Topic 1
⼀家公司在 Amazon EC2 实例的⾃动扩展组中运⾏⼀个 Web 应⽤程序。该应⽤程序使⽤运⾏在 Amazon RDS
for PostgreSQL 数据库实例上的数据库。当流量增加时，应⽤程序的性能会下降。在流量⾼峰期，数据库会承受
很⼤的读取负载。
解决⽅案架构师应该采取哪些措施来解决这些性能问题？（选择两项。）
A. 为数据库实例启⽤⾃动扩缩容。
B. 为数据库实例创建只读副本。配置应⽤程序将读取流量发送到只读副本。
C. 将数据库实例转换为多可⽤区数据库实例部署。配置应⽤程序将读取流量发送到备⽤数据库实例。
D. 创建⼀个 Amazon ElastiCache 集群。配置应⽤程序以将查询结果缓存到 ElastiCache 集群中。
E. 配置⾃动扩展组⼦⽹，以确保 EC2 实例与数据库实例位于同⼀可⽤区。
Question #675
CLI 删除快照。
Topic 1
⼀家公司使⽤ Amazon EC2 实例和 Amazon Elastic Block Store (Amazon EBS) 卷来运⾏应⽤程序。为了满⾜
合规性要求，该公司每天都会为每个 EBS 卷创建⼀个快照。该公司希望实施⼀种架构，以防⽌意外删除 EBS 卷
快照。该解决⽅案不得更改存储管理员⽤户的管理权限。
哪种解决⽅案能够以最少的管理⼯作量满⾜这些要求？
A. 创建⼀个具有删除快照权限的 IAM ⻆⾊。将该⻆⾊附加到⼀个新的 EC2 实例。使⽤新 EC2 实例上的 AWS
B. 创建⼀条禁⽌删除快照的 IAM 策略。将该策略附加到存储管理员⽤户。
C. 为快照添加标签。为带有这些标签的 EBS 快照在回收站中创建保留规则。
D. 锁定 EBS 快照以防⽌删除。
https://examlearn.online
[2026/05]
Question #676
Topic 1
⼀家公司的应⽤程序使⽤⽹络负载均衡器、⾃动扩展组、Amazon EC2 实例和数据库，这些资源都部署在
Amazon VPC 中。该公司希望近乎实时地捕获其 Amazon VPC 中⽹络接⼝的流量信息，并将这些信息发送到
Amazon OpenSearch Service 进⾏分析。
哪种解决⽅案能够满⾜这些要求？
A. 在 Amazon CloudWatch Logs 中创建⽇志组。配置 VPC 流⽇志将⽇志数据发送到该⽇志组。使⽤
Amazon Kinesis Data Streams 将⽇志从⽇志组流式传输到 OpenSearch Service。
B. 在 Amazon CloudWatch Logs 中创建⽇志组。配置 VPC 流⽇志将⽇志数据发送到该⽇志组。使⽤
Amazon Kinesis Data Firehose 将⽇志从⽇志组流式传输到 OpenSearch Service。
C. 在 AWS CloudTrail 中创建跟踪。配置 VPC 流⽇志以将⽇志数据发送到跟踪。使⽤ Amazon Kinesis Data
Streams 将⽇志从跟踪流式传输到 OpenSearch Service。
D. 在 AWS CloudTrail 中创建跟踪。配置 VPC 流⽇志以将⽇志数据发送到跟踪。使⽤ Amazon Kinesis Data
Firehose 将⽇志从跟踪流式传输到 OpenSearch Service。
Question #677
Topic 1
⼀家公司正在开发⼀款将在⽣产环境的 Amazon Elastic Kubernetes Service (Amazon EKS) 集群上运⾏的应⽤
程序。该 EKS 集群拥有托管节点组，这些节点组通过按需实例进⾏配置。
该公司需要⼀个专⽤的 EKS 集群⽤于开发⼯作。该公司将偶尔使⽤该开发集群来测试应⽤程序的弹性。EKS 集群
必须管理所有节点。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建⼀个仅包含竞价型实例的托管节点组。
B. 创建两个托管节点组。在⼀个节点组中配置按需实例。在另⼀个节点组中配置竞价型实例。
C. 创建⼀个⾃动扩展组，其启动配置使⽤竞价型实例。配置⽤户数据，将节点添加到 EKS 集群。
D. 创建⼀个仅包含按需实例的托管节点组。
https://examlearn.online
[2026/05]
Question #678
Topic 1
⼀家公司将敏感数据存储在 Amazon S3 中。解决⽅案架构师需要创建⼀个加密解决⽅案。该公司需要完全控制
⽤户创建、轮换和禁⽤加密密钥的能⼒，并尽可能简化所有需要加密的数据的操作。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon S3 管理的加密密钥 (SSE-S3) 的默认服务器端加密来存储敏感数据。
B. 使⽤ AWS Key Management Service (AWS KMS) 创建客户管理的密钥。使⽤新密钥，通过基于 AWS
KMS 密钥的服务器端加密 (SSE-KMS) 对 S3 对象进⾏加密。
C. 使⽤ AWS Key Management Service (AWS KMS) 创建 AWS 托管密钥。使⽤新密钥，通过基于 AWS
KMS 密钥的服务器端加密 (SSE-KMS) 对 S3 对象进⾏加密。
D. 将 S3 对象下载到 Amazon EC2 实例。使⽤客户管理的密钥对对象进⾏加密。将加密后的对象上传回
Amazon S3。
Question #679
以下哪些步骤组合可以满⾜这些要求？（选择三个。）
A. 创建⼀个启⽤了 S3 对象锁定的 S3 存储桶。
Topic 1
⼀家公司希望将其本地虚拟机 (VM) 备份到 AWS。该公司的备份解决⽅案会将本地备份以对象的形式导出到
Amazon S3 存储桶。S3 备份必须保留 30 天，并在 30 天后⾃动删除。
B. 创建⼀个启⽤对象版本控制的 S3 存储桶。
C. 将对象的默认保留期限配置为 30 天。
D. 配置 S3 ⽣命周期策略，以保护对象 30 天。
E. 配置 S3 ⽣命周期策略，使对象在 30 天后过期。
F. 配置备份解决⽅案，为对象添加30天保留期的标签。
https://examlearn.online
[2026/05]
Question #680
Topic 1
解决⽅案架构师需要将⽂件从 Amazon S3 存储桶复制到 Amazon Elastic File System (Amazon EFS) ⽂件系统
以及另⼀个 S3 存储桶。⽂件必须持续复制。新⽂件会持续添加到原始 S3 存储桶中。只有当源⽂件发⽣更改时，
才应覆盖复制的⽂件。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为⽬标 S3 存储桶和 EFS ⽂件系统分别创建 AWS DataSync 位置。为⽬标 S3 存储桶和 EFS ⽂件系统分
别创建任务。将传输模式设置为仅传输已更改的数据。
B. 创建⼀个 AWS Lambda 函数。将⽂件系统挂载到该函数。设置 S3 事件通知，以便在 Amazon S3 中创建
或更改⽂件时调⽤该函数。配置该函数，使其将⽂件复制到⽂件系统和⽬标 S3 存储桶。
C. 为⽬标 S3 存储桶和 EFS ⽂件系统创建 AWS DataSync 位置。为⽬标 S3 存储桶和 EFS ⽂件系统创建任
务。将传输模式设置为传输所有数据。
D. 在与⽂件系统相同的 VPC 中启动⼀个 Amazon EC2 实例。挂载该⽂件系统。创建⼀个脚本，定期将源 S3
存储桶中所有已更改的对象同步到⽬标 S3 存储桶和已挂载的⽂件系统。
Question #681
Topic 1
⼀家公司使⽤ Amazon EC2 实例并将数据存储在 Amazon Elastic Block Store (Amazon EBS) 卷上。该公司必
须使⽤ AWS Key Management Service (AWS KMS) 确保所有数据在静态存储时都经过加密。该公司还必须能够
控制加密密钥的轮换。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建客户管理的密钥。使⽤该密钥加密 EBS 卷。
B. 使⽤ AWS 托管密钥加密 EBS 卷。使⽤该密钥配置⾃动密钥轮换。
C. 使⽤导⼊的密钥材料创建外部 KMS 密钥。使⽤该密钥加密 EBS 卷。
D. 使⽤ AWS 拥有的密钥对 EBS 卷进⾏加密。
https://examlearn.online
[2026/05]
Question #682
Topic 1
⼀家公司需要⼀个解决⽅案来强制执⾏ Amazon EC2 实例上的静态数据加密。该解决⽅案必须能够⾃动识别不合
规的资源，并根据发现的问题强制执⾏合规策略。
哪个解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 使⽤ IAM 策略，仅允许⽤户创建加密的 Amazon Elastic Block Store (Amazon EBS) 卷。使⽤ AWS
Config 和 AWS Systems Manager ⾃动检测和修复未加密的 EBS 卷。
B. 使⽤ AWS Key Management Service (AWS KMS) 管理对加密的 Amazon Elastic Block Store (Amazon
EBS) 卷的访问。使⽤ AWS Lambda 和 Amazon EventBridge ⾃动检测和修复未加密的 EBS 卷。
C. 使⽤ Amazon Macie 检测未加密的 Amazon Elastic Block Store (Amazon EBS) 卷。使⽤ AWS Systems
Manager Automation 规则⾃动加密现有和新的 EBS 卷。
D. 使⽤ Amazon Inspector 检测未加密的 Amazon Elastic Block Store (Amazon EBS) 卷。使⽤ AWS
Systems Manager Automation 规则⾃动加密现有和新的 EBS 卷。
Question #683
以下哪两项措施组合能够满⾜这些要求？
Topic 1
⼀家公司正在将其多层本地应⽤程序迁移到 AWS。该应⽤程序包含⼀个单节点 MySQL 数据库和⼀个多节点
Web 层。该公司必须在迁移过程中尽可能减少对应⽤程序的更改。迁移后，该公司希望提⾼应⽤程序的弹性。
A. 将 Web 层迁移到位于应⽤程序负载均衡器后⾯的⾃动扩展组中的 Amazon EC2 实例。
B. 将数据库迁移到位于⽹络负载均衡器后⾯的⾃动扩展组中的 Amazon EC2 实例。
C. 将数据库迁移到 Amazon RDS 多可⽤区部署。
D. 将 Web 层迁移到 AWS Lambda 函数。
E. 将数据库迁移到 Amazon DynamoDB 表。
https://examlearn.online
[2026/05]
Question #684
Topic 1
⼀家公司希望将其 Web 应⽤程序从本地迁移到 AWS。该公司位于 eu-central-1 区域附近。由于法规限制，该公
司⽆法在 eu-central-1 区域部署某些应⽤程序。该公司希望实现个位数毫秒级的延迟。
哪种解决⽅案能够满⾜这些要求？
A. 在 eu-central-1 部署应⽤程序。将公司的 VPC 从 eu-central-1 扩展到 Amazon CloudFront 的边缘位
置。
B. 通过将公司的 VPC 从 eu-central-1 扩展到选定的本地区域，在 AWS 本地区域中部署应⽤程序。
C. 在 eu-central-1 部署应⽤程序。将公司的 VPC 从 eu-central-1 扩展到 Amazon CloudFront 中的区域边
缘缓存。
D. 通过将公司的 VPC 从 eu-central-1 扩展到选定的 Wavelength Zone，在 AWS Wavelength Zone 中部署
应⽤程序。
Question #685
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司的电商⽹站流量不稳定，并使⽤ AWS Lambda 函数直接访问私有的 Amazon RDS for PostgreSQL 数
据库实例。该公司希望保持数据库性能的稳定性，并确保 Lambda 函数调⽤不会因连接数过多⽽导致数据库过
载。
A. 将客户端驱动程序指向 RDS ⾃定义端点。将 Lambda 函数部署在 VPC 内。
B. 将客户端驱动程序指向 RDS 代理端点。将 Lambda 函数部署在 VPC 内。
C. 将客户端驱动程序指向 RDS ⾃定义端点。将 Lambda 函数部署在 VPC 之外。
D. 将客户端驱动程序指向 RDS 代理端点。将 Lambda 函数部署在 VPC 之外。
https://examlearn.online
[2026/05]
Question #686
⼀家公司正在开发⼀款应⽤程序。该公司将应⽤程序测试数据存储在多个本地位置。
Topic 1
该公司需要将这些本地位置连接到 AWS 云中某个 AWS 区域的 VPC。账户和 VPC 的数量将在未来⼀年内增加。
⽹络架构必须简化新连接的管理，并且必须具备可扩展性。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 在 VPC 之间创建对等连接。在 VPC 和本地位置之间创建 VPN 连接。
B. 启动⼀个 Amazon EC2 实例。在该实例上，安装 VPN 软件，该软件使⽤ VPN 连接来连接所有 VPC 和本
地位置。
C. 创建传输⽹关。为 VPC 连接创建 VPC 附件。为本地连接创建 VPN 附件。
D. 在本地位置和中央 VPC 之间创建 AWS Direct Connect 连接。使⽤对等连接将中央 VPC 连接到其他
VPC。
Question #687
以下哪些步骤组合可以满⾜这些要求？（选择两项。）
Topic 1
⼀家使⽤ AWS 的公司需要⼀个解决⽅案来预测每⽉⽣产流程所需的资源。该解决⽅案必须使⽤当前存储在
Amazon S3 存储桶中的历史数据。该公司没有机器学习 (ML) 经验，希望使⽤托管服务进⾏训练和预测。
A. 部署 Amazon SageMaker 模型。创建⽤于推理的 SageMaker 端点。
B. 使⽤ Amazon SageMaker 通过 S3 存储桶中的历史数据来训练模型。
C. 配置⼀个 AWS Lambda 函数，该函数使⽤ Amazon SageMaker 端点根据输⼊创建预测。
D. 配置⼀个 AWS Lambda 函数，该函数使⽤ Amazon Forecast 预测器根据输⼊创建预测。
E. 使⽤ S3 存储桶中的历史数据训练 Amazon Forsecast 预测器。
https://examlearn.online
[2026/05]
Question #688
Topic 1
⼀家公司在 AWS Organizations 中管理 AWS 账户。这些账户已配置 AWS IAM Identity Center（AW S 单点登
录）和 AWS Control Tower。该公司希望跨所有账户管理多个⽤户权限。
这些权限将由多个 IAM ⽤户使⽤，并且必须在开发⼈员团队和管理员团队之间进⾏划分。每个团队需要不同的权
限。该公司希望找到⼀个能够涵盖两个团队中新⼊职⽤户的解决⽅案。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 在 IAM 身份中⼼为每个帐户创建单独的⽤户。在 IAM 身份中⼼创建单独的开发⼈员组和管理员组。将⽤户
分配到相应的组。为每个组创建⾃定义 IAM 策略，以设置细粒度的权限。
B. 在 IAM 身份中⼼为每个账户创建单独的⽤户。在 IAM 身份中⼼创建单独的开发⼈员组和管理员组。将⽤户
分配到相应的组。根据需要，为每个⽤户附加 AWS 托管的 IAM 策略，以实现细粒度的权限控制。
C. 在 IAM 身份中⼼创建单个⽤户。在 IAM 身份中⼼创建新的开发⼈员组和管理员组。为每个组创建包含相应
IAM 策略的新权限集。将新组分配给相应的帐户。将新权限集分配给新组。新⽤户⼊职后，将其添加到相应
的组。
D. 在 IAM 身份中⼼创建单个⽤户。为每个⽤户创建包含相应 IAM 策略的新权限集。将⽤户分配到相应的帐
户。从特定帐户向⽤户授予额外的 IAM 权限。新⽤户⼊职后，将其添加到 IAM 身份中⼼并分配到相应的帐
户。
Question #689
哪种解决⽅案能够满⾜这些要求？
来运⾏这些 API 调⽤。
Topic 1
⼀家公司希望规范其 Amazon Elastic Block Store (Amazon EBS) 卷加密策略，并尽可能降低运⾏卷加密检查所
需的成本和配置⼯作量。
A. 编写 API 调⽤来描述 EBS 卷并确认 EBS 卷已加密。使⽤ Amazon EventBridge 调度 AWS Lambda 函数
B. 编写 API 调⽤来描述 EBS 卷并确认 EBS 卷已加密。在 AWS Fargate 任务上运⾏这些 API 调⽤。
C. 创建⼀条 AWS Identity and Access Management (IAM) 策略，要求在 EBS 卷上使⽤标签。使⽤ AWS
Cost Explorer 显示未正确标记的资源。⼿动加密未标记的资源。
D. 为 Amazon EBS 创建⼀个 AWS Config 规则，以评估卷是否已加密，如果卷未加密，则标记该卷。
https://examlearn.online
[2026/05]
Question #690
Topic 1
⼀家公司定期向 Amazon S3 上传 GB 级⽂件。上传⽂件后，该公司使⽤⼀组 Amazon EC2 Spot 实例对⽂件格
式进⾏转码。该公司需要在从本地数据中⼼向 Amazon S3 上传数据以及从 Amazon S3 下载数据到 EC2 实例时
扩展吞吐量。
哪些解决⽅案可以满⾜这些要求？（选择两个。）
A. 使⽤ S3 存储桶访问点，⽽不是直接访问 S3 存储桶。
B. 将⽂件上传到多个 S3 存储桶。
C. 使⽤ S3 分段上传。
D. 并⾏获取对象的多个字节范围。
E. 上传⽂件时，给每个对象添加⼀个随机前缀。
Question #691
哪些解决⽅案满⾜这些要求？（选择两个。）
Topic 1
⼀位解决⽅案架构师正在为⼀个跨多个可⽤区部署的 Web 应⽤程序设计共享存储解决⽅案。该 Web 应⽤程序运
⾏在位于⾃动扩展组中的 Amazon EC2 实例上。公司计划频繁更改内容。该解决⽅案必须具有⾼度⼀致性，能够
在内容更改发⽣后⽴即返回新内容。
A. 使⽤挂载到各个 EC2 实例的 AWS Storage Gateway Volume Gateway Internet Small Computer
Systems Interface (iSCSI) 块存储。
B. 创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。将 EFS ⽂件系统挂载到各个 EC2 实例上。
C. 创建共享的 Amazon Elastic Block Store (Amazon EBS) 卷。将 EBS 卷挂载到各个 EC2 实例上。
D. 使⽤ AWS DataSync 在⾃动扩展组中的 EC2 主机之间执⾏持续数据同步。
E. 创建⼀个 Amazon S3 存储桶来存储 Web 内容。将 Cache-Control 标头的元数据设置为 no-cache。使⽤
Amazon CloudFront 来分发内容。
https://examlearn.online
[2026/05]
Question #692
Topic 1
⼀家公司正在使⽤应⽤程序负载均衡器在三个 AWS 区域中部署应⽤程序。Amazon Route 53 将⽤于在这些区域
之间分配流量。
解决⽅案架构师应该使⽤哪种 Route 53 配置才能提供最佳性能体验？
A. 创建⼀个具有延迟策略的 A 记录。
B. 创建具有地理位置策略的 A 记录。
C. 创建具有故障转移策略的 CNAME 记录。
D. 创建⼀个具有地理位置邻近策略的 CNAME 记录。
Question #693
最近流量激增，要求应⽤程序具备⾼可⽤性，并且数据库最终保持⼀致性。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司有⼀个包含嵌⼊式 NoSQL 数据库的 Web 应⽤程序。该应⽤程序运⾏在 Amazon EC2 实例上，并由应
⽤程序负载均衡器 (ALB) 管理。这些实例运⾏在同⼀个可⽤区内的 Amazon EC2 ⾃动扩展组中。
A. 将应⽤负载均衡器 (ALB) 替换为⽹络负载均衡器。在 EC2 实例上维护嵌⼊式 NoSQL 数据库及其复制服
务。
B. 将应⽤负载均衡器 (ALB) 替换为⽹络负载均衡器。使⽤ AWS 数据库迁移服务 (AWS DMS) 将嵌⼊式
NoSQL 数据库迁移到 Amazon DynamoDB。
C. 修改⾃动扩展组，使其使⽤跨三个可⽤区的 EC2 实例。在 EC2 实例上维护嵌⼊式 NoSQL 数据库及其复制
服务。
D. 修改⾃动扩展组，使其使⽤跨三个可⽤区的 EC2 实例。使⽤ AWS 数据库迁移服务 (AWS DMS) 将嵌⼊式
NoSQL 数据库迁移到 Amazon DynamoDB。
https://examlearn.online
[2026/05]
Question #694
Topic 1
⼀家公司正在 AWS 上构建⼀个购物应⽤程序。该应⽤程序提供每⽉更新⼀次的商品⽬录，并且需要能够随着流
量的增⻓⽽扩展。该公司希望应⽤程序的延迟尽可能低。每个⽤户的购物⻋数据都需要⾼度可⽤。即使⽤户断开
连接并重新连接，⽤户会话数据也必须可⽤。
解决⽅案架构师应该如何做才能确保购物⻋数据始终保留？
A. 配置应⽤程序负载均衡器，以启⽤粘性会话功能（会话亲和性），从⽽访问 Amazon Aurora 中的⽬录。
B. 配置 Amazon ElastiCache for Redis 以缓存来⾃ Amazon DynamoDB 的⽬录数据和来⾃⽤户会话的购物
⻋数据。
C. 配置 Amazon OpenSearch Service 以缓存来⾃ Amazon DynamoDB 的⽬录数据和来⾃⽤户会话的购物
⻋数据。
D. 配置⼀个 Amazon EC2 实例，并使⽤ Amazon Elastic Block Store (Amazon EBS) 存储来存储商品⽬录和
购物⻋。配置⾃动快照。
Question #695
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在构建⼀个基于微服务的应⽤程序，该应⽤程序将部署在 Amazon Elastic Kubernetes Service
(Amazon EKS) 上。这些微服务之间会相互交互。该公司希望确保应⽤程序可观测，以便将来识别性能问题。
A. 配置应⽤程序以使⽤ Amazon ElastiCache 来减少发送到微服务的请求数量。
B. 配置 Amazon CloudWatch Container Insights 以收集 EKS 集群的指标。配置 AWS X-Ray 以跟踪微服务
之间的请求。
C. 配置 AWS CloudTrail 以查看 API 调⽤。构建 Amazon QuickSight 控制⾯板以观察微服务交互。
D. 使⽤ AWS Trusted Advisor 了解应⽤程序的性能。
https://examlearn.online
[2026/05]
Question #696
Topic 1
⼀家公司需要为客户提供安全的数据访问⽅式。该公司处理客户数据并将结果存储在 Amazon S3 存储桶中。
所有数据均受严格的法规和安全要求约束。数据必须进⾏静态加密。每位客户只能通过其 AWS 账户访问⾃⼰的
数据。公司员⼯不得访问这些数据。
哪种解决⽅案能够满⾜这些要求？
A. 为每位客户配置⼀个 AWS Certificate Manager (ACM) 证书。在客户端加密数据。在私有证书策略中，禁
⽌除客户提供的 IAM ⻆⾊之外的所有主体访问该证书。
B. 为每个客户配置⼀个单独的 AWS Key Management Service (AWS KMS) 密钥。在服务器端加密数据。在
S3 存储桶策略中，禁⽌除客户提供的 IAM ⻆⾊之外的所有主体解密数据。
C. 为每个客户配置⼀个单独的 AWS Key Management Service (AWS KMS) 密钥。在服务器端加密数据。在
每个 KMS 密钥策略中，禁⽌除客户提供的 IAM ⻆⾊之外的所有主体解密数据。
D. 为每位客户配置⼀个 AWS Certificate Manager (ACM) 证书。在客户端加密数据。在公有证书策略中，禁
⽌除客户提供的 IAM ⻆⾊之外的所有主体访问该证书。
Question #697
解决⽅案架构师应该如何解决此问题？
Topic 1
解决⽅案架构师创建了⼀个包含两个公有⼦⽹和两个私有⼦⽹的 VPC。公司安全规定要求解决⽅案架构师必须在
私有⼦⽹中启动所有 Amazon EC2 实例。但是，当解决⽅案架构师在私有⼦⽹中启动⼀个运⾏ Web 服务器（使
⽤ 80 和 443 端⼝）的 EC2 实例时，外部互联⽹流量⽆法连接到该服务器。
A. 将 EC2 实例附加到私有⼦⽹中的⾃动扩展组。确保⽹站的 DNS 记录解析到⾃动扩展组标识符。
B. 在公共⼦⽹中配置⾯向互联⽹的应⽤程序负载均衡器 (ALB)。将 EC2 实例添加到与 ALE 关联的⽬标组。确
保⽹站的 DNS 记录解析到 ALB。
C. 在私有⼦⽹中启动 NAT ⽹关。更新私有⼦⽹的路由表，添加指向 NAT ⽹关的默认路由。将公共弹性 IP 地
址附加到 NAT ⽹关。
D. 确保附加到 EC2 实例的安全组允许端⼝ 80 上的 HTTP 流量和端⼝ 443 上的 HTTPS 流量。确保⽹站的
DNS 记录解析到 EC2 实例的公共 IP 地址。
https://examlearn.online
[2026/05]
Question #698
Topic 1
⼀家公司正在将⼀款新应⽤程序部署到 Amazon Elastic Kubernetes Service (Amazon EKS) 和 AWS Fargate 集
群上。该应⽤程序需要⼀个⽤于数据持久化的存储解决⽅案。该解决⽅案必须具备⾼可⽤性和容错性，并且需要
在多个应⽤程序容器之间共享。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 在 EKS ⼯作节点所在的同⼀可⽤区创建 Amazon Elastic Block Store (Amazon EBS) 卷。将这些卷注册到
EKS 集群的 StorageClass 对象中。使⽤ EBS MultiAttach 在容器之间共享数据。
B. 创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。在 EKS 集群的 StorageClass 对象中注册该
⽂件系统。所有容器使⽤同⼀个⽂件系统。
C. 创建⼀个 Amazon Elastic Block Store (Amazon EBS) 卷。在 EKS 集群的 StorageClass 对象中注册该
卷。所有容器使⽤同⼀个卷。
D. 在 EKS ⼯作节点所在的同⼀可⽤区创建 Amazon Elastic File System (Amazon EFS) ⽂件系统。将这些⽂
件系统注册到 EKS 集群的 StorageClass 对象中。创建⼀个 AWS Lambda 函数来同步⽂件系统之间的数据。
Question #699
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在其本地数据中⼼运⾏⼀个使⽤ Docker 容器的应⽤程序。该应⽤程序运⾏在容器主机上，持久数据存
储在主机上的卷中。容器实例使⽤这些存储的持久数据。
该公司希望将该应⽤程序迁移到完全托管的服务，因为该公司不想管理任何服务器或存储基础设施。
A. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和⾃管理节点。创建⼀个 Amazon Elastic
Block Store (Amazon EBS) 卷并将其附加到 Amazon EC2 实例。将该 EBS 卷⽤作持久卷，并将其挂载到容
器中。
B. 使⽤ Amazon Elastic Container Service (Amazon ECS)，启动类型选择 AWS Fargate。创建 Amazon
Elastic File System (Amazon EFS) 卷。将 EFS 卷添加为持久存储卷，并将其挂载到容器中。
C. 使⽤ Amazon Elastic Container Service (Amazon ECS)，启动类型选择 AWS Fargate。创建⼀个
Amazon S3 存储桶。将该 S3 存储桶映射为挂载到容器中的持久存储卷。
D. 使⽤ Amazon Elastic Container Service (Amazon ECS)，启动类型选择 Amazon EC2。创建 Amazon
Elastic File System (Amazon EFS) 卷。将 EFS 卷添加为持久存储卷，并将其挂载到容器中。
https://examlearn.online
[2026/05]
Question #700
Topic 1
⼀家游戏公司希望在多个 AWS 区域推出⼀款⾯向互联⽹的新应⽤程序。该应⽤程序将使⽤ TCP 和 UDP 协议进
⾏通信。该公司需要为全球⽤户提供⾼可⽤性和最低延迟。
解决⽅案架构师应采取哪些措施组合来满⾜这些要求？（选择两项。）
A. 在每个区域的应⽤程序前⾯创建内部⽹络负载均衡器。
B. 在每个区域中，在应⽤程序前⾯创建外部应⽤程序负载均衡器。
C. 创建⼀个 AWS Global Accelerator 加速器，将流量路由到每个区域的负载均衡器。
D. 配置 Amazon Route 53 使⽤地理位置路由策略来分配流量。
E. 配置 Amazon CloudFront 以处理流量并将请求路由到每个区域中的应⽤程序
Question #701
哪个解决⽅案符合这些要求？
Topic 1
某城市部署了⼀个运⾏在 Amazon EC2 实例上的 Web 应⽤程序，该实例位于应⽤程序负载均衡器 (ALB) 之后。
该应⽤程序的⽤户报告称性能不稳定，这似乎与来⾃随机 IP 地址的 DDoS 攻击有关。该城市需要⼀个只需进⾏最
少配置更改即可解决问题，并且能够提供 DDoS 攻击源的审计跟踪。
A. 在 ALB 上启⽤ AWS WAF Web ACL，并配置规则以阻⽌来⾃未知来源的流量。
B. 订阅 Amazon Inspector。联系 AWS DDoS 响应团队 (DRT)，将缓解控制措施集成到服务中。
C. 订阅 AWS Shield Advanced。联系 AWS DDoS 响应团队 (DRT)，将缓解控制措施集成到该服务中。
D. 为应⽤程序创建 Amazon CloudFront 分发，并将 ALB 设置为源。在该分发上启⽤ AWS WAF Web ACL，
并配置规则以阻⽌来⾃未知来源的流量。
https://examlearn.online
[2026/05]
Question #702
Topic 1
⼀家公司将近期海洋调查的 200 TB 数据复制到 AWS Snowball Edge Storage Optimized 设备上。该公司拥有
⼀个托管在 AWS 上的⾼性能计算 (HPC) 集群，⽤于勘探油⽓矿藏。解决⽅案架构师必须确保该集群能够以亚毫
秒级的延迟和⾼吞吐量访问 Snowball Edge Storage Optimized 设备上的数据。该公司将把这些设备寄回
AWS。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个 Amazon S3 存储桶。将数据导⼊到 S3 存储桶中。配置 AWS Storage Gateway ⽂件⽹关以使⽤
该 S3 存储桶。从 HPC 集群实例访问该⽂件⽹关。
B. 创建⼀个 Amazon S3 存储桶。将数据导⼊到 S3 存储桶中。配置 Amazon FSx for Lustre ⽂件系统，并将
其与 S3 存储桶集成。从 HPC 集群实例访问 FSx for Lustre ⽂件系统。
C. 创建⼀个 Amazon S3 存储桶和⼀个 Amazon Elastic File System (Amazon EFS) ⽂件系统。将数据导⼊
S3 存储桶。将数据从 S3 存储桶复制到 EFS ⽂件系统。从 HPC 集群实例访问 EFS ⽂件系统。
D. 创建 Amazon FSx for Lustre ⽂件系统。将数据直接导⼊ FSx for Lustre ⽂件系统。从 HPC 集群实例访
问 FSx for Lustre ⽂件系统。
Question #703
Topic 1
⼀家公司在本地数据中⼼拥有 NFS 服务器，需要定期将少量数据备份到 Amazon S3。
哪种解决⽅案既满⾜这些要求，⼜最具成本效益？
A. 设置 AWS Glue 将数据从本地服务器复制到 Amazon S3。
B. 在本地服务器上设置 AWS DataSync 代理，并将数据同步到 Amazon S3。
C. 使⽤ AWS Transfer for SFTP 设置 SFTP 同步，将数据从本地同步到 Amazon S3。
D. 在本地数据中⼼和 VPC 之间建⽴ AWS Direct Connect 连接，并将数据复制到 Amazon S3。
https://examlearn.online
[2026/05]
Question #704
Topic 1
⼀家在线视频游戏公司必须保证其游戏服务器的超低延迟。这些游戏服务器运⾏在亚⻢逊 EC2 实例上。该公司需
要⼀个能够处理每秒数百万次 UDP ⽹络流量请求的解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置应⽤程序负载均衡器，并为其分配互联⽹流量所需的协议和端⼝。将 EC2 实例指定为⽬标。
B. 配置⽹关负载均衡器以处理互联⽹流量。指定 EC2 实例作为⽬标。
C. 配置⽹络负载均衡器，并指定所需的协议和端⼝以处理互联⽹流量。将 EC2 实例指定为⽬标。
D. 在不同的 AWS 区域中的 EC2 实例上启动⼀组相同的游戏服务器。将互联⽹流量路由到这两组 EC2 实例。
Question #705
以下哪些步骤组合可以满⾜这些要求？（选择两项。）
⼀家公司在 VPC 中运⾏⼀个三层应⽤程序。数据库层使⽤ Amazon RDS for MySQL 数据库实例。
Topic 1
该公司计划将 RDS for MySQL 数据库实例迁移到 Amazon Aurora PostgreSQL 数据库集群。该公司需要⼀个解
决⽅案，能够将迁移过程中发⽣的数据更改复制到新数据库。
A. 使⽤ AWS 数据库迁移服务 (AWS DMS) 架构转换来转换数据库对象。
B. 使⽤ AWS 数据库迁移服务 (AWS DMS) 架构转换在 RDS for MySQL 数据库实例上创建 Aurora
PostgreSQL 只读副本。
C. 为 RDS for MySQL 数据库实例配置 Aurora MySQL 只读副本。
D. 定义⼀个使⽤变更数据捕获 (CDC) 的 AWS 数据库迁移服务 (AWS DMS) 任务来迁移数据。
E. 当副本延迟为零时，将 Aurora PostgreSQL 只读副本提升为独⽴的 Aurora PostgreSQL 数据库集群。
https://examlearn.online
[2026/05]
Question #706
Topic 1
⼀家公司托管着⼀个数据库，该数据库运⾏在部署于多个可⽤区的 Amazon RDS 实例上。该公司定期运⾏⼀个脚
本来报告数据库中新增的条⽬。该脚本会对关键应⽤程序的性能产⽣负⾯影响。该公司需要以最⼩的成本提升应
⽤程序的性能。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 为脚本添加功能，以识别活动连接数最少的实例。配置脚本从该实例读取数据，并报告新增条⽬总数。
B. 创建数据库的只读副本。配置脚本，使其仅查询只读副本，以报告新增条⽬总数。
C. 指示开发团队在每天结束时⼿动导出数据库中当天的新条⽬。
D. 使⽤ Amazon ElastiCache 缓存脚本针对数据库运⾏的常⽤查询。
Question #707
满⾜这些要求的最佳运维解决⽅案是什么？
Topic 1
⼀家公司使⽤应⽤负载均衡器 (ALB) 将其应⽤程序部署到互联⽹上。该公司发现应⽤程序的流量访问模式异常。
解决⽅案架构师需要提⾼对基础设施的可⻅性，以帮助公司更好地了解这些异常情况。
A. 在 Amazon Athena 中创建⼀个⽤于存储 AWS CloudTrail ⽇志的表。创建⼀个查询以获取相关信息。
B. 启⽤ ALB 访问⽇志记录到 Amazon S3。在 Amazon Athena 中创建表，并查询⽇志。
C. 启⽤ ALB 对 Amazon S3 的访问⽇志记录。在⽂本编辑器中打开每个⽂件，并在每⼀⾏中搜索相关信息。
D. 使⽤专⽤ Amazon EC2 实例上的 Amazon EMR 直接查询 ALB 以获取流量访问⽇志信息。
https://examlearn.online
[2026/05]
Question #708
Topic 1
⼀家公司希望在其 AWS 环境中使⽤ NAT ⽹关。该公司私有⼦⽹中的 Amazon EC2 实例必须能够通过 NAT ⽹关
连接到公有互联⽹。
哪种解决⽅案能够满⾜这些要求？
A. 在与 EC2 实例相同的私有⼦⽹中创建公共 NAT ⽹关。
B. 在与 EC2 实例相同的私有⼦⽹中创建私有 NAT ⽹关。
C. 在与 EC2 实例相同的 VPC 的公共⼦⽹中创建公共 NAT ⽹关。
D. 在与 EC2 实例相同的 VPC 的公共⼦⽹中创建私有 NAT ⽹关。
Question #709
A. 将 SCP 附加到组织的根 OU。
Topic 1
⼀家公司在 AWS Organizations 中拥有⼀个组织。该公司在根组织单元 (OU) 下的四个 AWS 账户中运⾏
Amazon EC2 实例。其中三个账户为⾮⽣产账户，⼀个账户为⽣产账户。该公司希望禁⽌⽤户在⾮⽣产账户中启
动特定⼤⼩的 EC2 实例。为此，该公司创建了⼀个服务控制策略 (SCP)，⽤于拒绝启动使⽤禁⽌类型的实例。
以下哪些部署 SCP 的解决⽅案能够满⾜这些要求？（选择两个。）
B. 将 SCP 附加到三个⾮⽣产组织成员帐户。
C. 将 SCP 附加到组织管理帐户。
D. 为⽣产帐户创建⼀个组织单元 (OU)。将 SCP 附加到该 OU。将⽣产成员帐户移动到新的 OU 中。
E. 为所需帐户创建⼀个组织单元 (OU)。将 SCP 附加到该 OU。将⾮⽣产成员帐户移动到新的 OU 中。
https://examlearn.online
[2026/05]
Question #710
Topic 1
⼀家公司的⽹站托管在 Amazon EC2 实例上，并处理存储在 Amazon S3 中的机密数据。出于安全考虑，该公司
需要在其 EC2 资源和 Amazon S3 之间建⽴私密且安全的连接。
哪种解决⽅案满⾜这些要求？
A. 设置 S3 存储桶策略，允许从 VPC 端点访问。
B. 设置 IAM 策略以授予对 S3 存储桶的读写访问权限。
C. 设置 NAT ⽹关以访问私有⼦⽹之外的资源。
D. 设置访问密钥 ID 和秘密访问密钥以访问 S3 存储桶。
Question #711
解决⽅案架构师需要使应⽤程序架构更具可扩展性和⾼可⽤性。
Topic 1
⼀家电商公司将其应⽤程序运⾏在 AWS 上。该应⽤程序使⽤ Amazon Aurora PostgreSQL 集群作为底层数据
库，并采⽤多可⽤区 (Multi-AZ) 模式。在最近的⼀次促销活动期间，该应⽤程序经历了⼤量的读写负载。⽤户在
尝试访问该应⽤程序时遇到了超时问题。
哪种解决⽅案能够在满⾜这些要求的同时，最⼤限度地减少停机时间？
A. 创建⼀个以 Aurora 集群为源的 Amazon EventBridge 规则。创建⼀个 AWS Lambda 函数来记录 Aurora
集群的状态变更事件。将该 Lambda 函数添 加为 EventBridge 规则的⽬标。添加额外的读取节点以进⾏故障
转移。
B. 修改 Aurora 集群并启⽤零停机重启 (ZDR) 功能。使⽤集群上的数据库活动流来跟踪集群状态。
C. 向 Aurora 集群添加额外的读取器实例。为 Aurora 集群创建 Amazon RDS 代理⽬标组。
D. 为 Redis 缓存创建 Amazon ElastiCache。使⽤ AWS 数据库迁移服务 (AWS DMS) 和绕写⽅法将数据从
Aurora 集群复制到 Redis。
https://examlearn.online
[2026/05]
Question #712
Topic 1
⼀家公司正在AWS上设计⼀个Web应⽤程序。该应⽤程序将使⽤VPN连接公司现有的数据中⼼和其虚拟私有云
（VPC）。
该公司使⽤Amazon Route 53作为其DNS服务。该应⽤程序必须使⽤私有DNS记录才能从VPC与本地服务通信。
哪种解决⽅案能够以最安全的⽅式满⾜这些要求？
A. 创建 Route 53 解析器出站端点。创建解析器规则。将解析器规则与 VPC 关联。
B. 创建 Route 53 解析器⼊站端点。创建解析器规则。将解析器规则与 VPC 关联。
C. 创建⼀个 Route 53 私有托管区域。将该私有托管区域与 VPC 关联。
D. 创建⼀个 Route 53 公共托管区域。为每个服务创建⼀个记录，以允许服务通信。
Question #713
Topic 1
⼀家公司在美国东部地区（US-East-1）运营照⽚托管服务。该服务允许多个国家/地区的⽤户上传和查看照⽚。
有些照⽚会被浏览数⽉之久，⽽有些照⽚的浏览量则不到⼀周。该应⽤程序允许每张照⽚上传最⼤ 20 MB 的⽂
件。该服务使⽤照⽚元数据来确定向每个⽤户显示哪些照⽚。
哪种解决⽅案能够以最具成本效益的⽅式提供合适的⽤户访问权限？
A. 将照⽚存储在 Amazon DynamoDB 中。启⽤ DynamoDB 加速器 (DAX) 以缓存经常查看的项⽬。
B. 将照⽚存储在 Amazon S3 智能分层存储类别中。将照⽚元数据及其 S3 位置存储在 DynamoDB 中。
C. 将照⽚存储在 Amazon S3 标准存储类中。设置 S3 ⽣命周期策略，将超过 30 天的照⽚移动到 S3 标准-不
频繁访问 (S3 Standard-IA) 存储类。使⽤对象标签来跟踪元数据。
D. 将照⽚存储在 Amazon S3 Glacier 存储类中。设置 S3 ⽣命周期策略，将超过 30 天的照⽚移动到 S3
Glacier Deep Archive 存储类。将照⽚元数据及其 S3 位置存储在 Amazon OpenSearch Service 中。
https://examlearn.online
[2026/05]
Question #714
Topic 1
⼀家公司在应⽤程序负载均衡器 (API) 后⽅的 Amazon EC2 实例上运⾏着⼀个⾼可⽤性 Web 应⽤程序。该公司
使⽤ Amazon CloudWatch 指标。
随着 Web 应⽤程序流量的增加，⼀些 EC2 实例会因⼤量未完成的请求⽽过载。CloudWatch 指标显示，与其它
EC2 实例相⽐，某些 EC2 实例处理的请求数量和响应时间都更⾼。该公司不希望将新请求转发到已经过载的
EC2 实例。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤基于 RequestCountPerTarget 和 ActiveConnectionCount CloudWatch 指标的轮询路由算法。
B. 使⽤基于 RequestCountPerTarget 和 ActiveConnectionCount CloudWatch 指标的最少未决请求算法。
C. 使⽤基于 RequestCount 和 TargetResponseTime CloudWatch 指标的轮询路由算法。
D. 使⽤基于 CloudWatch 指标 RequestCount 和 TargetResponseTime 的最少未完成请求算法。
Question #715
哪种解决⽅案能够以最⾼的运营效率满⾜这些要求？
Topic 1
⼀家公司在其 AWS 账户中使⽤ Amazon EC2、AWS Fargate 和 AWS Lambda 运⾏多个⼯作负载。该公司希望
充分利⽤其计算资源节省计划 (Compute Savings Plans)。该公司希望在计算资源节省计划的可⽤额度下降时收
到通知。
A. 使⽤ AWS Budgets 为储蓄计划创建每⽇预算。配置预算覆盖阈值，以便向相应的电⼦邮件收件⼈发送通
知。
B. 创建⼀个 Lambda 函数，⽤于⽣成储蓄计划的覆盖率报告。使⽤ Amazon Simple Email Service (Amazon
SES) 将报告通过电⼦邮件发送给相应的收件⼈。
C. 为储蓄计划预算创建 AWS 预算报告。将频率设置为每⽇。
D. 创建储蓄计划提醒订阅。启⽤所有通知选项。输⼊⽤于接收通知的电⼦邮件地址。
https://examlearn.online
[2026/05]
Question #716
Topic 1
⼀家公司在 AWS 上运⾏实时数据采集解决⽅案。该解决⽅案基于最新版本的 Amazon Managed Streaming for
Apache Kafka (Amazon MSK)。该解决⽅案部署在三个可⽤区私有⼦⽹的 VPC 中。
解决⽅案架构师需要重新设计该数据采集解决⽅案，使其可以通过互联⽹公开访问。传输中的数据也必须加密。
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
A. 在现有 VPC 中配置公有⼦⽹。在公有⼦⽹中部署 MSK 集群。更新 MSK 集群安全设置以启⽤双向 TLS 身
份验证。
B. 创建⼀个包含公有⼦⽹的新 VPC。在公有⼦⽹中部署 MSK 集群。更新 MSK 集群安全设置以启⽤双向 TLS
身份验证。
C. 部署使⽤私有⼦⽹的应⽤负载均衡器 (ALB)。配置 ALB 安全组⼊站规则，允许来⾃ VPC CIDR 块的
HTTPS 协议⼊站流量。
D. 部署使⽤私有⼦⽹的⽹络负载均衡器 (NLB)。配置 NLB 监听器以进⾏互联⽹上的 HTTPS 通信。
Question #717
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望将本地部署的传统应⽤程序迁移到 AWS。该应⽤程序从本地企业资源计划 (ERP) 系统导⼊客户订
单⽂件，然后将其上传到 SFTP 服务器。该应⽤程序使⽤定时任务每⼩时检查⼀次订单⽂件。
该公司已拥有⼀个可连接到本地⽹络的 AWS 账户。AWS 上的新应⽤程序必须⽀持与现有 ERP 系统的集成。新
应⽤程序必须安全可靠，并且必须使⽤ SFTP 协议⽴即处理来⾃ ERP 系统的订单。
A. 在两个可⽤区中创建⾯向互联⽹的 AWS Transfer Family SFTP 服务器。使⽤ Amazon S3 存储。创建⼀个
AWS Lambda 函数来处理订单⽂件。使⽤ S3 事件通知向 Lambda 函数发送 s3:ObjectCreated:* 事件。
B. 在⼀个可⽤区中创建⼀个⾯向互联⽹的 AWS Transfer Family SFTP 服务器。使⽤ Amazon Elastic File
System (Amazon EFS) 存储。创建⼀个 AWS Lambda 函数来处理订单⽂件。使⽤ Transfer Family 托管⼯
作流来调⽤该 Lambda 函数。
C. 在两个可⽤区中创建 AWS Transfer Family SFTP 内部服务器。使⽤ Amazon Elastic File System
(Amazon EFS) 存储。创建 AWS Step Functions 状态机来处理订单⽂件。使⽤ Amazon EventBridge
Scheduler 调⽤该状态机，定期检查 Amazon EFS 中是否存在订单⽂件。
D. 在两个可⽤区中创建 AWS Transfer Family SFTP 内部服务器。使⽤ Amazon S3 存储。创建 AWS
Lambda 函数来处理订单⽂件。使⽤ Transfer Family 托管⼯作流来调⽤ Lambda 函数。
https://examlearn.online
[2026/05]
Question #718
Topic 1
⼀家公司使⽤ Apache Hadoop 和 Apache Spark 在本地处理数据。现有基础设施不具备可扩展性，且管理复
杂。
解决⽅案架构师必须设计⼀个可扩展的解决⽅案，以降低运维复杂性。该解决⽅案必须保持数据处理在本地进
⾏。
哪个解决⽅案能够满⾜这些要求？
A. 使⽤ AWS 站点到站点 VPN 访问本地 Hadoop 分布式⽂件系统 (HDFS) 数据和应⽤程序。使⽤ Amazon
EMR 集群处理数据。
B. 使⽤ AWS DataSync 连接到本地 Hadoop 分布式⽂件系统 (HDFS) 集群。创建 Amazon EMR 集群来处理
数据。
C. 将 Apache Hadoop 应⽤程序和 Apache Spark 应⽤程序迁移到 AWS Outposts 上的 Amazon EMR 集
群。使⽤ EMR 集群处理数据。
D. 使⽤ AWS Snowball 设备将数据迁移到 Amazon S3 存储桶。创建 Amazon EMR 集群来处理数据。
Question #719
公司需要设计⼀个数据托管解决⽅案。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司正在将⼤量数据从本地存储迁移到 AWS。同⼀ AWS 区域中的基于 Windows、Mac 和 Linux 的
Amazon EC2 实例将使⽤ SMB 和 NFS 存储协议访问这些数据。该公司将定期访问部分数据，不定期访问剩余数
据。该
A. 创建⼀个使⽤ EFS 智能分层的 Amazon Elastic File System (Amazon EFS) 卷。使⽤ AWS DataSync 将
数据迁移到 EFS 卷。
B. 创建 Amazon FSx for ONTAP 实例。创建⼀个具有根卷且使⽤⾃动分层策略的 FSx for ONTAP ⽂件系
统。将数据迁移到 FSx for ONTAP 卷。
C. 创建⼀个使⽤ S3 智能分层的 Amazon S3 存储桶。使⽤ AWS Storage Gateway 或 Amazon S3 ⽂件⽹关
将数据迁移到 S3 存储桶。
D. 创建⼀个适⽤于 OpenZFS ⽂件系统的 Amazon FSx。将数据迁移到新卷。
https://examlearn.online
[2026/05]
Question #720
Topic 1
⼀家制造公司在 AWS 上运⾏其报表⽣成应⽤程序。该应⽤程序⽣成每份报表⼤约需要 20 分钟。该应⽤程序采⽤
单体架构，运⾏在单个 Amazon EC2 实例上。由于其模块紧密耦合，因此需要频繁更新。随着公司不断添加新功
能，应⽤程序的维护变得越来越复杂。
每次公司修补软件模块时，应⽤程序都会出现停机。每次中断后，报表⽣成都必须从头开始。公司希望重新设计
该应⽤程序，使其具有灵活性、可扩展性和渐进式改进能⼒，并尽可能减少应⽤程序的停机时间。
哪种解决⽅案能够满⾜这些要求？
A. 在 AWS Lambda 上以最⼤预置并发数运⾏单个函数来运⾏应⽤程序。
B. 在 Amazon EC2 Spot 实例上以微服务形式运⾏应⽤程序，并采⽤ Spot Fleet 默认分配策略。
C. 在 Amazon Elastic Container Service (Amazon ECS) 上以微服务形式运⾏应⽤程序，并启⽤服务⾃动扩
展。
D. 在 AWS Elastic Beanstalk 上以单⼀应⽤程序环境运⾏应⽤程序，并采⽤⼀次性部署策略。
Question #721
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望将⼀个⼤型 Web 应⽤程序重构为⽆服务器微服务架构。该应⽤程序使⽤ Amazon EC2 实例，并⽤
Python 编写。
该公司选择该 Web 应⽤程序的⼀个组件作为微服务进⾏测试。该组件每秒可处理数百个请求。该公司希望在⽀持
Python 的 AWS 解决⽅案上创建并测试该微服务。该解决⽅案还必须能够⾃动扩展，并且所需的基础设施和运维
⽀持最少。
A. 使⽤⽀持⾃动扩展的 Spot Fleet，运⾏最新的 Amazon Linux 操作系统的 EC2 实例。
B. 使⽤配置了⾼可⽤性的 AWS Elastic Beanstalk Web 服务器环境。
C. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS)。启动⾃管理 EC2 实例的⾃动扩展组。
D. 使⽤运⾏⾃定义开发代码的 AWS Lambda 函数。
https://examlearn.online
[2026/05]
Question #722
Topic 1
⼀家公司通过 AWS Direct Connect 从其本地环境连接到⼀个 AWS 账户。该 AWS 账户在同⼀ AWS 区域内有
30 个不同的 VPC。这些 VPC 使⽤私有虚拟接⼝ (VIF)。每个 VPC 都有⼀个 CIDR 块，该 CIDR 块与公司控制下
的其他⽹络互不重叠。
该公司希望集中管理⽹络架构，同时允许每个 VPC 与其他所有 VPC 和本地⽹络通信。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个传输⽹关，并将 Direct Connect 连接与⼀个新的传输 VIF 关联。启⽤传输⽹关的路由传播功能。
B. 创建 Direct Connect ⽹关。重新创建私有 VIF 以使⽤新⽹关。通过创建新的虚拟专⽤⽹关来关联每个
VPC。
C. 创建传输 VP。将 Direct Connect 连接连接到传输 VP。在区域中所有其他 VPC 之间创建对等连接。更新
路由表。
D. 从本地到每个 VPC 创建 AWS 站点到站点 VPN 连接。确保每个连接的两个 VPN 隧道均已建⽴。启⽤路由
传播功能。
Question #723
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏应⽤程序。这些 EC2 实例通过具有关联策略的 IAM ⻆⾊连接到 Amazon
RDS 数据库。该公司希望使⽤ AWS Systems Manager 为 EC2 实例打补丁，同时不中断正在运⾏的应⽤程序。
A. 创建⼀个新的 IAM ⻆⾊。将 AmazonSSMManagedInstanceCore 策略附加到新的 IAM ⻆⾊。将新的 IAM
⻆⾊附加到 EC2 实例和现有的 IAM ⻆⾊。
B. 创建⼀个 IAM ⽤户。将 AmazonSSMManagedInstanceCore 策略附加到该 IAM ⽤户。配置 Systems
Manager 以使⽤该 IAM ⽤户管理 EC2 实例。
C. 在 Systems Manager 中启⽤默认主机配置管理，以管理 EC2 实例。
D. 从现有 IAM ⻆⾊中移除现有策略。将 AmazonSSMManagedInstanceCore 策略添加到现有 IAM ⻆⾊。
https://examlearn.online
[2026/05]
Question #724
Topic 1
⼀家公司使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 Kubernetes Horizo ntal Pod Autoscaler
运⾏容器应⽤程序。⼯作负载在⼀天中并不稳定。解决⽅案架构师注意到，当集群中现有节点达到最⼤容量时，
节点数量不会⾃动扩展，这导致了性能问题。
哪种解决⽅案能够以最⼩的管理开销解决此问题？
A. 通过跟踪内存使⽤情况来扩展节点。
B. 使⽤ Kubernetes 集群⾃动扩缩器来管理集群中的节点数。
C. 使⽤ AWS Lambda 函数⾃动调整 EKS 集群的⼤⼩。
D. 使⽤ Amazon EC2 ⾃动扩展组来分配⼯作负载。
Question #725
Topic 1
⼀家公司每⽉在 Amazon S3 标准存储中维护约 300 TB 的数据。每个 S3 对象的⼤⼩通常约为 50 GB，并且经
常被其全局应⽤程序以分段上传的⽅式替换。S3 对象的数量和⼤⼩保持不变，但该公司的 S3 存储成本却逐⽉增
加。
在这种情况下，解决⽅案架构师应该如何降低成本？
A. 从 分段上传切换到 Amazon S3 传输加速。
B. 启⽤ S3 ⽣命周期策略，删除不完整的分段上传⽂件。
C. 配置 S3 清单，防⽌对象归档过快。
D. 配置 Amazon CloudFront 以减少存储在 Amazon S3 中的对象数量。
https://examlearn.online
[2026/05]
Question #726
Topic 1
⼀家公司部署了⼀款⾯向移动设备的多⼈游戏。该游戏需要根据经纬度实时追踪玩家的位置。游戏的数据存储必
须⽀持位置数据的快速更新和检索。
游戏使⽤带有只读副本的 Amazon RDS for PostgreSQL 数据库实例来存储位置数据。在⾼峰使⽤期间，数据库
⽆法维持读写更新所需的性能。游戏的⽤户群正在快速增⻓。
解决⽅案架构师应该如何提⾼数据层的性能？
A. 对现有数据库实例进⾏快照。启⽤多可⽤区 (Multi-AZ) 功能后恢复快照。
B. 使⽤ OpenSearch 控制⾯板从 Amazon RDS 迁移到 Amazon OpenSearch Service。
C. 在现有数据库实例前部署 Amazon DynamoDB Accelerator (DAX)。修改游戏以使⽤ DAX。
D. 在现有数据库实例前部署 Amazon ElastiCache for Redis 集群。修改游戏以使⽤ Redis。
Question #727
哪种解决⽅案能够以最⼩的运营开销满⾜此要求？
Topic 1
⼀家公司将关键数据存储在公司 AWS 账户中的 Amazon DynamoDB 表中。⼀位 IT 管理员不⼩⼼删除了⼀个
DynamoDB 表。此次删除导致⼤量数据丢失，并中断了公司的运营。该公司希望防⽌此类中断再次发⽣。
A. 在 AWS CloudTrail 中配置跟踪。创建⽤于删除操作的 Amazon EventBridge 规则。创建 AWS Lambda
函数以⾃动恢复已删除的 DynamoDB 表。
B. 为 DynamoDB 表创建备份和恢复计划。⼿动恢复 DynamoDB 表。
C. 配置 DynamoDB 表的删除保护。
D. 对 DynamoDB 表启⽤时间点恢复。
https://examlearn.online
[2026/05]
Question #728
Topic 1
⼀家公司拥有⼀个本地数据中⼼，但存储容量即将耗尽。该公司希望将其存储基础设施迁移到 AWS，同时尽可能
降低带宽成本。该解决⽅案必须能够实现数据的即时检索，且⽆需额外费⽤。
如何才能满⾜这些要求？
A. 部署 Amazon S3 Glacier Vault 并启⽤快速检索。为⼯作负载启⽤预置检索容量。
B. 使⽤缓存卷部署 AWS Storage Gateway。使⽤ Storage Gateway 将数据存储在 Amazon S3 中，同时在
本地保留常⽤数据⼦集的副本。
C. 使⽤存储卷部署 AWS Storage Gateway，将数据存储在本地。使⽤ Storage Gateway 将数据的时间点快
照异步备份到 Amazon S3。
D. 部署 AWS Direct Connect 以连接到本地数据中⼼。配置 AWS Storage Gateway 以在本地存储数据。使
⽤ Storage Gateway 将数据的时间点快照异步备份到 Amazon S3。
Question #729
Topic 1
⼀家公司在跨多个可⽤区的 VPC 中运⾏⼀个三层 Web 应⽤程序。应⽤程序层使⽤ Amazon EC2 实例，并部署
在⾃动扩展组中。
该公司需要制定⼀个⾃动扩展计划，该计划将分析每个资源的每⽇和每周历史⼯作负载趋势。配置必须根据预测
和实际利⽤率的变化来适当地扩展资源。
解决⽅案架构师应该推荐哪种扩展策略来满⾜这些要求？
A. 根据 EC2 实例的平均 CPU 利⽤率，实现动态扩展和步进式扩展。
B. 启⽤预测扩展功能，以进⾏预测和扩展。配置带有⽬标跟踪的动态扩展功能。
C. 根据 Web 应⽤程序的流量模式创建⾃动计划扩展操作。
D. 设置简单的扩展策略。根据 EC2 实例的启动时间增加冷却时间。
https://examlearn.online
[2026/05]
Question #730
Topic 1
⼀家包裹递送公司有⼀个使⽤ Amazon EC2 实例和 Amazon Aurora MySQL 数据库集群的应⽤程序。随着应⽤
程序使⽤量的增⻓，EC2 实例的使⽤量仅略有增加，⽽数据库集群的使⽤量增⻓速度却快得多。
该公司添加了⼀个只读副本，这在短期内降低了数据库集群的使⽤量。然⽽，负载持续增加。导致数据库集群使
⽤量增加的操作都是与递送详情相关的重复读取语句。该公司需要减轻重复读取对数据库集群的影响。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在应⽤程序和数据库集群之间实现 Amazon ElastiCache for Redis 集群。
B. 向数据库集群添加⼀个额外的只读副本。
C. 为 Aurora 只读副本配置 Aurora ⾃动扩展。
D. 修改数据库集群，使其具有多个写⼊实例。
Question #731
解决⽅案架构师应该建议进⾏哪项设计更改？
A. 向表中添加只读副本。
Topic 1
⼀家公司有⼀个使⽤ Amazon DynamoDB 表进⾏存储的应⽤程序。解决⽅案架构师发现，对该表的许多请求没
有返回最新数据。该公司⽤户没有报告任何其他数据库性能问题。延迟在可接受的范围内。
B. 使⽤全球⼆级索引（GSI）。
C. 请求对表进⾏强⼀致性读取。
D. 请求对表进⾏最终⼀致性读取。
https://examlearn.online
[2026/05]
Question #732
Topic 1
⼀家公司已将其应⽤程序部署在 Amazon EC2 实例上，并使⽤ Amazon RDS 数据库。该公司遵循最⼩权限原则
配置数据库访问凭证。该公司的安全团队希望保护应⽤程序和数据库免受 SQL 注⼊和其他基于 Web 的攻击。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 使⽤安全组和⽹络 ACL 来保护数据库和应⽤程序服务器。
B. 使⽤ AWS WAF 保护应⽤程序。使⽤ RDS 参数组配置安全设置。
C. 使⽤ AWS ⽹络防⽕墙保护应⽤程序和数据库。
D. 在应⽤程序代码中为不同的功能使⽤不同的数据库帐户。避免授予数据库⽤户过多的权限。
Question #733
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
Topic 1
⼀家电⼦商务公司在 AWS Organizations 组织内的多个 AWS 账户中运⾏应⽤程序。这些应⽤程序运⾏在所有账
户的 Amazon Aurora PostgreSQL 数据库上。该公司需要防⽌恶意活动，并且必须识别异常的数据库登录失败和
不完整尝试。
A. 将服务控制策略 (SCP) 附加到组织的根⽬录，以识别失败的登录尝试。
B. 在 Amazon GuardDuty 中为组织的成员帐户启⽤ Amazon RDS Protection 功能。
C. 将 Aurora 常规⽇志发布到 Amazon CloudWatch Logs 中的⽇志组。将⽇志数据导出到中央 Amazon S3
存储桶。
D. 将 AWS CloudTrail 中的所有 Aurora PostgreSQL 数据库事件发布到中央 Amazon S3 存储桶。
https://examlearn.online
[2026/05]
Question #734
Topic 1
⼀家公司通过 AWS Direct Connect 将其企业数据中⼼连接到位于 us-east-1 区域的 VPC。该公司最近收购了⼀
家拥有多个 VPC 的企业，该企业在其本地数据中⼼和位于 eu-west-2 区域的 VPC 之间也建⽴了 Direct
Connect 连接。该公司和被收购企业的 VPC 的 CIDR 块并不重叠。该公司需要连接两个区域及其数据中⼼。该
公司需要⼀个可扩展且能降低运营成本的解决⽅案。
解决⽅案架构师应该如何满⾜这些要求？
A. 在 us-east-1 中的 VPC 和 eu-west-2 中的 VPC 之间建⽴跨区域 VPC 对等连接。
B. 从 us-east-1 中的 Direct Connect 连接创建到 eu-west-2 中的 VPC 的私有虚拟接⼝。
C. 在由 Amazon EC2 托管的全⽹状 VPN ⽹络中建⽴ VPN 设备。使⽤ AWS VPN CloudHub 在数据中⼼和每
个 VPC 之间发送和接收数据。
D. 将现有的 Direct Connect 连接连接到 Direct Connect ⽹关。将来⾃每个区域中 VPC 的虚拟专⽤⽹关的流
量路由到 Direct Connect ⽹关。
Question #735
解决⽅案架构师应该如何满⾜这些要求？
Topic 1
⼀家公司正在开发⼀款⼿机游戏，该游戏会将分数更新实时传输到后端处理器，然后将结果发布到排⾏榜上。解
决⽅案架构师需要设计⼀个能够应对流量⾼峰、按接收顺序处理⼿机游戏更新并将处理后的更新存储在⾼可⽤数
据库中的解决⽅案。该公司还希望最⼤限度地减少维护该解决⽅案所需的管理开销。
A. 将分数更新推送⾄ Amazon Kinesis Data Streams。使⽤ AWS Lambda 处理 Kinesis Data Streams 中的
更新。将处理后的更新存储⾄ Amazon DynamoDB。
B. 将分数更新推送⾄ Amazon Kinesis Data Streams。使⽤已配置⾃动扩展的 Amazon EC2 实例集群处理这
些更新。将处理后的更新存储在 Amazon Redshift 中。
C. 将分数更新推送⾄ Amazon Simple Notification Service (Amazon SNS) 主题。订阅⼀个 AWS Lambda
函数⾄该 SNS 主题以处理更新。将处理后的更新存储在运⾏于 Amazon EC2 上的 SQL 数据库中。
D. 将评分更新推送⾄ Amazon Simple Queue Service (Amazon SQS) 队列。使⽤启⽤⾃动扩展功能的
Amazon EC2 实例集群来处理 SQS 队列中的更新。将处理后的更新存储在 Amazon RDS 多可⽤区数据库实
例中。
https://examlearn.online
[2026/05]
Question #736
Topic 1
⼀家公司在 us-west-2 区域部署了多个 AWS 账户及其应⽤程序。应⽤程序⽇志存储在每个账户的 Amazon S3
存储桶中。该公司希望构建⼀个集中式⽇志分析解决⽅案，该⽅案仅使⽤⼀个 S3 存储桶。⽇志不得离开 us
west-2 区域，并且该公司希望将运营成本降⾄最低。
哪种解决⽅案既满⾜这些要求，⼜最具成本效益？
A. 创建⼀个 S3 ⽣命周期策略，将对象从应⽤程序 S3 存储桶复制到集中式 S3 存储桶。
B. 使⽤ S3 同区域复制将⽇志从 S3 存储桶复制到 us-west-2 中的另⼀个 S3 存储桶。使⽤此 S3 存储桶进⾏
⽇志分析。
C. 编写⼀个脚本，每天使⽤ PutObject API 操作将存储桶的全部内容复制到 us-west-2 中的另⼀个 S3 存储
桶。使⽤此 S3 存储桶进⾏⽇志分析。
D. 在这些账户中编写 AWS Lambda 函数，以便在每次⽇志被发送到 S3 存储桶时触发（s3:ObjectCreated:*
事件）。将⽇志复制到 us-west-2 分区中的另⼀个 S3 存储桶。使⽤此 S3 存储桶进⾏⽇志分析。
Question #737
southeast-1 S3 存储桶的单向复制。
Topic 1
⼀家公司开发了⼀款应⽤程序，可向全球学⽣提供按需培训视频。该应⽤程序还允许授权的内容开发者上传视
频。数据存储在位于 us-east-2 区域的 Amazon S3 存储桶中。
该公司已在 eu-west-2 区域和 ap-southeast-1 区域分别创建了⼀个 S3 存储桶。该公司希望将数据复制到新的
S3 存储桶中。该公司需要尽可能降低 eu-west-2 和 ap-southeast-1 区域附近上传视频的开发者和观看视频的学
⽣的延迟。
以下哪两项措施组合能够以对应⽤程序改动最少的⽅式满⾜这些要求？（选择两项。）
A. 配置从 us-east-2 S3 存储桶到 eu-west-2 S3 存储桶的单向复制。配置从 us-east-2 S3 存储桶到 ap
B. 配置从 us-east-2 S3 存储桶到 eu-west-2 S3 存储桶的单向复制。配置从 eu-west-2 S3 存储桶到 ap
southeast-1 S3 存储桶的单向复制。
C. 配置位于三个区域中的 S3 存储桶之间的双向复制。
D. 创建 S3 多区域访问点。修改应⽤程序，使其使⽤该多区域访问点的 Amazon 资源名称 (ARN) 进⾏视频流
传输。请勿修改应⽤程序以进⾏视频上传。
E. 创建 S3 多区域访问点。修改应⽤程序，使其使⽤多区域访问点的 Amazon 资源名称 (ARN) 进⾏视频流传
输和上传。
https://examlearn.online
[2026/05]
Question #738
Topic 1
⼀家公司推出了⼀款新的移动应⽤。⽤户⽆论身处世界何地，都能浏览他们选择主题的本地新闻。⽤户还可以直
接在应⽤内发布照⽚和视频。
⽤户通常会在内容发布后的最初⼏分钟内访问它。新内容会迅速取代旧内容，然后旧内容就会消失。由于新闻的
本地化特性，⽤户90%的内容都来⾃其上传所在的AWS区域。
哪种解决⽅案能够通过提供最低的内容上传延迟来优化⽤户体验？
A. 将内容上传并存储到 Amazon S3。使⽤ Amazon CloudFront 进⾏上传。
B. 将内容上传并存储到 Amazon S3 中。使⽤ S3 传输加速进⾏上传。
C. 将内容上传到距离⽤户最近的区域中的 Amazon EC2 实例。将数据复制到 Amazon S3。
D. 将内容上传并存储在距离⽤户最近的 Amazon S3 区域中。使⽤多个 Amazon CloudFront 分发。
Question #739
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
询不同的 SQS 队列。
Lambda 函数。
Topic 1
⼀家公司正在构建⼀个采⽤⽆服务器架构的新应⽤程序。该架构将包含⼀个 Amazon API Gateway REST API 和
⽤于管理传⼊请求的 AWS Lambda 函数。
该公司希望添加⼀项服务，该服务可以将从 API Gateway REST API 接收到的消息发送到多个⽬标 Lambda 函数
进⾏处理。该服务必须提供消息过滤功能，使⽬标 Lambda 函数能够仅接收其所需的消息。
A. 将来⾃ API Gateway REST API 的请求发送到 Amazon Simple Notification Service (Amazon SNS) 主
题。将 Amazon Simple Queue Service (Amazon SQS) 队列订阅到 SNS 主题。配置⽬标 Lambda 函数以轮
B. 将来⾃ API Gateway REST API 的请求发送到 Amazon EventBridge。配置 EventBridge 以调⽤⽬标
C. 将来⾃ API Gateway REST API 的请求发送到 Amazon Managed Streaming for Apache Kafka (Amazon
MSK)。配置 Amazon MSK 将消息发布到⽬标 Lambda 函数。
D. 将来⾃ API Gateway REST API 的请求发送到多个 Amazon Simple Queue Service (Amazon SQS) 队
列。配置⽬标 Lambda 函数以轮询不同的 SQS 队列。
https://examlearn.online
[2026/05]
Question #740
Topic 1
⼀家公司将数百万个归档⽂件迁移到了 Amazon S3。解决⽅案架构师需要实现⼀个解决⽅案，使⽤客户提供的密
钥对所有归档数据进⾏加密。该解决⽅案必须加密现有的未加密对象以及未来的对象。
哪个解决⽅案能够满⾜这些要求？
A. 通过筛选 Amazon S3 清单报告，创建未加密对象列表。配置 S3 批量操作作业，使⽤客户提供的密钥
(SSE-C) 对列表中的对象进⾏服务器端加密。配置 S3 默认加密功能，使其使⽤客户提供的密钥 (SSE-C) 进
⾏服务器端加密。
B. 使⽤ S3 Storage Lens 指标来识别未加密的 S3 存储桶。将 S3 默认加密功能配置为使⽤基于 AWS KMS
密钥的服务器端加密 (SSE-KMS)。
C. 通过筛选 Amazon S3 的 AWS 使⽤情况报告，创建未加密对象列表。配置 AWS Batch 作业，使⽤ AWS
KMS 密钥 (SSE-KMS) 对列表中的对象进⾏服务器端加密。配置 S3 默认加密功能，使其使⽤ AWS KMS 密
钥 (SSE-KMS) 进⾏服务器端加密。
D. 通过筛选 Amazon S3 的 AWS 使⽤情况报告，创建未加密对象列表。配置 S3 默认加密功能，使其使⽤客
户提供的密钥进⾏服务器端加密 (SSE-C)。
Question #741
解决⽅案架构师应该如何快速迁移 DNS 托管服务？
Topic 1
为公司托管域名记录的 DNS 提供商出现故障，导致运⾏在 AWS 上的⽹站服务中断。该公司需要迁移到更具弹性
的托管 DNS 服务，并希望该服务运⾏在 AWS 上。
A. 为该域名创建⼀个 Amazon Route 53 公共托管区域。导⼊之前服务提供商托管的包含域名记录的区域⽂
件。
B. 为该域名创建⼀个 Amazon Route 53 私有托管区域。导⼊包含先前提供商托管的域名记录的区域⽂件。
C. 在 AWS 中创建⼀个简单的 AD ⽬录。启⽤ DNS 提供商和 AWS Directory Service for Microsoft Active
Directory 之间的区域传输，以传输域记录。
D. 在 VPC 中创建 Amazon Route 53 解析器⼊站终端节点。指定提供商的 DNS 会将 DNS 查询转发到的 IP
地址。配置提供商的 DNS，使其将针对该域的 DNS 查询转发到⼊站终端节点中指定的 IP 地址。
https://examlearn.online
[2026/05]
Question #742
Topic 1
⼀家公司正在AWS上构建⼀个连接到Amazon RDS数据库的应⽤程序。该公司希望管理应⽤程序配置，并安全地
存储和检索数据库及其他服务的凭证。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 使⽤ AWS AppConfig 存储和管理应⽤程序配置。使⽤ AWS Secrets Manager 存储和检索凭证。
B. 使⽤ AWS Lambda 存储和管理应⽤程序配置。使⽤ AWS Systems Manager Parameter Store 存储和检
索凭证。
C. 使⽤加密的应⽤程序配置⽂件。将该⽂件存储在 Amazon S3 中，⽤于存储应⽤程序配置信息。创建另⼀
个 S3 ⽂件来存储和检索凭证。
D. 使⽤ AWS AppConfig 存储和管理应⽤程序配置。使⽤ Amazon RDS 存储和检索凭证。
Question #743
Topic 1
为了满⾜安全要求，⼀家公司需要在与 Amazon RDS MySQL 数据库实例通信时，对所有传输中的应⽤程序数据
进⾏加密。最近的⼀次安全审计发现，静态数据加密已使⽤ AWS Key Management Service (AWS KMS) 启⽤，
但传输中数据加密尚未启⽤。
解决⽅案架构师应该如何做才能满⾜这些安全要求？
A. 在数据库上启⽤ IAM 数据库身份验证。
B. 提供⾃签名证书。在与 RDS 实例的所有连接中使⽤这些证书。
C. 对 RDS 实例进⾏快照。将快照还原到启⽤加密的新实例。
D. 下载 AWS 提供的根证书。在与 RDS 实例的所有连接中提供这些证书。
https://examlearn.online
[2026/05]
Question #744
Topic 1
⼀家公司正在设计⼀项新的 Web 服务，该服务将运⾏在 Amazon EC2 实例上，并由弹性负载均衡器 (ELB) 进⾏
负载均衡。然⽽，许多 Web 服务客户端只能访问其防⽕墙上授权的 IP 地址。
解决⽅案架构师应该提出怎样的建议才能满⾜客户的需求？
A. 具有关联弹性 IP 地址的⽹络负载均衡器。
B. 具有关联弹性 IP 地址的应⽤负载均衡器。
C. Amazon Routs 53 托管区域中指向弹性 IP 地址的 A 记录。
D. 具有公共 IP 地址的 EC2 实例，作为负载均衡器前⾯的代理运⾏。
Question #745
应该采取哪些措施来保护根⽤户？
Topic 1
⼀家公司创建了⼀个新的 AWS 账户。该账户是新创建的，默认设置未做任何更改。该公司担⼼ AWS 账户根⽤户
的安全。
A. 创建⽤于⽇常管理任务的 IAM ⽤户。禁⽤ root ⽤户。
B. 创建⽤于⽇常管理任务的 IAM ⽤户。对根⽤户启⽤多因素身份验证。
C. 为根⽤户⽣成访问密钥。⽇常管理任务请使⽤访问密钥，⽽不是使⽤ AWS 管理控制台。
D. 向级别最⾼的解决⽅案架构师提供 root ⽤户凭据。让解决⽅案架构师使⽤ root ⽤户执⾏⽇常管理任务。
https://examlearn.online
[2026/05]
Question #746
Topic 1
⼀家公司正在部署⼀个近乎实时处理流数据的应⽤程序。该公司计划使⽤ Amazon EC2 实例来处理该⼯作负载。
⽹络架构必须可配置，以提供节点间尽可能低的延迟。
以下哪两项⽹络解决⽅案组合能够满⾜这些要求？
A. 在每个 EC2 实例上启⽤和配置增强型⽹络。
B. 将 EC2 实例分组到不同的账户中。
C. 在集群放置组中运⾏ EC2 实例。
D. 将多个弹性⽹络接⼝附加到每个 EC2 实例。
E. 使⽤ Amazon Elastic Block Store (Amazon EBS) 优化的实例类型。
Question #747
Topic 1
⼀家⾦融服务公司计划关闭两个数据中⼼，并将超过 100 TB 的数据迁移到 AWS。这些数据具有复杂的⽬录结
构，数百万个⼩⽂件存储在层级极深的⼦⽂件夹中。⼤部分数据为⾮结构化数据，且公司的⽂件存储由来⾃多家
供应商的基于 SMB 的存储类型组成。该公司不希望在迁移后更改其应⽤程序以访问数据。
解决⽅案架构师应该如何做才能在尽可能减少运维开销的情况下满⾜这些要求？
A. 使⽤ AWS Direct Connect 将数据迁移到 Amazon S3。
B. 使⽤ AWS DataSync 将数据迁移到 Amazon FSx for Lustre。
C. 使⽤ AWS DataSync 将数据迁移到 Amazon FSx for Windows ⽂件服务器。
D. 使⽤ AWS Direct Connect 将本地⽂件存储中的数据迁移到 AWS Storage Gateway 卷⽹关。
https://examlearn.online
[2026/05]
Question #748
Topic 1
⼀家公司使⽤ AWS Organizations 中的组织来管理包含应⽤程序的 AWS 账户。该公司在该组织中设置了⼀个专
⽤的监控成员账户。该公司希望使⽤ Amazon CloudWatch 查询和可视化跨账户的可观测性数据。
哪种解决⽅案能够满⾜这些要求？
A. 为监控账户启⽤ CloudWatch 跨账户可观测性。在每个 AWS 账户中部署由监控账户提供的 AWS
CloudFormation 模板，以便与监控账户共享数据。
B. 设置服务控制策略 (SCP)，以提供对组织根组织单元 (OU) 下的监控帐户中 CloudWatch 的访问权限。
C. 在监控账户中配置⼀个新的 IAM ⽤户。在每个 AWS 账户中，配置⼀个 IAM 策略，使其能够查询和可视化
账户中的 CloudWatch 数据。将新的 IAM 策略附加到新的 IAM ⽤户。
D. 在监控账户中创建⼀个新的 IAM ⽤户。在每个 AWS 账户中创建跨账户 IAM 策略。将这些 IAM 策略附加
到新的 IAM ⽤户。
Question #749
解决⽅案架构师应该如何保护该应⽤程序？
Topic 1
⼀家公司的⽹站⽤于向公众销售产品。该⽹站运⾏在 Amazon EC2 实例上，这些实例位于⾃动扩展组 (Auto
Scaling group) 中，并由应⽤程序负载均衡器 (ALB) 提供⽀持。此外，该⽹站还部署了 Amazon CloudFront 分
发，并使⽤ AWS Web 应⽤防⽕墙 (WAF) 来防御 SQL 注⼊攻击。ALB 是 CloudFront 分发的源站。最近对安全
⽇志的审查发现了⼀个外部恶意 IP 地址，需要阻⽌其访问该⽹站。
A. 修改 CloudFront 分发上的⽹络 ACL，添加⼀条拒绝恶意 IP 地址的规则。
B. 修改 AWS WAF 的配置，添加 IP 匹配条件以阻⽌恶意 IP 地址。
C. 修改 ALB 后⾯的⽬标组中 EC2 实例的⽹络 ACL，以拒绝恶意 IP 地址。
D. 修改 ALB 后⾯的⽬标组中 EC2 实例的安全组，以拒绝恶意 IP 地址。
https://examlearn.online
[2026/05]
Question #750
⼀家公司在 AWS Organizations 中创建了⼀个包含 10 个 AWS 账户的组织。解决⽅案架构师必须设计⼀个解决
⽅案，为数千名员⼯提供对这些账户的访问权限。该公司已有身份提供商 (IdP)。该公司希望使⽤该现有 IdP 进⾏
AWS 身份验证。
哪个解决⽅案能够满⾜这些要求？
Topic 1
A. 在所需的 AWS 账户中为员⼯创建 IAM ⽤户。将 IAM ⽤户连接到现有的身份提供商 (IdP)。为 IAM ⽤户配
置联合身份验证。
B. 设置 AWS 账户根⽤户，⽤户电⼦邮件地址和密码从现有身份提供商 (IdP) 同步。
C. 配置 AWS IAM 身份中⼼（AWS 单点登录）。将 IAM 身份中⼼连接到现有身份提供商 (IdP)。从现有 IdP
配置⽤户和组。
D. 使⽤ AWS 资源访问管理器 (AWS RAM) 与现有身份提供商 (IdP) 中的⽤户共享对 AWS 账户的访问权限。
https://examlearn.online
[2026/05]
Question #751
Topic 1
⼀位解决⽅案架构师正在为公司的 AWS 账户设计 AWS Identity and Access Management (IAM) 授权模型。该
公司已指定五名员⼯拥有对该 AWS 账户中 AWS 服务和资源的完全访问权限。
该解决⽅案架构师已为这五名指定员⼯分别创建了⼀个 IAM ⽤户和⼀个 IAM ⽤户组。
哪种解决⽅案能够满⾜这些要求？
A. 将 AdministratorAccess 资源策略附加到 IAM ⽤户组。将五个指定的员⼯ IAM ⽤户分别添加到该 IAM ⽤
户组中。
B. 将系统管理员身份策略附加到 IAM ⽤户组。将五个指定的员⼯ IAM ⽤户分别添加到 IAM ⽤户组中。
C. 将 AdministratorAccess 基于身份的策略附加到 IAM ⽤户组。将五个指定的员⼯ IAM ⽤户分别添加到
IAM ⽤户组中。
D. 将系统管理员资源策略附加到 IAM ⽤户组。将五个指定的员⼯ IAM ⽤户分别添加到该 IAM ⽤户组中。
Question #752
以下哪两项操作组合能够满⾜这些要求？
Topic 1
⼀家公司拥有⼀个基于虚拟机 (VM) 的多层⽀付处理应⽤程序。各层之间的通信通过第三⽅中间件解决⽅案异步
进⾏，该⽅案保证消息仅⼀次交付。
该公司需要⼀个基础设施管理量最⼩的解决⽅案，并且该解决⽅案必须保证应⽤程序消息的仅⼀次交付。
A. 在架构中使⽤ AWS Lambda 作为计算层。
B. 在架构的计算层中使⽤ Amazon EC2 实例。
C. 使⽤ Amazon Simple Notification Service (Amazon SNS) 作为计算层之间的消息传递组件。
D. 使⽤ Amazon Simple Queue Service (Amazon SQS) FIFO 队列作为计算层之间的消息传递组件。
E. 在架构的计算层中使⽤基于 Amazon Elastic Kubernetes Service (Amazon EKS) 的容器。
https://examlearn.online
[2026/05]
Question #753
Topic 1
⼀家公司有⼀个夜间批处理程序，⽤于分析本地⽂件系统每天通过 SFTP 接收的报告⽂件。该公司希望将此解决
⽅案迁移到 AWS 云。该解决⽅案必须具备⾼可⽤性和弹性，并且必须最⼤限度地减少运维⼯作量。
哪个解决⽅案满⾜这些要求？
A. 部署 AWS Transfer ⽤于 SFTP 传输，并使⽤ Amazon Elastic File System (Amazon EFS) ⽂件系统进⾏
存储。使⽤⾃动扩展组中的 Amazon EC2 实例，并设置计划扩展策略来运⾏批处理操作。
B. 部署⼀个运⾏ Linux 和 SFTP 服务的 Amazon EC2 实例。使⽤ Amazon Elastic Block Store (Amazon
EBS) 卷进⾏存储。使⽤⾃动扩展组，并将最⼩实例数和期望实例数均设置为 1。
C. 部署⼀个运⾏ Linux 和 SFTP 服务的 Amazon EC2 实例。使⽤ Amazon Elastic File System (Amazon
EFS) ⽂件系统进⾏存储。使⽤⾃动扩展组，并将最⼩实例数和期望实例数都设置为 1。
D. 部署 AWS Transfer ⽤于 SFTP 传输，并使⽤ Amazon S3 存储桶进⾏存储。修改应⽤程序，使其将批处理
⽂件从 Amazon S3 拉取到 Amazon EC2 实例进⾏处理。使⽤具有计划扩展策略的⾃动扩展组中的 EC2 实例
来运⾏批处理操作。
Question #754
解决⽅案架构师应该提出什么建议来实现这些⽬标？
Topic 1
⼀家公司拥有遍布全球的⽤户，他们通过部署在多个 AWS 区域的 Amazon EC2 实例上的 HTTP 应⽤程序访问该
应⽤程序。该公司希望提⾼应⽤程序的可⽤性和性能，并保护其免受可能影响可⽤性、损害安全性或消耗过多资
源的常⻅ Web 攻击。静态 IP 地址是必需的。
A. 将 EC2 实例部署在每个区域的⽹络负载均衡器 (NLB) 之后。在 NLB 上部署 AWS WAF。使⽤ AWS
Global Accelerator 创建加速器，并将 NLB 注册为终端节点。
B. 将 EC2 实例部署在每个区域的应⽤程序负载均衡器 (ALB) 之后。在 ALB 上部署 AWS WAF。使⽤ AWS
Global Accelerator 创建加速器，并将 ALB 注册为终端节点。
C. 将 EC2 实例置于每个区域的⽹络负载均衡器 (NLB) 之后。在 NLB 上部署 AWS WAF。创建⼀个 Amazon
CloudFront 分发，其源使⽤ Amazon Route 53 基于延迟的路由将请求路由到 NLB。
D. 将 EC2 实例部署在每个区域的应⽤程序负载均衡器 (ALB) 之后。创建⼀个 Amazon CloudFront 分发，其
源服务器使⽤ Amazon Route 53 基于延迟的路由将请求路由到 ALB。在 CloudFront 分发上部署 AWS
WAF。
https://examlearn.online
[2026/05]
Question #755
Topic 1
⼀家公司的数据平台使⽤ Amazon Aurora MySQL 数据库。该数据库拥有多个只读副本，并且跨多个可⽤区部署
了多个数据库实例。⽤户最近报告数据库出现错误，表明连接数过多。该公司希望在将只读副本提升为主写⼊实
例时，将故障转移时间缩短 20%。
哪种解决⽅案能够满⾜此要求？
A. 从 Aurora 切换到 Amazon RDS，并部署多可⽤区集群。
B. 在 Aurora 数据库前⾯使⽤ Amazon RDS 代理。
C. 使⽤ DynamoDB Accelerator (DAX) 切换到 Amazon DynamoDB 进⾏读取连接。
D. 切换到具有迁移功能的 Amazon Redshift。
Question #756
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
Topic 1
⼀家公司将⽂本⽂件存储在 Amazon S3 中。这些⽂本⽂件包含客户聊天记录、⽇期和时间信息以及客户个⼈身
份信息 (PII)。
该公司需要⼀个解决⽅案，以便向外部服务提供商提供对话样本进⾏质量控制。外部服务提供商需要随机抽取对
话样本，直⾄最近的对话。该公司不得与外部服务提供商共享客户的 PII。该解决⽅案必须能够随着客户对话数量
的增加⽽扩展。
A. 创建对象 Lambda 访问点。创建⼀个 AWS Lambda 函数，该函数在读取⽂件时会脱敏处理个⼈身份信息
(PII)。指示外部服务提供商访问该对象 Lambda 访问点。
B. 在 Amazon EC2 实例上创建⼀个批处理进程，定期读取所有新⽂件，从⽂件中删除个⼈身份信息 (PII)，并
将删除后的⽂件写⼊不同的 S3 存储桶。指示外部服务提供商访问不包含 PII 的存储桶。B
. 在 Amazon EC2 实例上创建⼀个 Web 应⽤程序，该应⽤程序显示⽂件列表，从⽂件中删除 PII，并允许外
部服务提供商下载已删除 PII 的⽂件的新版本。
D. 创建⼀个 Amazon DynamoDB 表。创建⼀个 AWS Lambda 函数，该函数仅读取⽂件中不包含个⼈身份信
息 (PII) 的数据。配置 Lambda 函数，使其在向 Amazon S3 写⼊新⽂件时，将⾮ PII 数据存储到 DynamoDB
表中。授予外部服务提供商对 DynamoDB 表的访问权限。
https://examlearn.online
[2026/05]
Question #757
Topic 1
⼀家公司在亚⻢逊 EC2 实例上运⾏着⼀个遗留系统。该应⽤程序代码⽆法修改，且系统只能在单个实例上运⾏。
解决⽅案架构师必须设计⼀个能够缩短系统恢复时间的弹性解决⽅案。
为了满⾜这些要求，解决⽅案架构师应该提出怎样的建议？
A. 为 EC2 实例启⽤终⽌保护。
B. 配置 EC2 实例以进⾏多可⽤区部署。
C. 创建 Amazon CloudWatch 警报，以便在发⽣故障时恢复 EC2 实例。
D. 启动 EC2 实例，使⽤两个 Amazon Elastic Block Store (Amazon EBS) 卷，采⽤ RAID 配置实现存储冗
余。
Question #758
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司希望将其容器化应⽤程序⼯作负载部署到跨三个可⽤区的 VPC 中。该公司需要⼀个跨可⽤区⾼可⽤的解
决⽅案，并且该解决⽅案必须对应⽤程序进⾏尽可能少的更改。
A. 使⽤ Amazon Elastic Container Service (Amazon ECS)。配置 Amazon ECS 服务⾃动扩展以使⽤⽬标跟
踪扩展。将最⼩容量设置为 3。将任务放置策略类型设置为“分散”，并指定可⽤区属性。
B. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) ⾃管理节点。配置应⽤程序⾃动扩展以使⽤⽬
标跟踪扩展。将最⼩容量设置为 3。
C. 使⽤ Amazon EC2 预留实例。在分散放置组中启动三个 EC2 实例。配置⾃动扩展组以使⽤⽬标跟踪扩
展。将最⼩容量设置为 3。
D. 使⽤ AWS Lambda 函数。配置 Lambda 函数以连接到 VPC。配置应⽤程序⾃动扩展以使⽤ Lambda 作为
可扩展⽬标。将最⼩容量设置为 3。
https://examlearn.online
[2026/05]
Question #759
Topic 1
⼀家媒体公司将电影存储在 Amazon S3 上。每部电影都以单个视频⽂件的形式存储，⼤⼩从 1 GB 到 10 GB 不
等。
该公司必须能够在⽤户购买后 5 分钟内提供电影的流媒体内容。⽤户对上映不到 20 年的电影的需求量⾼于上映
超过 20 年的电影。该公司希望根据需求量来降低托管服务成本。
哪种解决⽅案能够满⾜这些要求？
A. 将所有媒体内容存储在 Amazon S3 中。当对某部电影的需求减少时，使⽤ S3 ⽣命周期策略将媒体数据移
⾄不频繁访问层。
B. 将较新的电影视频⽂件存储在 S3 标准版中。将较旧的电影视频⽂件存储在 S3 标准版-不频繁访问 (S3
Standard-IA) 中。当⽤户订购较旧的电影时，使⽤标准检索⽅式检索视频⽂件。
C. 将较新的电影视频⽂件存储在 S3 智能分层存储中。将较旧的电影视频⽂件存储在 S3 Glacier 灵活检索存
储中。当⽤户订购较旧的电影时，使⽤快速检索⽅式检索视频⽂件。
D. 将较新的电影视频⽂件存储在 S3 标准版中。将较旧的电影视频⽂件存储在 S3 Glacier 灵活检索版中。当
⽤户订购较旧的电影时，使⽤批量检索功能检索视频⽂件。
Question #760
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Amazon S3 卷。
Block Store (Amazon EBS) 卷。
Topic 1
解决⽅案架构师需要为供应商提供的 Docker 容器镜像中的应⽤程序设计架构。该容器需要 50 GB 的存储空间⽤
于存放临时⽂件。基础设施必须是⽆服务器的。
A. 创建⼀个 AWS Lambda 函数，该函数使⽤ Docker 容器镜像，并挂载⼀个拥有超过 50 GB 空间的
B. 创建⼀个 AWS Lambda 函数，该函数使⽤ Docker 容器镜像，并具有超过 50 GB 空间的 Amazon Elastic
C. 创建⼀个使⽤ AWS Fargate 启动类型的 Amazon Elastic Container Service (Amazon ECS) 集群。为容
器镜像创建⼀个任务定义，该镜像使⽤ Amazon Elastic File System (Amazon EFS) 卷。使⽤该任务定义创
建⼀个服务。
D. 创建⼀个使⽤ Amazon EC2 启动类型的 Amazon Elastic Container Service (Amazon ECS) 集群，并分
配⼀个具有超过 50 GB 空间的 Amazon Elastic Block Store (Amazon EBS) 卷。为容器镜像创建任务定义。
使⽤该任务定义创建服务。
https://examlearn.online
[2026/05]
Question #761
Topic 1
⼀家公司需要使⽤其本地部署的 LDAP ⽬录服务来验证⽤户身份，以便访问 AWS 管理控制台。该⽬录服务与安
全断⾔标记语⾔ (SAML) 不兼容。
哪种解决⽅案满⾜这些要求？
A. 在 AWS 和本地 LDAP 之间启⽤ AWS IAM Identity Center（AW S 单点登录）。
B. 创建⼀个使⽤ AWS 凭证的 IAM 策略，并将该策略集成到 LDAP 中。
C. 建⽴⼀个流程，当 LDAP 凭据更新时，轮换 IAM 凭据。
D. 开发⼀个本地⾃定义身份代理应⽤程序或流程，该应⽤程序或流程使⽤ AWS 安全令牌服务 (AWS STS) 来
获取短期凭证。
Question #762
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司在 AWS 账户中存储了多个 Amazon 系统映像 (AMI)，⽤于启动其 Amazon EC2 实例。这些 AMI 包含
公司运营所必需的关键数据和配置。该公司希望实施⼀种解决⽅案，能够快速⾼效地恢复意外删除的 AMI。
A. 创建 AMI 的 Amazon Elastic Block Store (Amazon EBS) 快照。将快照存储在单独的 AWS 账户中。
B. 定期将所有 AMI 复制到另⼀个 AWS 账户。
C. 在回收站中创建保留规则。
D. 将 AMI 上传到具有跨区域复制功能的 Amazon S3 存储桶。
https://examlearn.online
[2026/05]
Question #763
Topic 1
⼀家公司在本地存储了 150 TB 的归档图像数据，需要在下个⽉内迁移到 AWS 云端。该公司⽬前的⽹络连接仅允
许在夜间以最⾼ 100 Mbps 的速度上传数据。请问，
迁移这些数据并满⾜迁移期限的最经济有效的⽅法是什么？
A. 使⽤ AWS Snowmobile 将数据传输到 AWS。
B. 订购多个 AWS Snowball 设备，将数据传输到 AWS。
C. 启⽤ Amazon S3 传输加速功能并安全上传数据。
D. 创建⼀个 Amazon S3 VPC 终端节点，并建⽴ VPN 以上传数据。
Question #764
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
RDS for MySQL。
Topic 1
⼀家公司希望将其三层应⽤程序从本地迁移到 AWS。Web 层和应⽤层运⾏在第三⽅虚拟机 (VM) 上，数据库层
运⾏在 MySQL 上。
该公司需要在尽可能减少架构更改的情况下完成应⽤程序迁移。此外，该公司还需要⼀个能够将数据恢复到特定
时间点的数据库解决⽅案。
A. 将 Web 层和应⽤层迁移到私有⼦⽹中的 Amazon EC2 实例。将数据库层迁移到私有⼦⽹中的 Amazon
B. 将 Web 层迁移到公有⼦⽹中的 Amazon EC2 实例。将应⽤层迁移到私有⼦⽹中的 EC2 实例。将数据库层
迁移到私有⼦⽹中的 Amazon Aurora MySQL。
C. 将 Web 层迁移到公有⼦⽹中的 Amazon EC2 实例。将应⽤层迁移到私有⼦⽹中的 EC2 实例。将数据库层
迁移到私有⼦⽹中的 Amazon RDS for MySQL。
D. 将 Web 层和应⽤层迁移到公有⼦⽹中的 Amazon EC2 实例。将数据库层迁移到公有⼦⽹中的 Amazon
Aurora MySQL。
https://examlearn.online
[2026/05]
Question #765
Topic 1
⼀个开发团队正在与另⼀家公司合作开发⼀款集成产品。另⼀家公司需要访问开发团队账户中的⼀个 Amazon
Simple Queue Service (Amazon SQS) 队列。另⼀家公司希望轮询该队列，但⼜不想放弃⾃⼰的账户权限。
解决⽅案架构师应该如何提供对 SQS 队列的访问权限？
A. 创建⼀个实例配置⽂件，使另⼀家公司能够访问 SQS 队列。
B. 创建⼀个 IAM 策略，允许另⼀家公司访问 SQS 队列。
C. 创建⼀个 SQS 访问策略，允许另⼀家公司访问 SQS 队列。
D. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 访问策略，允许另⼀家公司访问 SQS 队
列。
Question #766
解决⽅案架构师应该如何以最具成本效益的⽅式满⾜这些需求？
Topic 1
⼀家公司的开发⼈员希望找到⼀种安全的⽅式，通过 SSH 访问公司运⾏最新版 Amazon Linux 的 Amazon EC2
实例。这些开发⼈员既有远程办公的，也有在公司办公室⼯作的。
公司希望使⽤ AWS 服务作为解决⽅案的⼀部分。这些 EC2 实例托管在 VPC 私有⼦⽹中，并通过部署在公有⼦
⽹中的 NAT ⽹关访问互联⽹。
A. 在与 EC2 实例相同的⼦⽹中创建堡垒主机。授予开发⼈员 ec2:CreateVpnConnection IAM 权限。安装
EC2 Instance Connect，以便开发⼈员可以连接到 EC2 实例。
B. 在公司⽹络和 VPC 之间创建 AWS 站点到站点 VPN 连接。指示开发⼈员在公司⽹络内时使⽤此站点到站
点 VPN 连接访问 EC2 实例。指示开发⼈员在远程⼯作时设置另⼀个 VPN 连接进⾏访问。
C. 在虚拟专⽤⽹络 (VP) 的公有⼦⽹中创建堡垒主机。配置堡垒主机的安全组和 SSH 密钥，使其仅允许来⾃
开发⼈员公司⽹络和远程⽹络的连接和 SSH 身份验证。指示开发⼈员使⽤ SSH 通过堡垒主机连接到 EC2 实
例。
D. 将 AmazonSSMManagedInstanceCore IAM 策略附加到与 EC2 实例关联的 IAM ⻆⾊。指示开发⼈员使
⽤ AWS Systems Manager Session Manager 访问 EC2 实例。
https://examlearn.online
[2026/05]
Question #767
Topic 1
⼀家制药公司正在研发⼀种新药。过去⼏个⽉，该公司产⽣的数据量呈指数级增⻓。该公司研究⼈员经常需要⽴
即获取整个数据集的⼀个⼦集，延迟极低。但是，并不需要每天都访问整个数据集。⽬前所有数据都存储在公司
内部的存储阵列中，该公司希望降低持续的资本⽀出。
解决⽅案架构师应该推荐哪种存储解决⽅案来满⾜这些要求？
A. 将 AWS DataSync 作为定时任务运⾏，持续地将数据迁移到 Amazon S3 存储桶。
B. 部署⼀个 AWS Storage Gateway ⽂件⽹关，并将 Amazon S3 存储桶作为⽬标存储。将数据迁移到
Storage Gateway 设备。
C. 部署⼀个带有缓存卷的 AWS Storage Gateway 卷⽹关，并将 Amazon S3 存储桶作为⽬标存储。将数据
迁移到 Storage Gateway 设备。
D. 配置从本地环境到 AWS 的 AWS 站点到站点 VPN 连接。将数据迁移到 Amazon Elastic File System
(Amazon EFS) ⽂件系统。
Question #768
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为表配置时间点恢复。
⼀家公司有⼀个运⾏在 Amazon EC2 实例上的关键业务应⽤程序。该应⽤程序将数据存储在 Amazon
DynamoDB 表中。该公司必须能够将该表恢复到过去 24 ⼩时内的任何时间点。
B. 使⽤ AWS Backup 备份该表。
C. 使⽤ AWS Lambda 函数每⼩时按需备份⼀次表。
Topic 1
D. 启⽤表上的流，以捕获过去 24 ⼩时内对表的所有更改的⽇志。将该流的副本存储在 Amazon S3 存储桶
中。
https://examlearn.online
[2026/05]
Question #769
Topic 1
⼀家公司托管着⼀个⽤于将⽂件上传到 Amazon S3 存储桶的应⽤程序。⽂件上传后，系统会对其进⾏处理以提
取元数据，此过程耗时不到 5 秒。上传的⽂件数量和频率各不相同，从每⼩时⼏个⽂件到数百个并发上传不等。
该公司已委托解决⽅案架构师设计⼀个能够满⾜这些需求的经济⾼效的架构。
解决⽅案架构师应该提出怎样的建议？
A. 配置 AWS CloudTrail 跟踪以记录 S3 API 调⽤。使⽤ AWS AppSync 处理这些⽂件。
B. 在 S3 存储桶中配置对象创建事件通知，以调⽤ AWS Lambda 函数来处理⽂件。
C. 配置 Amazon Kinesis Data Streams 以处理数据并将其发送到 Amazon S3。调⽤ AWS Lambda 函数来
处理⽂件。
D. 配置 Amazon Simple Notification Service (Amazon SNS) 主题以处理上传到 Amazon S3 的⽂件。调⽤
AWS Lambda 函数来处理这些⽂件。
Question #770
Topic 1
⼀家公司的应⽤程序部署在 Amazon EC2 实例上，并使⽤ AWS Lambda 函数实现事件驱动架构。该公司在另⼀
个 AWS 账户中使⽤⾮⽣产开发环境来测试新功能，然后再将其部署到⽣产环境。
由于客户分布在不同的时区，⽣产实例的使⽤率⼀直很⾼。该公司仅在⼯作⽇的营业时间内使⽤⾮⽣产实例，周
末则不使⽤。该公司希望优化其应⽤程序在 AWS 上的运⾏成本。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. ⽣产环境实例使⽤按需实例。⾮⽣产环境实例仅在周末使⽤专⽤主机。
B. ⽣产实例和⾮⽣产实例均使⽤预留实例。不使⽤时，关闭⾮⽣产实例。
C. ⽣产实例使⽤计算节省计划。⾮⽣产实例使⽤按需实例。不使⽤时，关闭⾮⽣产实例。
D. ⽣产实例使⽤专⽤主机。⾮⽣产实例使⽤ EC2 实例节省计划。
https://examlearn.online
[2026/05]
Question #771
⼀家公司将数据存储在本地部署的 Oracle 关系数据库中。该公司需要将数据迁移到 Amazon Aurora
PostgreSQL 中进⾏分析。该公司使⽤ AWS Site-to-Site VPN 连接将其本地⽹络连接到 AWS。
该公司必须捕获迁移到 Aurora PostgreSQL 过程中源数据库发⽣的更改。
哪种解决⽅案能够满⾜这些要求？
Topic 1
A. 使⽤ AWS Schema Conversion Tool (AWS SCT) 将 Oracle 模式转换为 Aurora PostgreSQL 模式。使⽤
AWS Database Migration Service (AWS DMS) 的全负载迁移任务来迁移数据。
B. 使⽤ AWS DataSync 将数据迁移到 Amazon S3 存储桶。使⽤ Aurora PostgreSQL aws_s3 扩展将 S3 数
据导⼊ Aurora PostgreSQL。
C. 使⽤ AWS Schema Conversion Tool (AWS SCT) 将 Oracle 模式转换为 Aurora PostgreSQL 模式。使⽤
AWS Database Migration Service (AWS DMS) 迁移现有数据并复制正在进⾏的更改。
D. 使⽤ AWS Snowball 设备将数据迁移到 Amazon S3 存储桶。使⽤ Aurora PostgreSQL aws_s3 扩展将
S3 数据导⼊ Aurora PostgreSQL。
Question #772
Topic 1
⼀家公司使⽤ Docker 容器构建了⼀个应⽤程序，需要在 AWS 云上运⾏该应⽤程序。该公司希望使⽤托管服务来
托管该应⽤程序。
该解决⽅案必须能够根据各个容器服务的需求进⾏适当的横向扩展和缩减。此外，该解决⽅案不得增加额外的运
维开销或需要管理的基础设施。
哪些解决⽅案能够满⾜这些要求？（选择两个。）
A. 将 Amazon Elastic Container Service (Amazon ECS) 与 AWS Fargate 结合使⽤。
B. 将 Amazon Elastic Kubernetes Service (Amazon EKS) 与 AWS Fargate 结合使⽤。
C. 配置 Amazon API Gateway API。将该 API 连接到 AWS Lambda 以运⾏容器。
D. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 Amazon EC2 ⼯作节点。
E. 将 Amazon Elastic Kubernetes Service (Amazon EKS) 与 Amazon EC2 ⼯作节点⼀起使⽤。
https://examlearn.online
[2026/05]
Question #773
Topic 1
⼀家电商公司正在进⾏季节性线上促销活动。该公司将其⽹站托管在跨多个可⽤区的亚⻢逊 EC2 实例上。该公司
希望其⽹站能够应对促销期间的流量激增。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建⼀个⾜够⼤的⾃动扩展组，以应对⾼峰流量负载。停⽌⼀半的 Amazon EC2 实例。配置⾃动扩展组，
使其在流量增加时使⽤已停⽌的实例进⾏横向扩展。
B. 为⽹站创建⼀个⾃动伸缩组。设置⾃动伸缩组的最⼩规模，使其能够在⽆需横向扩展的情况下处理⾼流
量。
C. 使⽤ Amazon CloudFront 和 Amazon ElastiCache 缓存动态内容，并将 Auto Scaling 组设置为源。配置
Auto Scaling 组，使其包含填充 CloudFront 和 ElastiCache 所需的实例。缓存完全填充后再进⾏缩减。
D. 配置⾃动扩展组，以便在流量增加时进⾏横向扩展。创建启动模板，以便从预配置的 Amazon 系统映像
(AMI) 启动新实例。
Question #774
解决⽅案架构师应该如何做才能以最⼩的运维开销满⾜这些要求？
Topic 1
解决⽅案架构师必须为公司的合规策略提供⾃动化解决⽅案，该策略规定安全组不得包含允许来⾃ 0.0.0.0/0 的
SSH 连接的规则。如果策略遭到任何违反，公司需要收到通知。解决⽅案必须尽快到位。
A. 编写⼀个 AWS Lambda 脚本，监控安全组是否对 0.0.0.0/0 地址开放 SSH 访问权限，并在每次发现此类
访问权限时创建通知。
B. 启⽤受限 SSH AWS Config 托管规则，并在创建不合规规则时⽣成 Amazon Simple Notification Service
(Amazon SNS) 通知。
C. 创建⼀个具有全局开放安全组和⽹络 ACL 权限的 IAM ⻆⾊。创建⼀个 Amazon Simple Notification
Service (Amazon SNS) 主题，以便在⽤户每次承担该⻆⾊时⽣成通知。
D. 配置服务控制策略 (SCP)，防⽌⾮管理员⽤户创建或编辑安全组。当⽤户请求需要管理员权限的规则时，
在⼯单系统中创建通知。
https://examlearn.online
[2026/05]
Question #775
使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 Amazon EC2 ⼯作节点。
Topic 1
⼀家公司已在 AWS 账户中部署了⼀个应⽤程序。该应⽤程序由运⾏在 AWS Lambda 和 Amazon Elastic
Kubernetes Service (Amazon EKS) 上的微服务组成。每个微服务都由⼀个独⽴的团队负责维护。该公司拥有多
个 AWS 账户，并希望为每个团队的微服务分配⼀个独⽴的账户。
解决⽅案架构师需要设计⼀个解决⽅案，以提供通过 HTTPS（端⼝ 443）进⾏服务间通信。该解决⽅案还必须
提供⼀个⽤于服务发现的服务注册中⼼。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 创建⼀个检查 VPC。在检查 VPC 上部署 AWS ⽹络防⽕墙。将检查 VPC 连接到新的传输⽹关。将 VPC 之
间的流量路由到检查 VPC。应⽤防⽕墙规则，仅允许 HTTPS 通信。
B. 创建 VPC Lattice 服务⽹络。将微服务关联到该服务⽹络。为每个服务定义 HTTPS 监听器。将微服务计
算资源注册为⽬标。确定需要与服务通信的 VPC。将这些 VPC 关联到该服务⽹络。
Question #776
C. 为每个微服务创建⼀个⽹络负载均衡器 (NLB)，并配置 HTTPS 监听器和⽬标组。为每个微服务创建⼀个
AWS PrivateLink 终端节点服务。在需要使⽤该微服务的每个 VPC 中创建⼀个接⼝ VPC 终端节点。
D. 在包含微服务的 VPC 之间创建对等连接。为每个需要连接客户端的服务创建前缀列表。创建路由表，将流
量路由到相应的 VPC。创建安全组，仅允许 HTTPS 通信。
Topic 1
⼀家公司开发了⼀款⼿机游戏，该游戏的⼤部分元数据都从 Amazon RDS 数据库实例读取。随着游戏越来越受欢
迎，开发⼈员注意到游戏元数据加载速度变慢。性能指标表明，简单地扩展数据库并不能解决问题。解决⽅案架
构师必须探索所有⽅案，包括快照、复制和亚毫秒级响应时间等功能。
解决⽅案架构师应该推荐什么⽅案来解决这些问题？
A. 使⽤ Aurora Replicas 将数据库迁移到 Amazon Aurora。
B. 将数据库迁移到 Amazon DynamoDB，并使⽤全局表。
C. 在数据库前⾯添加 Amazon ElastiCache for Redis 层。
D. 在数据库前⾯添加 Amazon ElastiCache for Memcached 层。
https://examlearn.online
[2026/05]
Question #777
Topic 1
⼀家公司使⽤ AWS Organizations 构建其多账户 AWS 环境。该公司的安全组织单元 (OU) 需要与开发 OU 共享
已批准的 Amazon 系统映像 (AMI)。这些 AMI 是使⽤ AWS Key Management Service (AWS KMS) 加密快照创
建的。
以下哪个解决⽅案可以满⾜这些要求？（选择两个。）
A. 将开发团队的 OU Amazon 资源名称 (ARN) 添加到 AMI 的启动权限列表中。
B. 将组织根 Amazon 资源名称 (ARN) 添加到 AMI 的启动权限列表中。
C. 更新密钥策略，允许开发团队的 OU 使⽤⽤于解密快照的 AWS KMS 密钥。
D. 将开发团队的账户 Amazon 资源名称 (ARN) 添加到 AMI 的启动权限列表中。
E. 重新创建 AWS KMS 密钥。添加密钥策略，允许 Organizations 的根 Amazon 资源名称 (ARN) 使⽤ AWS
KMS 密钥。
Question #778
Topic 1
⼀家数据分析公司在全球设有 80 个办事处。每个办事处存储 1 PB 的数据，并拥有 1 到 2 Gbps 的互联⽹带宽。
该公司需要将其⼤量数据从各个办事处⼀次性迁移到 Amazon S3。该公司必须在 4 周内完成迁移。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 为每个办公室建⽴新的 10 Gbps AWS Direct Connect 连接。将数据传输到 Amazon S3。
B. 使⽤多个 AWS Snowball Edge 存储优化设备来存储数据并将其传输到 Amazon S3。
C. 使⽤ AWS Snowmobile 将数据存储并传输到 Amazon S3。
D. 设置 AWS Storage Gateway Volume Gateway 将数据传输到 Amazon S3。
https://examlearn.online
[2026/05]
Question #779
Topic 1
⼀家公司拥有⼀个包含参考数据集的 Amazon Elastic File System (Amazon EFS) ⽂件系统。该公司在 Amazon
EC2 实例上运⾏的应⽤程序需要读取该数据集。但是，这些应⽤程序不能修改该数据集。该公司希望使⽤ IAM 访
问控制来阻⽌应⽤程序修改或删除该数据集。
哪种解决⽅案能够满⾜这些要求？
A. 从 EC2 实例内部以只读模式挂载 EFS ⽂件系统。
B. 为 EFS ⽂件系统创建资源策略，禁⽌附加到 EC2 实例的 IAM ⻆⾊执⾏ elasticfilesystem:ClientWrite 操
作。
C. 为 EFS ⽂件系统创建身份策略，拒绝在 EFS ⽂件系统上执⾏ elasticfilesystem:ClientWrite 操作。
D. 为每个应⽤程序创建⼀个 EFS 访问点。使⽤可移植操作系统接⼝ (POSIX) ⽂件权限，允许对根⽬录中的⽂
件进⾏只读访问。
Question #780
哪种解决⽅案能够最安全地满⾜这些要求？
应 IAM 策略。
IAM 策略和权限。
Topic 1
⼀家公司聘请了⼀家外部供应商在其 AWS 账户中执⾏⼯作。该供应商使⽤⼀款⾃动化⼯具，该⼯具托管在其拥
有的 AWS 账户中。该供应商没有访问公司 AWS 账户的 IAM 权限。公司需要授予该供应商访问其 AWS 账户的
权限。
A. 在公司账户中创建⼀个 IAM ⻆⾊，并将访问权限委派给供应商的 IAM ⻆⾊。为该⻆⾊附加供应商所需的相
B. 在公司账户中创建⼀个 IAM ⽤户，并设置符合密码复杂度要求的密码。为该⽤户附加供应商要求的相应
C. 在公司账户中创建⼀个 IAM 组。将供应商账户中⾃动化⼯具的 IAM ⽤户添加到该组。为该组附加供应商所
需的相应 IAM 策略和权限。
D. 在公司账户中创建⼀个 IAM ⽤户，并赋予其允许访问供应商账户的权限范围。为该⽤户附加供应商所需的
相应 IAM 策略。
https://examlearn.online
[2026/05]
Question #781
Topic 1
⼀家公司希望在 AWS 云上运⾏其实验性⼯作负载。该公司有云⽀出预算。公司⾸席财务官 (CFO) 关注各部⻔的
云⽀出责任。CFO 希望在⽀出达到预算的 60% 时收到通知。
哪种解决⽅案能够满⾜这些要求？
A. 在 AWS 资源上使⽤成本分配标签来标记所有者。在 AWS Budgets 中创建使⽤预算。添加警报阈值，以便
在⽀出超过预算的 60% 时收到通知。
B. 使⽤ AWS Cost Explorer 预测来确定资源所有者。使⽤ AWS Cost Anomaly Detection 在⽀出超过预算的
60% 时创建警报阈值通知。
C. 在 AWS 资源上使⽤成本分配标签来标记所有者。使⽤ AWS Trusted Advisor 上的 AWS Support API 创
建警报阈值通知，以便在⽀出超过预算的 60% 时发出通知。
D. 使⽤ AWS Cost Explorer 预测来确定资源所有者。在 AWS Budgets 中创建使⽤预算。添加警报阈值，以
便在⽀出超过预算的 60% 时收到通知。
Question #782
哪种解决⽅案能够满⾜这些要求？
CIDR 块。
Topic 1
⼀家公司希望在 AWS 上部署⼀个内部 Web 应⽤程序。该 Web 应⽤程序只能从公司办公室访问。公司需要从互
联⽹下载该 Web 应⽤程序的安全补丁。
公司已创建了⼀个 VPC，并配置了与公司办公室的 AWS Site-to-Site VPN 连接。解决⽅案架构师必须为该 Web
应⽤程序设计⼀个安全架构。
A. 将 Web 应⽤程序部署在公共⼦⽹的 Amazon EC2 实例上，并置于公共应⽤程序负载均衡器 (ALB) 之后。
将互联⽹⽹关连接到 VPC。将 ALB 安全组的⼊站源设置为 0.0.0.0/0。
B. 将 Web 应⽤程序部署在内部应⽤程序负载均衡器 (ALB) 后⾯的私有⼦⽹中的 Amazon EC2 实例上。在公
有⼦⽹中部署 NAT ⽹关。将互联⽹⽹关连接到 VPC。将 ALB 安全组的⼊站源设置为公司办公⽹络的 CIDR
块。
C. 将 Web 应⽤程序部署在内部应⽤程序负载均衡器 (ALB) 后⾯的公有⼦⽹中的 Amazon EC2 实例上。在私
有⼦⽹中部署 NAT ⽹关。将互联⽹⽹关连接到 VPSet。将 ALB 安全组的出站⽬标设置为公司办公⽹络的
D. 将 Web 应⽤程序部署在公共应⽤程序负载均衡器 (ALB) 后⾯的私有⼦⽹中的 Amazon EC2 实例上。将互
联⽹⽹关连接到 VPC。将 ALB 安全组的出站⽬标设置为 0.0.0.0/0。
https://examlearn.online
[2026/05]
Question #783
Topic 1
⼀家公司使⽤运⾏在 Amazon EC2 实例上的⾃定义应⽤程序来维护其会计记录。该公司需要将数据迁移到 AWS
托管服务，以便进⾏应⽤程序数据的开发和维护。该解决⽅案必须尽可能减少运维⽀持，并提供不可篡改、可加
密验证的数据变更⽇志。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将应⽤程序中的记录复制到 Amazon Redshift 集群中。
B. 将应⽤程序中的记录复制到 Amazon Neptune 集群中。
C. 将应⽤程序中的记录复制到 Amazon Timestream 数据库中。
D. 将应⽤程序中的记录复制到 Amazon Quantum Ledger Database (Amazon QLDB) 账本中。
Question #784
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司的市场营销数据从多个来源上传到 Amazon S3 存储桶。⼀系列数据准备作业会将数据汇总以⽣成报
告。这些数据准备作业需要定期并⾏运⾏。之后，部分作业需要按特定顺序运⾏。
该公司希望消除作业错误处理、重试逻辑和状态管理带来的运维开销。
A. 使⽤ AWS Lambda 函数在数据上传到 S3 存储桶后⽴即处理数据。定期调⽤其他 Lambda 函数。
B. 使⽤ Amazon Athena 处理数据。使⽤ Amazon EventBridge Scheduler 定期在内部调⽤ Athena。
C. 使⽤ AWS Glue DataBrew 处理数据。使⽤ AWS Step Functions 状态机运⾏ DataBrew 数据准备作业。
D. 使⽤ AWS Data Pipeline 处理数据。安排 Data Pipeline 在午夜处理⼀次数据。
https://examlearn.online
[2026/05]
Question #785
Topic 1
⼀位解决⽅案架构师正在设计⼀个⽀付处理应⽤程序，该应⽤程序运⾏在跨多个可⽤区的私有⼦⽹中的 AWS
Lambda 上。该应⽤程序使⽤多个 Lambda 函数，每天处理数百万笔交易。
架构必须确保应⽤程序不会处理重复付款。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Lambda 函数检索所有到期款项。将到期款项发布到 Amazon S3 存储桶。配置 S3 存储桶，使其触
发事件通知，以便调⽤另⼀个 Lambda 函数来处理到期款项。
B. 使⽤ Lambda 函数检索所有到期款项。将到期款项发布到 Amazon Simple Queue Service (Amazon
SQS) 队列。配置另⼀个 Lambda 函数来轮询 SQS 队列并处理到期款项。
C. 使⽤ Lambda 函数检索所有到期款项。将到期款项发布到 Amazon Simple Queue Service (Amazon
SQS) 先进先出 (FIFO) 队列。配置另⼀个 Lambda 函数来轮询 FIFO 队列并处理到期款项。
D. 使⽤ Lambda 函数检索所有到期款项。将到期款项存储在 Amazon DynamoDB 表中。配置 DynamoDB
表上的流，以调⽤另⼀个 Lambda 函数来处理到期款项。
Question #786
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在其本地数据中⼼运⾏多个⼯作负载。该公司的数据中⼼⽆法快速扩展以满⾜其不断增⻓的业务需求。
该公司希望收集有关本地服务器和⼯作负载的使⽤情况和配置数据，以便规划向 AWS 的迁移。
A. 在 AWS Migration Hub 中设置 AWS 主区域。使⽤ AWS Systems Manager 收集有关本地服务器的数
据。
B. 在 AWS Migration Hub 中设置 AWS 主区域。使⽤ AWS Application Discovery Service 收集有关本地服
务器的数据。
C. 使⽤ AWS Schema Conversion Tool (AWS SCT) 创建相关模板。使⽤ AWS Trusted Advisor 收集有关本
地服务器的数据。
D. 使⽤ AWS Schema Conversion Tool (AWS SCT) 创建相关模板。使⽤ AWS Database Migration Service
(AWS DMS) 收集有关本地服务器的数据。
https://examlearn.online
[2026/05]
Question #787
Topic 1
⼀家公司在 AWS Organizations 中拥有⼀个启⽤了所有功能的组织。该公司要求对所有现有或新增 AWS 账户中
的所有 API 调⽤和登录进⾏审计。该公司需要⼀个托管解决⽅案来避免额外的⼯作并最⼤限度地降低成本。此
外，该公司还需要了解何时有任何 AWS 账户不符合 AWS 基础安全最佳实践 (FSBP) 标准。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 在 Organizations 管理账户中部署 AWS Control Tower 环境。在该环境中启⽤ AWS Security Hub 和
AWS Control Tower Account Factory。
B. 在专⽤的组织成员账户中部署 AWS Control Tower 环境。在该环境中启⽤ AWS Security Hub 和 AWS
Control Tower Account Factory。
C. 使⽤ AWS 托管服务 (AMS) Accelerate 构建多账户着陆区 (MALZ)。提交 RFC 以在 MALZ 中⾃助配置
Amazon GuardDuty。
D. 使⽤ AWS 托管服务 (AMS) Accelerate 构建多账户着陆区 (MALZ)。提交 RFC 以在 MALZ 中⾃助配置
AWS Security Hub。
Question #788
Topic 1
⼀家公司在 Amazon S3 存储桶中以 Apache Parquet 格式存储了 10 TB 的⽇志⽂件。该公司偶尔需要使⽤ SQL
分析这些⽇志⽂件。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建⼀个 Amazon Aurora MySQL 数据库。使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据从 S3 存储桶
迁移到 Aurora。向 Aurora 数据库发出 SQL 语句。
B. 创建⼀个 Amazon Redshift 集群。使⽤ Redshift Spectrum 直接对 S3 存储桶中的数据运⾏ SQL 语句。
C. 创建⼀个 AWS Glue 爬⾍程序，⽤于存储和检索 S3 存储桶中的表元数据。使⽤ Amazon Athena 直接对
S3 存储桶中的数据运⾏ SQL 语句。
D. 创建⼀个 Amazon EMR 集群。使⽤ Apache Spark SQL 直接对 S3 存储桶中的数据运⾏ SQL 语句。
https://examlearn.online
[2026/05]
Question #789
Topic 1
⼀家公司需要⼀个解决⽅案，以防⽌ AWS CloudFormation 堆栈部署包含内联策略或语句中包含“*”的 AWS
Identity and Access Management (IAM) 资源。该解决⽅案还必须禁⽌部署具有公有 IP 地址的 Amazon EC2 实
例。该公司已在其 AWS Organizations 组织中启⽤了 AWS Control Tower。
哪个解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Control Tower 主动控制来阻⽌部署具有公共 IP 地址的 EC2 实例，并使⽤具有提升访问权限或
“*”的内联策略。
B. 使⽤ AWS Control Tower 检测控制来阻⽌部署具有公共 IP 地址的 EC2 实例，并使⽤具有提升访问权限或
“*”的内联策略。
C. 使⽤ AWS Config 创建 EC2 和 IAM 合规性规则。配置这些规则，以便在资源不符合合规性要求时运⾏
AWS Systems Manager Session Manager ⾃动化流程将其删除。
D. 如果操作导致不合规，则使⽤服务控制策略 (SCP) 阻⽌对 EC2 实例和 IAM 资源的操作。
Question #790
以下哪两项措施可以满⾜这些要求？
Topic 1
⼀家公司托管在 AWS 云上的 Web 应⽤程序最近访问量激增。该 Web 应⽤程序⽬前运⾏在单个公有⼦⽹中的单
个 Amazon EC2 实例上。由于 Web 流量持续增⻓，该应⽤程序已⽆法满⾜需求。
该公司需要⼀个解决⽅案，能够在不重写 Web 应⽤程序的情况下，提供⾼可⽤性和可扩展性以满⾜不断增⻓的⽤
户需求。
A. 将 EC2 实例替换为计算能⼒更强的优化型实例。
B. 在私有⼦⽹中配置多个可⽤区，实现 Amazon EC2 ⾃动扩展。
C. 在公共⼦⽹中配置 NAT ⽹关以处理 Web 请求。
D. 将 EC2 实例替换为内存更⼤的优化型实例。
E. 在公共⼦⽹中配置应⽤程序负载均衡器以分配 Web 流量。
https://examlearn.online
[2026/05]
Question #791
⼀家公司拥有使⽤环境变量的 AWS Lambda 函数。该公司不希望开发⼈员以明⽂形式查看环境变量。
哪种解决⽅案能够满⾜这些要求？
A. 将代码部署到 Amazon EC2 实例，⽽不是使⽤ Lambda 函数。
B. 在 Lambda 函数上配置 SSL 加密，以使⽤ AWS CloudHSM 存储和加密环境变量。
C. 在 AWS Certificate Manager (ACM) 中创建证书。配置 Lambda 函数以使⽤该证书加密环境变量。
Topic 1
D. 创建 AWS Key Management Service (AWS KMS) 密钥。在 Lambda 函数上启⽤加密助⼿，以使⽤ KMS
密钥存储和加密环境变量。
Question #792
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
REST API。
Topic 1
⼀家分析公司使⽤ Amazon VPC 运⾏其多层服务。该公司希望使⽤ RESTful API 向数百万⽤户提供 Web 分析服
务。⽤户必须通过身份验证服务才能访问 API。
A. 配置 Amazon Cognito ⽤户池以进⾏⽤户身份验证。使⽤ Cognito 授权器实现 Amazon API Gateway
B. 配置⽤于⽤户身份验证的 Amazon Cognito 身份池。使⽤ Cognito 授权器实现 Amazon API Gateway
HTTP API。
C. 配置 AWS Lambda 函数来处理⽤户身份验证。使⽤ Lambda 授权器实现 Amazon API Gateway REST
API。
D. 配置 IAM ⽤户以处理⽤户身份验证。使⽤ IAM 授权器实现 Amazon API Gateway HTTP API。
https://examlearn.online
[2026/05]
Question #793
⼀家公司拥有⼀款⾯向客户的移动应⽤。该应⽤的数据⾮常敏感，必须进⾏静态加密。该公司使⽤ AWS Key
Management Service (AWS KMS)。
该公司需要⼀个解决⽅案来防⽌ KMS 密钥被意外删除。该解决⽅案必须使⽤ Amazon Simple Notification
Service (Amazon SNS) 在⽤户尝试删除 KMS 密钥时向管理员发送电⼦邮件通知。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 创建⼀个 Amazon EventBridge 规则，当⽤户尝试删除 KMS 密钥时触发该规则。配置⼀个 AWS Config
规则，取消任何 KMS 密钥的删除操作。将该 AWS Config 规则添加为 EventBridge 规则的⽬标。创建⼀个
SNS 主题，⽤于通知管理员。
Topic 1
B. 创建⼀个包含⾃定义逻辑的 AWS Lambda 函数，以防⽌ KMS 密钥被删除。创建⼀个 Amazon
CloudWatch 警报，当⽤户尝试删除 KMS 密钥时触发该警报。创建⼀个 Amazon EventBridge 规则，当执⾏
DeleteKey 操作时调⽤ Lambda 函数。创建⼀个 SNS 主题。配置 EventBridge 规则，使其发布 SNS 消息以
通知管理员。
C. 创建⼀个 Amazon EventBridge 规则，使其在执⾏ KMS DeleteKey 操作时做出响应。配置该规则以启动
⼀个 AWS Systems Manager Automation 运⾏⼿册。配置该运⾏⼿册以取消 KMS 密钥的删除操作。创建⼀
个 SNS 主题。配置 EventBridge 规则以发布⼀条 SNS 消息来通知管理员。
D. 创建 AWS CloudTrail 跟踪。配置该跟踪，使其将⽇志发送到新的 Amazon CloudWatch ⽇志组。基于
CloudWatch ⽇志组的指标筛选器创建 CloudWatch 警报。配置该警报，使其使⽤ Amazon SNS 在执⾏
KMS DeleteKey 操作时通知管理员。
https://examlearn.online
[2026/05]
Question #794
Topic 1
⼀家公司希望分析并⽣成报告，以追踪其移动应⽤的使⽤情况。该应⽤⼴受欢迎，拥有全球⽤户群。该公司使⽤
⼀款⾃定义报告⽣成程序来分析应⽤使⽤情况。
该程序会在每⽉最后⼀周⽣成多份报告，每份报告的⽣成时间不到 10 分钟。该公司很少在每⽉最后⼀周之外使⽤
该程序⽣成报告。该公司希望在需要报告时，能够以最短的时间⽣成报告。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ Amazon EC2 按需实例运⾏程序。创建⼀条 Amazon EventBridge 规则，以便在请求报告时启动
EC2 实例。在每个⽉的最后⼀周持续运⾏ EC2 实例。
B. 在 AWS Lambda 中运⾏程序。创建⼀个 Amazon EventBridge 规则，以便在请求报告时运⾏ Lambda 函
数。
C. 在 Amazon Elastic Container Service (Amazon ECS) 中运⾏程序。安排 Amazon ECS 在请求报告时运
⾏程序。
D. 使⽤ Amazon EC2 Spot 实例运⾏程序。创建 Amazon Event Builder 规则，以便在请求报告时启动 EC2
实例。在每个⽉的最后⼀周持续运⾏ EC2 实例。
Question #795
Topic 1
⼀家公司正在AWS云上设计⼀个紧耦合的⾼性能计算（HPC）环境。该公司需要包含⼀些功能，以优化HPC环境
的⽹络和存储性能。
以下哪两项解决⽅案组合能够满⾜这些要求？（选择两项。）
A. 在 AWS Global Accelerator 中创建⼀个加速器。为该加速器配置⾃定义路由。
B. 创建⼀个⽤于 Lustre ⽂件系统的 Amazon FSx。配置⽂件系统，使其具有临时存储。
C. 创建 Amazon CloudFront 分发。将查看器协议策略配置为 HTTP 和 HTTPS。
D. 启动 Amazon EC2 实例。将弹性⽹络适配器 (EFA) 附加到这些实例。
E. 创建 AWS Elastic Beanstalk 部署来管理环境。
https://examlearn.online
[2026/05]
Question #796
Topic 1
⼀家公司需要⼀种解决⽅案，以防⽌包含不良内容的照⽚被上传到公司的⽹站应⽤程序。该解决⽅案不能涉及训
练机器学习（ML）模型。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon SageMaker Autopilot 创建并部署模型。创建⼀个实时端点，当有新照⽚上传时，Web 应⽤
程序会调⽤该端点。
B. 创建⼀个使⽤ Amazon Rekognition 检测不良内容的 AWS Lambda 函数。创建⼀个 Lambda 函数 URL，
当上传新照⽚时，Web 应⽤程序会调⽤该 URL。
C. 创建⼀个使⽤ Amazon Comprehend 检测不良内容的 Amazon CloudFront 函数。将该函数与 Web 应⽤
程序关联。
D. 创建⼀个使⽤ Amazon Rekognition Video 检测不良内容的 AWS Lambda 函数。创建⼀个 Lambda 函数
URL，当上传新照⽚时，Web 应⽤程序会调⽤该 URL。
Question #797
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司使⽤ AWS 运⾏其电⼦商务平台。该平台对公司的运营⾄关重要，且流量和交易量巨⼤。该公司配置了
多因素身份验证 (MFA) 设备来保护其 AWS 账户根⽤户凭证。该公司希望确保即使 MFA 设备丢失，也不会失去
对根⽤户账户的访问权限。
A. 设置⼀个备⽤管理员帐户，以便在公司丢失 MFA 设备时公司可以使⽤该帐户登录。
B. 为 root ⽤户帐户添加多个 MFA 设备以应对灾难情况。
C. 当公司⽆法访问根帐户时，创建⼀个新的管理员帐户。
D. 当公司⽆法访问根帐户时，将管理员策略附加到另⼀个 IAM ⽤户。
https://examlearn.online
[2026/05]
Question #798
⼀家社交媒体公司正在为其⽤户创建⼀个奖励计划⽹站。⽤户在⽹站上创建并上传视频时，公司会奖励⽤户积
分。⽤户可以使⽤积分兑换公司合作商提供的礼品或折扣。每个⽤户都有⼀个唯⼀的ID。合作商会通过此ID来验
证⽤户是否符合奖励资格。
当公司向⽤户发放积分时，合作商希望通过HTTP端点接收⽤户ID的通知。每天都有数百家供应商表示有兴趣成为
合作商。公司希望设计⼀种架构，使⽹站能够以可扩展的⽅式快速添加合作伙伴。
哪种解决⽅案能够以最⼩的实施⼯作量满⾜这些要求？
Topic 1
A. 创建⼀个 Amazon Timestream 数据库来保存合作伙伴列表。实现⼀个 AWS Lambda 函数来读取该列
表。配置该 Lambda 函数，使其在公司向⽤户发放积分时，将⽤户 ID 发送给每个合作伙伴。
B. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。选择⼀个终端节点协议。让合作伙
伴订阅该主题。当公司向⽤户发放积分时，将⽤户 ID 发布到该主题。
C. 创建⼀个 AWS Step Functions 状态机。为每个合作伙伴创建⼀个任务。当公司向⽤户发放积分时，使⽤
⽤户 ID 作为输⼊调⽤该状态机。
D. 在 Amazon Kinesis Data Streams 中创建数据流。实现⽣产者和消费者应⽤程序。将合作伙伴列表存储在
数据流中。当公司向⽤户发放积分时，发送⽤户 ID。
https://examlearn.online
[2026/05]
Question #799
Topic 1
⼀家公司需要从存储在 Amazon S3 存储桶中的⽂本⽂件格式的⻝谱记录中提取⻝材名称。⼀个 Web 应⽤程序将
使⽤这些⻝材名称查询 Amazon DynamoDB 表，并计算营养评分。
该应⽤程序可以处理⾮⻝品记录和错误。该公司没有具备机器学习知识的员⼯来开发此解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ S3 事件通知在发⽣ PutObject 请求时调⽤ AWS Lambda 函数。编写 Lambda 函数，使其使⽤
Amazon Comprehend 分析对象并提取成分名称。将 Amazon Comprehend 的输出存储在 DynamoDB 表
中。
B. 使⽤ Amazon EventBridge 规则在发⽣ PutObject 请求时调⽤ AWS Lambda 函数。编写 Lambda 函数，
使其使⽤ Amazon Forecast 分析对象并提取成分名称。将 Forecast 的输出存储在 DynamoDB 表中。
C. 使⽤ S3 事件通知在发⽣ PutObject 请求时调⽤ AWS Lambda 函数。使⽤ Amazon Polly 创建⻝谱记录的
⾳频录⾳。将⾳频⽂件保存到 S3 存储桶中。使⽤ Amazon Simple Notification Service (Amazon SNS) 将
URL 作为消息发送给员⼯。指示员⼯收听⾳频⽂件并计算营养评分。将配料名称存储在 DynamoDB 表中。
D. 使⽤ Amazon EventBridge 规则在发⽣ PutObject 请求时调⽤ AWS Lambda 函数。对 Lambda 函数进⾏
编程，使其使⽤ Amazon SageMaker 分析对象并提取成分名称。将 SageMaker 端点的推理输出存储在
DynamoDB 表中。
Question #800
Topic 1
⼀家公司需要在其主 AWS 账户的 VPC 中创建⼀个 AWS Lambda 函数。该 Lambda 函数需要访问公司存储在
Amazon Elastic File System (Amazon EFS) ⽂件系统中的⽂件。EFS ⽂件系统位于另⼀个 AWS 账户中。随着
公司向⽂件系统中添加⽂件，该解决⽅案必须能够扩展以满⾜需求。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在主账户中创建⼀个新的 EFS ⽂件系统。使⽤ AWS DataSync 将原始 EFS ⽂件系统的内容复制到新的
EFS ⽂件系统。
B. 在主账户和辅助账户中的 VPC 之间创建 VPC 对等连接。
C. 在辅助账户中创建第⼆个 Lambda 函数，该函数具有已配置⽂件系统的挂载点。使⽤主账户的 Lambda 函
数来调⽤辅助账户的 Lambda 函数。
D. 将⽂件系统的内容移动到 Lambda 层。配置 Lambda 层的权限，允许公司的辅助帐户使⽤ Lambda 层。
https://examlearn.online
[2026/05]
Question #801
Topic 1
⼀家⾦融公司需要处理⾼度敏感的数据。该公司将数据存储在 Amazon S3 存储桶中。该公司需要确保数据在传
输和存储过程中都经过加密。该公司必须在 AWS 云之外管理加密密钥。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥，通过服务器端加密 (SSE) 对 S3 存储
桶中的数据进⾏加密。
B. 使⽤ AWS Key Management Service (AWS KMS) AWS 托管密钥的服务器端加密 (SSE) 对 S3 存储桶中
的数据进⾏加密。
C. 使⽤默认的服务器端加密 (SSE) 对 S3 存储桶中的数据进⾏加密。
D. 在将数据存储到 S3 存储桶之前，先在公司数据中⼼对数据进⾏加密。
Question #802
后端处理应⽤程序运⾏时间较⻓，需要调整计算和内存资源。该公司不希望管理基础设施。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司希望在 AWS 上运⾏其⽀付应⽤程序。该应⽤程序接收来⾃移动设备的⽀付通知。⽀付通知在发送进⾏
进⼀步处理之前需要进⾏基本验证。
A. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。将该队列与 Amazon EventBridge 规则
集成，以接收来⾃移动设备的付款通知。配置该规则以验证付款通知并将通知发送到后端应⽤程序。将后端应
⽤程序部署到 Amazon Elastic Kubernetes Service (Amazon EKS) Anywhere 上。创建⼀个独⽴集群。
B. 创建 Amazon API Gateway API。将该 API 与 AWS Step Functions 状态机集成，以接收来⾃移动设备的
⽀付通知。调⽤该状态机验证⽀付通知，并将通知发送到后端应⽤程序。将后端应⽤程序部署到 Amazon
Elastic Kubernetes Service (Amazon EKS)。配置包含⾃管理节点的 EKS 集群。
C. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。将该队列与 Amazon EventBridge 规则
集成，以接收来⾃移动设备的付款通知。配置该规则以验证付款通知并将通知发送到后端应⽤程序。将后端应
⽤程序部署在 Amazon EC2 Spot 实例上。配置⼀个使⽤默认分配策略的 Spot 实例组。
D. 创建 Amazon API Gateway API。将该 API 与 AWS Lambda 集成，以接收来⾃移动设备的⽀付通知。调
⽤ Lambda 函数来验证⽀付通知，并将通知发送到后端应⽤程序。将后端应⽤程序部署到 Amazon Elastic
Container Service (Amazon ECS)。将 Amazon ECS 配置为 AWS Fargate 启动类型。
https://examlearn.online
[2026/05]
Question #803
Topic 1
⼀位解决⽅案架构师正在为⼀家公司设计⽤户身份验证解决⽅案。该解决⽅案必须为从不同地理位置、IP 地址或
设备登录的⽤户启⽤双因素身份验证。此外，该解决⽅案还必须能够扩展以⽀持数百万⽤户。
哪种解决⽅案能够满⾜这些要求？
A. 配置 Amazon Cognito ⽤户池以进⾏⽤户身份验证。启⽤基于⻛险的⾃适应身份验证功能以及多因素身份
验证 (MFA)。
B. 配置 Amazon Cognito 身份池以进⾏⽤户身份验证。启⽤多因素身份验证 (MFA)。
C. 配置 AWS Identity and Access Management (IAM) ⽤户以进⾏⽤户身份验证。附加允许
AllowManageOwnUserMFA 操作的 IAM 策略。
D. 配置 AWS IAM 身份中⼼（AWS 单点登录）身份验证以进⾏⽤户身份验证。配置权限集以要求进⾏多因素
身份验证 (MFA)。
Question #804
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司拥有⼀个 Amazon S3 数据湖。该公司需要⼀个解决⽅案，能够每天将数据湖中的数据转换并加载到数
据仓库中。该数据仓库必须具备⼤规模并⾏处理 (MPP) 能⼒。
之后，数据分析师需要使⽤ SQL 命令对数据进⾏处理，从⽽创建和训练机器学习 (ML) 模型。该解决⽅案必须尽
可能使⽤ AWS ⽆服务器服务。
A. 每⽇运⾏ Amazon EMR 作业，转换数据并将其加载到 Amazon Redshift 中。使⽤ Amazon Redshift ML
创建和训练机器学习模型。
B. 每⽇运⾏ Amazon EMR 作业，转换数据并将其加载到 Amazon Aurora Serverless 中。使⽤ Amazon
Aurora ML 创建和训练机器学习模型。
C. 每⽇运⾏ AWS Glue 作业，转换数据并将其加载到 Amazon Redshift Serverless 中。使⽤ Amazon
Redshift ML 创建和训练机器学习模型。
D. 每⽇运⾏ AWS Glue 作业，转换数据并将其加载到 Amazon Athena 表中。使⽤ Amazon Athena ML 创建
和训练机器学习模型。
https://examlearn.online
[2026/05]
Question #805
Topic 1
⼀家公司在其本地数据中⼼的 Kubernetes 环境中运⾏容器。该公司希望使⽤ Amazon Elastic Kubernetes
Service (Amazon EKS) 和其他 AWS 托管服务。为了符合合规性要求，数据必须保留在公司数据中⼼内，不能存
储在任何远程站点或云端。
哪种解决⽅案能够满⾜这些要求？
A. 在公司数据中⼼部署 AWS 本地区域。
B. 在公司数据中⼼使⽤ AWS Snowmobile。
C. 在公司数据中⼼安装 AWS Outposts 机架。
D. 在数据中⼼安装 AWS Snowball Edge Storage 优化节点。
Question #806
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家社交媒体公司拥有⽤于收集和处理数据的⼯作负载。这些⼯作负载将数据存储在本地 NFS 存储中。该数据存
储的扩展速度⽆法满⾜公司不断增⻓的业务需求。该公司希望将当前的数据存储迁移到 AWS。
A. 设置 AWS Storage Gateway 卷⽹关。使⽤ Amazon S3 ⽣命周期策略将数据转换到相应的存储类别。
B. 设置 AWS Storage Gateway 和 Amazon S3 File Gateway。使⽤ Amazon S3 ⽣命周期策略将数据转换到
相应的存储类别。
C. 使⽤ Amazon Elastic File System (Amazon EFS) 标准-不频繁访问 (Standard-IA) 存储类。激活不频繁访
问⽣命周期策略。
D. 使⽤ Amazon Elastic File System (Amazon EFS) 单区域低频访问 (One Zone-IA) 存储类。激活低频访问
⽣命周期策略。
https://examlearn.online
[2026/05]
Question #807
Topic 1
⼀家公司在营销活动期间使⽤⾼并发 AWS Lambda 函数来处理消息队列中不断增⻓的消息数量。这些 Lambda
函数使⽤ CPU 密集型代码来处理消息。该公司希望降低计算成本并保持客户的服务延迟。
哪种解决⽅案能够满⾜这些要求？
A. 为 Lambda 函数配置保留并发性。减少分配给 Lambda 函数的内存。
B. 为 Lambda 函数配置预留并发数。根据 AWS Compute Optimizer 的建议增加内存。
C. 配置 Lambda 函数的预置并发性。减少分配给 Lambda 函数的内存。
D. 配置 Lambda 函数的预置并发性。根据 AWS Compute Optimizer 的建议增加内存。
Question #808
哪种解决⽅案能够在对⼯作负载进⾏最少更改的情况下满⾜这些要求？
Topic 1
⼀家公司在 Amazon Elastic Container Service (Amazon ECS) 上运⾏其⼯作负载。ECS 任务定义使⽤的容器镜
像需要进⾏常⻅漏洞和披露 (CVE) 扫描。新创建的容器镜像也需要进⾏扫描。
A. 使⽤ Amazon Elastic Container Registry (Amazon ECR) 作为私有镜像仓库来存储容器镜像。为 ECR 基
本扫描指定推送时扫描过滤器。
B. 将容器镜像存储在 Amazon S3 存储桶中。使⽤ Amazon Macie 扫描镜像。使⽤ S3 事件通知，针对每个
s3:ObjectCreated:Put 事件类型触发 Macie 扫描。
C. 将⼯作负载部署到 Amazon Elastic Kubernetes Service (Amazon EKS)。使⽤ Amazon Elastic
Container Registry (Amazon ECR) 作为私有镜像仓库。为 ECR 增强扫描指定推送时扫描过滤器。
D. 将容器镜像存储在已启⽤版本控制的 Amazon S3 存储桶中。配置 S3 事件通知，针对
s3:ObjectCreated:* 事件调⽤ AWS Lambda 函数。配置 Lambda 函数以启动 Amazon Inspector 扫描。
https://examlearn.online
[2026/05]
Question #809
Topic 1
⼀家公司使⽤ AWS Batch 作业来运⾏其每⽇销售结算流程。该公司需要⼀个⽆服务器解决⽅案，以便在 AWS
Batch 作业成功完成后调⽤第三⽅报表应⽤程序。该报表应⽤程序具有使⽤⽤户名和密码进⾏身份验证的 HTTP
API 接⼝。
哪种解决⽅案能够满⾜这些要求？
A. 配置 Amazon EventBridge 规则以匹配传⼊的 AWS Batch 作业成功事件。将第三⽅ API 配置为
EventBridge API ⽬标，并设置⽤户名和密码。将该 API ⽬标设置为 EventBridge 规则的⽬标。
B. 配置 Amazon EventBridge Scheduler 以匹配传⼊的 AWS Batch 作业成功事件。配置⼀个 AWS Lambda
函数，使⽤⽤户名和密码调⽤第三⽅ API。将该 Lambda 函数设置为 EventBridge 规则⽬标。
C. 配置 AWS Batch 作业，将作业成功事件发布到 Amazon API Gateway REST API。在 API Gateway REST
API 上配置 HTTP 代理集成，以使⽤⽤户名和密码调⽤第三⽅ API。
D. 配置 AWS Batch 作业，将作业成功事件发布到 Amazon API Gateway REST API。配置 API Gateway
REST API 到 AWS Lambda 函数的代理集成。配置 Lambda 函数，使其使⽤⽤户名和密码调⽤第三⽅ API。
Question #810
哪种解决⽅案可以满⾜此需求？
应商 VPC。
Topic 1
⼀家公司从供应商处收集并处理数据。供应商将其数据存储在其⾃身 AWS 账户中的 Amazon RDS for MySQL 数
据库中。该公司的 VPC 没有互联⽹⽹关、AWS Direct Connect 连接或 AWS Site-to-Site VPN 连接。该公司需
要访问供应商数据库中的数据。
A. 指示供应商注册 AWS Hosted Connection Direct Connect 计划。使⽤ VPC 对等互连连接公司 VPC 和供
B. 在公司 VPC 和供应商 VPC 之间配置客户端 VPN 连接。使⽤ VPC 对等连接将公司 VPC 和供应商 VPC 连
接起来。
C. 指示供应商创建⽹络负载均衡器 (NLB)。将 NLB 置于 Amazon RDS for MySQL 数据库的前端。使⽤
AWS PrivateLink 将公司的 VPC 和供应商的 VPC 集成在⼀起。
D. 使⽤ AWS Transit Gateway 集成公司 VPC 和供应商 VPC。使⽤ VPC 对等互连连接公司 VPC 和供应商
VPC。
https://examlearn.online
[2026/05]
Question #811
Topic 1
⼀家公司希望将 Amazon Managed Grafana 设置为其可视化⼯具。该公司希望将 Amazon RDS 数据库中的数据
作为单⼀数据源进⾏可视化。该公司需要⼀个安全的解决⽅案，不会将数据暴露在互联⽹上。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个不包含 VPC 的 Amazon Managed Grafana ⼯作区。为 RDS 数据库创建⼀个公共终端节点。将
该公共终端节点配置为 Amazon Managed Grafana 中的数据源。
B. 在 VPC 中创建⼀个 Amazon Managed Grafana ⼯作区。为 RDS 数据库创建⼀个私有终端节点。将该私
有终端节点配置为 Amazon Managed Grafana 中的数据源。
C. 创建⼀个没有虚拟专⽤服务器 (VP) 的 Amazon Managed Grafana ⼯作区。创建⼀个 AWS PrivateLink 端
点，以建⽴ Amazon Managed Grafana 和 Amazon RDS 之间的连接。将 Amazon RDS 设置为 Amazon
Managed Grafana 中的数据源。
D. 在 VPC 中创建⼀个 Amazon Managed Grafana ⼯作区。为 RDS 数据库创建⼀个公共终端节点。将该公
共终端节点配置为 Amazon Managed Grafana 中的数据源。
Question #812
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 Amazon S3 上托管了⼀个数据湖。该数据湖以 Apache Parquet 格式从各种数据源摄取数据。该公
司使⽤多个转换步骤来准备摄取的数据。这些步骤包括异常值过滤、将数据规范化为标准⽇期和时间值，以及⽣
成⽤于分析的聚合数据。
该公司必须将转换后的数据存储在数据分析师可以访问的 S3 存储桶中。该公司需要⼀个⽆需编写代码的预构建
数据转换解决⽅案。该解决⽅案必须提供数据沿袭和数据分析功能。该公司需要与公司所有员⼯共享数据转换步
骤。
A. 配置 AWS Glue Studio 可视化画布以转换数据。使⽤ AWS Glue 作业与员⼯共享转换步骤。
B. 配置 Amazon EMR Serverless 以转换数据。使⽤ EMR Serverless 作业与员⼯共享转换步骤。
C. 配置 AWS Glue DataBrew 以转换数据。使⽤ DataBrew 配⽅与员⼯共享转换步骤。
D. 创建⽤于存储数据的 Amazon Athena 表。编写 Athena SQL 查询语句来转换数据。与员⼯共享 Athena
SQL 查询语句。
https://examlearn.online
[2026/05]
Question #813
Topic 1
解决⽅案架构师在应⽤程序负载均衡器 (ALB) 后⽅的多个 Amazon EC2 实例上运⾏ Web 应⽤程序，这些实例位
于不同的⽬标组中。⽤户可以通过公共⽹站访问该应⽤程序。
解决⽅案架构师希望允许⼯程师使⽤⽹站的开发版本访问⼀个特定的开发 EC2 实例，以测试应⽤程序的新功能。
解决⽅案架构师希望使⽤ Amazon Route 53 托管区域为⼯程师提供对该开发实例的访问权限。即使开发实例被
替换，解决⽅案也必须能够⾃动路由到该开发实例。
哪个解决⽅案能够满⾜这些要求？
A. 为开发⽹站创建⼀个 A 记录，其值设置为 ALB。在 ALB 上创建⼀个监听器规则，将对开发⽹站的请求转
发到包含开发实例的⽬标组。
B. 使⽤公⽹ IP 地址重新创建开发实例。为开发⽹站创建⼀个 A 记录，并将值设置为开发实例的公⽹ IP 地
址。
C. 为开发⽹站创建⼀个 A 记录，并将值设置为 ALB。在 ALB 上创建⼀个监听器规则，将对开发⽹站的请求
重定向到开发实例的公共 IP 地址。
D. 将所有实例放在同⼀个⽬标组中。为开发⽹站创建⼀个 A 记录，并将值设置为 ALB。在 ALB 上创建⼀个
监听器规则，将对开发⽹站的请求转发到⽬标组。
Question #814
Topic 1
⼀家公司在其数据中⼼的 Kubernetes 集群上运⾏⼀个容器应⽤程序。该应⽤程序使⽤⾼级消息队列协议
(AMQP) 与消息队列通信。由于数据中⼼的扩展速度⽆法满⾜公司不断增⻓的业务需求，因此该公司希望将⼯作
负载迁移到 AWS。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 将容器应⽤程序迁移到 Amazon Elastic Container Service (Amazon ECS)。使⽤ Amazon Simple
Queue Service (Amazon SQS) 来检索消息。
B. 将容器应⽤程序迁移到 Amazon Elastic Kubernetes Service (Amazon EKS)。使⽤ Amazon MQ 来检索
消息。
C. 使⽤⾼可⽤性的 Amazon EC2 实例运⾏应⽤程序。使⽤ Amazon MQ 检索消息。
D. 使⽤ AWS Lambda 函数运⾏应⽤程序。使⽤ Amazon Simple Queue Service (Amazon SQS) 检索消
息。
https://examlearn.online
[2026/05]
Question #815
Topic 1
⼀家在线游戏公司将其平台托管在亚⻢逊 EC2 实例上，并通过⽹络负载均衡器 (NLB) 将其部署在多个 AWS 区
域。NLB 可以将请求路由到互联⽹上的⽬标服务器。该公司希望通过缩短其全球客户的端到端加载时间来改善客
户游戏体验。
哪种解决⽅案能够满⾜这些要求？
A. 在每个区域中创建应⽤程序负载均衡器 (ALB) 以替换现有的⽹络负载均衡器 (NLB)。将现有的 EC2 实例注
册为每个区域中 ALB 的⽬标。
B. 配置 Amazon Route 53 将等权重流量路由到每个区域中的 NLB。
C. 在公司拥有⼤量客户群的其他区域创建额外的 NLB 和 EC2 实例。
D. 在 AWS Global Accelerator 中创建⼀个标准加速器。将现有的 NLB 配置为⽬标终端节点。
Question #816
哪种解决⽅案能够以最⼩的运营开销满⾜这些要求？
Topic 1
⼀家公司有⼀个本地部署的应⽤程序，使⽤ SFTP 从多个供应商收集财务数据。该公司正在迁移到 AWS 云。该
公司创建了⼀个应⽤程序，使⽤ Amazon S3 API 从供应商上传⽂件。
⼀些供应商的系统运⾏在不⽀持 S3 API 的旧版应⽤程序上。这些供应商希望继续使⽤基于 SFTP 的应⽤程序上
传数据。该公司希望使⽤托管服务来满⾜使⽤旧版应⽤程序的供应商的需求。
A. 创建⼀个 AWS 数据库迁移服务 (AWS DMS) 实例，将使⽤旧版应⽤程序的供应商存储中的数据复制到
Amazon S3。向供应商提供访问 AWS DMS 实例的凭证。
B. 为使⽤传统应⽤程序的供应商创建 AWS Transfer Family 端点。
C. 配置 Amazon EC2 实例以运⾏ SFTP 服务器。指示使⽤旧版应⽤程序的供应商使⽤该 SFTP 服务器上传数
据。
D. 为使⽤旧版应⽤程序将⽂件上传到 SMB ⽂件共享的供应商配置 Amazon S3 ⽂件⽹关。
https://examlearn.online
[2026/05]
Question #817
Topic 1
⼀个市场营销团队想要为即将举办的综合性体育赛事策划营销活动。该团队拥有过去五年的新闻报道，格式为
PDF。他们需要⼀个解决⽅案来提取新闻报道的内容和情感倾向。该解决⽅案必须使⽤Amazon Textract来处理
新闻报道。
哪个解决⽅案能够以最低的运营成本满⾜这些要求？
A. 将提取的洞察结果提供给 Amazon Athena 进⾏分析。将提取的洞察结果和分析结果存储在 Amazon S3 存
储桶中。
B. 将提取出的洞察信息存储在 Amazon DynamoDB 表中。使⽤ Amazon SageMaker 构建情感模型。
C. 将提取的信息提供给 Amazon Comprehend 进⾏分析。将分析结果保存到 Amazon S3 存储桶。
D. 将提取出的洞察结果存储在 Amazon S3 存储桶中。使⽤ Amazon QuickSight 对数据进⾏可视化和分析。
Question #818
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司的应⽤程序运⾏在位于多个可⽤区的 Amazon EC2 实例上。该应⽤程序需要从第三⽅应⽤程序获取实时
数据。
该公司需要⼀个数据获取解决⽅案，将获取的原始数据放⼊ Amazon S3 存储桶中。
A. 创建⽤于数据摄取的 Amazon Kinesis 数据流。创建 Amazon Kinesis Data Firehose 传输流以使⽤
Kinesis 数据流。将 S3 存储桶指定为传输流的⽬标位置。
B. 在 AWS 数据库迁移服务 (AWS DMS) 中创建数据库迁移任务。将 EC2 实例的复制实例指定为源终端节
点。将 S3 存储桶指定为⽬标终端节点。将迁移类型设置为迁移现有数据并复制正在进⾏的更改。
C. 在 EC2 实例上创建和配置 AWS DataSync 代理。配置 DataSync 任务，将数据从 EC2 实例传输到 S3 存
储桶。
D. 创建与应⽤程序的 AWS Direct Connect 连接以进⾏数据摄取。创建 Amazon Kinesis Data Firehose 传输
流以使⽤来⾃应⽤程序的直接 PUT 操作。将 S3 存储桶指定为传输流的⽬标位置。
https://examlearn.online
[2026/05]
Question #819
Topic 1
⼀家公司的应⽤程序正在接收来⾃多个数据源的数据。数据⼤⼩各不相同，并且预计会随着时间推移⽽增加。⽬
前最⼤数据⼤⼩为 700 KB。随着更多数据源的加⼊，数据量和数据⼤⼩将持续增⻓。
该公司决定使⽤ Amazon DynamoDB 作为该应⽤程序的主数据库。解决⽅案架构师需要找到⼀种能够处理⼤数
据量的解决⽅案。
哪种解决⽅案能够以最⾼效的⽅式满⾜这些要求？
A. 创建⼀个 AWS Lambda 函数来过滤超出 DynamoDB 项⽬⼤⼩限制的数据。将较⼤的数据存储在 Amazon
DocumentDB（兼容 MongoDB）数据库中。
B. 将⼤型数据集中作为对象存储在 Amazon S3 存储桶中。在 DynamoDB 表中，创建⼀个包含指向数据 S3
URL 的属性的条⽬。
C. 将所有传⼊的⼤数据拆分成具有相同分区键的项集合。使⽤ BatchWriteItem API 操作，⼀次性将数据写⼊
DynamoDB 表。
D. 创建⼀个 AWS Lambda 函数，该函数使⽤ gzip 压缩来压缩写⼊ DynamoDB 表中的⼤对象。
Question #820
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在将⼀个遗留应⽤程序从本地数据中⼼迁移到 AWS。该应⽤程序依赖于数百个定时任务（cron
job），这些任务会在⼀天中不同的时间段以 1 到 20 分钟不等的间隔运⾏。
该公司希望找到⼀种解决⽅案，能够在 AWS 上调度和运⾏这些定时任务，并尽可能减少代码重构。此外，该解
决⽅案还必须⽀持在未来发⽣特定事件时运⾏定时任务。
A. 为定时任务创建容器镜像。使⽤ Amazon EventBridge Scheduler 创建周期性计划。将定时任务作为 AWS
Lambda 函数运⾏。
B. 为定时任务创建容器镜像。使⽤ Amazon Elastic Container Service (Amazon ECS) 上的 AWS Batch，并
设置调度策略来运⾏定时任务。
C. 为定时任务创建容器镜像。使⽤ Amazon EventBridge Scheduler 创建周期性计划。在 AWS Fargate 上
运⾏定时任务。
D. 为定时任务创建容器镜像。在 AWS Step Functions 中创建⼀个⼯作流，使⽤等待状态在指定时间运⾏定
时任务。使⽤ RunTask 操作在 AWS Fargate 上运⾏定时任务。
https://examlearn.online
[2026/05]
Question #821
Topic 1
⼀家公司使⽤ Salesforce。该公司需要将 Salesforce 中的现有数据和持续的数据变更加载到 Amazon Redshift
中进⾏分析。该公司不希望数据通过公共互联⽹传输。
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
A. 从 VPC 到 Salesforce 建⽴ VPN 连接。使⽤ AWS Glue DataBrew 传输数据。
B. 从 VPC 到 Salesforce 建⽴ AWS Direct Connect 连接。使⽤ AWS Glue DataBrew 传输数据。
C. 在 VPC 中创建到 Salesforce 的 AWS PrivateLink 连接。使⽤ Amazon AppFlow 传输数据。
D. 创建与 Salesforce 的 VPC 对等连接。使⽤ Amazon AppFlow 传输数据。
Question #822
该公司需要通过对应⽤程序和服务进⾏⼀些更改来优化存储成本。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司最近将其应⽤程序迁移到了 AWS。该应⽤程序运⾏在跨多个可⽤区的 Auto Scaling 组中的 Amazon
EC2 Linux 实例上。应⽤程序将数据存储在 Amazon Elastic File System (Amazon EFS) ⽂件系统中，该系统使
⽤ EFS 标准-不频繁访问存储。应⽤程序会对公司⽂件进⾏索引，索引存储在 Amazon RDS 数据库中。
A. 创建⼀个使⽤智能分层⽣命周期策略的 Amazon S3 存储桶。将所有⽂件复制到 S3 存储桶。更新应⽤程
序，使其使⽤ Amazon S3 API 来存储和检索⽂件。
B. 部署适⽤于 Windows ⽂件服务器的 Amazon FSx ⽂件共享。更新应⽤程序以使⽤ CIFS 协议存储和检索
⽂件。
C. 部署 Amazon FSx for OpenZFS ⽂件系统共享。更新应⽤程序以使⽤新的挂载点来存储和检索⽂件。
D. 创建⼀个使⽤ S3 Glacier 灵活检索的 Amazon S3 存储桶。将所有⽂件复制到该 S3 存储桶。更新应⽤程
序，使其使⽤ Amazon S3 API 以标准检索⽅式存储和检索⽂件。
https://examlearn.online
[2026/05]
Question #823
Topic 1
⼀家机器⼈公司正在设计⼀套⽤于医疗⼿术的解决⽅案。这些机器⼈将利⽤先进的传感器、摄像头和⼈⼯智能算
法来感知周围环境并完成⼿术。
该公司需要在 AWS 云中部署⼀个公共负载均衡器，以确保与后端服务的⽆缝通信。该负载均衡器必须能够根据
查询字符串将流量路由到不同的⽬标组，并且流量必须加密。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤⽹络负载均衡器，并附加来⾃ AWS Certificate Manager (ACM) 的证书。使⽤基于查询参数的路由。
B. 使⽤⽹关负载均衡器。在 AWS Identity and Access Management (IAM) 中导⼊⽣成的证书。将证书附加
到负载均衡器。使⽤基于 HTTP 路径的路由。
C. 使⽤已附加来⾃ AWS Certificate Manager (ACM) 证书的应⽤程序负载均衡器。使⽤基于查询参数的路
由。
D. 使⽤⽹络负载均衡器。在 AWS Identity and Access Management (IAM) 中导⼊⽣成的证书。将证书附加
到负载均衡器。使⽤基于查询参数的路由。
Question #824
哪个解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司有⼀个应⽤程序，运⾏在单个 Amazon EC2 实例上。该应⽤程序使⽤⼀个运⾏在同⼀个 EC2 实例上的
MySQL 数据库。该公司需要⼀个⾼可⽤性且可⾃动扩展的解决⽅案来应对不断增⻓的流量。
A. 将应⽤程序部署到运⾏在应⽤程序负载均衡器后⾯的⾃动扩展组中的 EC2 实例。创建⼀个包含多个与
MySQL 兼容节点的 Amazon Redshift 集群。
B. 将应⽤程序部署到配置为应⽤程序负载均衡器后⽅⽬标组的 EC2 实例。创建⼀个包含多个实例的 Amazon
RDS for MySQL 集群。
C. 将应⽤程序部署到运⾏在应⽤程序负载均衡器后⾯的⾃动扩展组中的 EC2 实例。为数据库层创建⼀个
Amazon Aurora Serverless MySQL 集群。
D. 将应⽤程序部署到配置为应⽤程序负载均衡器后⽬标组的 EC2 实例。创建⼀个使⽤ MySQL 连接器的
Amazon ElastiCache for Redis 集群。
https://examlearn.online
[2026/05]
Question #825
Topic 1
⼀家公司计划将数据迁移到 Amazon S3 存储桶。数据在 S3 存储桶中必须进⾏静态加密。加密密钥必须每年⾃
动轮换。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将数据迁移到 S3 存储桶。使⽤ Amazon S3 管理密钥 (SSE-S3) 进⾏服务器端加密。使⽤ SSE-S3 加密密
钥的内置密钥轮换机制。
B. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。启⽤⾃动密钥轮换。将 S3 存储桶的默
认加密⾏为设置为使⽤客户管理的 KMS 密钥。将数据迁移到 S3 存储桶。
C. 创建 AWS Key Management Service (AWS KMS) 客户管理密钥。将 S3 存储桶的默认加密⾏为设置为使
⽤该客户管理的 KMS 密钥。将数据迁移到 S3 存储桶。每年⼿动轮换 KMS 密钥。
D. 使⽤客户密钥材料加密数据。将数据迁移到 S3 存储桶。创建不包含密钥材料的 AWS Key Management
Service (AWS KMS) 密钥。将客户密钥材料导⼊ KMS 密钥。启⽤⾃动密钥轮换。
Question #826
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在将其管理的本地 Microsoft Active Directory 中的应⽤程序迁移到 AWS。该公司将这些应⽤程序部
署在多个 AWS 账户中，并使⽤ AWS Organizations 集中管理这些账户。该
公司的安全团队需要⼀个跨所有 AWS 账户的单点登录解决⽅案。此外，该公司还必须继续管理本地 Active
Directory 中的⽤户和组。
A. 在 AWS Directory Service 中为 Microsoft Active Directory 创建企业版 Active Directory。将该 Active
Directory 配置为 AWS IAM Identity Center 的身份源。
B. 启⽤ AWS IAM Identity Center。配置双向林信任关系，使⽤ AWS Directory Service for Microsoft
Active Directory 将公司⾃管理的 Active Directory 与 IAM Identity Center 连接起来。
C. 使⽤ AWS Directory Service 与公司⾃管理的 Active Directory 建⽴双向信任关系。
D. 在 Amazon EC2 上部署身份提供商 (IdP)。将 IdP 链接为 AWS IAM 身份中⼼中的身份源。
https://examlearn.online
[2026/05]
Question #827
Topic 1
⼀家公司计划将其应⽤程序部署在 Amazon Aurora PostgreSQL Serverless v2 集群上。该应⽤程序将⾯临巨⼤
的流量。随着应⽤程序负载的增加，该公司希望优化集群的存储性能。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置集群以使⽤ Aurora 标准存储配置。
B. 将集群存储类型配置为预置 IOPS。
C. 将集群存储类型配置为通⽤型。
D. 配置集群以使⽤ Aurora I/O 优化存储配置。
Question #828
⼀家在 AWS 上运⾏的⾦融服务公司已设计出符合⾏业标准的安全控制措施。这些⾏业标准包括美国国家标准与
技术研究院 (NIST) 和⽀付卡⾏业数据安全标准 (PCI DSS)。
哪种解决⽅案能够满⾜这些要求？
Topic 1
该公司的第三⽅审计机构需要证明这些已设计的控制措施已实施并正常运⾏。该公司在 AWS Organizations 的单
个组织中拥有数百个 AWS 账户。该公司需要监控所有账户中控制措施的当前状态。
A. 从 Organizations 管理账户中指定⼀个账户作为 Amazon Inspector 的委派管理员账户。将 Inspector 与
Organizations 集成，以发现和扫描所有 AWS 账户中的资源。启⽤ Inspector 的 NIST 和 PCI DSS ⾏业标
准。
B. 从组织管理帐户中指定⼀个帐户作为 Amazon GuardDuty 委托管理员帐户。在指定的 GuardDuty 管理员
帐户中，启⽤ GuardDuty 以保护所有成员帐户。启⽤ GuardDuty 的 NIST 和 PCI DSS ⾏业标准。
C. 在 Organizations 管理账户中配置 AWS CloudTrail 组织跟踪。指定⼀个账户作为合规性账户。在合规性
账户中启⽤ NIST 和 PCI DSS 的 CloudTrail 安全标准。
D. 从 Organizations 管理账户中指定⼀个账户作为 AWS Security Hub 的委派管理员账户。在该指定的
Security Hub 管理员账户中，为所有成员账户启⽤ Security Hub。启⽤符合 NIST 和 PCI DSS 标准的
Security Hub。
https://examlearn.online
[2026/05]
Question #829
Topic 1
⼀家公司使⽤ Amazon S3 存储桶作为其数据湖存储平台。该 S3 存储桶包含海量数据，多个团队和数百个应⽤
程序会随机访问这些数据。该公司希望降低 S3 存储成本，并为频繁访问的对象提供即时可⽤性。
满⾜这些要求的最佳运维解决⽅案是什么？
A. 创建 S3 ⽣命周期规则，将对象转换到 S3 智能分层存储类。
B. 将对象存储在 Amazon S3 Glacier 中。使⽤ S3 Select 为应⽤程序提供数据访问权限。
C. 使⽤ S3 存储类分析的数据创建 S3 ⽣命周期规则，以⾃动将对象转换为 S3 标准-不频繁访问 (S3
Standard-IA) 存储类。
D. 将对象转换为 S3 标准-不频繁访问 (S3 Standard-IA) 存储类。创建⼀个 AWS Lambda 函数，以便在应⽤
程序访问对象时将其转换为 S3 标准存储类。
Question #830
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司拥有 5 TB 的数据集。这些数据集包含 100 万个⽤户配置⽂件和 1000 万个连接。⽤户配置⽂件之间存
在多对多关系。该公司需要⼀种⾼效的⽅式来查找最多五层的相互连接。
A. 使⽤ Amazon S3 存储桶存储数据集。使⽤ Amazon Athena 执⾏ SQL JOIN 查询以查找连接。
B. 使⽤ Amazon Neptune 存储包含边和顶点的数据集。查询数据以查找连接。
C. 使⽤ Amazon S3 存储桶存储数据集。使⽤ Amazon QuickSight 可视化连接。
D. 使⽤ Amazon RDS 存储包含多个表的数据集。执⾏ SQL JOIN 查询以查找连接。
https://examlearn.online
[2026/05]
Question #831
Topic 1
⼀家公司需要在其本地环境和 AWS 之间建⽴安全连接。此连接不需要⾼带宽，且仅需处理少量流量。连接应快
速建⽴。
建⽴此类连接最具成本效益的⽅法是什么？
A. 实现客户端 VPN。
B. 实施 AWS Direct Connect。
C. 在 Amazon EC2 上部署堡垒主机。
D. 实现 AWS 站点到站点 VPN 连接。
Question #832
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
Topic 1
⼀家公司⽬前使⽤本地部署的 SFTP ⽂件传输解决⽅案。为了扩展⽂件传输解决⽅案并利⽤ Amazon S3 优化成
本，该公司正在迁移到 AWS 云平台。公司员⼯将使⽤其本地 Microsoft Active Directory (AD) 的凭据访问新解
决⽅案。该公司希望保留当前的身份验证和⽂件访问机制。
A. 配置 S3 ⽂件⽹关。在⽂件⽹关上创建 SMB ⽂件共享，并使⽤现有的 Active Directory 进⾏身份验证。
B. 配置⼀个包含 Amazon EC2 实例的⾃动扩展组来运⾏ SFTP 解决⽅案。将该组配置为在 CPU 利⽤率达到
60% 时进⾏扩展。
C. 创建具有 SFTP 端点的 AWS Transfer Family 服务器。选择 AWS Directory Service 作为身份提供程序。
使⽤ AD Connector 连接本地 Active Directory。
D. 创建 AWS Transfer Family SFTP 端点。配置该端点，使其使⽤ AWS Directory Service 作为身份提供程
序连接到现有的 Active Directory。
https://examlearn.online
[2026/05]
Question #833
Topic 1
⼀家公司正在设计⼀个事件驱动的订单处理系统。每个订单在创建后都需要经过多个验证步骤。每个验证步骤都
由⼀个幂等的 AWS Lambda 函数执⾏。每个验证步骤都独⽴于其他验证步骤。各个验证步骤只需要订单事件信
息的⼀个⼦集。
该公司希望确保每个验证步骤的 Lambda 函数只能访问其所需的订单事件信息。订单处理系统的各个组件应采⽤
松耦合设计，以适应未来的业务变化。
哪种解决⽅案能够满⾜这些要求？
A. 为每个验证步骤创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。创建⼀个新的 Lambda
函数，将订单数据转换为每个验证步骤所需的格式，并将消息发布到相应的 SQS 队列。将每个验证步骤的
Lambda 函数订阅到其对应的 SQS 队列。
B. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 主题。将验证步骤 Lambda 函数订阅到该
SNS 主题。使⽤消息体过滤功能，仅向每个已订阅的 Lambda 函数发送所需数据。
C. 创建 Amazon EventBridge 事件总线。为每个验证步骤创建⼀个事件规则。配置输⼊转换器，使其仅向每
个⽬标验证步骤 Lambda 函数发送所需数据。
D. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列。创建⼀个新的 Lambda 函数来订阅该
Question #834
SQS 队列，并将订单数据转换为每个验证步骤所需的格式。使⽤该新的 Lambda 函数在不同的线程上并⾏同
步调⽤各个验证步骤的 Lambda 函数。
Topic 1
⼀家公司正在将⼀个三层架构的应⽤程序迁移到 AWS。该应⽤程序需要使⽤ MySQL 数据库。过去，⽤户反映在
创建新条⽬时应⽤程序性能不佳。这些性能问题是由于⽤户在⼯作时间内通过该应⽤程序⽣成各种实时报告造成
的。
哪种解决⽅案可以提⾼应⽤程序迁移到 AWS 后的性能？
A. 将数据导⼊到已预置容量的 Amazon DynamoDB 表中。重构应⽤程序以使⽤ DynamoDB ⽣成报表。
B. 在计算优化型 Amazon EC2 实例上创建数据库。确保计算资源超过本地数据库的计算资源。
C. 创建⼀个具有多个只读副本的 Amazon Aurora MySQL 多可⽤区数据库集群。配置应⽤程序以使⽤读取器
端点⽣成报表。
D. 创建⼀个 Amazon Aurora MySQL 多可⽤区数据库集群。配置应⽤程序以使⽤该集群的备份实例作为报表
的端点。
https://examlearn.online
[2026/05]
Question #835
Topic 1
⼀家公司正在使⽤ AWS Direct Connect 连接将安全的本地⽹络扩展到 AWS 云。该本地⽹络没有直接的互联⽹
访问权限。运⾏在该本地⽹络上的应⽤程序需要使⽤ Amazon S3 存储桶。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建⼀个公共虚拟接⼝ (VIF)。将 AWS 流量路由到公共 VIF 上。
B. 创建⼀个 VPC 和⼀个 NAT ⽹关。将来⾃本地⽹络的 AWS 流量路由到 NAT ⽹关。
C. 创建⼀个 VPC 和⼀个 Amazon S3 接⼝终端节点。将来⾃本地⽹络的 AWS 流量路由到 S3 接⼝终端节
点。
D. 在本地⽹络和 Direct Connect 之间创建 VPC 对等连接。通过该对等连接路由 AWS 流量。
Question #836
Topic 1
⼀家公司使⽤位于单个 AWS 区域中的 Amazon EC2 实例⾃动扩展组来托管其⽹站。该⽹站不需要数据库。
随着公司业务的扩展，其⼯程团队将⽹站部署到了第⼆个区域。为了应对业务增⻓并实现灾难恢复，该公司希望
将流量分配到两个区域。解决⽅案不应处理来⾃⽹站运⾏状况不佳区域的流量。
为了满⾜这些要求，该公司应该使⽤哪种策略或资源？
A. Amazon Route 53 简单路由策略
B. Amazon Route 53 多值应答路由策略
C. 在⼀个区域中部署应⽤程序负载均衡器，其⽬标组指定来⾃两个区域的 EC2 实例 ID。
D. 在⼀个区域中部署应⽤程序负载均衡器，其⽬标组指定来⾃两个区域的 EC2 实例的 IP 地址。
https://examlearn.online
[2026/05]
Question #837
Topic 1
⼀家公司在由 Amazon Elastic Block Store (Amazon EBS) 提供⽀持的 Amazon EC2 实例上运⾏其应⽤程序。
这些 EC2 实例运⾏的是最新的 Amazon Linux 版本。当公司员⼯存储和检索 25 GB 或更⼤的⽂件时，应⽤程序
会出现可⽤性问题。该公司需要⼀个⽆需在 EC2 实例之间传输⽂件的解决⽅案。这些⽂件必须能够在多个 EC2
实例和多个可⽤区中访问。
哪个解决⽅案能够满⾜这些要求？
A. 将所有⽂件迁移到 Amazon S3 存储桶。指示员⼯从 S3 存储桶访问⽂件。
B. 对现有 EBS 卷进⾏快照。将快照作为 EBS 卷挂载到各个 EC2 实例上。指示员⼯从 EC2 实例访问这些⽂
件。
C. 在所有 EC2 实例上挂载 Amazon Elastic File System (Amazon EFS) ⽂件系统。指导员⼯从 EC2 实例访
问这些⽂件。
D. 从 EC2 实例创建 Amazon 系统映像 (AMI)。使⽤该 AMI 配置使⽤实例存储卷的新 EC2 实例。指导员⼯从
EC2 实例访问⽂件。
Question #838
Topic 1
⼀家公司在 Amazon EC2 上运⾏⼀个⾼度敏感的应⽤程序，该应⽤程序由 Amazon RDS 数据库提供⽀持。合规
性法规要求所有个⼈身份信息 (PII) 在静态存储时都必须加密。
解决⽅案架构师应该推荐哪种解决⽅案，才能在对基础设施进⾏最少更改的情况下满⾜此要求？
A. 部署 AWS Certificate Manager 以⽣成证书。使⽤这些证书加密数据库卷。
B. 部署 AWS CloudHSM，⽣成加密密钥，并使⽤这些密钥加密数据库卷。
C. 使⽤ AWS Key Management Service (AWS KMS) 密钥配置 SSL 加密，以加密数据库卷。
D. 使⽤ AWS Key Management Service (AWS KMS) 密钥配置 Amazon Elastic Block Store (Amazon EBS)
加密和 Amazon RDS 加密，以加密实例和数据库卷。
https://examlearn.online
[2026/05]
Question #839
Topic 1
⼀家公司在 VPC 的私有⼦⽹中运⾏⼀个 AWS Lambda 函数。这些⼦⽹默认通过 Amazon EC2 NAT 实例连接到
互联⽹。Lambda 函数处理输⼊数据，并将输出作为对象保存到 Amazon S3。
由于 NAT 实例⽹络流量过⼤，Lambda 函数在尝试上传对象时会间歇性地超时。该公司希望在不经过互联⽹的情
况下访问 Amazon S3。
哪种解决⽅案能够满⾜这些要求？
A. 将 EC2 NAT 实例替换为 AWS 托管的 NAT ⽹关。
B. 将 VPC 中的 EC2 NAT 实例的⼤⼩增加到⽹络优化型实例类型。
C. 在 VP 中为 Amazon S3 配置⽹关端点，并相应地更新⼦⽹的路由表。
D. 配置传输⽹关。将传输⽹关附件放置在 Lambda 函数运⾏所在的私有⼦⽹中。
Question #840
A. 亚⻢逊云前沿
Topic 1
⼀家在全球各地拥有记者的新闻公司将其⼴播系统托管在 AWS 上。记者们通过⼿机上的软件，利⽤实时消息协
议 (RTMP) 向⼴播系统发送直播流。
解决⽅案架构师需要设计⼀个⽅案，使记者能够发送最⾼质量的直播流，并且该⽅案必须提供与⼴播系统之间加
速的 TCP 连接。
解决⽅案架构师应该使⽤什么来满⾜这些要求？
B. AWS 全球加速器
C. AWS客户端VPN
D. Amazon EC2 实例和 AWS 弹性 IP 地址
https://examlearn.online
[2026/05]
Question #841
Topic 1
⼀家公司使⽤ Amazon EC2 实例和 Amazon Elastic Block Store (Amazon EBS) 来运⾏其⾃管理数据库。该公
司拥有 350 TB 的数据，分布在所有 EBS 卷上。该公司每天对 EBS 进⾏快照，并将快照保留 1 个⽉。每⽇数据
变更率为 EBS 卷的 5%。
由于新的法规要求，该公司需要将每⽉快照保留 7 年。为了符合新法规并确保数据可⽤且管理⼯作量最⼩，该公
司需要更改其备份策略。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将每⽇快照在 EBS 快照标准层保留 1 个⽉。将每⽉快照复制到 Amazon S3 Glacier Deep Archive，保留
期为 7 年。
B. 继续执⾏当前的 EBS 快照策略。添加⼀项新策略，将每⽉快照移动到 Amazon EBS 快照存档，保留期限
为 7 年。
C. 将每⽇快照在 EBS 标准快照层保留 1 个⽉。将每⽉快照在标准层保留 7 年。使⽤增量快照。
D. 将每⽇快照保存在 EBS 标准快照层。每⽉使⽤ EBS Direct API 对所有 EBS 卷进⾏快照。将快照存储在
Amazon S3 存储桶的“不频繁访问”层中，保存期限为 7 年。
Question #842
Topic 1
⼀家公司在多个 Amazon EC2 实例上运⾏⼀个应⽤程序，这些实例将持久数据存储在 Amazon Elastic File
System (Amazon EFS) ⽂件系统中。该公司需要使⽤ AWS 托管服务解决⽅案将数据复制到另⼀个 AWS 区域。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ EFS 到 EFS 备份解决⽅案将数据复制到另⼀个区域中的 EFS ⽂件系统。
B. 运⾏每⽇脚本，将数据从 EFS ⽂件系统复制到 Amazon S3 存储桶。在 S3 存储桶上启⽤ S3 跨区域复制。
C. 在另⼀个区域中创建 VPC。建⽴跨区域的 VPC 对等体。运⾏每⽇ rsync 命令，将数据从原始区域复制到
新区域。
D. 使⽤ AWS Backup 创建⼀个备份计划，该计划包含⼀条规则，⽤于每⽇备份并将其复制到另⼀个区域。将
EFS ⽂件系统资源分配给该备份计划。
https://examlearn.online
[2026/05]
Question #843
Topic 1
⼀家电商公司正在将其本地⼯作负载迁移到 AWS 云。该⼯作负载⽬前包含⼀个 Web 应⽤程序和⼀个⽤于存储的
后端 Microsoft SQL 数据库。
该公司预计在促销活动期间将迎来⼤量客户。AWS 云中的新基础设施必须具备⾼可⽤性和可扩展性。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 将 Web 应⽤程序迁移到位于两个可⽤区中的两个 Amazon EC2 实例，并通过应⽤程序负载均衡器进⾏配
置。将数据库迁移到 Amazon RDS for Microsoft SQL Server，并在两个可⽤区中都配置只读副本。
B. 将 Web 应⽤程序迁移到运⾏在跨两个可⽤区、位于应⽤程序负载均衡器后⾯的⾃动扩展组中的 Amazon
EC2 实例。将数据库迁移到位于不同 AWS 区域的两个 EC2 实例，并启⽤数据库复制。
C. 将 Web 应⽤程序迁移到运⾏在跨两个可⽤区、位于应⽤程序负载均衡器后⾯的⾃动扩展组中的 Amazon
EC2 实例。将数据库迁移到采⽤多可⽤区部署的 Amazon RDS。
D. 将 Web 应⽤程序迁移到位于三个可⽤区中的三个 Amazon EC2 实例，并部署在应⽤程序负载均衡器之
后。将数据库迁移到位于三个可⽤区中的三个 EC2 实例。
Question #844
Topic 1
⼀家公司有⼀个本地部署的业务应⽤程序，每天⽣成数百个⽂件。这些⽂件存储在 SMB ⽂件共享上，需要与应
⽤程序服务器建⽴低延迟连接。公司新政策规定，所有应⽤程序⽣成的⽂件都必须复制到 AWS。公司已经建⽴了
与 AWS 的 VPN 连接。
应⽤程序开发团队没有时间进⾏必要的代码修改以将应⽤程序迁移到 AWS。
解决⽅案架构师应该推荐哪项服务来允许应⽤程序将⽂件复制到 AWS？
A. Amazon Elastic File System (Amazon EFS)
B. Amazon FSx Windows ⽂件服务器
C. AWS 雪球
D. AWS 存储⽹关
https://examlearn.online
[2026/05]
Question #845
Topic 1
⼀家公司有 15 名员⼯。该公司将员⼯的⼊职⽇期存储在 Amazon DynamoDB 表中。该公司希望在每位员⼯的⼊
职周年纪念⽇当天向其发送电⼦邮件。
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
A. 创建⼀个脚本，⽤于扫描 DynamoDB 表，并在必要时使⽤ Amazon Simple Notification Service
(Amazon SNS) 向员⼯发送电⼦邮件。使⽤ cron 作业每天在 Amazon EC2 实例上运⾏此脚本。
B. 创建⼀个脚本，⽤于扫描 DynamoDB 表，并在必要时使⽤ Amazon Simple Queue Service (Amazon
SQS) 向员⼯发送电⼦邮件。使⽤ cron 作业每天在 Amazon EC2 实例上运⾏此脚本。
C. 创建⼀个 AWS Lambda 函数，该函数扫描 DynamoDB 表，并在必要时使⽤ Amazon Simple Notification
Service (Amazon SNS) 向员⼯发送电⼦邮件。将此 Lambda 函数设置为每天运⾏。
D. 创建⼀个 AWS Lambda 函数，该函数扫描 DynamoDB 表，并在必要时使⽤ Amazon Simple Queue
Service (Amazon SQS) 向员⼯发送电⼦邮件。将此 Lambda 函数设置为每天运⾏。
Question #846
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司的应⽤程序运⾏在 Amazon EC2 实例上，这些实例位于⾃动扩展组 (Auto Scaling group) 内，并由弹
性负载均衡器 (ELB) 负载均衡器管理。根据应⽤程序的历史数据，该公司预计每年节假⽇期间都会出现流量⾼
峰。解决⽅案架构师必须设计⼀个策略，以确保⾃动扩展组主动增加容量，从⽽最⼤限度地减少对应⽤程序⽤户
性能的影响。
A. 创建⼀个 Amazon CloudWatch 警报，以便在 CPU 利⽤率超过 90% 时扩展 EC2 实例。
B. 创建⼀个定期计划操作，以便在预计需求⾼峰期到来之前扩展⾃动扩展组。
C. 在⾼峰需求期间增加⾃动扩展组中 EC2 实例的最⼩和最⼤数量。
D. 配置 Amazon Simple Notification Service (Amazon SNS) 通知，以便在发⽣
autoscaling:EC2_INSTANCE_LAUNCH 事件时发送警报。
https://examlearn.online
[2026/05]
Question #847
Topic 1
⼀家公司使⽤ Amazon RDS for PostgreSQL 数据库作为其数据层。该公司必须为这些数据库实施密码轮换。
哪种解决⽅案能够以最⼩的运维开销满⾜此要求？
A. 将密码存储在 AWS Secrets Manager 中。启⽤密钥⾃动轮换功能。
B. 将密码存储在 AWS Systems Manager Parameter Store 中。启⽤参数的⾃动轮换功能。
C. 将密码存储在 AWS Systems Manager Parameter Store 中。编写⼀个 AWS Lambda 函数来轮换密码。
D. 将密码存储在 AWS Key Management Service (AWS KMS) 中。启⽤ AWS KMS 密钥的⾃动轮换。
Question #848
解决⽅案架构师必须设计⼀个数据库迁移⽅案。
哪种⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司在 Oracle 数据库企业版上运⾏其应⽤程序。该公司需要将应⽤程序和数据库迁移到 AWS。迁移过程
中，该公司可以使⽤⾃带许可证 (BYOL) 模式。该应⽤程序使⽤了需要特权访问的第三⽅数据库功能。
A. 使⽤原⽣⼯具将数据库迁移到 Amazon RDS for Oracle。将第三⽅功能替换为 AWS Lambda。
B. 使⽤原⽣⼯具将数据库迁移到 Amazon RDS Custom for Oracle。⾃定义新数据库设置以⽀持第三⽅功
能。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据库迁移到 Amazon DynamoDB。⾃定义新数据库设置以⽀
持第三⽅功能。
D. 使⽤ AWS 数据库迁移服务 (AWS DMS) 将数据库迁移到 Amazon RDS for PostgreSQL。重写应⽤程序代
码，消除对第三⽅功能的依赖。
https://examlearn.online
[2026/05]
Question #849
Topic 1
⼀所⼤型国际⼤学已将其所有计算服务部署在 AWS 云平台上，包括 Amazon EC2、Amazon RDS 和 Amazon
DynamoDB。该⼤学⽬前依赖许多⾃定义脚本来备份其基础设施。然⽽，该⼤学希望通过使⽤ AWS 原⽣选项来
集中管理并尽可能⾃动化数据备份。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤第三⽅备份软件和 AWS Storage Gateway 磁带⽹关虚拟磁带库。
B. 使⽤ AWS Backup 配置和监控所有正在使⽤的服务的备份。
C. 使⽤ AWS Config 设置⽣命周期管理，按计划对所有数据源进⾏快照。
D. 使⽤ AWS Systems Manager State Manager 来管理备份任务的配置和监控。
Question #850
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司希望构建其 IT 基础设施地图，以便识别并强制执⾏针对存在安全⻛险资源的策略。该公司的安全团队必
须能够查询 IT 基础设施地图中的数据并快速识别安全⻛险。
A. 使⽤ Amazon RDS 存储数据。使⽤ SQL 查询数据以识别安全⻛险。
B. 使⽤ Amazon Neptune 存储数据。使⽤ SPARQL 查询数据以识别安全⻛险。
C. 使⽤ Amazon Redshift 存储数据。使⽤ SQL 查询数据以识别安全⻛险。
D. 使⽤ Amazon DynamoDB 存储数据。使⽤ PartiQL 查询数据以识别安全⻛险。
https://examlearn.online
[2026/05]
Question #851
Topic 1
⼀家⼤型公司希望为其遍布全球的开发⼈员提供独⽴的、容量有限的托管 PostgreSQL 数据库，⽤于开发⽤途。
这些数据库的容量较⼩。开发⼈员仅在需要⼯作时才需要使⽤这些数据库。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 赋予开发⼈员启动独⽴ Amazon Aurora 实例的能⼒。设置⼀个流程，在⼯作⽇结束时关闭 Aurora 实例，
并在下⼀个⼯作⽇开始时启动 Aurora 实例。
B. 开发⼀款 AWS 服务⽬录产品，对启动 Amazon Aurora 实例的⼤⼩进⾏限制。允许开发⼈员在需要开发数
据库时启动该产品。
C. 创建⼀个 Amazon Aurora Serverless 集群。开发⼀个 AWS Service Catalog 产品，⽤于使⽤默认容量设
置在该集群中启动数据库。授予开发⼈员对该产品的访问权限。
D. 监控 AWS Trusted Advisor 对空闲 Amazon RDS 数据库的检查。创建⼀个进程来终⽌已识别的空闲 RDS
数据库。
Question #852
哪个解决⽅案满⾜这些要求？
Topic 1
⼀家公司正在构建⼀个⽤于内容管理系统的 Web 应⽤程序。该内容管理系统运⾏在 Amazon EC2 实例上，并由
应⽤程序负载均衡器 (ALB) 提供⽀持。这些 EC2 实例运⾏在跨多个可⽤区的⾃动扩展组中。⽤户不断地在内容管
理系统中添加和更新⽂件、博客和其他⽹站资源。
解决⽅案架构师必须实现⼀个解决⽅案，使所有 EC2 实例都能以尽可能⼩的延迟共享最新的⽹站内容。
A. 更新⾃动扩展组⽣命周期策略中的 EC2 ⽤户数据，以从最近启动的 EC2 实例复制⽹站资产。配置 ALB，
使其仅在最新的 EC2 实例中对⽹站资产进⾏更改。
B. 将⽹站资源复制到 Amazon Elastic File System (Amazon EFS) ⽂件系统。配置每个 EC2 实例以在本地挂
载 EFS ⽂件系统。配置⽹站托管应⽤程序以引⽤存储在 EFS ⽂件系统中的⽹站资源。
C. 将⽹站资源复制到 Amazon S3 存储桶。确保每个 EC2 实例都将⽹站资源从 S3 存储桶下载到关联的
Amazon Elastic Block Store (Amazon EBS) 卷。每⼩时运⾏⼀次 S3 同步命令，以保持⽂件最新。
D. 恢复包含⽹站资源的 Amazon Elastic Block Store (Amazon EBS) 快照。在新 EC2 实例启动时，将该
EBS 快照作为辅助 EBS 卷附加到实例。配置⽹站托管应⽤程序，使其引⽤存储在辅助 EBS 卷中的⽹站资源。
https://examlearn.online
[2026/05]
Question #853
Topic 1
⼀家公司的 Web 应⽤程序由多个 Amazon EC2 实例组成，这些实例运⾏在 VPC 中的应⽤程序负载均衡器之
后。数据存储在 Amazon RDS for MySQL 数据库实例中。该公司需要能够⾃动检测并响应其 AWS 环境中的可疑
或异常⾏为。该公司已在其架构中添加了 AWS WAF。
为了抵御威胁，解决⽅案架构师接下来应该做什么？
A. 使⽤ Amazon GuardDuty 执⾏威胁检测。配置 Amazon EventBridge 以筛选 GuardDuty 的检测结果，并
调⽤ AWS Lambda 函数来调整 AWS WAF 规则。
B. 使⽤ AWS Firewall Manager 执⾏威胁检测。配置 Amazon EventBridge 以筛选 Firewall Manager 的检测
结果，并调⽤ AWS Lambda 函数来调整 AWS WAF Web ACL。
C. 使⽤ Amazon Inspector 执⾏威胁检测并更新 AWS WAF 规则。创建 VPC ⽹络 ACL 以限制对 Web 应⽤
程序的访问。
D. 使⽤ Amazon Macie 执⾏威胁检测并更新 AWS WAF 规则。创建 VPC ⽹络 ACL 以限制对 Web 应⽤程序
的访问。
Question #854
哪种解决⽅案能够以最⼩的运维⼯作量满⾜这些要求？
Topic 1
⼀家公司计划运⾏⼀组连接到 Amazon Aurora 数据库的 Amazon EC2 实例。该公司已构建了⼀个 AWS
CloudFormation 模板来部署 EC2 实例和 Aurora 数据库集群。该公司希望允许实例以安全的⽅式对数据库进⾏
身份验证，并且不希望维护静态数据库凭证。
A. 创建⼀个数据库⽤户，并设置⽤户名和密码。将数据库⽤户名和密码参数添加到 CloudFormation 模板
中。在 EC2 实例启动时，将这些参数传递给实例。
B. 创建⼀个数据库⽤户，并设置⽤户名和密码。将⽤户名和密码存储在 AWS Systems Manager Parameter
Store 中。配置 EC2 实例以从 Parameter Store 中检索数据库凭证。
C. 配置数据库集群以使⽤ IAM 数据库身份验证。创建⼀个⽤于 IAM 身份验证的数据库⽤户。将⻆⾊与 EC2
实例关联，以允许实例上的应⽤程序访问数据库。
D. 配置数据库集群以使⽤ IAM ⽤户进⾏ IAM 数据库身份验证。创建⼀个与 IAM ⽤户名称匹配的数据库⽤
户。将该 IAM ⽤户与 EC2 实例关联，以允许实例上的应⽤程序访问数据库。
https://examlearn.online
[2026/05]
Question #855
Topic 1
⼀家公司希望配置其 Amazon CloudFront 分发以使⽤ SSL/TLS 证书。该公司不想使⽤分发的默认域名，⽽是希
望使⽤不同的域名。
哪种解决⽅案可以在不产⽣任何额外费⽤的情况下部署证书？
A. 从 美国东部 1 区域的 AWS Certificate Manager (ACM) 请求 Amazon 颁发的私有证书。
B. 从美国⻄部 1 区域的 AWS Certificate Manager (ACM) 请求 Amazon 颁发的私有证书。
C. 从美国东部 1 区域的 AWS Certificate Manager (ACM) 请求 Amazon 颁发的公共证书。
D. 从美国⻄部 1 区域的 AWS Certificate Manager (ACM) 请求 Amazon 颁发的公共证书。
Question #856
公司必须实施⼀种解决⽅案，仅允许外部顾问访问该报告。
哪种解决⽅案能够以最⾼的运营效率满⾜这些要求？
站 URL 分享给外部顾问。
Topic 1
⼀家公司创建运营数据并将其存储在 Amazon S3 存储桶中。为了进⾏年度审计，外部顾问需要访问存储在 S3
存储桶中的年度报告。该外部顾问需要访问该报告 7 天。
A. 创建⼀个新的 S3 存储桶，并将其配置为托管公共静态⽹站。将运营数据迁移到新的 S3 存储桶。将 S3 ⽹
B. 开放对 S3 存储桶的公共访问权限 7 天。外部顾问完成审计后，移除对 S3 存储桶的访问权限。
C. 创建⼀个新的 IAM ⽤户，该⽤户有权访问 S3 存储桶中的报告。将访问密钥提供给外部顾问。7 天后撤销
访问密钥。
D. ⽣成⼀个预签名 URL，该 URL 具有访问 S3 存储桶上报告位置所需的权限。将该预签名 URL 分享给外部
顾问。
https://examlearn.online
[2026/05]
Question #857
Topic 1
⼀家公司计划在 Amazon EC2 实例上运⾏⾼性能计算 (HPC) ⼯作负载。该⼯作负载需要低延迟⽹络性能和⾼⽹
络吞吐量，以及紧密耦合的节点间通信。
哪种解决⽅案能够满⾜这些要求？
A. 将 EC2 实例配置为集群放置组的⼀部分。
B. 启动具有专⽤实例租户的 EC2 实例。
C. 将 EC2 实例作为竞价型实例启动。
D. 在 EC2 实例启动时配置按需容量预留。
Question #858
哪种⽅案满⾜这些要求？
Topic 1
⼀家公司拥有相距 500 英⾥（804.7 公⾥）的主数据中⼼和备⽤数据中⼼，并通过⾼速光纤电缆互连。该公司需
要在其数据中⼼与 AWS 上的 VPC 之间建⽴⾼可⽤性且安全的⽹络连接，以⽀持关键业务⼯作负载。解决⽅案架
构师必须选择能够提供最⼤弹性的连接⽅案。
A. 来⾃主数据中⼼的两条 AWS Direct Connect 连接分别终⽌于两台不同设备上的两个 Direct Connect 位
置。
B. 来⾃主数据中⼼和辅助数据中⼼的单个 AWS Direct Connect 连接，终⽌于同⼀设备上的同⼀个 Direct
Connect 位置。
C. 来⾃主数据中⼼和备⽤数据中⼼的两条 AWS Direct Connect 连接分别终⽌于两台不同设备上的两个
Direct Connect 位置。
D. 来⾃主数据中⼼和辅助数据中⼼的单个 AWS Direct Connect 连接，终⽌于两台独⽴设备上的同⼀个
Direct Connect 位置。
https://examlearn.online
[2026/05]
Question #859
Topic 1
⼀家公司运⾏着多个⾼利⽤率的 Amazon RDS for Oracle On-Demand 数据库实例。这些 RDS 数据库实例运⾏
在 AWS Organizations 组织内的成员账户中。
该公司财务团队拥有对该组织管理账户和成员账户的访问权限。财务团队希望通过使⽤ AWS Trusted Advisor 来
优化成本。
以下哪两项步骤组合能够满⾜这些要求？
A. 在管理帐户中使⽤ Trusted Advisor 的建议。
B. 在运⾏ RDS 数据库实例的成员帐户中使⽤ Trusted Advisor 建议。
C. 检查 Amazon RDS 预留实例优化的 Trusted Advisor 检查。
D. 检查 Amazon RDS 空闲数据库实例的 Trusted Advisor 检查。
E. 检查 Trusted Advisor 的计算优化检查结果。使⽤ AWS Compute Optimizer 交叉验证结果。
Question #860
为了满⾜这些要求，解决⽅案架构师应该怎么做？
Topic 1
⼀位解决⽅案架构师正在开发⼀个应⽤程序。该应⽤程序将在VPC中多个可⽤区内私有⼦⽹的Amazon EC2实例
上运⾏。这些EC2实例会频繁访问包含机密信息的⼤型⽂件。这些⽂件存储在Amazon S3存储桶中进⾏处理。解
决⽅案架构师必须优化⽹络架构以最⼤限度地降低数据传输成本。
A. 在 VPC 中为 Amazon S3 创建⽹关终端节点。在私有⼦⽹的路由表中，添加⽹关终端节点的条⽬。
B. 在公有⼦⽹中创建⼀个 NAT ⽹关。在私有⼦⽹的路由表中，添加⼀条指向该 NAT ⽹关的默认路由。
C. 在 VP 中为 Amazon S3 创建 AWS PrivateLink 接⼝终端节点。在私有⼦⽹的路由表中，添加接⼝终端节
点的条⽬。
D. 为每个可⽤区在公有⼦⽹中创建⼀个 NAT ⽹关。在每个私有⼦⽹的路由表中，添加⼀条指向同⼀可⽤区内
NAT ⽹关的默认路由。
https://examlearn.online
[2026/05]
Question #861
Topic 1
⼀家公司希望将其本地 MySQL 数据库迁移到 AWS。该数据库定期接收来⾃⾯向客户端应⽤程序的导⼊请求，这
会导致⼤量的写⼊操作。该公司担⼼如此⼤的流量可能会导致应⽤程序性能问题。
解决⽅案架构师应该如何在 AWS 上设计架构？
A. 为 MySQL 数据库配置⼀个 Amazon RDS 实例，并为其配备预置 IOPS 的 SSD 存储。使⽤ Amazon
CloudWatch 监控写⼊操作指标。如有必要，调整预置 IOPS。
B. 配置⼀个配备通⽤型 SSD 存储的 Amazon RDS for MySQL 数据库实例。在数据库实例前⾯部署⼀个
Amazon ElastiCache 集群。配置应⽤程序以查询 ElastiCache。
C. 配置⼀个内存优化型 Amazon DocumentDB（兼容 MongoDB）实例。监控 Amazon CloudWatch 以发现
性能相关问题。如有必要，更改实例类型。
D. 以通⽤性能模式配置 Amazon Elastic File System (Amazon EFS) ⽂件系统。监控 Amazon CloudWatch
是否存在 IOPS 瓶颈。如有必要，切换到预置吞吐量性能模式。
Question #862
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 AWS 云上运⾏⼀个应⽤程序，该应⽤程序会⽣成敏感的归档数据⽂件。该公司希望重新设计该应⽤
程序的数据存储架构。该公司希望对数据⽂件进⾏加密，并确保在数据加密并发送到 AWS 之前，第三⽅⽆法访
问这些数据。该公司已经创建了⼀个 Amazon S3 存储桶。
A. 配置 S3 存储桶以使⽤ Amazon S3 管理的加密密钥进⾏客户端加密。配置应⽤程序以使⽤ S3 存储桶存储
归档⽂件。
B. 配置 S3 存储桶以使⽤ AWS KMS 密钥进⾏服务器端加密 (SSE-KMS)。配置应⽤程序以使⽤ S3 存储桶存
储归档⽂件。
C. 配置 S3 存储桶使⽤基于 AWS KMS 密钥的双层服务器端加密 (SSE-KMS)。配置应⽤程序使⽤ S3 存储桶
来存储归档⽂件。
D. 配置应⽤程序使⽤客户端加密，密钥存储在 AWS Key Management Service (AWS KMS) 中。配置应⽤程
序将归档⽂件存储在 S3 存储桶中。
https://examlearn.online
[2026/05]
Question #863
Topic 1
⼀家公司使⽤ Amazon RDS 的默认备份设置来管理其数据库层。为了满⾜监管要求，该公司需要每天备份数据
库，并且备份数据必须保留 30 天。
哪种解决⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 编写⼀个 AWS Lambda 函数，每天创建⼀个 RDS 快照。
B. 将 RDS 数据库的⾃动备份保留期修改为 30 天。
C. 使⽤ AWS Systems Manager 维护窗⼝修改 RDS 备份保留期。
D. 每天使⽤ AWS CLI 创建⼿动快照。修改 RDS 备份保留期。
Question #864
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家在 AWS 上运⾏应⽤程序的公司使⽤ Amazon Aurora DB 集群作为其数据库。在⾼峰时段，当多个⽤户访问
和读取数据时，监控系统显示写⼊查询的数据库性能下降。该公司希望提⾼应⽤程序的可扩展性以满⾜⾼峰时段
的使⽤需求。
A. 创建第⼆个 Aurora 数据库集群。配置复制作业，将⽤户数据复制到新数据库。更新应⽤程序，使其使⽤第
⼆个数据库读取数据。
B. 在现有 Aurora 数据库集群前⾯创建⼀个 Amazon DynamoDB Accelerator (DAX) 集群。更新应⽤程序，
使其使⽤ DAX 集群执⾏只读查询。将数据直接写⼊ Aurora 数据库集群。
C. 在现有的 Aurora 数据库集群中创建 Aurora 只读副本。更新应⽤程序，使其对只读查询使⽤副本端点，对
写⼊查询使⽤集群端点。
D. 创建⼀个 Amazon Redshift 集群。将⽤户数据复制到 Redshift 集群。更新应⽤程序以连接到 Redshift 集
群并对 Redshift 集群执⾏只读查询。
https://examlearn.online
[2026/05]
Question #865
Topic 1
⼀家公司的近实时流式应⽤程序运⾏在 AWS 上。数据被摄取后，会运⾏⼀个作业来处理这些数据，该作业需要
30 分钟才能完成。由于传⼊数据量巨⼤，⼯作负载经常出现⾼延迟。解决⽅案架构师需要设计⼀个可扩展的⽆服
务器解决⽅案来提升性能。
解决⽅案架构师应该采取哪些步骤组合？（选择两项。）
A. 使⽤ Amazon Kinesis Data Firehose 摄取数据。
B. 使⽤ AWS Lambda 和 AWS Step Functions 处理数据。
C. 使⽤ AWS 数据库迁移服务 (AWS DMS) 导⼊数据。
D. 使⽤⾃动扩展组中的 Amazon EC2 实例来处理数据。
E. 使⽤ AWS Fargate 和 Amazon Elastic Container Service (Amazon ECS) 处理数据。
Question #866
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 VPC 中的多个 Amazon EC2 实例上运⾏⼀个 Web 应⽤程序。该应⽤程序需要将敏感数据写⼊
Amazon S3 存储桶。这些数据不能通过公共互联⽹发送。
A. 为 Amazon S3 创建⽹关 VPC 终端节点。在 VPC 路由表中创建到该终端节点的路由。
B. 创建⼀个以 S3 存储桶为⽬标的内部⽹络负载均衡器。
C. 在 VPC 内部署 S3 存储桶，并在 VPC 路由表中创建指向该存储桶的路由。
D. 在 VPC 和 S3 区域终端节点之间创建 AWS Direct Connect 连接。
https://examlearn.online
[2026/05]
Question #867
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏其⽣产⼯作负载，并使⽤ Amazon Elastic Block Store (Amazon EBS)
卷。解决⽅案架构师需要分析当前的 EBS 卷成本并提出优化建议。这些建议需要包含预计的每⽉节省机会。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon Inspector 报告⽣成 EBS 卷优化建议。
B. 使⽤ AWS Systems Manager 报告来确定 EBS 容量优化建议。
C. 使⽤ Amazon CloudWatch 指标报告来确定 EBS 卷优化建议。
D. 使⽤ AWS Compute Optimizer ⽣成 EBS 卷优化建议。
Question #868
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家全球性公司在 AWS 上运⾏其⼯作负载。该公司的应⽤程序使⽤跨 AWS 区域的 Amazon S3 存储桶来存储和
分析敏感数据。该公司每天在多个 S3 存储桶中存储数百万个对象。该公司希望识别所有未启⽤版本控制的 S3 存
储桶。
B. 使⽤ Amazon S3 Storage Lens 识别所有未启⽤跨区域版本控制的 S3 存储桶。
C. 启⽤ S3 的 IAM 访问分析器，以识别所有未跨区域启⽤版本控制的 S3 存储桶。
D. 创建⼀个 S3 多区域访问点，以识别所有未启⽤跨区域版本控制的 S3 存储桶。
https://examlearn.online
[2026/05]
Question #869
Topic 1
⼀家公司希望改进其部署在 AWS 上的电⼦商务订单处理应⽤程序。该应⽤程序必须确保每个订单只处理⼀次，
并且在不可预测的流量⾼峰期间不会影响客户体验。
哪种解决⽅案能够满⾜这些要求？
A. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 先进先出 (FIFO) 队列。将所有订单放⼊ SQS
队列中。配置⼀个 AWS Lambda 函数作为处理订单的⽬标。
B. 创建⼀个 Amazon Simple Notification Service (Amazon SNS) 标准主题。将所有订单发布到该 SNS 标
准主题。将应⽤程序配置为通知⽬标。
C. 使⽤ Amazon AppFlow 创建流程。将订单发送到该流程。配置 AWS Lambda 函数作为处理订单的⽬标。
D. 在应⽤程序中配置 AWS X-Ray 以跟踪订单请求。配置应⽤程序以通过从 Amazon CloudWatch 拉取订单
来处理订单。
Question #870
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司有两个 AWS 账户：⽣产账户和开发账户。该公司需要将开发账户中的代码更改推送到⽣产账户。在
Alpha 测试阶段，只有开发团队中的两位⾼级开发⼈员需要访问⽣产账户。在 Beta 测试阶段，更多开发⼈员需要
访问权限以进⾏测试。
A. 使⽤ AWS 管理控制台在每个账户中创建两份策略⽂档。将策略分配给需要访问权限的开发⼈员。
B. 在开发账户中创建⼀个 IAM ⻆⾊。授予该 IAM ⻆⾊对⽣产账户的访问权限。允许开发⼈员担任该⻆⾊。
C. 在⽣产账户中创建⼀个 IAM ⻆⾊。定义⼀个信任策略，指定开发账户。允许开发⼈员担任该⻆⾊。
D. 在⽣产账户中创建⼀个 IAM 组。将该组作为主体添加到指定⽣产账户的信任策略中。将开发⼈员添加到该
组。
https://examlearn.online
[2026/05]
Question #871
Topic 1
⼀家公司希望限制对其 Web 应⽤程序内容的访问。该公司需要使⽤ AWS 上提供的授权技术来保护内容。此外，
该公司还希望实现低登录延迟的⽆服务器架构，⽤于授权和身份验证。
该解决⽅案必须与 Web 应⽤程序集成，并能在全球范围内提供 Web 内容。该应⽤程序⽬前⽤户群较⼩，但该公
司预计⽤户群将会增⻓。
哪种解决⽅案能够满⾜这些要求？
A. 配置 Amazon Cognito 进⾏身份验证。实现 Lambda@Edge 进⾏授权。配置 Amazon CloudFront 以在全
球范围内提供 Web 应⽤程序服务。
B. 配置 AWS Directory Service 以对 Microsoft Active Directory 进⾏身份验证。部署 AWS Lambda 以进⾏
授权。使⽤应⽤程序负载均衡器在全球范围内提供 Web 应⽤程序服务。
C. 配置 Amazon Cognito 进⾏身份验证。部署 AWS Lambda 进⾏授权。使⽤ Amazon S3 Transfer
Acceleration 在全球范围内部署 Web 应⽤程序。
D. 配置 AWS Directory Service 以⽀持 Microsoft Active Directory 进⾏身份验证。部署 Lambda@Edge 进
⾏授权。使⽤ AWS Elastic Beanstalk 在全球范围内部署 Web 应⽤程序。
Question #872
Topic 1
⼀个开发团队使⽤多个 AWS 账户来构建其开发、测试和⽣产环境。团队成员⼀直在启动⼀些利⽤率不⾜的⼤型
Amazon EC2 实例。解决⽅案架构师必须阻⽌在所有账户中启动⼤型实例。
解决⽅案架构师如何才能以最⼩的运维开销满⾜这⼀要求？
A. 更新 IAM 策略，禁⽌启动⼤型 EC2 实例。将这些策略应⽤于所有⽤户。
B. 在 AWS Resource Access Manager 中定义⼀个资源，以防⽌启动⼤型 EC2 实例。
C. 在每个账户中创建⼀个 IAM ⻆⾊，禁⽌启动⼤型 EC2 实例。授予开发⼈员 IAM 组对该⻆⾊的访问权限。
D. 在管理账户的 AWS Organizations 中创建⼀个组织，并使⽤默认策略。创建⼀个服务控制策略 (SCP)，禁
⽌启动⼤型 EC2 实例，并将其应⽤于 AWS 账户。
https://examlearn.online
[2026/05]
Question #873
Topic 1
⼀家公司已将数百台本地虚拟机 (VM) 迁移到 Amazon EC2 实例。这些实例运⾏着各种 Windows Server 版本以
及多个 Linux 发⾏版。该公司希望找到⼀种解决⽅案，能够⾃动清点和更新操作系统。此外，该公司还需要⼀份
每个实例常⻅漏洞的汇总报告，以便进⾏定期的⽉度审查。
解决⽅案架构师应该推荐什么⽅案来满⾜这些需求？
A. 设置 AWS Systems Manager Patch Manager 来管理所有 EC2 实例。配置 AWS Security Hub 以⽣成⽉
度报告。
B. 设置 AWS Systems Manager Patch Manager 来管理所有 EC2 实例。部署 Amazon Inspector，并配置
⽉度报告。
C. 设置 AWS Shield Advanced，并配置⽉度报告。部署 AWS Config 以⾃动在 EC2 实例上安装补丁。
D. 在账户中设置 Amazon GuardDuty 以监控所有 EC2 实例。部署 AWS Config 以⾃动安装 EC2 实例上的补
丁程序。
Question #874
哪种解决⽅案能够以最短的停机时间满⾜这些要求？
备区域的 ELB。
Topic 1
⼀家公司将其应⽤程序托管在 AWS 云上。该应⽤程序运⾏在 Amazon EC2 实例上，这些实例位于⾃动扩展组
(Auto Scaling group) 中，并由弹性负载均衡器 (ELB) 负载均衡器管理。该应⽤程序连接到 Amazon DynamoDB
表。
为了实现灾难恢复 (DR)，该公司希望确保该应⽤程序能够从另⼀个 AWS 区域访问，并且停机时间最短。
A. 在灾备区域中创建⾃动伸缩组和 ELB。将 DynamoDB 表配置为全局表。配置 DNS 故障转移以指向新的灾
B. 创建⼀个 AWS CloudFormation 模板，⽤于创建 EC2 实例、ELB 和 DynamoDB 表，以便在需要时启
动。配置 DNS 故障转移，使其指向新的灾备区域的 ELB。
C. 创建⼀个 AWS CloudFormation 模板，⽤于创建 EC2 实例和 ELB，以便在需要时启动。将 DynamoDB
表配置为全局表。配置 DNS 故障转移，使其指向新的灾备区域的 ELB。
D. 在灾备区域中创建⾃动扩展组和 ELB。将 DynamoDB 表配置为全局表。创建⼀个评估周期为 10 分钟的
Amazon CloudWatch 警报，以调⽤ AWS Lambda 函数，该函数更新 Amazon Route 53 以指向灾备区域的
ELB。
https://examlearn.online
[2026/05]
Question #875
Topic 1
⼀家公司在私有⼦⽹中的 Amazon EC2 实例上运⾏⼀个应⽤程序。该应⽤程序需要在 Amazon S3 存储桶中存储
和检索数据。根据监管要求，数据不得通过公共互联⽹传输。
解决⽅案架构师应该如何以最具成本效益的⽅式满⾜这些要求？
A. 部署 NAT ⽹关以访问 S3 存储桶。
B. 部署 AWS Storage Gateway 以访问 S3 存储桶。
C. 部署 S3 接⼝端点以访问 S3 存储桶。
D. 部署 S3 ⽹关端点以访问 S3 存储桶。
Question #876
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
B. 在 EC2 实例前⾯配置⽹络负载均衡器。
HTTPS 流量。
Topic 1
⼀家公司在运⾏于同⼀可⽤区的 Amazon EC2 实例上托管了⼀个应⽤程序。该应⽤程序可通过开放系统互连
(OSI) 模型的传输层访问。该公司需要该应⽤程序架构具备⾼可⽤性。
A. 在不同的可⽤区配置新的 EC2 实例。使⽤ Amazon Route 53 将流量路由到所有实例。
C. 为实例配置⽹络负载均衡器，⽤于处理 TCP 流量。为实例配置应⽤负载均衡器，⽤于处理 HTTP 和
D. 为 EC2 实例创建⾃动扩展组。配置⾃动扩展组以使⽤多个可⽤区。配置⾃动扩展组以对实例运⾏应⽤程序
运⾏状况检查。
E. 创建 Amazon CloudWatch 警报。配置该警报，以便在 EC2 实例状态变为停⽌状态时重新启动它们。
https://examlearn.online
[2026/05]
Question #877
Topic 1
⼀家公司使⽤ Amazon S3 托管其静态⽹站。该公司希望在⽹⻚上添加⼀个联系表单。该联系表单将包含动态服
务器端组件，供⽤户输⼊姓名、电⼦邮件地址、电话号码和留⾔。
该公司预计每⽉⽹站访问量少于 100 次。当客户填写表单时，联系表单必须通过电⼦邮件通知该公司。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将动态联系表单托管在 Amazon Elastic Container Service (Amazon ECS) 中。设置 Amazon Simple
Email Service (Amazon SES) 以连接到第三⽅电⼦邮件提供商。
B. 创建⼀个 Amazon API Gateway 端点，该端点从 AWS Lambda 函数返回联系表单。在 API Gateway 上配
置另⼀个 Lambda 函数，以向 Amazon Simple Notification Service (Amazon SNS) 主题发布消息。
C. 使⽤ AWS Amplify Hosting 托管⽹站，⽤于静态内容和动态内容。使⽤服务器端脚本构建联系表单。配置
Amazon Simple Queue Service (Amazon SQS) 将消息传递给公司。
D. 将⽹站从 Amazon S3 迁移到运⾏ Windows Server 的 Amazon EC2 实例。使⽤ Windows Server 版
Internet 信息服务 (IIS) 托管⽹⻚。使⽤客户端脚本构建联系表单。将表单与 Amazon WorkMail 集成。
Question #878
哪种解决⽅案能够最安全地满⾜这些要求？
Topic 1
⼀家公司在 AWS Organizations 中为其业务部⻔创建了专⽤的 AWS 账户。最近，⼀条重要通知被发送到了某个
业务部⻔账户的根⽤户邮箱，⽽不是指定的账户所有者邮箱。该公司希望确保今后所有通知都能根据账单、运营
或安全等通知类别发送给不同的员⼯。
A. 将每个 AWS 账户配置为使⽤公司管理的单个电⼦邮件地址。确保所有账户所有者都能访问该电⼦邮件账户
以接收通知。为每个 AWS 账户配置备⽤联系⼈，并为每个业务部⻔的计费团队、安全团队和运维团队创建相
应的通讯组列表。
B. 为每个 AWS 账户配置不同的电⼦邮件分发列表，每个账户对应公司管理的⼀个业务部⻔。在每个分发列表
中配置管理员电⼦邮件地址，以便他们能够响应警报。为每个 AWS 账户配置备⽤联系⼈，并为每个业务部⻔
的计费团队、安全团队和运维团队配置相应的分发列表。
C. 将每个 AWS 账户的根⽤户电⼦邮件地址配置为每个业务部⻔中⼀名员⼯的个⼈公司管理电⼦邮件地址。为
每个 AWS 账户配置备⽤联系⼈，并为每个业务部⻔的计费团队、安全团队和运维团队创建相应的通讯组列
表。
D. 配置每个 AWS 账户根⽤户使⽤发送到集中式邮箱的电⼦邮件别名。为每个账户配置备⽤联系⼈，分别使⽤
⼀个企业管理的电⼦邮件分发列表，供计费团队、安全团队和运维团队使⽤。
https://examlearn.online
[2026/05]
Question #879
Topic 1
⼀家公司在 AWS 上运⾏电⼦商务应⽤程序。Amazon EC2 实例处理购买交易并将购买详情存储在 Amazon
Aurora PostgreSQL 数据库集群中。
⾼峰时段，客户会遇到应⽤程序超时问题。解决⽅案架构师需要重新设计应⽤程序架构，使其能够扩展以满⾜⾼
峰时段的使⽤需求。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 配置⼀组新的 EC2 实例的⾃动扩展组，以重试购买操作直⾄处理完成。更新应⽤程序，使其使⽤ Amazon
RDS 代理连接到数据库集群。
B. 配置应⽤程序以在 Aurora PostgreSQL 数据库集群前⾯使⽤ Amazon ElastiCache 集群。
C. 更新应⽤程序，将采购请求发送到 Amazon Simple Queue Service (Amazon SQS) 队列。配置⼀个⾃动
扩展组，该组包含从 SQS 队列读取数据的新 EC2 实例。
D. 配置 AWS Lambda 函数，重试购票，直到处理完成。
E. 配置 Amazon AP! Gateway REST API 并设置使⽤计划。
Question #880
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家使⽤ AWS Organizations 的公司在 30 个不同的 AWS 账户中运⾏着 150 个应⽤程序。该公司使⽤ AWS
Cost and Usage Report 在管理账户中创建了⼀个新报告。该报告被发送到 Amazon S3 存储桶，该存储桶⼜被
复制到数据收集账户中的⼀个存储桶。
该公司的⾼层领导希望查看⼀个⾃定义仪表板，该仪表板从本⽉初开始每天提供 NAT ⽹关成本。
A. 分享包含所需表格可视化效果的 Amazon QuickSight 控制⾯板。配置 QuickSight 使⽤ AWS DataSync
查询新报表。
B. 共享包含所需表格可视化的 Amazon QuickSight 控制⾯板。配置 QuickSight 以使⽤ Amazon Athena 查
询新报表。
C. 共享包含所需表格可视化的 Amazon CloudWatch 控制⾯板。配置 CloudWatch 使⽤ AWS DataSync 查
询新报表。
D. 共享包含所需表格可视化的 Amazon CloudWatch 控制⾯板。配置 CloudWatch 使⽤ Amazon Athena 查
询新报表。
https://examlearn.online
[2026/05]
Question #881
Topic 1
⼀家公司在 Amazon S3 上托管了⼀个⾼流量的静态⽹站，该⽹站使⽤ Amazon CloudFront 分发，默认 TTL 为
0 秒。该公司希望实施缓存来提升⽹站性能。但是，该公司也希望确保过期内容在部署后⼏分钟内不会再次出
现。
解决⽅案架构师应该实施哪些缓存⽅法的组合来满⾜这些要求？（选择两种。）
A. 将 CloudFront 默认 TTL 设置为 2 分钟。
B. 将 S3 存储桶的默认 TTL 设置为 2 分钟。
C. 向 Amazon S3 中的对象添加 Cache-Control 私有指令。
D. 创建⼀个 AWS Lambda@Edge 函数，⽤于向 HTTP 响应添加 Expires 标头。配置该函数以在查看器响应
时运⾏。
E. 为 Amazon S3 中的对象添加 Cache-Control max-age 指令，设置为 24 ⼩时。部署时，创建
CloudFront 失效操作，以清除边缘缓存中所有已更改的⽂件。
Question #882
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司使⽤ Amazon EC2 实例和 AWS Lambda 函数运⾏其应⽤程序。EC2 实例运⾏在 VPC 的私有⼦⽹中。
Lambda 函数需要直接访问 EC2 实例的⽹络才能使应⽤程序正常运⾏。
该应⽤程序将运⾏⼀年。在这⼀年期间，应⽤程序使⽤的 Lambda 函数数量将会增加。该公司必须最⼤限度地降
低所有应⽤程序资源的成本。
A. 购买 EC2 实例节省计划。将 Lambda 函数连接到包含 EC2 实例的私有⼦⽹。
B. 购买 EC2 实例节省计划。将 Lambda 函数连接到 EC2 实例运⾏所在的同⼀ VPC 中的新公共⼦⽹。
C. 购买计算节省计划。将 Lambda 函数连接到包含 EC2 实例的私有⼦⽹。
D. 购买计算节省计划。将 Lambda 函数保留在 Lambda 服务 VPC 中。
https://examlearn.online
[2026/05]
Question #883
Topic 1
⼀家公司使⽤ AWS Control Tower 在 AWS 上部署了多账户策略。该公司为每位开发⼈员分配了独⽴的 AWS 账
户。该公司希望实施控制措施，以限制开发⼈员产⽣的 AWS 资源成本。
哪种解决⽅案能够以最低的运营开销满⾜这些要求？
A. 指示每位开发⼈员为其所有资源添加⼀个标签，该标签的键为 CostCenter，值为开发⼈员的姓名。使⽤
AWS Config 托管规则 required-tags 检查该标签是否存在。创建⼀个 AWS Lambda 函数来终⽌未添加该标
签的资源。配置 AWS Cost Explorer，使其每⽇向每位开发⼈员发送报告，以便监控其⽀出情况。
B. 使⽤ AWS Budgets 为每个开发⼈员账户设置预算。设置实际值和预测值的预算警报，以便在开发⼈员超
出或预计超出其分配的预算时通知他们。使⽤ AWS Budgets 操作将 DenyAll 策略应⽤于开发⼈员的 IAM ⻆
⾊，以防⽌在达到分配的预算时启动额外的资源。
C. 使⽤ AWS Cost Explorer 监控并报告每个开发⼈员账户的成本。配置 Cost Explorer 向每位开发⼈员发送
每⽇报告，以便他们监控⽀出。使⽤ AWS Cost Anomaly Detection 检测异常⽀出并提供警报。
D. 使⽤ AWS Service Catalog 允许开发⼈员在限定的成本范围内启动资源。在每个 AWS 账户中创建 AWS
Lambda 函数，以便在每个⼯作⽇结束时停⽌运⾏资源。配置 Lambda 函数，使其在每个⼯作⽇开始时恢复
运⾏资源。
Question #884
Topic 1
⼀位解决⽅案架构师正在设计⼀个三层 Web 应⽤程序。该架构包含⼀个⾯向互联⽹的应⽤程序负载均衡器 (ALB)
和⼀个 Web 层，Web 层托管在私有⼦⽹的 Amazon EC2 实例上。包含业务逻辑的应⽤程序层也运⾏在私有⼦⽹
的 EC2 实例上。数据库层由运⾏在私有⼦⽹ EC2 实例上的 Microsoft SQL Server 组成。安全性是公司的⾸要任
务。
解决⽅案架构师应该使⽤哪些安全组配置组合？（选择三个。）
A. 配置 Web 层的安全组，允许来⾃ ALB 安全组的⼊站 HTTPS 流量。
B. 配置 Web 层的安全组，允许出站 HTTPS 流量到 0.0.0.0/0。
C. 配置数据库层的安全组，允许来⾃应⽤程序层安全组的⼊站 Microsoft SQL Server 流量。
D. 配置数据库层的安全组，允许出站 HTTPS 流量和 Microsoft SQL Server 流量访问 Web 层的安全组。
E. 配置应⽤层的安全组，允许来⾃ Web 层安全组的⼊站 HTTPS 流量。
F. 配置应⽤程序层的安全组，允许出站 HTTPS 流量和 Microsoft SQL Server 流量访问 Web 层的安全组。
https://examlearn.online
[2026/05]
Question #885
Topic 1
⼀家公司发布了其⽣产应⽤程序的新版本。该公司的⼯作负载使⽤了 Amazon EC2、AWS Lambda、AWS
Fargate 和 Amazon SageMaker。
现在使⽤量已趋于稳定，该公司希望优化⼯作负载的成本。该公司希望⽤最少的节省⽅案覆盖最多的服务。
以下哪种节省⽅案组合能够满⾜这些要求？（选择两项。）
A. 为 Amazon EC2 和 SageMaker 购买 EC2 实例节省计划。
B. 为 Amazon EC2、Lambda 和 SageMaker 购买计算节省计划。
C. 购买 SageMaker 储蓄计划。
D. 为 Lambda、Fargate 和 Amazon EC2 购买计算节省计划。
E. 购买适⽤于 Amazon EC2 和 Fargate 的 EC2 实例节省计划。
Question #886
以下哪两项步骤组合能够满⾜这些要求？
Topic 1
⼀家公司使⽤ Microsoft SQL Server 数据库，其应⽤程序均连接到该数据库。该公司希望在尽量减少应⽤程序代
码更改的情况下，将数据库迁移到 Amazon Aurora PostgreSQL 数据库。
A. 使⽤ AWS Schema Conversion Tool (AWS SCT) 重写应⽤程序中的 SQL 查询。
B. 在 Aurora PostgreSQL 上启⽤ Babelfish，以运⾏来⾃应⽤程序的 SQL 查询。
C. 使⽤ AWS Schema Conversion Tool (AWS SCT) 和 AWS Database Migration Service (AWS DMS) 迁移
数据库架构和数据。
D. 使⽤ Amazon RDS Proxy 将应⽤程序连接到 Aurora PostgreSQL。
E. 使⽤ AWS 数据库迁移服务 (AWS DMS) 重写应⽤程序中的 SQL 查询。
https://examlearn.online
[2026/05]
Question #887
Topic 1
⼀家公司计划将⼀个应⽤程序迁移到使⽤ Amazon Elastic Block Store (Amazon EBS) 作为附加存储的 Amazon
EC2 实例上。
解决⽅案架构师必须设计⼀个解决⽅案，以确保所有新建的 Amazon EBS 卷默认加密。该解决⽅案还必须防⽌创
建未加密的 EBS 卷。
哪个解决⽅案能够满⾜这些要求？
A. 配置 EC2 帐户属性，使其始终加密新的 EBS 卷。
B. 使⽤ AWS Config。配置加密卷标识符。应⽤默认的 AWS Key Management Service (AWS KMS) 密钥。
C. 配置 AWS Systems Manager 以创建 EBS 卷的加密副本。重新配置 EC2 实例以使⽤加密卷。
D. 在 AWS Key Management Service (AWS KMS) 中创建客户管理的密钥。配置 AWS Migration Hub，以
便在公司迁移⼯作负载时使⽤该密钥。
Question #888
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家电商公司希望收集其⽹站的⽤户点击流数据，以便进⾏实时分析。该⽹站的流量全天波动较⼤。该公司需要
⼀个可扩展的解决⽅案，能够适应不同的流量⽔平。
A. 使⽤ Amazon Kinesis Data Streams 的按需模式数据流来捕获点击流数据。使⽤ AWS Lambda 实时处理
数据。
B. 使⽤ Amazon Kinesis Data Firehose 捕获点击流数据。使⽤ AWS Glue 实时处理数据。
C. 使⽤ Amazon Kinesis Video Streams 捕获点击流数据。使⽤ AWS Glue 实时处理数据。
D. 使⽤ Amazon Managed Service for Apache Flink（以前称为 Amazon Kinesis Data Analytics）捕获点
击流数据。使⽤ AWS Lambda 实时处理数据。
https://examlearn.online
[2026/05]
Question #889
Topic 1
⼀家全球性公司在 AWS 上运⾏其⼯作负载。该公司的应⽤程序使⽤跨 AWS 区域的 Amazon S3 存储桶来存储和
分析敏感数据。该公司每天在多个 S3 存储桶中存储数百万个对象。该公司希望识别所有未启⽤版本控制的 S3 存
储桶。
哪种解决⽅案能够满⾜这些要求？
A. 设置⼀个 AWS CloudTrail 事件，该事件包含⼀条规则，⽤于识别所有未启⽤跨区域版本控制的 S3 存储
桶。
B. 使⽤ Amazon S3 Storage Lens 识别所有未启⽤跨区域版本控制的 S3 存储桶。
C. 启⽤ S3 的 IAM 访问分析器，以识别所有未跨区域启⽤版本控制的 S3 存储桶。
D. 创建⼀个 S3 多区域访问点，以识别所有未启⽤跨区域版本控制的 S3 存储桶。
Question #890
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
对象创建 4 年后删除⽂件。
Topic 1
⼀家公司需要优化其 Amazon S3 存储成本，以存储⼀个会⽣成⼤量⽆法重新创建的⽂件的应⽤程序。每个⽂件
⼤⼩约为 5 MB，存储在 Amazon S3 标准存储中。
该公司必须将这些⽂件存储 4 年才能删除。这些⽂件必须能够⽴即访问。在⽂件创建的前 30 天内，访问频率很
⾼，但 30 天后访问频率很低。
A. 创建 S3 ⽣命周期策略，在对象创建 30 天后将⽂件移动到 S3 Glacier 即时检索。在对象创建 4 年后删除
⽂件。
B. 创建 S3 ⽣命周期策略，在对象创建 30 天后将⽂件移动到 S3 单区域不频繁访问 (S3 One Zone-IA)。在
C. 创建 S3 ⽣命周期策略，在对象创建 30 天后将⽂件移动到 S3 标准-不频繁访问 (S3 Standard-IA)。在对
象创建 4 年后删除⽂件。
D. 创建 S3 ⽣命周期策略，在对象创建 30 天后将⽂件移⾄ S3 标准-不频繁访问 (S3 Standard-IA)。在对象
创建 4 年后将⽂件移⾄ S3 Glacier 灵活检索。
https://examlearn.online
[2026/05]
Question #891
Topic 1
A company runs its critical storage application in the AWS Cloud. The application uses Amazon S3 in two
AWS Regions. The company wants the application to send remote user data to the nearest S3 bucket with
no public network congestion. The company also wants the application to fail over with the least amount
of management of Amazon S3.
Which solution will meet these requirements?
A. Implement an active-active design between the two Regions. Configure the application to use the
regional S3 endpoints closest to the user.
B. Use an active-passive configuration with S3 Multi-Region Access Points. Create a global endpoint
for each of the Regions.
C. Send user data to the regional S3 endpoints closest to the user. Configure an S3 cross-account
replication rule to keep the S3 buckets synchronized.
D. Set up Amazon S3 to use Multi-Region Access Points in an active-active configuration with a single
global endpoint. Configure S3 Cross-Region Replication.
Question #892
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在将其数据中⼼从本地迁移到 AWS。该公司有多个传统应⽤程序，这些应⽤程序托管在独⽴的虚拟服
务器上。这些应⽤程序的设计⽆法更改。
⽬前，每个虚拟服务器都作为独⽴的 EC2 实例运⾏。解决⽅案架构师需要确保应⽤程序在迁移到 AWS 后仍然可
靠且具有容错能⼒。这些应⽤程序将在 Amazon EC2 实例上运⾏。
A. 创建⼀个包含最少⼀个实例且最多⼀个实例的⾃动扩展组。为每个应⽤程序实例创建⼀个 Amazon 系统映
像 (AMI)。使⽤该 AMI 在⾃动扩展组中创建 EC2 实例。在⾃动扩展组前端配置应⽤程序负载均衡器。
B. 使⽤ AWS Backup 为托管每个应⽤程序的 EC2 实例创建每⼩时备份。将备份存储在 Amazon S3 的单独
可⽤区中。配置灾难恢复流程，以便从每个应⽤程序的最新备份还原 EC2 实例。
C. 为每个应⽤程序实例创建 Amazon 系统映像 (AMI)。从 AMI 启动两个新的 EC2 实例。将每个 EC2 实例放
置在不同的可⽤区中。配置⼀个⽹络负载均衡器，并将这些 EC2 实例作为⽬标。
D. 使⽤ AWS Mitigation Hub 重构空间将每个应⽤程序从 EC2 实例迁移出去。将每个应⽤程序的功能分解为
单独的组件。将每个应⽤程序托管在 Amazon Elastic Container Service (Amazon ECS) 上，并使⽤ AWS
Fargate 启动类型。
https://examlearn.online
[2026/05]
Question #893
Topic 1
⼀家公司希望通过为每个⼯作负载创建⼀个 AWS 账户来隔离其⼯作负载。该公司需要⼀个能够集中管理⼯作负
载⽹络组件的解决⽅案。该解决⽅案还必须创建具有⾃动安全控制（防护措施）的账户。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ AWS Control Tower 部署账户。创建⼀个包含私有⼦⽹和公有⼦⽹的 VPC 的⽹络账户。使⽤ AWS
Resource Access Manager (AWS RAM) 将这些⼦⽹共享给⼯作负载账户。
B. 使⽤ AWS Organizations 部署账户。创建⼀个⽹络账户，该账户包含⼀个 VPC，其中包含私有⼦⽹和公有
⼦⽹。使⽤ AWS Resource Access Manager (AWS RAM) 将这些⼦⽹共享给⼯作负载账户。
C. 使⽤ AWS Control Tower 部署账户。在每个⼯作负载账户中部署⼀个 VPC。配置每个 VPC，使其通过传
输⽹关附件将流量路由到检查 VPC。
D. 使⽤ AWS Organizations 部署账户。在每个⼯作负载账户中部署⼀个 VPC。配置每个 VPC，使其通过传
输⽹关附件将流量路由到检查 VPC。
Question #894
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2 实例上托管⽹站。该⽹站提供静态内容。⽹站流量
不断增⻓。该公司希望最⼤限度地降低⽹站托管成本。
A. 将⽹站迁移到 Amazon S3 存储桶。为该 S3 存储桶配置 Amazon CloudFront 分发。
B. 将⽹站迁移到 Amazon S3 存储桶。为该 S3 存储桶配置 Amazon ElastiCache 集群。
C. 将⽹站迁移到 AWS Amplify。配置 ALB 以解析到 Amplify ⽹站。
D. 将⽹站迁移到 AWS Amplify。配置 EC2 实例以缓存⽹站。
https://examlearn.online
[2026/05]
Question #895
Topic 1
⼀家公司正在为其托管在 AWS 上的媒体应⽤程序实施共享存储解决⽅案。该公司需要能够使⽤ SMB 客户端访问
存储的数据。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 创建 AWS Storage Gateway 卷⽹关。创建使⽤所需客户端协议的⽂件共享。将应⽤程序服务器连接到该
⽂件共享。
B. 创建 AWS Storage Gateway 磁带⽹关。配置磁带以使⽤ Amazon S3。将应⽤程序服务器连接到磁带⽹
关。
C. 创建⼀个 Amazon EC2 Windows 实例。在该实例上安装并配置 Windows ⽂件共享⻆⾊。将应⽤程序服
务器连接到该⽂件共享。
D. 创建 Amazon FSx for Windows ⽂件服务器⽂件系统。将应⽤程序服务器连接到该⽂件系统。
Question #896
Topic 1
⼀家公司正在为其⽣产应⽤程序设计灾难恢复 (DR) 策略。该应⽤程序由位于美国东部 1 区 Amazon Aurora 集群
上的 MySQL 数据库提供⽀持。该公司已选择美国⻄部 1 区作为其灾难恢复区域。
该公司的⽬标恢复点⽬标 (RPO) 为 5 分钟，⽬标恢复时间⽬标 (RTO) 为 20 分钟。该公司希望最⼤限度地减少配
置更改。
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
A. 在 us-west-1 创建⼀个⼤⼩与⽣产应⽤程序的 Aurora MySQL 集群写⼊实例类似的 Aurora 只读副本。
B. 将 Aurora 集群转换为 Aurora 全局数据库。配置托管故障转移。
C. 在 us-west-1 中创建⼀个具有跨区域复制功能的新 Aurora 集群。
D. 在 us-west-1 创建⼀个新的 Aurora 集群。使⽤ AWS 数据库迁移服务 (AWS DMS) 同步两个集群。
https://examlearn.online
[2026/05]
Question #897
Topic 1
⼀家公司每周都会在⼯作周的第⼀天之前运⾏⼀项关键的数据分析任务。该任务⾄少需要 1 ⼩时才能完成分析。
该任务是有状态的，不能容忍任何中断。该公司需要⼀个解决⽅案在 AWS 上运⾏该任务。
哪个解决⽅案能够满⾜这些要求？
A. 为作业创建⼀个容器。使⽤ Amazon EventBridge Scheduler 将作业调度为在 Amazon Elastic Container
Service (Amazon ECS) 集群上作为 AWS Fargate 任务运⾏。
B. 配置作业以在 AWS Lambda 函数中运⾏。在 Amazon EventBridge 中创建计划规则以调⽤ Lambda 函
数。
C. 配置⼀个运⾏ Amazon Linux 的 Amazon EC2 Spot 实例的⾃动扩展组。在这些实例上配置⼀个 crontab
条⽬来运⾏分析。
D. 配置 AWS DataSync 任务来运⾏该作业。配置 cron 表达式以按计划运⾏该任务。
Question #898
Topic 1
⼀家公司在 AWS 云上运⾏⼯作负载。该公司希望集中收集安全数据，以评估整个公司的安全性并改进⼯作负载
保护。
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
A. 在 AWS Lake Formation 中配置数据湖。使⽤ AWS Glue 爬⾍将安全数据提取到数据湖中。
B. 配置 AWS Lambda 函数以收集 .csv 格式的安全数据。将数据上传到 Amazon S3 存储桶。
C. 在 Amazon Security Lake 中配置数据湖以收集安全数据。将数据上传到 Amazon S3 存储桶。
D. 配置 AWS 数据库迁移服务 (AWS DMS) 复制实例，将安全数据加载到 Amazon RDS 集群中。
https://examlearn.online
[2026/05]
Question #899
Topic 1
⼀家公司正在将五个本地应⽤程序迁移到 AWS 云中的 VPC。每个应⽤程序⽬前都部署在本地的独⽴虚拟⽹络
中，并且需要在 AWS 云中以类似的⽅式部署。这些应⽤程序需要访问共享服务 VPC。所有应⽤程序必须能够相
互通信。
如果迁移成功，该公司将对超过 100 个应⽤程序重复此迁移过程。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 在应⽤ VPC 和共享服务 VPC 之间部署软件 VPN 隧道。在应⽤ VPC 的⼦⽹中，向共享服务 VPC 添加路
由。
B. 在应⽤ VPC 和共享服务 VPC 之间部署 VPC 对等连接。通过对等连接，在应⽤ VPC 的⼦⽹中向共享服务
VPC 添加路由。
C. 在应⽤程序 VPC 和共享服务 VPC 之间部署 AWS Direct Connect 连接。在应⽤程序 VPC 的⼦⽹中，向
共享服务 VPC 和应⽤程序 VPC 添加路由。在共享服务 VPC 的⼦⽹中，向应⽤程序 VPC 添加路由。
D. 部署⼀个传输⽹关，并将该传输⽹关与应⽤程序 VPC 和共享服务 VPC 关联起来。在应⽤程序 VPC 的⼦⽹
中，以及通过该传输⽹关将应⽤程序 VPC 路由到共享服务 VPC。
Question #900
以下哪两项操作组合可以满⾜这些要求？（选择两项。）
Anywhere 外部启动类型。
Topic 1
⼀家公司希望使⽤ Amazon Elastic Container Service (Amazon ECS) 在混合环境中运⾏其本地应⽤程序。该应
⽤程序⽬前运⾏在本地容器中。
该公司需要⼀个能够在本地、混合或云环境中扩展的单⼀容器解决⽅案。该公司必须在 AWS 云中运⾏新的应⽤
程序容器，并且必须使⽤负载均衡器来处理 HTTP 流量。
A. 设置⼀个 ECS 集群，云应⽤程序容器使⽤ AWS Fargate 启动类型。本地应⽤程序容器使⽤ Amazon ECS
B. 为云 ECS 服务设置应⽤程序负载均衡器。
C. 为云 ECS 服务设置⽹络负载均衡器。
D. 设置⼀个使⽤ AWS Fargate 启动类型的 ECS 集群。Fargate ⽤于云应⽤程序容器和本地应⽤程序容器。
E. 设置⼀个 ECS 集群，该集群使⽤ Amazon EC2 启动类型来运⾏云应⽤程序容器。对于本地应⽤程序容
器，则使⽤ Amazon ECS Anywhere，并采⽤ AWS Fargate 启动类型。
https://examlearn.online
[2026/05]
Question #901
Topic 1
A company is migrating its workloads to AWS. The company has sensitive and critical data in on-premises
relational databases that run on SQL Server instances.
The company wants to use the AWS Cloud to increase security and reduce operational overhead for the
databases.
Which solution will meet these requirements?
A. Migrate the databases to Amazon EC2 instances. Use an AWS Key Management Service (AWS KMS)
AWS managed key for encryption.
B. Migrate the databases to a Multi-AZ Amazon RDS for SQL Server DB instance. Use an AWS Key
Management Service (AWS KMS) AWS managed key for encryption.
C. Migrate the data to an Amazon S3 bucket. Use Amazon Macie to ensure data security.
D. Migrate the databases to an Amazon DynamoDB table. Use Amazon CloudWatch Logs to ensure
data security.
Question #902
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望将应⽤程序迁移到 AWS。该公司希望提⾼应⽤程序的当前可⽤性。该公司希望在应⽤程序架构中使
⽤ AWS WAF。
A. 创建⼀个包含多个 Amazon EC2 实例的⾃动扩展组，这些实例跨两个可⽤区托管应⽤程序。配置应⽤程序
负载均衡器 (ALB)，并将该⾃动扩展组设置为⽬标。将 Web 应⽤防⽕墙 (WAF) 连接到 ALB。
B. 创建⼀个包含多个托管应⽤程序的 Amazon EC2 实例的集群放置组。配置应⽤程序负载均衡器，并将这些
EC2 实例设置为⽬标。将 Web 应⽤防⽕墙 (WAF) 连接到该放置组。
C. 创建两个 Amazon EC2 实例，分别位于两个可⽤区，⽤于托管应⽤程序。将这两个 EC2 实例配置为应⽤
程序负载均衡器 (ALB) 的⽬标。将 Web 应⽤防⽕墙 (WAF) 连接到 ALB。
D. 创建⼀个包含多个 Amazon EC2 实例的⾃动扩展组，这些实例跨两个可⽤区托管应⽤程序。配置应⽤程序
负载均衡器 (ALB) 并将该⾃动扩展组设置为⽬标。将 Web 应⽤防⽕墙 (WAF) 连接到该⾃动扩展组。
https://examlearn.online
[2026/05]
Question #903
Topic 1
⼀家公司在 Amazon S3 存储桶中管理⼀个数据湖，众多应⽤程序可以访问该数据湖。每个应⽤程序都有⼀个唯
⼀的 S3 存储桶前缀。该公司希望将每个应⽤程序的访问权限限制在其特定的前缀范围内，并对每个前缀下的对
象进⾏精细控制。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为每个应⽤程序创建专⽤的 S3 接⼊点和接⼊点策略。
B. 创建⼀个 S3 批量操作作业，为 S3 存储桶中的每个对象设置 ACL 权限。
C. 将 S3 存储桶中的对象复制到每个应⽤程序的新 S3 存储桶中。按前缀创建复制规则。
D. 将 S3 存储桶中的对象复制到每个应⽤程序的新 S3 存储桶中。为每个应⽤程序创建专⽤的 S3 访问点。
Question #904
解决⽅案架构师需要修改该应⽤程序，使其在图像上传时⽴即进⾏处理。
哪种修改⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司有⼀个应⽤程序，客户可以使⽤该程序将图像上传到 Amazon S3 存储桶。每天晚上，该公司都会启动
⼀个 Amazon EC2 Spot 实例队列来处理当天收到的所有图像。处理每张图像需要 2 分钟，并占⽤ 512 MB 内
存。
A. 使⽤ S3 事件通知将包含图像详细信息的消息写⼊ Amazon Simple Queue Service (Amazon SQS) 队
列。配置 AWS Lambda 函数从队列中读取消息并处理图像。
B. 使⽤ S3 事件通知将包含图像详细信息的消息写⼊ Amazon Simple Queue Service (Amazon SQS) 队列。
配置 EC2 预留实例以从队列中读取消息并处理图像。
C. 使⽤ S3 事件通知将包含图像详细信息的消息发布到 Amazon Simple Notification Service (Amazon
SNS) 主题。在 Amazon Elastic Container Service (Amazon ECS) 中配置容器实例以订阅该主题并处理图
像。
D. 使⽤ S3 事件通知将包含图像详细信息的消息发布到 Amazon Simple Notification Service (Amazon
SNS) 主题。配置 AWS Elastic Beanstalk 应⽤程序以订阅该主题并处理图像。
https://examlearn.online
[2026/05]
Question #905
Topic 1
⼀家公司希望提⾼其混合应⽤程序的可⽤性和性能。该应⽤程序包含⼀个基于 TCP 的有状态⼯作负载（托管在不
同 AWS 区域的 Amazon EC2 实例上）和⼀个基于 UDP 的⽆状态⼯作负载（托管在公司内部）。
解决⽅案架构师应采取哪些措施组合来提⾼可⽤性和性能？（选择两项。）
A. 使⽤ AWS Global Accelerator 创建加速器。将负载均衡器添加为端点。
B. 创建⼀个 Amazon CloudFront 分发，其源使⽤ Amazon Route 53 基于延迟的路由将请求路由到负载均衡
器。
C. 在每个区域中配置两个应⽤程序负载均衡器。第⼀个将路由到 EC2 端点，第⼆个将路由到本地端点。
D. 在每个区域中配置⽹络负载均衡器，以寻址 EC2 端点。在每个区域中配置⽹络负载均衡器，以路由到本地
端点。
E. 在每个区域中配置⽹络负载均衡器，以寻址 EC2 端点。在每个区域中配置应⽤程序负载均衡器，以路由到
本地端点。
Question #906
Topic 1
⼀家公司在 Amazon EC2 实例上运⾏⾃托管的 Microsoft SQL Server 和 Amazon Elastic Block Store (Amazon
EBS)。每天都会对 EBS 卷进⾏快照。
最近，在运⾏⼀个会删除所有过期 EBS 快照的快照清理脚本时，该公司所有 EBS 快照都被意外删除。解决⽅案
架构师需要更新架构以防⽌数据丢失，同时避免⽆限期地保留 EBS 快照。
哪种解决⽅案能够以最少的开发⼯作量满⾜这些要求？
A. 更改⽤户的 IAM 策略，拒绝删除 EBS 快照。
B. 每⽇快照完成后，将 EBS 快照复制到另⼀个 AWS 区域。
C. 在回收站中创建 7 天的 EBS 快照保留规则，并将该规则应⽤于所有快照。
D. 将 EBS 快照复制到 Amazon S3 标准-不频繁访问 (S3 标准-IA)。
https://examlearn.online
[2026/05]
Question #907
Topic 1
⼀家公司希望在测试环境中使⽤ AWS CloudFormation 堆栈来部署其应⽤程序。该公司将 CloudFormation 模板
存储在 Amazon S3 存储桶中，并阻⽌了公共访问。该公司希望根据特定⽤户的请求，授予 CloudFormation 对
S3 存储桶中模板的访问权限，以便创建测试环境。该解决⽅案必须遵循安全最佳实践。
哪个解决⽅案能够满⾜这些要求？
A. 为 Amazon S3 创建⽹关 VPC 终端节点。配置 CloudFormation 堆栈以使⽤ S3 对象 URL。
B. 创建⼀个以 S3 存储桶为⽬标的 Amazon API Gateway REST API。配置 CloudFormation 堆栈以使⽤该
API Gateway URL。
C. 为模板对象创建预签名 URL。配置 CloudFormation 堆栈以使⽤该预签名 URL。
D. 允许公开访问 S3 存储桶中的模板对象。测试环境创建完成后，阻⽌公开访问。
Question #908
哪种解决⽅案能够最安全地满⾜这些要求？
Systems Manager 会话管理器分配所需的权限。
Topic 1
⼀家公司在 AWS Organizations 中运⾏着⼀些应⽤程序。该公司将这些应⽤程序的运维⽀持外包。该公司需要在
不影响安全性的前提下，为外部⽀持⼯程师提供访问权限。
外部⽀持⼯程师需要访问 AWS 管理控制台。此外，他们还需要访问该公司在私有⼦⽹中运⾏ Amazon Linux 的
Amazon EC2 实例集群的操作系统。
A. 确认所有实例上均已安装 AWS Systems Manager 代理 (SSM 代理)。分配包含必要策略的实例配置⽂
件，以便连接到 Systems Manager。使⽤ AWS IAM 身份中⼼为外部⽀持⼯程师提供控制台访问权限。使⽤
B. 确认所有实例上均已安装 AWS Systems Manager 代理 (SSM 代理)。为实例分配包含必要策略的配置⽂
件，以便连接到 Systems Manager。使⽤ Systems Manager 会话管理器，向外部⽀持⼯程师提供每个 AWS
账户中的本地 IAM ⽤户凭证，以便他们访问控制台。
C. 确认所有实例都已配置安全组，仅允许外部⽀持⼯程师的源 IP 地址范围通过 SSH 访问。向外部⽀持⼯程
师提供每个 AWS 账户中的本地 IAM ⽤户凭证，以便他们访问控制台。向每位外部⽀持⼯程师提供⼀对 SSH
密钥，⽤于登录应⽤程序实例。
D. 在公有⼦⽹中创建堡垒主机。配置堡垒主机的安全组，仅允许外部⼯程师的 IP 地址范围访问。确保所有实
例都拥有允许从堡垒主机进⾏ SSH 访问的安全组。为每位外部⽀持⼯程师提供 SSH 密钥对，以便他们登录
应⽤程序实例。向⼯程师提供本地帐户 IAM ⽤户凭据，以便他们访问控制台。
https://examlearn.online
[2026/05]
Question #909
Topic 1
⼀家公司使⽤ Amazon RDS for PostgreSQL 在 us-east-1 区域运⾏其应⽤程序。该公司还使⽤机器学习 (ML)
模型，根据近实时报告预测年度收⼊。这些报告由同⼀个 RDS for PostgreSQL 数据库⽣成。数据库性能在⼯作
时段会下降。该公司需要提⾼数据库性能。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建跨区域的只读副本。配置要从只读副本⽣成的报告。
B. 为 RDS for PostgreSQL 启⽤多可⽤区数据库实例部署。配置要从备⽤数据库⽣成的报告。
C. 使⽤ AWS 数据迁移服务 (AWS DMS) 将数据逻辑复制到新数据库。配置要从新数据库⽣成的报告。
D. 在 us-east-1 中创建只读副本。配置从只读副本⽣成的报告。
Question #910
解决⽅案架构师应该如何满⾜此要求？
Topic 1
⼀家公司将其多层公共 Web 应⽤程序托管在 AWS 云上。该 Web 应⽤程序运⾏在 Amazon EC2 实例上，其数据
库运⾏在 Amazon RDS 上。该公司预计在即将到来的假⽇周末期间销售额将⼤幅增⻓。解决⽅案架构师需要构建
⼀个解决⽅案，以不超过 2 分钟的粒度分析该 Web 应⽤程序的性能。
A. 将 Amazon CloudWatch ⽇志发送到 Amazon Redshift。使⽤ Amazon QuickSight 进⾏进⼀步分析。
B. 对所有 EC2 实例启⽤详细监控。使⽤ Amazon CloudWatch 指标进⾏进⼀步分析。
C. 创建⼀个 AWS Lambda 函数，从 Amazon CloudWatch Logs 获取 EC2 ⽇志。使⽤ Amazon
CloudWatch 指标进⾏进⼀步分析。
D. 将 EC2 ⽇志发送到 Amazon S3。使⽤ Amazon Redshift 从 S3 存储桶中提取⽇志，以便使⽤ Amazon
QuickSight 处理原始数据进⾏进⼀步分析。
https://examlearn.online
[2026/05]
Question #911
Topic 1
⼀家公司运营⼀款⽤于存储和共享照⽚的应⽤程序。⽤户将照⽚上传到 Amazon S3 存储桶。每天，⽤户⼤约上
传 150 张照⽚。该公司希望设计⼀个解决⽅案，为每张新上传的照⽚创建缩略图，并将缩略图存储在第⼆个 S3
存储桶中。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置⼀条 Amazon EventBridge 定时规则，使其在⻓时间运⾏的 Amazon EMR 集群上每分钟调⽤⼀次脚
本。配置该脚本为没有缩略图的照⽚⽣成缩略图。配置该脚本将缩略图上传到第⼆个 S3 存储桶。
B. 配置⼀条 Amazon EventBridge 定时规则，使其每分钟在始终运⾏的内存优化型 Amazon EC2 实例上调⽤
⼀个脚本。配置该脚本为没有缩略图的照⽚⽣成缩略图。配置该脚本将缩略图上传到第⼆个 S3 存储桶。
C. 配置 S3 事件通知，以便在⽤户每次向应⽤程序上传新照⽚时调⽤ AWS Lambda 函数。配置 Lambda 函
数以⽣成缩略图并将缩略图上传到第⼆个 S3 存储桶。
D. 配置 S3 Storage Lens，使其在⽤户每次向应⽤程序上传新照⽚时调⽤ AWS Lambda 函数。配置该
Lambda 函数⽣成缩略图并将缩略图上传到第⼆个 S3 存储桶。
Question #912
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司使⽤ Amazon S3 Glacier Deep Archive 存储类，在 Amazon S3 存储桶中跨多个前缀存储了数百万个
对象。该公司需要删除所有超过 3 年的数据，但必须保留⼀部分数据。该公司已确定必须保留的数据，并希望实
施⽆服务器解决⽅案。
A. 使⽤ S3 清单列出所有对象。使⽤ AWS CLI 创建⼀个在 Amazon EC2 实例上运⾏的脚本，该脚本从清单
列表中删除对象。
B. 使⽤ AWS Batch 删除超过 3 年的对象，但必须保留的数据除外。
C. 配置⼀个 AWS Glue 爬⾍程序，⽤于查询超过 3 年的对象。保存旧对象的清单⽂件。创建⼀个脚本来删除
清单中的对象。
D. 启⽤ S3 清单。创建⼀个 AWS Lambda 函数来筛选和删除对象。使⽤ S3 批量操作调⽤该 Lambda 函数，
并根据清单报告删除对象。
https://examlearn.online
[2026/05]
Question #913
Topic 1
⼀家公司正在 AWS 上构建⼀个应⽤程序。该应⽤程序使⽤多个 AWS Lambda 函数从单个 Amazon S3 存储桶中
检索敏感数据进⾏处理。该公司必须确保只有获得授权的 Lambda 函数才能访问这些数据。该解决⽅案必须符合
最⼩权限原则。
哪个解决⽅案能够满⾜这些要求？
A. 通过共享的 IAM ⻆⾊授予所有 Lambda 函数完全的 S3 存储桶访问权限。
B. 配置 Lambda 函数在 VPC 内运⾏。配置存储桶策略，根据 Lambda 函数的 VPC 端点 IP 地址授予访问权
限。
C. 为每个 Lambda 函数创建单独的 IAM ⻆⾊。授予这些 IAM ⻆⾊对 S3 存储桶的访问权限。将每个 IAM ⻆
⾊分配为其对应 Lambda 函数的执⾏⻆⾊。
D. 配置存储桶策略，根据 Lambda 函数的 ARN 授予对 Lambda 函数的访问权限。
Question #914
公司需要确保应⽤的安全性和全球可⽤性。
Topic 1
⼀家公司开发了⼀个⾮⽣产环境应⽤，该应⽤由多个微服务组成，分别服务于公司的各个业务部⻔。所有微服务
均由同⼀个开发团队维护。
当前的架构采⽤静态 Web 前端和基于 Java 的后端，后端包含应⽤逻辑。该架构还使⽤公司托管在 Amazon EC2
实例上的 MySQL 数据库。
哪种解决⽅案能够在满⾜这些要求的同时，将运维开销降⾄最低？
A. 使⽤ Amazon CloudFront 和 AWS Amplify 托管静态 Web 前端。重构微服务，使其使⽤ AWS Lambda
函数，并通过 Amazon API Gateway 访问这些函数。将 MySQL 数据库迁移到 Amazon EC2 预留实例。
B. 使⽤ Amazon CloudFront 和 Amazon S3 托管静态 Web 前端。重构微服务，使其使⽤ AWS Lambda 函
数，并通过 Amazon API Gateway 访问这些函数。将 MySQL 数据库迁移到 Amazon RDS for MySQL。
C. 使⽤ Amazon CloudFront 和 Amazon S3 托管静态 Web 前端。重构微服务，使其使⽤位于⽹络负载均衡
器后⽅⽬标组中的 AWS Lambda 函数。将 MySQL 数据库迁移到 Amazon RDS for MySQL。
D. 使⽤ Amazon S3 托管静态 Web 前端。重构微服务，使其使⽤位于应⽤程序负载均衡器后⽅⽬标组中的
AWS Lambda 函数。将 MySQL 数据库迁移到 Amazon EC2 预留实例。
https://examlearn.online
[2026/05]
Question #915
Topic 1
⼀家视频游戏公司正在向其全球⽤户部署⼀款新的游戏应⽤。该公司需要⼀个解决⽅案，能够提供近乎实时的玩
家评价和排名。
解决⽅案架构师必须设计⼀个能够快速访问数据的⽅案。该⽅案还必须确保在公司重启应⽤后，数据能够持久保
存在磁盘上。
哪种⽅案能够在满⾜这些要求的同时，将运营开销降⾄最低？
A. 配置以 Amazon S3 存储桶为源的 Amazon CloudFront 分发。将玩家数据存储在 S3 存储桶中。
B. 在多个 AWS 区域中创建 Amazon EC2 实例。将玩家数据存储在 EC2 实例上。配置 Amazon Route 53 的
地理位置记录，以便将⽤户引导⾄最近的 EC2 实例。
C. 部署 Amazon ElastiCache for Redis 集群。将玩家数据存储在 ElastiCache 集群中。
D. 部署 Amazon ElastiCache for Memcached 除尘器。将玩家数据存储在 ElastiCache 集群中。
Question #916
⼀家公司正在 AWS 上设计⼀个处理敏感数据的应⽤程序。该应⽤程序存储并处理多个客户的财务数据。
Topic 1
为了满⾜合规性要求，每个客户的数据必须使⽤安全、集中式的密钥管理解决⽅案进⾏静态加密。该公司希望使
⽤ AWS Key Management Service (AWS KMS) 来实现加密。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为每个客户⽣成唯⼀的加密密钥。将密钥存储在 Amazon S3 存储桶中。启⽤服务器端加密。
B. 在 AWS 环境中部署硬件安全设备，⽤于安全地存储客户提供的加密密钥。将该安全设备与 AWS KMS 集
成，以加密应⽤程序中的敏感数据。
C. 创建⼀个 AWS KMS 密钥来加密应⽤程序中的所有敏感数据。
D. 为每个客户的数据创建单独的 AWS KMS 密钥，并启⽤细粒度的访问控制和⽇志记录。
https://examlearn.online
[2026/05]
Question #917
Topic 1
⼀家公司需要设计⼀个⾼弹性的Web应⽤程序来处理客户订单。该Web应⽤程序必须能够⾃动应对⽹络流量和应
⽤程序使⽤量的增⻓，同时不影响客户体验或导致客户订单丢失。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ NAT ⽹关管理 Web 流量。使⽤ Amazon EC2 ⾃动扩展组接收、处理和存储已处理的客户订单。使⽤
AWS Lambda 函数捕获和存储未处理的订单。
B. 使⽤⽹络负载均衡器 (NLB) 管理 Web 流量。使⽤应⽤程序负载均衡器接收来⾃ NLB 的客户订单。使⽤采
⽤多可⽤区部署的 Amazon Redshift 存储未处理和已处理的客户订单。
C. 使⽤⽹关负载均衡器 (GWLB) 管理 Web 流量。使⽤ Amazon Elastic Container Service (Amazon ECS)
接收和处理客户订单。使⽤ GWLB 捕获和存储未处理的订单。使⽤ Amazon DynamoDB 存储已处理的客户
订单。
D. 使⽤应⽤程序负载均衡器管理 Web 流量。使⽤ Amazon EC2 ⾃动扩展组接收和处理客户订单。使⽤
Amazon 简单队列服务 (Amazon SQS) 存储未处理的订单。使⽤采⽤多可⽤区部署的 Amazon RDS 存储已
处理的客户订单。
Question #918
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司正在使⽤ AWS DataSync 将数百万个⽂件从本地系统迁移到 AWS。这些⽂件的平均⼤⼩为 10 KB。
该公司希望使⽤ Amazon S3 进⾏⽂件存储。迁移后的第⼀年，这些⽂件只会被访问⼀到两次，并且必须能够⽴
即访问。⼀年后，这些⽂件必须⾄少归档 7 年。
A. 使⽤归档⼯具将⽂件分组为⼤型对象。使⽤ DataSync 迁移这些对象。第⼀年将对象存储在 S3 Glacier
Instant Retrieval 中。使⽤⽣命周期配置，在⼀年后将⽂件迁移到 S3 Glacier Deep Archive，保留期为 7
年。
B. 使⽤归档⼯具将⽂件分组为⼤型对象。使⽤ DataSync 将这些对象复制到 S3 标准版（不频繁访问）（S3
Standard-IA）。使⽤⽣命周期配置，在 1 年后将⽂件迁移到 S3 Glacier 即时检索，保留期限为 7 年。
C. 将⽂件的⽬标存储类别配置为 S3 Glacier Instant Retrieval。使⽤⽣命周期策略，在 1 年后将⽂件迁移到
S3 Glacier Flexible Retrieval，保留期为 7 年。
D. 配置数据同步任务，将⽂件传输到 S3 标准版（不频繁访问）（S3 Standard-IA）。使⽤⽣命周期配置，在 1
年后将⽂件迁移到 S3 深度归档，保留期限为 7 年。
https://examlearn.online
[2026/05]
Question #919
Topic 1
⼀家公司最近将其本地 Oracle 数据库⼯作负载迁移到 Amazon EC2 内存优化型 Linux 实例上运⾏。该 EC2
Linux 实例使⽤ 1 TB 的预置 IOPS SSD (io1) EBS 卷，IOPS 为 64,000。迁移
后，数据库存储性能低于本地数据库的性能。
哪种解决⽅案可以提⾼存储性能？
A. 添加更多已配置 IOPS SSD (io1) EBS 卷。使⽤操作系统命令创建逻辑卷管理 (LVM) 条带。
B. 将已配置 IOPS SSD (io1) EBS 卷增加到 64,000 IOPS 以上。
C. 将已配置 IOPS SSD (io1) EBS 卷的⼤⼩增加到 2 TB。
D. 将 EC2 Linux 实例更改为存储优化型实例类型。请勿更改已配置 IOPS SSD (io1) EBS 卷。
Question #920
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司正在将其托管在 Amazon EC2 上的 Web 应⽤程序从单体架构迁移到⽆服务器微服务架构。该公司希望
使⽤⽀持事件驱动、松耦合架构的 AWS 服务，并采⽤发布/订阅 (pub/sub) 模式。
A. 配置 Amazon API Gateway REST API 以调⽤ AWS Lambda 函数，该函数将事件发布到 Amazon Simple
Queue Service (Amazon SQS) 队列。配置⼀个或多个订阅者以从 SQS 队列读取事件。
B. 配置 Amazon API Gateway REST API 以调⽤ AWS Lambda 函数，该函数将事件发布到 Amazon Simple
Notification Service (Amazon SNS) 主题。配置⼀个或多个订阅者以接收来⾃ SNS 主题的事件。
C. 配置 Amazon API Gateway WebSocket API，使其能够写⼊ Amazon Kinesis Data Streams 中的数据
流，并启⽤增强型扇出功能。配置⼀个或多个订阅者以接收来⾃数据流的事件。
D. 配置 Amazon API Gateway HTTP API 以调⽤ AWS Lambda 函数，该函数将事件发布到 Amazon Simple
Notification Service (Amazon SNS) 主题。配置⼀个或多个订阅者以接收来⾃该主题的事件。
https://examlearn.online
[2026/05]
Question #921
Topic 1
⼀家公司最近将⼀个单体应⽤迁移到了 Amazon EC2 实例和 Amazon RDS 上。该应⽤由紧密耦合的模块组成。
其现有设计使其只能在单个 EC2 实例上运⾏。
该公司注意到，在⾼峰使⽤时段，EC2 实例的 CPU 利⽤率很⾼。⾼ CPU 利⽤率导致 Amazon RDS 读取请求的
性能下降。该公司希望降低 CPU 利⽤率并提⾼读取请求的性能。
哪种解决⽅案能够满⾜这些要求？
A. 将 EC2 实例调整为具有更⾼ CPU 容量的 EC2 实例类型。配置⼀个⾃动扩展组，其最⼩和最⼤⼤⼩均为
1。配置⼀个 RDS 只读副本以处理读取请求。
B. 将 EC2 实例调整为具有更⾼ CPU 容量的 EC2 实例类型。配置⼀个⾃动扩展组，其最⼩和最⼤⼤⼩均为
1。添加⼀个 RDS 只读副本，并将所有读/写流量重定向到该副本。
C. 配置⼀个最⼩⼤⼩为 1、最⼤⼤⼩为 2 的⾃动扩展组。将 RDS 数据库实例调整为具有更⾼ CPU 容量的实
例类型。
D. 将 EC2 实例调整为具有更⾼ CPU 容量的 EC2 实例类型。配置⼀个最⼩和最⼤⼤⼩均为 1 的⾃动扩展组。
将 RDS 数据库实例调整为具有更⾼ CPU 容量的实例类型。
Question #922
哪种解决⽅案能够满⾜这些要求？
⼀家公司需要授予其开发团队访问公司 AWS 资源的权限。该公司必须确保这些资源的安全性。
该公司需要⼀个访问控制解决⽅案，以防⽌未经授权访问敏感数据。
A. 将每个开发团队成员的 IAM ⽤户凭证与团队其他成员共享，以简化访问管理并简化开发⼯作流程。
B. 根据最⼩权限原则，定义具有细粒度权限的 IAM ⻆⾊。为每位开发⼈员分配⼀个 IAM ⻆⾊。
Topic 1
C. 创建 IAM 访问密钥，以授予对 AWS 资源的程序化访问权限。仅允许开发⼈员使⽤这些访问密钥通过 API
调⽤与 AWS 资源进⾏交互。
D. 创建 AWS Cognito ⽤户池。通过该⽤户池授予开发⼈员对 AWS 资源的访问权限。
https://examlearn.online
[2026/05]
Question #923
Topic 1
⼀家公司在 Amazon EC2 实例上托管了⼀个单体 Web 应⽤程序。最近，应⽤程序⽤户反映在特定时间段内性能
不佳。对 Amazon CloudWatch 指标的分析显示，在性能不佳的时间段内，CPU 利⽤率达到了 100%。
该公司希望解决此性能问题并提⾼应⽤程序的可⽤性。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ AWS Compute Optimizer 获取⽤于垂直扩展的实例类型的建议。
B. 从 Web 服务器创建 Amazon 系统映像 (AMI)。在新启动模板中引⽤该 AMI。
C. 创建⼀个⾃动扩展组和⼀个应⽤程序负载均衡器，以实现垂直扩展。
D. 使⽤ AWS Compute Optimizer 获取⽤于⽔平扩展的实例类型的建议。
E. 创建⼀个⾃动扩展组和⼀个应⽤程序负载均衡器，以实现⽔平扩展。
Question #924
Topic 1
⼀家公司将其所有业务应⽤程序运⾏在 AWS 云上。该公司使⽤ AWS Organizations 管理多个 AWS 账户。
解决⽅案架构师需要审查授予 IAM ⽤户的所有权限，以确定哪些 IAM ⽤户拥有超出所需的权限。
哪种解决⽅案能够以最⼩的管理开销满⾜这些要求？
A. 使⽤⽹络访问分析器查看公司 AWS 账户中的所有访问权限。
B. 创建⼀个 AWS CloudWatch 警报，当 IAM ⽤户在 AWS 账户中创建或修改资源时激活该警报。
C. 使⽤ AWS Identity and Access Management (IAM) Access Analyzer 来审查公司的所有资源和帐户。
D. 使⽤ Amazon Inspector 查找现有 IAM 策略中的漏洞。
https://examlearn.online
[2026/05]
Question #925
Topic 1
⼀家公司需要实施新的数据保留策略以符合监管要求。根据该策略，存储在 Amazon S3 存储桶中的敏感⽂档必
须在⼀段固定时间内受到保护，防⽌被删除或修改。
哪种解决⽅案能够满⾜这些要求？
A. 对所需对象激活 S3 对象锁定并启⽤治理模式。
B. 对所需对象激活 S3 对象锁定并启⽤合规模式。
C. 在 S3 存储桶上启⽤版本控制。设置⽣命周期策略，以便在指定时间段后删除对象。
D. 配置 S3 ⽣命周期策略，将对象在保留期内转移到 S3 Glacier 灵活检索。
Question #926
整 Fargate 任务的⼤⼩。
Topic 1
⼀家公司在容器上运⾏其⾯向客户的 Web 应⽤程序。该⼯作负载使⽤ AWS Fargate 上的 Amazon Elastic
Container Service (Amazon ECS)。该 Web 应⽤程序资源密集型，
需要全天候 (24/7) 为客户提供服务。公司预计该应⽤程序会遇到短时⾼流量⾼峰。因此，⼯作负载必须具备⾼可
⽤性。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置带有 Fargate 的 ECS 容量提供程序。使⽤第三⽅⼯具进⾏负载测试。在 Amazon CloudWatch 中调
B. 配置 ECS 容量提供程序，其中 Fargate ⽤于稳定状态，Fargate Spot ⽤于突发流量。
C. 配置 ECS 容量提供程序，其中 Fargate Spot ⽤于稳定状态，Fargate ⽤于突发流量。
D. 配置包含 Fargate 的 ECS 容量提供程序。使⽤ AWS Compute Optimizer 调整 Fargate 任务的⼤⼩。
https://examlearn.online
[2026/05]
Question #927
Topic 1
⼀家公司正在 AWS 云上构建⼀个应⽤程序。该应⽤程序托管在应⽤程序负载均衡器 (ALB) 后⾯的 Amazon EC2
实例上。该公司使⽤ Amazon Route 53 进⾏ DNS 解析。
该公司需要⼀个具有主动防御能⼒的托管解决⽅案来检测 DDoS 攻击。
哪种解决⽅案能够满⾜这些要求？
A. 启⽤ AWS Config。配置 AWS Config 托管规则以检测 DDoS 攻击。
B. 在应⽤负载均衡器 (ALB) 上启⽤ AWS WAF。创建⼀个包含 DDoS 攻击检测和防御规则的 AWS WAF Web
ACL。将该 Web ACL 与应⽤负载均衡器 (ALB) 关联。
C. 将 ALB 访问⽇志存储在 Amazon S3 存储桶中。配置 Amazon GuardDuty 以检测 DDoS 攻击并采取⾃动
预防措施。
D. 订阅 AWS Shield Advanced。在 Route 53 中配置托管区域。将 ALB 资源添加为受保护资源。
Question #928
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在虚拟专⽤⽹络 (VPC) 中托管了⼀个视频流媒体 Web 应⽤程序。该公司使⽤⽹络负载均衡器 (NLB) 来
处理实时数据处理的 TCP 流量。⽬前已出现未经授权的访问尝试。
该公司希望在架构改动最⼩的情况下提⾼应⽤程序的安全性，以防⽌未经授权的访问尝试。
A. 在 NLB 上直接实施⼀系列 AWS WAF 规则，以过滤掉未经授权的流量。
B. 使⽤安全组重新创建 NLB，仅允许受信任的 IP 地址。
C. 部署第⼆个 NLB，与现有 NLB 并⾏，并配置严格的 IP 地址允许列表。
D. 使⽤ AWS Shield Advanced 提供增强的 DDoS 防护并防⽌未经授权的访问尝试。
https://examlearn.online
[2026/05]
Question #929
⼀家医疗保健公司正在开发⼀个 AWS Lambda 函数，该函数会将通知发布到加密的 Amazon Simple
Notification Service (Amazon SNS) 主题。这些通知包含受保护的健康信息 (PHI)。SNS
Topic 1
主题使⽤ AWS Key Management Service (AWS KMS) 客户管理的密钥进⾏加密。该公司必须确保该应⽤程序拥
有将消息安全地发布到 SNS 主题所需的权限。
以下哪些步骤组合可以满⾜这些要求？（选择三个。）
A. 为 SNS 主题创建资源策略，允许 Lambda 函数向该主题发布消息。
B. 对 SNS 主题使⽤ AWS KMS 密钥（SSE-KMS）进⾏服务器端加密，⽽不是使⽤客户管理的密钥。
C. 为 SNS 主题使⽤的加密密钥创建资源策略，该策略具有必要的 AWS KMS 权限。
D. 在 SNS 主题的资源策略中指定 Lambda 函数的 Amazon 资源名称 (ARN)。
E. 将 Amazon API Gateway HTTP API 与 SNS 主题关联，以便使⽤ API Gateway 资源策略来控制对该主题
的访问。
F. 配置 Lambda 执⾏⻆⾊，使其拥有必要的 IAM 权限，以便在 AWS KMS 中使⽤客户管理的密钥。
Question #930
Topic 1
⼀家公司拥有⼀个员⼯⻔户⽹站。员⼯登录该⽹站查看⼯资明细。该公司正在开发⼀个新系统，使员⼯能够上传
扫描⽂件进⾏报销。该公司运⾏⼀个程序，从⽂档中提取⽂本数据，并将提取的信息附加到每位员⼯的报销ID上
进⾏处理。
员⼯⻔户⽹站需要100%正常运⾏时间。⽂档提取程序在⼀天中按需运⾏，运⾏频率较低。该公司希望构建⼀个可
扩展且经济⾼效的新系统，并且只需对现有⻔户⽹站进⾏最⼩程度的更改。该公司不希望修改任何代码。
哪种解决⽅案能够以最⼩的实施⼯作量满⾜这些要求？
A. 在⾃动扩展组中运⾏ Amazon EC2 按需实例，⽤于 Web ⻔户。使⽤ AWS Lambda 函数运⾏⽂档提取程
序。当员⼯上传新的报销单据时，调⽤该 Lambda 函数。
B. 在⾃动扩展组中运⾏ Amazon EC2 Spot 实例，⽤于 Web ⻔户。在 EC2 Spot 实例上运⾏⽂档提取程序。
当员⼯上传新的报销单据时，启动⽂档提取程序实例。
C. 购买⼀个节能计划来运⾏⽹络⻔户和⽂档提取程序。在⾃动扩展组中运⾏⽹络⻔户和⽂档提取程序。
D. 创建⼀个 Amazon S3 存储桶来托管 Web ⻔户。使⽤ Amazon API Gateway 和 AWS Lambda 函数来实现
现有功能。使⽤ Lambda 函数运⾏⽂档提取程序。当调⽤与新⽂档上传关联的 API 时，调⽤ Lambda 函数。
https://examlearn.online
[2026/05]
Question #931
Topic 1
⼀家媒体公司在 us-east-1 区域拥有⼀个多账户的 AWS 环境。该公司在⼀个⽣产账户中创建了⼀个 Amazon
Simple Notification Service (Amazon SNS) 主题，⽤于发布性能指标。该公司在⼀个管理员账户中创建了⼀个
AWS Lambda 函数，⽤于处理和分析⽇志数据。
当报告重要指标时，必须通过来⾃⽣产账户中 SNS 主题的消息来调⽤管理员账户中的 Lambda 函数。
以下哪两项步骤组合可以满⾜这些要求？（选择两项。）
A. 为 Lambda 函数创建 IAM 资源策略，允许 Amazon SNS 调⽤该函数。
B. 在管理员账户中部署⼀个 Amazon Simple Queue Service (Amazon SQS) 队列，⽤于缓冲来⾃⽣产账户
中 SNS 主题的消息。配置 SQS 队列以调⽤ Lambda 函数。
C. 为 SNS 主题创建 IAM 策略，允许 Lambda 函数订阅该主题。
D. 在⽣产账户中使⽤ Amazon EventBridge 规则来捕获 SNS 主题通知。配置 EventBridge 规则，将通知转
发到管理员账户中的 Lambda 函数。
Question #932
哪种解决⽅案能够满⾜这些要求？
E. 将性能指标存储在⽣产账户的 Amazon S3 存储桶中。使⽤ Amazon Athena 从管理员账户分析这些指标。
Topic 1
⼀家公司正在将应⽤程序从本地部署迁移到 Amazon Elastic Kubernetes Service (Amazon EKS)。为了满⾜相
关要求，该公司必须为位于其 VPC 中的 Pod 使⽤⾃定义⼦⽹。此外，该公司还需要确保 Pod 能够在各⾃的 VPC
内安全通信。
A. 配置 AWS Transit Gateway 直接管理 Amazon EKS 中 pod 的⾃定义⼦⽹配置。
B. 从公司本地 IP 地址范围创建到 EKS pod 的 AWS Direct Connect 连接。
C. 使⽤适⽤于 Kubernetes 的 Amazon VPC CNI 插件。在 VPC 集群中定义⾃定义⼦⽹，供 Pod 使⽤。
D. 实施 Kubernetes ⽹络策略，该策略具有 pod 反亲和性规则，以限制 pod 放置到⾃定义⼦⽹内的特定节
点。
https://examlearn.online
[2026/05]
Question #933
Topic 1
⼀家公司托管了⼀个电⼦商务应⽤程序，该应⽤程序的所有数据存储在由 AWS 完全管理的单个 Amazon RDS
for MySQL 数据库实例中。该公司需要降低单点故障的⻛险。
哪种解决⽅案能够以最⼩的实施⼯作量满⾜这些要求？
A. 将 RDS 数据库实例修改为使⽤多可⽤区部署。在下⼀个维护窗⼝期间应⽤这些更改。
B. 将当前数据库迁移到新的 Amazon DynamoDB 多可⽤区部署。使⽤ AWS 数据库迁移服务 (AWS DMS) 和
异构迁移策略，将当前的 RDS 数据库实例迁移到 DynamoDB 表。
C. 在多可⽤区部署中创建⼀个新的 RDS 数据库实例。⼿动从现有 RDS 数据库实例的最新快照恢复数据。
D. 将数据库实例配置到 Amazon EC2 ⾃动扩展组中，最⼩组⼤⼩为 3。使⽤ Amazon Route 53 简单路由将
请求分发到所有数据库实例。
Question #934
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在本地环境中部署了多台⽤于⽂件共享的 Microsoft Windows SMB ⽂件服务器和 Linux NFS ⽂件服务
器。作为公司 AWS 迁移计划的⼀部分，该公司希望将⽂件服务器整合到 AWS 云中。
该公司需要⼀种托管的 AWS 存储服务，该服务必须同时⽀持 NFS 和 SMB 访问。该解决⽅案必须能够跨协议共
享⽂件，并且必须在可⽤区级别提供冗余。
A. 使⽤ Amazon FSx for NetApp ONTAP 作为存储。配置多协议访问。
B. 创建两个 Amazon EC2 实例。⼀个 EC2 实例⽤于 Windows SMB ⽂件服务器访问，另⼀个 EC2 实例⽤于
Linux NFS ⽂件服务器访问。
C. 使⽤ Amazon FSx for NetApp ONTAP 进⾏ SMB 访问。使⽤ Amazon FSx for Lustre 进⾏ NFS 访问。
D. 使⽤ Amazon S3 存储。通过 Amazon S3 ⽂件⽹关访问 Amazon S3。
https://examlearn.online
[2026/05]
Question #935
Topic 1
⼀家软件公司需要升级⼀个关键的 Web 应⽤程序。该应⽤程序⽬前运⾏在公司托管于公有⼦⽹中的单个
Amazon EC2 实例上。该 EC2 实例运⾏着⼀个 MySQL 数据库。应⽤程序的 DNS 记录发布在 Amazon Route
53 区域中。
解决⽅案架构师必须重新配置该应⽤程序，使其具有可扩展性和⾼可⽤性。此外，解决⽅案架构师还必须降低
MySQL 的读取延迟。
以下哪两项解决⽅案组合能够满⾜这些要求？（选择两项。）
A. 在第⼆个 AWS 区域中启动第⼆个 EC2 实例。使⽤ Route 53 故障转移路由策略将流量重定向到第⼆个
EC2 实例。
B. 创建并配置⼀个⾃动扩展组，以在多个可⽤区启动私有 EC2 实例。将这些实例添加到位于新应⽤程序负载
均衡器后⾯的⽬标组中。
C. 将数据库迁移到 Amazon Aurora MySQL 集群。在不同的可⽤区中创建主数据库实例和读取器数据库实
例。
E. 将数据库迁移到具有跨区域只读副本的 Amazon Aurora MySQL 集群。
Question #936
D. 创建并配置⼀个⾃动扩展组，以在多个 AWS 区域中启动私有 EC2 实例。将这些实例添加到位于新的应⽤
程序负载均衡器后⾯的⽬标组中。
Topic 1
⼀家公司运⾏着数千个 AWS Lambda 函数。该公司需要⼀个解决⽅案来安全地存储所有 Lambda 函数使⽤的敏
感信息。该解决⽅案还必须管理敏感信息的⾃动轮换。
以下哪两项措施组合能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ Lambda@Edge 创建 HTTP 安全标头以检索和创建敏感信息
B. 创建⼀个 Lambda 层来检索敏感信息
C. 将敏感信息存储在 AWS Secrets Manager 中
D. 将敏感信息存储在 AWS Systems Manager 参数存储中
E. 创建⼀个具有专⽤吞吐量的 Lambda 消费者，⽤于检索敏感信息并创建环境变量。
https://examlearn.online
[2026/05]
Question #937
Topic 1
⼀家公司有⼀个内部应⽤程序，运⾏在⾃动扩展组中的 Amazon EC2 实例上。这些 EC2 实例是计算优化型的，
并使⽤ Amazon Elastic Block Store (Amazon EBS) 卷。
该公司希望在 EC2 实例、⾃动扩展组和 EBS 卷⽅⾯找到成本优化⽅案。
哪种解决⽅案能够以最⾼的运营效率满⾜这些要求？
A. 创建⼀份新的 AWS 成本和使⽤情况报告。在报告中搜索 EC2 实例、⾃动扩展组和 EBS 卷的成本建议。
B. 创建新的 Amazon CloudWatch 账单警报。检查警报状态，获取 EC2 实例、⾃动扩展组和 EBS 卷的成本
建议。
C. 配置 AWS Compute Optimizer，以便为 EC2 实例、⾃动扩展组和 EBS 卷提供成本建议。
D. 配置 AWS Compute Optimizer，以便为 EC2 实例提供成本建议。创建新的 AWS 成本和使⽤情况报告。
在该报告中搜索 Auto Scaling 组和 EBS 卷的成本建议。
Question #938
解决⽅案架构师应该提出什么建议？
Topic 1
⼀家公司在单个 VPC 内的多个可⽤区中分布的多个 Amazon EC2 实例上运⾏媒体存储。该公司希望找到⼀种⾼
性能的解决⽅案，以便在所有 EC2 实例之间共享数据，并且希望将数据仅保留在 VPC 内。
A. 创建⼀个 Amazon S3 存储桶，并从每个实例的应⽤程序调⽤服务 API。
B. 创建⼀个 Amazon S3 存储桶，并将所有实例配置为以挂载卷的⽅式访问它。
C. 配置 Amazon Elastic Block Store (Amazon EBS) 卷并将其挂载到所有实例上
D. 配置 Amazon Elastic File System (Amazon EFS) ⽂件系统并将其挂载到所有实例上
https://examlearn.online
[2026/05]
Question #939
Topic 1
⼀家公司使⽤ Amazon RDS for MySQL 实例。为了准备年终处理，该公司添加了⼀个只读副本，以满⾜公司报
表⼯具的额外只读查询需求。只读副本的 CPU 使⽤率为 60%，主实例的 CPU 使⽤率也为 60%。
年终活动结束后，只读副本的 CPU 使⽤率稳定在 25%，⽽主实例的 CPU 使⽤率仍然稳定在 60%。该公司希望
调整数据库规模，同时确保其性能⾜以满⾜未来的增⻓需求。
哪种解决⽅案能够满⾜这些要求？
A. 删除只读副本，不要对主实例进⾏任何更改。
B. 将只读副本的实例⼤⼩调整为更⼩的实例⼤⼩。不要更改主实例。
C. 将只读副本调整为更⼤的实例⼤⼩；将主实例调整为更⼩的实例⼤⼩。
D. 删除只读副本，并将主实例调整为更⼤的实例
Question #940
哪种解决⽅案能够以最具成本效益的⽅式满⾜此要求？
“⽆需预付”选项来获取 EC2 实例。
Topic 1
⼀家公司正在将其数据库迁移到 Amazon RDS for PostgreSQL，并将其应⽤程序迁移到 Amazon EC2 实例。该
公司希望优化⻓时间运⾏⼯作负载的成本。
A. 对于 Amazon RDS for PostgreSQL ⼯作负载，请使⽤按需实例。购买为期 1 年的计算节省计划，并选择
B. 购买为期 1 年的 Amazon RDS for PostgreSQL ⼯作负载预留实例，⽆需预付任何费⽤。购买为期 1 年的
EC2 实例节省计划，⽆需预付任何费⽤。
C. 购买为期 1 年的 Amazon RDS for PostgreSQL ⼯作负载预留实例，并选择部分预付款选项。购买为期 1
年的 EC2 实例节省计划，并选择部分预付款选项。
D. 购买为期 3 年的 Amazon RDS for PostgreSQL ⼯作负载预留实例，并选择“全额预付”选项。购买为期 3
年的 EC2 实例节省计划，并选择“全额预付”选项。
https://examlearn.online
[2026/05]
Question #941
Topic 1
⼀家公司正在使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 集群。该公司必须确保 EKS 集群中的
Kubernetes 服务账户能够安全、精细地访问特定的 AWS 资源，为此需要使⽤ IAM 服务账户⻆⾊ (IRSA)。
以下哪两项解决⽅案组合能够满⾜这些要求？（选择两项。）
A. 创建⼀个定义所需权限的 IAM 策略，并将该策略直接附加到 EKS 节点的 IAM ⻆⾊。
B. 在 EKS 集群内实施⽹络策略，以防⽌ Kubernetes 服务帐户访问特定的 AWS 服务。
C. 修改 EKS 集群的 IAM ⻆⾊，为每个 Kubernetes 服务帐户添加权限。确保 IAM ⻆⾊与 Kubernetes ⻆⾊
⼀⼀对应。
D. 定义⼀个包含必要权限的 IAM ⻆⾊。使⽤该 IAM ⻆⾊的 Amazon 资源名称 (ARN) 注释 Kubernetes 服务
账户。
E. 在服务帐户的 IAM ⻆⾊和 OpenID Connect (OIDC) 身份提供程序之间建⽴信任关系。
Question #942
⼀家公司定期将机密数据上传到 Amazon S3 存储桶进⾏分析。
哪种解决⽅案能够满⾜这些要求？
Topic 1
该公司的安全策略要求对静态数据进⾏加密。该公司必须每年⾃动轮换加密密钥。该公司必须能够使⽤ AWS
CloudTrail 跟踪密钥轮换情况。此外，该公司还必须尽可能降低加密密钥的成本。
A. 使⽤客户提供的密钥进⾏服务器端加密 (SSE-C)
B. 使⽤ Amazon S3 管理的密钥进⾏服务器端加密 (SSE-S3)
C. 使⽤ AWS KMS 密钥进⾏服务器端加密 (SSE-KMS)
D. 使⽤客户管理的 AWS KMS 密钥进⾏服务器端加密
https://examlearn.online
[2026/05]
Question #943
Topic 1
⼀家公司在过去三个⽉内将多个应⽤程序迁移到了 AWS。该公司希望了解每个应⽤程序的成本明细，并定期收到
包含这些信息的报告。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ AWS Budgets 将过去 3 个⽉的数据下载到 .csv ⽂件中。查找所需信息。
B. 将 AWS 成本和使⽤情况报告加载到 Amazon RDS 数据库实例中。运⾏ SQL 查询以获取所需信息。
C. 为所有 AWS 资源添加标签，标签中包含成本键和应⽤程序名称值。启⽤成本分配标签。使⽤成本资源管理
器获取所需信息。
D. 为所有 AWS 资源添加标签，标签中包含成本键和应⽤程序名称值。使⽤ AWS 账单和成本管理控制台下载
过去 3 个⽉的账单。查找所需信息。
Question #944
该公司希望为该应⽤程序设计⼀个强⼤且具有弹性的架构。
哪种解决⽅案能够满⾜这些要求？
Amazon S3 存储静态资源。
CloudFront 分发静态资源。
Topic 1
⼀家电商公司正准备在 AWS 上部署⼀个 Web 应⽤程序，以确保为客户提供不间断的服务。该架构包括⼀个托管
在 Amazon EC2 实例上的 Web 应⽤程序、⼀个位于 Amazon RDS 中的关系数据库，以及存储在 Amazon S3 中
的静态资源。
A. 在单个可⽤区部署 Amazon EC2 实例。在同⼀可⽤区部署 RDS 数据库实例。使⽤启⽤版本控制的
B. 在跨多个可⽤区的⾃动扩展组中部署 Amazon EC2 实例。部署多可⽤区 RDS 数据库实例。使⽤ Amazon
C. 在单个可⽤区部署 Amazon EC2 实例。在第⼆个可⽤区部署 RDS 数据库实例以实现跨可⽤区冗余。直接
从 EC2 实例提供静态资源。
D. 使⽤ AWS Lambda 函数来提供 Web 应⽤程序服务。使⽤ Amazon Aurora Serverless v2 作为数据库。将
静态资源存储在 Amazon Elastic File System (Amazon EFS) 的 One Zone-Infrequent Access (One Zone
IA) 中。
https://examlearn.online
[2026/05]
Question #945
Topic 1
⼀家电⼦商务公司在多个 AWS 账户中运⾏多个内部应⽤程序。该公司使⽤ AWS Organizations 来管理其 AWS
账户。
该公司⽹络账户中的安全设备必须检查跨 AWS 账户的应⽤程序之间的交互。
哪种解决⽅案能够满⾜这些要求？
A. 在⽹络账号中部署⽹络负载均衡器 (NLB)，将流量发送到安全设备。配置应⽤账号，使其通过应⽤账号中
的接⼝ VPC 端点将流量发送到 NLB。
B. 在应⽤程序帐户中部署应⽤程序负载均衡器 (ALB)，将流量直接发送到安全设备。
C. 在⽹络帐户中部署⽹关负载均衡器 (GWLB)，将流量发送到安全设备。配置应⽤程序帐户，使其通过应⽤
程序帐户中的接⼝ GWLB 端点将流量发送到 GWLB。
D. 在应⽤程序帐户中部署接⼝ VPC 端点，以便将流量直接发送到安全设备。
Question #946
哪种解决⽅案满⾜这些要求？
Topic 1
⼀家公司在包含六个 Aurora 副本的 Amazon Aurora MySQL 数据库集群上运⾏其⽣产⼯作负载。该公司希望将
来⾃其某个部⻔的近实时报表查询⾃动分配到其中三个 Aurora 副本上。这三个副本的计算和内存配置与数据库集
群中的其他副本不同。
A. 为⼯作负载创建并使⽤⾃定义端点
B. 创建⼀个三节点集群克隆并使⽤读取器端点
C. 使⽤所选三个节点的任意实例端点
D. 使⽤读取器端点⾃动分配只读⼯作负载
https://examlearn.online
[2026/05]
Question #947
Topic 1
⼀家公司在其本地数据中⼼的服务器上运⾏⼀个 Node.js 函数。该数据中⼼将数据存储在 PostgreSQL 数据库
中。该公司将凭据存储在服务器环境变量中的连接字符串中。该公司希望将其应⽤程序迁移到 AWS，并将
Node.js 应⽤服务器替换为 AWS Lambda。该公司还希望将 PostgreSQL 迁移到 Amazon RDS，并确保数据库
凭据得到安全管理。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将数据库凭证作为参数存储在 AWS Systems Manager Parameter Store 中。配置 Parameter Store 每
30 天⾃动轮换⼀次密钥。更新 Lambda 函数，使其从参数中检索凭证。
B. 将数据库凭证作为密钥存储在 AWS Secrets Manager 中。配置 Secrets Manager 每 30 天⾃动轮换⼀次
凭证。更新 Lambda 函数，使其从密钥中检索凭证。
C. 将数据库凭据存储为加密的 Lambda 环境变量。编写⾃定义 Lambda 函数来轮换凭据。安排该 Lambda
函数每 30 天运⾏⼀次。
D. 将数据库凭证作为密钥存储在 AWS Key Management Service (AWS KMS) 中。配置密钥的⾃动轮换。更
新 Lambda 函数，使其从 KMS 密钥中检索凭证。
Question #948
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司希望将本地 Oracle 数据库中现有和持续的数据变更复制到 Amazon RDS for Oracle。每天需要复制的
数据量都在变化。该公司希望使⽤ AWS 数据库迁移服务 (AWS DMS) 进⾏数据复制。该解决⽅案必须仅分配复
制实例所需的容量。
A. 使⽤多可⽤区部署配置 AWS DMS 复制实例，以跨多个可⽤区预置实例。
B. 创建⼀个 AWS DMS ⽆服务器复制任务，以分析和复制数据，同时提供所需的容量。
C. 使⽤ Amazon EC2 ⾃动扩展功能，根据要复制的数据量⾃动扩展或缩减 AWS DMS 复制实例的⼤⼩。
D. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 AWS Fargate 启动类型来配置 AWS DMS 复
制容量，以便在配置所需容量的同时分析和复制数据。
https://examlearn.online
[2026/05]
Question #949
Topic 1
⼀家公司拥有⼀个多层Web应⽤程序。该应⽤程序的内部服务组件部署在Amazon EC2实例上。这些内部服务组
件需要访问托管在AWS上的第三⽅软件即服务（SaaS）API。
该公司需要提供从应⽤程序内部服务到第三⽅SaaS应⽤程序的安全私密连接，并确保将公共互联⽹暴露降⾄最
低。
哪种解决⽅案能够满⾜这些要求？
A. 实施 AWS 站点到站点 VPN，以与第三⽅ SaaS 提供商建⽴安全连接。
B. 部署 AWS Transit Gateway 来管理和路由应⽤程序的 VPC 和第三⽅ SaaS 提供商之间的流量。
C. 配置 AWS PrivateLink，仅允许 VPC 的出站流量，⽽不允许第三⽅ SaaS 提供商建⽴连接。
D. 使⽤ AWS PrivateLink 在应⽤程序的 VPC 和第三⽅ SaaS 提供商之间创建私有连接。
Question #950
哪个解决⽅案满⾜这些要求？
Topic 1
解决⽅案架构师需要将公司的企业⽹络连接到其虚拟私有云 (VPC)，以便允许本地⽤户访问其 AWS 资源。该解
决⽅案必须在⽹络层和会话层对企业⽹络和 VPC 之间的所有流量进⾏加密。此外，该解决⽅案还必须提供安全控
制措施，以防⽌ AWS 和本地系统之间不受限制的访问。
A. 配置 AWS Direct Connect 以连接到 VPC。根据需要配置 VPC 路由表，以允许或拒绝 AWS 与本地之间的
流量。
B. 创建 IAM 策略，仅允许从指定的企业 IP 地址访问 AWS 管理控制台。使⽤ IAM 策略和⻆⾊，根据⽤户职
责限制其访问权限。
C. 配置 AWS 站点到站点 VPN 连接到 VPConfigure 路由表条⽬，将来⾃本地的流量定向到 VPConfigure 实
例安全组和⽹络 ACL，以仅允许来⾃本地的必要流量。
D. 配置 AWS Transit Gateway 以连接到 VPC。配置路由表条⽬，将流量从本地定向到 VPC。配置实例安全
组和⽹络 ACL，仅允许来⾃本地的必要流量。
https://examlearn.online
[2026/05]
Question #951
Topic 1
⼀家公司有⼀个⾃定义应⽤程序，其中包含嵌⼊式凭证，⽤于从 Amazon RDS for MySQL 数据库集群中的数据
库检索信息。该公司需要以最⼩的编程⼯作量来提⾼应⽤程序的安全性。该公司已为应⽤程序⽤户在 RDS for
MySQL 数据库上创建了凭证。
哪种解决⽅案能够满⾜这些要求？
A. 将凭证存储在 AWS Key Management Service (AWS KMS) 中。在 AWS KMS 中创建密钥。配置应⽤程序
以从 AWS KMS 加载数据库凭证。启⽤⾃动密钥轮换
B. 将凭据存储在加密的本地存储中。配置应⽤程序从本地存储加载数据库凭据。通过创建 cron 作业来设置凭
据轮换计划。
C. 将凭证存储在 AWS Secrets Manager 中。配置应⽤程序以从 Secrets Manager 加载数据库凭证。通过为
Secrets Manager 创建 AWS Lambda 函数来设置凭证轮换计划。
D. 将凭证存储在 AWS Systems Manager Parameter Store 中。配置应⽤程序以从 Parameter Store 加载数
据库凭证。使⽤ Parameter Store 在 RDS for MySQL 数据库中设置凭证轮换计划。
Question #952
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司希望将其应⽤程序迁移到⽆服务器解决⽅案。该⽆服务器解决⽅案需要使⽤ SQL 分析现有数据和新数
据。公司将数据存储在 Amazon S3 存储桶中。数据必须进⾏静态加密，并复制到不同的 AWS 区域。
A. 创建⼀个新的 S3 存储桶，使⽤ AWS KMS 多区域密钥进⾏服务器端加密 (SSE-KMS)。配置跨区域复制
(CRR)。将数据加载到新的 S3 存储桶中。使⽤ Amazon Athena 查询数据。
B. 创建⼀个新的 S3 存储桶，使⽤ Amazon S3 管理密钥进⾏服务器端加密 (SSE-S3)。配置跨区域复制
(CRR)。将数据加载到新的 S3 存储桶中。使⽤ Amazon RDS 查询数据。
C. 在现有 S3 存储桶上配置跨区域复制 (CRR)。使⽤ Amazon S3 管理密钥进⾏服务器端加密 (SSE-S3)。使
⽤ Amazon Athena 查询数据。
D. 在现有 S3 存储桶上配置 S3 跨区域复制 (CRR)。使⽤ AWS KMS 多区域密钥 (SSE-KMS) 进⾏服务器端加
密。使⽤ Amazon RDS 查询数据。
https://examlearn.online
[2026/05]
Question #953
⼀家公司拥有⼀个拥有数千⽤户的⽹络应⽤程序。该应⽤程序使⽤⽤户上传的 8-10 张图⽚来⽣成 AI 图像。⽤户
可以每 6 ⼩时下载⼀次⽣成的 AI 图像。该公司还提供⾼级⽤户选项，允许⽤户随时下载⽣成的 AI 图像。
该公司每年使⽤⽤户上传的图⽚进⾏两次 AI 模型训练。该公司需要⼀个存储解决⽅案来存储这些图像。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
A. 将上传的图像移动到 Amazon S3 Glacier Deep Archive。将⾼级⽤户⽣成的 AI 图像移动到 S3
Standard。将⾮⾼级⽤户⽣成的 AI 图像移动到 S3 Standard-Infrequent Access (S3 Standard-IA)。
B. 将上传的图像移动到 Amazon S3 Glacier Deep Archive，将所有⽣成的 AI 图像移动到 S3 Glacier
Flexible Retrieval。
C. 将上传的图像移⾄ Amazon S3 单区-不频繁访问 (S3 单区-IA)。将⾼级⽤户⽣成的 AI 图像移⾄ S3 标准。
将⾮⾼级⽤户⽣成的 AI 图像移⾄ S3 标准-不频繁访问 (S3 标准-IA)。
D. 将上传的图像移动到 Amazon S3 单区低频访问 (S3 One Zone-IA)。将所有⽣成的 AI 图像移动到 S3
Glacier 灵活检索。
https://examlearn.online
[2026/05]
Question #954
⼀家公司正在 AWS 上开发机器学习 (ML) 模型。该公司将这些 ML 模型开发为独⽴的微服务。这些微服务在启动
时从 Amazon S3 获取约 1 GB 的模型数据并将其加载到内存中。⽤户通过异步 API 访问这些 ML 模型。⽤户可以
发送单个请求或批量请求。
该公司向数百名⽤户提供这些 ML 模型。这些模型的使⽤模式不规律。有些模型可能数天甚⾄数周⽆⼈使⽤，⽽
另⼀些模型则会⼀次性接收数千个请求。
哪种解决⽅案能够满⾜这些要求？
A. 将 API 请求定向到⽹络负载均衡器 (NLB)。将机器学习模型部署为 NLB 将调⽤的 AWS Lambda 函数。使
⽤⾃动扩展功能，根据 NLB 接收到的流量来扩展 Lambda 函数。
CPU (vCPU) 数量。
Topic 1
B. 将来⾃ API 的请求定向到应⽤程序负载均衡器 (ALB)。将机器学习模型部署为 Amazon Elastic Container
Service (Amazon ECS) 服务，供 ALB 调⽤。使⽤⾃动扩展功能，根据 ALB 接收到的流量来扩展 ECS 集群
实例。
C. 将来⾃ API 的请求定向到 Amazon Simple Queue Service (Amazon SQS) 队列。将机器学习模型部署为
AWS Lambda 函数，由 SQS 事件调⽤。使⽤⾃动扩展功能，根据 SQS 队列的⼤⼩增加 Lambda 函数的虚拟
D. 将来⾃ API 的请求定向到 Amazon Simple Queue Service (Amazon SQS) 队列。将机器学习模型部署为
Amazon Elastic Container Service (Amazon ECS) 服务，并从该队列读取数据。使⽤ Amazon ECS 的⾃动
扩展功能，根据 SQS 队列的⼤⼩扩展集群容量和服务数量。
https://examlearn.online
[2026/05]
Question #955
⼀家公司在 Amazon EC2 实例上运⾏⼀个 Web 应⽤程序，该实例位于 Auto Scaling 组中，并由应⽤程序负载均
衡器 (ALB) 管理。该应⽤程序将数据存储在 Amazon Aurora MySQL 数据库集群中。
该公司需要创建⼀个灾难恢复 (DR) 解决⽅案。DR 解决⽅案可接受的恢复时间不超过 30 分钟。当主基础设施运
⾏正常时，DR 解决⽅案⽆需⽀持客户使⽤。
哪种解决⽅案能够满⾜这些要求？
A. 在第⼆个 AWS 区域部署灾难恢复基础设施，包括应⽤负载均衡器 (ALB) 和⾃动扩展组。将⾃动扩展组的
期望容量和最⼤容量设置为最⼩值。将 Aurora MySQL 数据库集群转换为 Aurora 全局数据库。配置 Amazon
Route 53 以实现主备故障转移，并使⽤ ALB 端点。
Topic 1
B. 在第⼆个 AWS 区域部署灾难恢复基础设施，并更新⾃动扩展组，使其包含来⾃第⼆个区域的 EC2 实例。
使⽤ Amazon Route 53 配置主动-主动故障转移。将 Aurora MySQL 数据库集群转换为 Aurora 全局数据
库。
C. 使⽤ AWS Backup 备份 Aurora MySQL 数据库集群数据。在第⼆个 AWS 区域中部署灾难恢复基础设施，
并配置应⽤负载均衡器 (ALB)。更新⾃动扩展组，使其包含来⾃第⼆个区域的 EC2 实例。使⽤ Amazon
Route 53 配置主动-主动故障转移。在第⼆个区域中创建 Aurora MySQL 数据库集群。从备份恢复数据。
D. 使⽤ AWS Backup 备份基础设施配置。使⽤备份在另⼀个 AWS 区域中创建所需的基础设施。将⾃动扩展
组的期望容量设置为零。使⽤ Amazon Route 53 配置主备故障转移。将 Aurora MySQL 数据库集群转换为
Aurora 全局数据库。
https://examlearn.online
[2026/05]
Question #956
Topic 1
⼀家公司正在将其数据处理应⽤程序迁移到 AWS 云。该应⽤程序处理多个不能中断的短期批处理作业。每个批
处理作业完成后都会⽣成数据。数据访问期限为 30 天，保留期限为 2 年。
该公司希望尽可能降低在 AWS 云上运⾏该应⽤程序的成本。
哪种解决⽅案能够满⾜这些要求？
A. 将数据处理应⽤程序迁移到 Amazon EC2 Spot 实例。将数据存储在 Amazon S3 标准版中。将数据迁移
到 Amazon S3 Glacier 即时版。30 天后检索数据。设置数据过期时间，2 年后删除数据。
B. 将数据处理应⽤程序迁移到 Amazon EC2 按需实例。将数据存储在 Amazon S3 Glacier 即时检索中。30
天后将数据移动到 S3 Glacier 深度归档。设置数据过期时间，在 2 年后删除数据。
C. 部署 Amazon EC2 Spot 实例来运⾏批处理作业。将数据存储在 Amazon S3 标准存储中。30 天后将数据
迁移到 Amazon S3 Glacier 灵活检索存储。设置数据过期时间，在 2 年后删除数据。
D. 部署 Amazon EC2 按需实例来运⾏批处理作业。将数据存储在 Amazon S3 标准存储中。30 天后将数据
迁移到 Amazon S3 Glacier 深度归档存储。设置数据过期时间，2 年后删除数据。
Question #957
Topic 1
⼀家公司需要设计混合⽹络架构。该公司的⼯作负载⽬前存储在 AWS 云和本地数据中⼼中。这些⼯作负载需要
个位数延迟才能进⾏通信。该公司使⽤ AWS Transit Gateway 传输⽹关连接多个 VPC。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 为每个 VPC 建⽴ AWS 站点到站点 VPN 连接。
B. 将 AWS Direct Connect ⽹关与连接到 VPC 的传输⽹关关联起来。
C. 建⽴与 AWS Direct Connect ⽹关的 AWS 站点到站点 VPN 连接。
D. 建⽴ AWS Direct Connect 连接。创建到 Direct Connect ⽹关的传输虚拟接⼝ (VIF)。
E. 将 AWS 站点到站点 VPN 连接与连接到 VPC 的传输⽹关关联起来。
https://examlearn.online
[2026/05]
Question #958
Topic 1
⼀家全球电⼦商务公司在 AWS 上运⾏其关键⼯作负载。这些⼯作负载使⽤配置为多可⽤区部署的 Amazon RDS
for PostgreSQL 数据库实例。
客户报告称，当该公司进⾏数据库故障转移时，应⽤程序会出现超时。该公司需要⼀个弹性解决⽅案来缩短故障
转移时间。
哪种解决⽅案能够满⾜这些要求？
A. 创建 Amazon RDS 代理。将代理分配给数据库实例。
B. 为数据库实例创建只读副本。将读取流量转移到只读副本。
C. 启⽤性能分析功能。监控 CPU 负载以识别超时情况。
D. 定期进⾏⾃动快照。将⾃动快照复制到多个 AWS 区域。
Question #959
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
RDS 实例。
⽌ RDS 实例。
Topic 1
⼀家公司在开发环境的 AWS 账户中运⾏多个 Amazon RDS 数据库实例。所有实例都带有标签，以表明它们是开
发资源。该公司需要这些开发数据库实例仅在⼯作时间内按计划运⾏。
A. 创建 Amazon CloudWatch 警报以识别需要停⽌的 RDS 实例。创建 AWS Lambda 函数来启动和停⽌
B. 创建 AWS Trusted Advisor 报告，以确定要启动和停⽌的 RDS 实例。创建 AWS Lambda 函数来启动和停
C. 创建 AWS Systems Manager State Manager 关联以启动和停⽌ RDS 实例。
D. 创建⼀个 Amazon EventBridge 规则，调⽤ AWS Lambda 函数来启动和停⽌ RDS 实例。
https://examlearn.online
[2026/05]
Question #960
Topic 1
⼀家消费者调查公司多年来⼀直在特定地理区域收集数据。该公司将这些数据存储在 AWS 区域的 Amazon S3 存
储桶中。现在，
该公司开始与⼀家位于新地理区域的营销公司共享这些数据。该公司已授予该营销公司对其 AWS 账户访问 S3 存
储桶的权限。该公司希望在营销公司从 S3 存储桶请求数据时，尽可能降低数据传输成本。
哪种解决⽅案能够满⾜这些要求？
A. 在公司的 S3 存储桶上配置请求者付费功能。
B. 配置公司 S3 存储桶到营销公司 S3 存储桶之⼀的 S3 跨区域复制 (CRR)。
C. 配置 AWS Resource Access Manager 以与营销公司 AWS 账户共享 S3 存储桶。
D. 配置公司的 S3 存储桶以使⽤ S3 智能分层，并将 S3 存储桶同步到营销公司的⼀个 S3 存储桶。
Question #961
Topic 1
⼀家公司使⽤ AWS 托管其公共电⼦商务⽹站。该⽹站使⽤ AWS Global Accelerator 加速器处理来⾃互联⽹的流
量。Global Accelerator 加速器将流量转发到应⽤程序负载均衡器 (ALB)，ALB 是⾃动扩展组的⼊⼝点。
该公司最近发现其⽹站遭受了 DDoS 攻击。该公司需要⼀个解决⽅案来缓解未来的攻击。
哪种解决⽅案能够以最⼩的实施⼯作量满⾜这些要求？
A. 为 Global Accelerator 加速器配置 AWS WAF Web ACL，以使⽤基于速率的规则阻⽌流量。
B. 配置 AWS Lambda 函数读取 ALB 指标，通过更新 VPC ⽹络 ACL 来阻⽌攻击。
C. 在 ALB 上配置 AWS WAF Web ACL，以使⽤基于速率的规则阻⽌流量。
D. 在 Global Accelerator 加速器前端配置 Amazon CloudFront 分发
https://examlearn.online
[2026/05]
Question #962
Topic 1
⼀家公司使⽤ Amazon DynamoDB 表来存储从设备接收的数据。该 DynamoDB 表⽀持⼀个⾯向客户的⽹站，⽤
于显示客户设备的最新活动。该公司已为该表配置了写⼊和读取的预置吞吐量。
该公司希望每⽇计算客户设备数据的性能指标。该解决⽅案必须尽可能减少对表预置读取和写⼊容量的影响。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon Athena SQL 查询和 Amazon Athena DynamoDB 连接器按周期性计划计算性能指标。
B. 使⽤ AWS Glue 作业和 AWS Glue DynamoDB 导出连接器按周期性计划计算性能指标。
C. 使⽤ Amazon Redshift COPY 命令按周期性计划计算性能指标。
D. 使⽤ Amazon EMR 作业和 Apache Hive 外部表按周期性计划计算性能指标。
Question #963
A solutions architect is designing the cloud architecture for a new stateless application that will be
deployed on AWS. The solutions architect created an Amazon Machine Image (AMI) and launch template
for the application.
Which solution will meet these requirements?
Topic 1
Based on the number of jobs that need to be processed, the processing must run in parallel while adding
and removing application Amazon EC2 instances as needed. The application must be loosely coupled.
The job items must be durably stored.
A. Create an Amazon Simple Notification Service (Amazon SNS) topic to send the jobs that need to be
processed. Create an Auto Scaling group by using the launch template with the scaling policy set to
add and remove EC2 instances based on CPU usage.
B. Create an Amazon Simple Queue Service (Amazon SQS) queue to hold the jobs that need to be
processed. Create an Auto Scaling group by using the launch template with the scaling policy set to
add and remove EC2 instances based on network usage.
C. Create an Amazon Simple Queue Service (Amazon SQS) queue to hold the jobs that need to be
processed. Create an Auto Scaling group by using the launch template with the scaling policy set to
add and remove EC2 instances based on the number of items in the SQS queue.
D. Create an Amazon Simple Notification Service (Amazon SNS) topic to send the jobs that need to be
processed. Create an Auto Scaling group by using the launch template with the scaling policy set to
add and remove EC2 instances based on the number of messages published to the SNS topic.
https://examlearn.online
[2026/05]
Question #964
Topic 1
⼀家全球电⼦商务公司采⽤单体架构。该公司需要⼀个解决⽅案来管理⽇益增⻓的产品数据量。该解决⽅案必须
具有可扩展性和模块化服务架构。该公司需要维护其结构化数据库模式。此外，该公司还需要⼀个存储解决⽅案
来存储产品数据和产品图⽚。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤⾃动扩展组中的 Amazon EC2 实例部署容器化应⽤程序。使⽤应⽤程序负载均衡器分配 Web 流量。
使⽤ Amazon RDS 数据库实例存储产品数据和产品图⽚。
B. 使⽤ AWS Lambda 函数管理现有的单体应⽤程序。使⽤ Amazon DynamoDB 存储产品数据和产品图⽚。
使⽤ Amazon Simple Notification Service (Amazon SNS) 实现 Lambda 函数之间的事件驱动型通信。
C. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 和 Amazon EC2 部署容器化应⽤程序。使⽤
Amazon Aurora 集群存储产品数据。使⽤ AWS Step Functions 管理⼯作流。将产品镜像存储在 Amazon
S3 Glacier Deep Archive 中。
D. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 AWS Fargate 部署容器化应⽤程序。使⽤
Amazon RDS 的多可⽤区部署来存储产品数据。将产品图⽚存储在 Amazon S3 存储桶中。
Question #965
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在将⼀个应⽤程序从本地环境迁移到 AWS。该应⽤程序会将敏感数据存储在 Amazon S3 中。该公司
必须在将数据存储到 Amazon S3 之前对其进⾏加密。
A. 使⽤客户端加密和客户管理的密钥对数据进⾏加密。
B. 使⽤ AWS KMS 密钥（SSE-KMS）进⾏服务器端加密，从⽽对数据进⾏加密。
C. 使⽤客户提供的密钥通过服务器端加密（SSE-C）对数据进⾏加密。
D. 使⽤ Amazon S3 管理的密钥通过客户端加密对数据进⾏加密。
https://examlearn.online
[2026/05]
Question #966
Topic 1
⼀家公司希望创建⼀个供多个团队使⽤的 Amazon EMR 集群。该公司希望确保每个团队的⼤数据⼯作负载只能
访问其⾃身需要交互的 AWS 服务。该公司不希望⼯作负载能够访问集群底层 EC2 实例上的实例元数据服务版本
2 (IMDSv2)。
哪种解决⽅案能够满⾜这些要求？
A. 为团队所需的每个 AWS 服务配置接⼝ VPC 端点。使⽤所需的接⼝ VPC 端点提交⼤数据⼯作负载。
B. 创建EMR运⾏时⻆⾊。配置集群以使⽤这些运⾏时⻆⾊。使⽤运⾏时⻆⾊提交⼤数据⼯作负载。
C. 为每个团队创建⼀个具有所需权限的 EC2 IAM 实例配置⽂件。使⽤该实例配置⽂件提交⼤数据⼯作负载。
D. 创建⼀个 EMR 安全配置，并将 EnableApplicationScopedIAMRole 选项设置为 false。使⽤此安全配置提
交⼤数据⼯作负载。
Question #967
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀位解决⽅案架构师正在设计⼀个帮助⽤户填写并提交注册表单的应⽤程序。该架构师计划采⽤两层架构，包括
⼀个 Web 应⽤服务器层和⼀个⼯作层。
该应⽤程序需要快速处理提交的表单，并且每个表单必须只被处理⼀次。此外，该解决⽅案必须确保数据不会丢
失。
A. 在 Web 应⽤程序服务器层和⼯作层之间使⽤ Amazon Simple Queue Service (Amazon SQS) FIFO 队列
来存储和转发表单数据。
B. 在 Web 应⽤程序服务器层和⼯作层之间使⽤ Amazon API Gateway HTTP API 来存储和转发表单数据。
C. 在 Web 应⽤程序服务器层和⼯作层之间使⽤ Amazon Simple Queue Service (Amazon SQS) 标准队列来
存储和转发表单数据。
D. 使⽤ AWS Step Functions ⼯作流。在 Web 应⽤程序服务器层和⼯作层之间创建同步⼯作流，⽤于存储和
转发表单数据。
https://examlearn.online
[2026/05]
Question #968
Topic 1
⼀家⾦融公司使⽤本地部署的搜索应⽤程序从各种数据源收集流数据。该应⽤程序提供搜索和可视化功能的实时
更新。
该公司计划迁移到 AWS，并希望使⽤ AWS 原⽣解决⽅案。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon EC2 实例将数据流摄取并处理后存储到 Amazon S3 存储桶中。使⽤ Amazon Athena 搜索
数据。使⽤ Amazon Managed Grafana 创建可视化图表。
B. 使⽤ Amazon EMR 将数据流摄取并处理后存储到 Amazon Redshift。使⽤ Amazon Redshift Spectrum
搜索数据。使⽤ Amazon QuickSight 创建可视化图表。
C. 使⽤ Amazon Elastic Kubernetes Service (Amazon EKS) 将数据流摄取并处理后存储到 Amazon
DynamoDB 中。使⽤ Amazon CloudWatch 创建图形化仪表板，以便搜索和可视化数据。
D. 使⽤ Amazon Kinesis Data Streams 将数据流摄取并处理到 Amazon OpenSearch Service。使⽤
OpenSearch Service 搜索数据。使⽤ Amazon QuickSight 创建可视化图表。
Question #969
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
Topic 1
⼀家公司⽬前在 Linux 机器上运⾏⼀个基于 ASP.NET 的本地应⽤程序。该应⽤程序资源密集型，直接服务于客
户。
该公司希望将该应⽤程序现代化改造为 .NET 平台。该公司希望将应⽤程序运⾏在容器中，并根据 Amazon
CloudWatch 指标进⾏扩展。此外，该公司还希望减少运维活动所花费的时间。
A. 使⽤ AWS App2Container 将应⽤程序容器化。使⽤ AWS CloudFormation 模板将应⽤程序部署到 AWS
Fargate 上的 Amazon Elastic Container Service (Amazon ECS)。
B. 使⽤ AWS App2Container 将应⽤程序容器化。使⽤ AWS CloudFormation 模板将应⽤程序部署到
Amazon EC2 实例上的 Amazon Elastic Container Service (Amazon ECS)。
C. 使⽤ AWS App Runner 将应⽤程序容器化。使⽤ App Runner 将应⽤程序部署到 AWS Fargate 上的
Amazon Elastic Container Service (Amazon ECS)。
D. 使⽤ AWS App Runner 将应⽤程序容器化。使⽤ App Runner 将应⽤程序部署到 Amazon EC2 实例上的
Amazon Elastic Kubernetes Service (Amazon EKS)。
https://examlearn.online
[2026/05]
Question #970
Topic 1
⼀家公司正在AWS云上设计⼀个新的内部Web应⽤程序。该应⽤程序必须能够安全地从AWS托管服务中检索和存
储多个员⼯的⽤户名和密码。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 将员⼯凭证存储在 AWS Systems Manager Parameter Store 中。使⽤ AWS CloudFormation 和
BatchGetSecretValue API 从 Parameter Store 中检索⽤户名和密码。
B. 将员⼯凭证存储在 AWS Secrets Manager 中。使⽤ AWS CloudFormation 和 AWS Batch 以及
BatchGetSecretValue API 从 Secrets Manager 中检索⽤户名和密码。
C. 将员⼯凭证存储在 AWS Systems Manager Parameter Store 中。使⽤ AWS CloudFormation 和 AWS
Batch 以及 BatchGetSecretValue API 从 Parameter Store 中检索⽤户名和密码。
D. 将员⼯凭证存储在 AWS Secrets Manager 中。使⽤ AWS CloudFormation 和 BatchGetSecretValue API
从 Secrets Manager 中检索⽤户名和密码。
Question #971
The company must reduce the deployment latency for new software versions.
Topic 1
A company that is in the ap-northeast-1 Region has a fleet of thousands of AWS Outposts servers. The
company has deployed the servers at remote locations around the world. All the servers regularly
download new software versions that consist of 100 files. There is significant latency before all servers
run the new software versions.
Which solution will meet this requirement with the LEAST operational overhead?
A. Create an Amazon S3 bucket in ap-northeast-1. Set up an Amazon CloudFront distribution in ap
northeast-1 that includes a CachingDisabled cache policy. Configure the S3 bucket as the origin.
Download the software by using signed URLs.
B. Create an Amazon S3 bucket in ap-northeast-1. Create a second S3 bucket in the us-east-1 Region.
Configure replication between the buckets. Set up an Amazon CloudFront distribution that uses ap
northeast-1 as the primary origin and us-east-1 as the secondary origin. Download the software by
using signed URLs.
C. Create an Amazon S3 bucket in ap-northeast-1. Configure Amazon S3 Transfer Acceleration.
Download the software by using the S3 Transfer Acceleration endpoint.
D. Create an Amazon S3 bucket in ap-northeast-1. Set up an Amazon CloudFront distribution.
Configure the S3 bucket as the origin. Download the software by using signed URLs.
https://examlearn.online
[2026/05]
Question #972
⼀家公司⽬前使⽤ Microsoft Windows Server 运⾏本地股票交易应⽤程序。该公司希望将该应⽤程序迁移到
AWS 云。
该公司需要设计⼀个⾼可⽤性解决⽅案，以提供跨多个可⽤区对块存储的低延迟访问。
哪种解决⽅案能够以最⼩的实施⼯作量满⾜这些要求？
A. 在 Amazon EC2 实例上配置跨越两个可⽤区的 Windows Server 集群。在两个集群节点上安装应⽤程序。
使⽤ Amazon FSx for Windows File Server 作为两个集群节点之间的共享存储。
统接⼝ (iSCSI) 协议访问数据。
Topic 1
B. 在 Amazon EC2 实例上配置跨越两个可⽤区的 Windows Server 集群。在两个集群节点上安装应⽤程序。
使⽤ Amazon Elastic Block Store (Amazon EBS) 通⽤ SSD (gp3) 卷作为附加到 EC2 实例的存储。设置应
⽤程序级复制，将⼀个可⽤区中的 EBS 卷中的数据同步到另⼀个可⽤区中的 EBS 卷。
C. 将应⽤程序部署在两个可⽤区的 Amazon EC2 实例上。将⼀个 EC2 实例配置为活动实例，另⼀个 EC2 实
例配置为备⽤实例。使⽤ Amazon FSx for NetApp ONTAP Multi-AZ ⽂件系统，通过 Internet ⼩型计算机系
D. 将应⽤程序部署在两个可⽤区中的 Amazon EC2 实例上。将⼀个 EC2 实例配置为活动状态，另⼀个 EC2
实例配置为备⽤状态。使⽤ Amazon Elastic Block Store (Amazon EBS) 预置 IOPS SSD (io2) 卷作为附加到
EC2 实例的存储。设置 Amazon EBS 级别的复制，以将⼀个可⽤区中的⼀个 io2 卷中的数据同步到另⼀个可
⽤区中的另⼀个 io2 卷。
https://examlearn.online
[2026/05]
Question #973
⼀家公司正在设计⼀个带有⾯向互联⽹的应⽤负载均衡器 (ALB) 的 Web 应⽤程序。
Topic 1
该公司需要 ALB 接收来⾃公共互联⽹的 HTTPS Web 流量。ALB 必须仅将 HTTPS 流量发送到托管在 Amazon
EC2 实例上的 Web 应⽤程序服务器（端⼝ 443）。ALB 必须通过 HTTPS（端⼝ 8443）对 Web 应⽤程序服务
器执⾏健康检查。
与 ALB 关联的安全组的哪些配置组合可以满⾜这些要求？（选择三个。）
A. 允许来⾃ 0.0.0.0/0 的 HTTPS ⼊站流量，端⼝为 443。
B. 允许所有出站流量到 0.0.0.0/0 的 443 端⼝。
C. 允许通过端⼝ 443 向 Web 应⽤程序实例发送 HTTPS 出站流量。
D. 允许来⾃ Web 应⽤程序实例的 HTTPS ⼊站流量通过端⼝ 443。
E. 允许通过 8443 端⼝向 Web 应⽤程序实例发送 HTTPS 出站流量以进⾏健康检查。
F. 允许来⾃ Web 应⽤程序实例的 HTTPS ⼊站流量，以在端⼝ 8443 上进⾏健康检查。
Question #974
Topic 1
⼀家公司在 AWS 上托管了⼀个应⽤程序。该应⽤程序允许⽤户上传照⽚并将其存储在 Amazon S3 存储桶中。该
公司希望使⽤ Amazon CloudFront 和⾃定义域名将照⽚⽂件上传到位于 eu-west-1 区域的 S3 存储桶。
以下哪个解决⽅案可以满⾜这些要求？（选择两个。）
A. 使⽤ AWS Certificate Manager (ACM) 在 us-east-1 区域创建公共证书。在 CloudFront 中使⽤该证书。
B. 使⽤ AWS Certificate Manager (ACM) 在 eu-west-1 区域创建公共证书。在 CloudFront 中使⽤该证书。
C. 配置 Amazon S3 以允许从 CloudFront 上传。配置 S3 传输加速。
D. 配置 Amazon S3 以允许从 CloudFront 源访问控制 (OAC) 上传。
E. 配置 Amazon S3 以允许从 CloudFront 上传⽂件。配置 Amazon S3 ⽹站端点。
https://examlearn.online
[2026/05]
Question #975
Topic 1
⼀家天⽓预报公司持续从各种传感器收集温度读数。现有的数据采集流程收集这些读数，并将它们聚合到更⼤的
Apache Parquet ⽂件中。然后，该流程使⽤客户端加密和 KMS 管理密钥 (CSE-KMS) 对⽂件进⾏加密。最后，
该流程将⽂件写⼊ Amazon S3 存储桶，并为每个⽇历⽇使⽤不同的前缀。
该公司希望偶尔对数据运⾏ SQL 查询，以计算特定⽇历⽇的样本移动平均值。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置 Amazon Athena 以读取加密⽂件。直接在 Amazon S3 中对数据运⾏ SQL 查询。
B. 使⽤ Amazon S3 Select 直接在 Amazon S3 中对数据运⾏ SQL 查询。
C. 配置 Amazon Redshift 以读取加密⽂件。使⽤ Redshift Spectrum 和 Redshift 查询编辑器 v2 直接在
Amazon S3 中对数据运⾏ SQL 查询。
D. 配置 Amazon EMR Serverless 以读取加密⽂件。使⽤ Apache SparkSQL 直接在 Amazon S3 中对数据运
⾏ SQL 查询。
Question #976
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在 AWS 上部署⼀款新应⽤。该应⽤将在多个 AWS 区域内多个可⽤区的多个 Amazon EC2 实例上运
⾏，并通过互联⽹提供访问。⽤户将来⾃世界各地。
该公司希望确保每个访问应⽤的⽤户都被分配到距离其位置最近的 EC2 实例。
A. 实施 Amazon Route 53 地理位置路由策略。使⽤⾯向互联⽹的应⽤程序负载均衡器将流量分配到同⼀区
域内的所有可⽤区。
B. 实施 Amazon Route 53 地理位置路由策略。使⽤⾯向互联⽹的⽹络负载均衡器将流量分配到同⼀区域内
的所有可⽤区。
C. 实施 Amazon Route 53 多值应答路由策略。使⽤⾯向互联⽹的应⽤程序负载均衡器将流量分配到同⼀区
域内的所有可⽤区。
D. 实施 Amazon Route 53 加权路由策略。使⽤⾯向互联⽹的⽹络负载均衡器将流量分配到同⼀区域内的所
有可⽤区。
https://examlearn.online
[2026/05]
Question #977
Topic 1
⼀家⾦融服务公司计划在 AWS 上推出⼀款新的应⽤程序来处理敏感的⾦融交易。该公司将把该应⽤程序部署在
Amazon EC2 实例上，并使⽤ Amazon RDS for MySQL 作为数据库。该公司的安全策略要求数据在静态存储和
传输过程中都必须加密。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤ AWS KMS 管理的密钥为 Amazon RDS for MySQL 配置静态数据加密。配置 AWS Certificate
Manager (ACM) SSL/TLS 证书以进⾏传输中数据加密。
B. 使⽤ AWS KMS 管理的密钥为 Amazon RDS for MySQL 配置静态数据加密。配置 IPsec 隧道以实现传输
中数据的加密。
C. 在将数据存储到 Amazon RDS for MySQL 之前，实施第三⽅应⽤级数据加密。配置 AWS Certificate
Manager (ACM) SSL/TLS 证书以进⾏传输加密。
D. 使⽤ AWS KMS 管理的密钥为 Amazon RDS for MySQL 配置静态数据加密。配置 VPN 连接以启⽤私有连
接，从⽽加密传输中的数据。
Question #978
Topic 1
⼀家公司正在将其本地 Oracle 数据库迁移到 Amazon RDS for Oracle 数据库。为了满⾜监管要求，该公司需要
保留数据 90 天。此外，该公司还必须能够将数据库恢复到特定时间点，恢复期限最⻓为 14 天。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 创建 Amazon RDS ⾃动备份。将保留期设置为 90 天。
B. 每天创建 Amazon RDS ⼿动快照。删除超过 90 天的⼿动快照。
C. 使⽤ Amazon Aurora Clone for Oracle 功能创建时间点还原。删除超过 90 天的克隆。
D. 使⽤ AWS Backup for Amazon RDS 创建⼀个保留期为 90 天的备份计划。
https://examlearn.online
[2026/05]
Question #979
⼀家公司正在开发⼀款新应⽤，该应⽤使⽤关系型数据库来存储⽤户数据和应⽤配置。该公司预计该应⽤的⽤户
数量将稳步增⻓。该公司预计数据库的使⽤情况将波动较⼤，以读取为主，偶尔会有写⼊操作。
该公司希望优化数据库解决⽅案的成本。该公司希望使⽤能够提供所需性能的 AWS 托管数据库解决⽅案。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
A. 将数据库部署在 Amazon RDS 上。使⽤预置 IOPS SSD 存储，以确保读写操作的⼀致性性能。
B. 将数据库部署在 Amazon Aurora Serverless 上，以便根据实际使⽤情况⾃动扩展数据库容量，从⽽适应
⼯作负载。
C. 将数据库部署在 Amazon DynamoDB 上。使⽤按需容量模式⾃动扩展吞吐量以适应⼯作负载。
D. 将数据库部署在 Amazon RDS 上。使⽤磁存储并使⽤只读副本来满⾜⼯作负载需求。
https://examlearn.online
[2026/05]
Question #980
Topic 1
⼀家公司将其应⽤程序托管在 VPC 内的多个 Amazon EC2 实例上。该公司为每个客户创建⼀个专⽤的 Amazon
S3 存储桶，⽤于存储其相关信息。
该公司希望确保运⾏在 EC2 实例上的应⽤程序只能安全地访问属于该公司 AWS 账户的 S3 存储桶。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 为 Amazon S3 创建⼀个连接到 VPC 的⽹关终端节点。更新 IAM 实例配置⽂件策略，使其仅访问应⽤程序
所需的特定存储桶。
B. 在公共⼦⽹中创建⼀个 NAT ⽹关，并创建⼀个安全组，该安全组仅允许访问 Amazon S3。更新路由表以
使⽤ NAT ⽹关。
C. 为 Amazon S3 创建⼀个⽹关终端节点，并将其附加到 VPUpdate。使⽤“拒绝”操作和以下条件键更新
IAM 实例配置⽂件策略：
D. 在公共⼦⽹中创建 NAT ⽹关。更新路由表以使⽤该 NAT ⽹关。为所有存储桶分配“拒绝”操作的存储桶策
略，并设置以下条件键：
https://examlearn.online
[2026/05]
Question #981
Topic 1
⼀家公司正在 AWS 上构建⼀个云应⽤程序，该应⽤程序将处理敏感的客户数据。该应⽤程序使⽤ Amazon RDS
作为数据库，Amazon S3 作为对象存储，并通过 S3 事件通知调⽤ AWS Lambda 进⾏⽆服务器处理。
该公司使⽤ AWS IAM Identity Center 管理⽤户凭证。开发、测试和运维团队需要安全地访问 Amazon RDS 和
Amazon S3，同时确保敏感客户数据的机密性。该解决⽅案必须遵循最⼩权限原则。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤权限最⼩的 IAM ⻆⾊授予所有团队访问权限。为每个团队分配 IAM ⻆⾊，并根据团队职责⾃定义 IAM
策略，定义 Amazon RDS 和 S3 对象访问的特定权限。
B. 启⽤ IAM 身份中⼼并创建身份中⼼⽬录。创建并配置权限集，以实现对 Amazon RDS 和 Amazon S3 的精
细访问控制。将所有团队分配到具有特定访问权限的权限组中。
C. 为所有团队中的每位成员创建具有基于⻆⾊权限的独⽴ IAM ⽤户。根据⽤户需求，为每个⽤户分配具有预
定义 RDS 和 S3 访问策略的 IAM ⻆⾊。实施 IAM 访问分析器，以定期评估凭证。
D. 使⽤ AWS Organizations 为每个团队创建单独的账户。实施跨账户 IAM ⻆⾊，并遵循最⼩权限原则。根
据团队⻆⾊和职责授予对 RDS 和 S3 的特定访问权限。
Question #982
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司拥有⼀个包含敏感数据⽂件的 Amazon S3 存储桶。该公司有⼀个应⽤程序运⾏在本地数据中⼼的虚拟
机上。该公司⽬前使⽤ AWS IAM Identity Center。
该应⽤程序需要临时访问 S3 存储桶中的⽂件。该公司希望授予该应⽤程序对 S3 存储桶中⽂件的安全访问权限。
A. 创建⼀个 S3 存储桶策略，允许从公司内部数据中⼼的公共 IP 地址范围访问该存储桶。
B. 使⽤ IAM Roles Anywhere 在 IAM Identity Center 中获取授予 S3 存储桶访问权限的安全凭证。使⽤
AWS CLI 配置虚拟机以承担该⻆⾊。
C. 在虚拟机上安装 AWS CLI。使⽤具有存储桶访问权限的 IAM ⽤户的访问密钥配置 AWS CLI。
D. 创建⼀个 IAM ⽤户和策略，授予其对存储桶的访问权限。将该 IAM ⽤户的访问密钥和秘密密钥存储在
AWS Secrets Manager 中。配置应⽤程序在启动时检索访问密钥和秘密密钥。
https://examlearn.online
[2026/05]
Question #983
Topic 1
⼀家公司将其核⼼⽹络服务（包括⽬录服务和 DNS）托管在其本地数据中⼼。该数据中⼼通过 AWS Direct
Connect (DX) 连接到 AWS 云。该公司计划创建更多 AWS 账户，这些账户需要快速、经济⾼效且稳定地访问这
些⽹络服务。
解决⽅案架构师应该如何实施才能以最⼩的运营开销满⾜这些需求？
A. 在每个新帐户中创建 DX 连接。将⽹络流量路由到本地服务器。
B. 在 DX VPC 中为所有必需的服务配置 VPC 端点。将⽹络流量路由到本地服务器。
C. 在每个新帐户和 DX VPRute 之间创建 VPN 连接，将⽹络流量路由到本地服务器。
D. 在账户之间配置 AWS Transit Gateway。将 DX 分配给 Transit Gateway，并将⽹络流量路由到本地服务
器。
Question #984
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司将其主要公共 Web 应⽤程序托管在同⼀个 AWS 区域，该区域跨越多个可⽤区。该应⽤程序使⽤
Amazon EC2 ⾃动扩展组和应⽤程序负载均衡器 (ALB)。Web
开发团队需要⼀个成本优化的计算解决⽅案，以提升公司向全球数百万客户提供动态内容的能⼒。
A. 创建 Amazon CloudFront 分发。将现有 ALB 配置为源。
B. 使⽤ Amazon Route 53 根据每个客户的地理位置向 ALB 和 EC2 实例提供流量。
C. 创建⼀个启⽤公共读取权限的 Amazon S3 存储桶。将 Web 应⽤程序迁移到该 S3 存储桶。配置该 S3 存
储桶以托管⽹站。
D. 使⽤ AWS Direct Connect 将 Web 应⽤程序的内容直接提供给每个客户的位置。
https://examlearn.online
[2026/05]
Question #985
Topic 1
⼀家公司将⽤户数据存储在 AWS 中。这些数据会被持续使⽤，⾼峰时段为⼯作时间。访问模式各不相同，有些
数据可能⼏个⽉都不会被使⽤。解决⽅案架构师必须选择⼀种既经济⾼效⼜能保持最⾼持久性和⾼可⽤性的解决
⽅案。
哪种存储解决⽅案符合这些要求？
A. Amazon S3 标准
B. Amazon S3 智能分层
C. Amazon S3 Glacier Deep 存档
D. Amazon S3 单区不频繁访问 (S3 单区-IA)
Question #986
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在测试⼀个运⾏在 Amazon EC2 Linux 实例上的应⽤程序。该 EC2 实例上挂载了⼀个 500 GB 的
Amazon Elastic Block Store (Amazon EBS) 通⽤型 SSO (gp2) 卷。
该公司计划将该应⽤程序部署到 Auto Scaling 组中的多个 EC2 实例上。所有实例都需要访问存储在 EBS 卷中的
数据。该公司需要⼀个⾼可⽤性和⾼弹性的解决⽅案，且该⽅案不能对应⽤程序代码进⾏重⼤更改。
A. 配置⼀个使⽤ NFS 服务器软件的 EC2 实例。将⼀个 500 GB 的 gp2 EBS 卷附加到该实例。
B. 为 Windows ⽂件服务器配置 Amazon FSx ⽂件系统。将⽂件系统配置为单个可⽤区内的 SMB ⽂件存
储。
C. 配置⼀个 EC2 实例，其中包含两个 250 GB 已配置 IOPS SSD EBS 卷。
D. 配置 Amazon Elastic File System (Amazon EFS) ⽂件系统。将⽂件系统配置为使⽤通⽤性能模式。
https://examlearn.online
[2026/05]
Question #987
Topic 1
⼀家公司最近为其客户推出了⼀款新应⽤程序。该应⽤程序运⾏在两个可⽤区内的多个 Amazon EC2 实例上。最
终⽤户使⽤ TCP 与应⽤程序通信。
该应⽤程序必须具备⾼可⽤性，并且能够随着⽤户数量的增加⾃动扩展。
以下哪两项措施组合能够以最具成本效益的⽅式满⾜这些要求？
A. 在 EC2 实例前⾯添加⽹络负载均衡器。
B. 为 EC2 实例配置⾃动扩展组。
C. 在 EC2 实例前⾯添加应⽤程序负载均衡器。
D. ⼿动为应⽤程序添加更多 EC2 实例。
E. 在 EC2 实例前⾯添加⽹关负载均衡器。
Question #988
以下哪两项步骤组合可以满⾜这些要求？（选择两项。）
值。将标签策略附加到相应的组织单元 (OU)。
Topic 1
⼀家公司正在为⼀款使⽤ AWS 云的新移动应⽤设计架构。该公司使⽤ AWS Organizations 中的组织单元 (OU)
来管理其账户。该公司希望使⽤“敏感”和“⾮敏感”值来标记 Amazon EC2 实例的数据敏感度。IAM 身份不得删除
标记或创建没有标记的实例。
A. 在“组织”中，创建⼀个新的标签策略，指定数据敏感性标签键及其所需值。强制 EC2 实例使⽤这些标签
B. 在组织中，创建⼀个新的服务控制策略 (SCP)，指定数据敏感性标签键和所需的标签值。强制 EC2 实例使
⽤这些标签值。将 SCP 附加到相应的组织单元 (OU)。
C. 创建⼀条标签策略，禁⽌在未指定标签键的情况下运⾏实例。创建另⼀条标签策略，阻⽌身份删除标签。
将这些标签策略附加到相应的组织单元 (OU)。
D. 创建⼀条服务控制策略 (SCP)，禁⽌在未指定标签键的情况下创建实例。创建另⼀条 SCP，阻⽌身份删除
标签。将这些 SCP 附加到相应的组织单元 (OU)。
E. 创建⼀条 AWS Config 规则，检查 EC2 实例是否使⽤了数据敏感性标签及其指定的值。配置⼀个 AWS
Lambda 函数，以便在发现不合规资源时将其删除。
https://examlearn.online
[2026/05]
Question #989
Topic 1
⼀家公司在 AWS 上运⾏数据库⼯作负载，这些⼯作负载是公司客户⻔户的后端。该公司在 Amazon RDS 上运⾏
⼀个多可⽤区数据库集群，⽤于 PostgreSQL。
该公司需要实施 30 天的备份保留策略。该公司⽬前同时拥有⾃动 RDS 备份和⼿动 RDS 备份。该公司希望保留
所有现有 RDS 备份中不超过 30 天的备份。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 将 RDS 备份保留策略配置为 30 天，⽤于使⽤ AWS Backup 进⾏⾃动备份。⼿动删除超过 30 天的⼿动备
份。
B. 禁⽤ RDS ⾃动备份。删除超过 30 天的⾃动备份和⼿动备份。将 RDS ⾃动备份的保留策略配置为 30 天。
C. 将 RDS 备份保留策略配置为⾃动备份 30 天。⼿动删除超过 30 天的⼿动备份。
D. 禁⽤ RDS ⾃动备份。使⽤ AWS CloudFormation ⾃动删除超过 30 天的⾃动备份和⼿动备份。将 RDS ⾃
动备份的保留策略配置为 30 天。
Question #990
A. AWS 数据同步
Topic 1
⼀家公司计划将⼀个遗留应⽤程序迁移到 AWS。该应⽤程序⽬前使⽤ NFS 与本地存储解决⽅案通信以存储应⽤
程序数据。该应⽤程序⽆法修改以使⽤除 NFS 之外的任何其他通信协议。
解决⽅案架构师应该推荐在迁移后使⽤哪种存储解决⽅案？
B. Amazon Elastic Block Store (Amazon EBS)
C. Amazon Elastic File System (Amazon EFS)
D. Amazon EMR ⽂件系统 (Amazon EMRFS)
https://examlearn.online
[2026/05]
Question #991
Topic 1
⼀家公司使⽤ GPS 追踪器记录数千只海⻳的迁徙模式。追踪器每 5 分钟检查⼀次海⻳是否移动超过 100 码
（91.4 ⽶）。如果海⻳移动了，追踪器会将新的坐标发送到运⾏在三个 Amazon EC2 实例上的 Web 应⽤程序，
这些实例位于同⼀ AWS 区域的多个可⽤区中。
最近，该 Web 应⽤程序在处理意外的⼤量追踪器数据时不堪重负，导致数据丢失且⽆法重现。解决⽅案架构师必
须防⽌此类问题再次发⽣，并且需要⼀种运维开销最⼩的解决⽅案。
为了满⾜这些要求，解决⽅案架构师应该怎么做？
A. 创建⼀个 Amazon S3 存储桶来存储数据。配置应⽤程序以扫描存储桶中的新数据进⾏处理。
B. 创建⼀个 Amazon API Gateway 端点来处理传输的位置坐标。使⽤ AWS Lambda 函数并发处理每个项
⽬。
C. 创建⼀个 Amazon Simple Queue Service (Amazon SQS) 队列来存储传⼊的数据。配置应⽤程序轮询新
消息以进⾏处理。
D. 创建⼀个 Amazon DynamoDB 表来存储传输的位置坐标。配置应⽤程序以查询该表以获取要处理的新数
据。使⽤ TTL（⽣存时间）来删除已处理的数据。
Question #992
公司必须确保开发团队在办公室时能够通过客户端连接到该集群。
哪种解决⽅案能够以最安全的⽅式提供所需的连接？
Topic 1
⼀家公司的软件开发团队需要⼀个 Amazon RDS 多可⽤区集群。该 RDS 集群将作为部署在公司内部的桌⾯客户
端的后端。桌⾯客户端需要直接连接到 RDS 集群。
A. 创建⼀个 VPC 和两个公有⼦⽹。在公有⼦⽹中创建 RDS 集群。使⽤ AWS Site-to-Site VPN，并在公司办
公室部署客户⽹关。
B. 创建⼀个 VPC 和两个私有⼦⽹。在私有⼦⽹中创建 RDS 集群。使⽤ AWS Site-to-Site VPN，并在公司办
公室部署客户⽹关。
C. 创建⼀个 VPC 和两个私有⼦⽹。在私有⼦⽹中创建 RDS 集群。使⽤ RDS 安全组允许公司办公室的 IP 地
址范围访问该集群。
D. 创建⼀个 VPC 和两个公有⼦⽹。在公有⼦⽹中创建 RDS 集群。为每位开发⼈员创建⼀个集群⽤户。使⽤
RDS 安全组允许⽤户访问集群。
https://examlearn.online
[2026/05]
Question #993
Topic 1
⼀位解决⽅案架构师正在创建⼀个应⽤程序，⽤于批量处理⼤量数据。输⼊数据将存储在 Amazon S3 中，输出
数据将存储在另⼀个 S3 存储桶中。为了进⾏处理，该应⽤程序将通过⽹络在多个 Amazon EC2 实例之间传输数
据。
解决⽅案架构师应该如何降低整体数据传输成本？
A. 将所有 EC2 实例放⼊⾃动扩展组中。
B. 将所有 EC2 实例放置在同⼀个 AWS 区域中。
C. 将所有 EC2 实例放置在同⼀个可⽤区中。
D. 将所有 EC2 实例放置在多个可⽤区的私有⼦⽹中。
Question #994
解决⽅案架构师应该如何做才能以最⼩的运维⼯作量满⾜此要求？
Topic 1
⼀家公司托管了⼀个多层 Web 应⽤程序，该应⽤程序使⽤ Amazon Aurora MySQL 数据库集群进⾏存储。应⽤
程序层托管在 Amazon EC2 实例上。该公司的 IT 安全准则规定，数据库凭证必须加密，并且每 14 天轮换⼀次。
A. 创建⼀个新的 AWS Key Management Service (AWS KMS) 加密密钥。使⽤ AWS Secrets Manager 创建
⼀个使⽤该 KMS 密钥和相应凭证的新密钥。将该密钥与 Aurora 数据库集群关联。配置 14 天的⾃定义轮换周
期。
B. 在 AWS Systems Manager Parameter Store 中创建两个参数：⼀个⽤于存储⽤户名（字符串类型），另⼀
个⽤于存储密码（SecureString 类型）。为密码参数选择 AWS Key Management Service (AWS KMS) 加
密，并将这些参数加载到应⽤层。实现⼀个 AWS Lambda 函数，每 14 天轮换⼀次密码。
C. 将包含凭证的⽂件存储在 AWS Key Management Service (AWS KMS) 加密的 Amazon Elastic File
System (Amazon EFS) ⽂件系统中。将 EFS ⽂件系统挂载到应⽤层的所有 EC2 实例上。限制对⽂件系统上
该⽂件的访问，以便应⽤程序可以读取该⽂件，并且只有超级⽤户可以修改该⽂件。实现⼀个 AWS Lambda
函数，该函数每 14 天在 Aurora 中轮换⼀次密钥，并将新的凭证写⼊该⽂件。
D. 将包含凭证的⽂件存储在 AWS Key Management Service (AWS KMS) 加密的 Amazon S3 存储桶中，应
⽤程序使⽤该存储桶加载凭证。定期将该⽂件下载到应⽤程序，以确保使⽤正确的凭证。实现⼀个 AWS
Lambda 函数，每 14 天轮换⼀次 Aurora 凭证，并将这些凭证上传到 S3 存储桶中的⽂件中。
https://examlearn.online
[2026/05]
Question #995
⼀家流媒体公司正在重建其基础设施，以满⾜⽤户⽇益增⻓的视频内容需求。
该公司需要处理TB级的视频，以屏蔽视频中的某些内容。视频处理可能需要⻓达20分钟。
该公司需要⼀种能够随着需求扩展且经济⾼效的解决⽅案。
哪种解决⽅案能够满⾜这些要求？
Topic 1
A. 使⽤ AWS Lambda 函数处理视频。将视频元数据存储在 Amazon DynamoDB 中。将视频内容存储在
Amazon S3 智能分层存储中。
B. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 AWS Fargate 实现微服务来处理视频。将视
频元数据存储在 Amazon Aurora 中。将视频内容存储在 Amazon S3 智能分层存储中。
C. 使⽤位于应⽤程序负载均衡器 (ALB) 后⾯的⾃动扩展组中的 Amazon EC2 实例来处理视频。将视频内容存
储在 Amazon S3 标准版中。使⽤ Amazon 简单队列服务 (Amazon SQS) 进⾏队列管理和解耦处理任务。
D. 在 Amazon EC2 上的 Amazon Elastic Kubernetes Service (Amazon EKS) 上部署容器化的视频处理应⽤
程序。将视频元数据存储在单个可⽤区的 Amazon RDS 中。将视频内容存储在 Amazon S3 Glacier Deep
Archive 中。
Question #996
Topic 1
⼀家公司在 Kubernetes 集群上运⾏本地应⽤程序。该公司最近新增了数百万客户。其现有的本地基础设施⽆法
应对如此庞⼤的新客户数量。该公司需要将本地应⽤程序迁移到 AWS 云。
该公司将迁移到 Amazon Elastic Kubernetes Service (Amazon EKS) 集群。该公司不希望管理 AWS 上新架构
的底层计算基础设施。
哪种解决⽅案能够以最⼩的运维开销满⾜这些要求？
A. 使⽤⾃管理节点提供计算能⼒。将应⽤程序部署到新的 EKS 集群。
B. 使⽤托管节点组提供计算能⼒。将应⽤程序部署到新的 EKS 集群。
C. 使⽤ AWS Fargate 提供计算能⼒。创建 Fargate 配置⽂件。使⽤该 Fargate 配置⽂件部署应⽤程序。
D. 使⽤ Karpenter 管理的节点组来提供计算能⼒。将应⽤程序部署到新的 EKS 集群。
https://examlearn.online
[2026/05]
Question #997
Topic 1
⼀家公司正在推出⼀款新应⽤，该应⽤需要⼀个结构化数据库来存储⽤户配置⽂件、应⽤设置和交易数据。该数
据库必须能够随着应⽤流量的增⻓⽽扩展，并且必须提供备份功能。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤开源软件在 Amazon EC2 实例上部署⾃管理数据库。使⽤竞价型实例以优化成本。配置⾃动备份到
Amazon S3。
B. 使⽤ Amazon RDS。数据库采⽤按需容量模式，并使⽤通⽤型 SSD 存储。配置⾃动备份，保留期为 7
天。
C. 使⽤ Amazon Aurora Serverless 作为数据库。启⽤⽆服务器容量扩展。配置⾃动备份到 Amazon S3。
D. 在 Amazon EC2 实例上部署⾃管理 NoSQL 数据库。使⽤预留实例以优化成本。配置⾃动备份，直接备份
到 Amazon S3 Glacier Flexible Retrieval。
Question #998
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司在 AWS 上运⾏其传统 Web 应⽤程序。该 Web 应⽤程序服务器运⾏在 VPC 公有⼦⽹中的 Amazon
EC2 实例上。该 Web 应⽤程序服务器从客户处收集图像，并将图像⽂件存储在本地连接的 Amazon Elastic
Block Store (Amazon EBS) 卷中。图像⽂件每晚都会上传到 Amazon S3 存储桶进⾏备份。
解决⽅案架构师发现图像⽂件是通过公有端点上传到 Amazon S3 的。解决⽅案架构师需要确保发送到 Amazon
S3 的流量不使⽤公有端点。
A. 为 S3 存储桶创建⼀个具有 VPC 必要权限的⽹关 VPC 端点。配置⼦⽹路由表以使⽤该⽹关 VPC 端点。
B. 将 S3 存储桶移⾄ VPC 内。配置⼦⽹路由表，以便通过私有 IP 地址访问 S3 存储桶。
C. 为 VP 内的 Amazon EC2 实例创建 Amazon S3 访问点，配置 Web 应⽤程序以使⽤ Amazon S3 访问点进
⾏上传。
D. 在拥有 Amazon EC2 实例的 VPC 和 Amazon S3 之间配置 AWS Direct Connect 连接，以提供专⽤⽹络
路径。
https://examlearn.online
[2026/05]
Question #999
Topic 1
⼀家公司正在 AWS 上构建⼀个电⼦商务⽹站原型。该⽹站包含⼀个应⽤程序负载均衡器、⼀个⽤于 Web 服务器
的 Amazon EC2 实例⾃动扩展组，以及⼀个运⾏在单可⽤区配置下的 Amazon RDS for MySQL 数据库实例。
在搜索产品⽬录时，⽹站响应速度很慢。产品⽬录是 MySQL 数据库中的⼀组表，该公司并不经常更新这些表。
解决⽅案架构师发现，在进⾏产品⽬录搜索时，数据库实例的 CPU 利⽤率很⾼。
为了提⾼⽹站在搜索产品⽬录时的性能，解决⽅案架构师应该提出哪些建议？
A. 将产品⽬录迁移到 Amazon Redshift 数据库。使⽤ COPY 命令加载产品⽬录表。
B. 部署⼀个 Amazon ElastiCache for Redis 集群来缓存产品⽬录。使⽤延迟加载来填充缓存。
C. 向⾃动扩展组添加额外的扩展策略，以便在数据库响应缓慢时启动额外的 EC2 实例。
D. 为数据库实例启⽤多可⽤区配置。配置 EC2 实例以限制发送到数据库的产品⽬录查询。
Question #1000
哪种解决⽅案能够以最⾼的运⾏效率满⾜这些要求？
Topic 1
⼀家公司⽬前在本地块存储系统中存储了 5 TB 的数据。该公司当前的存储解决⽅案提供的空间有限，⽆法满⾜
额外的数据需求。该公司在本地运⾏的应⽤程序必须能够以低延迟检索频繁访问的数据。该公司需要⼀个基于云
的存储解决⽅案。
A. 使⽤ Amazon S3 ⽂件⽹关。将 S3 ⽂件⽹关与本地应⽤程序集成，以使⽤ SMB ⽂件系统存储和直接检索
⽂件。
B. 使⽤ AWS Storage Gateway Volume Gateway，并将缓存卷作为 iSCSI ⽬标。
C. 使⽤ AWS Storage Gateway Volume Gateway，并将存储的卷作为 iSCSI ⽬标。
D. 使⽤ AWS Storage Gateway 磁带⽹关。将磁带⽹关与本地应⽤程序集成，以在 Amazon S3 中存储虚拟
磁带。
https://examlearn.online
[2026/05]
Question #1001
Topic 1
⼀家公司运营外卖服务。由于近期业务增⻓，该公司的订单处理系统在⾼峰时段⾯临扩展性问题。⽬前的架构包
含⼀组位于⾃动扩展组中的 Amazon EC2 实例，⽤于从应⽤程序收集订单。另⼀组位于⾃动扩展组中的 EC2 实
例⽤于处理订单。
订单收集过程快速，但订单处理过程可能需要更⻓时间。数据不能因扩展⽽丢失。
解决⽅案架构师必须确保订单收集过程和订单处理过程在⾼峰时段都能充分扩展。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon CloudWatch 监控两个⾃动扩展组中每个实例的 CPU 利⽤率指标。配置每个⾃动扩展组的
最⼩容量，以满⾜其峰值⼯作负载值。
B. 使⽤ Amazon CloudWatch 监控两个 Auto Scaling 组中每个实例的 CPU 利⽤率指标。配置 CloudWatch
警报，以调⽤ Amazon Simple Notification Service (Amazon SNS) 主题，从⽽按需创建额外的 Auto
Scaling 组。
C. 配置两个 Amazon Simple Queue Service (Amazon SQS) 队列。⼀个 SQS 队列⽤于订单收集，另⼀个
SQS 队列⽤于订单履⾏。配置 EC2 实例轮询各⾃的队列。根据队列发送的通知扩展⾃动扩展组。
D. 配置两个 Amazon Simple Queue Service (Amazon SQS) 队列。⼀个 SQS 队列⽤于订单收集，另⼀个
SQS 队列⽤于订单履⾏。配置 EC2 实例轮询各⾃的队列。根据每个队列中的消息数量扩展⾃动扩展组。
Question #1002
Topic 1
⼀家在线游戏公司正在将⽤户数据存储迁移到 Amazon DynamoDB，以⽀持其不断增⻓的⽤户群。⽬前的架构包
含 DynamoDB 表，其中存储着⽤户个⼈资料、成就和游戏内交易信息。
该公司需要设计⼀个强⼤、持续可⽤且具有弹性的 DynamoDB 架构，以确保⽤户获得流畅的游戏体验。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 在单个 AWS 区域中创建 DynamoDB 表。使⽤按需容量模式。使⽤全局表跨多个区域复制数据。
B. 使⽤ DynamoDB Accelerator (DAX) 缓存频繁访问的数据。将表部署在单个 AWS 区域中并启⽤⾃动扩
展。⼿动配置跨区域复制到其他区域。
C. 在多个 AWS 区域中创建 DynamoDB 表。使⽤按需容量模式。使⽤ DynamoDB Streams 实现区域间的跨
区域复制。
D. 使⽤ DynamoDB 全局表实现⾃动跨区域复制。将表部署在多个 AWS 区域中。使⽤预置容量模式。启⽤⾃
动扩展。
https://examlearn.online
[2026/05]
Question #1003
Topic 1
⼀家公司在本地运⾏其媒体渲染应⽤程序。该公司希望降低存储成本，已将所有数据迁移到 Amazon S3。该本地
渲染应⽤程序需要低延迟的存储访问。
该公司需要为该应⽤程序设计⼀个存储解决⽅案。该存储解决⽅案必须保持所需的应⽤程序性能。
哪种存储解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 使⽤ Mountpoint for Amazon S3 访问 Amazon S3 中的数据，以便本地应⽤程序使⽤。
B. 配置 Amazon S3 ⽂件⽹关，为本地应⽤程序提供存储。
C. 将数据从 Amazon S3 复制到 Amazon FSx for Windows ⽂件服务器。配置 Amazon FSx ⽂件⽹关，为本
地应⽤程序提供存储。
D. 配置本地⽂件服务器。使⽤ Amazon S3 API 连接到 S3 存储。配置应⽤程序以从本地⽂件服务器访问存
储。
Question #1004
Topic 1
⼀家公司将其企业资源计划 (ERP) 系统托管在 us-east-1 区域。该系统运⾏在 Amazon EC2 实例上。客户使⽤
托管在 EC2 实例上的公共 API 与 ERP 系统交换信息。国际客户反映其数据中⼼的 API 响应速度较慢。
哪种解决⽅案能够以最具成本效益的⽅式改善国际客户的响应速度？
A. 创建⼀个具有公共虚拟接⼝ (VIF) 的 AWS Direct Connect 连接，以提供从每个客户的数据中⼼到 us
east-1 的连接。使⽤ Direct Connect ⽹关将客户 API 请求路由到 ERP 系统 API。
B. 在 API 前端设置 Amazon CloudFront 分发。配置 CachingOptimized 托管缓存策略以提⾼缓存效率。
C. 设置 AWS Global Accelerator。为必要的端⼝配置监听器。为相应的区域配置终端节点组以分发流量。在
组中为 API 创建终端节点。
D. 使⽤ AWS 站点到站点 VPN 在区域和客户⽹络之间建⽴专⽤ VPN 隧道。通过 VPN 连接将流量路由到
API。
https://examlearn.online
[2026/05]
Question #1005
⼀家公司通过在其⽹站上开展的调查来追踪客户满意度。这些调查有时每⼩时能触达数千名客户。⽬前，调查结
果会以电⼦邮件的形式发送给公司，以便员⼯⼿动查看结果并评估客户情绪。
该公司希望实现客户调查流程的⾃动化。调查结果必须涵盖过去 12 个⽉。
哪种解决⽅案能够以最具可扩展性的⽅式满⾜这些要求？
A. 将调查结果数据发送到连接到 Amazon Simple Queue Service (Amazon SQS) 队列的 Amazon API
Gateway 端点。创建⼀个 AWS Lambda 函数来轮询 SQS 队列，调⽤ Amazon Comprehend 进⾏情感分
析，并将结果保存到 Amazon DynamoDB 表中。将所有记录的 TTL 设置为未来 365 天。
DynamoDB 表中。将所有记录的 TTL 设置为未来 365 天。
Topic 1
B. 将调查结果数据发送到运⾏在 Amazon EC2 实例上的 API。配置该 API，使其将调查结果作为新记录存储
在 Amazon DynamoDB 表中，调⽤ Amazon Comprehend 进⾏情感分析，并将结果保存到第⼆个
C. 将调查结果数据写⼊ Amazon S3 存储桶。使⽤ S3 事件通知调⽤ AWS Lambda 函数读取数据并调⽤
Amazon Rekognition 进⾏情感分析。将情感分析结果存储在第⼆个 S3 存储桶中。在每个存储桶上使⽤ S3
⽣命周期策略，使对象在 365 天后过期。
D. 将调查结果数据发送到连接到 Amazon Simple Queue Service (Amazon SQS) 队列的 Amazon API
Gateway 端点。配置 SQS 队列以调⽤ AWS Lambda 函数，该函数调⽤ Amazon Lex 进⾏情感分析，并将结
果保存到 Amazon DynamoDB 表中。将所有记录的 TTL 设置为未来 365 天。
https://examlearn.online
[2026/05]
Question #1006
Topic 1
⼀家公司使⽤ AWS Systems Manager 对 Amazon EC2 实例进⾏⽇常管理和补丁更新。这些 EC2 实例位于应⽤
程序负载均衡器 (ALB) 后⾯的 IP 地址类型⽬标组中。
新的安全协议要求该公司在补丁更新期间将 EC2 实例从服务中移除。当该公司尝试在下次补丁更新期间遵循该安
全协议时，在补丁更新窗⼝期间会收到错误。
以下哪两项解决⽅案可以解决这些错误？（选择两项。）
A. 将⽬标组的⽬标类型从 IP 地址类型更改为实例类型。
B. 继续使⽤现有的系统管理器⽂档，⽆需更改，因为它已经针对位于 ALB 后⾯的 IP 地址类型⽬标组中的实
例进⾏了优化。
C. 实施 AWSEC2-PatchLoadBalanacerInstance Systems Manager Automation ⽂档来管理修补过程。
D. 使⽤系统管理器维护窗⼝⾃动将实例从服务中移除，以便修补实例。
E. 配置系统管理器状态管理器，使其从服务中移除实例并管理补丁计划。使⽤应⽤负载均衡器 (ALB) 健康检
查来重新路由流量。
Question #1007
哪种解决⽅案能够以最少的运维⼯作量满⾜这些要求？
的服务器端加密 (SSE-S3) 来加密数据。
Topic 1
⼀家医疗公司需要对来⾃多个客户的⼤量临床试验数据进⾏转换。该公司必须从包含客户数据的关系数据库中提
取数据，然后使⽤⼀系列复杂的规则对数据进⾏转换。转换完成后，该公司会将数据加载到 Amazon S3。
所有数据在存储到 Amazon S3 之前，必须在处理过程中进⾏加密，并且必须使⽤客户特定的密钥进⾏加密。
A. 为每个客户创建⼀个 AWS Glue 作业。为每个作业附加⼀个安全配置，该配置使⽤ Amazon S3 托管密钥
B. 为每个客户创建⼀个 Amazon EMR 集群。为每个集群附加⼀个安全配置，该配置使⽤客户端加密和⾃定义
客户端根密钥 (CSE-Custom) 来加密数据。
C. 为每个客户创建⼀个 AWS Glue 作业。为每个作业附加⼀个安全配置，该配置使⽤客户端加密和 AWS
KMS 管理的密钥 (CSE-KMS) 来加密数据。
D. 为每个客户创建⼀个 Amazon EMR 集群。为每个集群附加⼀个安全配置，该配置使⽤ AWS KMS 密钥进
⾏服务器端加密 (SSE-KMS) 来加密数据。
https://examlearn.online
[2026/05]
Question #1008
Topic 1
⼀家公司将⽹站分析应⽤程序托管在单个 Amazon EC2 按需实例上。该分析应⽤程序具有很⾼的弹性，并设计为
以⽆状态模式运⾏。
该公司注意到，在访问⾼峰期，该应⽤程序的性能出现下降，并出现 5xx 错误。该公司需要使该应⽤程序能够⽆
缝扩展。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 创建 Web 应⽤程序的 Amazon 系统映像 (AMI)。使⽤该 AMI 启动第⼆个 EC2 按需实例。使⽤应⽤程序负
载均衡器将负载分配到这两个 EC2 实例上。
B. 创建 Web 应⽤程序的 Amazon 系统映像 (AMI)。使⽤该 AMI 启动第⼆个 EC2 按需实例。使⽤ Amazon
Route 53 加权路由将负载分配到这两个 EC2 实例上。
C. 创建⼀个 AWS Lambda 函数来停⽌ EC2 实例并更改实例类型。创建⼀个 Amazon CloudWatch 警报，以
便在 CPU 利⽤率超过 75% 时调⽤ Lambda 函数。
D. 创建 Web 应⽤程序的 Amazon 系统映像 (AMI)。将该 AMI 应⽤到启动模板。创建⼀个包含该启动模板的
⾃动扩展组。将启动模板配置为使⽤竞价型实例。将应⽤程序负载均衡器附加到该⾃动扩展组。
Question #1009
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司运⾏着⼀个数据存储在 Amazon S3 存储桶中的环境。这些对象全天都会被频繁访问。该公司对存储在
S3 存储桶中的数据有严格的加密要求。⽬前，该公司使⽤ AWS Key Management Service (AWS KMS) 进⾏加
密。
该公司希望在不额外调⽤ AWS KMS 的情况下，优化 S3 对象加密的相关成本。
A. 使⽤ Amazon S3 管理密钥的服务器端加密 (SSE-S3)。
B. 对新对象使⽤ S3 存储桶密钥和 AWS KMS 密钥 (SSE-KMS) 进⾏服务器端加密。
C. 使⽤ AWS KMS 客户管理的密钥进⾏客户端加密。
D. 使⽤存储在 AWS KMS 中的客户提供的密钥（SSE-C）进⾏服务器端加密。
https://examlearn.online
[2026/05]
Question #1010
Topic 1
⼀家公司在本地数据中⼼的虚拟机 (VM) 上运⾏多个⼯作负载。该公司正在快速扩张，但本地数据中⼼的扩展速
度已⽆法满⾜业务需求。该公司希望将这些⼯作负载迁移到 AWS，且
迁移时间紧迫。对于⾮关键⼯作负载，该公司希望采⽤“直接迁移”策略。
以下哪三项步骤组合能够满⾜这些要求？（选择三项。）
A. 使⽤ AWS Schema Conversion Tool (AWS SCT) 收集有关虚拟机的数据。
B. 使⽤ AWS 应⽤程序迁移服务。在虚拟机上安装 AWS 复制代理。
C. 完成虚拟机的初始复制。启动测试实例，对虚拟机执⾏验收测试。
D. 停⽌虚拟机上的所有操作。启动⼀个切换实例。
E. 使⽤ AWS App2Container (A2C) 收集有关虚拟机的数据。
F. 使⽤ AWS 数据库迁移服务 (AWS DMS) 迁移虚拟机。
Question #1011
Topic 1
⼀家公司在私有⼦⽹中托管了⼀个应⽤程序。该公司已将该应⽤程序与 Amazon Cognito 集成。该公司使⽤
Amazon Cognito ⽤户池进⾏⽤户身份验证。
该公司需要修改该应⽤程序，使其能够安全地将⽤户⽂档存储在 Amazon S3 存储桶中。
以下哪两项步骤组合可以安全地将 Amazon S3 与该应⽤程序集成？
A. 创建⼀个 Amazon Cognito 身份池，以便在⽤户成功登录时为其⽣成安全的 Amazon S3 访问令牌。
B. 使⽤现有的 Amazon Cognito ⽤户池，在⽤户成功登录时为其⽣成 Amazon S3 访问令牌。
C. 在公司托管应⽤程序的同⼀ VPC 中创建 Amazon S3 VPC 终端节点。
D. 在公司托管应⽤程序的 VPC 中创建⼀个 NAT ⽹关。为 S3 存储桶分配策略，拒绝任何并⾮由 Amazon
Cognito 发起的请求。
E. 将策略附加到 S3 存储桶，仅允许从⽤户的 IP 地址访问。
https://examlearn.online
[2026/05]
Question #1012
Topic 1
⼀家公司拥有⼀个三层架构的Web应⽤程序，⽤于处理客户订单。Web层由位于应⽤程序负载均衡器 (ALB) 后⾯
的Amazon EC2实例组成。处理层也由EC2实例组成。该公司使⽤Amazon Simple Queue Service (Amazon
SQS) 将Web层和处理层解耦。存储层使⽤Amazon DynamoDB。
在⾼峰时段，部分⽤户反映订单处理出现延迟和卡顿。该公司注意到，在这些延迟期间，EC2实例的CPU使⽤率
达到100%，并且SQS队列被填满。⾼峰时段不固定且难以预测。
该公司需要提升应⽤程序的性能。
哪种解决⽅案能够满⾜这些要求？
A. 使⽤ Amazon EC2 Auto Scaling 的计划扩展功能，在⾼峰使⽤时段扩展处理层实例。使⽤ CPU 利⽤率指
标来确定何时进⾏扩展。
B. 在 DynamoDB 后端层前端使⽤ Amazon ElastiCache for Redis。使⽤⽬标利⽤率作为指标来确定何时进
⾏扩展。
C. 添加 Amazon CloudFront 分发以缓存 Web 层的响应。使⽤ HTTP 延迟作为指标来确定何时进⾏扩展。
D. 使⽤ Amazon EC2 Auto Scaling ⽬标跟踪策略来扩展处理层实例。使⽤
ApproximateNumberOfMessages 属性来确定何时进⾏扩展。
Question #1013
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
Topic 1
⼀家公司的⽣产环境由 Amazon EC2 按需实例组成，这些实例周⼀⾄周六持续运⾏。周⽇这些实例只需运⾏ 12
⼩时，且不能容忍任何中断。该公司希望优化⽣产环境的成本。
A. 购买计划预留实例，⽤于周⽇仅运⾏ 12 ⼩时的 EC2 实例。购买标准预留实例，⽤于周⼀⾄周六持续运⾏
的 EC2 实例。
B. 对于周⽇仅运⾏ 12 ⼩时的 EC2 实例，请购买可转换预留实例。对于周⼀⾄周六持续运⾏的 EC2 实例，请
购买标准预留实例。
C. 对于周⽇仅运⾏ 12 ⼩时的 EC2 实例，请使⽤竞价型实例。对于周⼀⾄周六持续运⾏的 EC2 实例，请购买
标准预留实例。
D. 对于周⽇仅运⾏ 12 ⼩时的 EC2 实例，请使⽤竞价型实例。对于周⼀⾄周六持续运⾏的 EC2 实例，请购买
可转换预留实例。
https://examlearn.online
[2026/05]
Question #1014
Topic 1
⼀家数字图像处理公司希望将其本地部署的单体应⽤程序迁移到 AWS 云平台。该公司需要处理数千张图像，并
在处理过程中⽣成⼤量⽂件。
该公司需要⼀个解决⽅案来管理⽇益增⻓的图像处理作业数量，并且该解决⽅案还必须减少图像处理⼯作流程中
的⼿动操作。此外，该公司不希望管理解决⽅案的底层基础设施。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 使⽤ Amazon Elastic Container Service (Amazon ECS) 和 Amazon EC2 Spot 实例处理镜像。配置
Amazon Simple Queue Service (Amazon SQS) 来编排⼯作流。将处理后的⽂件存储在 Amazon Elastic File
System (Amazon EFS) 中。
B. 使⽤ AWS Batch 作业处理图像。使⽤ AWS Step Functions 编排⼯作流。将处理后的⽂件存储在
Amazon S3 存储桶中。
C. 使⽤ AWS Lambda 函数和 Amazon EC2 Spot 实例处理图像。将处理后的⽂件存储在 Amazon FSx 中。
D. 部署⼀组 Amazon EC2 实例来处理图像。使⽤ AWS Step Functions 来编排⼯作流。将处理后的⽂件存储
在 Amazon Elastic Block Store (Amazon EBS) 卷中。
Question #1015
该公司必须提升⽹站性能。
哪种解决⽅案能够以最⼩的实施成本满⾜这些要求？
Topic 1
⼀家公司的图⽚托管⽹站允许全球⽤户通过移动设备上传、查看和下载图⽚。该公司⽬前将静态⽹站托管在亚⻢
逊S3存储桶中。
由于⽹站访问量不断增⻓，其性能有所下降。⽤户反映在上传和下载图⽚时存在延迟问题。
A. 为 S3 存储桶配置 Amazon CloudFront 分发以提⾼下载性能。启⽤ S3 传输加速以提⾼上传性能。
B. 在多个 AWS 区域中配置合适⼤⼩的 Amazon EC2 实例。将应⽤程序迁移到这些 EC2 实例。使⽤应⽤程序
负载均衡器将⽹站流量平均分配到各个 EC2 实例。配置 AWS Global Accelerator 以低延迟满⾜全球需求。
C. 配置⼀个使⽤ S3 存储桶作为源的 Amazon CloudFront 分发，以提⾼下载性能。配置应⽤程序使⽤
CloudFront 上传图像，以提⾼上传性能。在多个 AWS 区域中创建 S3 存储桶。配置存储桶的复制规则，根据
⽤户位置复制⽤户数据。将下载重定向到距离每个⽤户位置最近的 S3 存储桶。
D. 为 S3 存储桶配置 AWS Global Accelerator 以提⾼⽹络性能。创建⼀个终端节点，使应⽤程序能够使⽤
Global Accelerator ⽽不是 S3 存储桶。
https://examlearn.online
[2026/05]
Question #1016
Topic 1
⼀家公司在虚拟私有云 (VPC) 内的应⽤程序负载均衡器 (ALB) 后⾯的私有⼦⽹中运⾏⼀个应⽤程序。该 VPC 具
有 NAT ⽹关和互联⽹⽹关。该应⽤程序调⽤ Amazon S3 API 来存储对象。
根据该公司的安全策略，来⾃该应⽤程序的流量不得通过互联⽹传输。
哪种解决⽅案能够以最具成本效益的⽅式满⾜这些要求？
A. 配置 S3 接⼝端点。创建⼀个安全组，允许出站流量访问 Amazon S3。
B. 配置 S3 ⽹关端点。更新 VPC 路由表以使⽤该端点。
C. 配置 S3 存储桶策略，允许来⾃分配给 NAT ⽹关的弹性 IP 地址的流量。
D. 在部署旧版应⽤程序的同⼀⼦⽹中创建第⼆个 NAT ⽹关。更新 VPC 路由表以使⽤第⼆个 NAT ⽹关。
Question #1017
哪种解决⽅案能够满⾜这些要求？
DynamoDB 的访问。
Topic 1
⼀家公司有⼀个应⽤程序，运⾏在 Amazon EC2 实例上的 Amazon Elastic Kubernetes Service (Amazon EKS)
集群中。该应⽤程序的 UI 使⽤ Amazon DynamoDB，数据服务则使⽤ Amazon S3。
该公司必须确保 UI 的 EKS Pod 只能访问 Amazon DynamoDB，⽽数据服务的 EKS Pod 只能访问 Amazon
S3。该公司使⽤ AWS Identity and Access Management (IAM)。
A. 为 Amazon S3 和 DynamoDB 访问创建单独的 IAM 策略，并赋予其所需的权限。将这两个 IAM 策略附加
到 EC2 实例配置⽂件。使⽤基于⻆⾊的访问控制 (RBAC) 来控制相应 EKS Pod 对 Amazon S3 或
B. 为 Amazon S3 和 DynamoDB 访问创建单独的 IAM 策略，并赋予其所需的权限。将 Amazon S3 IAM 策
略直接附加到⽤于数据服务的 EKS Pod，并将 DynamoDB 策略附加到⽤于 UI 的 EKS Pod。
C. 为⽤户界⾯服务和数据服务创建单独的 Kubernetes 服务账户，并赋予它们 IAM ⻆⾊。将
AmazonS3FullAccess 策略附加到数据服务账户，将 AmazonDynamoDBFullAccess 策略附加到⽤户界⾯服
务账户。
D. 为⽤户界⾯服务和数据服务创建独⽴的 Kubernetes 服务账号，并赋予它们 IAM ⻆⾊。使⽤ IAM 服务账号
⻆⾊ (IRSA) 为⽤户界⾯服务的 EKS Pod 提供对 Amazon S3 的访问权限，并为数据服务的 EKS Pod 提供对
DynamoDB 的访问权限。
https://examlearn.online
[2026/05]
Question #1018
Topic 1
⼀家公司需要为遍布全球的开发团队提供安全访问公司 AWS 资源的途径，并确保该访问⽅式符合安全策略。
该公司⽬前使⽤本地 Active Directory 进⾏内部身份验证。该公司使⽤ AWS Organizations 管理⽀持多个项⽬的
多个 AWS 账户。
该公司需要⼀个能够与现有基础设施集成的解决⽅案，以提供集中式的身份管理和访问控制。
哪种解决⽅案能够以最低的运维开销满⾜这些要求？
A. 设置 AWS Directory Service，在 AWS 上创建 AWS 托管的 Microsoft Active Directory。与本地 Active
Directory 建⽴信任关系。使⽤分配给 Active Directory 组的 IAM 权限访问公司 AWS 账户中的 AWS 资源。
B. 为每位开发⼈员创建⼀个身份和访问管理 (IAM) ⽤户。根据每位⽤户在各个项⽬中的参与程度，⼿动管理
其权限。强制启⽤多因素身份验证 (MFA) 作为额外的安全层。
C. 使⽤ AWS Directory Service 中的 AD Connector 连接到本地 Active Directory。将 AD Connector 与
AWS IAM Identity Center 集成。配置权限集，为每个 AD 组授予对特定 AWS 账户和资源的访问权限。
D. 使⽤ Amazon Cognito 部署身份联合解决⽅案。将身份联合解决⽅案与本地 Active Directory 集成。使⽤
Amazon Cognito 为开发⼈员提供访问令牌，以便他们访问 AWS 账户和资源。
Question #1019
哪种解决⽅案能够满⾜这些要求？
Topic 1
⼀家公司正在 AWS 云上开发⼀个应⽤程序。该应⽤程序的 HTTP API 包含发布在 Amazon API Gateway 中的关
键信息。这些关键信息必须只能从公司内部⽹络中⼀组有限的受信任 IP 地址访问。
A. 设置 API ⽹关私有集成，将访问权限限制在预定义的⼀组 IP 地址内。
B. 为 API 创建⼀个资源策略，拒绝任何未经明确允许的 IP 地址的访问。
C. 直接在私有⼦⽹中部署 API。创建⽹络访问控制列表 (ACL)。设置规则以允许来⾃特定 IP 地址的流量。
D. 修改附加到 API ⽹关的安全组，仅允许来⾃受信任 IP 地址的⼊站流量。
https://examlearn.online
