import subprocess
import shlex
import datetime
import os

# import whisper
import whisper
import whisper_at

from transformers import pipeline
import torch
import torchaudio

import scraper_MySQL
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def main():
    download_file = 'temp_audio_for_ai_summary.mp3'
    voice_only_file = "temp_voice_only_file.wav"
    speech_only_file = "temp_speech_only_file.wav"
    speech_only_file_trimmed = "temp_speech_only_file_trimmed.wav"
    # Get episodes without a description
    mySQL = scraper_MySQL.MySQL() 
    eps = mySQL.get_query("""
        SELECT `episodes`.`id`, show_id, mp3, showName, source, `host`
        FROM episodes  
        LEFT JOIN shows ON `shows`.`id` = `episodes`.`show_id`               
        WHERE ai_desc is null
        AND show_id = 110
        ORDER BY `episodes`.`id` DESC
        LIMIT 5
    """)

    for ep in eps:

        print("\n*****", ep['id'])
        
        save_portion_of_audio_file(ep['mp3'], download_file, end_time="00:59:00")

        reduce_audio_to_voice_only_using_silero(download_file, voice_only_file)
        reduce_audio_to_speech_only_using_whisper(voice_only_file, speech_only_file)

        save_portion_of_audio_file(speech_only_file, speech_only_file_trimmed, end_time="00:10:00")

        transcription = transcribe_audio(speech_only_file_trimmed, ep)

        # summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #limited length ~1024 tokens
        # summarizer = pipeline("summarization", model="google/bigbird-pegasus-large-bigpatent") # Max length 4096 https://huggingface.co/google/bigbird-pegasus-large-bigpatent
        summarizer = pipeline("summarization", model="pszemraj/pegasus-x-large-book-summary") # Max length ??? https://huggingface.co/pszemraj/pegasus-x-large-book-summary

        title_summarizer = pipeline("summarization", model="ybagoury/flan-t5-base-tldr_news")
        # title_summarizer = pipeline("summarization", model="JulesBelveze/t5-small-headline-generator")

        summary = create_summary(transcription, summarizer)

        title = create_title(summary[0]['summary_text'], title_summarizer)

        # add to db
        print('saving to db')
        print(datetime.datetime.utcnow())
        print(summary[0]['summary_text'])
        mySQL.insert_ep_ai_details(ep['id'], summary[0]['summary_text'], title[0]['summary_text'])

def save_portion_of_audio_file(orig_audio_file, new_file, start_time="00:00:00", end_time = "00:30:00"):
    """saves audio. Defaults to downloading 30 minutes.
        orig_audio_file: url address of file to download or local file location.
        new_file: specifies path and name to output local saved file.
        start_time: specifies time code of file to start downloading.
        end_time: specifies time code at which to stop downloading.

    """
    print('**** saving audio')
    print(datetime.datetime.utcnow())
    command = shlex.split(f'ffmpeg -y -i "{orig_audio_file}" -ss {start_time} -t {end_time} -c:v copy -c:a copy "{new_file}"')
    subprocess.call(command)

def reduce_audio_to_speech_only_using_whisper(download_file, speech_only_file):
    # Reduce to voice parts only
    # Uses whisper_at which is a fork of whisper that includes audio tagging
    # Audio tagging identifies speech and music and other sounds types
    # list of other sound types shown by calling: whisper.print_label_name(language='en')
    
    print("**** Finding voice only timestamps")
    print(datetime.datetime.utcnow())
    model = whisper_at.load_model("tiny.en")
    audio_tagging_time_resolution = 6
    result = model.transcribe(download_file, at_time_res=audio_tagging_time_resolution, no_speech_threshold=.75, fp16=False)

    # 0 = speech, 137 = music
    audio_tag_result = whisper_at.parse_at_label(result, language='follow_asr', top_k=5, p_threshold=0, include_class_list=[0, 137])

    # create list of speech only time stamps
    speech_timestamp_samples = get_only_speech_timestamps(audio_tag_result)

    # merge all speech chunks to one audio
    print("Merging speech chunks into new file")
    print(datetime.datetime.utcnow())
    wav = read_audio(download_file, sampling_rate=16000)

    save_audio(speech_only_file, collect_chunks(speech_timestamp_samples, wav), sampling_rate=16000)
    

def reduce_audio_to_voice_only_using_silero(download_file, voice_only_file):
    # # Reduce to voice parts only
    print("**** Finding voice only timestamps")
    print(datetime.datetime.utcnow())
    torch.set_num_threads(1)
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                            model='silero_vad',
                            force_reload=False,
                            trust_repo=True,
                            onnx=False)

    (get_speech_timestamps,
    save_audio,
    read_audio,
    VADIterator,
    collect_chunks) = utils
    SAMPLING_RATE = 16000

    mp3 = read_audio(download_file, sampling_rate=SAMPLING_RATE)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(mp3, model, sampling_rate=SAMPLING_RATE)
    print(speech_timestamps)
    # merge all speech chunks to one audio
    print("Merging speech chunks into new file")
    print(datetime.datetime.utcnow())
    save_audio(voice_only_file, collect_chunks(speech_timestamps, mp3), sampling_rate=SAMPLING_RATE) 

def transcribe_audio(audio_file, ep):
    # transcribe the audio
    print('**** transcribing audio')
    print(datetime.datetime.utcnow())
    model = whisper.load_model("small.en")
    result = model.transcribe(audio_file, no_speech_threshold=.6, fp16=False, initial_prompt= f"From the roots up CIUT 89.5 FM CFRU archives {ep['showName']} {ep['host']}")

    print("detected language:", result['language'])

    txt = result["text"]

    # Often commercials at begining. This will muddle up description.
    # Use keyword indicators to guess where the show actually starts
    key_phrase_search_limit = 2500

    if ep['showName'] in txt[:key_phrase_search_limit]:
        print("found show name key phrase", ep['showName'])
        keyPhraseIdx = txt.find(ep['showName'])          
    elif len(ep['host']) and ep['host'].split()[0] in txt[:key_phrase_search_limit]:
        print("found host key phrase", ep['host'].split()[0])
        keyPhraseIdx = txt.find(ep['host'].split()[0])
    elif "From the roots up" in txt[:key_phrase_search_limit]:
        print("found roots up key phrase")
        keyPhraseIdx = txt.find("From the roots up")
    elif "CFRU archives" in txt[:key_phrase_search_limit]:
        print("found CFRU archives key phrase")
        keyPhraseIdx = txt.find("CFRU archives")
    # elif 'welcome' in txt[:key_phrase_search_limit]:
    #     print("found welcome key phrase")
    #     keyPhraseIdx = txt.find('welcome')
    # elif 'hello' in txt[:key_phrase_search_limit]: 
        # print("found hi key phrase")
        # keyPhraseIdx = txt.find('hi')
    else:
        keyPhraseIdx = -1
    

    if keyPhraseIdx > -1:
        print("key phrase found at index", keyPhraseIdx)
        cleaned_txt = txt[keyPhraseIdx:]
    else:
        # If no key phrase found, just use recklessly chop 800 characters
        if len(txt) > 1000:
            cleaned_txt = txt[800:]
        else:
            cleaned_txt = txt

    print(cleaned_txt)
    # audio_tag_result = whisper.parse_at_label(result, language='follow_asr', top_k=5, p_threshold=-1, include_class_list=list(range(527)))

    return cleaned_txt

def create_summary(txt, summarizer,  max_characters=3250):
    """Sumarize Text, using a given summarizer. Max characters can be set to accomodate the summarizer models token length.
        txt: the text to summarize,
        summarizer: the huggingface summarization pipeline,
        max_characters: defaults to 3250 which seems sufficient to reduce the txt to the token limits of facebook/bart-large-cnn's 1024 token limit.
    """
    print("**** summarizing transcription")
    print(datetime.datetime.utcnow())    
    # Limit text used for summary to 3000 characters as the model has limit on token numbers
    print("transcript length:", len(txt))
    txt_for_summary = txt[:max_characters]
    summary = summarizer(txt_for_summary, max_length=250, min_length=50, do_sample=True)
    return summary

def create_title(txt, summarizer):
    # create title by summarizing summary
    print("**** Creating title")
    print(datetime.datetime.utcnow())
    title = summarizer(txt, max_length=30, min_length=15, do_sample=True)
    return title


def get_only_speech_timestamps(audio_tag_results: list[dict]):
    """Returns list of only speech timestamps from audio_tag_result"""
    speech_timestamp_samples:list[dict] = []
    sample_rate = 16000

    for label in audio_tag_results:

        tags_dict = dict(label['audio tags'])
        if 'Speech' in tags_dict:
            speech_timestamp_samples.append({'start': label['time']['start']*sample_rate, 'end':label['time']['end']*sample_rate})
    return speech_timestamp_samples

###### From silero_vad
def read_audio(path: str,
               sampling_rate: int = 16000):

    wav, sr = torchaudio.load(path)

    if wav.size(0) > 1:
        wav = wav.mean(dim=0, keepdim=True)

    if sr != sampling_rate:
        transform = torchaudio.transforms.Resample(orig_freq=sr,
                                                   new_freq=sampling_rate)
        wav = transform(wav)
        sr = sampling_rate

    assert sr == sampling_rate
    return wav.squeeze(0)

def collect_chunks(tss: list[dict], wav: torch.Tensor):
    chunks = []
    for i in tss:
        chunks.append(wav[i['start']: i['end']])
    return torch.cat(chunks)

def save_audio(path: str,
               tensor: torch.Tensor,
               sampling_rate: int = 16000):
    torchaudio.save(path, tensor.unsqueeze(0), sampling_rate, bits_per_sample=16)



###### end from silero_vad

if __name__ == '__main__':
    main()



