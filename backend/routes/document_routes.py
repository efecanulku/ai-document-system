from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os, uuid, pdfplumber, docx, openpyxl
import pytesseract
from PIL import Image

from models.database import db, Document, DocumentContent
from .auth_routes import token_required

documents_bp = Blueprint('documents_bp', __name__)

# Tesseract (Windows yolu)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ALLOWED_EXT = {'txt','pdf','png','jpg','jpeg','gif','doc','docx','xls','xlsx'}

def allowed_file(name): 
    return '.' in name and name.rsplit('.',1)[1].lower() in ALLOWED_EXT

# ---- Text extraction helpers ----
def _extract_pdf(path):
    out=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            if t.strip(): out.append(t)
    return "\n".join(out).strip()

def _extract_docx(path):
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs).strip()

def _extract_xlsx(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts=[]
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            vals=[str(c) for c in row if c is not None]
            if vals: parts.append(" ".join(vals))
    return "\n".join(parts).strip()

def _extract_img(path):
    try:
        return pytesseract.image_to_string(Image.open(path), lang="tur+eng").strip()
    except Exception:
        return pytesseract.image_to_string(Image.open(path)).strip()

def _extract_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def extract_by_ext(path, ext):
    ext=(ext or "").lower()
    if ext=='pdf':  return _extract_pdf(path)
    if ext=='docx': return _extract_docx(path)
    if ext in ('xlsx','xls'): return _extract_xlsx(path)
    if ext in ('png','jpg','jpeg','gif'): return _extract_img(path)
    if ext=='txt':  return _extract_txt(path)
    return ""
# ---------------------------------

@documents_bp.route('/upload', methods=['POST'])
@token_required
def upload_documents():
    try:
        if 'files' not in request.files:
            return jsonify({'error':'Dosya seçilmemiş'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'error':'Dosya bulunamadı'}), 400

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        uploaded=[]
        for f in files:
            if not f or f.filename=='' or not allowed_file(f.filename):
                continue

            filename = secure_filename(f.filename)
            ext = filename.rsplit('.',1)[1].lower() if '.' in filename else ''
            unique = f"{uuid.uuid4()}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique)
            f.save(save_path)

            doc = Document(
                filename=unique,
                original_filename=filename,
                file_path=save_path,
                file_type=ext,
                file_size=os.path.getsize(save_path),
                company_id=request.company_id,
                uploaded_by=request.user_id
            )
            db.session.add(doc); db.session.flush()

            content = ""
            try:
                content = extract_by_ext(save_path, ext)
            except Exception as e:
                current_app.logger.warning(f"Extract fail doc {doc.id}: {e}")

            if content:
                dc = DocumentContent(document_id=doc.id, content=content)
                db.session.add(dc)
                if hasattr(doc, "is_processed"):
                    doc.is_processed = True
            else:
                if hasattr(doc, "is_processed"):
                    doc.is_processed = False

            uploaded.append(doc.to_dict())

        db.session.commit()
        return jsonify({'message': f'{len(uploaded)} dosya başarıyla yüklendi', 'files': uploaded}), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Upload error")
        return jsonify({'error':'Dosya yüklenirken hata oluştu'}), 500

@documents_bp.route('', methods=['GET'])
@token_required
def list_documents():
    try:
        docs = Document.query.filter_by(company_id=request.company_id).order_by(Document.created_at.desc()).all()
        return jsonify({'documents':[d.to_dict() for d in docs]})
    except Exception:
        current_app.logger.exception("List docs error")
        return jsonify({'error':'Belgeler alınırken hata oluştu'}), 500

@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@token_required
def delete_document(doc_id:int):
    try:
        doc = Document.query.filter_by(id=doc_id, company_id=request.company_id).first()
        if not doc:
            return jsonify({'error':'Belge bulunamadı'}), 404

        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            current_app.logger.warning(f"File delete warn: {e}")

        DocumentContent.query.filter_by(document_id=doc.id).delete(synchronize_session=False)
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'message':'Belge başarıyla silindi'})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete doc error")
        return jsonify({'error':'Belge silinirken hata oluştu'}), 500

@documents_bp.route('/stats', methods=['GET'])
@token_required
def stats():
    try:
        total = Document.query.filter_by(company_id=request.company_id).count()
        processed = Document.query.filter_by(company_id=request.company_id, is_processed=True).count()
        return jsonify({
            'total_documents': total,
            'processed_documents': processed,
            'pending_documents': total - processed
        })
    except Exception:
        current_app.logger.exception("Stats error")
        return jsonify({'error':'İstatistikler alınırken hata oluştu'}), 500
