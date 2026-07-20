import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SACA Smart Assistant",
    page_icon="✈️",
    layout="centered",
)

DATA_FILE = Path(__file__).with_name("locations.json")
ASSETS_DIR = Path(__file__).with_name("assets")
FLOOR_MAPS = {
    "GF": ASSETS_DIR / "gf_plan.jpg",
    "FF": ASSETS_DIR / "ff_plan.jpg",
}

# The assumed starting point changes with the displayed floor:
# - Ground floor: Reception.
# - First floor: The elevator reached from Reception.
CURRENT_POSITION = {
    "GF": {"x": 0.495, "y": 0.225},
    "FF": {"x": 0.595, "y": 0.255},
}


@st.cache_data
def load_locations():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)




@st.cache_data
def image_to_base64(path: Path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


locations = load_locations()

TEXT = {
    "العربية": {
        "title": "✈️ مساعد الأكاديمية السعودية للطيران المدني",
        "subtitle": "اختر وجهتك خطوة بخطوة.",
        "language": "اختر اللغة",
        "main_category": "اختر القسم الرئيسي",
        "sub_category": "اختر القسم الفرعي",
        "destination": "اختر المكان",
        "choose_main": "اختر قسمًا رئيسيًا",
        "choose_sub": "اختر قسمًا فرعيًا",
        "choose_destination": "اختر المكان",
        "next": "التالي",
        "back": "رجوع",
        "start_over": "البدء من جديد",
        "details": "بيانات الموقع",
        "name": "الاسم",
        "floor": "الدور",
        "room": "رقم الغرفة",
        "area": "المنطقة",
        "directions": "طريقة الوصول",
        "coordinates": "موقع الوجهة على الخريطة",
        "no_room": "لا يوجد رقم غرفة",
        "listen": "🔊 استمع للرد",
        "playing": "جارٍ تشغيل الرد...",
        "stopped": "تم إيقاف الصوت",
        "voice_error": "تعذر تشغيل الصوت. تأكد من رفع صوت الجهاز وجرب متصفح Chrome أو Edge.",
        "answer_intro": "المكان الذي اخترته هو",
        "room_phrase": "رقم الغرفة",
        "route_phrase": "طريقة الوصول",
        "note": "البيانات المستخدمة حقيقية من مخططات الدور الأرضي والأول.",
        "step_language": "1. اللغة",
        "step_main": "2. القسم الرئيسي",
        "step_sub": "3. القسم الفرعي",
        "step_destination": "4. المكان",
    },
    "English": {
        "title": "✈️ SACA Smart Assistant",
        "subtitle": "Choose your destination step by step.",
        "language": "Choose language",
        "main_category": "Choose main category",
        "sub_category": "Choose subcategory",
        "destination": "Choose destination",
        "choose_main": "Choose a main category",
        "choose_sub": "Choose a subcategory",
        "choose_destination": "Choose a destination",
        "next": "Next",
        "back": "Back",
        "start_over": "Start over",
        "details": "Location Details",
        "name": "Name",
        "floor": "Floor",
        "room": "Room",
        "area": "Area",
        "directions": "Directions",
        "coordinates": "Destination on the map",
        "no_room": "No room number",
        "listen": "🔊 Listen to the answer",
        "playing": "Playing response...",
        "stopped": "Audio stopped",
        "voice_error": "Audio could not be played. Check your device volume and try Chrome or Edge.",
        "answer_intro": "Your selected destination is",
        "room_phrase": "Room",
        "route_phrase": "Directions",
        "note": "The data is based on the real ground- and first-floor plans.",
        "step_language": "1. Language",
        "step_main": "2. Main category",
        "step_sub": "3. Subcategory",
        "step_destination": "4. Destination",
    },
}

AREA_AR_TO_EN = {
    "الشمال": "North",
    "الجنوب": "South",
    "الشرق": "East",
    "الغرب": "West",
    "الشمال الأوسط": "North Central",
    "الجنوب الأوسط": "South Central",
    "الشرق الأوسط": "East Central",
    "الغرب الأوسط": "West Central",
    "الشمال الشرقي": "Northeast",
    "الشمال الغربي": "Northwest",
    "الجنوب الشرقي": "Southeast",
    "الجنوب الغربي": "Southwest",
    "الشمال الشرقي الأوسط": "Northeast Central",
    "الشمال الغربي الأوسط": "Northwest Central",
    "الجنوب الشرقي الأوسط": "Southeast Central",
    "الجنوب الغربي الأوسط": "Southwest Central",
    "الجنوب الأوسط الغربي": "South-Central West",
    "الشمال الأوسط الشرقي": "North-Central East",
}


def reset_after(step_name):
    order = ["language_done", "main_done", "sub_done", "destination_done"]
    start = order.index(step_name)
    for key in order[start + 1:]:
        st.session_state[key] = False
    for key in ["selected_main", "selected_sub", "selected_destination"]:
        if key in st.session_state:
            del st.session_state[key]


def full_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def speak_button(text, language_code, label, playing_text, error_text):
    safe_text = json.dumps(text, ensure_ascii=False)
    safe_label = json.dumps(label, ensure_ascii=False)
    safe_playing = json.dumps(playing_text, ensure_ascii=False)
    safe_error = json.dumps(error_text, ensure_ascii=False)

    components.html(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; gap:8px;">
            <button id="speakBtn" onclick="speakText()" style="
                background:#0f766e;
                color:white;
                border:none;
                border-radius:10px;
                padding:12px 22px;
                font-size:16px;
                cursor:pointer;
                font-family:Arial;">
            </button>
            <div id="voiceStatus" style="
                min-height:20px;
                font-family:Arial;
                font-size:13px;
                color:#6b7280;">
            </div>
        </div>

        <script>
        const button = document.getElementById("speakBtn");
        const status = document.getElementById("voiceStatus");
        button.textContent = {safe_label};

        function findVoice(langCode) {{
            const voices = window.speechSynthesis.getVoices();
            const exact = voices.find(v => v.lang.toLowerCase() === langCode.toLowerCase());
            if (exact) return exact;

            const languagePrefix = langCode.split("-")[0].toLowerCase();
            return voices.find(v => v.lang.toLowerCase().startsWith(languagePrefix)) || null;
        }}

        function speakText() {{
            try {{
                window.speechSynthesis.cancel();

                const utterance = new SpeechSynthesisUtterance({safe_text});
                utterance.lang = "{language_code}";
                utterance.rate = 0.92;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;

                const voice = findVoice("{language_code}");
                if (voice) {{
                    utterance.voice = voice;
                }}

                utterance.onstart = () => {{
                    status.textContent = {safe_playing};
                    button.disabled = true;
                    button.style.opacity = "0.75";
                }};

                utterance.onend = () => {{
                    status.textContent = "";
                    button.disabled = false;
                    button.style.opacity = "1";
                }};

                utterance.onerror = () => {{
                    status.textContent = {safe_error};
                    button.disabled = false;
                    button.style.opacity = "1";
                }};

                window.speechSynthesis.speak(utterance);
            }} catch (error) {{
                status.textContent = {safe_error};
                button.disabled = false;
                button.style.opacity = "1";
            }}
        }}

        window.speechSynthesis.onvoiceschanged = () => {{
            window.speechSynthesis.getVoices();
        }};
        window.speechSynthesis.getVoices();
        </script>
        """,
        height=90,
    )


if "language_done" not in st.session_state:
    st.session_state.language_done = False
if "main_done" not in st.session_state:
    st.session_state.main_done = False
if "sub_done" not in st.session_state:
    st.session_state.sub_done = False
if "destination_done" not in st.session_state:
    st.session_state.destination_done = False

language = st.selectbox(
    "Language / اللغة",
    ["العربية", "English"],
    index=None,
    placeholder="اختر اللغة / Choose language",
    key="language_selector",
)

# Reset the navigation flow whenever the language changes.
# Stored category/destination names are language-specific, so keeping the old
# values would cause a StopIteration error after switching languages.
previous_language = st.session_state.get("_active_language")
if language and previous_language and language != previous_language:
    for key in [
        "language_done",
        "main_done",
        "sub_done",
        "destination_done",
        "selected_main",
        "selected_sub",
        "selected_destination",
        "main_selector",
        "sub_selector",
        "destination_selector",
    ]:
        st.session_state.pop(key, None)

    st.session_state["language_done"] = False
    st.session_state["main_done"] = False
    st.session_state["sub_done"] = False
    st.session_state["destination_done"] = False
    st.session_state["_active_language"] = language
    st.rerun()

if language:
    st.session_state["_active_language"] = language

if not language:
    st.title("✈️ SACA Smart Assistant")
    st.info("اختر اللغة للبدء / Choose a language to begin")
    st.stop()

t = TEXT[language]
is_ar = language == "العربية"

if is_ar:
    st.markdown(
        """
        <style>
        .stApp, .stMarkdown, .stAlert, p, h1, h2, h3 {
            direction: rtl;
            text-align: right;
        }
        div[data-baseweb="select"] > div {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title(t["title"])
st.caption(t["subtitle"])

category_key = "category_ar" if is_ar else "category_en"
subcategory_key = "subcategory_ar" if is_ar else "subcategory_en"
name_key = "name_ar" if is_ar else "name_en"
floor_key = "floor_ar" if is_ar else "floor_en"
directions_key = "directions_ar" if is_ar else "directions_en"

if not st.session_state.main_done:
    st.subheader(t["step_main"])
    categories = sorted(
        {item[category_key] for item in locations},
        key=lambda value: value.casefold(),
    )
    selected_main = st.selectbox(
        t["main_category"],
        categories,
        index=None,
        placeholder=t["choose_main"],
        key="main_selector",
    )
    if st.button(t["next"], use_container_width=True, disabled=not selected_main):
        st.session_state.selected_main = selected_main
        st.session_state.main_done = True
        st.rerun()
    st.stop()

if not st.session_state.sub_done:
    st.subheader(t["step_sub"])
    selected_main = st.session_state.selected_main
    category_items = [
        item for item in locations
        if item[category_key] == selected_main
    ]
    subcategories = sorted(
        {item[subcategory_key] for item in category_items},
        key=lambda value: value.casefold(),
    )
    selected_sub = st.selectbox(
        t["sub_category"],
        subcategories,
        index=None,
        placeholder=t["choose_sub"],
        key="sub_selector",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["back"], use_container_width=True):
            st.session_state.main_done = False
            if "selected_main" in st.session_state:
                del st.session_state.selected_main
            st.rerun()
    with col2:
        if st.button(t["next"], use_container_width=True, disabled=not selected_sub):
            st.session_state.selected_sub = selected_sub
            st.session_state.sub_done = True
            st.rerun()
    st.stop()

if not st.session_state.destination_done:
    st.subheader(t["step_destination"])
    selected_main = st.session_state.selected_main
    selected_sub = st.session_state.selected_sub

    destination_items = [
        item for item in locations
        if item[category_key] == selected_main
        and item[subcategory_key] == selected_sub
    ]

    destination_names = sorted(
        [item[name_key] for item in destination_items],
        key=lambda value: value.casefold(),
    )

    selected_destination = st.selectbox(
        t["destination"],
        destination_names,
        index=None,
        placeholder=t["choose_destination"],
        key="destination_selector",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["back"], use_container_width=True):
            st.session_state.sub_done = False
            if "selected_sub" in st.session_state:
                del st.session_state.selected_sub
            st.rerun()
    with col2:
        if st.button(t["next"], use_container_width=True, disabled=not selected_destination):
            st.session_state.selected_destination = selected_destination
            st.session_state.destination_done = True
            st.rerun()
    st.stop()

selected_item = next(
    item for item in locations
    if item[category_key] == st.session_state.selected_main
    and item[subcategory_key] == st.session_state.selected_sub
    and item[name_key] == st.session_state.selected_destination
)

st.subheader(t["details"])

name_value = selected_item[name_key]
floor_value = selected_item[floor_key]
room_value = selected_item["room"] or t["no_room"]
area_value = (
    selected_item["area_ar"]
    if is_ar
    else AREA_AR_TO_EN.get(selected_item["area_ar"], "Not specified")
)

st.success(f"**{t['name']}:** {name_value}")
st.write(f"**{t['floor']}:** {floor_value}")
st.write(f"**{t['room']}:** {room_value}")
st.write(f"**{t['area']}:** {area_value}")

st.subheader(t["directions"])
st.info(selected_item[directions_key])

if is_ar:
    spoken_answer = (
        f"{t['answer_intro']} {name_value}. "
        f"يوجد في {floor_value}. "
        f"{t['room_phrase']}: {room_value}. "
        f"{t['route_phrase']}: {selected_item[directions_key]}"
    )
    speech_language = "ar-SA"
else:
    spoken_answer = (
        f"{t['answer_intro']} {name_value}. "
        f"It is on the {floor_value}. "
        f"{t['room_phrase']}: {room_value}. "
        f"{t['route_phrase']}: {selected_item[directions_key]}"
    )
    speech_language = "en-US"

speak_button(
    spoken_answer,
    speech_language,
    t["listen"],
    t["playing"],
    t["voice_error"],
)

# The coordinates in locations.json are normalized to the usable building area,
# not to the full exported drawing image (which still contains a small border).
# Convert building-relative coordinates to full-image coordinates before drawing.
raw_x = float(selected_item["x"] or 0.5)
raw_y = float(selected_item["y"] or 0.5)

floor_code = selected_item.get("floor_code", "GF")
map_path = FLOOR_MAPS.get(floor_code)

# Bounds of the actual building inside each cropped map image:
# (left, top, right, bottom), expressed as fractions of the image size.
BUILDING_BOUNDS = {
    "GF": (0.065, 0.095, 0.935, 0.905),
    "FF": (0.065, 0.095, 0.935, 0.905),
}
left, top, right, bottom = BUILDING_BOUNDS.get(
    floor_code, (0.0, 0.0, 1.0, 1.0)
)
x = left + raw_x * (right - left)
y = top + raw_y * (bottom - top)

current_position = CURRENT_POSITION.get(floor_code, {"x": 0.5, "y": 0.5})
current_x = left + current_position["x"] * (right - left)
current_y = top + current_position["y"] * (bottom - top)
current_label = "أنت هنا" if is_ar else "You're here"
destination_label = "الوجهة" if is_ar else "Destination"

st.subheader(t["coordinates"])

if map_path and map_path.exists():
    map_b64 = image_to_base64(map_path)
    map_html = f"""
    <div style="
        position:relative;
        width:100%;
        border:2px solid #d1d5db;
        border-radius:14px;
        overflow:hidden;
        background:white;
        line-height:0;">
        <img src="data:image/jpeg;base64,{map_b64}" style="
            display:block;
            width:100%;
            height:auto;
            object-fit:contain;">
        <div title="{destination_label}" style="
            position:absolute;
            left:calc({x * 100}% - 9px);
            top:calc({y * 100}% - 9px);
            width:18px;
            height:18px;
            border-radius:50%;
            background:#e11d48;
            border:3px solid white;
            box-shadow:0 0 0 4px rgba(225,29,72,.28), 0 2px 8px rgba(0,0,0,.55);
            line-height:1;
            z-index:3;">
        </div>

        <div title="{current_label}" style="
            position:absolute;
            left:calc({current_x * 100}% - 15px);
            top:calc({current_y * 100}% - 16px);
            width:30px;
            height:32px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:27px;
            line-height:1;
            filter:drop-shadow(0 2px 3px rgba(0,0,0,.7));
            z-index:5;">⭐️
        </div>
        <div style="
            position:absolute;
            left:calc({current_x * 100}% + 13px);
            top:calc({current_y * 100}% - 14px);
            background:rgba(15,118,110,.94);
            color:white;
            border:2px solid white;
            border-radius:8px;
            padding:4px 8px;
            font:700 12px Arial,sans-serif;
            line-height:1.2;
            white-space:nowrap;
            box-shadow:0 2px 7px rgba(0,0,0,.35);
            z-index:4;">{current_label}
        </div>
    </div>
    <div style="
        display:flex;
        gap:18px;
        flex-wrap:wrap;
        align-items:center;
        padding:10px 4px 0;
        font:14px Arial,sans-serif;
        line-height:1.4;">
        <span>⭐️ {current_label}</span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#e11d48;margin-inline-end:5px;"></span>{destination_label}</span>
    </div>
    """
    components.html(map_html, height=500, scrolling=False)
else:
    st.error("تعذر العثور على صورة الخريطة لهذا الدور." if is_ar else "The map image for this floor could not be found.")

col1, col2 = st.columns(2)
with col1:
    if st.button(t["back"], use_container_width=True):
        st.session_state.destination_done = False
        if "selected_destination" in st.session_state:
            del st.session_state.selected_destination
        st.rerun()
with col2:
    if st.button(t["start_over"], use_container_width=True):
        full_reset()

st.caption(t["note"])
