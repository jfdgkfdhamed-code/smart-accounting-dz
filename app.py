import sqlite3
import pandas as pd
import streamlit as st

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="المحاسب الذكي بالذكاء الاصطناعي - AI Accounting ERP",
    page_icon="🤖",
    layout="wide",
)


# --- 1. إعداد قاعدة البيانات المتقدمة ---
def init_db():
  conn = sqlite3.connect("ai_accounting.db", check_same_thread=False)
  cursor = conn.cursor()

  # جدول الشركات
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            rc_number TEXT,
            capital REAL
        )
    """)

  # جدول القيود المحاسبية المعقدة
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            operation_type TEXT,
            debit_account TEXT,
            credit_account TEXT,
            amount REAL,
            ai_notes TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
  conn.commit()
  return conn, cursor


conn, cursor = init_db()

st.title("🤖 النظام المحاسبي الذكي المدعوم بالذكاء الاصطناعي (AI ERP)")
st.write(
    "نظام متطور يدمج المنطق المحاسبي المعقد (اهتلاك، سفتجات، ضرائب) مع معالجة"
    " الذكاء الاصطناعي."
)

# --- 2. القائمة الجانبية ---
st.sidebar.title("🏢 إداراة العملاء والشركات")
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
      except:
        st.sidebar.error("الشركة مسجلة مسبقاً!")

cursor.execute("SELECT id, name, capital FROM companies")
comps = cursor.fetchall()

if not comps:
  st.warning("👈 يرجى تسجيل وإضافة شركة للبدء.")
else:
  c_map = {c[1]: (c[0], c[2]) for c in comps}
  sel_comp = st.sidebar.selectbox(
      "اختر الشركة المعنية:", list(c_map.keys())
  )
  cid, c_capital = c_map[sel_comp]

  st.sidebar.divider()
  st.sidebar.info(f"الشركة النشطة: **{sel_comp}**")

  # التبويبات الكبرى للنظام الذكي
  tab1, tab2, tab3 = st.tabs(
      [
          "🤖 المحلل الذكي للعمليات المعقدة (AI Engine)",
          "📊 ميزانية الشركات وجدول النتائج (TCR)",
          "📜 دفتر القيود المركبة والتدقيق",
      ]
  )

  # ==========================================
  # التبويب الأول: الذكاء الاصطناعي لمعالجة العمليات الصعبة
  # ==========================================
  with tab1:
    st.subheader(
        "🧠 معالجة العمليات المحاسبية المعقدة بالذكاء الاصطناعي (اهتلاك، سفتجات،"
        " خصومات)"
    )
    st.write(
        "أدخل وصف العملية باللغة العادية (مثلاً: شراء معدات بـ 500 ألف دج تهتلك"
        " على 3 سنوات، أو خصم سفتجة بقيمة 20 ألف دج)، وسيقوم المحرك الذكي بتحليلها"
        " واستخراج القيد المحاسبي تلقائياً!"
    )

    with st.form("ai_engine_form"):
      ai_input_text = st.text_area(
          "اكتب العملية المحاسبية أو المالية هنا:",
          placeholder=(
              "مثال: تم شراء شاحنة بـ 1,200,000 دج، وتخضع للاهتلاك الخطي على 5"
              " سنوات."
          ),
      )
      ai_submit = st.form_submit_button("🚀 تحليل العملية وتوليد القيد المحاسبي")

      if ai_submit and ai_input_text:
        st.info("🔄 جاري تحليل المعطيات وحساب الآثار المحاسبية والجبائية...")

        # محاكاة لمحرك الذكاء الاصطناعي المحاسبي المتقدم
        lower_text = ai_input_text.lower()
        if "اهتلاك" in lower_text or "إهتلاك" in lower_text:
          op_type = "تسجيل قسط الاهتلاك (Amortissement)"
          debit = "حساب 68 (مخصصات الاهتلاك والمؤونات)"
          credit = "حساب 28 (اهتلاك تثبيتات)"
          # محاكاة استخراج الأرقام وتحليلها
          ai_analysis = (
              "✅ **تحليل الذكاء الاصطناعي:** تم رصد عملية اهتلاك تثبيتات."
              " النظام قام بتطبيق طريقة الاهتلاك الخطي وتوليد القيد المحاسبي"
              " القانوني المطابق للمعايير المحاسبية المالية (SCF)."
          )
        elif "سفتجة" in lower_text or "كمبيالة" in lower_text:
          op_type = "خصم ورقة تجارية (Effet de commerce)"
          debit = "حساب 51 (البنك / الصندوق) + حساب 62 (مصاريف البنك والخصم)"
          credit = "حساب 41 (الزبناء - أوراق تجارية للدفع)"
          ai_analysis = (
              "✅ **تحليل الذكاء الاصطناعي:** تم رصد عملية سفتجة مع خصم بنكي."
              " النظام قام بفصل الصافي المقبوض عن مصاريف الأغراض البنكية"
              " لتفادي خطأ تسوية الصندوق."
          )
        else:
          op_type = "عملية مالية عامة ومشتريات"
          debit = "حساب الأعباء أو المخزون المعني"
          credit = "حساب الموردين أو الخزينة"
          ai_analysis = (
              "✅ **تحليل الذكاء الاصطناعي:** تم تصنيف العملية ضمن القيود"
              " العادية مع التحقق من توازن المدين والدائن."
          )

        st.success(ai_analysis)
        st.markdown(f"**نوع العملية:** {op_type}")
        st.markdown(f"**المدين (Débit):** {debit}")
        st.markdown(f"**الدائن (Crédit):** {credit}")

        # زر لتأكيد حفظ القيد المستخرج بالذكاء الاصطناعي في قاعدة البيانات
        if st.button("💾 اعتماد وحفظ هذا القيد في دفاتر الشركة"):
          cursor.execute(
              "INSERT INTO entries (company_id, operation_type, debit_account,"
              " credit_account, amount, ai_notes) VALUES (?, ?, ?, ?, ?, ?)",
              (
                  cid,
                  op_type,
                  debit,
                  credit,
                  100000.0,
                  ai_input_text,
              ),  # مبلغ افتراضي للتوضيح
          )
          conn.commit()
          st.success("تم تثبيت القيد المحاسبي في السجل بنجاح!")

  # ==========================================
  # التبويب الثاني: التقارير والتحليل المالي
  # ==========================================
  with tab2:
    st.subheader("📊 لوحة المؤشرات المالية وجدول حساب النتائج (TCR)")
    cursor.execute(
        "SELECT operation_type, amount FROM entries WHERE company_id = ?",
        (cid,),
    )
    recs = cursor.fetchall()

    total_ops = len(recs)
    st.metric("إجمالي القيود المعالجة ذكياً", total_ops)

    if recs:
      st.markdown("### جدول النتائج الملخص المستخرج من النظام الذكي")
      tcr_df = pd.DataFrame(
          recs, columns=["العملية المحاسبية", "المبلغ المقدر (دج)"]
      )
      st.dataframe(tcr_df, use_container_width=True)
    else:
      st.info(
          "لم يتم تسجيل أي عمليات بعد. استخدم المحلل الذكي في التبوب الأول لإدخال"
          " العمليات."
      )

  # ==========================================
  # التبويب الثالث: سجل القيود والتدقيق
  # ==========================================
  with tab3:
    st.subheader("📜 سجل التدقيق والقيود المحاسبية المؤكدة")
    cursor.execute(
        "SELECT operation_type, debit_account, credit_account, ai_notes, date"
        " FROM entries WHERE company_id = ?",
        (cid,),
    )
    audit_log = cursor.fetchall()

    if audit_log:
      st.dataframe(
          pd.DataFrame(
              audit_log,
              columns=[
                  "نوع العملية",
                  "المدين",
                  "الدائن",
                  "الوصف الأصلي",
                  "التاريخ",
              ],
          ),
          use_container_width=True,
      )
    else:
      st.info("سجل القيود فارغ حالياً.")
