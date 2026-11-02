import sqlite3
import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="المحاسب الآلي - نظام مكاتب المحاسبة",
    page_icon="💼",
    layout="wide",
)


# --- 1. إعداد قاعدة بيانات مكتب المحاسبة ---
def init_db():
  conn = sqlite3.connect("accounting_office.db", check_same_thread=False)
  cursor = conn.cursor()

  # جدول الشركات والعملاء
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            rc_number TEXT,
            capital REAL
        )
    """)

  # جدول الحركات المالية (فواتير، مصاريف، شراء، بيع)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            type TEXT, -- (بيع، شراء، مصاريف، أجور)
            amount REAL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
  conn.commit()
  return conn, cursor


conn, cursor = init_db()

st.title("💼 المحاسب الآلي - نظام إدارة مكاتب المحاسبة")
st.write(
    "نظام آلي متكامل يتطلب إدخال كافة البيانات الأساسية للشركة قبل توليد"
    " الميزانيات والتقارير المالية."
)

# --- 2. القائمة الجانبية: اختيار أو إضافة شركة ---
st.sidebar.title("🏢 إدارة العملاء والشركات")

# إضافة شركة جديدة
with st.sidebar.expander("➕ تسجيل شركة جديدة"):
  comp_name = st.text_input("اسم الشركة/المؤسسة")
  comp_rc = st.text_input("رقم السجل التجاري (RC)")
  comp_capital = st.number_input(
      "رأس المال الافتتاحي (دج)", min_value=0.0, value=1000000.0
  )

  if st.button("حفظ الشركة"):
    if comp_name and comp_rc:
      try:
        cursor.execute(
            "INSERT INTO companies (name, rc_number, capital) VALUES (?, ?,"
            " ?)",
            (comp_name.strip(), comp_rc.strip(), comp_capital),
        )
        conn.commit()
        st.sidebar.success(f"تم تسجيل الشركة '{comp_name}' بنجاح!")
        st.rerun()
      except sqlite3.IntegrityError:
        st.sidebar.error("هذه الشركة مسجلة مسبقاً!")
    else:
      st.sidebar.error("يرجى ملء جميع بيانات الشركة!")

# جلب قائمة الشركات المسجلة
cursor.execute("SELECT id, name, capital FROM companies")
companies_list = cursor.fetchall()

if not companies_list:
  st.warning(
      "👈 لا توجد شركات مسجلة في المكتب بعد. يرجى إضافة شركة من القائمة الجانبية"
      " للبدء."
  )
else:
  # اختيار الشركة المراد العمل عليها
  comp_dict = {c[1]: (c[0], c[2]) for c in companies_list}
  selected_comp_name = st.sidebar.selectbox(
      "اختر الشركة للعمل عليها:", list(comp_dict.keys())
  )

  selected_comp_id = comp_dict[selected_comp_name][0]
  selected_comp_capital = comp_dict[selected_comp_name][1]

  st.info(
      f"الشركة الحالية: **{selected_comp_name}** | رأس المال الافتتاحي:"
      f" **{selected_comp_capital:,.2f} دج**"
  )

  # تبويبات النظام
  tab1, tab2 = st.tabs(
      ["📥 شاشة المدخلات الإجبارية", "📊 المخرجات والميزانية الآلية"]
  )

  # ==========================================
  # التبويب الأول: إدخال البيانات الإجبارية
  # ==========================================
  with tab1:
    st.subheader("إدخال الفواتير والحركات المالية للشركة")
    st.caption("ملاحظة: لن يمكنك استخراج التقارير دون تسجيل الحركات المكتملة.")

    with st.form("transaction_form", clear_on_submit=True):
      col1, col2 = st.columns(2)
      t_type = col1.selectbox(
          "نوع الحركة المالية",
          [
              "بيع (Produit / Vente)",
              "شراء (Achat / Charge)",
              "مصاريف عامة (إيجار، كهرباء...)",
              "أجور العمال (Paie)",
          ],
      )
      t_amount = col2.number_input(
          "المبلغ الإجمالي (دج)", min_value=0.0, value=10000.0
      )
      t_desc = st.text_input("بيان الحركة / رقم الفاتورة / التفاصيل")

      submit_trans = st.form_submit_button("تسجيل الحركة المالية")
      if submit_trans:
        if t_amount > 0 and t_desc:
          cursor.execute(
              "INSERT INTO transactions (company_id, type, amount, description)"
              " VALUES (?, ?, ?, ?)",
              (selected_comp_id, t_type, t_amount, t_desc),
          )
          conn.commit()
          st.success("تم تسجيل الحركة بنجاح!")
          st.rerun()
        else:
          st.error("يرجى إدخال مبلغ صحيح وبيان للحركة!")

    # عرض الحركات المسجلة لهذه الشركة
    cursor.execute(
        "SELECT type, amount, description, date FROM transactions WHERE"
        " company_id = ?",
        (selected_comp_id,),
    )
    history = cursor.fetchall()

    if history:
      st.subheader("📋 سجل المدخلات الحالي:")
      df_history = pd.DataFrame(
          history, columns=["النوع", "المبلغ (دج)", "البيان/التفاصيل", "التاريخ"]
      )
      st.dataframe(df_history, use_container_width=True)
    else:
      st.warning("لم يتم تسجيل أي حركات مالية لهذه الشركة بعد.")

  # ==========================================
  # التبويب الثاني: معالجة البيانات واستخراج الميزانية
  # ==========================================
  with tab2:
    st.subheader("جدول حساب النتائج والميزانية الآلية")

    cursor.execute(
        "SELECT type, amount FROM transactions WHERE company_id = ?",
        (selected_comp_id,),
    )
    records = cursor.fetchall()

    # شرط النظام: يرفض الحساب إذا كانت البيانات فارغة
    if not records:
      st.error(
          "🚨 النظام يرفض العمل! لا يمكن توليد تقرير مالي أو ميزانية لأن البيانات"
          " فارغة. يرجى إدخال حركات مالية في تبويب المدخلات أولاً."
      )
    else:
      # حساب المبيعات والمصاريف تلقائياً
      total_sales = sum(
          r[1] for r in records if r[0] == "بيع (Produit / Vente)"
      )
      total_purchases = sum(
          r[1] for r in records if r[0] == "شراء (Achat / Charge)"
      )
      total_expenses = sum(
          r[1] for r in records if "مصاريف" in r[0] or "أجور" in r[0]
      )

      total_costs = total_purchases + total_expenses
      net_result = total_sales - total_costs

      col_a, col_b, col_c = st.columns(3)
      col_a.metric("إجمالي الإيرادات (المبيعات)", f"{total_sales:,.2f} دج")
      col_b.metric("إجمالي التكاليف والمصاريف", f"{total_costs:,.2f} دج")

      if net_result >= 0:
        col_c.metric(
            "صافي النتيجة (ربح 🟢)",
            f"{net_result:,.2f} دج",
            delta_color="normal",
        )
      else:
        col_c.metric(
            "صافي النتيجة (خسارة 🔴)",
            f"{net_result:,.2f} دج",
            delta_color="inverse",
        )

      st.divider()
      st.markdown("### 📜 جدول حساب النتائج الملخص (TCR)")
      tcr_data = {
          "البيان المحاسبي": [
              "رقم الأعمال (المبيعات)",
              "مشتريات البضائع والخدمات",
              "المصاريف والأجور",
              "إجمالي التكاليف",
              "النتيجة الصافية قبل الضريبة",
          ],
          "المبلغ (دج)": [
              f"{total_sales:,.2f}",
              f"{total_purchases:,.2f}",
              f"{total_expenses:,.2f}",
              f"{total_costs:,.2f}",
              f"{net_result:,.2f}",
          ],
      }
      st.table(pd.DataFrame(tcr_data))
