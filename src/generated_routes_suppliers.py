# Auto-generated routes - Copy these into app.py

# Auto-generated CRUD routes for suppliers

@app.route('/suppliers')
@login_required
def suppliers():
    """List all suppliers records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suppliers ORDER BY id DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('suppliers_list.html', records=records, title='Suppliers')
    except Exception as e:
        flash(f'Error loading records: {str(e)}', 'error')
        return render_template('suppliers_list.html', records=[], title='Suppliers')

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_suppliers():
    """Add new suppliers record"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('suppliers'))
        
        try:
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO suppliers (name, contact, email)
                VALUES (%s, %s, %s)
            """, (name, contact, email))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Record added successfully', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'Error adding record: {str(e)}', 'error')
            return redirect(url_for('add_suppliers'))
    
    return render_template('suppliers_add.html', title='Add Suppliers')

@app.route('/suppliers/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_suppliers(record_id):
    """Edit suppliers record"""
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('suppliers'))
        
        try:
                        name = request.form.get('name', '').strip()
            contact = request.form.get('contact', '').strip()
            email = request.form.get('email', '').strip()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE suppliers 
                SET name = %s, contact = %s, email = %s
                WHERE name = %s
            """, (name, contact, email, record_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Record updated successfully', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'Error updating record: {str(e)}', 'error')
            return redirect(url_for('edit_suppliers', record_id=record_id))
    
    # GET request - load record
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suppliers WHERE name = %s", (record_id,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if record:
            return render_template('suppliers_edit.html', record=record, title='Edit Suppliers')
        else:
            flash('Record not found', 'error')
            return redirect(url_for('suppliers'))
    except Exception as e:
        flash(f'Error loading record: {str(e)}', 'error')
        return redirect(url_for('suppliers'))

@app.route('/suppliers/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_suppliers(record_id):
    """Delete suppliers record"""
    if not validate_csrf_token():
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('suppliers'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE name = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Record deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting record: {str(e)}', 'error')
    
    return redirect(url_for('suppliers'))
