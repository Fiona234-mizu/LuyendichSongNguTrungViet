import json
import re
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
DATA_FILE = DATA_DIR / "lessons.json"
DATA_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Trung Việt Learning", page_icon="📚", layout="wide")

def empty_data():
    return {"lessons": [], "vocabulary": [], "grammar": []}

def load_data():
    if DATA_FILE.exists():
        try:
            obj = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
                return obj
        except Exception:
            pass
    return empty_data()

def save_data(obj):
    DATA_FILE.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def norm(s):
    return re.sub(r"\s+", "", s or "")

def compare_text(expected, actual):
    a, b = norm(expected), norm(actual)
    if not a:
        return 0, [], []
    # Character-level positional comparison; punctuation is retained intentionally.
    matches = [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x == y]
    wrong = []
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "∅"
        y = b[i] if i < len(b) else "∅"
        if x != y:
            wrong.append((i + 1, x, y))
    score = round(len(matches) / max(len(a), len(b), 1) * 100, 1)
    return score, matches, wrong

data = load_data()
lessons = data.get("lessons", [])
levels = ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"]

st.title("📚 中文学习 · Trung Việt Learning")
st.caption("Luyện dịch • Luyện gõ chữ Hán • Từ vựng • Ngữ pháp • Nghe MP3")

with st.sidebar:
    st.header("Điều hướng")
    page = st.radio("Chọn chức năng", ["Trang chủ", "Luyện dịch", "Luyện gõ Trung–Trung", "Từ vựng", "Ngữ pháp", "Quản lý JSON", "Quản lý MP3"])
    st.divider()
    st.caption("Phiên bản khởi đầu: lưu dữ liệu trong thư mục data/ trên máy chạy app.")

if page == "Trang chủ":
    st.subheader("Chọn trình độ")
    cols = st.columns(3)
    for i, level in enumerate(levels):
        count = sum(1 for x in lessons if x.get("level") == level)
        cols[i % 3].metric(level, f"{count} bài")
    st.info("Chọn mục ở thanh bên để học hoặc nhập dữ liệu. Có thể nhập JSON trước và tải MP3 sau.")
    if lessons:
        st.subheader("Bài học mới nhất")
        for lesson in lessons[-5:][::-1]:
            st.write(f"**{lesson.get('title', 'Chưa đặt tên')}** · {lesson.get('level','Chưa phân cấp')} · `{lesson.get('lesson_id','')}`")
    else:
        st.warning("Chưa có bài học. Vào “Quản lý JSON” để nhập file dữ liệu mẫu hoặc dữ liệu của bạn.")

elif page == "Luyện dịch":
    st.subheader("Luyện dịch Trung → Việt / Việt → Trung")
    level = st.selectbox("Trình độ", levels)
    subset = [x for x in lessons if x.get("level") == level]
    if not subset:
        st.info(f"Chưa có bài học ở {level}. Hãy nhập JSON trong mục Quản lý JSON.")
    else:
        lesson = st.selectbox("Bài học", subset, format_func=lambda x: f"{x.get('title','')} ({x.get('lesson_id','')})")
        direction = st.radio("Chiều dịch", ["Trung → Việt", "Việt → Trung"], horizontal=True)
        sentences = lesson.get("sentences", [])
        if sentences:
            for idx, sent in enumerate(sentences):
                source = sent.get("zh", "") if direction == "Trung → Việt" else sent.get("vi", "")
                target = sent.get("vi", "") if direction == "Trung → Việt" else sent.get("zh", "")
                st.markdown(f"**Câu {idx+1}**")
                st.write(source)
                if direction == "Trung → Việt" and sent.get("pinyin"):
                    st.caption(sent["pinyin"])
                audio_key = sent.get("audio_file") or lesson.get("audio_file")
                if audio_key and (AUDIO_DIR / Path(audio_key).name).exists():
                    st.audio(str(AUDIO_DIR / Path(audio_key).name))
                answer = st.text_area("Bản dịch của bạn", key=f"tr_{lesson.get('lesson_id')}_{idx}")
                if st.button("Hiện đáp án", key=f"ans_{lesson.get('lesson_id')}_{idx}"):
                    st.success(target or "Chưa có đáp án mẫu.")
        else:
            st.warning("Bài học chưa có câu. Kiểm tra trường sentences trong JSON.")

elif page == "Luyện gõ Trung–Trung":
    st.subheader("Luyện nghe/nhìn và gõ lại chữ Hán")
    level = st.selectbox("Trình độ", levels, key="type_level")
    subset = [x for x in lessons if x.get("level") == level]
    if subset:
        lesson = st.selectbox("Bài học", subset, format_func=lambda x: f"{x.get('title','')} ({x.get('lesson_id','')})", key="type_lesson")
        sentences = lesson.get("sentences", [])
        if sentences:
            idx = st.selectbox("Câu", range(len(sentences)), format_func=lambda i: f"Câu {i+1}")
            sent = sentences[idx]
            st.write("Hãy nghe MP3 (nếu có) hoặc nhìn câu mẫu rồi gõ lại:")
            audio_key = sent.get("audio_file") or lesson.get("audio_file")
            if audio_key and (AUDIO_DIR / Path(audio_key).name).exists():
                st.audio(str(AUDIO_DIR / Path(audio_key).name))
            if st.toggle("Hiện câu mẫu"):
                st.write(sent.get("zh", ""))
            typed = st.text_area("Gõ lại câu tiếng Trung", key="dictation_input")
            if st.button("Chấm kết quả"):
                score, matches, wrong = compare_text(sent.get("zh", ""), typed)
                st.metric("Độ khớp ký tự", f"{score}%")
                st.write("Câu chuẩn:", sent.get("zh", ""))
                st.write("Câu bạn gõ:", typed)
                st.write(f"Vị trí khớp: {matches if matches else 'Không có'}")
                if wrong:
                    st.write("Vị trí khác (vị trí, chuẩn, bạn gõ):")
                    st.write(wrong)
                else:
                    st.success("Các ký tự đều khớp.")
        else:
            st.info("Bài học chưa có câu.")
    else:
        st.info("Chưa có bài trong trình độ này.")

elif page == "Từ vựng":
    st.subheader("Từ vựng")
    vocab = data.get("vocabulary", [])
    if not vocab:
        st.info("Chưa có từ vựng. Hãy thêm mục vocabulary trong JSON.")
    for item in vocab:
        with st.expander(f"{item.get('hanzi','')} · {item.get('meaning_vi','')}"):
            st.write("Pinyin:", item.get("pinyin", ""))
            st.write("Từ loại:", item.get("word_type", ""))
            st.write("Bộ thủ:", item.get("radical", ""))
            st.write("Mẹo nhớ:", item.get("memory_tip", ""))
            for ex in item.get("examples", []):
                st.write(f"- {ex.get('zh','')} ({ex.get('pinyin','')}) — {ex.get('vi','')}")

elif page == "Ngữ pháp":
    st.subheader("Ngữ pháp")
    grammar = data.get("grammar", [])
    if not grammar:
        st.info("Chưa có ngữ pháp. Hãy thêm mục grammar trong JSON.")
    for item in grammar:
        with st.expander(f"{item.get('pattern','')} · {item.get('meaning_vi','')}"):
            st.write(item.get("explanation_vi", ""))
            for ex in item.get("examples", []):
                st.write(f"- {ex.get('zh','')} ({ex.get('pinyin','')}) — {ex.get('vi','')}")

elif page == "Quản lý JSON":
    st.subheader("Nhập / xuất dữ liệu JSON")
    uploaded = st.file_uploader("Chọn file JSON", type=["json"])
    mode = st.radio("Cách nhập", ["Gộp và cập nhật theo lesson_id", "Thay thế toàn bộ dữ liệu"])
    if uploaded and st.button("Nhập JSON"):
        try:
            incoming = json.loads(uploaded.getvalue().decode("utf-8"))
            if not isinstance(incoming, dict) or not isinstance(incoming.get("lessons", []), list):
                raise ValueError("JSON cần có cấu trúc object và trường lessons dạng danh sách.")
            if mode.startswith("Thay thế"):
                merged = incoming
            else:
                merged = data.copy()
                by_id = {x.get("lesson_id"): x for x in merged.get("lessons", [])}
                for item in incoming.get("lessons", []):
                    lid = item.get("lesson_id")
                    if not lid:
                        raise ValueError("Mỗi bài học phải có lesson_id.")
                    old = by_id.get(lid, {})
                    # Keep previously attached audio when incoming JSON omits it.
                    if old.get("audio_file") and not item.get("audio_file"):
                        item["audio_file"] = old["audio_file"]
                    by_id[lid] = {**old, **item}
                merged["lessons"] = list(by_id.values())
                for key in ("vocabulary", "grammar"):
                    if key in incoming:
                        merged[key] = incoming[key]
            save_data(merged)
            st.success("Đã nhập và lưu JSON vào data/lessons.json.")
            st.rerun()
        except Exception as e:
            st.error(f"Không nhập được JSON: {e}")
    st.download_button("Tải xuống JSON hiện tại", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="trung_viet_lessons_backup.json", mime="application/json")
    st.caption("Khi chọn gộp, bài cùng lesson_id được cập nhật; các bài cũ khác vẫn được giữ.")

elif page == "Quản lý MP3":
    st.subheader("Tải MP3 hàng loạt")
    st.write("Đặt tên file trùng với audio_id của câu hoặc lesson_id của bài. Ví dụ: `HSK1_B001_S001.mp3`.")
    st.caption("Nếu tên file trùng sentence_id/audio_id, app gắn vào câu; nếu trùng lesson_id, app gắn vào toàn bài.")
    files = st.file_uploader("Chọn một hoặc nhiều file MP3", type=["mp3"], accept_multiple_files=True)
    if files and st.button("Lưu và tự ghép MP3"):
        known_lessons = {x.get("lesson_id"): x for x in data.get("lessons", [])}
        sentence_map = {}
        for lesson in data.get("lessons", []):
            for sent in lesson.get("sentences", []):
                key = sent.get("audio_id") or sent.get("sentence_id")
                if key:
                    sentence_map[key] = sent
        attached, unmatched = [], []
        for f in files:
            stem = Path(f.name).stem
            safe_name = Path(f.name).name
            (AUDIO_DIR / safe_name).write_bytes(f.getvalue())
            if stem in sentence_map:
                sentence_map[stem]["audio_file"] = safe_name
                attached.append(f.name)
            elif stem in known_lessons:
                known_lessons[stem]["audio_file"] = safe_name
                attached.append(f.name)
            else:
                unmatched.append(f.name)
        save_data(data)
        st.success(f"Đã lưu {len(files)} file; ghép được {len(attached)} file.")
        if attached:
            st.write("Đã ghép:", attached)
        if unmatched:
            st.warning("Chưa tìm thấy mã tương ứng: " + ", ".join(unmatched))
    st.caption("MP3 được lưu trong data/audio/ trên máy chủ chạy Streamlit. Với Streamlit Cloud, cần nối kho lưu trữ bền vững như Supabase ở bước triển khai tiếp theo.")

st.divider()
st.caption("Trung Việt Learning · Bản nền có thể mở rộng kết nối Supabase ở bước tiếp theo.")
