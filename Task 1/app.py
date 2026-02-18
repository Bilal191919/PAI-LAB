from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os
from io import BytesIO

from scrapper import WebFinder

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'temp_uploads'
if not os.path.exists('temp_uploads'):
    os.makedirs('temp_uploads')

my_tool = WebFinder()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process-excel', methods=['POST'])
def run_scanner():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Filename is empty'}), 400

        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except:
            return jsonify({'success': False, 'error': 'File format sahi nahi hai'}), 400

        columns = [c.lower() for c in df.columns]
        target_col = None
        
        if 'urls' in columns:
            target_col = df.columns[columns.index('urls')]
        elif 'website' in columns:
            target_col = df.columns[columns.index('website')]
            
        if not target_col:
            return jsonify({'success': False, 'error': 'Excel me "Urls" column nahi mila'}), 400

        url_list = df[target_col].dropna().astype(str).tolist()
        
        final_results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(my_tool.scan_website, url_list)
            
            for res in results:
                final_results.append(res)
        
        total_mails = sum(item['email_count'] for item in final_results)
        success_sites = sum(1 for item in final_results if item['email_count'] > 0)

        return jsonify({
            'success': True,
            'results': final_results,
            'total_urls': len(url_list),
            'successful': success_sites,
            'total_emails': total_mails
        })

    except Exception as e:
        print("Server Error:", e)
        return jsonify({'success': False, 'error': 'Server error aya ha'}), 500

@app.route('/api/download', methods=['POST'])
def get_excel():
    try:
        data = request.json.get('results', [])
        
        rows = []
        for item in data:
            if not item['emails']:
                rows.append({
                    'Website': item['base_url'],
                    'Found Email': 'Not Found',
                    'Pages Checked': item['pages_crawled']
                })
            else:
                for mail in item['emails']:
                    rows.append({
                        'Website': item['base_url'],
                        'Found Email': mail,
                        'Pages Checked': item['pages_crawled']
                    })
                    
        df = pd.DataFrame(rows)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Scraped Data')
            
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='scraped_data.xlsx'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': 'Download fail hogya'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)