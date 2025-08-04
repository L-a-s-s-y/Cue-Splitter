from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations
import shutil
import psycopg2
import os
from charset_normalizer import from_path

ALLOWED_EXTENSIONS = {'flac', 'opus', 'mp3', 'wav', 'ogg'}

def crear_tabla(conexion, el_cursor):
    el_cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",("chopped_musical",))
    if not el_cursor.fetchone()[0]:
        el_cursor.execute("""
            CREATE TABLE chopped_musical(
                discid      char(8) CONSTRAINT discid PRIMARY KEY,
                title       varchar(150),
                performer   varchar(150),
                date        smallint,
                genre       varchar(100)
            );
        """)
    conexion.commit()

def album_info(aCueSheet):
    try:
        conexion = psycopg2.connect(
            dbname="music_chops",
            user="postgres",
            password="1234",
            #host="localhost"
            host="my-postgres-database"
        )
        el_cursor = conexion.cursor()
        crear_tabla(conexion, el_cursor)
        respuesta = {}
        getdata = FFCueSplitter(filename=aCueSheet, dry=True)
        do_not_repeat = False
        el_cursor.execute("SELECT discid FROM public.chopped_musical WHERE discid = %s",(getdata.cue.meta.data['DISCID'],))
        do_not_repeat = el_cursor.fetchone() is None
        print("----------------------------------------------")
        if 'DISCID' in getdata.cue.meta.data:
            print("DISCID: "+getdata.cue.meta.data['DISCID'])
            respuesta['DISCID'] = getdata.cue.meta.data['DISCID']
            if do_not_repeat:
                el_cursor.execute("INSERT INTO public.chopped_musical (discid, title, performer, date, genre) VALUES (%s,%s,%s,%s,%s)", (respuesta['DISCID'], 'XXYYYYZZ', 'XXYYYYZZ', '1999', 'XXYYYYZZ'))

        if 'ALBUM' in getdata.cue.meta.data:
            print("Album: "+getdata.cue.meta.data['ALBUM'])
            respuesta['Album'] = getdata.cue.meta.data['ALBUM']
            if do_not_repeat:
                el_cursor.execute("UPDATE public.chopped_musical SET title = %s WHERE discid = %s",(respuesta['Album'],respuesta['DISCID']))

        if 'PERFORMER' in getdata.cue.meta.data:
            print("Intérpretes: "+getdata.cue.meta.data['PERFORMER'])
            respuesta['Interpretes'] = getdata.cue.meta.data['PERFORMER']
            if do_not_repeat:
                el_cursor.execute("UPDATE public.chopped_musical SET performer = %s WHERE discid = %s",(respuesta['Interpretes'],respuesta['DISCID']))

        if 'DATE' in getdata.cue.meta.data:
            print("Año: "+getdata.cue.meta.data['DATE'])
            respuesta['Fecha'] = getdata.cue.meta.data['DATE']
            if do_not_repeat:
                el_cursor.execute("UPDATE public.chopped_musical SET date = %s WHERE discid = %s",(respuesta['Fecha'],respuesta['DISCID']))

        if 'CATALOG' in getdata.cue.meta.data:
            print("Nº Catálogo: "+getdata.cue.meta.data['CATALOG'])
            respuesta['catalog'] = getdata.cue.meta.data['CATALOG']

        if 'GENRE' in getdata.cue.meta.data:
            print("Género: "+getdata.cue.meta.data['GENRE'])
            respuesta['Genero'] = getdata.cue.meta.data['GENRE']
            if do_not_repeat:
                el_cursor.execute("UPDATE public.chopped_musical SET genre = %s WHERE discid = %s",(respuesta['Genero'],respuesta['DISCID']))
    
        print("*****************PISTAS***********************")
        indice = 0
        tracks = []
        for i in range(len(getdata.audiotracks)):
            if 'TITLE' in getdata.audiotracks[i]:
                print(getdata.audiotracks[i]['TITLE'])
                tracks.append(getdata.audiotracks[i]['TITLE'])
        print("----------------------------------------------")
        respuesta['tracks'] = tracks
        conexion.commit()
        el_cursor.close()
        conexion.close()
        return respuesta
    except psycopg2.OperationalError as e:
        #PROCEDER SIN ESCRIBIR EN LA BASE DE DATOS
        respuesta = {}
        getdata = FFCueSplitter(filename=aCueSheet, dry=True)
        print("----------------------------------------------")
        if 'DISCID' in getdata.cue.meta.data:
            print("DISCID: "+getdata.cue.meta.data['DISCID'])
            respuesta['DISCID'] = getdata.cue.meta.data['DISCID']
            
        if 'ALBUM' in getdata.cue.meta.data:
            print("Album: "+getdata.cue.meta.data['ALBUM'])
            respuesta['Album'] = getdata.cue.meta.data['ALBUM']
            
        if 'PERFORMER' in getdata.cue.meta.data:
            print("Intérpretes: "+getdata.cue.meta.data['PERFORMER'])
            respuesta['Interpretes'] = getdata.cue.meta.data['PERFORMER']
            
        if 'DATE' in getdata.cue.meta.data:
            print("Año: "+getdata.cue.meta.data['DATE'])
            respuesta['Fecha'] = getdata.cue.meta.data['DATE']
            
        if 'CATALOG' in getdata.cue.meta.data:
            print("Nº Catálogo: "+getdata.cue.meta.data['CATALOG'])
            respuesta['catalog'] = getdata.cue.meta.data['CATALOG']

        if 'GENRE' in getdata.cue.meta.data:
            print("Género: "+getdata.cue.meta.data['GENRE'])
            respuesta['Genero'] = getdata.cue.meta.data['GENRE']
            
        print("*****************PISTAS***********************")
        indice = 0
        tracks = []
        for i in range(len(getdata.audiotracks)):
            if 'TITLE' in getdata.audiotracks[i]:
                print(getdata.audiotracks[i]['TITLE'])
                tracks.append(getdata.audiotracks[i]['TITLE'])
        print("----------------------------------------------")
        respuesta['tracks'] = tracks
        print(getdata.probedata)
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
wav_pcm, wav_ar, 
ogg_bitrate, ogg_quality, ogg_ar,
mp3_bitrate, mp3_ar):

    codec_allowed = check_codec_target_file(cue_file)
    print (codec_allowed)
    final_outputformat = None
    final_ffmpeg_add_params='-c copy'

    if output_format == 'copy':
        final_ffmpeg_add_params = '-c copy'
        if not codec_allowed:
            final_outputformat = 'flac'
    elif output_format == 'flac':
        final_outputformat = output_format
        final_ffmpeg_add_params = f'-ar {flac_ar} -sample_fmt {flac_sample_fmt} -compression_level {flac_compression_level}'
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
        final_ffmpeg_add_params = f'-c:a libmp3lame -ar {mp3_ar} -b:a {mp3_bitrate}'

    print(final_outputformat)
    split = FileSystemOperations(
        filename=cue_file,
        outputdir=cue_file.split('.')[0],
        #del_orig_files=True,
        outputformat='flac',
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

    return shutil.make_archive(cue_file.split('.')[0],'zip',cue_file.split('.')[0])