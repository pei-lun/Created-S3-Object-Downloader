import json
from os import makedirs
from os.path import dirname, isdir, join

import boto3
import click


def receive_sqs_msgs(sqs_queue_url: str):
    sqs = boto3.resource('sqs')
    sqs_queue = sqs.Queue(sqs_queue_url)

    msgs = sqs_queue.receive_messages(VisibilityTimeout=180)
    while msgs:
        for msg in msgs:
            yield msg
        msgs = sqs_queue.receive_messages()


@click.command()
@click.option('--reserved-prefixes', default=0, type=int)
@click.argument('sqs_queue_url')
@click.argument(
    'destination',
    type=click.Path(
        exists=True, file_okay=False, writable=True, resolve_path=True
    ),
)
def download(sqs_queue_url, destination, reserved_prefixes):
    s3_client = boto3.client('s3')

    for msg in receive_sqs_msgs(sqs_queue_url):
        try:
            event: dict = json.loads(msg.body)['Records'][0]
        except KeyError:
            continue

        event_src: str = event['eventSource']
        event_name: str = event['eventName']

        if event_src == 'aws:s3' and event_name.startswith('ObjectCreated'):
            bucket_name: str = event['s3']['bucket']['name']
            object_key: str = event['s3']['object']['key']

            filename = join(
                destination, *object_key.split('/')[-1 - reserved_prefixes :]
            )

            directory = dirname(filename)
            if not isdir(directory):
                makedirs(directory)

            s3_client.download_file(bucket_name, object_key, filename)

            msg.delete()


if __name__ == '__main__':
    download()
