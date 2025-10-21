import json
import boto3

dynamodb = boto3.resource('dynamodb')
userlist_table = dynamodb.Table('Userlists')

def update(event, context):
    data = json.loads(event['body'])
    path_params = event.get('pathParameters') or {}

    userlist_id = path_params.get('userlistId')
    song_id = data.get('song')

    if not userlist_id or not song_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'all parameters required'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    
    userlist = userlist_table.get_item(Key={'id': userlist_id}).get('Item')
    if not userlist:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Song not found'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    
    songs = userlist.get('songs', [])
    delete = False
    for song in songs:
        if song == song_id:
            delete = True
            break
    if delete:
        songs.remove(song_id)
    else:
        songs.append(song_id)
    
    userlist_table.update_item(
        Key={'id': userlist_id},
        UpdateExpression='SET songs = :s',
        ExpressionAttributeValues={
            ':s': songs,
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'List updated successfully'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }