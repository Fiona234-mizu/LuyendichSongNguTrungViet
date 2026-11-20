import streamlit as st
import json
from pathlib import Path
from difflib import SequenceMatcher

st.set_page_config(page_title="Trung Việt Learning", page_icon="📚", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "lessons.json"

DEFAULT_DATA = {
    "lessons": [
        {
            "id": "HSK1-001",
            "level": "HSK 1",
            "title": "Chào hỏi",
            "chinese": "你好！",
            "pinyin": "Nǐ hǎo!",
            "vietnamese": "Xin chào!",
            "audio": "",
            "vocabulary": [
                {"hanzi": "你", "pinyin": "nǐ", "meaning": "bạn"},
                {"hanzi": "好", "pinyin": "hǎo", "meaning": "tốt; khỏe"}
            ],
            "grammar": ["你好 là cách chào hỏi thông dụng."]
        },
        {
            "id": "HSK1-002",
            "level": "HSK 1",
            "title": "Cảm ơn",
            "chinese": "谢谢你。",
            "pinyin": "Xièxie nǐ.",
            "vietnamese": "Cảm ơn bạn.",
            "audio": "",
            "vocabulary": [
                {"hanzi": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn"},
                {"hanzi": "你", "pinyin": "nǐ", "meaning": "bạn"}
            ],
            "grammar": ["谢谢 dùng để nói lời cảm ơn."]
        }
    ]
}

if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps(DEFAULT_DATA, ensure_ascii=False, indent=2), encoding="utf-8")

def load_data():
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {"lessons": data}
        data.setdefault("lessons", [])
        return data
    except Exception:
        return {"lessons": []}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

data = load_data()
lessons = data.get("lessons", [])

st.title("📚 Trung Việt Learning")
st.caption("Ứng dụng luyện tiếng Trung – tiếng Việt | Bản khởi đầu")

with st.sidebar:
    st.header("Thiết lập học tập")
    levels = ["Tất cả"] + [f"HSK {i}" for i in range(1, 7)]
    selected_level = st.selectbox("Chọn cấp độ", levels)
    if selected_level != "Tất cả":
        filtered = [x for x in lessons if x.get("level") == selected_level]
    else:
        filtered = lessons
    st.metric("Số bài học", len(filtered))
    st.divider()
    st.caption("Dữ liệu được lưu trong thư mục data/lessons.json")

tabs = st.tabs(["Trung → Việt", "Việt → Trung", "Trung → Trung", "Từ vựng & ngữ pháp", "Quản lý JSON"])

def choose_lesson(items, key):
    if not items:
        st.info("Chưa có bài học ở cấp độ này. Bạn có thể nhập JSON ở mục Quản lý JSON.")
        return None
    labels = [f"{x.get('id','')} — {x.get('title','')}" for x in items]
    idx = st.selectbox("Chọn bài học", range(len(items)), format_func=lambda i: labels[i], key=key)
    return items[idx]

with tabs[0]:
    st.subheader("Luyện dịch Trung → Việt")
    lesson = choose_lesson(filtered, "cv_lesson")
    if lesson:
        st.markdown(f"**{lesson.get('level','')} · {lesson.get('title','')}**")
        st.markdown(f"<div style='font-size:32px;font-weight:600'>{lesson.get('chinese','')}</div>", unsafe_allow_html=True)
        st.write("Pinyin:", lesson.get("pinyin", ""))
        if lesson.get("audio"):
            st.audio(lesson["audio"])
        answer = st.text_area("Nhập bản dịch tiếng Việt", key=f"cv_answer_{lesson.get('id')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Hiện đáp án", key="cv_show"):
                st.success(lesson.get("vietnamese", "Chưa có đáp án"))
        with c2:
            if st.button("Xóa câu trả lời", key="cv_clear"):
                st.rerun()

with tabs[1]:
    st.subheader("Luyện dịch Việt → Trung")
    lesson = choose_lesson(filtered, "vc_lesson")
    if lesson:
        st.markdown(f"**{lesson.get('level','')} · {lesson.get('title','')}**")
        st.markdown(f"<div style='font-size:24px'>{lesson.get('vietnamese','')}</div>", unsafe_allow_html=True)
        answer = st.text_input("Nhập câu tiếng Trung", key=f"vc_answer_{lesson.get('id')}")
        if st.button("Đối chiếu đáp án", key="vc_check"):
            target = lesson.get("chinese", "")
            ratio = SequenceMatcher(None, answer.strip(), target.strip()).ratio() if answer.strip() else 0
            st.write("Đáp án:", target)
            st.write("Pinyin:", lesson.get("pinyin", ""))
            st.metric("Độ giống ký tự", f"{ratio*100:.0f}%")
            if answer.strip() == target.strip():
                st.success("Chính xác!")
            else:
                st.info("Hãy so sánh với đáp án và thử lại nhé.")

with tabs[2]:
    st.subheader("Luyện gõ Trung → Trung")
    lesson = choose_lesson(filtered, "cc_lesson")
    if lesson:
        st.write("Hãy nhìn câu mẫu rồi gõ lại chính xác.")
        st.markdown(f"<div style='font-size:30px;font-weight:600'>{lesson.get('chinese','')}</div>", unsafe_allow_html=True)
        typed = st.text_input("Gõ lại câu tiếng Trung", key=f"cc_answer_{lesson.get('id')}")
        if st.button("Kiểm tra từng ký tự", key="cc_check"):
            target = lesson.get("chinese", "")
            if typed == target:
                st.success("Rất tốt! Bạn đã gõ chính xác.")
            else:
                st.warning(f"Đáp án đúng: {target}")
                st.write(f"Độ chính xác tổng thể: {SequenceMatcher(None, typed, target).ratio()*100:.0f}%")
                st.write("Bạn hãy chú ý các ký tự khác nhau rồi gõ lại.")

with tabs[3]:
    st.subheader("Từ vựng & ngữ pháp")
    lesson = choose_lesson(filtered, "vg_lesson")
    if lesson:
        st.markdown(f"**{lesson.get('level','')} · {lesson.get('title','')}**")
        vocab = lesson.get("vocabulary", [])
        if vocab:
            for item in vocab:
                st.markdown(f"- **{item.get('hanzi','')}** ({item.get('pinyin','')}) — {item.get('meaning','')}")
        else:
            st.info("Bài này chưa có dữ liệu từ vựng.")
        st.markdown("**Ngữ pháp / ghi chú**")
        grammar = lesson.get("grammar", [])
        if grammar:
            for item in grammar:
                st.markdown(f"- {item}")
        else:
            st.info("Bài này chưa có ghi chú ngữ pháp.")

with tabs[4]:
    st.subheader("Nhập và cập nhật dữ liệu JSON")
    st.write("Định dạng dữ liệu gồm một đối tượng có khóa `lessons`, hoặc một danh sách bài học.")
    uploaded = st.file_uploader("Chọn file JSON", type=["json"])
    mode = st.radio("Cách cập nhật", ["Bổ sung bài mới (không ghi đè ID cũ)", "Thay thế toàn bộ dữ liệu"], index=0)
    if uploaded is not None:
        try:
            incoming = json.loads(uploaded.getvalue().decode("utf-8-sig"))
            incoming_lessons = incoming if isinstance(incoming, list) else incoming.get("lessons", [])
            if st.button("Nhập dữ liệu JSON"):
                if mode.startswith("Thay thế"):
                    data["lessons"] = incoming_lessons
                else:
                    existing = {x.get("id"): x for x in lessons}
                    for item in incoming_lessons:
                        item_id = item.get("id")
                        if item_id and item_id not in existing:
                            data["lessons"].append(item)
                        elif not item_id:
                            data["lessons"].append(item)
                save_data(data)
                st.success(f"Đã nhập dữ liệu. Hiện có {len(data['lessons'])} bài học.")
                st.rerun()
        except Exception as e:
            st.error(f"Không đọc được JSON: {e}")
    st.download_button("Tải dữ liệu JSON hiện tại", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="lessons_backup.json", mime="application/json")
    st.divider()
    st.caption("Mẫu cấu trúc một bài học:")
    st.code(json.dumps(DEFAULT_DATA["lessons"][0], ensure_ascii=False, indent=2), language="json")

st.divider()
st.caption("Bản MVP: MP3 có thể phát khi có đường dẫn/URL trong trường audio. Tích hợp lưu trữ Supabase sẽ được bổ sung ở phiên bản tiếp theo.")
