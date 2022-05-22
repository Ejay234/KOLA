
from configure import AUTH_KEY
import requests
import pprint
import json
import time

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers_auth_only = {
    'authorization': AUTH_KEY
}

headers = {
    'authorization': AUTH_KEY,
    'content-type': 'application/json'
}

CHUNK_SIZE = 5_242_880


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                                    headers=headers_auth_only,
                                    data=read_file(filename))
    pprint.pprint(upload_response.json())
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': True,
        'auto_highlights': True
    }

    transcript_response = requests.post(transcript_endpoint,
                                        json=transcript_request,
                                        headers=headers)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)

    if polling_response.json()['status'] == 'completed':
        filename = transcript_id + '.txt'
        with open(filename, 'w') as f:
            f.write(polling_response.json()['text'])

        filename = transcript_id + '_chapters.json'
        with open(filename, 'w') as f:
            chapters = polling_response.json()['chapters']
            json.dump(chapters, f, indent=4)

        filename = transcript_id + '_highlights.json'
        with open(filename, 'w') as f:
            data = polling_response.json()['auto_highlights_result']
            json.dump(data, f, indent=4)

        print('Transcript saved')
        return True
    return False


def main(filename):
    audio_url = upload(filename)
    transcribe_id = transcribe(audio_url)
    while True:
        result = poll(transcribe_id)
        if result:
            break
        print("waiting for 60 seconds")
        time.sleep(60)


if __name__ == '__main__':
    main("<MP3 File")
