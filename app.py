import streamlit as st
import streamlit.components.v1 as components
import json, html
from pathlib import Path
from difflib import SequenceMatcher

st.set_page_config(page_title='Trung – Việt Learning', page_icon='📚', layout='wide')
BASE = Path(__file__).parent
DATA_DIR = BASE / 'data'
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / 'lessons.json'

DEFAULT_DATA = {
    'version': 2,
    'folders': [
        {
            'id': 'hsk1', 'name': 'HSK 1',
            'settings': {'speed': 1.0, 'repeat': 2},
            'lessons': [
                {'id':'hsk1-001','title':'Chào hỏi','sentences':[{'id':'s1','chinese':'你好！','pinyin':'Nǐ hǎo!','vietnamese':'Xin chào!','audio':''}],
                 'vocabulary':[{'id':'v1','hanzi':'你','pinyin':'nǐ','meaning':'bạn','example':'你好！','example_vi':'Xin chào!','audio':''},{'id':'v2','hanzi':'好','pinyin':'hǎo','meaning':'tốt; khỏe','example':'你好！','example_vi':'Xin chào!','audio':''}],
                 'grammar':[{'id':'g1','title':'你好','explanation':'Cách chào hỏi thông dụng trong tiếng Trung.','example':'你好！','example_vi':'Xin chào!','audio':''}]}
            ]
        }
    ]
}


def load_data():
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
    try:
        raw = json.loads(DATA_FILE.read_text(encoding='utf-8'))
        if isinstance(raw, list):
            # Hỗ trợ dữ liệu phiên bản cũ dạng danh sách lessons
            folder = {'id':'imported','name':'Bài đã nhập','settings':{'speed':1.0,'repeat':2},'lessons':[]}
            for old in raw:
                folder['lessons'].append(legacy_lesson(old))
            return {'version':2,'folders':[folder]}
        if 'folders' in raw:
            for f in raw['folders']:
                f.setdefault('settings', {'speed':1.0,'repeat':2})
                f.setdefault('lessons', [])
            return raw
        if 'lessons' in raw:
            folder = {'id':'imported','name':'Bài đã nhập','settings':{'speed':1.0,'repeat':2},'lessons':[legacy_lesson(x) for x in raw['lessons']]}
            return {'version':2,'folders':[folder]}
    except Exception as e:
        st.error(f'Không đọc được dữ liệu hiện tại: {e}')
    return {'version':2,'folders':[]}


def legacy_lesson(x):
    if 'sentences' in x:
        return x
    return {'id':str(x.get('id') or 'lesson-'+str(abs(hash(x.get('title','bai'))))), 'title':x.get('title','Bài học'),
            'sentences':[{'id':'s1','chinese':x.get('chinese',''),'pinyin':x.get('pinyin',''),'vietnamese':x.get('vietnamese',''),'audio':x.get('audio','')}],
            'vocabulary':x.get('vocabulary',[]),'grammar':x.get('grammar',[])}


def save_data(d):
    DATA_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')


def speak(text, settings, audio=''):
    text = str(text or '').strip()
    if not text and not audio:
        return
    if audio:
        st.audio(audio)
    if text:
        safe = json.dumps(text, ensure_ascii=False)
        speed = float(settings.get('speed',1.0))
        repeat = int(settings.get('repeat',2))
        # Web Speech API: phát âm trực tiếp trên trình duyệt, có tốc độ và số lần lặp.
        components.html(f'''<div style="display:flex;align-items:center;gap:8px;font-family:Arial">
        <button id="play" style="padding:6px 12px;border:1px solid #999;border-radius:8px;background:#f5f5f5;cursor:pointer">🔊 Nghe ({speed:.1f}× · {repeat} lần)</button>
        <span id="status" style="font-size:12px;color:#777"></span></div>
        <script>
        const t={safe}; const rate={speed}; const count={repeat};
        const b=document.getElementById('play'), s=document.getElementById('status');
        b.onclick=()=>{{ if(!('speechSynthesis' in window)){{s.textContent='Trình duyệt chưa hỗ trợ đọc văn bản';return;}}
          window.speechSynthesis.cancel(); let n=0;
          const go=()=>{{ if(n>=count){{s.textContent='';return;}} const u=new SpeechSynthesisUtterance(t); u.lang='zh-CN'; u.rate=rate; n++; s.textContent='Lần '+n+'/'+count; u.onend=go; u.onerror=()=>s.textContent='Không phát được âm thanh'; window.speechSynthesis.speak(u); }}; go(); }};
        </script>''', height=45)


def get_lesson_label(x):
    return f"{x.get('title','Bài học')} · {x.get('id','')}"


data = load_data()
folders = data['folders']

st.title('📚 Trung – Việt Learning')
st.caption('Ứng dụng học tiếng Trung độc lập · Quản lý bài học theo thư mục tự tạo')

with st.sidebar:
    st.header('📁 Thư mục học')
    folder_names = [f.get('name','Thư mục') for f in folders]
    if folder_names:
        chosen_name = st.selectbox('Chọn thư mục', folder_names)
        folder = next(f for f in folders if f.get('name') == chosen_name)
        settings = folder.setdefault('settings', {'speed':1.0,'repeat':2})
        st.divider()
        st.subheader('🔊 Phát âm của thư mục này')
        speed = st.slider('Tốc độ đọc', 0.5, 2.0, float(settings.get('speed',1.0)), 0.1, key=f"speed_{folder['id']}")
        repeat = st.selectbox('Số lần lặp', [1,2,3,4,5,6,8,10], index=[1,2,3,4,5,6,8,10].index(int(settings.get('repeat',2))) if int(settings.get('repeat',2)) in [1,2,3,4,5,6,8,10] else 1, key=f"repeat_{folder['id']}")
        if speed != settings.get('speed') or repeat != settings.get('repeat'):
            settings['speed'], settings['repeat'] = speed, repeat
            save_data(data)
        st.caption('Thiết lập này chỉ áp dụng cho thư mục đang chọn. Mỗi thư mục lưu tốc độ và số lần lặp riêng.')
        lessons = folder.get('lessons', [])
        st.metric('Số bài trong thư mục', len(lessons))
    else:
        folder = None; settings = {'speed':1.0,'repeat':2}; lessons=[]
        st.info('Chưa có thư mục. Hãy tạo thư mục trong mục Quản lý dữ liệu.')
    st.divider()
    st.caption('Dữ liệu lưu tại data/lessons.json trong dự án Streamlit.')

if folder:
    tabs = st.tabs(['Trung → Việt','Việt → Trung','Nghe & chép','Từ vựng','Ngữ pháp','Quản lý dữ liệu'])
else:
    tabs = st.tabs(['Quản lý dữ liệu'])

if folder:
    with tabs[0]:
        st.subheader('Luyện dịch Trung → Việt')
        if lessons:
            lesson = st.selectbox('Chọn bài', lessons, format_func=get_lesson_label, key='cv_lesson')
            for i, sent in enumerate(lesson.get('sentences', [])):
                with st.container(border=True):
                    st.markdown(f"### {sent.get('chinese','')}")
                    st.write(f"**Pinyin:** {sent.get('pinyin','')}")
                    speak(sent.get('chinese',''), settings, sent.get('audio',''))
                    st.text_area('Bản dịch tiếng Việt của bạn', key=f"cv_{lesson.get('id')}_{sent.get('id',i)}")
                    if st.button('Hiện bản dịch', key=f"cv_show_{lesson.get('id')}_{sent.get('id',i)}"):
                        st.success(sent.get('vietnamese','Chưa có bản dịch'))
        else: st.info('Thư mục chưa có bài học.')

    with tabs[1]:
        st.subheader('Luyện dịch Việt → Trung')
        if lessons:
            lesson = st.selectbox('Chọn bài', lessons, format_func=get_lesson_label, key='vc_lesson')
            for i, sent in enumerate(lesson.get('sentences', [])):
                with st.container(border=True):
                    st.markdown(f"### {sent.get('vietnamese','')}")
                    st.text_input('Nhập câu tiếng Trung', key=f"vc_{lesson.get('id')}_{sent.get('id',i)}")
                    speak(sent.get('chinese',''), settings, sent.get('audio',''))
                    if st.button('Đối chiếu đáp án', key=f"vc_check_{lesson.get('id')}_{sent.get('id',i)}"):
                        st.info(f"**Đáp án:** {sent.get('chinese','')}\n\n**Pinyin:** {sent.get('pinyin','')}")
        else: st.info('Thư mục chưa có bài học.')

    with tabs[2]:
        st.subheader('Nghe và chép chính tả tiếng Trung')
        if lessons:
            lesson = st.selectbox('Chọn bài', lessons, format_func=get_lesson_label, key='listen_lesson')
            for i, sent in enumerate(lesson.get('sentences', [])):
                with st.container(border=True):
                    st.write(f'Câu {i+1}')
                    speak(sent.get('chinese',''), settings, sent.get('audio',''))
                    typed = st.text_input('Nghe rồi nhập lại câu', key=f"listen_{lesson.get('id')}_{sent.get('id',i)}")
                    if st.button('Kiểm tra', key=f"listen_check_{lesson.get('id')}_{sent.get('id',i)}"):
                        target = sent.get('chinese','')
                        st.write(f'Đáp án: {target}')
                        st.metric('Độ chính xác', f"{SequenceMatcher(None,typed,target).ratio()*100:.0f}%")
        else: st.info('Thư mục chưa có bài học.')

    with tabs[3]:
        st.subheader('Từ vựng')
        if lessons:
            lesson = st.selectbox('Chọn bài', lessons, format_func=get_lesson_label, key='vocab_lesson')
            if not lesson.get('vocabulary'): st.info('Bài này chưa có từ vựng.')
            for i, v in enumerate(lesson.get('vocabulary', [])):
                with st.container(border=True):
                    st.markdown(f"**{v.get('hanzi',v.get('word',''))}** · {v.get('pinyin','')}")
                    st.write(v.get('meaning',v.get('vietnamese','')))
                    speak(v.get('hanzi',v.get('word','')), settings, v.get('audio',''))
                    if v.get('example'):
                        st.caption('Ví dụ: '+v.get('example',''))
                        st.write(v.get('example_vi',''))
                        speak(v.get('example',''), settings, v.get('example_audio',''))
        else: st.info('Thư mục chưa có bài học.')

    with tabs[4]:
        st.subheader('Ngữ pháp')
        if lessons:
            lesson = st.selectbox('Chọn bài', lessons, format_func=get_lesson_label, key='grammar_lesson')
            if not lesson.get('grammar'): st.info('Bài này chưa có ngữ pháp.')
            for i, g in enumerate(lesson.get('grammar', [])):
                if isinstance(g,str): g={'title':g,'explanation':'','example':'','example_vi':''}
                with st.container(border=True):
                    st.markdown(f"**{g.get('title',g.get('pattern','Ngữ pháp'))}**")
                    st.write(g.get('explanation',g.get('meaning','')))
                    speak(g.get('title',g.get('pattern','')), settings, g.get('audio',''))
                    if g.get('example'):
                        st.caption('Ví dụ: '+g.get('example',''))
                        st.write(g.get('example_vi',''))
                        speak(g.get('example',''), settings, g.get('example_audio',''))
        else: st.info('Thư mục chưa có bài học.')

    management_tab = tabs[5]
else:
    management_tab = tabs[0]

with management_tab:
    st.subheader('Quản lý thư mục và bài học')
    with st.expander('➕ Tạo thư mục mới', expanded=False):
        new_folder = st.text_input('Tên thư mục (ví dụ: Giáo trình HSK 2, Giáo trình Boya...)')
        if st.button('Tạo thư mục'):
            if new_folder.strip() and not any(f.get('name')==new_folder.strip() for f in data['folders']):
                data['folders'].append({'id':'folder-'+str(abs(hash(new_folder.strip()))),'name':new_folder.strip(),'settings':{'speed':1.0,'repeat':2},'lessons':[]})
                save_data(data); st.success('Đã tạo thư mục.'); st.rerun()
            else: st.warning('Tên thư mục trống hoặc đã tồn tại.')

    if folder:
        with st.expander('➕ Thêm bài học vào thư mục đang chọn', expanded=False):
            lesson_title = st.text_input('Tên bài học', key='new_title')
            lesson_id = st.text_input('Mã bài (có thể để trống)', key='new_id')
            st.markdown('**Các câu Trung – Việt**')
            sentence_json = st.text_area('Nhập danh sách câu dạng JSON', value='[{"id":"s1","chinese":"你好！","pinyin":"Nǐ hǎo!","vietnamese":"Xin chào!","audio":""}]', height=120, key='new_sentences')
            vocab_json = st.text_area('Từ vựng dạng JSON', value='[]', height=90, key='new_vocab')
            grammar_json = st.text_area('Ngữ pháp dạng JSON', value='[]', height=90, key='new_grammar')
            if st.button('Lưu bài học mới'):
                try:
                    item={'id':lesson_id.strip() or 'lesson-'+str(len(lessons)+1),'title':lesson_title.strip() or 'Bài học mới','sentences':json.loads(sentence_json),'vocabulary':json.loads(vocab_json),'grammar':json.loads(grammar_json)}
                    folder['lessons'].append(item); save_data(data); st.success('Đã thêm bài học.'); st.rerun()
                except Exception as e: st.error(f'JSON chưa đúng định dạng: {e}')

    with st.expander('📥 Nhập dữ liệu JSON', expanded=False):
        uploaded=st.file_uploader('Chọn file JSON',type=['json'],key='json_import')
        mode=st.radio('Cách nhập',['Bổ sung thư mục/bài mới','Thay thế toàn bộ dữ liệu'],key='import_mode')
        if uploaded and st.button('Nhập JSON'):
            try:
                incoming=json.loads(uploaded.getvalue().decode('utf-8-sig'))
                if isinstance(incoming,list): incoming={'folders':[{'id':'imported','name':'Dữ liệu nhập','settings':{'speed':1.0,'repeat':2},'lessons':[legacy_lesson(x) for x in incoming]}]}
                elif 'folders' not in incoming and 'lessons' in incoming:
                    incoming={'folders':[{'id':'imported','name':'Dữ liệu nhập','settings':{'speed':1.0,'repeat':2},'lessons':[legacy_lesson(x) for x in incoming['lessons']]}]}
                if mode.startswith('Thay thế'):
                    data=incoming
                else:
                    by_name={f.get('name'):f for f in data['folders']}
                    for incf in incoming.get('folders',[]):
                        dest=by_name.get(incf.get('name'))
                        if not dest:
                            data['folders'].append(incf); by_name[incf.get('name')]=incf
                        else:
                            known={x.get('id') for x in dest.get('lessons',[])}
                            dest['lessons'].extend(x for x in incf.get('lessons',[]) if x.get('id') not in known)
                save_data(data); st.success('Đã nhập dữ liệu JSON.'); st.rerun()
            except Exception as e: st.error(f'Không nhập được JSON: {e}')

    st.download_button('⬇️ Tải bản sao lưu JSON',data=json.dumps(data,ensure_ascii=False,indent=2),file_name='trung_viet_lessons.json',mime='application/json')
    st.caption('Mỗi thư mục có cấu hình tốc độ và số lần lặp riêng. Mọi nút loa trong phần câu, từ vựng, ví dụ và ngữ pháp đều sử dụng cấu hình của thư mục đang mở. Có thể gắn MP3 riêng cho từng mục bằng trường audio trong JSON.')
