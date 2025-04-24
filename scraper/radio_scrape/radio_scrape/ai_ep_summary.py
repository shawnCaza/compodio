import subprocess
import shlex
import datetime
import time
import os
import re
import requests
import string
import platform as pf
import sys

import whisper
from lightning_whisper_mlx import LightningWhisperMLX
import whisper_at

from transformers import pipeline
import torch
import torchaudio

from nltk.tokenize.texttiling import TextTilingTokenizer

import scraper_MySQL


# os.environ["TOKENIZERS_PARALLELISM"] = "false" #may be required if multiple threads are unavailable
audio_directory = f"{os.path.dirname(os.path.realpath(__file__))}/temp_audio/"


def main():
    global audio_directory

    download_file = f"{audio_directory}temp_audio_for_ai_summary.wav"
    speech_only_file = f"{audio_directory}temp_speech_only_file.wav"
    speech_only_file_trimmed = f"{audio_directory}temp_speech_only_file_trimmed.wav"

    # Get episodes without a description
    mySQL = scraper_MySQL.MySQL()

    query = """
        SELECT `episodes`.`id`, show_id, mp3, showName, source, `host`, lang, source
        FROM episodes  
        LEFT JOIN shows ON `shows`.`id` = `episodes`.`show_id`               
        WHERE ai_desc is null and source != 'ckut'
        AND (lang is null OR lang = 'en')
        ORDER BY `episodes`.`id` DESC
        LIMIT 100
    """

    # query = """
    #     SELECT `episodes`.`id`, show_id, mp3, showName, source, `host`, lang, source
    #     FROM episodes
    #     LEFT JOIN shows ON `shows`.`id` = `episodes`.`show_id`
    #     WHERE episodes.id = 69770
    #     AND (lang is null OR lang = 'en')
    #     ORDER BY `episodes`.`id` DESC
    #     LIMIT 1
    # """

    eps = mySQL.get_query(query)
    removed_eps = []
    for ep in eps:
        print("ep", ep)
        voice_only_file = f"{audio_directory}temp_voice_only_file.wav"  # reset voice only file, as it may have been trimmed in previous loop

        print("\n*****", ep["id"])

        # validate mp3 - solution may not be robust for all servers(https://stackoverflow.com/q/70446485/1586014)
        r = requests.head(ep["mp3"], stream=True)
        if r.status_code < 400:

            save_portion_of_audio_file(ep["mp3"], download_file, length="00:59:00")

            if ep["lang"] == None:
                # detect language by first saving an excerpt than running whisper transcribe
                lang = detect_lang(download_file)
                mySQL.set_show_lang(ep["show_id"], lang)
            else:
                lang = ep["lang"]

            # Only supporting english for now
            if lang == "en":

                voice_only_file, show_type_guess = (
                    reduce_audio_to_voice_only_using_silero(
                        download_file, voice_only_file
                    )
                )

                if voice_only_file != False:
                    speech_found, key_phrase = (
                        reduce_audio_to_speech_only_using_whisper(
                            voice_only_file, speech_only_file, ep
                        )
                    )

                    if speech_found:

                        length_of_speech_only_file = get_audio_length_in_minutes(
                            speech_only_file
                        )

                        if (
                            show_type_guess == "talk"
                            and length_of_speech_only_file > 1
                            and key_phrase
                        ):
                            # Idea is show with lots of talking may introduce all topics at begining. If not transcribing whole show, the first topic may drown out the others in summary if we don't trim it.
                            save_portion_of_audio_file(
                                speech_only_file,
                                speech_only_file_trimmed,
                                length="00:01:30",
                            )

                        else:
                            # trim to reduce transcription time
                            save_portion_of_audio_file(
                                speech_only_file,
                                speech_only_file_trimmed,
                                length="00:10:00",
                            )

                        transcription = transcribe_audio(
                            speech_only_file_trimmed, ep, show_type_guess
                        )

                        if transcription:
                            # summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #limited length ~1024 tokens. Short and sweet, but often misses the point. https://huggingface.co/facebook/bart-large-cnn

                            # summarizer = pipeline("summarization", model="google/bigbird-pegasus-large-bigpatent") # Pretty terrible at summarizing music shows. Lots of repition. - Max length 4096 https://huggingface.co/google/bigbird-pegasus-large-bigpatent

                            summarizer = pipeline(
                                "summarization",
                                model="pszemraj/pegasus-x-large-book-summary",
                            )  # Pretty good. Often does track listings. Can ramble on occasionaly. Max length ??? complains of indexing errors if > 1024 https://huggingface.co/pszemraj/pegasus-x-large-book-summary

                            # title_summarizer = pipeline("summarization", model="ybagoury/flan-t5-base-tldr_news")
                            # title_summarizer = pipeline("summarization", model="JulesBelveze/t5-small-headline-generator")

                            summary_txt = create_summary(transcription, summarizer)

                            summary_txt_paragraphed = add_paragraphs(summary_txt)
                            # title = create_title(summary[0]['summary_text'], title_summarizer)
                        else:
                            # no speech found in audio
                            summary_txt_paragraphed = ""
                    else:
                        # no speech found in audio.
                        # Could be something wrong with audio file.
                        summary_txt_paragraphed = ""
                else:
                    summary_txt_paragraphed = ""

                # add to db
                print("saving to db")
                print(datetime.datetime.utcnow())
                print(summary_txt_paragraphed)

                # summary model(pegasus-x-large-book-summary) often hallucinates 'Underground Man' in place of a persons name.
                summary_txt_paragraphed = summary_txt_paragraphed.replace(
                    "Underground Man", "host"
                ).replace("underground man", "host")

                mySQL.insert_ep_ai_details(ep["id"], summary_txt_paragraphed)
                break

        else:
            print("mp3 not found")
            if r.status_code in [400, 401, 402, 403, 404, 405, 406, 407, 409, 410]:
                print("removing episode from db")
                removed_eps.append(ep["show_id"])
                mySQL.remove_old_eps_by_show(ep["show_id"], f"id = {ep['id']}")

            # TODO: handle level 500 errors, so summatization isn't blocked when one server goes down temporarily.
            # For now we are selecting many episodes, and breaking the for loop after the first one is processed.

    print("removed eps:", removed_eps)


def save_portion_of_audio_file(
    orig_audio_file, new_file, start_time="00:00:00", length="00:30:00"
):
    """saves audio. Defaults to downloading 30 minutes.
    orig_audio_file: url address of file to download or local file location.
    new_file: specifies path and name to output local saved file.
    start_time: specifies time code of file to start downloading.
    end_time: specifies time code at which to stop downloading.

    """
    print("**** saving audio")
    print(datetime.datetime.utcnow())

    command = shlex.split(
        f'ffmpeg -y -i "{orig_audio_file}" -ss {start_time} -t {length} -acodec pcm_s16le -ar 16000 -ac 1 "{new_file}"'
    )
    subprocess.call(command)


def detect_lang(download_file):
    """detects language by first saving an exceprt than running whisper transcribe. returns: language code"""
    # save excerpt
    lang_detect_excerpt_file = "temp_lang_detect_excerpt_file.wav"
    save_portion_of_audio_file(
        download_file,
        lang_detect_excerpt_file,
        start_time="00:10:00",
        length="00:10:00",
    )

    print("**** Detecting language")
    print(datetime.datetime.utcnow())
    model = whisper_model("tiny")
    result = model.transcribe(
        lang_detect_excerpt_file, no_speech_threshold=0.75, fp16=False
    )
    lang = result["language"]
    print("language:", lang)
    return lang


def reduce_audio_to_speech_only_using_whisper(orig_file, speech_only_file, ep):
    """Reduce to voice parts only
    Uses whisper_at which is a fork of whisper that includes audio tagging
    Audio tagging set to identify speech and music.
    Returns True if speech only file was created, False if not.
    """

    print("**** Finding speech only timestamps (whisper_at)")
    print(datetime.datetime.utcnow())
    model = whisper_at.load_model("tiny.en")
    prompts = define_prompts(ep)
    audio_tagging_time_resolution = 6
    result = model.transcribe(
        orig_file,
        at_time_res=audio_tagging_time_resolution,
        no_speech_threshold=0.75,
        fp16=False,
    )
    print("result", result["text"])

    key_phrase_idx, key_phrase = find_key_phrase_idx(result["text"], ep)

    if key_phrase:
        print("key phrase", key_phrase)
        # find the start time of the key phrase in result['segments']
        key_phrase_timestamps = [
            seg["start"]
            for seg in result["segments"]
            if key_phrase in seg["text"].lower()
        ]
        print("key phrase timestamps", key_phrase_timestamps)

    # 0 = speech, 137 = music
    # get list of all availabe sound type ids by calling: whisper.print_label_name(language='en')
    audio_tag_result = whisper_at.parse_at_label(
        result,
        language="follow_asr",
        top_k=5,
        p_threshold=0,
        include_class_list=[0, 137],
    )

    # create list of speech only time stamps
    if key_phrase and len(key_phrase_timestamps):
        min_start_time = key_phrase_timestamps[0]
    else:
        min_start_time = None

    speech_timestamp_samples = get_only_speech_timestamps(
        audio_tag_result, min_start_time
    )

    if len(speech_timestamp_samples):
        # merge all speech chunks to one audio
        print("Merging speech chunks into new file")
        print(datetime.datetime.utcnow())
        wav = read_audio(orig_file, sampling_rate=16000)

        save_audio(
            speech_only_file,
            collect_chunks(speech_timestamp_samples, wav),
            sampling_rate=16000,
        )

        return True, key_phrase
    else:
        return False, key_phrase


def reduce_audio_to_voice_only_using_silero(orig_file, voice_only_file):
    global audio_directory
    # Reduce to voice parts only
    print("**** Finding voice only timestamps (silero_vad)")
    print(datetime.datetime.utcnow())
    # torch.set_num_threads(1) #may be required if on some systems
    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        force_reload=False,
        trust_repo=True,
        onnx=False,
    )

    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
    SAMPLING_RATE = 16000

    audio = read_audio(orig_file, sampling_rate=SAMPLING_RATE)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(audio, model, sampling_rate=SAMPLING_RATE)

    if len(speech_timestamps):
        # merge all speech chunks to one audio
        print("Merging voice chunks into new file")
        print(datetime.datetime.utcnow())
        save_audio(
            voice_only_file,
            collect_chunks(speech_timestamps, audio),
            sampling_rate=SAMPLING_RATE,
        )
    else:
        return False, None

    # get the length of the voice only file

    wav_total_minutes = get_audio_length_in_minutes(voice_only_file)

    if wav_total_minutes > 20:
        print("**** trimming voice only file")
        trimmed_voice_file = f"{audio_directory}temp_voice_only_file_trimmed.wav"

        # Will take too long to summarize. let's reduce length before next steps
        # The longer the episode, the less chance their is music to cut out in the next step when searching for speech.
        # so we can cut more now from longer files
        if wav_total_minutes > 40:
            new_length = "00:06:00"
            show_type_guess = "talk"
        elif wav_total_minutes > 33:
            new_length = "00:16:30"
            show_type_guess = "mix"
        else:
            show_type_guess = "music"
            new_length = "00:20:00"

        save_portion_of_audio_file(
            orig_audio_file=voice_only_file,
            new_file=trimmed_voice_file,
            start_time="00:00:00",
            length=new_length,
        )

        return trimmed_voice_file, show_type_guess
    else:
        return voice_only_file, "much music"


def transcribe_audio(audio_file, ep, show_type_guess):

    # transcribe the audio
    print("**** transcribing audio")
    print(datetime.datetime.utcnow())
    audio_file_length_in_minutes = int(get_audio_length_in_minutes(audio_file))
    print("audio_file_length_in_minutes", audio_file_length_in_minutes)

    if show_type_guess == "talk" and audio_file_length_in_minutes == 1:
        print("using large model for short talk show excerpt")
        model = whisper_model("distil-large-v3")  # whisper.load_model()
    else:
        print("using small model")
        model = whisper_model("distil-small.en")

    prompts = define_prompts(ep)
    result = model.transcribe(
        audio_file, no_speech_threshold=0.6, fp16=False, initial_prompt=prompts
    )

    txt = result["text"]
    # print('segments', result['segments'])
    print("transcription raw", txt)

    # Can  be ads/messages at the end of the show. Try and locate end of show indicators to guess where the show actually ends

    # define phrases often used by station after a show
    station_boilerplate = None
    if ep["source"] == "cfru":
        station_boilerplate = "You're listening to CFRU 93.3 FM."

    if station_boilerplate:
        last_station_boilerplate_idx = txt.rfind(station_boilerplate)

    # find last index of station reference
    last_station_idx = txt.lower().rfind(ep["source"])

    if station_boilerplate and last_station_boilerplate_idx > len(txt) * 0.4:
        print("found station boilerplate. Cutting")
        cleaned_txt = txt[:last_station_boilerplate_idx]
    elif last_station_idx > len(txt) * 0.75:
        print("found station name near end. Cutting")
        cleaned_txt = txt[:last_station_idx]
    else:
        cleaned_txt = txt

    # Really short descriptions may not be useful and could contain lots of irrelevant info from ads / station messages.
    if len(cleaned_txt) < 900 and not (
        show_type_guess == "talk" and audio_file_length_in_minutes == 1
    ):
        cleaned_txt = None

    print("cleaned transcription", cleaned_txt)
    # audio_tag_result = whisper.parse_at_label(result, language='follow_asr', top_k=5, p_threshold=-1, include_class_list=list(range(527)))

    return cleaned_txt


def create_summary(txt, summarizer, max_characters=3250):
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

    # set max token length relative to length of text + based on assumption 1 token ~= 4 characters.
    # could use tiktokenizer(https://github.com/openai/tiktoken/blob/main/README.md) to get more exact token length, but maybe this is close enough.
    approx_tokens_expected = len(txt_for_summary) / 4
    max_length = int(
        approx_tokens_expected / 2 if approx_tokens_expected / 2 < 300 else 300
    )
    min_length = int(max_length / 3 if max_length / 3 > 50 else 50)

    summary = summarizer(
        txt_for_summary, max_length=max_length, min_length=min_length, do_sample=True
    )
    return summary[0]["summary_text"]


def create_title(txt, summarizer):
    # create title by summarizing summary
    print("**** Creating title")
    print(datetime.datetime.utcnow())
    title = summarizer(txt, max_length=30, min_length=15, do_sample=True)
    return title


def define_prompts(ep):
    show_prompts = f"{ep['showName']} {ep['host']}"
    if ep["source"] == "ciut":
        station_prompts = "From the roots up CIUT 89.5 FM"
    elif ep["source"] == "cfru":
        station_prompts = "CFRU archives You're listening to 93.3 FM."
    else:
        station_prompts = ""

    return f"{show_prompts} {station_prompts}"


def find_key_phrase_idx(txt, ep):
    # Often commercials at begining. This will muddle up description.
    # Use keyword indicators to guess where the show actually starts
    key_phrase_search_limit = 5000

    show_name_punctuation_removed = (
        ep["showName"].lower().translate(str.maketrans("", "", string.punctuation))
    )
    print("show_name_punctuation_removed", show_name_punctuation_removed)

    # Often times show names are shortened when spoken. Creates a reduced version of the show name to search for.
    show_name_parts = show_name_punctuation_removed.split()

    if len(show_name_parts) > 2:
        show_name_shortened = f"{show_name_parts[0]} {show_name_parts[1]}"

    if show_name_punctuation_removed in txt[:key_phrase_search_limit].lower():
        print("found show name key phrase", show_name_punctuation_removed)
        key_phrase = show_name_punctuation_removed.lower()

    elif (
        len(show_name_parts) > 2
        and show_name_shortened.lower() in txt[:key_phrase_search_limit].lower()
    ):
        print("found show name shortened key phrase", show_name_shortened)
        key_phrase = show_name_shortened.lower()

    elif (
        ep["host"]
        and len(ep["host"])
        and ep["host"].split()[0].lower() in txt[:key_phrase_search_limit].lower()
    ):
        key_phrase = ep["host"].split()[0].lower()
        print("found host key phrase", ep["host"].split()[0])

    elif "from the roots up" in txt[:key_phrase_search_limit].lower():
        print("found roots up key phrase")
        key_phrase = "from the roots up"

    elif "cfru archives" in txt[:key_phrase_search_limit].lower():
        key_phrase = "cfru archives"
        print("found CFRU archives key phrase")

    # elif 'welcome' in txt[:key_phrase_search_limit]:
    #     print("found welcome key phrase")
    #     key_phrase_idx = txt.find('welcome')
    # elif 'hello' in txt[:key_phrase_search_limit]:
    # print("found hi key phrase")
    # key_phrase_idx = txt.find('hi')

    else:
        key_phrase = None
        print("no key phrase found")
        key_phrase_idx = -1

    if key_phrase:
        key_phrase_idx = txt.lower().find(key_phrase)

    return key_phrase_idx, key_phrase


def get_only_speech_timestamps(audio_tag_results: list[dict], min_start_time=None):
    """Returns list of only speech timestamps from audio_tag_result"""
    speech_timestamp_samples: list[dict] = []
    sample_rate = 16000

    for label in audio_tag_results:

        if (
            min_start_time
            and label["time"]["end"] > min_start_time
            or not min_start_time
        ):

            tags_dict = dict(label["audio tags"])
            if "Speech" in tags_dict:
                speech_timestamp_samples.append(
                    {
                        "start": label["time"]["start"] * sample_rate,
                        "end": label["time"]["end"] * sample_rate,
                    }
                )

    return speech_timestamp_samples


def add_paragraphs(summary_txt: str):
    """Returns text divided into paragraphs by detected 'shifts in topic'. Uses '\n\n' to denote paragraph breaks."""
    print("**** Adding paragraphs")
    print(datetime.datetime.utcnow())

    if len(summary_txt) < 400:
        return summary_txt

    # Tokenizer expects paragraphs in text. Since we don't have them, we'll add '\n\n' to every sentence.
    paragraphed_summary_for_tokenizer = (
        summary_txt.replace('."', '."\n\n')
        .replace(".", ".\n\n")
        .replace('?"', '?"\n\n')
        .replace("?", "?\n\n")
        .replace('!"', '!"\n\n')
        .replace("!", "!\n\n")
    )

    if len(paragraphed_summary_for_tokenizer.split("\n\n")) < 7:
        # trying to errors in tokenizer smoothing algorithm
        return summary_txt

    # Now we can feed the text to the tokenizer to detect 'topics'
    print("paragraphed_summary_for_tokenizer", paragraphed_summary_for_tokenizer)

    # Create tokenizer
    tokenizer = TextTilingTokenizer()
    topic_tokens = tokenizer.tokenize(paragraphed_summary_for_tokenizer)

    # remove the line breaks we added previously, then reform our summary with paragraph breaks based on the tokenizer's topic detection.
    paragraphs = [topic.replace("\n\n", "").strip() for topic in topic_tokens]
    summary_txt_paragraphed = "\n\n".join(paragraphs)

    return summary_txt_paragraphed


def get_audio_length_in_minutes(audio_file):
    """Returns length of audio file in minutes"""
    print("**** Getting audio length")
    print(datetime.datetime.utcnow())
    command = shlex.split(
        f'ffprobe -i "{audio_file}" -show_entries format=duration -v quiet -of csv="p=0"'
    )
    result = subprocess.check_output(command)
    return float(result) / 60


###### From silero_vad
def read_audio(path: str, sampling_rate: int = 16000):

    wav, sr = torchaudio.load(path)

    if wav.size(0) > 1:
        wav = wav.mean(dim=0, keepdim=True)

    if sr != sampling_rate:
        transform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=sampling_rate)
        wav = transform(wav)
        sr = sampling_rate

    assert sr == sampling_rate
    return wav.squeeze(0)


def collect_chunks(tss: list[dict], wav: torch.Tensor):
    chunks = []
    for i in tss:
        chunks.append(wav[i["start"] : i["end"]])
    return torch.cat(chunks)


def save_audio(path: str, tensor: torch.Tensor, sampling_rate: int = 16000):
    torchaudio.save(path, tensor.unsqueeze(0), sampling_rate, bits_per_sample=16)


def whisper_model(model_name: str):
    print("platform:", pf.system(), "processor:", pf.processor())
    if sys.platform == "darwin" and pf.processor() == "arm":
        print("Using LightningWhisperMLX for macOS ARM")
        return LightningWhisperMLX(model=model_name, batch_size=12, quant=None)
    else:
        # Remove 'distil-' prefix as whisper.load_model() doesn't support it
        return whisper.load_model(
            model_name.replace("distil-", ""),
            device="cuda" if torch.cuda.is_available() else "cpu",
        )


###### end from silero_vad

if __name__ == "__main__":
    main()
    # ep = {'id': 66843, 'show_id': 30061, 'mp3': 'https://archive.cfru.ca/archive/2023/10/10/Power Up! with Electrified Voltage - October 10, 2023 at 14:00 - CFRU 93.3.mp3', 'showName': 'IF 2023', 'source': 'cfru', 'host': 'various', 'lang': 'en'}

    # reduce_audio_to_speech_only_using_whisper("/Users/scaza/Sites/community-podcast/scraper/radio_scrape/radio_scrape/temp_audio/temp_voice_only_file.wav", "/Users/scaza/Sites/community-podcast/scraper/radio_scrape/radio_scrape/temp_audio/temp_speech_only_file.wav", ep)

    # transcribe_audio("/Users/scaza/Sites/community-podcast/scraper/radio_scrape/radio_scrape/temp_audio/temp_speech_only_file_trimmed.wav", ep, "talk")
