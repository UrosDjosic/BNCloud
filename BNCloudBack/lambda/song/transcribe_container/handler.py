import os
import json
import tempfile
from urllib.parse import unquote_plus

import boto3
# Force all caches to /tmp to avoid read-only FS
os.environ.setdefault('HF_HOME', '/tmp/.cache')
os.environ.setdefault('HUGGINGFACE_HUB_CACHE', '/tmp/.cache')
os.environ.setdefault('TRANSFORMERS_CACHE', '/tmp/.cache')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/.cache')
os.environ.setdefault('HOME', '/tmp')
os.environ.setdefault('WHISPER_DOWNLOAD_ROOT', '/tmp/faster-whisper')
from faster_whisper import WhisperModel

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

MODEL_NAME = os.environ.get('WHISPER_MODEL', 'base')
COMPUTE_TYPE = os.environ.get('WHISPER_COMPUTE', 'int8_float16')  
# Optional decoding/config hints
WHISPER_LANGUAGE = os.environ.get('WHISPER_LANGUAGE','')  # e.g., 'sr' for Serbian
WHISPER_TASK = os.environ.get('WHISPER_TASK', 'transcribe')  # 'transcribe' or 'translate'
WHISPER_VAD = os.environ.get('WHISPER_VAD', 'false').lower() == 'true'
WHISPER_BEAM_SIZE = int(os.environ.get('WHISPER_BEAM_SIZE', '1'))
WHISPER_BEST_OF = int(os.environ.get('WHISPER_BEST_OF', '5'))
WHISPER_TEMPERATURE = float(os.environ.get('WHISPER_TEMPERATURE', '0.4'))
MODEL_DOWNLOAD_ROOT = os.environ.get('WHISPER_DOWNLOAD_ROOT', '/tmp/faster-whisper')
_model = None  # lazy-loaded

#GETTING AND SETTING UP MODEL
def _get_model():
    global _model
    if _model is None:
        try:
            os.makedirs(MODEL_DOWNLOAD_ROOT, exist_ok=True)
        except Exception:
            pass
        print(f"Loading Whisper model '{MODEL_NAME}' (compute={COMPUTE_TYPE}) to {MODEL_DOWNLOAD_ROOT}...", flush=True)
        _model = WhisperModel(
            MODEL_NAME,
            device="cpu",
            compute_type=COMPUTE_TYPE,
            download_root=MODEL_DOWNLOAD_ROOT,
        )
    return _model


def _transcribe(local_path: str):
    # Transcribe to plain text (no word timestamps)
    model = _get_model()
    print(
        f"Starting transcription (words=False, lang={WHISPER_LANGUAGE or 'auto'}, "
        f"beam={WHISPER_BEAM_SIZE}, best_of={WHISPER_BEST_OF}, vad={WHISPER_VAD}) for {local_path}...",
        flush=True,
    )
    
    kwargs = dict(
        task=WHISPER_TASK,
        vad_filter=WHISPER_VAD,
        beam_size=WHISPER_BEAM_SIZE,
        best_of=WHISPER_BEST_OF,
    )
    if WHISPER_LANGUAGE:
        kwargs["language"] = WHISPER_LANGUAGE
    else:
        kwargs['temperature'] = WHISPER_TEMPERATURE
    if WHISPER_LANGUAGE:
        kwargs["language"] = WHISPER_LANGUAGE
    
    kwargs["no_speech_threshold"] = 0.3
    kwargs["compression_ratio_threshold"] = 2.8
    kwargs["log_prob_threshold"] = -2.0
    kwargs["condition_on_previous_text"] = False
    kwargs['patience'] = 1.0

    segments, info = model.transcribe(local_path, **kwargs)
    parts = []
    for seg in segments:
        parts.append((seg.text or "").strip())
    text = " ".join(parts)
    text = _collapse_repeats(text)
    return text


def _collapse_repeats(text: str, max_word_repeat: int = 3) -> str:
    # Collapse consecutive identical words beyond a threshold to reduce looping artifacts
    tokens = text.split()
    if not tokens:
        return text
    out = []
    prev = None
    run = 0
    for tok in tokens:
        if tok == prev:
            run += 1
        else:
            run = 1
            prev = tok
        if run <= max_word_repeat:
            out.append(tok)
    return " ".join(out)


def _iter_s3_records(event):
    # S3 EVENTS ASWELL AS S3 WRAPPED EVENTS
    for rec in event.get('Records', []) or []:
        if rec.get('eventSource') == 'aws:sqs' and 'body' in rec:
            try:
                s3_event = json.loads(rec['body'])
                for s3rec in s3_event.get('Records', []) or []:
                    yield s3rec
            except Exception as e:
                print('Failed to parse SQS body as S3 event:', e)
        else:
            # Assume this is already an S3 record
            if rec.get('s3'):
                yield rec


def transcribe(event, context):
    table = dynamodb.Table(os.environ.get('TABLE_NAME', 'Songs'))
    bucket = os.environ.get('S3_BUCKET_NAME')

    processed = 0
    for rec in _iter_s3_records(event):
        obj = rec.get('s3', {}).get('object', {})
        raw_key = obj.get('key')
        if not raw_key:
            continue
        key = unquote_plus(raw_key)
        parts = key.split('/')
        # Expect key like <song_id>/audio/<filename>
        if len(parts) < 3 or parts[1] != 'audio':
            continue

        song_id = parts[0]
        fd, local_path = tempfile.mkstemp(prefix='audio_', suffix='_' + parts[-1].replace('/', '_'))
        os.close(fd)
        try:
            print(f"Processing S3://{bucket}/{key} for song_id={song_id}", flush=True)
            # Mark processing
            try:
                table.update_item(
                    Key={'id': song_id},
                    UpdateExpression='SET transcriptionStatus = :s',
                    ExpressionAttributeValues={':s': 'processing'}
                )
            except Exception as e:
                print('Failed to mark processing for', song_id, e)

            print("Downloading audio to", local_path, flush=True)
            s3.download_file(bucket, key, local_path)
            text = _transcribe(local_path)
            print(f"Transcription complete. chars={len(text)}", flush=True)

            table.update_item(
                Key={'id': song_id},
                UpdateExpression='SET transcript = :t, transcriptionStatus = :s',
                ExpressionAttributeValues={':t': text, ':s': 'completed'},
            )
            print("DynamoDB updated for", song_id, flush=True)
            processed += 1
        except Exception as e:
            print('Transcription error for', song_id, e)
            try:
                table.update_item(
                    Key={'id': song_id},
                    UpdateExpression='SET transcriptionStatus = :s, transcriptionError = :e',
                    ExpressionAttributeValues={':s': 'failed', ':e': str(e)}
                )
            except Exception:
                pass
        finally:
            try:
                os.remove(local_path)
            except OSError:
                pass

    return {
        'statusCode': 200,
        'body': json.dumps({'processed': processed})
    }
