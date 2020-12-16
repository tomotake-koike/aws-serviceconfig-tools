# aws-serviceconfig-tools

## scripts/aws-serviceconfig-roundup.py

CloudConfigから取得可能な各リソースの設定情報をリソース間の関連性（ディフォルト3レベル）から辿って収集します。  
標準出力に関連性の状況を出力し、JSONで取得した設定情報を出力します。  

### 引数

    $ python3 aws-serviceconfig-roundup.py resourceType [resourceId]
	
`resourceType`はリソース種別を[こちら](https://docs.aws.amazon.com/config/latest/APIReference/API_GetResourceConfigHistory.html#config-GetResourceConfigHistory-request-resourceType)から選択して指定します。  
`resourceId`を省略すると指定したリソース種別の全てのリソースを収集します。

### 環境変数

- `RELATION_NEST_MAX` (default: 3)
再帰的に関連性を探索する深度を設定します。
- `OUT_ALL_RELATION` (default: False)
通常は重複して検出したリソースは標準出力に出力しませんが、この環境変数に何らかの値を設定すると、重複したものを`*`を付与して出力します。
