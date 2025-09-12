from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations
from pathlib import Path
import shutil
import os
from charset_normalizer import from_path

ALLOWED_EXTENSIONS = {'flac', 'opus', 'mp3', 'wav', 'ogg', 'wv'}

def album_info(aCueSheet):
    respuesta = {}
    getdata = FFCueSplitter(filename=aCueSheet, dry=True)
    #print("----------------------------------------------")
    if 'DISCID' in getdata.cue.meta.data:
        #print("DISCID: "+getdata.cue.meta.data['DISCID'])
        respuesta['DISCID'] = getdata.cue.meta.data['DISCID']
        
    if 'ALBUM' in getdata.cue.meta.data:
        #print("Album: "+getdata.cue.meta.data['ALBUM'])
        respuesta['Album'] = getdata.cue.meta.data['ALBUM']
        
    if 'PERFORMER' in getdata.cue.meta.data:
        #print("Intérpretes: "+getdata.cue.meta.data['PERFORMER'])
        respuesta['Interpretes'] = getdata.cue.meta.data['PERFORMER']
        
    if 'DATE' in getdata.cue.meta.data:
        #print("Año: "+getdata.cue.meta.data['DATE'])
        respuesta['Fecha'] = getdata.cue.meta.data['DATE']
        
    if 'CATALOG' in getdata.cue.meta.data:
        #print("Nº Catálogo: "+getdata.cue.meta.data['CATALOG'])
        respuesta['catalog'] = getdata.cue.meta.data['CATALOG']
    if 'GENRE' in getdata.cue.meta.data:
        #print("Género: "+getdata.cue.meta.data['GENRE'])
        respuesta['Genero'] = getdata.cue.meta.data['GENRE']
        
    #print("*****************PISTAS***********************")

    tracks = []
    for i in range(len(getdata.audiotracks)):
        if 'TITLE' in getdata.audiotracks[i]:
            #print(getdata.audiotracks[i]['TITLE'])
            tracks.append(getdata.audiotracks[i]['TITLE'])
    #print("----------------------------------------------")
    respuesta['tracks'] = tracks
    respuesta['codec_type'] = getdata.probedata[0]['streams'][0]['codec_type']
    respuesta['codec_name'] = getdata.probedata[0]['streams'][0]['codec_name']
    respuesta['codec_long_name'] = getdata.probedata[0]['streams'][0]['codec_long_name']
    respuesta['sample_rate'] = getdata.probedata[0]['streams'][0]['sample_rate']
    respuesta['sample_fmt'] = getdata.probedata[0]['streams'][0]['sample_fmt']
    respuesta['channels'] = getdata.probedata[0]['streams'][0]['channels']
    if 'channel_layout' in getdata.probedata[0]['streams'][0]:
        respuesta['channel_layout'] = getdata.probedata[0]['streams'][0]['channel_layout']
    #print(getdata.probedata[0]['streams'][0]['sample_rate'])
    return respuesta

def allowed_audio(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_codec_target_file(cue_path):
    expected_audio_file = None

    codec_allowed = False

    if os.path.exists(cue_path): # Si el cue está en el servidor
        result = from_path(cue_path)
        best_match = result.best()
        #cue_en_lista = best_match.decoded.splitlines(keepends=True)
        with open(cue_path, 'r', encoding=best_match.encoding) as mod_cue:
            cue_en_lista = [line for line in mod_cue]
        print("--------------------------------------")
        for i in range(len(cue_en_lista)):
            if cue_en_lista[i].split(' ')[0] == "FILE":
                audio_file = cue_en_lista[i].split('\"')
                codec_allowed = check_codec_target_file(audio_file[1])
    return codec_allowed

def split_it_like_solomon(
cue_file, output_format, 
flac_compression_level, flac_ar, flac_sample_fmt, 
wv_compression_level, wv_ar, wv_sample_fmt, wv_bitrate, 
wav_pcm, wav_ar, 
ogg_bitrate, ogg_quality, ogg_ar,
mp3_bitrate, mp3_ar,
orig_codec, orig_sample_rate, orig_sample_fmt):

    cue_path = Path(cue_file).resolve()
    album_dir = cue_path.parent / cue_path.stem

    final_outputformat = None
    final_ffmpeg_add_params='-c copy'

    if output_format == 'copy':
        if orig_codec == 'flac':
            final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a flac -ar {orig_sample_rate} -sample_fmt {orig_sample_fmt} -compression_level 5'
            final_outputformat = 'flac'
        else:
            final_ffmpeg_add_params = '-map 0:a:0 -vn -c copy'
    elif output_format == 'flac':
        final_outputformat = output_format
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a flac -ar {flac_ar} -sample_fmt {flac_sample_fmt} -compression_level {flac_compression_level}'
    elif output_format == 'wav':
        final_outputformat = output_format
        final_ffmpeg_add_params = f'-ar {wav_ar} -c:a {wav_pcm}'
    elif output_format == 'ogg_vorbis':
        final_outputformat = 'ogg'
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a libvorbis -qscale:a {ogg_quality} -ar {ogg_ar}'
    elif output_format == 'ogg_opus':
        final_outputformat = 'ogg'
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a libopus -b:a {ogg_bitrate} -ar {ogg_ar}'
    elif output_format == 'mp3':
        final_outputformat = output_format
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a libmp3lame -ar {mp3_ar} -b:a {mp3_bitrate}'
    elif output_format == 'wavpack':
        final_outputformat = 'wv'
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a wavpack -compression_level {wv_compression_level} -sample_fmt {wv_sample_fmt} -ar {wv_ar}'
    elif output_format == 'wavpack_l':
        final_outputformat = 'wv'
        final_ffmpeg_add_params = f'-map 0:a:0 -vn -c:a wavpack -b:a {wv_bitrate} -compression_level {wv_compression_level} -sample_fmt {wv_sample_fmt} -ar {wv_ar}'

    #print(cue_file.split('.')[0])
    
    split = FileSystemOperations(
        filename=cue_file,
        #outputdir=cue_file.split('.')[0],
        outputdir=str(album_dir),
        del_orig_files=False,
        outputformat=final_outputformat,
        ffmpeg_add_params=final_ffmpeg_add_params,
        progress_meter='tqdm',
        prg_loglevel='info',
        ffmpeg_loglevel='error',
        overwrite='always'
    )
    if split.kwargs["dry"]:
        split.dry_run_mode()
    else:
        overwr = split.check_for_overwriting()
        if not overwr:
            split.work_on_temporary_directory()
    
    return shutil.make_archive(str(album_dir),'zip',str(album_dir))