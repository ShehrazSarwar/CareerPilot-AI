import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(analysis_data: dict, target_role: str) -> io.BytesIO:
    """
    Generates a beautifully formatted PDF report from the AI career analysis data.
    Returns the PDF content as a BytesIO buffer.
    """
    buffer = io.BytesIO()
    
    # Page setup
    # Margins: 0.5 inch (36 points) for maximum printable area and sleek look
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Define primary theme colors
    primary_color = colors.HexColor("#1e293b")  # Dark slate gray
    secondary_color = colors.HexColor("#4f46e5")  # Deep Indigo (SaaS vibe)
    accent_color = colors.HexColor("#f8fafc")  # Off-white background card
    border_color = colors.HexColor("#e2e8f0")  # Light border gray
    text_color = colors.HexColor("#334155")  # Muted slate text
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'H1_Header',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceAfter=4
    )

    card_body_style = ParagraphStyle(
        'CardBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_color,
        spaceAfter=4
    )
    
    # 1. Header Section
    story.append(Paragraph("CareerPilot AI", title_style))
    story.append(Paragraph(f"Personalized Career Mentorship & Development Report  |  Target: {target_role}", subtitle_style))
    
    # Decorative line
    line_table = Table([[""]], colWidths=[504], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), secondary_color),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))
    
    # 2. Score & Summary Grid
    score = analysis_data.get("career_score", 0)
    score_color = "#22c55e" if score >= 80 else ("#eab308" if score >= 60 else "#ef4444")
    
    summary_text = analysis_data.get("summary", "No summary available.")
    
    # Score Card
    score_p_title = Paragraph("<b>CAREER READINESS SCORE</b>", ParagraphStyle('ScoreTitle', parent=body_style, fontSize=9, leading=12, alignment=1))
    score_p_val = Paragraph(f"<font color='{score_color}' size='32'><b>{score}%</b></font>", ParagraphStyle('ScoreVal', parent=body_style, alignment=1))
    score_p_desc = Paragraph("Compared against industry standards.", ParagraphStyle('ScoreDesc', parent=body_style, fontSize=8, leading=10, textColor=colors.HexColor("#64748b"), alignment=1))
    
    # Summary Card
    summary_p_title = Paragraph("<b>PROFILE EVALUATION SUMMARY</b>", ParagraphStyle('SumTitle', parent=body_style, fontSize=9, leading=12, textColor=secondary_color))
    summary_p_text = Paragraph(summary_text, body_style)
    
    # Grid Table
    grid_data = [
        [
            [score_p_title, Spacer(1, 8), score_p_val, Spacer(1, 6), score_p_desc],
            [summary_p_title, Spacer(1, 6), summary_p_text]
        ]
    ]
    
    grid_table = Table(grid_data, colWidths=[150, 354])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (0,0), 1, border_color),
        ('BOX', (1,0), (1,0), 1, border_color),
        ('BACKGROUND', (1,0), (1,0), accent_color),
        ('PADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 15))
    
    # 3. Strengths & Weaknesses (2 columns)
    strengths_paragraphs = [Paragraph(f"<b>&bull;</b> {s}", bullet_style) for s in analysis_data.get("strengths", [])]
    weaknesses_paragraphs = [Paragraph(f"<b>&bull;</b> {w}", bullet_style) for w in analysis_data.get("weaknesses", [])]
    
    if not strengths_paragraphs:
        strengths_paragraphs = [Paragraph("No specific strengths noted.", body_style)]
    if not weaknesses_paragraphs:
        weaknesses_paragraphs = [Paragraph("No major weaknesses noted.", body_style)]
        
    sw_data = [
        [
            [Paragraph("<b>Key Strengths</b>", ParagraphStyle('STitle', parent=h1_style, spaceBefore=0, textColor=colors.HexColor("#16a34a")))] + strengths_paragraphs,
            [Paragraph("<b>Areas for Growth</b>", ParagraphStyle('WTitle', parent=h1_style, spaceBefore=0, textColor=colors.HexColor("#dc2626")))] + weaknesses_paragraphs
        ]
    ]
    
    sw_table = Table(sw_data, colWidths=[244, 244])
    sw_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (0,0), 1, border_color),
        ('BOX', (1,0), (1,0), 1, border_color),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0fdf4")), # Soft green
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fef2f2")), # Soft red
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(sw_table)
    story.append(Spacer(1, 15))
    
    # 4. Skill Gaps (Full Width Box)
    gaps_content = []
    gaps_content.append(Paragraph("Target Skill Gaps", h1_style))
    gaps = analysis_data.get("skill_gaps", [])
    if gaps:
        for g in gaps:
            gaps_content.append(Paragraph(f"<b>&bull; {g}</b>", bullet_style))
    else:
        gaps_content.append(Paragraph("No major skill gaps identified.", body_style))
        
    gaps_table = Table([[gaps_content]], colWidths=[504])
    gaps_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('BACKGROUND', (0,0), (-1,-1), accent_color),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(gaps_table)
    
    story.append(PageBreak())  # Force roadmap and projects onto Page 2 for clean formatting
    
    # 5. Career Roadmap (30-60-90 Day Plan)
    story.append(Paragraph("30-60-90 Day Strategic Roadmap", h1_style))
    
    roadmap_data = analysis_data.get("roadmap_30_60_90", {})
    r_30 = roadmap_data.get("30_day", [])
    r_60 = roadmap_data.get("60_day", [])
    r_90 = roadmap_data.get("90_day", [])
    
    rm_table_content = []
    
    # 30 Day Row
    rm_30_paragraphs = [Paragraph(f"<b>&bull;</b> {item}", bullet_style) for item in r_30]
    rm_table_content.append([
        Paragraph("<b>DAYS 1–30</b><br/><font size='8' color='#64748b'>FOUNDATION</font>", ParagraphStyle('RM30Label', parent=body_style, fontName='Helvetica-Bold', alignment=1)),
        rm_30_paragraphs
    ])
    
    # 60 Day Row
    rm_60_paragraphs = [Paragraph(f"<b>&bull;</b> {item}", bullet_style) for item in r_60]
    rm_table_content.append([
        Paragraph("<b>DAYS 31–60</b><br/><font size='8' color='#64748b'>APPLICATION</font>", ParagraphStyle('RM60Label', parent=body_style, fontName='Helvetica-Bold', alignment=1)),
        rm_60_paragraphs
    ])
    
    # 90 Day Row
    rm_90_paragraphs = [Paragraph(f"<b>&bull;</b> {item}", bullet_style) for item in r_90]
    rm_table_content.append([
        Paragraph("<b>DAYS 61–90</b><br/><font size='8' color='#64748b'>TRANSITION</font>", ParagraphStyle('RM90Label', parent=body_style, fontName='Helvetica-Bold', alignment=1)),
        rm_90_paragraphs
    ])
    
    rm_table = Table(rm_table_content, colWidths=[100, 404])
    rm_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 1, border_color),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
    ]))
    story.append(rm_table)
    story.append(Spacer(1, 15))
    
    # 6. Suggested Certifications
    story.append(Paragraph("Recommended Certifications", h1_style))
    for c in analysis_data.get("certifications", [])[:3]:
        cert_card_content = [
            Paragraph(f"<b>{c.get('name')}</b> ({c.get('provider')})", card_title_style),
            Spacer(1, 3),
            Paragraph(c.get('reason', ''), card_body_style)
        ]
        cert_card_table = Table([[cert_card_content]], colWidths=[504])
        cert_card_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('BACKGROUND', (0,0), (-1,-1), accent_color),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(cert_card_table)
        story.append(Spacer(1, 6))
        
    story.append(Spacer(1, 10))
    
    # 7. Strategic Project Portfolio
    story.append(Paragraph("Strategic Project Portfolio", h1_style))
    for p in analysis_data.get("project_ideas", [])[:3]:
        techs = ", ".join(p.get("technologies", []))
        proj_card_content = [
            Paragraph(f"<b>{p.get('title')}</b> <font size='8' color='#64748b'>({p.get('difficulty')})</font>", card_title_style),
            Spacer(1, 3),
            Paragraph(p.get('description', ''), card_body_style),
            Spacer(1, 3),
            Paragraph(f"<i>Stack: {techs}</i>", ParagraphStyle('ProjTech', parent=card_body_style, fontSize=8, textColor=secondary_color))
        ]
        proj_card_table = Table([[proj_card_content]], colWidths=[504])
        proj_card_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('BACKGROUND', (0,0), (-1,-1), accent_color),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(proj_card_table)
        story.append(Spacer(1, 6))
    
    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer
