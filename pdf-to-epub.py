import os
import fitz  # PyMuPDF
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import tempfile

def extract_images_from_page(doc, page, page_num, output_dir):
    images = page.get_images(full=True)
    image_paths = []
    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
        image_path = os.path.join(output_dir, image_filename)
        with open(image_path, 'wb') as img_file:
            img_file.write(image_bytes)
        image_paths.append(image_path)
    return image_paths

def extract_text_with_layout(page):
    text_data = page.get_text("dict")
    text_blocks = text_data['blocks']
    extracted_text = ""
    for block in text_blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    left, top, right, bottom = span['bbox']
                    font_size = span['size']
                    text = span['text']
                    # Use a div with absolute positioning for each text span
                    extracted_text += f'<div style="position:absolute; left:{left}px; top:{top}px; font-size:{font_size}px; white-space:nowrap;">{text}</div>'
    return extracted_text

def convert_pdf_to_html_ebook(pdf_file):
    doc = fitz.open(pdf_file)
    temp_dir = tempfile.mkdtemp()
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    output_file = os.path.join(temp_dir, "ebook.html")
   
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PDF to eBook</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }

            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }

            .page {
                position: relative;
                width: 700px;  /* Fixed width */
                height: 870px; /* Fixed height */
                overflow: hidden;
                margin: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .page img {
                width: 100%;
                height: 100%;
                object-fit: contain;  /* Maintain aspect ratio */
                max-width: 100%;  /* Constrain to page width */
                max-height: 100%;  /* Constrain to page height */
            }

            .nav-buttons {
                text-align: center;
                margin-top: 20px;
            }

            .hidden {
                display: none;
            }

            button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }

            button:hover {
                background-color: #0056b3;
            }
        </style>
        <script>
            let currentPage = 0;

            function showPage(pageNum) {
                const pages = document.querySelectorAll('.page');
                pages.forEach((page, index) => {
                    page.classList.add('hidden');
                    if (index === pageNum || index === pageNum + 1) {
                        page.classList.remove('hidden');
                    }
                });
            }

            function nextPage() {
                const pages = document.querySelectorAll('.page');
                if (currentPage < pages.length - 2) {
                    currentPage += 2;
                    showPage(currentPage);
                }
            }

            function prevPage() {
                if (currentPage > 0) {
                    currentPage -= 2;
                    showPage(currentPage);
                }
            }

            window.onload = function() {
                showPage(0);
            }
        </script>
    </head>
    <body>
        <div class="container">
    """
   
    for page_num in range(0, doc.page_count, 2):
        left_page = doc.load_page(page_num)
        right_page = doc.load_page(page_num + 1) if page_num + 1 < doc.page_count else None
        images_left = extract_images_from_page(doc, left_page, page_num, images_dir)
       
        html_content += f'<div class="page hidden">{extract_text_with_layout(left_page)}'
        for image_path in images_left:
            html_content += f'<img src="images/{os.path.basename(image_path)}" alt="Page Image">'
        html_content += '</div>'
       
        if right_page:
            images_right = extract_images_from_page(doc, right_page, page_num + 1, images_dir)
            html_content += f'<div class="page hidden">{extract_text_with_layout(right_page)}'
            for image_path in images_right:
                html_content += f'<img src="images/{os.path.basename(image_path)}" alt="Page Image">'
            html_content += '</div>'
   
    html_content += """
        </div>
        <div class="nav-buttons">
            <button onclick="prevPage()">Previous</button>
            <button onclick="nextPage()">Next</button>
        </div>
    </body>
    </html>
    """
   
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
   
    return output_file

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        output_file = convert_pdf_to_html_ebook(file_path)
        messagebox.showinfo("Success", "HTML eBook with images created successfully!")
        webbrowser.open(output_file)

def create_gui():
    root = tk.Tk()
    root.title("PDF to HTML eBook Converter")
    browse_button = tk.Button(root, text="Select PDF and Convert to eBook (HTML)", command=browse_file)
    browse_button.pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_gui()