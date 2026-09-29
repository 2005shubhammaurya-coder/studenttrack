"""
StudentTrack - Student Performance Analytics
v3: Role-based access (Teacher/Student), data entry, polished UI
Run with: py -m streamlit run dashboard_v3.py
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

st.set_page_config(page_title="StudentTrack", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    #MainMenu, footer, header { visibility: hidden; }
    .metric-card { background:#1a1d27; border-radius:12px; padding:20px; border:1px solid #2a2d3a; text-align:center; }
    .metric-value { font-size:32px; font-weight:700; color:#ffffff; margin:0; }
    .metric-label { font-size:12px; color:#8b8fa8; margin:0; text-transform:uppercase; letter-spacing:1px; }
    .profile-card { background:linear-gradient(135deg,#1a1d27 0%,#1e2235 100%); border-radius:16px; padding:24px; border:1px solid #2a2d3a; margin-bottom:24px; }
    .student-name { font-size:28px; font-weight:700; color:#fff; margin:0; }
    .student-sub { font-size:14px; color:#8b8fa8; margin:4px 0 0 0; }
    .section-header { font-size:18px; font-weight:600; color:#ffffff; margin-bottom:2px; }
    .section-sub { font-size:12px; color:#8b8fa8; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px; }
    .badge-school { background:#2a2d3a; color:#c8c9d4; padding:3px 10px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; }
    .badge-district { background:#1a3a2a; color:#4ade80; padding:3px 10px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; }
    .badge-state { background:#3a2a1a; color:#fb923c; padding:3px 10px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; }
    .badge-national { background:#2a1a3a; color:#a78bfa; padding:3px 10px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; }
    .trend-rising { background:#14532d; color:#4ade80; padding:2px 10px; border-radius:20px; font-size:12px; }
    .trend-declining { background:#450a0a; color:#f87171; padding:2px 10px; border-radius:20px; font-size:12px; }
    .trend-stable { background:#1e3a5f; color:#60a5fa; padding:2px 10px; border-radius:20px; font-size:12px; }
    .suggest-card { background:#1a1d27; border:1px solid #2a2d3a; border-radius:10px; padding:12px 16px; margin:4px 0; font-size:14px; color:#e2e8f0; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "students_data.csv"
LEVEL_WEIGHT = {"School":1,"District":2,"State":3,"National":4}
DOMAIN_CAREERS = {
    "STEM":       ["Engineering (IIT/NIT)","Data Science & AI","Research & Academia","Medicine (NEET)","Architecture"],
    "Arts":       ["Design (UX/Graphic/Product)","Fine Arts & Animation","Journalism & Media","Performing Arts","Fashion Design"],
    "Leadership": ["Business & Management (MBA)","Civil Services (IAS/IPS)","Law (CLAT)","Entrepreneurship","Public Policy"],
    "Sports":     ["Professional Sports","Sports Management","Physical Education & Coaching","Sports Journalism"],
    "Social Work":["NGO & Development Sector","Psychology & Counselling","Public Policy","Social Entrepreneurship"],
}

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["student_id","name","grade","year","subject","score","attendance","activity","activity_category","activity_level"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.cache_data.clear()

def get_badge(level):
    l = str(level).lower()
    if "national" in l: return "badge-national"
    if "state" in l: return "badge-state"
    if "district" in l: return "badge-district"
    return "badge-school"

def render_charts(student_df, selected_name):
    left, right = st.columns(2)
    colors = ["#3b82f6","#10b981","#f59e0b","#ec4899","#8b5cf6","#14b8a6"]
    with left:
        st.markdown("<p class='section-header'>Subject Performance Trend</p><p class='section-sub'>Scores across grades</p>", unsafe_allow_html=True)
        pivot = student_df.pivot_table(index="grade", columns="subject", values="score", aggfunc="mean")
        fig = go.Figure()
        for i, subj in enumerate(pivot.columns):
            fig.add_trace(go.Scatter(x=[f"Gr {int(g)}" for g in pivot.index], y=pivot[subj], mode="lines+markers", name=subj, line=dict(color=colors[i%len(colors)],width=2), marker=dict(size=7)))
        fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b8fa8"), margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h",y=-0.25,font=dict(size=11)), xaxis=dict(gridcolor="#2a2d3a"), yaxis=dict(gridcolor="#2a2d3a"))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("<p class='section-header'>Domain Balance</p><p class='section-sub'>Strengths across five dimensions</p>", unsafe_allow_html=True)
        stem = student_df[student_df["subject"].isin(["Math","Science"])]["score"].mean()
        adf = student_df.dropna(subset=["activity_category"])
        ds = {"STEM": stem if not pd.isna(stem) else 0}
        for cat in ["Arts","Leadership","Sports","Social Work"]:
            rows = adf[adf["activity_category"]==cat]
            ds[cat] = min(100, rows["activity_level"].map(LEVEL_WEIGHT).sum()*8) if len(rows)>0 else 0
        cats = list(ds.keys()); vals = list(ds.values())
        fig2 = go.Figure()
        fig2.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself", fillcolor="rgba(59,130,246,0.15)", line=dict(color="#3b82f6",width=2)))
        fig2.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b8fa8"), margin=dict(l=0,r=0,t=10,b=0), polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True,range=[0,100],gridcolor="#2a2d3a",tickfont=dict(size=9)), angularaxis=dict(gridcolor="#2a2d3a")))
        st.plotly_chart(fig2, use_container_width=True)
    return ds

def render_strengths(student_df):
    st.markdown("<p class='section-header'>Strengths & Areas to Watch</p>", unsafe_allow_html=True)
    rows = []
    for subj in student_df["subject"].dropna().unique():
        s = student_df[student_df["subject"]==subj].sort_values("grade")
        if len(s)>=2:
            ch = s["score"].iloc[-1]-s["score"].iloc[0]
            status = "Rising" if ch>5 else "Declining" if ch<-5 else "Stable"
            badge = "trend-rising" if status=="Rising" else "trend-declining" if status=="Declining" else "trend-stable"
            rows.append({"Subject":subj,"First":s["score"].iloc[0],"Latest":s["score"].iloc[-1],"Status":status,"Badge":badge})
    cols = st.columns([3,1,1,1])
    cols[0].markdown("**Subject**"); cols[1].markdown("**First**"); cols[2].markdown("**Latest**"); cols[3].markdown("**Trend**")
    st.markdown("<hr style='margin:4px 0;border-color:#2a2d3a;'>", unsafe_allow_html=True)
    for r in rows:
        c1,c2,c3,c4 = st.columns([3,1,1,1])
        c1.markdown(f"<p style='color:#e2e8f0;margin:4px 0;'>{r['Subject']}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='color:#8b8fa8;margin:4px 0;'>{r['First']}</p>", unsafe_allow_html=True)
        c3.markdown(f"<p style='color:#fff;font-weight:600;margin:4px 0;'>{r['Latest']}</p>", unsafe_allow_html=True)
        c4.markdown(f"<span class='{r['Badge']}'>{r['Status']}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:4px 0;border-color:#2a2d3a;'>", unsafe_allow_html=True)

def render_history(student_df):
    st.markdown("<br><p class='section-header'>Year-by-Year History</p>", unsafe_allow_html=True)
    with st.expander("📚 Academics"):
        acad = student_df[["grade","subject","score"]].dropna().sort_values("grade")
        for g in sorted(acad["grade"].unique()):
            gdf = acad[acad["grade"]==g]
            parts = " &nbsp; ".join([f"<b style='color:#fff;'>{r.subject}</b> <span style='color:#3b82f6;'>{r.score}</span>" for _,r in gdf.iterrows()])
            st.markdown(f"<p style='margin:6px 0;'><span style='color:#8b8fa8;'>Grade {int(g)}</span> &nbsp;→&nbsp; {parts} &nbsp; <span style='color:#10b981;'>Avg {gdf['score'].mean():.1f}%</span></p>", unsafe_allow_html=True)
    with st.expander("📅 Attendance"):
        att = student_df[["grade","attendance"]].drop_duplicates("grade").sort_values("grade")
        acols = st.columns(max(1,len(att)))
        for i,(_,r) in enumerate(att.iterrows()):
            acols[i].markdown(f"<div class='metric-card'><p class='metric-label'>Grade {int(r.grade)}</p><p class='metric-value' style='font-size:22px;color:#10b981;'>{r.attendance:.0f}%</p></div>", unsafe_allow_html=True)
    with st.expander("🏆 Activities & Achievements"):
        acts = student_df.dropna(subset=["activity"])[["grade","activity","activity_category","activity_level"]].drop_duplicates()
        if len(acts)==0:
            st.info("No activities recorded yet.")
        for g in sorted(acts["grade"].unique()):
            gacts = acts[acts["grade"]==g]
            badges = " ".join([f"<span class='{get_badge(r.activity_level)}'>{r.activity} · {r.activity_level}</span>" for _,r in gacts.iterrows()])
            st.markdown(f"<p style='margin:8px 0;'><span style='color:#8b8fa8;'>Grade {int(g)}</span> &nbsp; {badges}</p>", unsafe_allow_html=True)

def render_suggestions(domain_scores):
    st.markdown("<br><p class='section-header'>Suggested Directions</p><p class='section-sub'>Based on your top domains</p>", unsafe_allow_html=True)
    top = [d for d,s in sorted(domain_scores.items(),key=lambda x:x[1],reverse=True) if s>0][:2]
    if top:
        st.markdown(f"<p style='color:#8b8fa8;font-size:13px;'>Strongest areas: <b style='color:#fff;'>{' and '.join(top)}</b></p>", unsafe_allow_html=True)
        paths=[]; seen=set()
        for d in top: paths.extend(DOMAIN_CAREERS.get(d,[]))
        paths=[p for p in paths if not (p in seen or seen.add(p))]
        cols=st.columns(4)
        for i,p in enumerate(paths[:8]):
            with cols[i%4]: st.markdown(f"<div class='suggest-card'>✦ {p}</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='color:#4b5563;font-size:11px;'>Prediction based on performance data, not official advice. Verify with official exam authorities before decisions.</p>", unsafe_allow_html=True)

# ---------- Session state ----------
if "role" not in st.session_state:
    st.session_state.role = None

# ---------- Header ----------
c1,c2 = st.columns([4,1])
with c1:
    st.markdown("## 🎓 StudentTrack")
    st.markdown('<p style="color:#8b8fa8;font-size:13px;margin-top:-12px;">Student Performance Analytics</p>', unsafe_allow_html=True)
with c2:
    if st.session_state.role:
        label = "👨‍🏫 Teacher" if st.session_state.role=="teacher" else "🎒 Student"
        st.markdown(f"<p style='color:#8b8fa8;font-size:13px;text-align:right;margin-top:8px;'>{label}</p>", unsafe_allow_html=True)
        if st.button("Switch role", use_container_width=True):
            st.session_state.role = None
            st.rerun()

# ---------- Login ----------
if st.session_state.role is None:
    st.markdown("---")
    _,mid,_ = st.columns([1,2,1])
    with mid:
        st.markdown("""
        <div style='background:#1a1d27;border-radius:16px;padding:40px;border:1px solid #2a2d3a;text-align:center;'>
            <div style='font-size:48px;'>🎓</div>
            <h2 style='color:white;margin:8px 0;'>Welcome to StudentTrack</h2>
            <p style='color:#8b8fa8;font-size:14px;margin-bottom:24px;'>Select your role to continue</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        r1,r2 = st.columns(2)
        with r1:
            if st.button("👨‍🏫 Teacher / Admin", use_container_width=True, type="primary"):
                st.session_state.role = "teacher"; st.rerun()
        with r2:
            if st.button("🎒 Student", use_container_width=True):
                st.session_state.role = "student"; st.rerun()
    st.stop()

st.markdown("---")
df = load_data()
student_names = df[["student_id","name"]].drop_duplicates() if len(df)>0 else pd.DataFrame(columns=["student_id","name"])

# ================================================================
# TEACHER VIEW
# ================================================================
if st.session_state.role == "teacher":
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Student", "➕ Add Year Record", "🏃 Add Activity", "🗑️ Delete Records"])

    with tab1:
        if len(student_names)==0:
            st.info("No students yet — add records using the tabs above."); st.stop()
        sel = st.selectbox("Select student", student_names["name"].tolist())
        sid = student_names[student_names["name"]==sel]["student_id"].iloc[0]
        sdf = df[df["student_id"]==sid]
        grade = sdf["grade"].max()
        lat = sdf[sdf["year"]==sdf["year"].max()]
        st.markdown(f"<div class='profile-card'><p class='student-name'>{sel}</p><p class='student-sub'>Grade {int(grade)} &nbsp;·&nbsp; Roll #{int(sid)}</p></div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f"<div class='metric-card'><p class='metric-value'>{lat['score'].mean():.0f}%</p><p class='metric-label'>Academic Avg</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><p class='metric-value'>{lat['attendance'].mean():.0f}%</p><p class='metric-label'>Attendance</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><p class='metric-value'>{sdf['year'].nunique()}</p><p class='metric-label'>Years Tracked</p></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><p class='metric-value'>{sdf['activity'].notna().sum()}</p><p class='metric-label'>Activities</p></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        ds = render_charts(sdf, sel)
        render_strengths(sdf)
        render_history(sdf)
        render_suggestions(ds)

    with tab2:
        st.markdown("<p class='section-header'>Add Year Record</p><p class='section-sub'>Enter academic scores and attendance for a student</p>", unsafe_allow_html=True)
        with st.form("add_record"):
            c1,c2 = st.columns(2)
            with c1:
                # Dropdown of existing students + option to add new
                existing = student_names["name"].tolist() if len(student_names)>0 else []
                name_options = existing + ["➕ Add new student"]
                name_choice = st.selectbox("Select student", name_options)
                if name_choice == "➕ Add new student":
                    new_name = st.text_input("New student name")
                else:
                    new_name = name_choice
                new_grade = st.number_input("Grade", min_value=1, max_value=12, value=6)
            with c2:
                new_year = st.number_input("Year", min_value=2010, max_value=2030, value=2024)
                new_att = st.number_input("Attendance %", min_value=0.0, max_value=100.0, value=90.0)
            st.markdown("**Subject scores** (leave 0 to skip)")
            subjects = ["Math","Science","English","Social Studies","Hindi","Art","Computer Science","Physical Education"]
            scores = {}
            cols = st.columns(4)
            for i,subj in enumerate(subjects):
                with cols[i%4]: scores[subj] = st.number_input(subj, min_value=0.0, max_value=100.0, value=0.0, key=f"sc_{subj}")
            if st.form_submit_button("💾 Save Year Record", type="primary", use_container_width=True):
                if not new_name or not str(new_name).strip():
                    st.error("Please enter a student name.")
                else:
                    df = load_data()
                    # Match by name exactly from dropdown, or by lowercase strip for new entries
                    match = df[df["name"]==new_name] if name_choice != "➕ Add new student" else df[df["name"].str.strip().str.lower()==new_name.strip().lower()]
                    sid = match["student_id"].iloc[0] if len(match)>0 else (int(df["student_id"].max()+1) if len(df)>0 else 1)
                    new_rows = [{"student_id":sid,"name":new_name if name_choice!="➕ Add new student" else new_name.strip(),"grade":new_grade,"year":new_year,"subject":subj,"score":sc,"attendance":new_att,"activity":None,"activity_category":None,"activity_level":None} for subj,sc in scores.items() if sc>0]
                    if new_rows:
                        df = pd.concat([df,pd.DataFrame(new_rows)],ignore_index=True)
                        save_data(df)
                        st.success(f"✅ Saved {len(new_rows)} subjects for {new_name} (Grade {new_grade})")
                    else:
                        st.warning("Enter at least one subject score.")

    with tab3:
        st.markdown("<p class='section-header'>Add Activity</p><p class='section-sub'>Record extracurricular achievements</p>", unsafe_allow_html=True)
        with st.form("add_activity"):
            c1,c2 = st.columns(2)
            with c1:
                # Dropdown of existing students + option to add new
                existing_a = student_names["name"].tolist() if len(student_names)>0 else []
                a_options = existing_a + ["➕ Add new student"]
                a_choice = st.selectbox("Select student", a_options, key="a_sel")
                if a_choice == "➕ Add new student":
                    a_name = st.text_input("New student name")
                else:
                    a_name = a_choice
                a_grade = st.number_input("Grade", min_value=1, max_value=12, value=6, key="ag")
                a_year = st.number_input("Year", min_value=2010, max_value=2030, value=2024, key="ay")
            with c2:
                a_title = st.text_input("Activity / Achievement", placeholder="e.g. State Chess Championship – 1st Prize")
                a_cat = st.selectbox("Category", ["Sports","Arts","Technical","Leadership","Social Work"])
                a_level = st.selectbox("Level", ["School","District","State","National"])
            if st.form_submit_button("➕ Add Activity", type="primary", use_container_width=True):
                if not a_name or not str(a_name).strip() or not a_title.strip():
                    st.error("Fill in student name and activity title.")
                else:
                    df = load_data()
                    match = df[df["name"]==a_name] if a_choice!="➕ Add new student" else df[df["name"].str.strip().str.lower()==a_name.strip().lower()]
                    sid = match["student_id"].iloc[0] if len(match)>0 else (int(df["student_id"].max()+1) if len(df)>0 else 1)
                    att_val = match["attendance"].iloc[0] if len(match)>0 else 0
                    new_row = pd.DataFrame([{"student_id":sid,"name":a_name,"grade":a_grade,"year":a_year,"subject":None,"score":None,"attendance":att_val,"activity":a_title.strip(),"activity_category":a_cat,"activity_level":a_level}])
                    df = pd.concat([df,new_row],ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Added '{a_title}' ({a_level}) for {a_name} in Grade {a_grade}")

    with tab4:
        st.markdown("<p class='section-header'>Delete Records</p><p class='section-sub'>Remove specific year records or an entire student</p>", unsafe_allow_html=True)

        if len(student_names) == 0:
            st.info("No student records found.")
        else:
            del_student = st.selectbox("Select student", student_names["name"].tolist(), key="del_sel")
            sid_del = student_names[student_names["name"] == del_student]["student_id"].iloc[0]
            sdf_del = df[df["student_id"] == sid_del]

            delete_type = st.radio("What do you want to delete?", ["Delete a specific year's record", "Delete entire student record"], horizontal=True)

            if delete_type == "Delete a specific year's record":
                available_grades = sorted(sdf_del["grade"].dropna().unique().astype(int).tolist())
                if not available_grades:
                    st.warning("No grade records found for this student.")
                else:
                    del_grade = st.selectbox("Select grade to delete", available_grades, key="del_grade")
                    preview = sdf_del[sdf_del["grade"] == del_grade]
                    st.markdown(f"<p style='color:#8b8fa8;font-size:13px;'>This will delete <b style='color:#f87171;'>{len(preview)} row(s)</b> for {del_student} — Grade {del_grade}.</p>", unsafe_allow_html=True)
                    confirm = st.checkbox(f"Yes, I confirm — delete Grade {del_grade} record for {del_student}")
                    if st.button("🗑️ Delete Grade Record", type="primary", disabled=not confirm):
                        df = load_data()
                        df = df[~((df["student_id"] == sid_del) & (df["grade"] == del_grade))]
                        save_data(df)
                        st.success(f"✅ Deleted Grade {del_grade} record for {del_student}.")
                        st.rerun()

            else:
                st.markdown(f"<p style='color:#f87171;font-size:13px;'>⚠️ This will permanently delete <b>all {len(sdf_del)} records</b> for {del_student} including all grades, activities and attendance.</p>", unsafe_allow_html=True)
                confirm_all = st.checkbox(f"Yes, I confirm — permanently delete all records for {del_student}")
                if st.button("🗑️ Delete Entire Student", type="primary", disabled=not confirm_all):
                    df = load_data()
                    df = df[df["student_id"] != sid_del]
                    save_data(df)
                    st.success(f"✅ All records for {del_student} have been deleted.")
                    st.rerun()

# ================================================================
# STUDENT VIEW
# ================================================================
else:
    if len(student_names)==0:
        st.info("No records found. Ask your teacher to add your data."); st.stop()
    sel = st.selectbox("Select your name", student_names["name"].tolist())
    sid = student_names[student_names["name"]==sel]["student_id"].iloc[0]
    sdf = df[df["student_id"]==sid]
    grade = sdf["grade"].max()
    lat = sdf[sdf["year"]==sdf["year"].max()]
    st.markdown(f"<div class='profile-card'><p class='student-name'>{sel}</p><p class='student-sub'>Grade {int(grade)} &nbsp;·&nbsp; Roll #{int(sid)}</p></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><p class='metric-value'>{lat['score'].mean():.0f}%</p><p class='metric-label'>Academic Avg</p></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><p class='metric-value'>{lat['attendance'].mean():.0f}%</p><p class='metric-label'>Attendance</p></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><p class='metric-value'>{sdf['year'].nunique()}</p><p class='metric-label'>Years Tracked</p></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><p class='metric-value'>{sdf['activity'].notna().sum()}</p><p class='metric-label'>Activities</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    ds = render_charts(sdf, sel)
    render_strengths(sdf)
    render_history(sdf)
    render_suggestions(ds)
