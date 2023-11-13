import subprocess
import shlex
import datetime
import time
import os
import re
import requests
import string

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
    speech_only_file = "temp_speech_only_file.wav"
    speech_only_file_trimmed = "temp_speech_only_file_trimmed.wav"
    # Get episodes without a description
    mySQL = scraper_MySQL.MySQL() 
    eps = mySQL.get_query("""
        SELECT `episodes`.`id`, show_id, mp3, showName, source, `host`, lang, source
        FROM episodes  
        LEFT JOIN shows ON `shows`.`id` = `episodes`.`show_id`               
        WHERE ai_desc is null
        AND (lang is null OR lang = 'en')
        ORDER BY `episodes`.`id` DESC
        LIMIT 30
    """)
    removed_eps = []
    for ep in eps:
        voice_only_file = "temp_voice_only_file.wav" # reset voice only file, as it may have been trimmed in previous loop

        print("\n*****", ep['id'])

        #validate mp3 - solution may not be robust for all servers(https://stackoverflow.com/q/70446485/1586014)
        r = requests.head(ep['mp3'], stream=True)
        if r.status_code < 400:

            save_portion_of_audio_file(ep['mp3'], download_file, length="00:59:00")

            if ep['lang'] == None:
                # detect language by first saving an exceprt than running whisper transcribe
                lang = detect_lang(download_file)
            else:
                lang = ep['lang']

            # Only supporting english for now
            if lang == 'en':

                voice_only_file = reduce_audio_to_voice_only_using_silero(download_file, voice_only_file)

                speech_found = reduce_audio_to_speech_only_using_whisper(voice_only_file, speech_only_file)

                if speech_found:

                    save_portion_of_audio_file(speech_only_file, speech_only_file_trimmed, length="00:10:00")

                    transcription = transcribe_audio(speech_only_file_trimmed, ep)

                    if transcription:
                        # summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #limited length ~1024 tokens. Short and sweet, but often misses the point. https://huggingface.co/facebook/bart-large-cnn


                        # summarizer = pipeline("summarization", model="google/bigbird-pegasus-large-bigpatent") # Pretty terrible at summarizing music shows. Lots of repition. - Max length 4096 https://huggingface.co/google/bigbird-pegasus-large-bigpatent


                        summarizer = pipeline("summarization", model="pszemraj/pegasus-x-large-book-summary") # Pretty good. Often does track listings. Can ramble on occasionaly. Max length ??? complains of indexing errors if > 1024 https://huggingface.co/pszemraj/pegasus-x-large-book-summary

                        # title_summarizer = pipeline("summarization", model="ybagoury/flan-t5-base-tldr_news")
                        # title_summarizer = pipeline("summarization", model="JulesBelveze/t5-small-headline-generator")

                        summary_txt = create_summary(transcription, summarizer)

                        # title = create_title(summary[0]['summary_text'], title_summarizer)
                    else:
                        # no speech found in audio
                        summary_txt = ''
                else:
                    summary_txt = ''

                # add to db
                print('saving to db')
                print(datetime.datetime.utcnow())
                print(summary_txt)
                mySQL.insert_ep_ai_details(ep['id'], summary_txt)

                time.sleep(120)
            
            mySQL.set_show_lang(ep['show_id'], lang)
        else:
            print("mp3 not found")
            removed_eps.append(ep['show_id'])
            mySQL.remove_old_eps_by_show(ep['show_id'], f"id = {ep['id']}")
    
    print("removed eps:", removed_eps)


def save_portion_of_audio_file(orig_audio_file, new_file, start_time="00:00:00", length="00:30:00"):
    """saves audio. Defaults to downloading 30 minutes.
        orig_audio_file: url address of file to download or local file location.
        new_file: specifies path and name to output local saved file.
        start_time: specifies time code of file to start downloading.
        end_time: specifies time code at which to stop downloading.

    """
    print('**** saving audio')
    print(datetime.datetime.utcnow())

    command = shlex.split(f'ffmpeg -y -i "{orig_audio_file}" -ss {start_time} -t {length} -c:v copy -c:a copy "{new_file}"')
    subprocess.call(command)

def detect_lang(download_file):
    """detects language by first saving an exceprt than running whisper transcribe. returns: language code"""
    # save excerpt
    lang_detect_excerpt_file = "temp_lang_detect_excerpt_file.wav"
    save_portion_of_audio_file(download_file, lang_detect_excerpt_file, start_time="00:10:00", length="00:10:00")

    print("**** Detecting language")
    print(datetime.datetime.utcnow())
    model = whisper.load_model("tiny")
    result = model.transcribe(lang_detect_excerpt_file, no_speech_threshold=.75, fp16=False)
    lang = result['language']
    print("language:", lang)
    return lang

def reduce_audio_to_speech_only_using_whisper(orig_file, speech_only_file):
    """Reduce to voice parts only
    Uses whisper_at which is a fork of whisper that includes audio tagging
    Audio tagging set to identify speech and music.
    Returns True if speech only file was created, False if not.
    """

    
    print("**** Finding speech only timestamps")
    print(datetime.datetime.utcnow())
    model = whisper_at.load_model("tiny.en")
    audio_tagging_time_resolution = 6
    result = model.transcribe(orig_file, at_time_res=audio_tagging_time_resolution, no_speech_threshold=.75, fp16=False)


    # 0 = speech, 137 = music
    # get list of all availabe sound type ids by calling: whisper.print_label_name(language='en')
    audio_tag_result = whisper_at.parse_at_label(result, language='follow_asr', top_k=5, p_threshold=0, include_class_list=[0, 137])

    

    # create list of speech only time stamps
    speech_timestamp_samples = get_only_speech_timestamps(audio_tag_result)

    if len(speech_timestamp_samples):
        # merge all speech chunks to one audio
        print("Merging speech chunks into new file")
        print(datetime.datetime.utcnow())
        wav = read_audio(orig_file, sampling_rate=16000)

        save_audio(speech_only_file, collect_chunks(speech_timestamp_samples, wav), sampling_rate=16000)

        return True
    else:
        return False
    

def reduce_audio_to_voice_only_using_silero(orig_file, voice_only_file):
    # Reduce to voice parts only
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

    mp3 = read_audio(orig_file, sampling_rate=SAMPLING_RATE)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(mp3, model, sampling_rate=SAMPLING_RATE)
    # merge all speech chunks to one audio
    print("Merging voice chunks into new file")
    print(datetime.datetime.utcnow())
    save_audio(voice_only_file, collect_chunks(speech_timestamps, mp3), sampling_rate=SAMPLING_RATE) 

    # get the length of the voice only file

    process = subprocess.Popen(['ffmpeg',  '-i', voice_only_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout.decode(), re.DOTALL).groupdict()
    
    wav_total_minutes = int(matches['hours']) * 60 + int(matches['minutes'])
    print("voice only file length:", wav_total_minutes, "minutes")

    if wav_total_minutes > 20:
        print('**** trimming voice only file')
        trimmed_voice_file = "temp_voice_only_file_trimmed.wav"
        
        # Will take too long to summarize. let's reduce length before next steps
        # The longer the episode, the less chance their is music to cut out in the next step when searching for speech. 
        # so we can cut more now from longer files
        if wav_total_minutes > 40:
            new_length = "00:06:00"
        elif wav_total_minutes > 33:
            new_length = "00:16:30"
        else:
            new_length = "00:20:00"


        save_portion_of_audio_file(orig_audio_file=voice_only_file, new_file=trimmed_voice_file, start_time="00:00:00", length = new_length)

        return trimmed_voice_file
    else:
        return voice_only_file
   


def transcribe_audio(audio_file, ep):
    # transcribe the audio
    print('**** transcribing audio')
    print(datetime.datetime.utcnow())
    model = whisper.load_model("small.en")

    show_prompts = f"{ep['showName']} {ep['host']}"
    if ep['source'] == 'ciut':
        station_prompts = "From the roots up CIUT 89.5 FM"
    elif ep['source'] == 'cfru':
        station_prompts = "CFRU archives You're listening to 93.3 FM."
    else:
        station_prompts = ""

    result = model.transcribe(audio_file, no_speech_threshold=.6, fp16=False, initial_prompt= f"{show_prompts} {station_prompts}")

    txt = result["text"]
    print('transcription raw',txt)
    # Often commercials at begining. This will muddle up description.
    # Use keyword indicators to guess where the show actually starts
    key_phrase_search_limit = 2500

    show_name_punctuation_removed = ep['showName'].lower().translate(str.maketrans('', '', string.punctuation))

    # Often times show names are shortened when spoken. Creates a reduced version of the show name to search for.
    show_name_parts = show_name_punctuation_removed.split()
    if len(show_name_parts) > 2:
        show_name_shortened = f"{show_name_parts[0]} {show_name_parts[1]}"
        

    if show_name_punctuation_removed in txt[:key_phrase_search_limit].lower():
        print("found show name key phrase", show_name_punctuation_removed)
        keyPhraseIdx = txt.lower().find(show_name_punctuation_removed)          
    elif len(show_name_parts) > 2 and show_name_shortened.lower() in txt[:key_phrase_search_limit].lower():
        print("found show name shortened key phrase", show_name_shortened)
        keyPhraseIdx = txt.lower().find(show_name_shortened.lower())
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
        print("no key phrase found")
        keyPhraseIdx = -1
    

    if keyPhraseIdx > -1:
        print("key phrase found at index", keyPhraseIdx)
        cleaned_txt = txt[keyPhraseIdx:]
    else:
        # If no key phrase found, just recklessly chop 800 characters + a percentage of length
        if len(txt) > 3000:
            cut_length = int(800 + len(txt)*.1)
            cleaned_txt = txt[cut_length:]
        else:
            cleaned_txt = txt

    # Can also be ads/messages at the end of the show. Try and locate end of show indicators to guess where the show actually ends
    
    # define phrases often used by station after a show
    station_boilerplate = None
    if ep['source'] == 'cfru':
        station_boilerplate = "You're listening to CFRU 93.3 FM."

    if station_boilerplate:
        last_station_boilerplate_idx = cleaned_txt.rfind(station_boilerplate)
    
    # find last index of station reference
    last_station_idx = cleaned_txt.lower().rfind(ep['source'])
    
    if station_boilerplate and last_station_boilerplate_idx > len(cleaned_txt)*.5:
        cleaned_txt = cleaned_txt[:last_station_boilerplate_idx]
    elif last_station_idx > len(cleaned_txt)*.75:
        cleaned_txt = cleaned_txt[:last_station_idx]

    # Really short descriptions may not be useful and could contain lots of irrelevant info from ads / station messages.
    if len(cleaned_txt) < 2200:
        cleaned_txt = None

    print('cleaned transcription',cleaned_txt)
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
    # Limit text used for summary to max_characters as the model has limit on token numbers
    print("transcript length:", len(txt))
    txt_for_summary = txt[:max_characters]
    summary = summarizer(txt_for_summary, max_length=250, min_length=50, do_sample=True)
    return summary[0]['summary_text']

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



