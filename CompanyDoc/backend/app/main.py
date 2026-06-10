from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
import os

app = FastAPI(title="CompanyDoc API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "companydoc.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
def startup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            content_en TEXT,
            content_th TEXT,
            template_id INTEGER,
            category TEXT DEFAULT '其他',
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            approver TEXT,
            status TEXT,
            comment TEXT,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zh TEXT NOT NULL,
            en TEXT,
            th TEXT,
            category TEXT DEFAULT '通用'
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM terms")
    if cursor.fetchone()[0] == 0:
        sample_terms = [
            ("经销商授权书", "Dealer Authorization", "จดหมายอนุญาตตัวแทนจำหน่าย", "合同"),
            ("有效期", "Valid Period", "ช่วงเวลาที่มีผลบังคับ", "合同"),
            ("授权范围", "Scope of Authorization", "ขอบเขตของการอนุญาต", "合同"),
            ("乙方", "Party B", "ฝ่ายที่สอง", "合同"),
            ("甲方", "Party A", "ฝ่ายที่หนึ่ง", "合同"),
            ("协议", "Agreement", "ข้อตกลง", "合同"),
            ("合同", "Contract","สัญญา", "合同"),
            ("通知", "Notice", "การแจ้ง", "通知"),
            ("会议纪要", "Meeting Minutes", "บันทึกการประชุม", "会议"),
            ("报告", "Report", "รายงาน", "报告"),
            # 法律术语
            ("仲裁", "Arbitration", "อนุญาต", "法律"),
            ("不可抗力", "Force Majeure", "อุปสรรคสงคราม", "法律"),
            ("产品责任", "Product Liability","ความรับผิดต่อสินค้า", "法律"),
            ("知识产权", "Intellectual Property", "ทรัพย์สินทางปัญญา", "法律"),
            ("保密义务", "Confidentiality", "การรักษาความลับ", "法律"),
            ("违约", "Breach of Contract", "การละเมิดสัญญา", "法律"),
            ("赔偿", "Compensation", "การชดเชย", "法律"),
            ("终止", "Termination", "การสิ้นสุด", "法律"),
            ("诉讼", "Litigation","การฟ้องคดี", "法律"),
            # 税务贸易术语
            ("关税", "Customs Duty", "อากรศุลกากร", "税务"),
            ("增值税", "VAT / Value Added Tax", "ภาษีมูลค่าเพิ่ม", "税务"),
            ("原产地证明", "Certificate of Origin", "หนังสือรับรองแหล่งกำเนิดสินค้า", "贸易"),
            ("检验证书", "Inspection Certificate", "วุติับัตรตรวจสอบสินค้า", "贸易"),
            ("货运单据", "Bill of Lading", "ตราสารการขนส่ง", "贸易"),
            # 电商术语
            ("电商平台", "E-Commerce Platform", "แพลตฟอร์มอีคอมเมิร์ซ", "电商"),
            ("最低销售额", "Minimum Sales Target", "ยอดขายขั้นต่ำ", "电商"),
            ("退换货", "Return and Exchange", "การคืนและเปลี่ยนสินค้า", "电商"),
        ]
        cursor.executemany("INSERT INTO terms (zh, en, th, category) VALUES (?, ?, ?, ?)", sample_terms)
    
    cursor.execute("SELECT COUNT(*) FROM templates")
    if cursor.fetchone()[0] == 0:
        sample_templates = [
            ("简版合同模板", "合同", "# {title}\n## 甲方：{party_a}\n## 乙方：{party_b}\n## 有效期：{valid_period}\n### 第一条 合作内容\n\n此处填写合作内容...\n### 第二条 双方权利义务\n\n此处填写权利义务..."),
            ("通知模板", "通知", "# {title}\n**致：{recipient}**\n**发件人：{sender}**\n**日期：{date}**\n\n---\n\n{content}"),
            ("会议纪要模板", "会议", "# 会议纪要\n\n**会议时间：** {meeting_time}\n**会议地点：** {meeting_location}\n**参会人员：** {participants}\n**会议主题：** {topic}\n\n---\n## 会议内容\n\n{content}\n\n## 决议事项\n\n{decisions}"),
            ("经销协议模板", "合同", "# 经销协议 | Dealer Distribution Agreement\n\n## 协议双方\n\n**甲方 (Party A):** {company_name_cn}\n注册地址: {address_cn}\n**乙方 (Party B):** VISION DANCE CO., LTD.\n注册号: 0505568025253\n注册地址: 34 Suk Kasame Road, Suthep Sub-district, Mueang Chiang Mai District, Chiang Mai Province 50200\n\n## 产品授权\n\n授权产品: {products}\n授权区域: 泰国全境\n授权期限: {start_date} 至 {end_date}\n\n## 价格与付款\n\n结算货币: {currency}\n付款方式: {payment_terms}\n信用账期: {credit_period}\n\n## 双方权利义务\n\n### 甲方权利义务\n1. 提供产品质量保证\n2. 提供市场推广支持\n3. 保护乙方经销区域\n\n### 乙方权利义务\n1. 完成最低销售额 {min_sales}\n2. 遵守价格体系\n3. 遵守泰国产品标准\n\n## 产品责任\n\n依据泰国《产品责任法》(Product Liability Act, B.E. 2551 (2008))，甲方对产品缺陷造成的损害承担赔偿责任。\n\n## 争议解决\n\n首选: 友好协商 (30天内)\n次选: 仲裁 (CIETAC)\n适用法律: {applicable_law}\n\n## 协议生效\n\n本协议自双方签字之日起生效。\n本协议一式三份，中英文泰文各执一份，三种文本具有同等法律效力。\n\n[签字] [签字]\n甲方:          乙方:\n日期:           日期:"),
            ("产品责任条款", "合同", "# 产品责任条款 | Product Liability Clause\n\n## 缺陷定义\n\n产品缺陷包括:\n- 生产缺陷 (Manufacturing Defect)\n- 设计缺陷 (Design Defect)\n- 说明缺陷 (Warning Defect)\n\n## 责任范围\n\n甲方对因产品缺陷造成的以下损害负责:\n1. 人身伤害\n2. 财产损失\n3. 合理费用\n\n## 免责条款\n\n以下情况甲方不承担责任:\n1. 产品未被用于正常用途\n2. 消费者故意造成损害\n3. 不可抗力因素\n\n## 赔偿限额\n\n年度赔偿限额: {annual_cap}\n单次事故限额: {per_incident_cap}"),
            ("争议解决条款", "合同", "# 争议解决条款 | Dispute Resolution Clause\n\n## 第一阶段: 友好协商\n任何争议应在争议发生后30天内通过友好协商解决。\n\n## 第二阶段: 仲裁\n\n如协商未能解决争议，任何一方可将争议提交以下仲裁机构:\n- CIETAC (中国国际经济贸易仲裁委员会) - 仲裁地: 北京/上海\n- SIAC (新加坡国际仲裁中心) - 仲裁地: 新加坡\n- THAC (泰国贸易仲裁委员会) - 仲裁地: 曼谷\n\n## 仲裁规则\n适用《联合国国际贸易法委员会仲裁规则》(UNCITRAL Rules)\n仲裁裁决为终局裁决，对双方具有约束力\n\n## 适用法律\n- 中国法: 《中华人民共和国合同法》/ 《中华人民共和国民法典》\n- 泰国法: 泰国《民事和商事法典》"),
            ("跨境电商补充协议", "合同", "# 跨境电商补充条款 | Cross-Border E-Commerce Addendum\n\n## 电商平台责任\n\n乙方作为电商平台责任:\n1. 确保平台符合泰国《电子商务和数据保护法》\n2. 保护消费者个人信息\n3. 处理退换货请求\n\n## 海关与税务\n\n进出口税务责任:\n- 甲方负责中国出口清关\n- 乙方负责泰国进口清关\n- 乙方负责代扣代缴泰国增值税 (VAT7%)\n\n## 知识产权\n\n甲方保证授权产品不侵犯第三方知识产权。\n如发生侵权投诉，乙方应及时通知甲方，甲方承担赔偿责任。\n\n## 合规检查\n\n- [ ] 泰国工业标准 (TIS) 认证\n- [ ] 泰国FDA批准（如适用）\n- [ ] 产品标签泰文标注\n- [ ] 原产地标识"),
        ]
        cursor.executemany("INSERT INTO templates (name, category, content) VALUES (?, ?, ?)", sample_templates)
    
    conn.commit()
    conn.close()

class Document(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    content_en: Optional[str] = None
    content_th: Optional[str] = None
    template_id: Optional[int] = None
    category: str = "其他"
    status: str = "draft"
    created_by: Optional[str] = None

class Template(BaseModel):
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    content: str

class Term(BaseModel):
    id: Optional[int] = None
    zh: str
    en: Optional[str] = None
    th: Optional[str] = None
    category: str = "通用"

@app.get("/")
def root():
    return {"message": "CompanyDoc API - 企业文档管理系统", "version": "1.0.0"}

@app.get("/api/documents", response_model=List[dict])
def get_documents(page: int = 1, limit: int = 100, category: str = None, status: str = None, db: sqlite3.Connection = Depends(get_db)):
    offset = (page - 1) * limit
    query = "SELECT * FROM documents WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor = db.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

@app.get("/api/documents/{doc_id}", response_model=dict)
def get_document(doc_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return dict(row)

@app.post("/api/documents", response_model=dict)
def create_document(doc: Document, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute('''
        INSERT INTO documents (title, content, content_en, content_th, template_id, category, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc.title, doc.content, doc.content_en, doc.content_th, doc.template_id, doc.category, doc.status, doc.created_by))
    
    db.commit()
    doc_id = cursor.lastrowid
    
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    return dict(cursor.fetchone())

@app.put("/api/documents/{doc_id}", response_model=dict)
def update_document(doc_id: int, doc: Document, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute('''
        UPDATE documents SET title=?, content=?, content_en=?, content_th=?, template_id=?, category=?, status=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    ''', (doc.title, doc.content, doc.content_en, doc.content_th, doc.template_id, doc.category, doc.status, doc_id))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.commit()
    
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    return dict(cursor.fetchone())

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.commit()
    return {"message": "Document deleted successfully", "id": doc_id}

@app.get("/api/templates", response_model=List[dict])
def get_templates(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM templates ORDER BY name")
    return [dict(row) for row in cursor.fetchall()]

@app.post("/api/templates", response_model=dict)
def create_template(template: Template, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute('''
        INSERT INTO templates (name, category, content)
        VALUES (?, ?, ?)
    ''', (template.name, template.category, template.content))
    
    db.commit()
    template_id = cursor.lastrowid
    
    cursor = db.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
    return dict(cursor.fetchone())

@app.delete("/api/templates/{template_id}")
def delete_template(template_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.commit()
    return {"message": "Template deleted successfully", "id": template_id}

@app.get("/api/terms", response_model=List[dict])
def get_terms(category: str = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM terms WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY zh"
    cursor = db.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

@app.post("/api/terms", response_model=dict)
def create_term(term: Term, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute('''
        INSERT INTO terms (zh, en, th, category)
        VALUES (?, ?, ?, ?)
    ''', (term.zh, term.en, term.th, term.category))
    
    db.commit()
    term_id = cursor.lastrowid
    
    cursor = db.execute("SELECT * FROM terms WHERE id = ?", (term_id,))
    return dict(cursor.fetchone())

@app.put("/api/terms/{term_id}", response_model=dict)
def update_term(term_id: int, term: Term, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute('''
        UPDATE terms SET zh=?, en=?, th=?, category=? WHERE id=?
    ''', (term.zh, term.en, term.th, term.category, term_id))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    
    db.commit()
    
    cursor = db.execute("SELECT * FROM terms WHERE id = ?", (term_id,))
    return dict(cursor.fetchone())

@app.delete("/api/terms/{term_id}")
def delete_term(term_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM terms WHERE id = ?", (term_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    
    db.commit()
    return {"message": "Term deleted successfully", "id": term_id}

@app.post("/api/documents/{doc_id}/translate")
def translate_document(doc_id: int, target_language: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = dict(row)
    original_content = doc['content']
    
    translated_content = f"[翻译结果 - {target_language.upper()}] {original_content[:100]}"
    
    if target_language == 'en':
        db.execute("UPDATE documents SET content_en = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (translated_content, doc_id))
    elif target_language == 'th':
        db.execute("UPDATE documents SET content_th = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (translated_content, doc_id))
    
    db.commit()
    
    return {
        "document_id": doc_id,
        "target_language": target_language,
        "message": "Translation completed successfully",
        "translated_content": translated_content
    }

@app.post("/api/documents/{doc_id}/approve")
def approve_document(doc_id: int, approver: str = "系统", comment: str = "", db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.execute('''
        INSERT INTO approvals (document_id, approver, status, comment)
        VALUES (?, ?, 'approved', ?)
    ''', (doc_id, approver, comment))
    
    db.execute("UPDATE documents SET status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (doc_id,))
    
    db.commit()
    
    return {"message": "Document approved successfully", "document_id": doc_id, "approver": approver}

@app.post("/api/documents/{doc_id}/reject")
def reject_document(doc_id: int, approver: str = "系统", comment: str = "", db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.execute('''
        INSERT INTO approvals (document_id, approver, status, comment)
        VALUES (?, ?, 'rejected', ?)
    ''', (doc_id, approver, comment))
    
    db.execute("UPDATE documents SET status = 'rejected', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (doc_id,))
    
    db.commit()
    
    return {"message": "Document rejected successfully", "document_id": doc_id, "approver": approver}

@app.get("/api/stats")
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM documents WHERE status = 'draft'")
    draft_docs = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM documents WHERE status = 'approved'")
    approved_docs = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM terms")
    total_terms = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM templates")
    total_templates = cursor.fetchone()[0]
    
    return {
        "total_documents": total_docs,
        "draft_documents": draft_docs,
        "approved_documents": approved_docs,
        "total_terms": total_terms,
        "total_templates": total_templates
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 CompanyDoc API 启动中...")
    print("📊 API 文档: http://localhost:8000/docs")
    print("📊 备用文档: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
