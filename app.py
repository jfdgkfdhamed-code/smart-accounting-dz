import os
import sqlite3
from google import genai
import pandas as pd
import streamlit as st

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="المحاسب الذكي - AI Accounting ERP",
    page_icon="🤖",
    layout="wide",
)


# --- 1. إعداد قاعدة البيانات ---
def init_db():
  conn = sqlite3.connect("real_ai_accounting.db", check_same_thread=False)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            rc_number TEXT,
            capital REAL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            operation_type TEXT,
            debit_account TEXT,
            credit_account TEXT,
            amount REAL,
            ai_analysis TEXT,
            raw_text TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
  conn.commit()
  return conn, cursor


conn, cursor = init_db()

st.title("🧠 النظام المحاسبي المدعوم بالذكاء الاصطناعي (Gemini AI)")
st.write(
    "نظام سحابي يقبل النصوص الحرة بأي صياغة ويقوم بتحليلها وإيجاد القيود"
    " المحاسبية وفق نظام SCF."
)

# --- 2. القائمة الجانبية: الإعدادات والشركات ---
st.sidebar.title("⚙️ الإعدادات والشركات")

# خانة إدخال مفتاح الـ API
gemini_api_key = st.sidebar.text_input(
    "أدخل مفتاح Gemini API الخاص بك:",
    type="password",
    value="",
    help="الصق المفتاح الظاهر في صورتك هنا",
)

st.sidebar.divider()
with st.sidebar.expander("➕ تسجيل شركة جديدة"):
  comp_name = st.text_input("اسم المؤسسة")
  comp_rc = st.text_input("رقم السجل التجاري")
  comp_cap = st.number_input(
      "رأس المال (دج)", min_value=0.0, value=1000000.0, step=10000.0
  )
  if st.button("حفظ الشركة"):
    if comp_name:
      try:
        cursor.execute(
            "INSERT INTO companies (name, rc_number, capital) VALUES (?, ?, ?)",
            (comp_name, comp_rc, comp_cap),
        )
        conn.commit()
        st.sidebar.success("تم فتح ملف الشركة بنجاح!")
        st.rerun()
      except Exception:
        st.sidebar.error("الشركة مسجلة مسبقاً!")

cursor.execute("SELECT id, name, capital FROM companies")
comps = cursor.fetchall()

if not comps:
  st.warning("👈 يرجى تسجيل وإضافة شركة للبدء من القائمة الجانبية.")
else:
  c_map = {c[1]: (c[0], c[2]) for c in comps}
  sel_comp = st.sidebar.selectbox(
      "اختر الشركة المعنية:", list(c_map.keys())
  )
  cid, c_capital = c_map[sel_comp]

  st.sidebar.info(f"الشركة النشطة: **{sel_comp}**")

  tab1, tab2, tab3 = st.tabs([
      "🤖 المحلل المحاسبي الذكي (Gemini)",
      "📊 ميزانية الشركة وجدول النتائج",
      "📜 دفتر القيود المعتمدة",
  ])

  # ==========================================
  # التبويب الأول: التحليل بالذكاء الاصطناعي
  # ==========================================
  with tab1:
    st.subheader(
        "🧠 تحليل النصوص الحرة والعمليات المعقدة (اهتلاكات، سفتجة، خصم)"
    )

    with st.form("gemini_form"):
      user_query = st.text_area(
          "اكتب العملية المحاسبية بأي طريقة (عربي، دارجة، فرنسية):",
          placeholder=(
              "مثال: شرينا شاحنة بـ 2 مليون دينار ورايحين نحسبو الاهتلاك تاعها"
              " على 5 سنين."
          ),
      )
      submit_ai = st.form_submit_button("🚀 تحليل العملية عبر الذكاء الاصطناعي")

    if submit_ai:
      if not gemini_api_key.strip():
        st.error(
            "🚨 يرجى لصق مفتاح Gemini API في خانة الشريط الجانبي أولاً!"
        )
      elif not user_query.strip():
        st.warning("يرجى كتابة نص العملية أولاً.")
      else:
        with st.spinner(
            "🧠 جاري الاتصال بمحرك Gemini وتحليل القيود المحاسبية..."
        ):
          try:
            # تهيئة عميل الذكاء الاصطناعي بالمفتاح المُدخل
            client = genai.Client(api_key=gemini_api_key.strip())

            prompt = f"""
            أنت خبير محاسبي مالي محترف متخصص في النظام المحاسبي المالي الجزائر (SCF) والقوانين الجبائية.
            قم بتحليل العملية التالية التي كتبها المحاسب:
            "{user_query}"

            المطلوب:
            1. حدد نوع العملية المحاسبية بدقة (اهتلاك، سفتجة، خصم، شراء، مبيعات...).
            2. حدد حسابات المدين (Débit) وحسابات الدائن (Crédit) وأرقام الحسابات إن أمكن.
            3. احسب المبلغ الصافي أو الأقساط إن وجدت.
            4. قدم تحليلاً محاسبياً وجبائياً قصيراً ومباشراً.

            اكتب الإجابة بتنسيق واضح ومنظم جداً.
            """

            # استخدام النموذج القياسي السريع والمستقر
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            st.session_state["ai_response_text"] = response.text
            st.session_state["raw_user_query"] = user_query
            st.success("تم التحليل بنجاح بواسطة الذكاء الاصطناعي!")

          except Exception as e:
            st.error(
                "حدث خطأ في الاتصال. تأكد أن المفتاح منسوخ بشكل صحيح وبدون فراغات"
                f" إضافية.\nالتفاصيل التقنية: {e}"
            )

    # عرض نتائج التحليل
    if "ai_response_text" in st.session_state:
      st.divider()
      st.markdown("### 📋 نتيجة تحليل الذكاء الاصطناعي الحقيقي:")
      st.markdown(st.session_state["ai_response_text"])

      if st.button("💾 اعتماد وحفظ هذا القيد والتحليل في سجلات الشركة"):
        cursor.execute(
            "INSERT INTO entries (company_id, operation_type, debit_account,"
            " credit_account, amount, ai_analysis, raw_text) VALUES (?, ?,"
            " ?, ?, ?, ?, ?)",
            (
                cid,
                "تحليل AI معقد",
                "محدد في التقرير",
                "محدد في التقرير",
                0.0,
                st.session_state["ai_response_text"],
                st.session_state["raw_user_query"],
            ),
        )
        conn.commit()
        st.success("تم تثبيت التقرير والقيد المحاسبي بنجاح!")
        del st.session_state["ai_response_text"]
        st.rerun()

  # ==========================================
  # التبويب الثاني والثالث
  # ==========================================
  with tab2:
    st.subheader("📊 القيود والتقارير المعتمدة للشركة")
    cursor.execute(
        "SELECT raw_text, date FROM entries WHERE company_id = ?", (cid,)
    )
    entries_list = cursor.fetchall()
    st.metric("عدد العمليات المحللة ذكياً", len(entries_list))
    if entries_list:
      st.dataframe(
          pd.DataFrame(entries_list, columns=["العملية الأصلية", "التاريخ"]),
          use_container_width=True,
      )

  with tab3:
    st.subheader("📜 تفاصيل التحليلات المحفوظة")
    cursor.execute(
        "SELECT raw_text, ai_analysis, date FROM entries WHERE company_id = ?",
        (cid,),
    )
    logs = cursor.fetchall()
    for l in logs:
      with st.expander(f"العملية: {l[0]} ({l[2]})"):
        st.markdown(l[1])
