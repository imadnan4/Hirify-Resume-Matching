import io
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import xlsxwriter
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match import Match
from app.models.candidate import Candidate


class ExportService:
    """Service for exporting data in various formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
    def export_matches_csv(self, matches: List[Match], include_details: bool = False) -> io.BytesIO:
        """Export matches to CSV format"""
        output = io.BytesIO()
        
        # Create CSV writer
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Header row
        headers = [
            'Match ID', 'Resume ID', 'Job ID', 'Candidate Name', 'Job Title', 
            'Company', 'Overall Score', 'Skills Score', 'Experience Score', 
            'Education Score', 'Additional Score', 'Created At'
        ]
        
        if include_details:
            headers.extend(['Matched Skills', 'Missing Skills', 'Explanation'])
        
        writer.writerow(headers)
        
        # Data rows
        for match in matches:
            row = [
                match.id,
                match.resume_id,
                match.job_id,
                match.resume.structured_data.get('contact_info', {}).get('full_name', 'N/A') if match.resume else 'N/A',
                match.job_description.title if match.job_description else 'N/A',
                match.job_description.company if match.job_description else 'N/A',
                f"{match.overall_score:.2f}",
                f"{match.skills_score:.2f}" if match.skills_score else 'N/A',
                f"{match.experience_score:.2f}" if match.experience_score else 'N/A',
                f"{match.education_score:.2f}" if match.education_score else 'N/A',
                f"{match.additional_score:.2f}" if match.additional_score else 'N/A',
                match.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            if include_details:
                matched_skills = ', '.join(match.matched_skills) if match.matched_skills else 'None'
                explanation = match.explanation.get('overall_explanation', 'N/A') if match.explanation else 'N/A'
                missing_skills = ', '.join(match.explanation.get('skill_gaps', [])) if match.explanation else 'N/A'
                row.extend([matched_skills, missing_skills, explanation])
            
            writer.writerow(row)
        
        # Convert to bytes
        output.write(csv_buffer.getvalue().encode('utf-8'))
        output.seek(0)
        
        return output
    
    def export_matches_excel(self, matches: List[Match], include_details: bool = False) -> io.BytesIO:
        """Export matches to Excel format"""
        output = io.BytesIO()
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Matches')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4472C4',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'text_wrap': True
        })
        
        score_format = workbook.add_format({
            'border': 1,
            'num_format': '0.00'
        })
        
        # Headers
        headers = [
            'Match ID', 'Resume ID', 'Job ID', 'Candidate Name', 'Job Title', 
            'Company', 'Overall Score', 'Skills Score', 'Experience Score', 
            'Education Score', 'Additional Score', 'Created At'
        ]
        
        if include_details:
            headers.extend(['Matched Skills', 'Missing Skills', 'Explanation'])
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        for row, match in enumerate(matches, start=1):
            worksheet.write(row, 0, match.id, cell_format)
            worksheet.write(row, 1, match.resume_id, cell_format)
            worksheet.write(row, 2, match.job_id, cell_format)
            worksheet.write(row, 3, 
                          match.resume.structured_data.get('contact_info', {}).get('full_name', 'N/A') if match.resume else 'N/A', 
                          cell_format)
            worksheet.write(row, 4, match.job_description.title if match.job_description else 'N/A', cell_format)
            worksheet.write(row, 5, match.job_description.company if match.job_description else 'N/A', cell_format)
            worksheet.write(row, 6, match.overall_score, score_format)
            worksheet.write(row, 7, match.skills_score if match.skills_score else 0, score_format)
            worksheet.write(row, 8, match.experience_score if match.experience_score else 0, score_format)
            worksheet.write(row, 9, match.education_score if match.education_score else 0, score_format)
            worksheet.write(row, 10, match.additional_score if match.additional_score else 0, score_format)
            worksheet.write(row, 11, match.created_at.strftime('%Y-%m-%d %H:%M:%S'), cell_format)
            
            if include_details:
                matched_skills = ', '.join(match.matched_skills) if match.matched_skills else 'None'
                explanation = match.explanation.get('overall_explanation', 'N/A') if match.explanation else 'N/A'
                missing_skills = ', '.join(match.explanation.get('skill_gaps', [])) if match.explanation else 'N/A'
                worksheet.write(row, 12, matched_skills, cell_format)
                worksheet.write(row, 13, missing_skills, cell_format)
                worksheet.write(row, 14, explanation, cell_format)
        
        # Auto-fit columns
        for col in range(len(headers)):
            worksheet.set_column(col, col, 15)
        
        workbook.close()
        output.seek(0)
        
        return output
    
    def export_matches_pdf(self, matches: List[Match], include_summary: bool = True) -> io.BytesIO:
        """Export matches to PDF format"""
        output = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Story elements
        story = []
        
        # Title
        title = Paragraph(f"Resume-Job Matching Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_info = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Matches: {len(matches)}"
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary statistics
        if include_summary and matches:
            avg_score = sum(match.overall_score for match in matches) / len(matches)
            high_score_count = sum(1 for match in matches if match.overall_score >= 80)
            medium_score_count = sum(1 for match in matches if 60 <= match.overall_score < 80)
            low_score_count = len(matches) - high_score_count - medium_score_count
            
            summary_text = f"""
            <b>Summary Statistics:</b><br/>
            Average Match Score: {avg_score:.2f}<br/>
            High Score Matches (≥80): {high_score_count}<br/>
            Medium Score Matches (60-79): {medium_score_count}<br/>
            Low Score Matches (<60): {low_score_count}
            """
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Table data
        table_data = [
            ['Candidate', 'Job Title', 'Company', 'Overall Score', 'Skills Score', 'Experience Score']
        ]
        
        for match in matches:
            candidate_name = match.resume.structured_data.get('contact_info', {}).get('full_name', 'N/A') if match.resume else 'N/A'
            job_title = match.job_description.title if match.job_description else 'N/A'
            company = match.job_description.company if match.job_description else 'N/A'
            
            table_data.append([
                candidate_name,
                job_title,
                company,
                f"{match.overall_score:.1f}",
                f"{match.skills_score:.1f}" if match.skills_score else 'N/A',
                f"{match.experience_score:.1f}" if match.experience_score else 'N/A'
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        
        return output
    
    def export_candidates_csv(self, candidates: List[Candidate]) -> io.BytesIO:
        """Export candidates to CSV format"""
        output = io.BytesIO()
        
        # Create CSV writer
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Header row
        headers = [
            'Candidate ID', 'Full Name', 'Email', 'Phone', 'Location', 
            'Years Experience', 'Education Level', 'Field of Study', 'Skills Count', 'Created At'
        ]
        writer.writerow(headers)
        
        # Data rows
        for candidate in candidates:
            skills_count = len(candidate.skills.get('skills', [])) if candidate.skills else 0
            
            row = [
                candidate.id,
                candidate.full_name or 'N/A',
                candidate.email or 'N/A',
                candidate.phone or 'N/A',
                candidate.location or 'N/A',
                candidate.years_experience or 0,
                candidate.education_level or 'N/A',
                candidate.field_of_study or 'N/A',
                skills_count,
                candidate.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            writer.writerow(row)
        
        # Convert to bytes
        output.write(csv_buffer.getvalue().encode('utf-8'))
        output.seek(0)
        
        return output
    
    def export_jobs_csv(self, jobs: List[JobDescription]) -> io.BytesIO:
        """Export job descriptions to CSV format"""
        output = io.BytesIO()
        
        # Create CSV writer
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Header row
        headers = [
            'Job ID', 'Title', 'Company', 'Location', 'Employment Type', 
            'Experience Level', 'Skills Count', 'Source', 'Status', 'Created At'
        ]
        writer.writerow(headers)
        
        # Data rows
        for job in jobs:
            skills_count = len(job.skills) if job.skills else 0
            
            row = [
                job.id,
                job.title,
                job.company,
                job.location or 'N/A',
                job.employment_type or 'N/A',
                job.experience_level or 'N/A',
                skills_count,
                job.source or 'Manual',
                job.status or 'active',
                job.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            writer.writerow(row)
        
        # Convert to bytes
        output.write(csv_buffer.getvalue().encode('utf-8'))
        output.seek(0)
        
        return output
    
    def generate_analytics_report(self, db: Session, include_charts: bool = False) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        # Get statistics
        total_resumes = db.query(Resume).count()
        total_jobs = db.query(JobDescription).count()
        total_matches = db.query(Match).count()
        total_candidates = db.query(Candidate).count()
        
        # Processing statistics
        processed_resumes = db.query(Resume).filter(Resume.status == "completed").count()
        failed_resumes = db.query(Resume).filter(Resume.status == "failed").count()
        success_rate = (processed_resumes / total_resumes * 100) if total_resumes > 0 else 0
        
        # Match quality statistics
        if total_matches > 0:
            avg_match_score = db.query(Match).with_entities(
                db.func.avg(Match.overall_score)
            ).scalar() or 0
            
            high_score_matches = db.query(Match).filter(Match.overall_score >= 80).count()
            medium_score_matches = db.query(Match).filter(
                Match.overall_score >= 60, Match.overall_score < 80
            ).count()
            low_score_matches = total_matches - high_score_matches - medium_score_matches
        else:
            avg_match_score = 0
            high_score_matches = 0
            medium_score_matches = 0
            low_score_matches = 0
        
        # Top skills analysis
        all_skills = []
        candidates_with_skills = db.query(Candidate).filter(Candidate.skills.isnot(None)).all()
        
        for candidate in candidates_with_skills:
            if candidate.skills and 'skills' in candidate.skills:
                candidate_skills = [skill.get('skill', '') for skill in candidate.skills['skills']]
                all_skills.extend(candidate_skills)
        
        from collections import Counter
        top_skills = Counter(all_skills).most_common(10)
        
        # Job market analysis
        job_sources = db.query(JobDescription.source, db.func.count(JobDescription.id)).group_by(JobDescription.source).all()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_resumes': total_resumes,
                'total_jobs': total_jobs,
                'total_matches': total_matches,
                'total_candidates': total_candidates
            },
            'processing_stats': {
                'processed_resumes': processed_resumes,
                'failed_resumes': failed_resumes,
                'success_rate': round(success_rate, 2)
            },
            'match_quality': {
                'average_match_score': round(float(avg_match_score), 2),
                'high_score_matches': high_score_matches,
                'medium_score_matches': medium_score_matches,
                'low_score_matches': low_score_matches
            },
            'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills],
            'job_sources': [{'source': source or 'Manual', 'count': count} for source, count in job_sources]
        }
        
        return report
    
    def export_analytics_pdf(self, analytics_data: Dict[str, Any]) -> io.BytesIO:
        """Export analytics report as PDF"""
        output = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Story elements
        story = []
        
        # Title
        title = Paragraph("Resume Parser Analytics Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_info = f"Generated on: {analytics_data['generated_at']}"
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Overview section
        overview = analytics_data['overview']
        overview_text = f"""
        <b>System Overview:</b><br/>
        Total Resumes: {overview['total_resumes']}<br/>
        Total Jobs: {overview['total_jobs']}<br/>
        Total Matches: {overview['total_matches']}<br/>
        Total Candidates: {overview['total_candidates']}
        """
        story.append(Paragraph(overview_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Processing stats
        processing = analytics_data['processing_stats']
        processing_text = f"""
        <b>Processing Statistics:</b><br/>
        Processed Resumes: {processing['processed_resumes']}<br/>
        Failed Resumes: {processing['failed_resumes']}<br/>
        Success Rate: {processing['success_rate']}%
        """
        story.append(Paragraph(processing_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Match quality
        match_quality = analytics_data['match_quality']
        quality_text = f"""
        <b>Match Quality Analysis:</b><br/>
        Average Match Score: {match_quality['average_match_score']}<br/>
        High Score Matches (≥80): {match_quality['high_score_matches']}<br/>
        Medium Score Matches (60-79): {match_quality['medium_score_matches']}<br/>
        Low Score Matches (<60): {match_quality['low_score_matches']}
        """
        story.append(Paragraph(quality_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Top skills table
        if analytics_data['top_skills']:
            story.append(Paragraph("<b>Top Skills in Demand:</b>", self.styles['Normal']))
            story.append(Spacer(1, 10))
            
            skills_data = [['Skill', 'Count']]
            for skill_info in analytics_data['top_skills'][:10]:
                skills_data.append([skill_info['skill'], str(skill_info['count'])])
            
            skills_table = Table(skills_data, colWidths=[3*inch, 1*inch])
            skills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(skills_table)
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        
        return output
