import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Response
from fpdf import FPDF
from datetime import datetime

# --- SETUP ---
app = Flask(__name__)
DATABASE_FILE = 'billing.db'

# --- DATABASE HELPER FUNCTION ---
# A simple function to connect to our database
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This makes the data easier to work with
    return conn

# --- WEB PAGES (ROUTES) ---

# 1. The Main Page: Shows the billing form
@app.route('/')
def index():
    return render_template('index.html')

# 2. The Calculation Logic: This runs when you submit the form
@app.route('/create_bill', methods=['POST'])
def create_bill():
    # Get all the data from the form the user filled out
    customer_name = request.form['customer_name']
    customer_phone = request.form['customer_phone']
    product_details = request.form['product_details']
    gold_weight = float(request.form['gold_weight'])
    gold_rate = float(request.form['gold_rate'])
    making_charges = float(request.form['making_charges'])
    gst_percent = 3.0 # Standard 3% GST

    # --- The Calculation ---
    # Formula: (Weight * Rate) + Making Charges + GST
    price_before_tax = (gold_weight * gold_rate) + making_charges
    gst_amount = price_before_tax * (gst_percent / 100)
    final_total_amount = price_before_tax + gst_amount

    # Save this bill to our database
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO sales (customer_name, customer_phone, product_details, gold_weight, gold_rate, making_charges, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (customer_name, customer_phone, product_details, gold_weight, gold_rate, making_charges, final_total_amount)
    )
    conn.commit()
    conn.close()

    # After saving, send the user to the reports page
    return redirect(url_for('reports'))

# 3. The Reports Page: Shows a list of all past bills
@app.route('/reports')
def reports():
    conn = get_db_connection()
    # Get all sales from the database, with the newest ones first
    sales_records = conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
    conn.close()
    # Send that data to our reports.html webpage
    return render_template('reports.html', sales=sales_records)

# 4. The PDF Generator: Creates an invoice for a specific bill
@app.route('/invoice/<int:sale_id>')
def generate_invoice(sale_id):
    # Find the specific sale in the database
    conn = get_db_connection()
    sale = conn.execute('SELECT * FROM sales WHERE id = ?', (sale_id,)).fetchone()
    conn.close()

    # --- PDF Creation using FPDF2 ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Shop Details (You can change these)
    pdf.cell(0, 10, 'Your Shop Name', 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 6, 'Your Address, Bengaluru, Karnataka', 0, 1, 'C')
    pdf.ln(10)

    # Invoice Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 8, 'Invoice ID:', 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, str(sale['id']), 0, 1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 8, 'Date:', 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, datetime.strptime(sale['sale_date'], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y'), 0, 1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 8, 'Customer:', 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"{sale['customer_name']} ({sale['customer_phone']})", 0, 1)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 8, 'Description', 1, 0, 'C')
    pdf.cell(50, 8, 'Amount (INR)', 1, 1, 'C')

    # Table Body
    pdf.set_font("Arial", '', 12)
    price_before_tax = (sale['gold_weight'] * sale['gold_rate']) + sale['making_charges']
    gst_amount = price_before_tax * 0.03

    pdf.cell(130, 8, f"{sale['product_details']} ({sale['gold_weight']}g)", 1, 0)
    pdf.cell(50, 8, f"{price_before_tax:,.2f}", 1, 1, 'R')
    pdf.cell(130, 8, 'GST (3%)', 1, 0)
    pdf.cell(50, 8, f"{gst_amount:,.2f}", 1, 1, 'R')

    # Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 10, 'Total', 1, 0, 'R')
    pdf.cell(50, 10, f"{sale['total_amount']:,.2f}", 1, 1, 'R')

    # Return the PDF to the browser
    return Response(pdf.output(dest='S').encode('latin-1'),
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline;filename=invoice_{sale_id}.pdf'})


# --- START THE APP ---
# This is the last line that actually starts your web application server
if __name__ == '__main__':
    app.run(debug=True)
    # dummy comment