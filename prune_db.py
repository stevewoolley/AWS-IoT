import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
client = boto3.client('dynamodb')
table_name = 'sensors'
table = dynamodb.Table(table_name)
key = 'pi12xx'

response = client.describe_table(TableName=table_name)
keys = [k['AttributeName'] for k in response['Table']['KeySchema']]
response = table.scan()
items = response['Items']
number_of_items = len(items)

if number_of_items == 0:  # no items to delete
    print("Table '{}' is empty.".format(table_name))

print("You are about to delete all ({}) items from table '{}'."
      .format(number_of_items, table_name))
exit(0)

print("Attempting a conditional delete source = '%s'..." % key)

try:
    response = table.delete_item(
        Key={
            'source': key
        }
    )
except ClientError as e:
    if e.response['Error']['Code'] == "ConditionalCheckFailedException":
        print(e.response['Error']['Message'])
    else:
        raise
else:
    print("DeleteItem succeeded:")
